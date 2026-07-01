from bhsm.interface.primitive_charged_incidence import audit_overlap_4_over_3


def test_overlap_is_conditional_not_action_derived():
    report = audit_overlap_4_over_3()
    assert report["overlap"] == "4/3"
    assert report["status"] == "CONDITIONAL_CHARGED_OVERLAP_4_OVER_3_SOURCE_CANDIDATE"
    assert report["action_derived"] is False

