from bhsm.interface.gauge_coupling_quantum import audit_ckm_value_source_update


def test_ckm_value_and_exponent_remain_open():
    result = audit_ckm_value_source_update()
    assert result["status"] == "OPEN_MISSING_CKM_COEFFICIENT_VALUE_SOURCE"
    assert result["ckm_exponent_status"] == "not_derived"
