from bhsm.interface.aether_n3_complete_child_persistence_v17_99 import (
    completion_payload,
)


def test_complete_child_persists_with_nonzero_relative_evolution():
    payload = completion_payload()
    assert payload["validation_passed"]
    result = payload["complete_child_persistence"]
    assert result["persistence"]["positive_duration_witness"]
    assert result["persistence"]["all_sampled_states_inside_B_child"]
    assert result["persistence"]["relative_evolution_nonzero"]
    assert not result["persistence"]["eternal_stability_claimed"]
    assert result["evolution"]["maximum_constraint_residual"] < 1.0e-8
    assert result["evolution"]["minimum_eta_Legendre"] > 0.0
    assert not result["decay"]["decay_observed_on_witness_interval"]
    assert payload["direct_N3_solve_authorized_next"]
