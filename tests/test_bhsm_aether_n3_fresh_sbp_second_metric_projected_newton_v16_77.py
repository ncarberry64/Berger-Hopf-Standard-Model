from bhsm.interface.aether_n3_fresh_sbp_second_metric_projected_newton_v16_77 import completion_payload,v16_76_selected_raw_vector

def test_v16_76_state_has_complete_dimension():assert v16_76_selected_raw_vector().shape==(376,)
def test_second_metric_projected_step_validates():assert completion_payload()["validation_passed"]
