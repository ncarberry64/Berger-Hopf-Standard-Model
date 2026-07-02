from bhsm.interface.weak_gauge_action_source import audit_normalized_weak_gauge_action_coefficient


def test_overall_action_coefficient_remains_open():
    result = audit_normalized_weak_gauge_action_coefficient()
    assert result["status"] == "OPEN_MISSING_NORMALIZED_WEAK_GAUGE_ACTION_COEFFICIENT"
    assert result["coefficient_value_status"] == "open"
