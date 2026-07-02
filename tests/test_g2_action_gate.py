from bhsm.interface.full_action_closure.g2_action_gate import audit_g2_action_gate


def test_g2_requires_action_derived_alpha2():
    payload = audit_g2_action_gate()
    assert payload["status"] == "OPEN_MISSING_G2_BH_ACTION_SOURCE"
    assert "conditional only" in payload["candidate_g2"]
