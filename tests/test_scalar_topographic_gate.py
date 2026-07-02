from bhsm.interface.full_action_closure.scalar_topographic_gate import audit_scalar_topographic_gate


def test_scalar_decoupling_remains_open():
    payload = audit_scalar_topographic_gate()
    assert payload["status"] == "OPEN_MISSING_SCALAR_TOPOGRAPHIC_ACTION_SOURCE"
    assert payload["decoupling_status"] == "OPEN_MISSING_SCALAR_TOPOGRAPHIC_DECOUPLING"
