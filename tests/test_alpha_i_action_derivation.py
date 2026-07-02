from bhsm.interface.gauge_coupling_quantum import audit_alpha_i_action_derivation


def test_all_alpha_i_action_derivations_remain_open():
    result = audit_alpha_i_action_derivation()
    assert result["status"] == "OPEN_MISSING_ALPHA_I_ACTION_DERIVATION"
    assert result["is_action_derived"] is False
    assert all(result[key].startswith("OPEN_MISSING") for key in ("alpha1_status", "alpha2_status", "alpha3_status"))
