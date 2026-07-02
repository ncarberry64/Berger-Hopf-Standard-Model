from bhsm.interface.full_action_closure.unified_action_skeleton import build_unified_action_skeleton


def test_unified_action_is_only_a_skeleton():
    payload = build_unified_action_skeleton()
    assert payload["status"] == "CONDITIONAL_UNIFIED_ACTION_SKELETON"
    assert "not a single derived local action" in payload["claim_boundary"]
