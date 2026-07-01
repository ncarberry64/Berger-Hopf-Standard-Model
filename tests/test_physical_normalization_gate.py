from bhsm.interface.primitive_charged_incidence import audit_physical_normalization


def test_physical_normalization_remains_fail_closed():
    report = audit_physical_normalization()
    assert report["status"] == "OPEN_MISSING_PHYSICAL_NORMALIZATION"
    assert report["physical_unit_map_available"] is False
    assert report["dimensionful_prediction_produced"] is False

