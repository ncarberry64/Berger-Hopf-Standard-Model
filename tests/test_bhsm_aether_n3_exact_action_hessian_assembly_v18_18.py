from bhsm.interface.aether_n3_exact_action_hessian_assembly_v18_18 import completion_payload


def test_v18_18_assembles_the_same_exact_action_covector_response() -> None:
    payload = completion_payload()
    assert payload["validation_passed"]
    result = payload["exact_action_hessian_assembly"]
    assert not result["physical_action_changed"]
    assert not result["event_definition_changed"]
    assert result["base_dimension"] == 375
    assert result["maximum_directional_relative_residual"] < 2.0e-4
