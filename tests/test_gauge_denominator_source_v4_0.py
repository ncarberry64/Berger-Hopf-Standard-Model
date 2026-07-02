from bhsm.interface.full_action_closure.gauge_denominator_source import audit_gauge_denominator_source


def test_volume_identity_alone_does_not_derive_couplings():
    payload = audit_gauge_denominator_source()
    assert payload["status"] == "OPEN_MISSING_GAUGE_COUPLING_VOLUME_DENOMINATOR"
    assert "action must use it" in payload["claim_boundary"]
