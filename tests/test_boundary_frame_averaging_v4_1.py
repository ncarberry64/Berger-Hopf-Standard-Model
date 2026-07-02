from bhsm.interface.boundary_collar_measure.boundary_frame_averaging import audit_boundary_frame_averaging


def test_action_selected_frame_average_remains_open():
    payload = audit_boundary_frame_averaging()
    assert payload["status"] == "OPEN_MISSING_BOUNDARY_FRAME_AVERAGING"
    assert "action-selected factor 1/3" in payload["blocking_conditions"]
