from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from bhsm.interface.aether_microscopic_core_action_v15_3 import (
    EXACT_NEXT_OBJECT,
    FORBIDDEN_CORE_PRIMITIVES,
    OUTCOME,
    PRIMARY_VERDICT,
    artifact_payloads,
    attachment_block_diagnostics,
    boundary_event_payload,
    candidate_foundations_payload,
    completion_payload,
    core_algebra_payload,
    core_pairing_payload,
    core_quadratic_form_payload,
    core_representation_payload,
    cyclic_dirichlet_operator,
    cyclic_foundation,
    cyclic_shift,
    fifteen_gate_payload,
    finite_form_diagnostics,
    geometry_core_attachment_payload,
    materialize,
    microscopic_nonuniqueness_witness,
    normalized_pairing,
    quadratic_form,
    reconstruction_clock_payload,
    total_action_payload,
    weighted_pairing_nonuniqueness_witness,
)

ROOT = Path(__file__).resolve().parents[1]


def test_core_schema_contains_no_spacetime_coordinate() -> None:
    assert "spacetime_coordinate" in FORBIDDEN_CORE_PRIMITIVES
    assert completion_payload()["validation"]["no_primitive_spacetime_coordinate"] is True


def test_core_schema_contains_no_primitive_metric() -> None:
    assert "metric_tensor" in FORBIDDEN_CORE_PRIMITIVES
    assert completion_payload()["validation"]["no_primitive_metric"] is True


def test_core_schema_contains_no_coordinate_time() -> None:
    assert "coordinate_time" in FORBIDDEN_CORE_PRIMITIVES
    assert completion_payload()["validation"]["no_coordinate_time"] is True


def test_core_schema_contains_no_ordinary_energy() -> None:
    assert "ordinary_energy" in FORBIDDEN_CORE_PRIMITIVES
    assert completion_payload()["validation"]["no_ordinary_energy"] is True


def test_core_action_uses_no_spacetime_measure() -> None:
    assert "spacetime_volume_measure" in FORBIDDEN_CORE_PRIMITIVES
    assert total_action_payload()["ordinary_spacetime_integration_on_core_used"] is False


def test_cyclic_shift_is_a_unitary_representation() -> None:
    for order in (2, 3, 5):
        shift = cyclic_shift(order)
        assert np.linalg.norm(shift.conj().T @ shift - np.eye(order)) < 1e-12
        assert np.linalg.norm(np.linalg.matrix_power(shift, order) - np.eye(order)) < 1e-12


def test_cyclic_dirichlet_operator_is_positive_self_adjoint() -> None:
    for order in (2, 3):
        operator = cyclic_dirichlet_operator(order)
        diagnostics = finite_form_diagnostics(operator)
        assert diagnostics["Hermitian_residual"] == 0.0
        assert diagnostics["semibounded"] is True
        assert diagnostics["associated_operator_self_adjoint"] is True
        assert diagnostics["kernel_dimension"] == 1


def test_cyclic_witness_spectra_are_exact() -> None:
    assert np.linalg.eigvalsh(cyclic_dirichlet_operator(2)).tolist() == pytest.approx([0.0, 4.0])
    assert np.linalg.eigvalsh(cyclic_dirichlet_operator(3)).tolist() == pytest.approx([0.0, 3.0, 3.0])


def test_normalized_pairing_is_conjugate_symmetric_positive() -> None:
    left = np.array([1.0 + 2.0j, -0.5j, 0.25])
    right = np.array([0.2j, 1.0, -0.75j])
    assert normalized_pairing(left, right) == pytest.approx(np.conj(normalized_pairing(right, left)))
    assert normalized_pairing(left, left).real > 0.0
    assert abs(normalized_pairing(np.zeros(3), np.zeros(3))) == 0.0


def test_quadratic_form_is_nonnegative_on_cyclic_witness() -> None:
    operator = cyclic_dirichlet_operator(3)
    for vector in (np.ones(3), np.array([1.0, 0.0, -1.0]), np.array([1.0j, 2.0, -0.5j])):
        assert quadratic_form(operator, vector) >= -1e-12


def test_form_dimension_mismatch_is_rejected() -> None:
    with pytest.raises(ValueError):
        quadratic_form(np.eye(2), np.ones(3))


