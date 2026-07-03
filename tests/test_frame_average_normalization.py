from bhsm.interface.berger_frame_weighting.frame_average_normalization import audit_frame_average_normalization

def test_equal_weights_do_not_imply_division_by_three():
    payload = audit_frame_average_normalization()
    assert payload["status"] == "OPEN_MISSING_FRAME_AVERAGE_NORMALIZATION"
    assert "action-selected factor 1/3" in payload["blocking_conditions"]
