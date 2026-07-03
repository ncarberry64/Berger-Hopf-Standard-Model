from bhsm.interface.berger_frame_weighting.ckm_value_update import audit_ckm_value_update

def test_ckm_value_and_exponent_remain_open():
    payload = audit_ckm_value_update()
    assert payload["status"] == "OPEN_MISSING_CKM_COEFFICIENT_VALUE_SOURCE"
    assert payload["ckm_exponent_status"] == "not_derived"
