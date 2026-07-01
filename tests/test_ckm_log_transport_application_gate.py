from bhsm.interface.action_lemmas import audit_ckm_log_transport_application


def test_abstract_lemma_does_not_derive_ckm_application():
    report = audit_ckm_log_transport_application()
    assert report["abstract_lemma_status"] == "ARTIFACT_BACKED_MATHEMATICAL_LEMMA"
    assert report["candidate_exponent"] == "1/16"
    assert report["N_16_equivalent_bilinear_channels_proven"] is False
    assert report["application_gate_passes"] is False
    assert report["ckm_exponent_derived"] is False
    assert report["status"] == "OPEN_MISSING_CKM_LOG_TRANSPORT_AVERAGING_THEOREM"

