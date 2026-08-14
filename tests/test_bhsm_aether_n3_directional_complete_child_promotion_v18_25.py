from bhsm.interface.aether_n3_directional_complete_child_promotion_v18_25 import completion_payload


def test_v18_25_promotes_only_the_recomputed_persistent_child() -> None:
    payload = completion_payload()
    assert payload["validation_passed"]
    result = payload["directional_complete_child_promotion"]
    assert result["global_step"]["complete_norm_reduction"] > 0.0
    assert result["event_to_complete_child"]["chart_recomputed_from_all_child_variables"]
    assert result["persistence"]["all_steps_valid"]
    assert result["persistence"]["nonzero_relative_evolution_retained"]
