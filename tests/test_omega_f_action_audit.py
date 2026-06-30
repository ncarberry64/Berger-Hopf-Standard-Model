from bhsm.interface.action_derivation_gates import audit_omega_f_action


def test_omega_f_is_not_promoted_without_complete_action():
    report = audit_omega_f_action()
    assert report["status"] == "STRUCTURALLY_INTEGRATED_NOT_ACTION_DERIVED"
    assert report["complete_action_derivation"] is False
    assert report["forbidden_inputs_used"] == []

