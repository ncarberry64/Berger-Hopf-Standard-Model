from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from bhsm.interface.completion.pair_wake_hybrid_action_v14_56 import (
    CoherentMatterImpulse,
    CoherentPhaseMap,
    EXACT_NEXT_OBJECT,
    HybridPairWakeState,
    apply_coherent_matter_impulse,
    completion_payload,
    dtn_heat_kernel_input_schema_payload,
    free_evolve_hybrid_state,
    hybrid_action_payload,
    materialize,
    phase_kick_contract_payload,
    reset_open_system_payload,
    separability_no_go_payload,
    state_probabilities,
    synthetic_detector_basis,
    synthetic_hybrid_monodromy_witness,
    two_gap_minimum_payload,
    unitarity_residual,
)


def test_separable_action_cannot_transfer_common_mode_impulse_to_cycle():
    payload = separability_no_go_payload()
    assert payload["distributional_result"]["cycle_jump"] == "Delta p_phi = 0"
    assert len(payload["minimum_allowed_couplings"]) >= 3
    assert payload["pair_identity_exchange_required"] is False


def test_coherent_phase_map_is_globally_invertible_when_modulation_below_one():
    phase_map = CoherentPhaseMap(offset=0.2, modulation=0.31, orientation=-0.4)
    assert phase_map.globally_invertible() is True
    for phase in (0.0, 0.7, 2.0, 5.9):
        assert phase_map.jacobian(phase) >= 1.0 - abs(phase_map.modulation)
        assert 0.0 <= phase_map.apply(phase) < 2.0 * math.pi


def test_noninvertible_coherent_phase_map_is_rejected():
    with pytest.raises(ValueError):
        CoherentPhaseMap(offset=0.0, modulation=1.0).validate()


def test_literal_reset_is_reclassified_as_open_system():
    payload = reset_open_system_payload()
    assert payload["jacobian"] == 0.0
    assert payload["invertible"] is False
    assert payload["closed_hamiltonian_action_compatible"] is False
    assert len(payload["allowed_realizations"]) >= 4


def test_one_scalar_phase_is_rank_one_but_three_wake_state_has_two_relative_phases():
    payload = two_gap_minimum_payload()
    assert payload["single_scalar_cycle"]["independent_phase_scale_rank"] == 1
    assert payload["single_scalar_cycle"]["sufficient_for_two_generic_independent_splittings"] is False
    assert payload["minimum_wake_state"]["independent_relative_phase_dimension"] == 2
    assert payload["fixed_pair_condition"] == "D_tau Xi_AB=0"


def test_synthetic_detector_basis_is_unitary():
    basis = synthetic_detector_basis()
    assert unitarity_residual(basis) < 1e-12


def test_hybrid_free_evolution_preserves_probability_and_pair_identity():
    basis = synthetic_detector_basis()
    state = HybridPairWakeState(
        proper_time=0.0,
        scalar_phase=0.1,
        momentum=(1.0, 0.0, 0.0),
        wake_state=(1.0 + 0j, 0j, 0j),
        pair_identity=("A", "B"),
        internal_relation_tag="fixed",
    )
    evolved = free_evolve_hybrid_state(
        state, 1.2, 0.7, (0.0, 0.43, 1.37), basis
    )
    assert math.isclose(sum(state_probabilities(evolved.wake_state)), 1.0, abs_tol=1e-12)
    assert evolved.pair_identity == state.pair_identity
    assert evolved.internal_relation_tag == state.internal_relation_tag


def test_coherent_matter_impulse_changes_collective_motion_and_wake_without_pair_exchange():
    state = HybridPairWakeState(
        proper_time=0.4,
        scalar_phase=0.8,
        momentum=(1.0, 0.0, 0.0),
        wake_state=(1.0 + 0j, 0j, 0j),
        pair_identity=("A", "B"),
        internal_relation_tag="fixed",
    )
    impulse = CoherentMatterImpulse(
        momentum_kick=(0.0, 0.2, 0.0),
        phase_map=CoherentPhaseMap(0.3, 0.2, 0.1),
        wake_angle_12=0.2,
        wake_angle_23=-0.1,
        wake_phase=0.6,
    )
    kicked = apply_coherent_matter_impulse(state, impulse)
    assert kicked.momentum == (1.0, 0.2, 0.0)
    assert kicked.scalar_phase != state.scalar_phase
    assert state_probabilities(kicked.wake_state) != state_probabilities(state.wake_state)
    assert kicked.pair_identity == state.pair_identity
    assert kicked.internal_relation_tag == state.internal_relation_tag


def test_synthetic_hybrid_witness_is_unitary_noncommuting_and_not_physical():
    payload = synthetic_hybrid_monodromy_witness()
    assert payload["basis_unitarity_residual"] < 1e-12
    assert payload["kick_unitarity_residual"] < 1e-12
    assert payload["kick_noncommutator_norm"] > 1e-6
    assert payload["matter_kick_changes_later_detector_probabilities"] is True
    assert payload["pair_identity_preserved"] is True
    assert payload["internal_relation_preserved"] is True
    assert payload["status"].endswith("NOT_A_NEUTRINO_PREDICTION")
    assert payload["physical_PMNS_emitted"] is False
    assert payload["physical_splittings_emitted"] is False


def test_all_synthetic_probability_vectors_normalize():
    payload = synthetic_hybrid_monodromy_witness()
    for total in payload["probability_sums"].values():
        assert math.isclose(total, 1.0, abs_tol=1e-12)


def test_hybrid_action_requires_cross_coupling_and_keeps_cycle_mass_invariant():
    payload = hybrid_action_payload()
    assert "must depend jointly" in payload["mandatory_cross_term"]
    assert payload["coherent_matter_map"]["pair_identity"] == "unchanged"
    assert "complete-cycle" in payload["mass_readout"]
    assert payload["physical_coefficients_derived"] is False


def test_dtn_heat_kernel_gate_rejects_physical_execution_without_bundle():
    payload = dtn_heat_kernel_input_schema_payload()
    assert payload["bundle_present"] is False
    assert payload["physical_BVP_execution_allowed"] is False
    assert "trace-class proof for Delta exp(-t D^2)" in payload["required_relative_spectral_data"]
    assert len(payload["physical_acceptance_conditions"]) >= 5


def test_phase_kick_artifact_records_deterministic_impact_variables():
    payload = phase_kick_contract_payload()
    assert payload["deterministic_witness"]["globally_invertible"] is True
    assert all(sample["jacobian"] > 0.0 for sample in payload["deterministic_witness"]["samples"])
    assert "impact strength" in payload["impact_dependence_required"]


def test_completion_gate_fails_closed_and_preserves_frozen_outputs():
    payload = completion_payload()
    assert payload["validation_passed"] is True
    assert payload["Mark_III"] == "NOT_REACHED"
    assert payload["BHSM_physical_completion"] is False
    assert payload["exact_next_object"] == EXACT_NEXT_OBJECT
    assert payload["validation"]["frozen_predictions_changed"] is False
    assert payload["validation"]["official_prediction_logic_changed"] is False
    assert payload["validation"]["USB_untouched"] is True
    assert payload["validation"]["full_repository_suite_run"] is False


def test_materialization_is_byte_deterministic(tmp_path: Path):
    first = {path.name: path.read_bytes() for path in materialize(tmp_path)}
    second = {path.name: path.read_bytes() for path in materialize(tmp_path)}
    assert first == second
    assert len(first) == 8
    for payload in first.values():
        json.loads(payload)
