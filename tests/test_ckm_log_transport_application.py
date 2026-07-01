from bhsm.interface.ckm_channel_equivalence import audit_ckm_channel_application


def test_abstract_lemma_does_not_promote_ckm_application():
    report = audit_ckm_channel_application()
    assert report["abstract_log_lemma_status"] == "ARTIFACT_BACKED_MATHEMATICAL_LEMMA"
    assert report["channel_equivalence_status"] == "CONDITIONAL_CKM_CHANNEL_EQUIVALENCE_CANDIDATE"
    assert report["status"] == "OPEN_MISSING_CKM_LOG_TRANSPORT_AVERAGING_THEOREM"
    assert report["selected_N_CKM"] is None
    assert report["ckm_exponent_derived"] is False

