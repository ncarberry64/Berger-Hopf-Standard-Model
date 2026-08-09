from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from bhsm.interface.aether_generator_selection_v15_2 import (
    EXACT_NEXT_OBJECT,
    OUTCOME,
    PRIMARY_VERDICT,
    action_schur_composition_payload,
    affine_spectral_equivalence,
    artifact_payloads,
    boundary_selection_payload,
    central_shift_gate,
    clock_selection_payload,
    completion_payload,
    core_module_payload,
    invariant_commutant_diagnostics,
    joint_clocked_hamiltonian,
    materialize,
    physical_equivalence_payload,
    preclock_scaling_diagnostics,
    quotient_nonuniqueness_witness,
    structure_preserving_unitary_diagnostics,
    uniqueness_payload,
    zero_parameter_schur_reduction,
)

ROOT = Path(__file__).resolve().parents[1]


def test_structure_preserving_unitary_is_basis_equivalence() -> None:
    first = np.diag([1.0, 2.0])
    invariant = np.diag([-1.0, 1.0])
    projection = np.diag([1.0, 0.0])
    unitary = np.array([[0.0, 1.0], [1.0, 0.0]])
    result = structure_preserving_unitary_diagnostics(
        first,
        unitary @ first @ unitary.T,
        unitary,
        [invariant],
        [unitary @ invariant @ unitary.T],
        projection,
        unitary @ projection @ unitary.T,
    )
    assert result["structure_preserving_unitary_equivalence"] is True
    assert result["generator_intertwining_residual"] == 0.0


def test_generator_only_intertwining_is_not_enough() -> None:
    generator = np.diag([1.0, 2.0])
    unitary = np.eye(2)
    result = structure_preserving_unitary_diagnostics(
        generator, generator, unitary, [np.diag([1.0, -1.0])], [np.diag([-1.0, 1.0])]
    )
    assert result["structure_preserving_unitary_equivalence"] is False


def test_nonunitary_intertwiner_is_rejected() -> None:
    with pytest.raises(ValueError):
        structure_preserving_unitary_diagnostics(np.eye(2), np.eye(2), 2.0 * np.eye(2))


def test_v15_1_two_level_witness_is_affine_equivalent_preclock() -> None:
    result = affine_spectral_equivalence([0.0, 1.0], [0.0, 2.0])
    assert result["equivalent"] is True
    assert result["positive_scale"] == pytest.approx(2.0)


def test_three_level_gap_ratio_witness_survives_full_affine_quotient() -> None:
    result = affine_spectral_equivalence([0.0, 1.0, 2.0], [0.0, 1.0, 3.0])
    assert result["equivalent"] is False
    assert result["positive_scale"] is None


def test_central_shift_is_not_unconditionally_quotiented() -> None:
    gate = central_shift_gate()
    assert gate["single_fixed_depth_transition_probabilities_unchanged"] is True
    assert gate["different_depth_history_interference_can_change"] is True
    assert gate["event_interference_or_projectivization_action_owned"] is False
    assert gate["classification"].startswith("CONDITIONAL_PROJECTIVE")


def test_block_relative_shift_is_not_central() -> None:
    assert central_shift_gate()["block_relative_shift_is_central"] is False


def test_preclock_scaling_leaves_kernel_exactly_invariant() -> None:
    result = preclock_scaling_diagnostics(np.diag([0.0, 1.0, 3.0]), 2.5, 0.7)
    assert result["kernel_residual"] < 1e-12
    assert result["is_preclock_reparameterization"] is True


def test_joint_clock_hamiltonian_is_scaling_covariant() -> None:
    generator = np.diag([0.0, 1.0, 3.0])
    original = joint_clocked_hamiltonian(generator, 2.0, 5.0, hbar=7.0)
    transformed = joint_clocked_hamiltonian(4.0 * generator, 0.5, 5.0, hbar=7.0)
    assert np.array_equal(original, transformed)


def test_joint_clock_hamiltonian_rejects_external_zero_scale() -> None:
    with pytest.raises(ValueError):
        joint_clocked_hamiltonian(np.eye(2), 0.0, 1.0)


def test_simple_three_sector_invariant_commutant_has_dimension_three() -> None:
    result = invariant_commutant_diagnostics([np.diag([-1.0, 0.0, 1.0])])
    assert result["complex_commutant_dimension"] == 3
    assert result["Hermitian_commutant_real_dimension"] == 3
    assert result["symmetry_selects_unique_generator_mod_identity"] is False


def test_scalar_invariant_has_large_commutant() -> None:
    result = invariant_commutant_diagnostics([np.eye(3)])
    assert result["complex_commutant_dimension"] == 9


def test_discrete_nonuniqueness_witness_closes_all_admissibility_checks() -> None:
    witness = quotient_nonuniqueness_witness()
    assert witness["spectra"] == [[0.0, 1.0, 2.0], [0.0, 1.0, 3.0]]
    assert witness["gap_ratio_invariants"] == [1.0, 2.0]
    assert witness["physically_inequivalent_after_unitary_shift_and_positive_scale_quotient"] is True
    assert max(witness["commutator_residuals"]) == 0.0
    assert max(witness["unitarity_residuals"]) < 1e-12
    assert max(witness["identity_residuals"]) < 1e-12
    assert max(witness["event_composition_residuals"]) < 1e-12
    assert witness["same_self_adjoint_domain"] is True
    assert witness["boundary_Green_form_norm"] < 1e-12
    assert witness["continuous_parameter_used_in_witness"] is False


