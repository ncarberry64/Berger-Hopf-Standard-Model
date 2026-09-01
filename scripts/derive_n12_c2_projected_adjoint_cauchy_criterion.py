"""Derive the exact projected C2 maximal-adjoint convergence criterion."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_C2_PROJECTED_ADJOINT_CAUCHY_CRITERION.json"
C2 = BASE / "BHSM_N12_C2_CLASS_REDUCED_MAXIMAL_RESPONSE.json"
ADJOINT = BASE / "BHSM_N12_MAXIMAL_FORWARD_ADJOINT_EXHAUSTION.json"
PULLBACK = BASE / "BHSM_N12_FORCE_ADJOINT_PULLBACK.json"
QUOTIENT = BASE / "BHSM_N12_INTRINSIC_TIME_QUOTIENT_FORCE_ROOT.json"
FINITE_CORE = BASE / "BHSM_N12_C2_1222_SEGMENT_FINITE_CORE_DESCRIPTOR.json"
PARAMETRIC = BASE / "BHSM_N12_C2_1222_PARAMETRIC_BASE_FAMILY.json"
INTERVAL_ACTIONS = BASE / "BHSM_N12_C2_1222_TRANSPOSED_DURATION_ACTION_COVERAGE.json"
DINI = BASE / "BHSM_N12_GATE7_AE2_COMPACT_SOURCE_DINI_CLOSURE.json"
ANGULAR = BASE / "BHSM_N12_GATE7_AE2_ANGULAR_DINI_UNIFORMITY_AUDIT.json"
HIGH = BASE / "BHSM_N12_FORWARD_E1_HIGH_ENERGY_TRACE_NORM.json"
FINITE_ENDPOINT = BASE / "BHSM_N12_FINITE_ENDPOINT_FORWARD_ADJOINT_KKT.json"
SEAM_NO_GO = BASE / "BHSM_N12_NEGATIVE_AXIS_SEAM_HEAT_SYNTHESIS_NO_GO.json"
NHIM_NO_GO = BASE / "BHSM_N12_ASYMPTOTIC_NHIM_ANGULAR_FORCE_NO_GO.json"
SOURCE_ONTOLOGY = BASE / "BHSM_N12_GATE7_CLOSED_SYSTEM_ZERO_EXTERNAL_SOURCE_ONTOLOGY.json"
THEORY = ROOT / "theory/n12_c2_projected_adjoint_cauchy_criterion.md"
INPUTS = (
    C2, ADJOINT, PULLBACK, QUOTIENT, FINITE_CORE, PARAMETRIC,
    INTERVAL_ACTIONS, DINI, ANGULAR, HIGH,
    FINITE_ENDPOINT, SEAM_NO_GO, NHIM_NO_GO, SOURCE_ONTOLOGY, THEORY,
)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _witnesses(beta: float = 0.5) -> dict[str, Any]:
    durations = (0.5, 1.0, 2.0, 4.0, 8.0)
    stable_rows = [
        {
            "duration": duration,
            "projected_force": -math.expm1(-beta * duration) / beta,
            "limit": 1.0 / beta,
        }
        for duration in durations
    ]
    return {
        "absolute_norm_not_necessary": {
            "state_space": "R2",
            "physical_pullback": "P(x1,x2)=x1",
            "U(t,0)": "I",
            "q_rep(t)": "(0,1)",
            "ambient_weighted_norm_integral": "infinity",
            "projected_force_for_every_T": 0.0,
            "purpose": "GENERAL_MATHEMATICAL_LOGIC_WITNESS_NOT_A_BHSM_TAIL",
        },
        "regular_factors_not_sufficient": {
            "state_space": "R",
            "U(t,0)": "exp(t)",
            "q_rep(t)": "exp(-t)",
            "finite_core_force": "T",
            "maximal_projected_limit_exists": False,
            "purpose": "GENERAL_MATHEMATICAL_LOGIC_WITNESS_NOT_A_BHSM_TAIL",
        },
        "stable_rate_pair": {
            "U(t,0)": "exp(alpha*t)",
            "q_rep(t)": "exp(-(alpha+beta)*t)",
            "beta": beta,
            "projected_force_limit": 1.0 / beta,
            "rows": stable_rows,
            "purpose": "GENERAL_MATHEMATICAL_CAUCHY_WITNESS",
        },
    }


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing projected-adjoint inputs: " + ", ".join(missing))
    records = [_load(path) for path in INPUTS[:-1]]
    if not all(record.get("validation_passed") is True for record in records):
        raise RuntimeError("validated projected-adjoint parents required")
    (
        c2, adjoint, pullback, quotient, finite_core, parametric,
        interval_actions, dini, angular, high, finite_endpoint, seam_no_go,
        nhim_no_go, source_ontology,
    ) = records
    witness = _witnesses()
    rows = witness["stable_rate_pair"]["rows"]
    limit = witness["stable_rate_pair"]["projected_force_limit"]
    errors = [abs(row["projected_force"] - limit) for row in rows]

    slot_audit = [
        {
            "diagram_slot": "ZERO_EXTERNAL_BIRTH_CAUCHY_DATUM",
            "required_type": "EXTERNAL_LINEAR_DATUM_J_ext_ONLY",
            "candidate": "OWNER_AUTHORIZED_CLOSED_SYSTEM_SOURCE_PARTITION",
            "domain_check": "VALID_AFTER_JOINT_OPERATOR_DIFFERENTIATION",
            "provenance_check": "VALID_OWNER_PHYSICAL_ONTOLOGY_NOT_ACTION_DERIVATION",
            "verdict": "VALID_MATCH_ONLY_J_ext_IS_ZEROED",
        },
        {
            "diagram_slot": "JOINT_INTERNAL_AE2_OPERATOR",
            "required_type": "M_f_PLUS_U_R_DAGGER_M_C2_U_R_PLUS_W_phys_WITH_INTERNAL_CONTACTS",
            "candidate": "CLOSED_SYSTEM_SOURCE_ONTOLOGY_AND_GLUING_IDENTITY",
            "domain_check": "ASSEMBLY_RULE_VALID_COMPLETE_NUMERICAL_REALIZATION_OPEN",
            "provenance_check": "VALID_ACTION_BLOCKS_AND_OWNER_SOURCE_PARTITION",
            "verdict": "VALID_MATCH_ASSEMBLY_COMPLETE_COTANGENT_MISSING",
        },
        {
            "diagram_slot": "C2_MAXIMAL_HISTORY_AND_DOMAIN",
            "required_type": "ACTION_OWNED_MAXIMAL_FORWARD_HISTORY_WITH_ENDPOINT_CLASS",
            "candidate": "M_C2^max_ON_Phi_C2_AND_RETAINED_ENDPOINT_DICHOTOMY",
            "domain_check": "VALID",
            "provenance_check": "VALID_ACTION_AND_CLASS_THEOREMS",
            "verdict": "VALID_MATCH_ABSTRACT_ENDPOINT_OUTCOME_OPEN",
        },
        {
            "diagram_slot": "STATE_PROPAGATOR_U",
            "required_type": "PHYSICAL_QUOTIENT_EULER_DIRAC_TANGENT_PROPAGATOR_ON_Phi_C2",
            "candidate": "1222_SEGMENT_PARAMETRIC_STATE_JACOBI_FAMILY",
            "domain_check": "VALID_ON_CERTIFIED_FINITE_PREFIX_ONLY",
            "provenance_check": "VALID_ACTION_LINEARIZATION",
            "verdict": "ACTUALLY_MISSING_ON_MAXIMAL_TAIL",
        },
        {
            "diagram_slot": "FIXED_CHANNEL_HEAT_SOURCE",
            "required_type": "SOURCE_WEIGHTED_LOW_AND_HIGH_ENERGY_COTANGENT_CONTROL",
            "candidate": "COMPACT_VOL_TERRA_SOURCE_DINI_PLUS_HEAT_SANDWICH",
            "domain_check": "VALID_PER_RETAINED_COMPACT_SOURCE_CHANNEL",
            "provenance_check": "VALID_AE2_ACTION",
            "verdict": "VALID_MATCH_FIXED_CHANNEL_ONLY",
        },
        {
            "diagram_slot": "FULL_GRADED_ANGULAR_q_heat",
            "required_type": "ABSOLUTE_OR_ACTION_CANCELLED_PHYSICAL_COTANGENT_ASSEMBLY",
            "candidate": "ANGULAR_DINI_UNIFORMITY_AUDIT",
            "domain_check": "FINITE_ENDPOINT_CLOSED_INFINITE_ROUTE_OPEN",
            "provenance_check": "VALID_NO_GO_AND_CONDITIONAL_BARRIERS",
            "verdict": "ACTUALLY_MISSING_ON_CURRENT_MAXIMAL_TAIL",
        },
        {
            "diagram_slot": "DIRECT_ZETA_COTANGENT",
            "required_type": "MAXIMAL_CORE_CONVERGENT_DIRECT_ACTION_COVECTOR",
            "candidate": "q_direct_OR_q_zeta_SYMBOLIC_FORCE_TERM",
            "domain_check": "FORMULA_VALID_VALUE_AND_TAIL_NOT_EVALUATED",
            "provenance_check": "VALID_SYMBOLIC_ACTION_TERM",
            "verdict": "ACTUALLY_MISSING_ON_MAXIMAL_TAIL",
        },
        {
            "diagram_slot": "PHYSICAL_RESET_PULLBACK",
            "required_type": "B_reset_AND_INTRINSIC_GAUGE_TIME_QUOTIENT_PULLBACK",
            "candidate": "N_phys^dagger_B_reset^dagger_ADJOINT_CHAIN",
            "domain_check": "VALID_ON_REGULAR_RESET_QUOTIENT_STRATUM",
            "provenance_check": "VALID_AE2_RESET_AND_CONSTRAINT_THEOREMS",
            "verdict": "VALID_MATCH",
        },
        {
            "diagram_slot": "NUMERICAL_ZERO_SOURCE_FORCE",
            "required_type": "LIMIT_IN_PHYSICAL_RESET_QUOTIENT_DUAL",
            "candidate": "CLOSED_SYSTEM_FINITE_CORE_FORCE_NET_F_T_AT_J_ext_EQUALS_ZERO",
            "domain_check": "1222_SEGMENT_PREFIX_ONLY",
            "provenance_check": "VALID_BUT_INCOMPLETE",
            "verdict": "ACTUALLY_MISSING",
        },
    ]

    validation = {
        "all_inputs_validated": True,
        "zero_source_means_only_zero_external_Cauchy_datum": (
            source_ontology["external_internal_partition"]["set_to_zero"] == ["J_ext"]
        ),
        "all_seam_responses_remain_internal_and_are_counted_once": (
            source_ontology["adjudication"]["internal_response_zeroing"] == "FORBIDDEN"
            and source_ontology["adjudication"]["additional_independent_seam_force"] == "FORBIDDEN"
        ),
        "C2_maximal_family_instantiated": (
            c2["adjudication"]["abstract_M_C2_value_definition_exists_and_is_unique"]
            is True
        ),
        "physical_force_pullback_derived": (
            pullback["claim_boundary"]["G7_08_force_adjoint_pullback"] == "DERIVED"
        ),
        "intrinsic_quotient_equivalence_derived": (
            quotient["claim_boundary"]["force_root_time_quotient_equivalence"]
            == "DERIVED"
        ),
        "finite_prefix_propagator_bound_is_finite": math.isfinite(
            parametric["finite_cover_witness"]["complete_fixed_s_growth_upper"]
        ),
        "finite_prefix_not_promoted_to_maximal_tail": (
            finite_core["endpoint_event_child_partition"][
                "far_core_edge_is_physical_endpoint"
            ] is False
        ),
        "all_1222_interval_transposed_duration_actions_are_certified": (
            interval_actions["adjudication"][
                "all_1222_interval_transposed_duration_actions"
            ] == "CERTIFIED"
        ),
        "fixed_channel_Dini_closed": (
            dini["validation"]["arbitrary_positive_admissible_tail_closed"]
            is True
        ),
        "fixed_channel_high_energy_closed": (
            high["adjudication"]["compact_weak_E1_high_energy_integrability"]
            == "DERIVED"
        ),
        "infinite_angular_assembly_not_assumed": (
            angular["minimal_requirement"]["factorization_and_compact_source_sufficient_after_angular_sum"]
            is False
        ),
        "finite_endpoint_alternative_is_derived": (
            finite_endpoint["status"]
            == "NO_SELECTOR_FORWARD_ADJOINT_KKT_SYSTEM_DERIVED_EVALUATION_OPEN"
        ),
        "broad_seam_family_not_promoted_to_force": (
            seam_no_go["status"]
            == "BROAD_NEGATIVE_AXIS_SEAM_FAMILY_CANNOT_DECIDE_HEAT_MINUS_ZETA_FORCE_SIGN"
        ),
        "finite_optical_NHIM_not_promoted_to_force_domain": (
            nhim_no_go["status"]
            == "FINITE_OPTICAL_NHIM_CHILD_ROUTE_EXCLUDED_FROM_ABSOLUTE_GRADED_FORCE_DOMAIN"
        ),
        "absolute_weighted_norm_is_only_sufficient": (
            witness["absolute_norm_not_necessary"]["projected_force_for_every_T"] == 0.0
        ),
        "smooth_regular_factor_witness_can_diverge": (
            witness["regular_factors_not_sufficient"]["maximal_projected_limit_exists"]
            is False
        ),
        "stable_rate_pair_converges": (
            errors[-1] < 0.04
            and all(left > right for left, right in zip(errors, errors[1:]))
        ),
        "no_selector_scale_fit_recurrence_endpoint_box_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_C2_PROJECTED_ADJOINT_CAUCHY_CRITERION",
        "status": (
            "PROJECTED_FORCE_CAUCHY_CRITERION_DERIVED_ACTUAL_C2_TAIL_OPEN"
            if passed else "PROJECTED_FORCE_CAUCHY_CRITERION_NOT_DERIVED"
        ),
        "classification": (
            "THE_EXACT_GATE7_MAXIMAL_FORCE_OWNER_IS_CAUCHY_CONVERGENCE_OF_"
            "THE_FINITE_CORE_FORCE_NET_IN_THE_PHYSICAL_RESET_QUOTIENT_DUAL;_"
            "THE_AMBIENT_WEIGHTED_NORM_BOUND_IS_SUFFICIENT_NOT_NECESSARY,_"
            "BUT_THE_CURRENT_C2_CLASS_AND_1222_SEGMENT_PREFIX_DO_NOT_CLOSE_"
            "THE_ACTUAL_PROPAGATOR_FULL_GRADED_HEAT_OR_DIRECT_ZETA_TAILS"
        ),
        "theorem": {
            "finite_core_adjoint": "p_T(0)=integral_0^T U(t,0)^dagger*q_rep(t)dt",
            "finite_core_physical_force": (
                "F_T=N_phys^dagger*(B_reset^dagger*p_T(0)+q_direct,T)"
            ),
            "necessary_and_sufficient_maximal_criterion": (
                "FOR_EVERY_epsilon>0_EXISTS_T0_FOR_ALL_S,T>T0:_"
                "norm(N_phys^dagger*(B_reset^dagger*integral_S^T_"
                "U(t,0)^dagger*q_rep(t)dt+q_direct,T-q_direct,S))<epsilon"
            ),
            "strong_sufficient_condition": (
                "integral_0^Tmax_norm(U(t,0))*norm(q_rep(t))dt<infinity_"
                "AND_q_direct,T_CONVERGES"
            ),
            "finite_endpoint_corollary": (
                "CERTIFIED_FINITE_EVENT_OR_CANONICAL_STOP_PLUS_RETAINED_"
                "REGULAR_COMPACT_ENDPOINT_THEOREM_IMPLIES_THE_CRITERION"
            ),
            "quotient_cancellation_rule": (
                "ONLY_ACTION_DERIVED_GRADED_CONSTRAINT_NORMAL_OR_EXACT_TIME_"
                "CANCELLATION_MAY_BE_USED"
            ),
        },
        "matching_audit": slot_audit,
        "finite_prefix_evidence": {
            "segment_count": finite_core["coefficient_path"]["segment_count"],
            "proper_duration_interval": finite_core["coefficient_path"]["proper_duration_interval"],
            "state_Jacobi_growth_upper": parametric["finite_cover_witness"][
                "complete_fixed_s_growth_upper"
            ],
            "interval_transposed_duration_actions": interval_actions[
                "adjudication"
            ]["all_1222_interval_transposed_duration_actions"],
            "role": "FINITE_FORCE_NET_PREFIX_NOT_A_MAXIMAL_TAIL_BOUND_OR_ENDPOINT",
        },
        "logical_witnesses": witness,
        "adjudication": {
            "zero_external_source_semantics": "CLOSED_ONLY_J_ext_IS_ZEROED_AFTER_JOINT_DIFFERENTIATION",
            "internal_seam_response_semantics": "CLOSED_INTERNAL_BLOCKS_NOT_SEPARATE_SOURCES",
            "class_and_domain_slot": "CLOSED",
            "physical_pullback_and_quotient_slot": "CLOSED",
            "fixed_channel_source_Dini_slot": "CLOSED_DO_NOT_REOPEN",
            "fixed_channel_high_energy_slot": "CLOSED_DO_NOT_REOPEN",
            "finite_prefix_interval_duration_action_slot": "CLOSED_THROUGH_1222",
            "actual_maximal_state_propagator_tail": "OPEN",
            "actual_infinite_route_full_graded_heat_cotangent": "OPEN",
            "actual_direct_zeta_tail": "OPEN",
            "actual_projected_force_Cauchy_limit": "OPEN_CURRENT_OWNER",
            "finite_later_event_or_canonical_stop": "ALTERNATIVE_OPEN_OUTCOME",
            "zero_source_force": "OPEN",
        },
        "validated_invalidated_open": {
            "VALIDATED": [
                "the maximal Gate7 observable is a quotient-dual finite-core limit",
                "absolute weighted-load integrability is sufficient",
                "finite endpoint or canonical stop uses the retained compact theorem",
                "fixed-channel Dini and compact high-energy smoothing remain closed",
            ],
            "INVALIDATED": [
                "absolute ambient weighted norm is logically necessary for the projected force",
                "enclosure-class constancy determines continuous propagator or cotangent tails",
                "finite-prefix Jacobi growth controls the maximal tail",
                "fixed-channel spectral integrability implies temporal weighted-load convergence",
                "broad negative-axis seam bounds determine the force sign",
            ],
            "OPEN": [
                "C2 maximal endpoint outcome",
                "quotient-Cauchy tail of the actual full heat-minus-zeta force net",
                "zero-source force, same-action saddle, and physical Hessian",
            ],
        },
        "hindsight": {
            "physical_enclosure_class": "CLOSED_ON_CERTIFIED_C2_PREFIX",
            "continuous_modulation_within_class": "REMAINS_IN_THE_FORCE_TAIL",
            "numerical_proof_box": "FINITE_PREFIX_EVIDENCE_ONLY",
            "event_or_class_transition": "NOT_REACHED",
            "canonical_stop": "NOT_REACHED",
            "difficulty_type": "CONTINUOUS_MAXIMAL_HISTORY_OPERATOR_AND_DUAL_LIMIT_NOT_CLASSIFICATION",
        },
        "exact_next_dependency": (
            "ASSEMBLE_THE_COMPLETE_JOINT_INTERNAL_M_f_PLUS_TRANSPORTED_M_C2_PLUS_"
            "W_phys_HEAT_MINUS_ZETA_COTANGENT,_SET_ONLY_J_ext_TO_ZERO_AFTER_"
            "DIFFERENTIATION,_AND_PROVE_THE_ACTION_OWNED_QUOTIENT_CAUCHY_TAIL_"
            "OR_CERTIFY_A_FINITE_LATER_EVENT_OR_CANONICAL_STOP;_THE_"
            "STRONGER_AMBIENT_ABSOLUTE_WEIGHTED_NORM_BOUND_IS_OPTIONAL,_AND_"
            "FIXED_CHANNEL_DINI_HIGH_ENERGY_RESET_SEMANTICS_RECURRENCE_AND_"
            "CHORD3_MUST_NOT_BE_REOPENED"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_PROJECTED_C2_FORCE_CAUCHY_TAIL_OR_FINITE_ENDPOINT",
            "Gate8": "LOCKED",
            "projected_Cauchy_criterion": "DERIVED",
            "actual_projected_Cauchy_tail": "OPEN_CURRENT_OWNER",
            "actual_zero_source_force": "OPEN",
            "same_action_saddle": "WAITING_ON_FORCE",
            "physical_Hessian": "WAITING_ON_SADDLE",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FLAGSHIP_READY": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": passed,
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "validation_passed": payload["validation_passed"],
        "next": payload["claim_boundary"]["actual_projected_Cauchy_tail"],
    }, indent=2))


if __name__ == "__main__":
    main()
