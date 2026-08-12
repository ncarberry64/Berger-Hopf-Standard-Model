import math

from bhsm.interface.aether_cycle_dtn_local_limit_v15_90 import (
    completion_payload,
    cycle_local_coefficients,
    continuous_spectral_dtn,
    locality_claim_boundary,
    variational_local_coefficient,
)


def test_variational_coefficients_match_direct_small_lambda_solve():
    lam = 1.0e-5
    for sector in ("transverse", "electric"):
        direct = continuous_spectral_dtn(0.10602, sector, lam) / lam
        analytic = variational_local_coefficient(0.10602, sector)
        assert abs(direct - analytic) / analytic < 5.0e-6


def test_cycle_local_coefficients_and_trace_ray_are_derived():
    result = cycle_local_coefficients()
    assert math.isclose(result["cycle_K_T_local"], 1394.790186982647, rel_tol=1e-11)
    assert math.isclose(result["cycle_K_E_Gauss_local"], 1082.968993955627, rel_tol=1e-11)
    assert math.isclose(
        result["carrier_trace_local_ray"]["Y"]
        / result["carrier_trace_local_ray"]["Sp1"],
        5.0 / 3.0,
    )


def test_static_local_result_does_not_overclaim_lorentz_completion():
    boundary = locality_claim_boundary()
    assert boundary["local_spatial_Fij_derivative_coefficient_derived"]
    assert boundary["local_Gauss_constraint_derivative_coefficient_derived"]
    assert boundary["dynamic_frequency_response_derived"] is False
    assert boundary["Lorentz_invariant_FmunuFmunu_coefficient_derived"] is False
    assert boundary["independent_intrinsic_boundary_normalization_added"] is False


def test_payload_validates():
    assert completion_payload()["validation_passed"]
