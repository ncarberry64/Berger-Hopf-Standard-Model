from bhsm.interface.normalized_action_adjoint_pair import audit_hermitian_charged_current_action_rule


def test_hermitian_rule_is_separated_from_ckm_exponent_derivation():
    payload = audit_hermitian_charged_current_action_rule()
    assert payload["status"] == "CONDITIONAL_HERMITIAN_CHARGED_CURRENT_ACTION_RULE"
    assert "OPEN" in payload["ckm_transport_application"]
    assert "does not by itself derive the CKM exponent" in payload["claim_boundary"]
    assert any("h.c." in item or "Hermitian" in item for item in payload["evidence_for"])


def test_hermitian_rule_keeps_bhsm_action_application_open():
    payload = audit_hermitian_charged_current_action_rule()
    assert "OPEN" in payload["bhsm_charged_current_rule"]
    assert payload["ckm_fitting_used"] is False
    assert payload["charged_mass_fitting_used"] is False

