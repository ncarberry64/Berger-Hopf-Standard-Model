from bhsm.interface.full_action_closure.full_completion_gate import audit_full_completion_gate


def test_full_completion_requires_every_gate():
    payload = audit_full_completion_gate()
    assert payload["status"] == "FULL_BHSM_NOT_COMPLETE"
    assert payload["completion"] is False
