from bhsm.interface.ckm_bounded_interface_normalization import search_ckm_bounded_interface_sources


def test_search_locates_bounded_term_and_records_missing_promotion_sources():
    payload = search_ckm_bounded_interface_sources()
    assert payload["status"] == "ARTIFACT_BACKED_BOUNDED_CKM_INTERFACE_TERM"
    assert "L_CKM_charged_current_bounded" in str(payload["bounded_interface_evidence"])
    assert "boundary/action measure for this term" in payload["missing_sources"]
    assert payload["empirical_inputs_used"] is False
