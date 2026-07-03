from bhsm.interface.berger_hodge_component_map.denominator_update import audit_denominator_update

def test_volume_denominator_remains_open():
    assert audit_denominator_update()["status"] == "OPEN_MISSING_GAUGE_COUPLING_VOLUME_DENOMINATOR"
