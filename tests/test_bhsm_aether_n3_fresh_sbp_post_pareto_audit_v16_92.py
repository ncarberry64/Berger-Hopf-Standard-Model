from bhsm.interface.aether_n3_fresh_sbp_post_pareto_audit_v16_92 import completion_payload,post_pareto_audit
def test_scale_closed_without_deleting_row():
    audit=post_pareto_audit();assert audit["owner_transition"]["current_log_scale_norm"]<0.05*audit["owner_transition"]["v16_75_log_scale_norm"]
def test_post_pareto_audit_validates():assert completion_payload()["validation_passed"]
