from bhsm.interface.gauge_coframe_hodge.full_completion_update import audit_full_completion_update
def test_completion_false(): assert audit_full_completion_update()["status"]=="FULL_BHSM_NOT_COMPLETE"
