from bhsm.interface.berger_hodge_component_map.frame_average_update import audit_frame_average_update

def test_three_components_do_not_promote_average():
    assert audit_frame_average_update()["status"] == "OPEN_MISSING_FRAME_AVERAGE_NORMALIZATION"
