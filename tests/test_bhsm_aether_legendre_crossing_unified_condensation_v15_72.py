from bhsm.interface.aether_legendre_crossing_unified_condensation_v15_72 import (
    branch_intermediate_value_theorem,
    completion_payload,
    crossing_theorem,
    joint_absolute_normalization,
)


def test_positive_crossing_before_event() -> None:
    crossing = crossing_theorem()
    assert crossing["existence"]
    assert 0.0 < crossing["numerical_upper_bound_on_L_star"] < 1.0
    assert branch_intermediate_value_theorem()["crosses_L_star_before_firewall"]


def test_gauge_and_yukawa_are_one_output() -> None:
    result = joint_absolute_normalization()
    assert result["Yukawa_and_gauge_share_L_star"]
    assert not result["absolute_gauge_normalization_independently_chosen"]
    assert not result["Yukawa_matrix_independently_chosen"]


def test_payload_validates() -> None:
    payload = completion_payload()
    assert payload["validation_passed"]
    assert payload["claim_boundary"]["joint_crossing_existence_derived"]
