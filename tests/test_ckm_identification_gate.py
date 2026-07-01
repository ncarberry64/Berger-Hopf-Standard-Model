from bhsm.interface.ckm_bounded_interface_normalization import audit_ckm_identification_gate


def test_ckm_identification_requires_action_selected_transport():
    payload = audit_ckm_identification_gate()
    assert payload["ckm_identification_status"] == "OPEN_MISSING_CKM_IDENTIFICATION_THEOREM"
    assert "normalized projector-sandwiched action term is missing" in payload["blocking_conditions"]
    assert "V_CKM_BH" in payload["mixing_law_sources"][0]
