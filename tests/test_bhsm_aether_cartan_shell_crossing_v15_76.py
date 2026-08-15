from bhsm.interface.aether_cartan_shell_crossing_v15_76 import (
    clifford_coefficient_contract,
    completion_payload,
    leading_crossing_estimate,
    shell_geometry,
)


def test_cartan_coefficient_is_fixed() -> None:
    result = clifford_coefficient_contract()
    assert result["c_EC"] == 0.75
    assert not result["new_coefficient"]


def test_actual_shell_has_nonzero_zero_mode() -> None:
    shell = shell_geometry()
    assert shell["Legendre_quadratic_coefficient"] > 0.0
    assert shell["u0_shell_nonzero"]


def test_leading_crossing_is_finite_and_up_first() -> None:
    result = leading_crossing_estimate()
    assert 0.0 < result["up_leading_epsilon_star"] < 1.0e-6
    assert result["first_channel"] == "up"
    assert completion_payload()["validation_passed"]
