from __future__ import annotations

import json
import math
from pathlib import Path

from bhsm.interface.completion.pair_wake_neutrino_bvp_v14_55 import (
    EXACT_NEXT_OBJECT,
    MatterImpulse,
    PairWakeState,
    advance_pair_wake,
    apply_common_mode_matter_impulse,
    completion_payload,
    materialize,
    moving_seam_bvp_contract_payload,
    nested_color_neutral_orbit_payload,
    pair_capture_formation_payload,
    pair_wake_dynamics_witness,
    pair_wake_neutrino_action_payload,
    synthetic_periodic_bvp_witness,
    three_harmonic_observability_payload,
    wake_probabilities,
)


def test_three_shape_channels_are_independent_and_noncommuting():
    payload = three_harmonic_observability_payload()
    assert payload["channel_rank"] == 3
    assert payload["rank_three_basis"] is True
    assert payload["at_least_one_noncommuting_pair"] is True
    assert payload["physical_prediction"] is False


def test_synthetic_periodic_bvp_harness_closes_but_is_not_physical():
    payload = synthetic_periodic_bvp_witness()
    assert payload["residual"]["contract_satisfied"] is True
    assert payload["residual"]["max_residual"] < 1e-10
    assert payload["status"].endswith("NOT_A_PHYSICAL_SOLUTION")
    assert payload["physical_coefficients_used"] is False


def test_bvp_contract_keeps_missing_action_inputs_open():
    payload = moving_seam_bvp_contract_payload()
    assert payload["physical_solution_obtained"] is False
    assert len(payload["required_residual_blocks"]) >= 9
    assert "complete trace-class relative heat kernel" in payload["missing_physical_inputs"]


def test_free_pair_cycle_follows_elapsed_proper_time():
    state = PairWakeState(0.0, 0.2, 0.75, (1.0, 0.0, 0.0), ("A", "B"), "fixed")
    advanced = advance_pair_wake(state, 2.0)
    assert math.isclose(advanced.proper_time, 2.0)
    assert math.isclose(advanced.phase, (0.2 + 1.5) % (2.0 * math.pi))
    assert advanced.pair_identity == state.pair_identity
    assert advanced.internal_relation_tag == state.internal_relation_tag


def test_common_mode_impulse_redirects_and_advances_delays_or_resets():
    state = PairWakeState(1.0, 1.0, 0.9, (1.0, 0.0, 0.0), ("A", "B"), "fixed")
    advanced = apply_common_mode_matter_impulse(
        state, MatterImpulse((0.0, 1.0, 0.0), "advance", 0.4)
    )
    delayed = apply_common_mode_matter_impulse(
        advanced, MatterImpulse((0.0, 0.0, 0.0), "delay", 0.2)
    )
    reset = apply_common_mode_matter_impulse(
        delayed, MatterImpulse((0.0, 0.0, 0.0), "reset", 5.1)
    )
    assert advanced.momentum == (1.0, 1.0, 0.0)
    assert math.isclose(advanced.phase, 1.4)
    assert math.isclose(delayed.phase, 1.2)
    assert math.isclose(reset.phase, 5.1)
    assert all(item.pair_identity == state.pair_identity for item in (advanced, delayed, reset))
    assert all(item.internal_relation_tag == state.internal_relation_tag for item in (advanced, delayed, reset))


def test_three_wake_response_weights_are_positive_and_normalized():
    for phase in (0.0, 0.7, 2.4, 5.8):
        probabilities = wake_probabilities(phase)
        assert set(probabilities) == {"electron", "muon", "tau"}
        assert all(value > 0.0 for value in probabilities.values())
        assert math.isclose(sum(probabilities.values()), 1.0, abs_tol=1e-14)


def test_pair_wake_witness_preserves_identity_through_all_phase_kicks():
    payload = pair_wake_dynamics_witness()
    assert payload["pair_identity_preserved"] is True
    assert payload["internal_relation_preserved"] is True
    assert payload["status"].endswith("NOT_A_NEUTRINO_PREDICTION")
    assert len(payload["states"]) == 5


def test_neutrino_action_is_detector_wake_hypothesis_not_PMNS_output():
    payload = pair_wake_neutrino_action_payload()
    assert payload["fixed_inception_data"]["pair_identity"].startswith("Xi_AB")
    assert payload["matter_coupling"]["acts_on"] == "collective motion of the intact pair"
    assert payload["physical_PMNS_emitted"] is False
    assert payload["physical_mass_splittings_emitted"] is False
    assert len(payload["required_empirical_gates"]) >= 6


def test_pair_capture_keeps_core_pair_recognizable_and_remainder_unstable():
    payload = pair_capture_formation_payload()
    assert payload["capture_rules"]["original_pair_remains_recognizable"] is True
    assert payload["capture_rules"]["roles_exchange_during_cycle"] is False
    assert payload["one_body_remainder"]["stable_particle"] is False
    assert "prompt radiation" in payload["one_body_remainder"]["channels"]


def test_nested_color_neutral_contract_requires_local_gauss_law():
    payload = nested_color_neutral_orbit_payload()
    assert payload["global_color_charge_zero_is_sufficient"] is False
    assert any("local nonabelian Gauss law" in item for item in payload["required_equations"])
    assert payload["numerical_hadron_solution_obtained"] is False


def test_completion_gate_fails_closed_and_preserves_frozen_outputs():
    payload = completion_payload()
    assert payload["validation_passed"] is True
    assert payload["Mark_III"] == "NOT_REACHED"
    assert payload["BHSM_physical_completion"] is False
    assert payload["exact_next_object"] == EXACT_NEXT_OBJECT
    assert payload["validation"]["frozen_predictions_changed"] is False
    assert payload["validation"]["physical_PMNS_emitted"] is False
    assert payload["validation"]["USB_untouched"] is True


def test_materialization_is_byte_deterministic(tmp_path: Path):
    first = {path.name: path.read_bytes() for path in materialize(tmp_path)}
    second = {path.name: path.read_bytes() for path in materialize(tmp_path)}
    assert first == second
    assert len(first) == 7
    for payload in first.values():
        json.loads(payload)
