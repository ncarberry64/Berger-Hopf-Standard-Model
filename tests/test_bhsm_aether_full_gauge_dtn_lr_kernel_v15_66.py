from fractions import Fraction
import math

from bhsm.interface.aether_full_gauge_dtn_lr_kernel_v15_66 import (
    completion_payload,
    deterministic_json,
    full_gauge_dtn_completion,
    gap_reduction,
    inverse_kernel_eigenvalues,
    left_right_group_factors,
    projected_lr_kernel,
)


def test_single_carrier_extension_is_nonlocal_and_coefficient_free():
    result = full_gauge_dtn_completion()
    assert result["new_continuous_coefficient"] is False
    assert result["local_M4_Yang-Mills_action"] is False
    assert result["absolute_nonlocal_kernel_fixed_in_kappa1_units"] is True


def test_inverse_kernel_has_exact_full_gauge_ray():
    result = inverse_kernel_eigenvalues(2)
    assert math.isclose(result["Y"] / result["Sp1"], 3.0 / 5.0, rel_tol=1.0e-14)
    assert result["SU3"] == result["Sp1"]


def test_left_right_group_factors_are_exact():
    result = left_right_group_factors()["pre_Fierz_attraction_weights"]
    assert Fraction(result["up"]) == Fraction(7, 5)
    assert Fraction(result["down"]) == Fraction(13, 10)
    assert Fraction(result["charged_lepton"]) == Fraction(3, 10)
    assert Fraction(result["neutrino"]) == 0


def test_projected_kernel_orders_channels_without_claiming_gap():
    result = projected_lr_kernel(2)
    values = result["channel_kernel_eigenvalues_before_fermion_susceptibility"]
    assert values["up"] > values["down"] > values["charged_lepton"] > values["neutrino"]
    assert result["gap_eigenvalue_computed"] is False
    assert gap_reduction()["first_candidate_channel_by_group_weight"] == "up"


def test_payload_is_deterministic_and_fail_closed():
    payload = completion_payload()
    assert payload["validation_passed"]
    assert payload["FULL_BHSM_COMPLETE"] is False
    first = deterministic_json(payload)
    second = deterministic_json(completion_payload())
    assert first == second
    assert "NaN" not in first and "Infinity" not in first
