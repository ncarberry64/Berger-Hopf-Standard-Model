from bhsm.interface.boundary_collar_measure.gauge_action_attachment_update import audit_gauge_action_attachment_update


def test_gauge_attachment_requires_frame_trace_and_k():
    payload = audit_gauge_action_attachment_update()
    assert payload["status"] == "OPEN_MISSING_GAUGE_COUPLING_ACTION_ATTACHMENT"
    assert "coefficient k" in payload["dependencies"]
