from bhsm.interface.ckm_bidirectional_channel import audit_bidirectional_log_transport_application


def test_ckm_exponent_is_not_derived_from_conditional_pair_selection():
    report = audit_bidirectional_log_transport_application()
    assert report["abstract_log_lemma_status"] == "ARTIFACT_BACKED_MATHEMATICAL_LEMMA"
    assert report["adjoint_pair_selection_status"] == "OPEN_MISSING_CKM_ADJOINT_PAIR_SELECTION_RULE"
    assert report["status"] == "OPEN_MISSING_CKM_LOG_TRANSPORT_AVERAGING_THEOREM"
    assert report["candidate_status"] == "CONDITIONAL_CKM_LOG_TRANSPORT_APPLICATION"
    assert report["selected_N_CKM"] is None
    assert report["ckm_exponent_derived"] is False

