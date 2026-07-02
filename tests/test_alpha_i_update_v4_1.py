from bhsm.interface.boundary_collar_measure.alpha_i_update import audit_alpha_i_update


def test_alpha_i_remains_registered_not_derived():
    payload = audit_alpha_i_update()
    assert payload["status"] == "OPEN_MISSING_ALPHA_I_ACTION_DERIVATION"
    assert payload["candidate_values"]["alpha2"] == "2/(6*pi^2)"
