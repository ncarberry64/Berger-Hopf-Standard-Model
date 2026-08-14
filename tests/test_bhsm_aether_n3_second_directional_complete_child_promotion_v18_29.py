from bhsm.interface.aether_n3_second_directional_complete_child_promotion_v18_29 import completion_payload


def test_v18_29_second_directional_complete_child_promotion() -> None:
    payload = completion_payload()
    result = payload["second_directional_complete_child_promotion"]
    assert payload["validation_passed"]
    assert payload["status"] == "VALIDATED"
    assert result["global_step"]["complete_norm_reduction"] > 0.0
    assert result["event_to_complete_child"]["local_chart_rank"] == 14
    assert result["persistence"]["all_steps_valid"]
    assert result["persistence"]["nonzero_relative_evolution_retained"]
