import math

from bhsm.interface.aether_unified_heat_pushforward_gap_v15_70 import (
    completion_payload,
    critical_heat_parameter,
    deterministic_json,
    geometric_heat_parameter,
    largest_static_inverse_kernel_bound,
    regulated_dimensionless_susceptibility,
    rejection_semantics,
    unified_heat_candidate_contract,
    up_channel_gap_norm_bound,
)


def test_geometric_heat_regulator_is_positive_and_convergent():
    t = geometric_heat_parameter()
    assert t > 0.0
    assert regulated_dimensionless_susceptibility(t) > 0.0
    assert regulated_dimensionless_susceptibility(0.5 * t) > regulated_dimensionless_susceptibility(t)


def test_static_transverse_plus_coulomb_inverse_kernel_bound():
    result = largest_static_inverse_kernel_bound()
    assert result["transverse_maximum"] > 0.0
    assert result["Coulomb_maximum"] > result["transverse_maximum"]
    assert math.isclose(
        result["sum_bound"], result["transverse_maximum"] + result["Coulomb_maximum"]
    )


def test_same_pushforward_heat_candidate_is_strictly_subcritical():
    result = unified_heat_candidate_contract()
    assert result["same_regulator_applied_before_gauge_and_LR_source_derivatives"] is True
    assert result["up_channel_gap_operator_norm_upper_bound"] < 1.0e-3
    assert result["supercritical_even_at_upper_bound"] is False
    assert result["candidate_generates_nonzero_composite_Yukawa"] is False


def test_critical_cutoff_is_far_above_action_scale_and_no_split_rescue_occurs():
    result = unified_heat_candidate_contract()
    assert critical_heat_parameter() < geometric_heat_parameter()
    assert result["critical_effective_cutoff_times_R4"] > 50.0
    rejection = rejection_semantics()
    assert rejection["independent_Yukawa_added_after_rejection"] is False
    assert rejection["independent_gauge_retuning_after_rejection"] is False


def test_payload_is_deterministic_and_fail_closed():
    payload = completion_payload()
    assert payload["validation_passed"]
    assert payload["FULL_BHSM_COMPLETE"] is False
    first = deterministic_json(payload)
    second = deterministic_json(completion_payload())
    assert first == second
    assert "NaN" not in first and "Infinity" not in first
