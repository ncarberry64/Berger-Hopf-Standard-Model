from bhsm.interface.ckm_boundary_measure_normalization import audit_projector_sandwich_requirement

def test_projectors_are_not_attached_to_ckm_term():
    p = audit_projector_sandwich_requirement()
    assert p["Pi_u_source"] is None and p["Pi_d_source"] is None
    assert p["status"] == "OPEN_MISSING_PROJECTOR_SANDWICH_REQUIREMENT"
