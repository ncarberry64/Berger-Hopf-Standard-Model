from bhsm.interface.gauge_coupling_quantum import audit_gauge_coupling_registry_pattern


def test_registry_pattern_is_exact_but_not_action_derived():
    result = audit_gauge_coupling_registry_pattern()
    assert result["weights"] == {"w1": 1, "w2": 2, "w3": 7}
    assert result["is_registry_pattern"] is True
    assert result["is_action_derivation"] is False