def test_event_architecture_supplies_only_an_algebraic_skeleton() -> None:
    payload = core_algebra_payload()
    assert payload["architecture_derived"]["associative_composition"] is True
    assert payload["architecture_derived"]["identity_events"] is True
    assert payload["not_derived"]["star_algebra"] is True
    assert payload["not_derived"]["positive_cone"] is True
    assert payload["physical_core_observable_algebra_action_derived"] is False


def test_no_candidate_foundation_is_silently_selected() -> None:
    payload = candidate_foundations_payload()
    assert len(payload["candidates"]) == 6
    assert all(row["selected"] is False for row in payload["candidates"])
    assert payload["preferred_schema_is_currently_derived"] is False
    assert payload["candidate_foundation_uniqueness"] is False


def test_hilbert_module_is_schema_not_action_output() -> None:
    row = candidate_foundations_payload()["candidates"][1]
    assert row["candidate"] == "B_Hilbert_module_correspondence"
    assert row["naturally_models_geometry_core_relation"] is True
    assert "NO_OWNED_COEFFICIENT_ALGEBRA" in row["verdict"]


def test_spectral_triple_is_not_promoted() -> None:
    row = candidate_foundations_payload()["candidates"][2]
    assert row["candidate"] == "C_spectral_triple_like"
    assert row["selected"] is False
    assert row["verdict"].startswith("NOT_FORCED")


def test_unbounded_KK_cycle_is_not_promoted() -> None:
    row = candidate_foundations_payload()["candidates"][4]
    assert row["candidate"] == "E_unbounded_KK_cycle"
    assert row["selected"] is False


def test_two_fixed_core_foundations_prove_nonuniqueness() -> None:
    witness = microscopic_nonuniqueness_witness()
    assert [item["Hilbert_dimension"] for item in witness["foundations"]] == [2, 3]
    assert witness["unitarily_or_module_equivalent"] is False
    assert witness["continuous_parameter_introduced"] is False
    assert witness["either_foundation_selected_by_BHSM"] is False
    assert all(item["positive"] for item in witness["foundations"])


def test_fixed_pairing_states_are_inequivalent() -> None:
    witness = weighted_pairing_nonuniqueness_witness()
    assert witness["same_observable_expectations"] == pytest.approx([0.5, 1.0 / 3.0])
    assert witness["states_related_by_algebra_automorphism"] is False
    assert witness["continuous_parameter_introduced"] is False


def test_core_representation_gate_remains_open() -> None:
    payload = core_representation_payload()
    assert payload["GNS_representation_available_after_positive_state"] is True
    assert payload["positive_state_action_owned"] is False
    assert payload["physical_core_representation_derived"] is False
    assert payload["fundamental_core_spinors_derived"] is False


def test_core_pairing_gate_remains_open() -> None:
    payload = core_pairing_payload()
    assert payload["Hilbert_trace_requires_representation_first"] is True
    assert payload["supertrace_requires_action_owned_grading"] is True
    assert payload["KMS_or_thermal_state_justified"] is False
    assert payload["core_scalar_pairing_action_derived"] is False


def test_core_form_gate_uses_representation_theorem_only_conditionally() -> None:
    payload = core_quadratic_form_payload()
    assert payload["action_owned_core_form_found"] is False
    assert payload["representation_theorem_selects_form_or_Hilbert_space"] is False
    assert payload["q_C_derived"] is False
    assert payload["D_C_derived"] is False


def test_attachment_diagnostics_are_adjoint_compatible_and_closed() -> None:
    for order in (2, 3):
        result = attachment_block_diagnostics(order)
        assert result["attachment_adjoint_residual"] < 1e-12
        assert result["total_form_Hermitian_residual"] == 0.0
        assert result["total_form_semibounded"] is True
        assert result["associated_total_operator_self_adjoint"] is True
        assert result["attachment_map_action_owned"] is False


def test_regular_attachment_does_not_become_core_attachment() -> None:
    payload = geometry_core_attachment_payload()
    assert payload["regular_Wentzell_data_define_core_Wentzell_data"] is False
    assert payload["core_trace_map_action_owned"] is False
    assert payload["b_GC_action_owned"] is False
    assert payload["v11_3_term_has_new_boundary_flux"] is False


