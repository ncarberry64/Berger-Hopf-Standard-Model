from bhsm.interface.aether_scale_child_ownership_audit_v16_78 import completion_payload,scale_ownership_audit

def test_scale_ownership_does_not_delete_a_physical_residual():
    audit=scale_ownership_audit()
    assert audit["configuration_ownership"]["reset_log_scale_is_KKT_unknown"] is False
    assert audit["measured_frontier"]["free_log_scale_nodes"]==audit["measured_frontier"]["log_scale_stationarity_rows"]
    assert audit["verdict"]["continue_current_metric_Gauss_Newton"] is True

def test_scale_child_ownership_audit_validates():assert completion_payload()["validation_passed"]
