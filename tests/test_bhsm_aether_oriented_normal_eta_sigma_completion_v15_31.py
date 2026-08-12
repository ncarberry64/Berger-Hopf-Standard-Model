import numpy as np
import pytest

from bhsm.interface.aether_oriented_normal_eta_sigma_completion_v15_31 import (
    candidate_status,
    completion_payload,
    coupling_derivative,
    coupling_function,
    deterministic_json,
    eta_dimensionless_invariant_and_normal_derivative,
    integration_by_parts_form,
    mixed_variation_diagnostics,
    orientation_reversal_theorem,
)


def test_matching_function_has_required_parity_and_is_regular():
    sigma = np.linspace(-0.5, 0.5, 1001)
    h = np.asarray(coupling_function(sigma))
    hp = np.asarray(coupling_derivative(sigma))
    assert np.max(np.abs(h + h[::-1])) < 1e-11
    assert np.max(np.abs(hp - hp[::-1])) < 1e-11
    assert np.all(np.isfinite(h)) and np.all(np.isfinite(hp))


def test_matching_function_domain_fails_closed():
    with pytest.raises(ValueError):
        coupling_function(0.6)
    with pytest.raises(ValueError):
        coupling_derivative(-0.6)


def test_identity_invariant_has_zero_normal_gradient():
    arrays = eta_dimensionless_invariant_and_normal_derivative(1.0, points=6001)
    interior = slice(10, -10)
    assert np.max(np.abs(np.asarray(arrays["a2_X_eta"])[interior] - 7.0)) < 1e-12
    assert np.max(np.abs(np.asarray(arrays["dchi_a2_X_eta"])[interior])) < 1e-12


def test_mixed_variation_reproduces_exact_leading_source():
    result = mixed_variation_diagnostics(points=20001)
    assert result["maximum_force_residual_over_q"] < 0.02
    assert result["mixed_density_finite"]


def test_covariant_by_parts_form_uses_existing_objects():
    result = integration_by_parts_form()
    assert result["gauge_covariant"]
    assert result["preferred_external_frame"] is False
    assert result["new_field"] is False


def test_orientation_reversal_is_paired_not_coordinate_convention():
    result = orientation_reversal_theorem()
    assert result["product_H_times_normal_derivative_is_even"]
    assert result["H_is_odd_residual"] < 1e-11
    assert result["H_prime_is_even_residual"] < 1e-11


def test_status_preserves_candidate_boundary():
    status = candidate_status()
    assert status["local"] and status["gauge_covariant"]
    assert status["new_continuous_coefficient"] is False
    assert status["recovered_by_variation_of_historical_parent_action"] is False
    assert status["uniqueness_among_all_local_oriented_invariants"] is False


def test_payload_and_deterministic_json():
    payload = completion_payload()
    assert payload["validation_passed"]
    assert payload["FULL_BHSM_COMPLETE"] is False
    first = deterministic_json(payload)
    second = deterministic_json(completion_payload())
    assert first == second
    assert "NaN" not in first and "Infinity" not in first
