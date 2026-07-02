from bhsm.interface.weak_gauge_action_source import audit_g2_bh_action_source


def test_g2_runtime_and_action_statuses_are_separate():
    result = audit_g2_bh_action_source()
    assert result["status"] == "ARTIFACT_BACKED_G2_BH_RUNTIME_INPUT"
    assert result["action_derivation_status"] == "OPEN_MISSING_G2_BH_ACTION_SOURCE"
    assert result["is_action_derived"] is False
