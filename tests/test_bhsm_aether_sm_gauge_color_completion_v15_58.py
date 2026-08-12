import math

from bhsm.interface import aether_sm_gauge_color_completion_v15_58 as gauge


def test_single_carrier_trace_extends_weak_coefficient_without_new_parameter():
    result = gauge.carrier_trace_extension_contract()
    assert result["trace_ratio"] == "10/3:2:2"
    assert result["new_continuous_coefficient"] is False
    assert result["historically_derived_from_EH_for_SU3_or_U1"] is False


def test_reset_gauge_ray_and_weak_angle_without_dimensional_misidentification():
    result = gauge.reset_gauge_normalization_ray()
    assert result["M4_inverse_coupling_ray"] == "K_Y:K_2:K_3=5/3:1:1"
    assert math.isclose(result["sin_squared_theta_W_on_this_ray"], 3 / 8)
    assert result["K_F_five_dimensional"] > 0.0
    assert result["five_dimensional_K_F_identified_directly_with_M4_inverse_g_squared"] is False
    assert result["absolute_M4_couplings_derived"] is False
    assert result["external_measured_coupling_used"] is False


def test_closed_s3_gauss_law_selects_mesons_and_baryons():
    result = gauge.color_gauss_singlet_contract()
    assert result["meson_decomposition"].startswith("3_tensor_bar3=1")
    assert result["baryon_decomposition"].startswith("3_tensor_3_tensor_3=1")
    assert result["kinematic_confinement_on_the_closed_child"]
    assert result["global_color_open_asymptotic_state_allowed"] is False
    assert result["dynamical_area_law_or_Yang-Mills_mass_gap_derived"] is False


def test_payload_json_is_deterministic_and_valid():
    payload = gauge.completion_payload()
    assert payload["validation_passed"]
    assert payload["claim_boundary"]["M4_gauge_coupling_ray_derived_by_carrier_trace"]
    assert payload["claim_boundary"]["absolute_M4_gauge_couplings_derived"] is False
    assert gauge.deterministic_json(payload) == gauge.deterministic_json(
        gauge.completion_payload()
    )
