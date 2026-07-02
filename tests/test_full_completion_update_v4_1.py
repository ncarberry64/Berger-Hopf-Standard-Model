from bhsm.interface.boundary_collar_measure.full_completion_update import audit_full_completion_update


def test_full_completion_remains_false():
    payload = audit_full_completion_update()
    assert payload["status"] == "FULL_BHSM_NOT_COMPLETE"
    assert payload["completion"] is False
