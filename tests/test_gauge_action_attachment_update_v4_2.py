from bhsm.interface.berger_frame_weighting.gauge_action_attachment_update import audit_gauge_action_attachment_update

def test_gauge_action_attachment_remains_open():
    assert audit_gauge_action_attachment_update()["status"] == "OPEN_MISSING_GAUGE_COUPLING_ACTION_ATTACHMENT"
