from bhsm.interface.aether_n3_action_curvature_coordinate_map_v18_15 import completion_payload


def test_v18_15_coordinate_map_is_physically_equivalent() -> None:
    payload = completion_payload()
    assert payload["validation_passed"]
    result = payload["action_curvature_coordinate_map"]
    assert result["global_transform"]["invertible"]
    assert not result["derivation"]["left_residual_scaling_applied"]
    assert not result["equivalence"]["physical_equations_changed"]
    assert not result["equivalence"]["event_definition_changed"]
    assert not result["equivalence"]["complete_child_acceptance_changed"]
