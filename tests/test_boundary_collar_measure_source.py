from bhsm.interface.boundary_collar_measure.boundary_collar_measure_source import audit_boundary_collar_measure_source


def test_measure_source_is_conditional_and_does_not_fix_unit_s3():
    payload = audit_boundary_collar_measure_source()
    assert payload["status"] == "CONDITIONAL_BOUNDARY_COLLAR_MEASURE_SOURCE"
    assert "BHSM-specific boundary geometry" in payload["blocking_conditions"]
