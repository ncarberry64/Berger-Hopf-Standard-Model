from bhsm.interface.berger_frame_weighting.denominator_update import audit_denominator_update

def test_denominator_does_not_promote_without_all_dependencies():
    payload = audit_denominator_update()
    assert payload["status"] == "OPEN_MISSING_GAUGE_COUPLING_VOLUME_DENOMINATOR"
    assert "unit S3 volume" in payload["dependencies"]
