from bhsm.interface.gauge_coupling_quantum import audit_gauge_coupling_volume_denominator


def test_volume_denominator_source_remains_open():
    result = audit_gauge_coupling_volume_denominator()
    assert result["status"] == "OPEN_MISSING_GAUGE_COUPLING_VOLUME_DENOMINATOR"
    assert result["S3_volume_sources"] == []
    assert "does not by itself derive" in result["claim_boundary"]
