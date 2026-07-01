from bhsm.interface.ckm_boundary_measure_normalization import audit_boundary_measure_source

def test_boundary_measure_is_symbolic_conditional_only():
    p = audit_boundary_measure_source()
    assert p["candidate_measure"] == "dmu_boundary"
    assert p["status"] == "CONDITIONAL_BOUNDARY_MEASURE_SOURCE"
    assert "A boundary measure alone" in p["claim_boundary"]
