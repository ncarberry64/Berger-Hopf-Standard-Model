import math

import numpy as np
import pytest

from bhsm.interface.aether_compact_trace_response_jet_v15_30 import (
    completion_payload,
    deterministic_json,
    identity_trace_response_jet,
    mixed_source_arrays,
    mixed_source_diagnostics,
    parent_locality_audit,
    state_independent_potential_no_go,
)


def test_identity_trace_selects_exact_quadratic_and_quartic_shape():
    jet = identity_trace_response_jet(points=20001)
    assert jet["dimensionless_quadratic_coefficient_a2_A_over_Z"] == -8.0
    assert jet["dimensionless_quartic_coefficient_a2_G_over_Z"] == pytest.approx(
        2.0 * math.pi**2 / 3.0
    )
    assert abs(jet["linear_fit_residual"]) < 1e-6
    assert abs(jet["cubic_fit_residual"]) < 2e-4


def test_leading_mixed_source_matches_solved_near_branch():
    result = mixed_source_diagnostics(points=20001)
    assert result["maximum_error_over_q_on_interior"] < 0.02
    assert result["source_at_sigma_zero_over_q"] == pytest.approx(
        20.0 / (3.0 * math.pi), abs=0.01
    )


def test_mixed_source_is_nonzero_and_finite():
    arrays = mixed_source_arrays(1.001, points=8001)
    source = np.asarray(arrays["required_mixed_source"])
    assert np.all(np.isfinite(source))
    assert np.max(np.abs(source)) > 0.01


def test_single_state_independent_sigma_potential_is_rejected():
    theorem = state_independent_potential_no_go()
    assert theorem["values_disagree"]
    assert abs(theorem["identity_required_a2_U_prime_at_zero"]) < 1e-10
    assert theorem["formed_required_a2_U_prime_at_zero"] > 0.1


def test_parent_locality_boundary_is_fail_closed():
    audit = parent_locality_audit()
    assert audit["branchwise_U_q_is_local_state_independent_parent_action"] is False
    assert audit["unique_local_parent_completion_proved"] is False
    assert audit["arbitrary_continuous_coefficient_in_leading_reduced_source"] is False


def test_invalid_mixed_source_domain_fails_closed():
    with pytest.raises(ValueError):
        mixed_source_arrays(1.0)


def test_payload_passes_without_overclaiming_completion():
    payload = completion_payload()
    assert payload["validation_passed"]
    assert payload["claim_boundary"]["historical_independent_sigma_identified_with_trace"] is False
    assert payload["claim_boundary"]["unique_local_parent_mixed_term_derived"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False


def test_json_is_deterministic_and_finite():
    first = deterministic_json(completion_payload())
    second = deterministic_json(completion_payload())
    assert first == second
    assert "NaN" not in first and "Infinity" not in first
