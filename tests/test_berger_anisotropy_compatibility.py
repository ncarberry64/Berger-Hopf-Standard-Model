from bhsm.interface.berger_frame_weighting.berger_anisotropy_compatibility import audit_berger_anisotropy_compatibility

def test_anisotropy_compatibility_is_explicit_and_conditional():
    payload = audit_berger_anisotropy_compatibility()
    assert payload["status"] == "CONDITIONAL_BERGER_ANISOTROPY_COMPATIBILITY"
    assert "orthonormal coframe" in payload["claim_boundary"]
