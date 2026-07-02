from bhsm.interface.full_action_closure.dimensionful_scale_bridge import audit_dimensionful_scale_bridge


def test_dimensionful_bridge_fails_closed():
    payload = audit_dimensionful_scale_bridge()
    assert payload["status"] == "DIMENSIONFUL_MASS_NOT_AVAILABLE"
    assert payload["candidate_bridge"] == "none"
