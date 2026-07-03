from bhsm.interface.gauge_coframe_hodge.denominator_update import audit_denominator_update
def test_denominator_open(): assert audit_denominator_update()["status"]=="OPEN_MISSING_GAUGE_COUPLING_VOLUME_DENOMINATOR"
