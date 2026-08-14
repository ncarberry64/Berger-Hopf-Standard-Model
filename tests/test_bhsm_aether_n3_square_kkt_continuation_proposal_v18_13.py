from bhsm.interface.aether_n3_square_kkt_continuation_proposal_v18_13 import completion_payload


def test_v18_13_classifies_square_kkt_trials_without_solver_physics() -> None:
    payload = completion_payload()
    assert payload["validation_passed"]
    result = payload["square_kkt_continuation_proposal"]
    assert result["proposal_model"]["physical_solve_dimension"] == [376, 376]
    assert result["proposal_model"]["event_multiplier_explicit"]
    assert not result["componentwise_monotonicity_required"]
    assert not result["must_remain_on_previous_iterate_path"]
    selected = result["selected_true_merit_candidate_pending_child_acceptance"]
    if selected is not None:
        assert selected["complete_norm_reduction"] > 0.0
        assert selected["eta_minimum"] > 0.0
