from bhsm.interface.primitive_charged_incidence import audit_bridge_beta_identity


def test_bridge_and_beta_fractions_are_exact():
    report = audit_bridge_beta_identity()
    assert report["N_16"] == 16
    assert report["g_bridge"] == "16/189"
    assert report["betas"] == {"lepton": "16/1323", "up": "32/1323", "down": "64/1323"}
    assert report["all_exact_identities_pass"] is True

