from bhsm.interface.boundary_collar_measure.three_boundary_frame_directions import audit_three_boundary_frame_directions


def test_three_frames_do_not_imply_average():
    payload = audit_three_boundary_frame_directions()
    assert payload["status"] == "ARTIFACT_BACKED_THREE_BOUNDARY_FRAME_DIRECTIONS"
    assert "does not select" in payload["claim_boundary"]
