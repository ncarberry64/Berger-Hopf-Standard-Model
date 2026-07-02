from bhsm.interface.weak_gauge_action_source import audit_ckm_value_source_blocker


def test_ckm_value_and_exponent_remain_open():
    result = audit_ckm_value_source_blocker()
    assert result["ckm_coefficient_value_status"] == "OPEN_MISSING_CKM_COEFFICIENT_VALUE_SOURCE"
    assert result["ckm_exponent_status"] == "not_derived"
