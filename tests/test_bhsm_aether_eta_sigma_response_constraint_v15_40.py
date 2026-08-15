import math

import numpy as np

from bhsm.interface.aether_eta_sigma_response_constraint_v15_40 import (
    child_system_reclassification,
    completion_payload,
    constrained_tangent_theorem,
    deterministic_json,
    finite_difference_tangent_check,
    identity_join_recovery,
    normalized_join_response,
    response_constraint_action,
)


def test_normalized_response_has_fixed_endpoints_and_unit_jump():
    chi = np.linspace(0.0, math.pi / 2.0, 4001)
    result = normalized_join_response(chi, chi + 0.05 * np.sin(2 * chi))
    sigma = np.asarray(result["sigma"])
    assert abs(sigma[0] + 0.5) < 1e-14
    assert abs(sigma[-1] - 0.5) < 1e-14
    assert np.all(np.diff(sigma) >= 0.0)


def test_identity_reciprocal_join_trace_is_recovered():
    result = identity_join_recovery(8001)
    assert math.isclose(result["normalization"], math.pi / 16, rel_tol=2e-8)
    assert result["identity_join_trace_recovered"]
    assert result["reflection_residual"] < 1e-12


def test_normalized_response_tangent_matches_finite_difference():
    result = finite_difference_tangent_check(8001)
    assert result["normalized_tangent_verified"]
    assert result["left_endpoint_residual"] < 1e-12
    assert result["right_endpoint_residual"] < 1e-12


def test_skin_only_negative_mode_is_not_on_complete_constraint_tangent():
    result = constrained_tangent_theorem()
    assert result["independent_skin_translation"][
        "satisfies_linearized_constraint"
    ] is False
    assert result["mode_removed_by_actual_constraint"]
    assert result["stable_auxiliary_Schur_argument_used"] is False


def test_constraint_adds_no_physical_field_or_coefficient():
    result = response_constraint_action()
    assert result["new_physical_field"] is False
    assert result["new_continuous_coefficient"] is False
    assert result["lambda_sigma"] == "nonpropagating_constraint_multiplier"


def test_fixed_profile_child_is_reclassified_and_FR_domain_preserved():
    result = child_system_reclassification()
    assert result["derived_material_field"].startswith("sigma=C_J")
    assert result["v15_34_fixed-profile_off-seam_minimum"].startswith(
        "CONDITIONAL"
    )
    assert result["v15_37_zero-current_FR_domain"] == "PRESERVED"


def test_payload_is_deterministic_and_keeps_joint_solution_active():
    payload = completion_payload()
    assert payload["validation_passed"]
    assert payload["claim_boundary"]["complete_child_material_constraint_derived"]
    assert payload["claim_boundary"]["physical_child_scale_derived"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False
    first = deterministic_json(payload)
    second = deterministic_json(completion_payload())
    assert first == second
    assert "NaN" not in first and "Infinity" not in first
