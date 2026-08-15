import math

import numpy as np
import pytest

from bhsm.interface.aether_formed_compact_sigma_response_v15_29 import (
    LEADING_SOURCE_COEFFICIENT,
    compact_material_arrays,
    compact_response_diagnostics,
    completion_payload,
    deterministic_json,
    formed_eta_profile,
    orientation_pair_diagnostics,
)


def test_identity_profile_and_trace_are_exactly_normalized():
    profile = formed_eta_profile(1.0, points=6001)
    arrays = compact_material_arrays(1.0, points=6001)
    assert np.max(np.abs(profile["f_eta"] - profile["chi"])) < 1e-15
    assert np.allclose([arrays["sigma"][0], arrays["sigma"][-1]], [-0.5, 0.5])


def test_identity_branch_source_is_zero():
    identity = compact_response_diagnostics(1.0, points=8001)
    assert abs(identity["a2_U_sigma_at_sigma_zero"]) < 1e-10
    assert abs(identity["median_chi"] - math.pi / 2.0) < 1e-10


def test_formed_branch_generates_nonzero_source():
    formed = compact_response_diagnostics(1.01, points=12001)
    assert formed["q"] > 0.0
    assert formed["a2_U_sigma_at_sigma_zero"] > 0.1
    assert formed["potential_reflection_asymmetry"] > 0.01


def test_near_critical_source_matches_exact_linear_coefficient():
    near = compact_response_diagnostics(1.001, points=12001)
    assert near["source_over_q"] == pytest.approx(
        LEADING_SOURCE_COEFFICIENT, abs=0.02
    )


def test_orientation_pair_flips_q_and_source_without_external_frame():
    pair = orientation_pair_diagnostics(1.01, points=8001)
    assert pair["q_minus"] == pytest.approx(-pair["q_plus"])
    assert abs(pair["source_sum_residual"]) < 1e-10
    assert pair["external_preferred_frame_used"] is False
    assert pair["orientation_is_internal_branch_of_retained_radial_solution"]


def test_invalid_domains_fail_closed():
    with pytest.raises(ValueError):
        formed_eta_profile(0.99)
    with pytest.raises(ValueError):
        formed_eta_profile(1.01, points=100)


def test_completion_payload_passes_and_preserves_claim_boundary():
    payload = completion_payload()
    assert payload["validation_passed"]
    assert payload["classification"] == "BHSM_ACTION_COMPLETION_CANDIDATE"
    assert payload["claim_boundary"]["old_parent_action_already_contains_U_q"] is False
    assert payload["claim_boundary"]["historical_independent_sigma_identified_with_trace"] is False
    assert payload["claim_boundary"]["branchwise_U_q_is_one_local_state_independent_parent_potential"] is False
    assert payload["claim_boundary"]["FULL_BHSM_COMPLETE"] is False
    assert payload["no_retuning_certificate"]["new_continuous_coefficients"] == []


def test_json_is_deterministic_and_finite():
    first = deterministic_json(completion_payload())
    second = deterministic_json(completion_payload())
    assert first == second
    assert "NaN" not in first and "Infinity" not in first
