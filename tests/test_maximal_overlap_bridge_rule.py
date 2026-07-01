from bhsm.interface.action_lemmas import audit_maximal_overlap_bridge_rule


def test_bridge_identity_passes_but_selection_rule_remains_open():
    report = audit_maximal_overlap_bridge_rule()
    assert report["overlap"] == "4/3"
    assert report["g_bridge"] == "16/189"
    assert report["exact_conditional_identity"] is True
    assert report["status"] == "OPEN_MISSING_ACTION_RULE_THAT_BRIDGE_USES_MAX_PRIMITIVE_OVERLAP"
    assert report["action_derived"] is False

