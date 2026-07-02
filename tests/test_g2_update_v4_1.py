from bhsm.interface.boundary_collar_measure.g2_update import audit_g2_update


def test_g2_requires_action_derived_alpha2():
    payload = audit_g2_update()
    assert payload["status"] == "OPEN_MISSING_G2_BH_ACTION_SOURCE"
