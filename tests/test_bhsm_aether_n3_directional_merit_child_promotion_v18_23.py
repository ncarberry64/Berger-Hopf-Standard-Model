from bhsm.interface.aether_n3_directional_merit_child_promotion_v18_23 import completion_payload


def test_v18_23_promotes_only_after_complete_child_persistence() -> None:
    payload = completion_payload()
    result = payload["directional_merit_child_promotion"]
    if payload["validation_passed"]:
        assert result["global_step"]["complete_norm_reduction"] > 0.0
        assert result["event_to_complete_child"]["maximum_trace_residual"] < 1.0e-9
        assert result["persistence"]["all_steps_valid"]
    else:
        assert payload["status"] == "INVALIDATED"
