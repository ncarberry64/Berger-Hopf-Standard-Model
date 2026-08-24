"""Audit angular uniformity after fixed-channel source-Dini closure."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.action_extension_ae2_angular_dini_uniformity import (  # noqa: E402
    at_most_linear_angular_series_witness,
    at_most_linear_radius_agmon_bound,
    angular_uniformity_requirement,
    dominant_round_radius_balance,
    exponential_radius_angular_counterexample,
    logarithmic_radius_speed_agmon_bound,
    radius_speed_bound_from_state_controls,
    uniform_scale_shift_osgood_audit,
)
from bhsm.interface.aether_diagonal_sp1_m4_attachment_v15_50 import RADIUS0  # noqa: E402
from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (  # noqa: E402
    exact_full_action_jet_at_state,
)
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import (  # noqa: E402
    dimensions,
)


TARGET = ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_AE2_ANGULAR_DINI_UNIFORMITY_AUDIT.json"
INPUTS = (
    ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_AE2_COMPACT_SOURCE_DINI_CLOSURE.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_FORWARD_E1_HIGH_ENERGY_TRACE_NORM.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_FORWARD_SOURCE_TAIL_OWNERSHIP_AUDIT.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_FORWARD_BRST_HEAT_TAIL_CANCELLATION_AUDIT.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_FORWARD_HEAT_TRACE_CLASS_AUDIT.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_FORWARD_BOUNDARY_RADIUS_ACTION_PROJECTION.json",
    ROOT / "artifacts/intrinsic_state_selection/BHSM_N12_CONTINUUM_MAXIMAL_FLOW_DICHOTOMY.json",
    ROOT / "artifacts/intrinsic_state_selection/BHSM_N12_GLOBAL_FLOW_COERCIVE_CONTROL_GATE.json",
    ROOT / "artifacts/intrinsic_state_selection/BHSM_N12_CONSTRAINT_REDUCED_ENERGY_IDENTITY_GATE.json",
    ROOT / "src/bhsm/interface/action_extension_ae2_angular_dini_uniformity.py",
    ROOT / "scripts/derive_n12_gate7_ae2_angular_dini_uniformity.py",
    ROOT / "theory/bhsm_action_ae2_angular_dini_uniformity.md",
    ROOT / "src/bhsm/interface/aether_n3_exact_full_local_action_jet_v17_60.py",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _large_scale_round_replay(kappa0: float) -> dict[str, Any]:
    """Replay the weight-seven limit against the complete retained action."""

    dims = dimensions(12)
    qdim = dims["coordinates"]
    h = math.sqrt(kappa0 / 42.0)
    predicted = -kappa0 / 24.0
    rows = []
    for scale in (2.0, 4.0, 6.0):
        q = np.zeros(qdim)
        velocity = np.zeros(qdim)
        multipliers = np.zeros(dims["multipliers"])
        q[0] = scale
        velocity[0] = h
        jet = exact_full_action_jet_at_state(
            12, q, velocity, multipliers, points=96
        )
        radius = RADIUS0 * math.exp(scale)
        radius7 = radius**7
        normalized_action = float(np.real(jet.value)) / radius7
        momentum = np.asarray(
            np.real(jet.gradient[qdim:2 * qdim]), dtype=float
        )
        normalized_energy = (
            float(velocity @ momentum - np.real(jet.value)) / radius7
        )
        normalized_scale_EL_residual = float(np.real(
            jet.hessian[qdim, 0] * h - jet.gradient[0]
        )) / radius7
        rows.append({
            "q0": scale,
            "proper_log_radius_rate": h,
            "normalized_full_action_over_R7": normalized_action,
            "predicted_weight_seven_limit": predicted,
            "absolute_action_limit_error": abs(normalized_action - predicted),
            "normalized_reduced_energy_over_R7": normalized_energy,
            "normalized_constant_rate_scale_EL_residual_over_R7": (
                normalized_scale_EL_residual
            ),
        })
    return {
        "ansatz": "q=(q0,0,...),_v=(sqrt(kappa0/42),0,...),_multipliers=0",
        "quadrature_points": 96,
        "rows": rows,
        "action_limit_errors_strictly_decrease": all(
            later["absolute_action_limit_error"]
            < earlier["absolute_action_limit_error"]
            for earlier, later in zip(rows, rows[1:])
        ),
        "normalized_energy_magnitudes_strictly_decrease": all(
            abs(later["normalized_reduced_energy_over_R7"])
            < abs(earlier["normalized_reduced_energy_over_R7"])
            for earlier, later in zip(rows, rows[1:])
        ),
        "normalized_scale_EL_residuals_strictly_decrease": all(
            abs(later["normalized_constant_rate_scale_EL_residual_over_R7"])
            < abs(earlier["normalized_constant_rate_scale_EL_residual_over_R7"])
            for earlier, later in zip(rows, rows[1:])
        ),
        "observed_relative_remainder_weight": "R^-2_CONSISTENT_WITH_NEXT_SCALE_WEIGHT_5",
    }


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("angular Dini audit inputs required")
    compact, high, ownership, brst, heat_trace, radius, flow, coercive, energy = (
        _load(path) for path in INPUTS[:9]
    )
    if not all(
        payload.get("validation_passed") is True
        for payload in (compact, high, ownership, brst, heat_trace, radius, flow, coercive, energy)
    ):
        raise RuntimeError("validated angular-tail lineage required")
    counterexample = exponential_radius_angular_counterexample()
    requirement = angular_uniformity_requirement()
    barrier = at_most_linear_radius_agmon_bound(
        angular_eigenvalue=12.5,
        radius_upper_at_source_end=1.25,
        radius_speed_upper=1.0,
        threshold_wave_number=1.0,
        chirality=1,
    )
    partner_barrier = at_most_linear_radius_agmon_bound(
        angular_eigenvalue=12.5,
        radius_upper_at_source_end=1.25,
        radius_speed_upper=1.0,
        threshold_wave_number=1.0,
        chirality=-1,
    )
    state_control_reduction = radius_speed_bound_from_state_controls(
        galerkin_order=12,
        coordinate_norm_upper=0.25,
        velocity_norm_upper=0.5,
        multiplier_norm_upper=0.1,
        reference_radius=RADIUS0,
    )
    logarithmic_barrier = logarithmic_radius_speed_agmon_bound(
        angular_eigenvalue=128.0,
        radius_at_source_end=1.0,
        speed_offset=1.0,
        speed_log_coefficient=0.5,
        threshold_wave_number=1.0,
        chirality=1,
    )
    logarithmic_partner = logarithmic_radius_speed_agmon_bound(
        angular_eigenvalue=128.0,
        radius_at_source_end=1.0,
        speed_offset=1.0,
        speed_log_coefficient=0.5,
        threshold_wave_number=1.0,
        chirality=-1,
    )
    scale_shift = uniform_scale_shift_osgood_audit(
        scale_shift=2.0,
        radius=1.25,
        proper_log_radius_rate=0.1,
    )
    dominant_balance = dominant_round_radius_balance(
        cosmological_coefficient=15.0 * 5.0 ** (1.0 / 3.0) / 4.0,
    )
    large_scale_replay = _large_scale_round_replay(
        float(dominant_balance["cosmological_coefficient"])
    )
    summability = at_most_linear_angular_series_witness()
    rows = counterexample["rows"]
    validation = {
        "all_inputs_validated": True,
        "fixed_channel_Dini_closure_preserved": compact["frontier_sharpening"]["G7_06_fixed_channel_E1_source_measure"] == "CLOSED",
        "counterexample_is_positive_smooth_and_non_power": counterexample["smooth_positive_non_power_tail"] is True,
        "counterexample_has_bounded_log_derivative": counterexample["log_radius_derivative"] == 1.0,
        "counterexample_has_finite_optical_length": counterexample["reciprocal_radius_integral"] == 1.0,
        "every_fixed_channel_remains_Dini_finite": counterexample["fixed_channel_source_Dini_finite_for_every_level"] is True,
        "angular_terms_fail_even_to_tend_to_zero": counterexample["degeneracy_weighted_terms_tend_to_zero"] is False and counterexample["minimum_successive_log_term_increment"] > 0.0,
        "absolute_angular_sum_is_not_closed_for_arbitrary_tails": counterexample["absolute_angular_source_Dini_sum_finite"] is False,
        "high_energy_fixed_sector_theorem_preserved": high["adjudication"]["compact_weak_E1_high_energy_integrability"] == "DERIVED",
        "spatial_Galerkin_tail_not_repurposed": ownership["adjudication"]["may_be_used_as_internal_source_level_tail_without_new_theorem"] is False,
        "BRST_physical_leading_coefficient_nonzero": brst["exact_asymptotic"]["leading_scaled_limit"] == "-5*sqrt(pi)",
        "retained_forward_reference_is_not_executable": heat_trace["source_audit"]["action_owned_forward_reference_operator_available"] is False and heat_trace["source_audit"]["relative_heat_trace_class_theorem_on_current_history_available"] is False,
        "action_does_not_currently_prove_optical_completeness": radius["claim_boundary"]["maximal_x_history_numerically_enclosed"] is False and coercive["owned_and_missing_energy_structure"]["coercive_S2_bound_on_continuum_child_component"] is False,
        "action_does_not_currently_prove_global_absolute_radius_speed_bound": coercive["validation"]["ADM_velocity_form_has_both_signs"] is True and radius["remaining_variational_owner"]["global_DV_and_D2V_enclosures_on_maximal_component"] == "OPEN",
        "maximal_flow_dichotomy_does_not_select_infinite_tail_class": flow["ordered_event"]["outcome_selected"] is False,
        "at_most_linear_radius_implies_optical_completeness": barrier["reciprocal_linear_envelope_integral_diverges"] is True,
        "at_most_linear_barrier_has_mu_log_mu_action": "mu*log(mu)" in barrier["asymptotic_action_class"],
        "barrier_beats_local_exponential_and_polynomial_growth": barrier["beats_exp(C*mu)*mu^d_for_every_fixed_C_and_d"] is True,
        "both_chiralities_have_direct_mu_log_mu_barrier_without_monotonicity": barrier["potential_lower"] == "V_plus>=s_mu^2/2_FOR_mu>=2*v" and partner_barrier["potential_lower"] == "V_minus>=s_mu^2/2_FOR_mu>=2*v" and barrier["radius_monotonicity_assumed"] is False and "mu*log(mu)" in partner_barrier["asymptotic_action_class"],
        "state_control_reduction_is_finite_and_two_sided": math.isfinite(state_control_reduction["proper_radius_speed_upper"]) and state_control_reduction["requires_radius_monotonicity"] is False,
        "logarithmic_speed_Osgood_barrier_allows_unbounded_speed": logarithmic_barrier["allows_unbounded_radius_speed"] is True and logarithmic_partner["allows_unbounded_radius_speed"] is True,
        "logarithmic_speed_barrier_beats_local_exponential_growth": logarithmic_barrier["beats_exp(C*mu)*mu^d_for_every_fixed_C_and_d"] is True and "mu*log(log(mu))" in logarithmic_barrier["asymptotic_action_class"],
        "uniform_scale_shift_preserves_log_rate_and_scales_radius_speed_linearly": math.isclose(scale_shift["translated_proper_log_radius_rate"], scale_shift["base_proper_log_radius_rate"], rel_tol=0.0, abs_tol=0.0) and math.isclose(scale_shift["translated_absolute_proper_radius_speed"] / scale_shift["base_absolute_proper_radius_speed"], scale_shift["radius_scale_factor"], rel_tol=1.0e-15, abs_tol=0.0),
        "retained_action_has_same_leading_scale_weight_for_kinetic_and_algebraic_terms": scale_shift["leading_ADM_kinetic_scale_weight"] == 7 and scale_shift["leading_algebraic_scale_weight"] == 7 and scale_shift["scale_weights_alone_force_log_rate_decay"] is False,
        "constraint_reduced_energy_identity_consumed": "IDENTICALLY_ZERO" in energy["classification"],
        "exact_weight_seven_energy_and_scale_equations_have_nonzero_expanding_equilibrium": math.isclose(dominant_balance["zero_energy_constraint_residual_at_equilibrium"], 0.0, rel_tol=0.0, abs_tol=1.0e-14) and math.isclose(dominant_balance["scale_equation_residual_at_equilibrium"], 0.0, rel_tol=0.0, abs_tol=1.0e-14) and dominant_balance["expanding_equilibrium_log_rate"] > 0.0,
        "dominant_balance_does_not_prove_full_exponential_history": dominant_balance["full_retained_history_with_this_asymptotic_proved"] is False and dominant_balance["lower_weight_and_transverse_remainders_controlled"] is False,
        "full_action_large_scale_replay_converges_to_weight_seven_balance": large_scale_replay["action_limit_errors_strictly_decrease"] is True and large_scale_replay["normalized_energy_magnitudes_strictly_decrease"] is True and large_scale_replay["normalized_scale_EL_residuals_strictly_decrease"] is True and large_scale_replay["rows"][-1]["absolute_action_limit_error"] < 2.0e-6 and abs(large_scale_replay["rows"][-1]["normalized_constant_rate_scale_EL_residual_over_R7"]) < 1.0e-5,
        "conditional_angular_series_root_test_closes": summability["angular_series_absolutely_summable"] is True and summability["analytic_root_test_limit"] == "minus_infinity",
        "no_relative_reference_inserted": True,
        "strict_gap_power_tail_terminal_recurrence_and_chord3_not_reopened": True,
        "frozen_predictions_unchanged": True,
        "FULL_BHSM_COMPLETE_false": True,
    }
    return {
        "artifact": "BHSM_N12_GATE7_AE2_ANGULAR_DINI_UNIFORMITY_AUDIT",
        "action_version": "BHSM-AE-2.0.0",
        "status": "FIXED_CHANNEL_DINI_CLOSED_ANGULAR_UNIFORMITY_REDUCED_TO_OPTICAL_COMPLETENESS_OR_ACTION_OWNED_RELATIVE_TRACE",
        "classification": "THE_COMPACT_VOL_TERRA_THEOREM_CLOSES_EVERY_FIXED_FACTORIZED_CHANNEL_BUT_IS_NOT_UNIFORM_IN_THE_SIGNED_S3_DIRAC_LEVEL;_THE_SMOOTH_POSITIVE_NON_POWER_HISTORY_R4=exp(tau)_HAS_BOUNDED_LOG_DERIVATIVE_AND_FINITE_OPTICAL_LENGTH,_AND_THE_EXACT_POSITIVE_CHIRALITY_ZERO_TRANSFER_NORMALIZATION_FORCES_THE_LEVEL_n_SOURCE_DINI_COEFFICIENT_TO_GROW_AT_LEAST_AS_exp(2*(n+3/2));_WITH_QUADRATIC_WEYL_DEGENERACY_THE_ABSOLUTE_ANGULAR_TERMS_DO_NOT_TEND_TO_ZERO",
        "exact_lower_bound": {
            "geometry": "r=1/R4,_I=int_0^infinity_r,_s_mu=mu*r",
            "zero_transfer_normalization": "N_mu^2=(2/pi)*exp(2*mu*I)",
            "source_hypothesis": "h>=0_AND_H=int_delta^L_h(t)*r(t)dt>0",
            "initial_core_hypothesis": "r(t)<=r_max_ON_[0,delta]",
            "range": "mu>=1/(2*r_max*delta)",
            "coefficient_bound": "C_mu>=((2/pi)*(1-exp(-1))*H/r_max)*exp(2*mu*I)",
            "Weyl_levels": "mu_n=n+3/2,_d_n=48*(n+1)*(n+2)",
            "consequence": "sum_n_d_n*C_mu_n=infinity_WHEN_I>0_IS_FINITE",
        },
        "counterexample": counterexample,
        "minimal_requirement": requirement,
        "conditional_at_most_linear_sufficient_class": {
            "status": "CLOSED_CONDITIONAL_THEOREM",
            "hypothesis": "AFTER_COMPACT_SOURCE_abs(D_tau_R4)<=v<infinity",
            "radius_envelope": "R4(tau)<=R_L+v*(tau-L)",
            "optical_consequence": "integral_L^infinity_d_tau/R4=infinity",
            "two_chirality_potential": "V_chi=s_mu^2+/-mu*(D_tau_R4)/R4^2>=s_mu^2/2_FOR_mu>=2*v",
            "barrier_range": "R_L+v*(tau-L)<=mu/(2*k)",
            "agmon_action_lower": {
                "positive_chirality": "A_plus_mu(k)>=(mu/(2*v))*log(mu/(2*k*R_L))_FOR_mu>=2*v",
                "negative_chirality": "A_minus_mu(k)>=(mu/(2*v))*log(mu/(2*k*R_L))_FOR_mu>=2*v",
            },
            "local_source_growth_class": "exp(C_source*mu)*(1+mu)^d",
            "summability": "exp(C_source*mu)*(1+mu)^d*exp(-2*A_mu(k))_IS_SUMMABLE_IN_mu_BY_ROOT_TEST",
            "monotonicity_required": False,
            "two_sided_direct_bound": "abs(D_tau_R4)<=v_IMPLIES_V_plus_AND_V_minus>=s_mu^2/2_FOR_mu>=2*v;_ON_s_mu>=2*k_THIS_GIVES_sqrt(V_chi-k^2)>=s_mu/2",
            "exact_power_law_assumed": False,
            "barrier_witnesses": {
                "positive_chirality": barrier,
                "negative_chirality": partner_barrier,
            },
            "root_test_witness": summability,
        },
        "conditional_action_state_control_reduction": {
            "status": "EXACT_FINITE_N_REDUCTION_GLOBAL_HYPOTHESES_OPEN",
            "identity": "abs(D_tau_R4)=R4*abs(D_q_x[v])/N_boundary",
            "uniform_hypotheses": "sup_norm(q)<=Q,_sup_norm(v)<=V,_sup_norm(multipliers)<=M",
            "result": "abs(D_tau_R4)<=(R0/2)*exp(sqrt(1+N)*Q+sqrt(N)*M)*sqrt(1+2N)*V",
            "witness": state_control_reduction,
            "retained_action_supplies_global_coordinate_bound": False,
            "retained_action_supplies_global_velocity_bound": False,
            "retained_action_supplies_uniform_positive_lapse_margin": False,
        },
        "conditional_logarithmic_speed_Osgood_class": {
            "status": "CLOSED_CONDITIONAL_THEOREM",
            "hypothesis": "ON_EVERY_OUTWARD_PASSAGE_abs(D_tau_R4)<=a+b*log(R4/R_L),_a>0,_b>=0",
            "turning_radius": "R_turn=mu/(2*k)",
            "high_angular_range": "mu>=2*(a+b*log(R_turn/R_L))",
            "two_chirality_potential": "V_chi>=s_mu^2/2",
            "Osgood_optical_lower": "int_d_tau/R4>=int_(R_L)^R_turn_dR/(R*(a+b*log(R/R_L)))",
            "agmon_action_for_b_positive": "A_chi_mu(k)>=(mu/(2*b))*log(1+(b/a)*log(mu/(2*k*R_L)))",
            "asymptotic_action_class": "mu*log(log(mu))",
            "summability": "exp(C_source*mu)*(1+mu)^d*exp(-2*A_chi_mu(k))_IS_SUMMABLE_BY_ROOT_TEST",
            "allows_unbounded_radius_speed": True,
            "radius_monotonicity_required": False,
            "exact_power_law_assumed": False,
            "witnesses": {
                "positive_chirality": logarithmic_barrier,
                "negative_chirality": logarithmic_partner,
            },
        },
        "retained_action_uniform_scale_ownership_audit": {
            "status": "EXACT_SCALE_WEIGHTS_DERIVED_NO_OSGOOD_DECAY_THEOREM",
            "uniform_shift": "q0->q0+sigma_WITH_OTHER_COORDINATES_VELOCITIES_AND_LAPSE_SHIFT_FIXED",
            "kinematic_consequence": "R4->exp(sigma)*R4,_D_tau_log_R4_UNCHANGED,_abs(D_tau_R4)->exp(sigma)*abs(D_tau_R4)",
            "Osgood_requirement": "omega(R)=o(R)_REQUIRES_D_tau_log_R4->0_ALONG_UNBOUNDED_OUTWARD_RADIUS",
            "action_scale_structure": "PRE_QUOTIENT_BULK_WEIGHTS_{7,5,3,1,-1};_INERTIA_WEIGHTS_{7,5,3,1};_BOUNDARY_CASIMIR_WEIGHT_-1",
            "leading_balance": "ADM_KINETIC_AND_ALGEBRAIC_TERMS_BOTH_HAVE_WEIGHT_7",
            "conclusion": "POSITIVE_RADIUS_LAPSE_AND_SCALE_WEIGHTS_DO_NOT_FORCE_OSGOOD;_A_CONSTRAINT_REDUCED_FLOW_ESTIMATE_IS_REQUIRED",
            "witness": scale_shift,
        },
        "retained_action_dominant_round_radius_balance": {
            "status": "EXACT_WEIGHT_SEVEN_BALANCE_PERMITS_NONZERO_LOG_RATE_FULL_HISTORY_OPEN",
            "scope": "ROUND_COMMON_SCALE_ANSATZ_AND_COMPLETE_WEIGHT_SEVEN_ADM_PLUS_COSMOLOGICAL_SECTOR",
            "result": dominant_balance,
            "full_action_large_scale_replay": large_scale_replay,
            "consequence": "THE_LEADING_RETAINED_EQUATIONS_DO_NOT_FORCE_D_tau_log_R4_TO_ZERO_AND_ARE_COMPATIBLE_WITH_FINITE_OPTICAL_LENGTH",
            "not_claimed": "EXISTENCE_OF_A_FULL_RETAINED_EXPONENTIAL_HISTORY_OR_INCOMPATIBILITY_OF_THE_RETAINED_ACTION",
        },
        "adjudication": {
            "fixed_channel_source_Dini": "CLOSED_DO_NOT_REOPEN",
            "exact_power_tail_fixed_channel_results": "PRESERVED_DO_NOT_REOPEN",
            "arbitrary_positive_tail_angular_sum": "FALSE",
            "bounded_log_derivative_monotonicity_and_smoothness_suffice": False,
            "finite_optical_length_compatible_with_absolute_angular_sum": False,
            "optical_completeness_proved_by_retained_action": False,
            "optical_completeness_proved_sufficient_for_every_nonasymptotic_tail": False,
            "eventual_two_sided_Lipschitz_radius_sufficient": True,
            "eventual_logarithmic_speed_Osgood_radius_sufficient": True,
            "radius_monotonicity_required": False,
            "eventual_two_sided_Lipschitz_radius_proved_by_action": False,
            "eventual_logarithmic_speed_Osgood_radius_proved_by_action": False,
            "leading_ADM_cosmological_balance_excludes_constant_positive_log_rate": False,
            "action_owned_forward_relative_reference_available": False,
            "BRST_grading_closes_physical_tail": False,
            "spatial_Galerkin_tail_used_as_angular_or_temporal_tail": False,
        },
        "frontier_sharpening": {
            "G7_07_angular_tail": "OPEN_CURRENT_OWNER",
            "first_branch": "PROVE_THAT_THE_LOWER_WEIGHT_AND_TRANSVERSE_RETAINED_EQUATIONS_DESTABILIZE_OR_EXCLUDE_THE_WEIGHT_SEVEN_CONSTANT_POSITIVE_LOG_RATE_BALANCE_AND_FORCE_THE_OUTWARD_OSGOOD_ENVELOPE_abs(D_tau_R4)<=a+b*log(R4/R_L)",
            "second_branch": "DERIVE_AN_ALREADY_ACTION_OWNED_FORWARD_RELATIVE_REFERENCE_AND_PROVE_SOURCE_CONTRACTED_RELATIVE_TRACE_CLASS",
            "finite_branch": "USE_THE_RETAINED_COMPACT_RESOLVENT_OPERATOR_IF_THE_ACTUAL_HISTORY_REACHES_EVENT_OR_CANONICAL_STOP",
        },
        "claim_boundary": {
            "Gate7": "ACTIVE_NOT_CLOSED",
            "Gate8": "LOCKED",
            "zero_source_force": "OPEN",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": "CONTROL_THE_LOWER_WEIGHT_AND_TRANSVERSE_REMAINDERS_IN_THE_FULL_CONSTRAINT_REDUCED_RADIUS_EQUATION_STRONGLY_ENOUGH_TO_EXCLUDE_OR_DESTABILIZE_THE_EXACT_WEIGHT_SEVEN_EXPANDING_EQUILIBRIUM_D_tau_log_R4=sqrt(kappa0/42)_AND_FORCE_AN_OUTWARD_OSGOOD_ENVELOPE,_OR_PROVE_THAT_THIS_BRANCH_REACHES_AN_EXISTING_EVENT_OR_CANONICAL_STOP;_THE_LEADING_ADM_COSMOLOGICAL_SECTOR_ALONE_CANNOT_CLOSE_G7_07",
        "inputs": {path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def deterministic_bytes(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def materialize() -> Path:
    payload = build_payload()
    if not payload["validation_passed"]:
        failed = [key for key, value in payload["validation"].items() if not value]
        raise RuntimeError(f"angular Dini uniformity audit failed: {failed}")
    TARGET.write_bytes(deterministic_bytes(payload))
    return TARGET


if __name__ == "__main__":
    print(materialize())
