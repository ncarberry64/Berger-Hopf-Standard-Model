from bhsm.interface.action_derivation_gates import audit_charged_overlap_source


def test_four_thirds_overlap_action_source_remains_open():
    report = audit_charged_overlap_source()
    assert report["status"] == "OPEN_MISSING_CHARGED_OVERLAP_4_OVER_3_ACTION_SOURCE"
    assert report["forbidden_inputs_used"] == []

