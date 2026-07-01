from bhsm.interface.ckm_bounded_interface_normalization import audit_ckm_bounded_interface_term


def test_bounded_interface_term_is_artifact_backed_but_not_action_selected():
    payload = audit_ckm_bounded_interface_term()
    assert payload["term_name"] == "L_CKM_charged_current_bounded"
    assert payload["status"] == "ARTIFACT_BACKED_BOUNDED_CKM_INTERFACE_TERM"
    assert "sector projector sandwich" in payload["what_is_not_proven"]
    assert "not automatically" in payload["claim_boundary"]
