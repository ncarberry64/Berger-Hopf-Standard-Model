from bhsm.interface.berger_hodge_component_map.downstream_update import audit_downstream_update

def test_downstream_sources_are_not_promoted():
    payload = audit_downstream_update()
    assert payload["alpha_i_status"] == "OPEN_MISSING_ALPHA_I_ACTION_DERIVATION"
    assert payload["g2_status"] == "OPEN_MISSING_G2_BH_ACTION_SOURCE"
    assert payload["ckm_value_status"] == "OPEN_MISSING_CKM_COEFFICIENT_VALUE_SOURCE"
    assert payload["ckm_exponent_status"] == "not_derived"
