from bhsm.interface.charged_current_action import audit_ckm_transport_space_application_gate


def test_ckm_transport_space_application_gate_keeps_exponent_unpromoted():
    payload = audit_ckm_transport_space_application_gate()
    assert payload["charged_current_space_status"] == "OPEN_MISSING_CHARGED_CURRENT_TRANSPORT_SPACE"
    assert payload["ckm_identification_status"] == "OPEN_MISSING_CKM_TRANSPORT_SPACE_THEOREM"
    assert payload["application_status"] == "OPEN_MISSING_CKM_LOG_TRANSPORT_AVERAGING_THEOREM"
    assert payload["ckm_exponent_status"] == "not_derived"
    assert payload["ckm_exponent_derived"] is False
    assert payload["selected_N"] is None


def test_ckm_transport_space_application_gate_requires_selected_space():
    payload = audit_ckm_transport_space_application_gate()
    blockers = " ".join(payload["blocking_conditions"])
    assert "charged-current transport space is not action-selected" in blockers
    assert "CKM is not proven" in blockers

