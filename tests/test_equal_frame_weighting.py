from bhsm.interface.berger_frame_weighting.equal_frame_weighting import audit_equal_frame_weighting

def test_three_frames_do_not_imply_equal_weights():
    payload = audit_equal_frame_weighting()
    assert payload["status"] == "OPEN_MISSING_EQUAL_FRAME_WEIGHTING"
    assert "sigma_3" in payload["evidence_against"][0]
