from bhsm.interface.full_action_closure.gauge_action_coefficient_k import audit_gauge_action_coefficient_k


def test_k_remains_open_without_action_source():
    payload = audit_gauge_action_coefficient_k()
    assert payload["status"] == "OPEN_MISSING_GAUGE_ACTION_COEFFICIENT_K"
    assert payload["candidate_k"] == "unspecified"
