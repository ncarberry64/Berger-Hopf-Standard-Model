from bhsm.interface.weak_gauge_action_source import audit_alpha2_bh_action_source


def test_alpha2_registry_and_action_statuses_are_separate():
    result = audit_alpha2_bh_action_source()
    assert result["status"] == "ARTIFACT_BACKED_ALPHA2_BH_REGISTERED_COUPLING"
    assert result["action_derivation_status"] == "OPEN_MISSING_ALPHA2_BH_ACTION_SOURCE"
    assert result["is_action_derived"] is False
