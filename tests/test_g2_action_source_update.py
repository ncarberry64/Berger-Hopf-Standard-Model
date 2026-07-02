from bhsm.interface.gauge_coupling_quantum import audit_g2_action_source_update


def test_g2_remains_runtime_not_action_derived():
    result = audit_g2_action_source_update()
    assert result["status"] == "OPEN_MISSING_G2_BH_ACTION_SOURCE"
    assert result["g2_runtime_status"] == "ARTIFACT_BACKED_G2_BH_RUNTIME_INPUT"
    assert result["does_action_fix_g2"] is False
