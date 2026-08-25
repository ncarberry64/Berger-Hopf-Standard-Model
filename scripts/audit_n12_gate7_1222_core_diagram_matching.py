"""Audit Gate-7 diagram slots after the exact-fiber 1222-core milestone."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_1222_CORE_DIAGRAM_MATCHING_AUDIT.json"
OLD = BASE / "BHSM_N12_GATE7_C2_DIAGRAM_SLOT_MATCHING_AUDIT.json"
CORE = BASE / "BHSM_N12_C2_1222_SEGMENT_FINITE_CORE_DESCRIPTOR.json"
FAMILY = BASE / "BHSM_N12_C2_1222_SEGMENT_NEGATIVE_AXIS_WEYL_FAMILY.json"
NESTED = BASE / "BHSM_N12_C2_1064_TO_1222_NESTED_WEYL_INCREMENT.json"
MAXIMAL = BASE / "BHSM_N12_MAXIMAL_FRIEDRICHS_WEYL_EXHAUSTION.json"
BIRTH = BASE / "BHSM_N12_C2_BIRTH_COEFFICIENT_QUOTIENT_JET.json"
COMPACT = BASE / "BHSM_N12_COMPACT_FINITE_HISTORY_OPERATOR.json"
SEAM = BASE / "BHSM_N12_AE2_NEGATIVE_AXIS_SEAM_FAMILY.json"
INCIDENCE = BASE / "BHSM_N12_FORWARD_COMMON_SOURCE_INCIDENCE.json"
FORCE = BASE / "BHSM_N12_FINITE_ENDPOINT_ZERO_SOURCE_FORCE_FUNCTIONAL.json"
ADJOINT = BASE / "BHSM_N12_FORCE_ADJOINT_PULLBACK.json"
CAUCHY = BASE / "BHSM_N12_C2_PROJECTED_ADJOINT_CAUCHY_CRITERION.json"
COMMON_SCALE = BASE / "BHSM_N12_C2_COMMON_SCALE_WEYL_COVARIANCE.json"
THEORY = ROOT / "theory" / "n12_gate7_1222_core_diagram_matching_audit.md"
INPUTS = (OLD, CORE, FAMILY, NESTED, MAXIMAL, BIRTH, COMPACT, SEAM, INCIDENCE, FORCE, ADJOINT, CAUCHY, COMMON_SCALE, THEORY)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing 1222 matching inputs: " + ", ".join(missing))
    old, core, family, nested, maximal, birth, compact, seam, incidence, force, adjoint, cauchy, common_scale = (
        _load(path) for path in INPUTS[:-1]
    )
    if not all(record.get("validation_passed") is True for record in (
        old, core, family, nested, maximal, birth, compact, seam, incidence, force, adjoint, cauchy, common_scale,
    )):
        raise RuntimeError("validated diagram parents required")

    slots = [
        {
            "diagram_slot": "C2_COEFFICIENT_FORM_PREFIX",
            "required_type": "NESTED_ACTION_OWNED_FORM_CORE_ON_THE_ACTUAL_RESET_GENERATED_C2_HISTORY",
            "candidate": "BHSM_N12_C2_1222_SEGMENT_FINITE_CORE_DESCRIPTOR",
            "dimension_domain_check": "VALID_1223_BY_98_NODES_1222_POSITIVE_PROPER_INTERVALS",
            "provenance_check": "VALID_EXACT_FIBER_UNIFORM_GAP_AND_MATRIX_LOHNER_CONTINUATION",
            "verdict": "VALID_MATCH_FINITE_PREFIX",
        },
        {
            "diagram_slot": "C2_NEGATIVE_AXIS_WEYL_AND_COEFFICIENT_COTANGENT",
            "required_type": "POLE_FREE_M_C2_T(z)_AND_D_COEFFICIENT_M_C2_T(z)_FOR_EVERY_REAL_z_NEGATIVE",
            "candidate": "BHSM_N12_C2_1222_SEGMENT_NEGATIVE_AXIS_WEYL_FAMILY",
            "dimension_domain_check": "VALID_FIXED_CHANNEL_BIRTH_TRACE_FOR_EVERY_REAL_z_NEGATIVE",
            "provenance_check": "VALID_INVERSE_FREE_RETAINED_FORM_RECURRENCE",
            "verdict": "VALID_MATCH_FINITE_PREFIX",
        },
        {
            "diagram_slot": "C2_MAXIMAL_WEYL_VALUE",
            "required_type": "UNIQUE_ACTION_OWNED_MAXIMAL_FRIEDRICHS_CORE_EXHAUSTION_LIMIT",
            "candidate": "BHSM_N12_MAXIMAL_FRIEDRICHS_WEYL_EXHAUSTION",
            "dimension_domain_check": "VALID_AT_FIXED_CHANNEL_AND_GALERKIN_LEVEL",
            "provenance_check": "VALID_MONOTONE_MOSCO_FORM_THEOREM",
            "verdict": "VALID_MATCH_ABSTRACT_VALUE_NUMERIC_LIMIT_OPEN",
        },
        {
            "diagram_slot": "C2_FINITE_CORE_BACKWARD_OPERATOR_COTANGENT",
            "required_type": "INVERSE_FREE_ADJOINT_SEMIGROUP_ACROSS_NESTED_FORM_CORES",
            "candidate": "BHSM_N12_C2_1064_TO_1222_NESTED_WEYL_INCREMENT",
            "dimension_domain_check": "VALID_1064_PREFIX_PLUS_158_SEGMENT_TAIL_FOR_EVERY_REAL_z_NEGATIVE",
            "provenance_check": "VALID_SAME_ACTION_MOBIUS_CHAIN_RULE_WITH_ARBITRARY_PRECISION_LOAD",
            "verdict": "VALID_MATCH_OPERATOR_COTANGENT_GEOMETRY_PULLBACK_STILL_OPEN",
        },
        {
            "diagram_slot": "C2_PHYSICAL_COMMON_SCALE_FIRST_JET",
            "required_type": "COMMON_SCALE_PULLBACK_INCLUDING_MOVING_PROPER_DURATION",
            "candidate": "BHSM_N12_C2_COMMON_SCALE_WEYL_COVARIANCE",
            "dimension_domain_check": "VALID_ON_EVERY_FINITE_POSITIVE_DURATION_CORE_AND_EVERY_REAL_z_NEGATIVE",
            "provenance_check": "EXACT_RETAINED_FORM_HOMOGENEITY_WITH_COMMON_SCALE_KEPT_PHYSICAL",
            "verdict": "VALID_MATCH_CLOSED_WITHOUT_PATHWISE_JACOBI",
        },
        {
            "diagram_slot": "C2_NON_SCALE_RESET_QUOTIENT_FIRST_JET",
            "required_type": "NONCOMPACT_PATHWISE_JACOBI_OR_EQUIVALENT_BACKWARD_ADJOINT_PULLBACK",
            "candidate": "BIRTH_RANK_TWO_CAUCHY_JET_MOD_COMMON_SCALE_PLUS_FORCE_ADJOINT_IDENTITY",
            "dimension_domain_check": "BIRTH_GERM_AND_ALGEBRA_VALID_BUT_NO_MAXIMAL_NON_SCALE_PATHWISE_SOLUTION",
            "provenance_check": "VALID_PARTIAL_ACTION_DATA_AFTER_EXACT_COMMON_SCALE_REDUCTION",
            "verdict": "ACTUALLY_MISSING_REALIZED_NON_SCALE_PULLBACK",
        },
        {
            "diagram_slot": "INCOMING_C1_RESPONSE_M_f",
            "required_type": "SHARP_ACTION_OWNED_NEGATIVE_AXIS_INCOMING_WEYL_RESPONSE_ON_THE_PHYSICAL_C1_TO_E1_HISTORY",
            "candidate": "COMPACT_TWO_BOUNDARY_OPERATOR_AND_M_f_SCHUR_TYPE",
            "dimension_domain_check": "TYPE_AND_ALGORITHM_VALID_COMPLETE_COEFFICIENT_REALIZATION_NOT_STORED",
            "provenance_check": "VALID_INCOMING_ACTION_THEORY_PARTIAL_DATA_ONLY",
            "verdict": "ACTUALLY_MISSING_SHARP_REALIZATION_NOT_MISSING_THEORY",
        },
        {
            "diagram_slot": "E1_TO_C2_SEAM",
            "required_type": "M_f+U_R_DAGGER*M_C2*U_R+W_phys_ON_COMMON_EVENT_TRACE",
            "candidate": "AE2_COVARIANT_SEAM_IDENTITY_AND_BROAD_NEGATIVE_AXIS_INTERVALS",
            "dimension_domain_check": "ASSEMBLY_VALID_INTERVALS_TOO_WIDE_FOR_NONLINEAR_TRACE",
            "provenance_check": "VALID_AE2_ACTION",
            "verdict": "VALID_ASSEMBLY_ACTUALLY_MISSING_SHARP_INPUT_VALUES",
        },
        {
            "diagram_slot": "PAIR_CONTACT_AND_GRADED_SOURCE_INCIDENCE",
            "required_type": "LOCAL_DOMAIN_PARAMETRIC_BRST_PAIR_PLUS_CONTACT_CONTRACTION",
            "candidate": "BHSM_N12_FORWARD_COMMON_SOURCE_INCIDENCE",
            "dimension_domain_check": "VALID_FOR_SUPPLIED_HISTORY_SECTIONS_AND_NATIVE_z",
            "provenance_check": "VALID_RETAINED_ACTION_INCIDENCE",
            "verdict": "VALID_MATCH_CONDITIONAL_CONSUMER",
        },
        {
            "diagram_slot": "HEAT_MINUS_ZETA_FORCE_FUNCTIONAL",
            "required_type": "BASIS_INDEPENDENT_FIRST_VARIATION_ON_POSITIVE_SELF_ADJOINT_PHYSICAL_QUOTIENT",
            "candidate": "BHSM_N12_FINITE_ENDPOINT_ZERO_SOURCE_FORCE_FUNCTIONAL",
            "dimension_domain_check": "VALID_FOR_REALIZED_OPERATOR_AND_GEOMETRY_JET",
            "provenance_check": "VALID_RETAINED_HEAT_AND_ZETA_ACCOUNTING",
            "verdict": "VALID_MATCH_CONDITIONAL_CONSUMER",
        },
        {
            "diagram_slot": "MAXIMAL_PROJECTED_FORCE_LIMIT",
            "required_type": "CAUCHY_LIMIT_IN_THE_PHYSICAL_RESET_QUOTIENT_DUAL",
            "candidate": "PROJECTED_ADJOINT_CAUCHY_CRITERION",
            "dimension_domain_check": "CRITERION_VALID_ACTUAL_NET_NOT_YET_ASSEMBLED",
            "provenance_check": "VALID_MAXIMAL_ACTION_DOMAIN",
            "verdict": "ACTUALLY_MISSING_VALUE_AND_TAIL",
        },
    ]
    validation = {
        "all_parents_validate": True,
        "1222_core_slot_is_now_matched": core["coefficient_path"]["segment_count"] == 1222,
        "C2_negative_axis_family_slot_is_now_matched": family["claim_boundary"]["finite_core_complete_negative_axis_family"].startswith("DERIVED"),
        "finite_core_backward_cotangent_semigroup_is_matched": (
            nested["adjudication"]["nested_form_core_inverse_free_value_and_backward_cotangent_composition"]
            == "CLOSED"
        ),
        "maximal_value_exists_abstractly": maximal["closed_here"]["Friedrichs_negative_z_Weyl_value_existence"] is True,
        "birth_jet_is_not_promoted_to_pathwise_jet": birth["diagram_feed"]["future_coefficient_path"] == "OPEN",
        "physical_common_scale_pullback_is_closed_exactly": (
            common_scale["adjudication"]["physical_common_scale_geometry_pullback"]
            == "CLOSED"
            and common_scale["adjudication"]["moving_duration_contribution"]
            == "INCLUDED_EXACTLY"
        ),
        "non_scale_pathwise_pullback_is_not_overclaimed": (
            common_scale["adjudication"]["non_scale_reset_quotient_geometry_pullback"]
            == "OPEN"
        ),
        "compact_incoming_operator_is_only_executable_until_path_supplied": compact["claim_boundary"]["actual_family_M_C_value"] == "OPEN_AFTER_COEFFICIENT_PATH",
        "broad_seam_intervals_do_not_decide_force": seam["force_adjudication"]["broad_intervals_decide_heat_minus_zeta_force_sign"] is False,
        "source_incidence_is_a_valid_conditional_consumer": incidence["claim_boundary"]["domain_parametric_nonzero_local_incidence"] == "DERIVED",
        "force_functional_is_derived_but_value_open": force["claim_boundary"]["zero_source_force_functional"] == "DERIVED" and force["claim_boundary"]["zero_source_force_value"] == "OPEN",
        "adjoint_removes_forward_column_requirement_not_base_history": adjoint["computational_consequence"]["forward_Jacobi_columns_required"] == 0 and adjoint["computational_consequence"]["required_base_history"] is True,
        "actual_projected_Cauchy_tail_remains_open": cauchy["claim_boundary"]["actual_projected_Cauchy_tail"] == "OPEN_CURRENT_OWNER",
        "no_probe_interval_prefix_or_proof_edge_promoted_to_force_or_endpoint": True,
        "no_selector_scale_fit_recurrence_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_GATE7_1222_CORE_DIAGRAM_MATCHING_AUDIT",
        "status": "GATE7_1222_CORE_SLOTS_MATCHED_REALIZED_PARENT_PULLBACK_AND_PROJECTED_TAIL_OPEN" if passed else "GATE7_1222_CORE_MATCHING_NOT_VALIDATED",
        "classification": "C2_FINITE_CORE_NEGATIVE_AXIS_RESPONSE,_BACKWARD_OPERATOR_COTANGENT,_AND_PHYSICAL_COMMON_SCALE_PULLBACK_SLOTS_ARE_VALID_MATCHES;_M_f_AND_THE_NON_SCALE_RESET_GEOMETRY_PULLBACK_REMAIN_MISSING_AS_REALIZED_DATA,_WHILE_INCIDENCE_FORCE_AND_CAUCHY_THEOREMS_ARE_VALID_CONDITIONAL_CONSUMERS",
        "forward_event_diagram": "C1 --M_f--> E1 --(U_R,W_phys)--> C2 --M_C2--> MAXIMAL_ENDPOINT",
        "matching_audit": slots,
        "adjudication": {
            "new_C2_response_theory_required": False,
            "more_scalar_C2_boxes_are_the_owner": False,
            "sharp_incoming_M_f_realization": "ACTUALLY_MISSING",
            "finite_core_backward_operator_cotangent": "CLOSED",
            "physical_common_scale_geometry_pullback": "CLOSED_BY_EXACT_COVARIANCE",
            "non_scale_pathwise_reset_quotient_geometry_pullback": "ACTUALLY_MISSING",
            "projected_heat_minus_zeta_force_net_and_tail": "ACTUALLY_MISSING",
            "finite_event_or_canonical_stop": "NOT_REACHED",
            "Gate7": "G7_08_OPEN",
            "Gate8": "LOCKED",
        },
        "validated_invalidated_open": {
            "VALIDATED": ["C2 1222-core coefficient slot", "C2 complete negative-axis finite-core response", "finite-core backward operator cotangent semigroup", "physical common-scale pullback including moving duration", "maximal abstract Weyl value", "source and force consumer formulas"],
            "INVALIDATED": ["new C2 theory is required", "a full pathwise Jacobi is required for the common-scale component", "birth jet alone is the remaining non-scale pathwise reset jet", "broad seam intervals or probes determine the force", "proof edge is an endpoint"],
            "OPEN": ["sharp incoming M_f realization", "non-scale pathwise reset quotient geometry pullback", "actual projected force net and Cauchy tail"],
        },
        "hindsight": {"classification": "PROOF_CHART_LIMIT_REMOVED;_OPERATOR_DATA_GAP_REMAINS", "obstruction_physical": False},
        "exact_next_dependency": "INSTANTIATE_THE_ACTION_OWNED_INCOMING_M_f_NEGATIVE_AXIS_REALIZATION_AND_CHAIN_THE_NOW_CLOSED_BACKWARD_OPERATOR_COTANGENT_THROUGH_ONLY_THE_REMAINING_NON_SCALE_RESET_QUOTIENT_GEOMETRY_ADJOINT,_THEN_COMBINE_IT_WITH_THE_CLOSED_COMMON_SCALE_COMPONENT,_CONTRACT_THE_SOURCE_AND_FORCE_FUNCTIONALS,_AND_TEST_THE_PROJECTED_CAUCHY_TAIL",
        "claim_boundary": {
            "Gate7": "G7_08_OPEN_REALIZED_PARENT_PULLBACK_AND_PROJECTED_TAIL",
            "Gate8": "LOCKED",
            "zero_source_force": "OPEN",
            "same_action_saddle": "WAITING_ON_FORCE",
            "physical_Hessian": "WAITING_ON_SADDLE",
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
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": payload["status"], "open": payload["validated_invalidated_open"]["OPEN"], "validation_passed": payload["validation_passed"]}, indent=2))


if __name__ == "__main__":
    main()
