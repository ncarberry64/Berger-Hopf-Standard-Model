from bhsm.interface.ckm_boundary_measure_normalization import audit_normalized_ckm_action_candidate

def test_normalized_action_candidate_fails_closed():
    p = audit_normalized_ckm_action_candidate()
    assert p["bounded_interface_status"] == "ARTIFACT_BACKED_BOUNDED_CKM_INTERFACE_TERM"
    assert p["promotion_status"] == "not_promoted"
    assert p["status"] == "OPEN_MISSING_NORMALIZED_CKM_ACTION_CANDIDATE"
