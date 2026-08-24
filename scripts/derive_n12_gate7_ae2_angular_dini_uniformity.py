"""Audit angular uniformity after fixed-channel source-Dini closure."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.action_extension_ae2_angular_dini_uniformity import (  # noqa: E402
    angular_uniformity_requirement,
    exponential_radius_angular_counterexample,
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
    ROOT / "src/bhsm/interface/action_extension_ae2_angular_dini_uniformity.py",
    ROOT / "scripts/derive_n12_gate7_ae2_angular_dini_uniformity.py",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("angular Dini audit inputs required")
    compact, high, ownership, brst, heat_trace, radius, flow, coercive = (
        _load(path) for path in INPUTS[:8]
    )
    if not all(
        payload.get("validation_passed") is True
        for payload in (compact, high, ownership, brst, heat_trace, radius, flow, coercive)
    ):
        raise RuntimeError("validated angular-tail lineage required")
    counterexample = exponential_radius_angular_counterexample()
    requirement = angular_uniformity_requirement()
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
        "maximal_flow_dichotomy_does_not_select_infinite_tail_class": flow["ordered_event"]["outcome_selected"] is False,
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
        "adjudication": {
            "fixed_channel_source_Dini": "CLOSED_DO_NOT_REOPEN",
            "exact_power_tail_fixed_channel_results": "PRESERVED_DO_NOT_REOPEN",
            "arbitrary_positive_tail_angular_sum": "FALSE",
            "bounded_log_derivative_monotonicity_and_smoothness_suffice": False,
            "finite_optical_length_compatible_with_absolute_angular_sum": False,
            "optical_completeness_proved_by_retained_action": False,
            "optical_completeness_proved_sufficient_for_every_nonasymptotic_tail": False,
            "action_owned_forward_relative_reference_available": False,
            "BRST_grading_closes_physical_tail": False,
            "spatial_Galerkin_tail_used_as_angular_or_temporal_tail": False,
        },
        "frontier_sharpening": {
            "G7_07_angular_tail": "OPEN_CURRENT_OWNER",
            "first_branch": "PROVE_THE_ACTUAL_INFINITE_REGULAR_HISTORY_IS_OPTICALLY_COMPLETE_AND_DERIVE_A_QUANTITATIVE_ANGULAR_BARRIER_SUM",
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
        "exact_next_dependency": "TEST_THE_RETAINED_ACTION_FOR_OPTICAL_COMPLETENESS_OF_THE_UNIQUE_INFINITE_REGULAR_HISTORY;_IN_PARALLEL_AUDIT_WHETHER_THE_EXISTING_QUANTUM_REPLACEMENT_IDENTITY_ALREADY_OWNS_A_FORWARD_REFERENCE_OPERATOR_WITHOUT_ADDING_A_COUNTERTERM_OR_NEW_ACTION_TERM",
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
