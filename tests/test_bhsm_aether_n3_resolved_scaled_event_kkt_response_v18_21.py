from bhsm.interface.aether_n3_resolved_scaled_event_kkt_response_v18_21 import completion_payload


def test_v18_21_invalidates_the_coordinatewise_scaled_event_hessian() -> None:
    payload = completion_payload()
    assert not payload["validation_passed"]
    assert payload["status"] == "INVALIDATED"
    result = payload["resolved_scaled_event_kkt_response"]
    assert result["v18_19_uniform_raw_event_hessian"].startswith("INVALIDATED")
    assert result["assembly"]["physical_solve_dimension"] == [376, 376]
    assert not result["assembly"]["left_residual_scaling_applied"]
    assert result["maximum_directional_relative_residual"] > 1.0
