from bhsm.interface.ckm_boundary_measure_normalization import audit_measure_coefficient_pair

def test_measure_and_coefficient_are_not_paired_on_same_term():
    p = audit_measure_coefficient_pair()
    assert p["same_term_support"] is False
    assert p["status"] == "OPEN_MISSING_CKM_ACTION_MEASURE_COEFFICIENT_PAIR"
