from bhsm.interface.full_action_closure.alpha_i_action_gate import audit_alpha_i_action_gate


def test_registry_pattern_does_not_promote_alpha_i():
    payload = audit_alpha_i_action_gate()
    assert payload["promoted_from"] == "ARTIFACT_BACKED_GAUGE_COUPLING_REGISTRY_PATTERN"
    assert payload["status"] == "OPEN_MISSING_ALPHA_I_ACTION_DERIVATION"
