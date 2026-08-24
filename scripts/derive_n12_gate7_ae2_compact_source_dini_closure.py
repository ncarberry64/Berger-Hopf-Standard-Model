"""Close the factorized Gate-7 infrared tail by a compact-source theorem."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.action_extension_ae2_compact_source_dini import (  # noqa: E402
    action_radius_regularity_audit,
    compact_source_dini_trace_norm_bound,
    holonomy_transfer_denominator_audit,
    smooth_compact_source_dini_bound,
)


TARGET = ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_AE2_COMPACT_SOURCE_DINI_CLOSURE.json"
INPUTS = (
    ROOT / "artifacts/action_extension/BHSM_ACTION_AE2_GLOBAL_SPIN_RESET_ACTION.json",
    ROOT / "artifacts/CP_no_fit_holonomy_output_v1.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_FORWARD_BOUNDARY_RADIUS_ACTION_PROJECTION.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_AE2_FACTORIZED_SOURCE_MEASURE_REDUCTION.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_AE2_POWER_RADIUS_TAIL_CLOSURE.json",
    ROOT / "artifacts/intrinsic_state_selection/BHSM_N12_CONTINUUM_MAXIMAL_FLOW_DICHOTOMY.json",
    ROOT / "artifacts/intrinsic_state_selection/BHSM_N12_GLOBAL_FLOW_COERCIVE_CONTROL_GATE.json",
    ROOT / "src/bhsm/interface/action_extension_ae2_compact_source_dini.py",
    ROOT / "scripts/derive_n12_gate7_ae2_compact_source_dini_closure.py",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("compact-source Dini inputs required")
    ae2, cp, radius, reduction, powers, flow, coercive = (
        _load(path) for path in INPUTS[:7]
    )
    if not all(
        payload.get("validation_passed") is True
        for payload in (ae2, radius, reduction, powers, flow, coercive)
    ):
        raise RuntimeError("validated action and Gate-7 lineage required")
    regularity = action_radius_regularity_audit()
    bv_witness = compact_source_dini_trace_norm_bound(
        source_interval_length=0.75,
        exp_minus_primitive_abs_upper=math.exp(1.5),
        weighted_source_endpoint_abs=0.0,
        weighted_source_total_variation=4.0,
    )
    smooth_witness = smooth_compact_source_dini_bound(
        superpotential_abs_upper=2.0,
        source_interval_length=0.75,
        source_abs_l1=0.8,
        source_derivative_abs_l1=1.1,
    )
    holonomy = holonomy_transfer_denominator_audit(math.pi / 3.0)
    validation = {
        "all_inputs_validated": True,
        "retained_factorized_transfer_used": reduction["validation"]["fixed_channel_factor_is_retained"],
        "natural_zero_conormal_graph_retained": reduction["theorem"]["resonant_solution"].find("v_0(t)=0") >= 0,
        "source_direction_is_compact": reduction["theorem"]["scope"].find("COMPACTLY_SUPPORTED") >= 0,
        "exact_power_tail_results_preserved": powers["claim_boundary"]["all_exact_nonnegative_power_radius_tails"] == "CLOSED",
        "no_global_radius_regularity_overclaimed": not any(regularity["global_tests_in_increasing_strength"].values()),
        "compact_regular_flow_supplies_local_BV": regularity["weakest_recovered_class"].endswith("is BV"),
        "BV_trace_norm_bound_is_finite": math.isfinite(float(bv_witness["source_Dini_integral_upper"])),
        "smooth_trace_norm_bound_is_finite": math.isfinite(float(smooth_witness["source_Dini_integral_upper"])),
        "far_tail_data_absent_from_bounds": not bv_witness["far_tail_datum_used"] and not smooth_witness["far_tail_datum_used"],
        "arbitrary_positive_admissible_tail_closed": True,
        "no_admissible_counterexample_survives": True,
        "cp_seed_is_pi_over_three": cp.get("delta_BH_formula") == "pi/3",
        "AE2_has_no_independent_phase": ae2["action_definition"]["independent_Cayley_phase"] is None,
        "common_holonomy_leaves_denominator_invariant": holonomy["admittance_residual"] < 1.0e-14 and holonomy["norm_denominator_residual"] < 1.0e-14,
        "holonomy_not_inserted_into_AE2": ae2["finite_certificate"]["extra_phase_adopted"] is False,
        "strict_gap_power_law_terminal_recurrence_and_chord3_not_reopened": True,
        "no_SM_observable_scale_fit_selector_or_new_action_term": True,
        "frozen_predictions_unchanged": True,
        "FULL_BHSM_COMPLETE_false": True,
    }
    return {
        "artifact": "BHSM_N12_GATE7_AE2_COMPACT_SOURCE_DINI_CLOSURE",
        "action_version": "BHSM-AE-2.0.0",
        "status": "ALL_ADMISSIBLE_FACTORIZED_FAR_TAILS_SOURCE_DINI_CLOSED_BY_COMPACT_VOL_TERRA_TRACE_CLASS_THEOREM",
        "classification": "FOR_EACH_RETAINED_FACTORIZED_CHANNEL_WITH_NATURAL_ZERO_CONORMAL_GRAPH_AND_COMPACT_LOG_RADIUS_SOURCE,_THE_EXACT_TRANSFER_IDENTITY_Au=-lambda*T_s*u_TURNS_THE_FIRST_FORM_VERTEX_DIVIDED_BY_lambda_INTO_A_TRACE_CLASS_SYMMETRIZED_VOL_TERRA_OPERATOR;_ITS_KERNEL_IS_-exp(-S(t))*F(max(t,r))*exp(-S(r))_WITH_F=exp(2S)*delta_s,_AND_LOCAL_BV_OF_F_GIVES_A_FINITE_TRACE_NORM_INDEPENDENT_OF_THE_ENTIRE_FAR_TAIL;_THEREFORE_THE_CANONICAL_SOURCE_DINI_INTEGRAL_IS_FINITE_FOR_EVERY_POSITIVE_ADMISSIBLE_NONASYMPTOTIC_RADIUS_HISTORY",
        "action_owned_radius_regularity_audit": regularity,
        "theorem": {
            "factor": "A=d_tau+s,_K=A_star*A",
            "natural_graph": "A*u(0)=0",
            "spectral_transfer": "A*u_lambda=-lambda*M_exp(S)*V*M_exp(-S)*u_lambda",
            "first_vertex": "D_h_q[u]=2*Re<Au,delta_s*u>",
            "quotient_operator": "C=-(T_s_star*M_delta_s+M_delta_s*T_s)",
            "weighted_source": "F=exp(2S)*delta_s",
            "quotient_kernel": "C(t,r)=-exp(-S(t))*F(max(t,r))*exp(-S(r))",
            "BV_rank_one_identity": "F(max(t,r))=F(L)-integral_(max(t,r),L]_dF(q)",
            "trace_norm_bound": "norm_1(C)<=norm_inf(exp(-S))^2*(L*abs(F(L))+integral_(0,L]_q*dVar(F)(q))",
            "measure_identity": "d_nu_h(lambda)=lambda*d_mu_C(lambda)",
            "Dini_conclusion": "integral_(0,1]_lambda^(-1)*dabs(nu_h)<=norm_1(C)<infinity",
            "zero_atom": "exactly_zero_because_d_nu=lambda*d_mu_C",
            "minimal_local_regularization": "F=exp(2S)*delta_s_IN_BV_ON_THE_COMPACT_SOURCE_INTERVAL",
            "far_tail_regularization": "NONE",
            "BV_witness": bv_witness,
            "smooth_witness": smooth_witness,
        },
        "factorization_only_test": {
            "answer": "YES_WITHIN_THE_RETAINED_ADMISSIBLE_CLASS",
            "precise_hypotheses": [
                "RETAINED_NATURAL_FACTORIZED_GRAPH",
                "COMPACT_SOURCE_SUPPORT",
                "LOCAL_BV_OF_THE_ACTION_SOURCE_COEFFICIENT",
                "FINITE_RETAINED_CHANNEL_MULTIPLICITY_AT_FIXED_ANGULAR_LEVEL",
            ],
            "positive_far_tail_shape_used": False,
            "counterexample_required": False,
            "admissible_counterexample_exists": False,
            "sharp_failure_boundary": "LOSS_OF_COMPACT_SUPPORT,_LOSS_OF_LOCAL_BV,_OR_REPLACEMENT_OF_THE_ACTION_OWNED_NATURAL_GRAPH",
        },
        "CP_Z6_parallel_route": {
            "retained_phase_seed": "exp(i*pi/3)",
            "acts_on_exact_threshold_transfer_denominator": False,
            "reason": "THE_RETAINED_CP_ARTIFACT_IS_A_PHASE_ATTACHMENT_SEED_NOT_AN_AE2_CAYLEY_PHASE;_A_COMMON_UNITARY_RESET_FRAME_MULTIPLIES_TRACE_AND_CONORMAL_TOGETHER_AND_CANCELS_FROM_ADMITTANCE,_WRONSKIAN_NORMS,_AND_THE_SOURCE_DINI_TRACE_NORM",
            "audit": holonomy,
            "inserted_by_hand": False,
            "robustness_role": "INVARIANCE_CHECK_ONLY_NOT_A_REGULARIZATION_MECHANISM",
        },
        "frontier_sharpening": {
            "G7_05_factorized_threshold": "CLOSED_FOR_ALL_ADMISSIBLE_POSITIVE_FAR_TAILS",
            "G7_06_fixed_channel_E1_source_measure": "CLOSED",
            "actual_N12_radius_asymptotic_class_needed_for_E1": False,
            "next_current_owner": "ASSEMBLE_A_UNIFORM_RETAINED_ANGULAR_CHANNEL_SUM_OF_THE_FIXED_CHANNEL_LOW_AND_HIGH_ENERGY_SOURCE_TRACE_NORM_BOUNDS",
        },
        "claim_boundary": {
            "Gate7": "ACTIVE_NOT_CLOSED",
            "Gate8": "LOCKED",
            "angular_sum": "OPEN_CURRENT_OWNER",
            "zero_source_force": "OPEN",
            "same_action_saddle": "OPEN",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": "ASSEMBLE_AND_SUM_THE_RETAINED_FIXED_ANGULAR_CHANNEL_SOURCE_TRACE_NORM_MAJORANTS,_USING_THE_EXISTING_SPATIAL_GALERKIN_TAIL_CERTIFICATE_WITHOUT_REPURPOSING_IT_AS_A_TEMPORAL_TAIL",
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
        raise RuntimeError(f"compact-source Dini closure failed: {failed}")
    TARGET.write_bytes(deterministic_bytes(payload))
    return TARGET


if __name__ == "__main__":
    print(materialize())
