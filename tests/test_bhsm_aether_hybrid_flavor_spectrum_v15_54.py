import numpy as np

from bhsm.interface import aether_hybrid_flavor_spectrum_v15_54 as flavor


def test_round_berger_seed_and_triality_projectors():
    radius = flavor.RADIUS0
    assert abs(
        flavor.berger_scalar_eigenvalue(6, 0, radius, radius) * radius**2 - 48
    ) < 1e-12
    projectors = flavor.triality_projectors()
    assert np.allclose(sum(projectors), np.eye(3))
    for projector in projectors:
        assert np.allclose(projector @ projector, projector)


def test_current_action_predicts_canonical_no_mixing():
    result = flavor.canonical_mixing_theorem()
    assert result["all_action-owned_sector_operators_commute"]
    assert np.allclose(result["CKM"], np.eye(3))
    assert np.allclose(result["PMNS"], np.eye(3))
    assert result["Jarlskog_invariant"] == 0.0
    assert result["such_an_operator_present_in_current_completed_action"] is False


def test_spectral_seeds_are_not_relabelled_physical_masses():
    payload = flavor.completion_payload()
    assert payload["validation_passed"]
    assert payload["claim_boundary"]["Berger_excitation_spectrum_derived"]
    assert payload["claim_boundary"]["physical_fermion_masses_derived"] is False
    assert payload["scale_ledger"]["external_calibration_used"] is False


def test_payload_json_is_deterministic():
    payload = flavor.completion_payload()
    assert flavor.deterministic_json(payload) == flavor.deterministic_json(
        flavor.completion_payload()
    )
