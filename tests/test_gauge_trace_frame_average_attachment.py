from bhsm.interface.boundary_collar_measure.gauge_trace_frame_average_attachment import audit_gauge_trace_frame_average_attachment


def test_frame_average_does_not_imply_gauge_attachment():
    payload = audit_gauge_trace_frame_average_attachment()
    assert payload["status"] == "OPEN_MISSING_GAUGE_TRACE_FRAME_AVERAGE_ATTACHMENT"
