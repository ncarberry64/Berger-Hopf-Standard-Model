from bhsm.interface.aether_n3_square_kkt_complete_child_promotion_v18_12 import completion_payload


def test_square_kkt_complete_child_promotion_validates():
    payload = completion_payload()
    assert payload["validation_passed"]
    result = payload["square_kkt_complete_child_promotion"]
    global_step = result["global_step"]
    assert global_step["physical_solve_dimension"] == [376, 376]
    assert global_step["event_multiplier_explicit"]
    assert not global_step["componentwise_monotonicity_required"]
    assert not global_step["must_remain_on_previous_iterate_path"]
    assert global_step["complete_norm_reduction"] > 0.0
    child = result["event_to_complete_child"]
    assert child["chart_recomputed_from_all_child_variables"]
    assert child["maximum_trace_residual"] < 1.0e-9
    assert child["maximum_seven_constraint_residual"] < 1.0e-9
    assert child["attachment_momentum_residual_norm"] < 1.0e-7
    assert child["resolved_dynamic_flux_envelope"] < 2.0e-5
    assert result["persistence"]["nonzero_relative_evolution_retained"]
