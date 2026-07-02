from bhsm.interface.gauge_coupling_quantum import audit_universal_gauge_coupling_quantum


def test_universal_quantum_fails_closed_without_attachment():
    result = audit_universal_gauge_coupling_quantum()
    assert result["status"] == "OPEN_MISSING_UNIVERSAL_GAUGE_COUPLING_QUANTUM"
    assert result["action_attachment_status"] == "OPEN_MISSING_GAUGE_COUPLING_ACTION_ATTACHMENT"
    assert result["is_action_derived"] is False
