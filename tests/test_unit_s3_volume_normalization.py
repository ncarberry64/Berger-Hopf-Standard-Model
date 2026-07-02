from bhsm.interface.boundary_collar_measure.unit_s3_volume_normalization import audit_unit_s3_volume_normalization


def test_volume_identity_does_not_imply_coupling_derivation():
    payload = audit_unit_s3_volume_normalization()
    assert payload["status"] == "OPEN_MISSING_UNIT_S3_VOLUME_NORMALIZATION"
    assert "not evidence" in payload["claim_boundary"]
