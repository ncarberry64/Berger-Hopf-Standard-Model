from bhsm.interface.full_action_closure.neutral_scale_gate import audit_neutral_scale_gate


def test_dimensionless_neutral_structure_does_not_emit_mass():
    payload = audit_neutral_scale_gate()
    assert payload["status"] == "OPEN_MISSING_NEUTRAL_SCALE"
    assert payload["action_normalization_status"] == "OPEN_MISSING_NEUTRAL_ACTION_NORMALIZATION"
    assert "physical neutrino mass" in payload["claim_boundary"]
