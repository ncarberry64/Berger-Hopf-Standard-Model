from bhsm.interface.aether_n3_fine_directional_merit_bracket_v18_27 import completion_payload


def test_v18_27_fine_directional_merit_bracket() -> None:
    payload = completion_payload()
    result = payload["fine_directional_merit_bracket"]
    assert payload["validation_passed"]
    assert payload["status"] == "VALIDATED"
    assert result["source_state"].startswith("v18.25")
    assert result["source_direction_response_validated"]
    assert result["physical_solve_dimension"] == [376, 376]
    assert result["event_multiplier_explicit"]
    assert not result["componentwise_monotonicity_required"]
    assert not result["must_remain_on_previous_iterate_path"]
