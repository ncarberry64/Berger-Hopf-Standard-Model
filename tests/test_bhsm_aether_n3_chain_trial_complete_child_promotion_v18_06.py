from bhsm.interface.aether_n3_chain_trial_complete_child_promotion_v18_06 import completion_payload


def test_chain_trial_complete_child_promotion_validates():
    payload = completion_payload()
    assert payload["validation_passed"]
    result = payload["chain_trial_complete_child_promotion"]
    assert result["global_step"]["source_jacobian_claim_status"] == "INVALIDATED"
    assert result["global_step"]["complete_norm_reduction"] > 0.0
    child = result["event_to_complete_child"]
    assert child["maximum_trace_residual"] < 1.0e-9
    assert child["maximum_seven_constraint_residual"] < 1.0e-9
    assert child["attachment_momentum_residual_norm"] < 1.0e-7
    assert child["resolved_dynamic_flux_envelope"] < 2.0e-5
    assert result["persistence"]["nonzero_relative_evolution_retained"]
