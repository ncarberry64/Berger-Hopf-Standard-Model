from bhsm.interface.ckm_coefficient_form_source import audit_ckm_coefficient_value_source
def test_value_open():
 p=audit_ckm_coefficient_value_source(); assert p["is_runtime_only"] and not p["is_action_derived"] and p["status"]=="OPEN_MISSING_CKM_COEFFICIENT_VALUE_SOURCE"
