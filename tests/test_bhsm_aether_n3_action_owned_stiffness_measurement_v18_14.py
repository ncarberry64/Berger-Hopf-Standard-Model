from bhsm.interface.aether_n3_action_owned_stiffness_measurement_v18_14 import completion_payload


def test_v18_14_measures_without_changing_physics_or_acceptance() -> None:
    payload = completion_payload()
    assert payload["validation_passed"]
    result = payload["action_owned_stiffness_measurement"]
    assert not result["physical_equations_changed"]
    assert not result["acceptance_conditions_added"]
    assert abs(result["source_exact_376_residual_norm"] - 0.829011042726390) < 5.0e-12
    assert len(result["global_directional_measurements"]) == 8
    assert result["local_dimensionless_curvature_spectrum"]["ratio_to_1e-6"] > 0.0
