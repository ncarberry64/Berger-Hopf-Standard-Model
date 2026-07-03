from bhsm.interface.berger_frame_weighting.g2_update import audit_g2_update

def test_g2_remains_open_without_alpha2():
    assert audit_g2_update()["status"] == "OPEN_MISSING_G2_BH_ACTION_SOURCE"
