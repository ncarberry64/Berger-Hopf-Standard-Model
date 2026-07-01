from bhsm.interface.primitive_charged_incidence import audit_rho_gcd_selection


def test_rho_is_exact_gcd_but_not_action_selected():
    report = audit_rho_gcd_selection()
    assert report["rho_ch"] == 3
    assert report["status"] == "CONDITIONAL_RHO_CH_PRIMITIVE_LATTICE_CANDIDATE"
    assert report["open_status"] == "OPEN_MISSING_ACTION_PRIMITIVE_LATTICE_NORMALIZATION_RULE"
    assert report["action_derived"] is False

