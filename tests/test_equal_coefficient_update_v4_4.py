from bhsm.interface.berger_hodge_component_map.equal_coefficient_update import audit_equal_coefficient_update

def test_hodge_map_does_not_promote_equal_coefficients():
    payload = audit_equal_coefficient_update()
    assert payload["status"] == "OPEN_MISSING_EQUAL_ORTHONORMAL_GAUGE_FRAME_COEFFICIENTS"
    assert payload["raw_frame_weights_status"] == "CONDITIONAL_RAW_BERGER_FRAME_WEIGHTS"
