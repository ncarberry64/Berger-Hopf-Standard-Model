import math

from bhsm.interface.aether_round_cap_maxwell_dtn_v15_65 import (
    boundary_effective_operator,
    boundary_radius,
    completion_payload,
    deterministic_json,
    radial_ode_residual,
    static_dtn_eigenvalue,
    transverse_profile,
    transverse_profile_derivative,
    weak_left_right_projection,
)


def test_regular_profiles_solve_static_transverse_radial_equation():
    for mode in (2, 3, 5, 9):
        for rho in (0.05, 0.2, 0.7, 1.2):
            assert abs(radial_ode_residual(rho, mode)) < 1.0e-9


def test_boundary_value_and_normal_derivative_give_exact_dtn_spectrum():
    a = boundary_radius()
    for mode in (2, 3, 4, 8):
        assert math.isclose(transverse_profile(math.pi / 2, mode), 1.0, abs_tol=1.0e-14)
        assert math.isclose(transverse_profile_derivative(math.pi / 2, mode) / a, mode / a)
        assert static_dtn_eigenvalue(mode) == mode / a


def test_exact_bulk_operator_is_nonlocal_order_one_not_local_maxwell():
    result = boundary_effective_operator()
    assert result["pseudodifferential_order"] == 1
    assert result["local_Maxwell_operator_order"] == 2
    assert result["equals_local_M4_Maxwell_action"] is False


def test_owned_weak_kernel_has_zero_left_right_higgs_projection():
    result = weak_left_right_projection()
    assert result["scalar_LR_group_factor"].endswith("=0")
    assert result["weak_DtN_kernel_projects_nontrivially_to_LR_Higgs_channel"] is False


def test_payload_is_deterministic_and_fail_closed():
    payload = completion_payload()
    assert payload["validation_passed"]
    assert payload["FULL_BHSM_COMPLETE"] is False
    first = deterministic_json(payload)
    second = deterministic_json(completion_payload())
    assert first == second
    assert "NaN" not in first and "Infinity" not in first
