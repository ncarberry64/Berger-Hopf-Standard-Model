import numpy as np

from bhsm.interface.envelopment import boundary_complementarity as complementarity


def test_eta_conjugation_is_an_involution():
    eta = np.array([1 + 2j, 3 - 4j])
    derivative = np.array([[0.2 + 0.1j, -0.4j]])
    c_eta, c_derivative = complementarity.eta_conjugation(eta, derivative)
    cc_eta, cc_derivative = complementarity.eta_conjugation(c_eta, c_derivative)
    assert np.array_equal(cc_eta, eta)
    assert np.array_equal(cc_derivative, derivative)


def test_eta_sector_invariants_and_phase_current_transform_correctly():
    residuals = complementarity.numerical_involution_audit()
    assert max(residuals.values()) < 1.0e-14


def test_full_matter_antimatter_equivalence_fails_closed():
    payload = complementarity.complementarity_payload()
    assert payload["validation_passed"] is True
    gate = payload["physical_gate"]
    assert gate["full_action_invariance"] is None
    assert gate["opposite_additive_gauge_charges"] is None
    assert gate["annihilation_or_reconfiguration_channel"] is None
    assert gate["conventional_antiparticle_fields_retained"] is True
    assert payload["verdict"] == "BHSM_CURRENT_ETA_ACTION_DOES_NOT_ENCODE_ALL_CHARGE_CONJUGATION_DATA"