def test_total_microscopic_action_is_not_claimed() -> None:
    payload = total_action_payload()
    assert payload["regular_q_G_owned"] is True
    assert payload["q_C_owned"] is False
    assert payload["b_GC_owned"] is False
    assert payload["total_q_A_closed_action_owned"] is False
    assert payload["variation_selects_physical_boundary_condition"] is False


def test_theorem_class_boundary_green_form_still_vanishes() -> None:
    payload = boundary_event_payload()
    assert payload["theorem_class_self_adjoint_boundary_domain"]["self_adjoint_extension"] is True
    assert payload["sample_Green_form_norm"] < 1e-12
    assert payload["physical_Theta_A_from_core_action"] is False


def test_event_amplitude_and_central_shift_remain_unresolved() -> None:
    payload = boundary_event_payload()
    assert payload["event_amplitude_from_microscopic_core_action"] is False
    assert payload["central_shift_projective_gauge_resolved"] is False
    assert payload["central_shift_gate"]["classification"].startswith("CONDITIONAL_PROJECTIVE")


def test_reconstruction_is_restriction_not_core_emergence() -> None:
    payload = reconstruction_clock_payload()
    assert payload["exact_regular_restriction_recovery"] is True
    assert payload["core_to_geometry_emergence_map_derived"] is False
    assert payload["locality_from_core_derived"] is False
    assert payload["metric_from_core_derived"] is False
    assert payload["high_excitation_low_reconstructibility_test_eligible"] is False


def test_no_stable_clock_or_joint_Hamiltonian_is_selected() -> None:
    payload = reconstruction_clock_payload()
    assert payload["stable_core_cycle_action_derived"] is False
    assert payload["Delta_chi_clock_derived"] is False
    assert payload["tau_clock_derived"] is False
    assert payload["H_eff_selected"] is False


def test_fifteen_gate_classification_is_outcome_G() -> None:
    payload = fifteen_gate_payload()
    assert payload["T1_core_algebra"].startswith("COMPOSITION_SKELETON_ONLY")
    assert payload["T15_microscopic_foundation_uniqueness"].startswith("FALSE")
    assert payload["outcome"] == OUTCOME
    assert "AT_LEAST_TWO_DISCRETE" in payload["residual_ambiguity"]


def test_completion_gate_preserves_claim_boundary_and_recovery() -> None:
    payload = completion_payload()
    assert payload["primary_verdict"] == PRIMARY_VERDICT
    assert payload["outcome"] == OUTCOME
    assert payload["exact_next_object"] == EXACT_NEXT_OBJECT
    assert payload["core_algebra_action_derived"] is False
    assert payload["total_microscopic_action_derived"] is False
    assert payload["physical_boundary_block_selected"] is False
    assert payload["event_kernel_action_derived"] is False
    assert payload["physical_generator_class_selected"] is False
    assert payload["stable_clock_selected"] is False
    assert payload["H_eff_selected"] is False
    assert payload["regular_BHSM_recovery_exact"] is True
    assert payload["FULL_BHSM_COMPLETE"] is False
    assert payload["validation_passed"] is True


def test_no_parameter_field_frame_or_empirical_input_is_added() -> None:
    payload = completion_payload()
    assert payload["new_continuous_parameter_introduced"] is False
    assert payload["new_fundamental_dynamical_field_introduced"] is False
    assert payload["preferred_frame_introduced"] is False
    assert payload["empirical_inputs_used"] is False


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


def test_artifacts_contain_no_forbidden_phenomenology_or_core_geometry() -> None:
    text = json.dumps(artifact_payloads(), sort_keys=True).lower()
    for forbidden in ("ckm_input", "pmns_input", "measured_mass", "higgs_target", "cosmological_fit"):
        assert forbidden not in text
    assert "integral_over_core_spacetime" not in text


def test_materialization_is_deterministic_and_strict_json(tmp_path: Path) -> None:
    first_paths = materialize(tmp_path)
    first = {path.name: path.read_bytes() for path in first_paths}
    second_paths = materialize(tmp_path)
    second = {path.name: path.read_bytes() for path in second_paths}
    assert first == second
    assert set(first) == set(artifact_payloads())
    assert len(first) == 10
    for name, raw in first.items():
        assert json.loads(raw) == artifact_payloads()[name]
