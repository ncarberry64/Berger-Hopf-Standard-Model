from bhsm.interface.weak_gauge_action_source import audit_normalized_weak_gauge_action_skeleton


def test_skeleton_records_unfixed_overall_coefficient():
    result = audit_normalized_weak_gauge_action_skeleton()
    assert result["status"] == "CONDITIONAL_NORMALIZED_WEAK_GAUGE_ACTION_SKELETON"
    assert "overall coefficient k is not fixed" in result["evidence_against"]
