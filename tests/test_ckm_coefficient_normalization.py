from bhsm.interface.ckm_boundary_measure_normalization import audit_coefficient_normalization

def test_runtime_coefficient_is_not_action_normalization():
    p = audit_coefficient_normalization()
    assert p["status"] == "OPEN_MISSING_CKM_COEFFICIENT_NORMALIZATION"
    assert "g2_BH_runtime" in p["candidate_coefficient"]
    assert p["depends_on_reference_values"] is False
