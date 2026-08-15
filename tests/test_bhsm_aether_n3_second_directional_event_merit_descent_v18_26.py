from bhsm.interface.aether_n3_second_directional_event_merit_descent_v18_26 import completion_payload


def test_v18_26_second_directional_event_merit_descent() -> None:
    payload = completion_payload()
    result = payload["second_directional_event_merit_descent"]
    assert not payload["validation_passed"]
    assert payload["status"] == "INVALIDATED"
    assert result["source_state"].startswith("v18.25")
    assert result["physical_solve_dimension"] == [376, 376]
    assert result["event_multiplier_explicit"]
    assert not result["componentwise_monotonicity_required"]
    assert not result["must_remain_on_previous_iterate_path"]
    assert result["maximum_response_relative_residual"] < 2.0e-2
    assert result["selected_true_merit_candidate_pending_child_acceptance"] is None
