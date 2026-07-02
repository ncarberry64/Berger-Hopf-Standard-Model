from bhsm.interface.weak_gauge_action_source import audit_weak_gauge_trace_normalization


def test_trace_normalization_does_not_fix_coupling():
    result = audit_weak_gauge_trace_normalization()
    assert result["status"] == "CONDITIONAL_WEAK_GAUGE_TRACE_NORMALIZATION"
    assert result["does_trace_fix_coupling_value"] is False
