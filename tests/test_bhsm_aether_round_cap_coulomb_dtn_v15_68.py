import math

from bhsm.interface.aether_round_cap_coulomb_dtn_v15_68 import (
    boundary_derivative_exact,
    completion_payload,
    deterministic_json,
    electric_dtn_contract,
    electric_dtn_eigenvalue,
    electric_profile,
    electric_profile_derivatives,
    electric_radial_residual,
    full_static_gauge_kernel_correction,
)


def test_hypergeometric_electric_profiles_solve_maxwell_radial_equation():
    for ell in (1, 2, 3, 6):
        for rho in (0.08, 0.3, 0.8, 1.2):
            assert abs(electric_radial_residual(rho, ell)) < 2.0e-9


def test_boundary_value_and_derivative_have_exact_limits():
    step = 1.0e-4
    for ell in (1, 2, 4, 8):
        assert abs(electric_profile(math.pi / 2.0 - step / 2.0, ell) - 1.0) < 5.0e-4
        derivative = (
            2.0 * electric_profile_derivatives(math.pi / 2.0 - step / 2.0, ell)[1]
            - electric_profile_derivatives(math.pi / 2.0 - step, ell)[1]
        )
        assert abs(derivative - boundary_derivative_exact(ell)) < 3.0e-6


def test_electric_dtn_spectrum_and_operator_formula():
    radius = 1.7
    for ell in (1, 2, 5):
        assert math.isclose(
            electric_dtn_eigenvalue(ell, radius),
            ell * (ell + 2) / ((ell + 1) * radius),
            rel_tol=1.0e-14,
        )
    assert electric_dtn_contract()["operator_form"].startswith("N_0=Omega")


def test_transverse_only_kernel_is_reclassified_and_static_kernel_completed():
    result = full_static_gauge_kernel_correction()
    assert result["v15_66_full_current_kernel_wording"].startswith("RECLASSIFIED")
    assert result["static_current_kernel_complete_after_v15_68"] is True
    assert result["local_M4_Maxwell_term_derived"] is False


def test_payload_is_deterministic_and_fail_closed():
    payload = completion_payload()
    assert payload["validation_passed"]
    assert payload["FULL_BHSM_COMPLETE"] is False
    first = deterministic_json(payload)
    second = deterministic_json(completion_payload())
    assert first == second
    assert "NaN" not in first and "Infinity" not in first
