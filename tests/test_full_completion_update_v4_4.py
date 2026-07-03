from bhsm.interface.berger_hodge_component_map.full_completion_update import audit_full_completion_update

def test_full_completion_remains_open():
    payload = audit_full_completion_update()
    assert payload["status"] == "FULL_BHSM_NOT_COMPLETE"
    assert payload["completion"] is False
