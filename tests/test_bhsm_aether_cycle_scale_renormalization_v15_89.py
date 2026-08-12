import math

from bhsm.interface.aether_cycle_scale_renormalization_v15_89 import (
    absolute_cycle_form_factors,
    completion_payload,
    cycle_matching_scale,
    renormalization_semantics,
    rg_transport,
)


def test_cycle_matching_scale_is_fixed_in_the_single_action_unit():
    scale = cycle_matching_scale()
    assert math.isclose(scale["cycle_log_mean_R4_in_ell_kappa"], 1.020827793518, rel_tol=1e-11)
    assert math.isclose(scale["cycle_matching_scale_in_ell_kappa_inverse"], 0.979597152771, rel_tol=1e-11)
    assert scale["external_SI_value_of_kappa1_inserted"] is False


def test_one_cycle_fixes_both_gauge_form_factors_on_the_trace_ray():
    result = absolute_cycle_form_factors()
    assert math.isclose(result["sectors"]["Sp1"]["K_transverse"], 3166.083808336222)
    assert math.isclose(result["sectors"]["Sp1"]["K_electric"], 2345.290876580072)
    assert math.isclose(
        result["sectors"]["Y"]["K_transverse"]
        / result["sectors"]["Sp1"]["K_transverse"],
        5.0 / 3.0,
    )
    assert result["independent_Lorentzian_Maxwell_coefficients_inserted"] is False


def test_rg_transport_and_scheme_do_not_reopen_split_normalizations():
    flow = rg_transport(2.0)
    semantics = renormalization_semantics()
    assert flow["new_matching_coefficient_introduced"] is False
    assert flow["SM_one_loop_flow_preserves_matching_ray"] is False
    assert semantics["finite_shift_of_only_gauge_or_only_Yukawa_allowed"] is False
    assert semantics["dimensionless_normalization_missing"] is False


def test_payload_validates():
    assert completion_payload()["validation_passed"]
