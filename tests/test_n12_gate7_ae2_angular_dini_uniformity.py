from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys

import pytest

from bhsm.interface.action_extension_ae2_angular_dini_uniformity import (
    at_most_linear_angular_series_witness,
    at_most_linear_radius_agmon_bound,
    angular_uniformity_requirement,
    dominant_round_radius_balance,
    exponential_radius_angular_counterexample,
    integrable_optical_tail_dini_coefficient_lower,
    logarithmic_radius_speed_agmon_bound,
    radius_speed_bound_from_state_controls,
    uniform_scale_shift_osgood_audit,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/derive_n12_gate7_ae2_angular_dini_uniformity.py"
TARGET = ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_AE2_ANGULAR_DINI_UNIFORMITY_AUDIT.json"


def test_integrable_optical_tail_lower_bound_grows_exponentially() -> None:
    low = integrable_optical_tail_dini_coefficient_lower(
        angular_eigenvalue=3.0,
        reciprocal_radius_integral=1.0,
        initial_reciprocal_radius_upper=1.0,
        initial_interval_length=0.25,
        positive_source_reciprocal_integral=0.2,
    )
    high = integrable_optical_tail_dini_coefficient_lower(
        angular_eigenvalue=7.0,
        reciprocal_radius_integral=1.0,
        initial_reciprocal_radius_upper=1.0,
        initial_interval_length=0.25,
        positive_source_reciprocal_integral=0.2,
    )
    assert high["log_threshold_coefficient_lower"] - low["log_threshold_coefficient_lower"] == pytest.approx(8.0)
    assert low["fixed_channel_source_Dini_finite"] is True


def test_exponential_radius_is_a_smooth_nonpower_angular_counterexample() -> None:
    row = exponential_radius_angular_counterexample(10)
    assert row["radius_history"] == "R4(tau)=exp(tau)"
    assert row["log_radius_derivative"] == 1.0
    assert row["reciprocal_radius_integral"] == 1.0
    assert row["minimum_successive_log_term_increment"] > 2.0
    assert row["absolute_angular_source_Dini_sum_finite"] is False
    assert row["fixed_channel_source_Dini_finite_for_every_level"] is True


def test_optical_completeness_is_necessary_but_not_overclaimed_sufficient() -> None:
    row = angular_uniformity_requirement()
    assert row["finite_optical_length_excluded_by_angular_finiteness"] is True
    assert row["necessary_geometric_exclusion"].endswith("=infinity")
    assert row["optical_completeness_alone_proved_sufficient"] is False


def test_at_most_linear_radius_has_mu_log_mu_barrier() -> None:
    low = at_most_linear_radius_agmon_bound(
        angular_eigenvalue=8.0,
        radius_upper_at_source_end=1.0,
        radius_speed_upper=1.0,
        threshold_wave_number=1.0,
    )
    high = at_most_linear_radius_agmon_bound(
        angular_eigenvalue=16.0,
        radius_upper_at_source_end=1.0,
        radius_speed_upper=1.0,
        threshold_wave_number=1.0,
    )
    assert high["agmon_action_lower"] > 2.0 * low["agmon_action_lower"]
    assert high["reciprocal_linear_envelope_integral_diverges"] is True
    assert high["beats_exp(C*mu)*mu^d_for_every_fixed_C_and_d"] is True
    assert high["exact_power_law_assumed"] is False
    partner = at_most_linear_radius_agmon_bound(
        angular_eigenvalue=16.0,
        radius_upper_at_source_end=1.0,
        radius_speed_upper=1.0,
        threshold_wave_number=1.0,
        chirality=-1,
    )
    assert high["potential_lower"] == "V_plus>=s_mu^2/2_FOR_mu>=2*v"
    assert partner["potential_lower"] == "V_minus>=s_mu^2/2_FOR_mu>=2*v"
    assert partner["agmon_action_lower"] == high["agmon_action_lower"]
    assert high["radius_monotonicity_assumed"] is False


def test_state_controls_give_exact_two_sided_radius_speed_bound() -> None:
    row = radius_speed_bound_from_state_controls(
        galerkin_order=3,
        coordinate_norm_upper=0.25,
        velocity_norm_upper=0.5,
        multiplier_norm_upper=0.125,
        reference_radius=2.0,
    )
    expected = math.exp(2.0 * 0.25 + math.sqrt(3.0) * 0.125) * math.sqrt(7.0) * 0.5
    assert row["proper_radius_speed_upper"] == pytest.approx(expected)
    assert row["requires_radius_monotonicity"] is False
    assert row["global_state_controls_proved_by_retained_action"] is False


def test_unbounded_logarithmic_speed_still_has_superlinear_angular_action() -> None:
    row = logarithmic_radius_speed_agmon_bound(
        angular_eigenvalue=128.0,
        radius_at_source_end=1.0,
        speed_offset=1.0,
        speed_log_coefficient=0.5,
        threshold_wave_number=1.0,
    )
    partner = logarithmic_radius_speed_agmon_bound(
        angular_eigenvalue=128.0,
        radius_at_source_end=1.0,
        speed_offset=1.0,
        speed_log_coefficient=0.5,
        threshold_wave_number=1.0,
        chirality=-1,
    )
    expected_optical = 2.0 * math.log1p(0.5 * math.log(64.0))
    assert row["Osgood_optical_integral_lower"] == pytest.approx(expected_optical)
    assert row["agmon_action_lower"] == pytest.approx(64.0 * expected_optical)
    assert partner["agmon_action_lower"] == row["agmon_action_lower"]
    assert row["allows_unbounded_radius_speed"] is True
    assert row["radius_monotonicity_assumed"] is False
    assert "mu*log(log(mu))" in row["asymptotic_action_class"]


def test_uniform_scale_shift_does_not_kinematically_supply_osgood_decay() -> None:
    row = uniform_scale_shift_osgood_audit(
        scale_shift=2.0,
        radius=1.25,
        proper_log_radius_rate=0.1,
    )
    assert row["translated_radius"] / row["base_radius"] == pytest.approx(math.exp(2.0))
    assert row["translated_absolute_proper_radius_speed"] / row["base_absolute_proper_radius_speed"] == pytest.approx(math.exp(2.0))
    assert row["translated_proper_log_radius_rate"] == row["base_proper_log_radius_rate"]
    assert row["leading_ADM_kinetic_scale_weight"] == row["leading_algebraic_scale_weight"] == 7
    assert row["scale_weights_alone_force_log_rate_decay"] is False
    assert row["positive_radius_and_lapse_domain_alone_proves_Osgood_envelope"] is False


def test_weight_seven_radius_balance_permits_exponential_expansion() -> None:
    kappa0 = 15.0 * 5.0 ** (1.0 / 3.0) / 4.0
    row = dominant_round_radius_balance(cosmological_coefficient=kappa0)
    assert row["round_volume_integral"] == pytest.approx(1.0 / 24.0)
    assert row["ADM_trace_coefficient"] == -21.0
    assert row["expanding_equilibrium_log_rate"] == pytest.approx(
        math.sqrt(kappa0 / 42.0)
    )
    assert row["zero_energy_constraint_residual_at_equilibrium"] == pytest.approx(0.0)
    assert row["scale_equation_residual_at_equilibrium"] == pytest.approx(0.0)
    assert row["dominant_balance_forces_log_rate_decay"] is False
    assert row["dominant_balance_is_compatible_with_finite_optical_length"] is True
    assert row["full_retained_history_with_this_asymptotic_proved"] is False


def test_at_most_linear_root_test_beats_compact_source_growth() -> None:
    row = at_most_linear_angular_series_witness(
        source_exponential_rate=3.0,
        polynomial_degree=6,
        first_level=24,
        last_level=48,
    )
    assert row["local_weight_class"] == "exp(C*mu)*(1+mu)^d"
    assert row["weighted_log_terms_strictly_decrease"] is True
    assert row["nth_root_logs_decrease"] is True
    assert row["angular_series_absolutely_summable"] is True


def test_bounded_radius_is_the_infinite_barrier_limit() -> None:
    row = at_most_linear_radius_agmon_bound(
        angular_eigenvalue=4.0,
        radius_upper_at_source_end=1.0,
        radius_speed_upper=0.0,
        threshold_wave_number=1.0,
    )
    assert row["agmon_action_lower"] == "INFINITY"
    assert row["squared_amplitude_suppression_upper"] == 0.0


def test_invalid_angular_inputs_fail() -> None:
    with pytest.raises(ValueError):
        integrable_optical_tail_dini_coefficient_lower(
            angular_eigenvalue=1.0,
            reciprocal_radius_integral=1.0,
            initial_reciprocal_radius_upper=1.0,
            initial_interval_length=0.25,
            positive_source_reciprocal_integral=0.2,
        )
    with pytest.raises(ValueError):
        exponential_radius_angular_counterexample(1)
    with pytest.raises(ValueError):
        at_most_linear_radius_agmon_bound(
            angular_eigenvalue=1.0,
            radius_upper_at_source_end=1.0,
            radius_speed_upper=1.0,
            threshold_wave_number=1.0,
        )


def test_artifact_is_validated_and_deterministic() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    payload = json.loads(TARGET.read_text(encoding="utf-8"))
    assert first == second
    assert payload["validation_passed"] is True
    assert payload["adjudication"]["fixed_channel_source_Dini"] == "CLOSED_DO_NOT_REOPEN"
    assert payload["adjudication"]["arbitrary_positive_tail_angular_sum"] == "FALSE"
    assert payload["conditional_at_most_linear_sufficient_class"]["status"] == "CLOSED_CONDITIONAL_THEOREM"
    assert payload["adjudication"]["eventual_two_sided_Lipschitz_radius_sufficient"] is True
    assert payload["adjudication"]["eventual_logarithmic_speed_Osgood_radius_sufficient"] is True
    assert payload["adjudication"]["radius_monotonicity_required"] is False
    assert payload["adjudication"]["eventual_two_sided_Lipschitz_radius_proved_by_action"] is False
    assert payload["adjudication"]["eventual_logarithmic_speed_Osgood_radius_proved_by_action"] is False
    assert payload["conditional_logarithmic_speed_Osgood_class"]["allows_unbounded_radius_speed"] is True
    assert payload["retained_action_uniform_scale_ownership_audit"]["status"] == "EXACT_SCALE_WEIGHTS_DERIVED_NO_OSGOOD_DECAY_THEOREM"
    dominant = payload["retained_action_dominant_round_radius_balance"]
    assert dominant["result"]["expanding_equilibrium_log_rate"] > 0.0
    assert dominant["result"]["full_retained_history_with_this_asymptotic_proved"] is False
    replay = dominant["full_action_large_scale_replay"]
    assert replay["action_limit_errors_strictly_decrease"] is True
    assert replay["normalized_energy_magnitudes_strictly_decrease"] is True
    assert replay["normalized_scale_EL_residuals_strictly_decrease"] is True
    assert replay["full_coordinate_EL_residuals_strictly_decrease"] is True
    assert replay["transverse_coordinate_EL_residuals_strictly_decrease"] is True
    assert replay["multiplier_constraint_residuals_strictly_decrease"] is True
    assert replay["rows"][-1]["absolute_action_limit_error"] < 2.0e-6
    assert abs(
        replay["rows"][-1][
            "normalized_constant_rate_scale_EL_residual_over_R7"
        ]
    ) < 1.0e-5
    assert replay["rows"][-1][
        "maximum_absolute_normalized_transverse_coordinate_EL_residual"
    ] < 5.0e-6
    assert replay["rows"][-1][
        "maximum_absolute_normalized_multiplier_constraint_residual"
    ] < 1.0e-6
    kernel = dominant["weight_seven_kernel_and_weight_five_lift"]
    assert kernel["kernel_dimension_exhibited"] == 12
    assert kernel["weight_seven_Euler_Dirac_block_invertible"] is False
    assert kernel["ordinary_leading_inverse_stability_analysis_authorized"] is False
    assert all(
        row["maximum_weight_seven_kernel_residual"] < 1.0e-13
        for row in kernel["leading_cross_quadrature"]
    )
    assert kernel["rescaled_operator_norm_relative_spread"] < 1.0e-5
    assert kernel["rescaled_minimum_singular_value_relative_spread"] < 1.0e-5
    assert payload["adjudication"]["leading_ADM_cosmological_balance_excludes_constant_positive_log_rate"] is False
    assert payload["conditional_action_state_control_reduction"]["retained_action_supplies_global_velocity_bound"] is False
    assert payload["frontier_sharpening"]["G7_07_angular_tail"] == "OPEN_CURRENT_OWNER"
    assert payload["FULL_BHSM_COMPLETE"] is False
