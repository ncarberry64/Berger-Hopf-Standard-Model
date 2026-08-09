from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from bhsm.interface.aether_dynamical_correspondence_v15_1 import (
    EXACT_NEXT_OBJECT,
    PRIMARY_VERDICT,
    action_kernel_payload,
    artifact_payloads,
    boundary_data_on_domain,
    boundary_green_form,
    clocked_hamiltonian,
    commutator_residual,
    completion_payload,
    event_weight,
    generator_nonuniqueness_witness,
    materialize,
    relational_action_density,
    relative_boundary_matrices,
    self_adjoint_domain_diagnostics,
    symbolic_regular_recovery,
    transition_amplitude,
    unitary_event_kernel,
)
from bhsm.interface.completion.aether_encapsulation_correspondence_v15_0 import EventSpan

ROOT = Path(__file__).resolve().parents[1]


def test_unitary_kernel_composes_on_additive_process_depth() -> None:
    generator = np.array([[1.0, 0.25j], [-0.25j, 2.0]], dtype=complex)
    first = unitary_event_kernel(generator, 0.4)
    second = unitary_event_kernel(generator, 0.7)
    combined = unitary_event_kernel(generator, 1.1)
    assert np.linalg.norm(second @ first - combined) < 1e-12
    assert np.linalg.norm(combined.conj().T @ combined - np.eye(2)) < 1e-12


def test_identity_transport_and_v15_0_event_span_interoperate() -> None:
    signature = (("degree_eta", "1"),)
    identity = EventSpan.identity("A", signature)
    generator = np.diag([0.0, 1.0])
    assert identity.process_depth == Fraction(0)
    assert np.array_equal(unitary_event_kernel(generator, float(identity.process_depth)), np.eye(2))


def test_transition_amplitude_uses_boundary_pairing() -> None:
    generator = np.diag([0.0, 1.0])
    incoming = np.array([1.0, 0.0])
    outgoing = np.array([1.0, 0.0])
    assert transition_amplitude(outgoing, generator, 3.0, incoming) == pytest.approx(1.0 + 0.0j)


def test_relational_action_density_is_real_and_weight_has_unit_norm() -> None:
    generator = np.diag([1.0, 2.0])
    state = np.array([1.0 + 1.0j, 0.5j])
    derivative = np.array([0.2j, -0.1])
    density = relational_action_density(state, derivative, generator)
    assert isinstance(density, float)
    assert abs(abs(event_weight(density)) - 1.0) < 1e-14


def test_action_sign_is_consistent_with_declared_schrodinger_kernel() -> None:
    generator = np.diag([1.0, 2.0])
    state = np.array([1.0 + 0.5j, -0.25j])
    solution_derivative = -1j * generator @ state
    assert abs(relational_action_density(state, solution_derivative, generator)) < 1e-12


def test_nonhermitian_generator_is_rejected() -> None:
    with pytest.raises(ValueError):
        unitary_event_kernel(np.array([[0.0, 1.0], [0.0, 0.0]]), 1.0)


def test_relative_boundary_domain_satisfies_exact_extension_criterion() -> None:
    wentzell = np.array([[2.0, 0.5j], [-0.5j, 3.0]], dtype=complex)
    diagnostics = self_adjoint_domain_diagnostics(wentzell)
    assert diagnostics["rank_A_B"] == diagnostics["boundary_dimension"]
    assert diagnostics["ABstar_minus_BAstar_norm"] < 1e-12
    assert diagnostics["self_adjoint_extension"] is True


def test_nonhermitian_wentzell_operator_is_rejected() -> None:
    with pytest.raises(ValueError):
        relative_boundary_matrices(np.array([[1.0, 1.0], [0.0, 1.0]]))


def test_boundary_green_form_vanishes_on_declared_domain() -> None:
    wentzell = np.diag([1.0, 2.0])
    f0, f1 = boundary_data_on_domain(wentzell, (1.0 + 2.0j, -0.5j), (0.3, -0.2j))
    g0, g1 = boundary_data_on_domain(wentzell, (-0.7j, 0.2 + 0.1j), (0.4j, -0.1))
    assert abs(boundary_green_form(f0, f1, g0, g1)) < 1e-12


