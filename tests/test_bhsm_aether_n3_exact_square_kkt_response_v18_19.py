from bhsm.interface.aether_n3_exact_square_kkt_response_v18_19 import completion_payload


def test_v18_19_invalidates_the_uniform_raw_event_hessian() -> None:
    payload = completion_payload()
    assert not payload["validation_passed"]
    assert payload["status"] == "INVALIDATED"
    result = payload["exact_square_kkt_response"]
    assert result["assembly"]["physical_solve_dimension"] == [376, 376]
    assert result["assembly"]["event_multiplier_explicit"]
    assert not result["assembly"]["physical_equations_changed"]
    assert result["maximum_directional_relative_residual"] > 1.0
