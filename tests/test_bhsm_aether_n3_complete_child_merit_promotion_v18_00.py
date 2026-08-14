from bhsm.interface.aether_n3_complete_child_merit_promotion_v18_00 import (
    completion_payload,
    v18_00_selected_raw_vector,
)


def test_complete_child_merit_promotion_validates():
    payload = completion_payload()
    assert payload["validation_passed"]
    result = payload["complete_child_merit_promotion"]
    assert result["promoted_global_state"]["complete_norm_reduction"] > 0.0
    child = result["complete_child_acceptance"]
    assert child["maximum_trace_residual"] < 1.0e-9
    assert child["maximum_seven_constraint_residual"] < 1.0e-9
    assert child["attachment_momentum_residual_norm"] < 1.0e-7
    assert child["dynamic_flux_residual_envelope"] < 2.0e-5
    assert child["next_step_eta_Legendre_minimum"]["minimum"] > 0.0
    assert v18_00_selected_raw_vector().shape == (376,)
    assert not result["acceptance_rule"]["new_KKT_row_added"]