def test_zero_parameter_schur_reduction_is_self_adjoint() -> None:
    reduced = zero_parameter_schur_reduction(
        np.diag([2.0, 3.0]), np.diag([4.0, 5.0]), np.array([[1.0, 0.2], [0.2, 0.5]])
    )
    assert np.linalg.norm(reduced - reduced.conj().T) < 1e-12


def test_zero_parameter_schur_reduction_rejects_singular_core() -> None:
    with pytest.raises(ValueError):
        zero_parameter_schur_reduction(np.eye(2), np.diag([1.0, 0.0]), np.eye(2))


def test_core_module_gate_does_not_fabricate_H_C() -> None:
    payload = core_module_payload()
    assert payload["regular_geometric_Hilbert_spaces_owned"] is True
    assert payload["pregeometric_core_has_measure"] is False
    assert payload["pregeometric_core_has_operator_representation"] is False
    assert payload["finite_dimensional_convenience_module_adopted"] is False
    assert payload["unique_H_C_action_derived"] is False


def test_boundary_theory_classifies_but_action_does_not_select() -> None:
    payload = boundary_selection_payload()
    assert payload["pregeometric_core_boundary_term_in_retained_action"] is False
    assert payload["physical_Theta_A_action_selected"] is False
    assert payload["self_adjointness_implies_physical_selection"] is False


def test_schur_and_composition_routes_remain_conditional() -> None:
    payload = action_schur_composition_payload()
    assert payload["retained_action_contains_Q_A"] is False
    assert payload["D_C_action_owned"] is False
    assert payload["B_action_owned"] is False
    assert payload["spectral_z_legitimate_before_clock"] is False
    assert payload["event_group_law"].startswith("U(")
    assert payload["full_event_functor_selects_generator"] is False


def test_no_archived_rotor_is_promoted_to_reference_clock() -> None:
    payload = clock_selection_payload()
    assert payload["action_selected_stable_core_cycle"] is False
    assert payload["Goldstone_rotor_is_reference_clock"] is False
    assert payload["FR_rotor_is_reference_clock"] is False
    assert payload["relative_periodic_monodromy_is_reference_clock"] is False
    assert payload["joint_H_eff_unique"] is False


def test_physical_quotient_is_not_claimed_action_owned() -> None:
    payload = physical_equivalence_payload()
    assert payload["unitary_basis_change_is_physical_difference"] is False
    assert payload["physical_quotient_action_owned"] is False
    assert payload["preclock_scaling"]["classification"] == "REPARAMETERIZATION_REDUNDANCY_BEFORE_CLOCK_SELECTION"


def test_thirteen_gate_classification_is_outcome_F() -> None:
    payload = uniqueness_payload()
    assert payload["T13_physical_uniqueness"].startswith("UNRESOLVED")
    assert payload["physical_generator_cardinality"] == "UNDEFINED_NOT_ZERO"
    assert payload["outcome"] == OUTCOME


def test_completion_gate_preserves_claim_boundary_and_recovery() -> None:
    payload = completion_payload()
    assert payload["primary_verdict"] == PRIMARY_VERDICT
    assert payload["exact_next_object"] == EXACT_NEXT_OBJECT
    assert payload["outcome"] == OUTCOME
    assert payload["K_A_literal_unique"] is False
    assert payload["K_A_physical_class_unique"] is False
    assert payload["physical_K_A_quotient_action_defined"] is False
    assert payload["H_eff_uniquely_determined"] is False
    assert payload["exact_regular_recovery"]["all_residuals_exactly_zero"] is True
    assert payload["FULL_BHSM_COMPLETE"] is False
    assert payload["validation_passed"] is True


def test_no_time_energy_frame_parameter_field_or_empirical_input_is_added() -> None:
    payload = completion_payload()
    assert payload["new_continuous_parameter_introduced"] is False
    assert payload["new_fundamental_dynamical_field_introduced"] is False
    assert payload["preferred_frame_introduced"] is False
    assert payload["empirical_inputs_used"] is False
    assert payload["validation"]["no_ordinary_time_primitive"] is True
    assert payload["validation"]["no_conventional_energy_primitive"] is True


def test_frozen_predictions_and_official_logic_remain_byte_exact() -> None:
    expected = {
        "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
        "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
        "src/bhsm_model.py": "8fc5a59ac4fcafe4d3fca3249c46eaaf4ee2d0a019656333b75e3b1a989c8b3b",
        "src/bhsm/interface/predictions.py": "ea0539bef06184c619dd028eafafb76ea15e92a444483ff93637593f0eaa1fed",
        "artifacts/CKM_no_fit_operator_output_v1.json": "9c354e8812682c75187c00becb90ff44b5dcc74aef10992103df28b34321d757",
    }
    for relative, digest in expected.items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest


def test_artifacts_contain_no_forbidden_target_inputs() -> None:
    text = json.dumps(artifact_payloads(), sort_keys=True).lower()
    for forbidden in ("ckm_input", "pmns_input", "measured_mass", "higgs_target", "cosmological_fit"):
        assert forbidden not in text


def test_materialization_is_deterministic_and_strict_json(tmp_path: Path) -> None:
    first_paths = materialize(tmp_path)
    first = {path.name: path.read_bytes() for path in first_paths}
    second_paths = materialize(tmp_path)
    second = {path.name: path.read_bytes() for path in second_paths}
    assert first == second
    assert set(first) == set(artifact_payloads())
    for name, raw in first.items():
        assert json.loads(raw) == artifact_payloads()[name]
