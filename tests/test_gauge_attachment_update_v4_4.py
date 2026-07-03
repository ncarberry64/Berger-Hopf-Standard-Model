from bhsm.interface.berger_hodge_component_map.gauge_attachment_update import audit_gauge_attachment_update

def test_gauge_attachment_remains_open():
    assert audit_gauge_attachment_update()["status"] == "OPEN_MISSING_GAUGE_TRACE_FRAME_AVERAGE_ATTACHMENT"
