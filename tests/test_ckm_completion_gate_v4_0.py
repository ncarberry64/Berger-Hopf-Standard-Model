from bhsm.interface.full_action_closure.ckm_completion_gate import audit_ckm_completion_gate


def test_ckm_form_does_not_imply_value_or_exponent():
    payload = audit_ckm_completion_gate()
    assert payload["coefficient_value_status"] == "OPEN_MISSING_CKM_COEFFICIENT_VALUE_SOURCE"
    assert payload["exponent_status"] == "not_derived"
