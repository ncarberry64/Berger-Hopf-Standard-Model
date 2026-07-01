from bhsm.interface.charged_current_action import audit_normalized_charged_current_action_term


def test_normalized_charged_current_action_term_finds_bounded_candidate():
    payload = audit_normalized_charged_current_action_term()
    assert payload["candidate_term"] == "L_CKM_charged_current_bounded"
    assert "V_CKM_BH" in payload["symbolic_form"]
    assert "+ h.c." in payload["symbolic_form"]
    assert payload["status"] == "OPEN_MISSING_NORMALIZED_CHARGED_CURRENT_ACTION_TERM"


def test_normalized_charged_current_action_term_does_not_promote_target_convention():
    payload = audit_normalized_charged_current_action_term()
    assert payload["adjoint_required"] == "unresolved_by_normalized_action"
    assert "not the complete BHSM 4D Lagrangian" in " ".join(payload["evidence_against"])
    assert "operator domain/codomain" in payload["claim_boundary"]
    assert payload["ckm_fitting_used"] is False
