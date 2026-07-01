from bhsm.interface.action_derivation_gates import audit_rho_ch_action


def test_rho_ch_three_remains_unselected():
    report = audit_rho_ch_action()
    assert report["status"] == "STRUCTURALLY_MOTIVATED_NOT_DERIVED"
    assert report["selected_value"] is None
    assert report["forbidden_inputs_used"] == []

