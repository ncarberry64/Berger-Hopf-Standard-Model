from bhsm.interface.boundary_collar_measure.gauge_denominator_source import audit_gauge_denominator_source


def test_denominator_conjunction_fails_closed():
    payload = audit_gauge_denominator_source()
    assert payload["status"] == "OPEN_MISSING_GAUGE_COUPLING_VOLUME_DENOMINATOR"
    assert "unit S^3" in payload["evidence_against"][0]
