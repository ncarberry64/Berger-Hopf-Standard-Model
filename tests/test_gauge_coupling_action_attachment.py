from bhsm.interface.gauge_coupling_quantum import audit_gauge_coupling_action_attachment


def test_action_attaches_neither_quantum_nor_alpha_i():
    result = audit_gauge_coupling_action_attachment()
    assert result["status"] == "OPEN_MISSING_GAUGE_COUPLING_ACTION_ATTACHMENT"
    assert result["does_action_attach_alpha_i"] is False
    assert result["does_action_fix_k"] is False
