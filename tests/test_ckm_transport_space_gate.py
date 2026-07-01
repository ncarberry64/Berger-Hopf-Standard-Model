from bhsm.interface.normalized_action_adjoint_pair import audit_ckm_transport_space_gate


def test_ckm_transport_gate_fails_closed_until_action_selection_passes():
    payload = audit_ckm_transport_space_gate()
    assert payload["selection_status"] == "OPEN_MISSING_NORMALIZED_ACTION_ADJOINT_PAIR_SELECTION"
    assert payload["log_transport_lemma_status"] == "ARTIFACT_BACKED_MATHEMATICAL_LEMMA"
    assert payload["transport_space_theorem_status"] == "OPEN_MISSING_CKM_TRANSPORT_SPACE_THEOREM"
    assert payload["application_status"] == "OPEN_MISSING_CKM_LOG_TRANSPORT_AVERAGING_THEOREM"
    assert payload["ckm_exponent_status"] == "not_derived"
    assert payload["ckm_exponent_derived"] is False
    assert payload["selected_space"] is None
    assert payload["selected_dimension"] is None


def test_ckm_transport_gate_records_blocking_conditions():
    payload = audit_ckm_transport_space_gate()
    assert payload["blocking_conditions"]
    assert "normalized action" in payload["blocking_conditions"][0]
    assert "CKM exponent remains open" in payload["claim_boundary"]

