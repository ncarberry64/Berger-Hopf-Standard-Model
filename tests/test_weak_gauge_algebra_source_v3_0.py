from bhsm.interface.weak_gauge_action_source import audit_weak_gauge_algebra_source


def test_algebra_is_conditional_not_a_coupling_derivation():
    result = audit_weak_gauge_algebra_source()
    assert result["status"] == "CONDITIONAL_WEAK_GAUGE_ALGEBRA_SOURCE"
    assert "does not derive the coupling value" in result["claim_boundary"]
