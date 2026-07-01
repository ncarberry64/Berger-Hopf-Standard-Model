from bhsm.interface.ckm_boundary_measure_normalization import audit_paired_normalization_rule

def test_hc_does_not_supply_paired_normalization():
    p = audit_paired_normalization_rule()
    assert p["same_measure_source"] is False
    assert p["paired_as_single_action_object"] is False
    assert p["status"] == "OPEN_MISSING_PAIRED_NORMALIZATION_RULE"
