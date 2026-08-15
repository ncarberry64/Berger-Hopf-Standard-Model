from bhsm.interface.aether_n3_directional_event_merit_descent_v18_22 import completion_payload


def test_v18_22_uses_only_validated_directional_event_response() -> None:
    payload = completion_payload()
    assert payload["validation_passed"]
    result = payload["directional_event_merit_descent"]
    assert not result["event_response"]["full_event_hessian_claimed"]
    assert not result["event_response"]["invalidated_v18_19_v18_21_matrices_reused"]
    assert not result["componentwise_monotonicity_required"]
    selected = result["selected_true_merit_candidate_pending_child_acceptance"]
    if selected is not None:
        assert selected["complete_norm_reduction"] > 0.0
        assert selected["eta_minimum"] > 0.0
