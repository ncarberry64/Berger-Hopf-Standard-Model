from bhsm.interface.full_action_closure.boundary_frame_averaging import audit_boundary_frame_averaging


def test_frame_average_does_not_imply_coupling_derivation():
    payload = audit_boundary_frame_averaging()
    assert payload["status"] == "OPEN_MISSING_BOUNDARY_FRAME_AVERAGING"
    assert "gauge trace density" in payload["evidence_against"][0]
