from bhsm.interface.action_lemmas import audit_primitive_lattice_rule


def test_gcd_remains_conditional_on_missing_action_quotient():
    report = audit_primitive_lattice_rule()
    assert report["rho_ch"] == 3
    assert report["primitive_representative"] == [1, 2, 4]
    assert report["status"] == "OPEN_MISSING_ACTION_PRIMITIVE_LATTICE_NORMALIZATION_RULE"
    assert report["action_derived"] is False

