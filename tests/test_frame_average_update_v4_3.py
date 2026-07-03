from bhsm.interface.gauge_coframe_hodge.frame_average_update import audit_frame_average_update
def test_average_open(): assert audit_frame_average_update()["status"]=="OPEN_MISSING_FRAME_AVERAGE_NORMALIZATION"
