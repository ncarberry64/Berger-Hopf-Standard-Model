from bhsm.interface.primitive_charged_incidence import audit_ckm_log_transport


def test_ckm_reciprocal_identity_does_not_promote_transport_theorem():
    report = audit_ckm_log_transport()
    assert report["candidate_exponent"] == "1/16"
    assert report["reciprocal_identity_exact"] is True
    assert report["ckm_exponent_derived"] is False
    assert report["open_status"] == "OPEN_MISSING_CKM_LOG_TRANSPORT_AVERAGING_THEOREM"

