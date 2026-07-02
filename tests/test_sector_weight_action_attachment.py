from bhsm.interface.full_action_closure.sector_weight_action_attachment import audit_sector_weight_action_attachment


def test_sector_weights_require_action_attachment():
    payload = audit_sector_weight_action_attachment()
    assert payload["candidate_weights"] == {"w1": 1, "w2": 2, "w3": 7}
    assert payload["status"].startswith("OPEN_MISSING_")
