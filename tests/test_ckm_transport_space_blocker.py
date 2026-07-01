from bhsm.interface.ckm_boundary_measure_normalization import audit_transport_space_blocker

def test_transport_and_exponent_remain_open():
    p = audit_transport_space_blocker()
    assert p["selected_transport_space"] is None and p["selected_dimension"] is None
    assert p["status"] == "OPEN_MISSING_CKM_TRANSPORT_SPACE_SELECTION"
    assert p["ckm_exponent_status"] == "not_derived"