def test_parent_invariants_must_commute_with_generator() -> None:
    invariant = np.diag([1.0, -1.0])
    compatible = np.diag([0.0, 2.0])
    incompatible = np.array([[0.0, 1.0], [1.0, 0.0]])
    assert commutator_residual(compatible, invariant) == 0.0
    assert commutator_residual(incompatible, invariant) > 1.0


def test_clocked_hamiltonian_is_only_a_calibrated_rescaling() -> None:
    generator = np.diag([0.0, 2.0])
    hamiltonian = clocked_hamiltonian(generator, tau_clock=4.0, hbar=6.0)
    assert np.array_equal(hamiltonian, np.diag([0.0, 3.0]))
    with pytest.raises(ValueError):
        clocked_hamiltonian(generator, tau_clock=0.0)


def test_two_fixed_generators_prove_nonuniqueness_without_a_continuous_parameter() -> None:
    witness = generator_nonuniqueness_witness()
    assert witness["spectra"] == [[0.0, 1.0], [0.0, 2.0]]
    assert max(witness["invariant_commutator_residuals"]) == 0.0
    assert max(witness["unitarity_residuals"]) < 1e-12
    assert witness["kernels_at_unit_depth_differ"] > 0.1
    assert witness["unitarily_equivalent"] is False
    assert witness["continuous_parameter_introduced"] is False
    assert witness["selection_from_existing_BHSM_action"] is False


def test_symbolic_identity_limit_recovers_metric_eta_field_equations_exactly() -> None:
    recovery = symbolic_regular_recovery()
    assert recovery["field_equation_residuals_at_identity"] == ["0", "0", "0"]
    assert recovery["event_action_at_identity"] == "0"
    assert recovery["all_residuals_exactly_zero"] is True
    assert recovery["formal_marker_is_physical_parameter"] is False


def test_action_kernel_is_structural_not_falsely_action_selected() -> None:
    payload = action_kernel_payload()
    assert payload["universal_form_derived_from_additive_cocycle_and_unitary_composition"] is True
    assert payload["physical_generator_action_selected"] is False
    assert payload["process_depth_is_background_time"] is False
    assert payload["ordinary_energy_is_primitive"] is False


def test_completion_gate_preserves_claim_boundary_and_next_object() -> None:
    payload = completion_payload()
    assert payload["primary_verdict"] == PRIMARY_VERDICT
    assert payload["exact_next_object"] == EXACT_NEXT_OBJECT
    assert payload["structural_event_dynamics_theorem_class_derived"] is True
    assert payload["physical_event_law_derived"] is False
    assert payload["requested_next_object_fully_closed"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False
    assert payload["new_continuous_parameter_introduced"] is False
    assert payload["new_fundamental_dynamical_field_introduced"] is False
    assert payload["preferred_frame_introduced"] is False
    assert payload["validation_passed"] is True


def test_no_empirical_or_preferred_frame_inputs_enter_artifacts() -> None:
    payload = completion_payload()
    assert payload["empirical_inputs_used"] is False
    assert payload["preferred_frame_introduced"] is False
    text = json.dumps(artifact_payloads(), sort_keys=True).lower()
    for forbidden in ("ckm_input", "pmns_input", "measured_mass", "cosmological_fit"):
        assert forbidden not in text


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


def test_materialization_is_deterministic_strict_json(tmp_path: Path) -> None:
    first_paths = materialize(tmp_path)
    first = {path.name: path.read_bytes() for path in first_paths}
    second_paths = materialize(tmp_path)
    second = {path.name: path.read_bytes() for path in second_paths}
    assert first == second
    assert set(first) == set(artifact_payloads())
    for name, raw in first.items():
        assert json.loads(raw) == artifact_payloads()[name]
