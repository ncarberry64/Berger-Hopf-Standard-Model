from bhsm.interface.aether_n3_fresh_sbp_event_balanced_metric_v16_87 import EVENT_WEIGHTS,completion_payload
def test_event_weight_is_preconditioner_grid():assert EVENT_WEIGHTS[0]==1.0 and EVENT_WEIGHTS[-1]>1.0
def test_event_balanced_metric_validates():assert completion_payload()["validation_passed"]
