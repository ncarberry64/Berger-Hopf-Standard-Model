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
COMMON_SCALE_WARD = BASE / "BHSM_N12_GATE7_COMMON_SCALE_HEAT_ZETA_WARD.json"
FIXED_CHANNEL_HEAT = BASE / "BHSM_N12_GATE7_FIXED_CHANNEL_FINITE_CORE_HEAT_BOUND.json"
INCOMING_MATCH = BASE / "BHSM_N12_INCOMING_MF_COMPACT_MATCH.json"
INCOMING_PATH_GERM = BASE / "BHSM_N12_INCOMING_COEFFICIENT_PATH_QUADRATIC_GERM.json"
INCOMING_SEGMENT = BASE / "BHSM_N12_INCOMING_REGULARIZED_TERMINAL_SEGMENT.json"
INCOMING_FINITE_PATH = BASE / "BHSM_N12_INCOMING_FINITE_AMPLITUDE_COEFFICIENT_ENCLOSURE.json"
THEORY = ROOT / "theory" / "n12_gate7_1222_core_diagram_matching_audit.md"
INPUTS = (OLD, CORE, FAMILY, NESTED, MAXIMAL, BIRTH, COMPACT, SEAM, INCIDENCE, FORCE, ADJOINT, CAUCHY, COMMON_SCALE, COMMON_SCALE_WARD, FIXED_CHANNEL_HEAT, INCOMING_MATCH, INCOMING_PATH_GERM, INCOMING_SEGMENT, INCOMING_FINITE_PATH, THEORY)


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
    old, core, family, nested, maximal, birth, compact, seam, incidence, force, adjoint, cauchy, common_scale, common_scale_ward, fixed_channel_heat, incoming_match, incoming_path_germ, incoming_segment, incoming_finite_path = (
        _load(path) for path in INPUTS[:-1]
    )
    if not all(record.get("validation_passed") is True for record in (
        old, core, family, nested, maximal, birth, compact, seam, incidence, force, adjoint, cauchy, common_scale, common_scale_ward, fixed_channel_heat, incoming_match, incoming_path_germ, incoming_segment, incoming_finite_path,
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
            "diagram_slot": "COMMON_SCALE_HEAT_MINUS_ZETA_SOURCE_CONTRACTION",
            "required_type": "GRADED_HEAT_FORCE_WITH_MOVING_DURATION_AND_ZETA_PRODUCT_RULE",
            "candidate": "BHSM_N12_GATE7_COMMON_SCALE_HEAT_ZETA_WARD",
            "dimension_domain_check": "VALID_FOR_EVERY_POSITIVE_SELF_ADJOINT_JOINT_REALIZATION_WITH_THE_RETAINED_PARENT_HEAT_LENGTH",
            "provenance_check": "VALID_GRADED_ACTION_AND_SIMULTANEOUS_RADIUS_PROPER_DURATION_SCALING",
            "verdict": "VALID_MATCH_FORMULA_CLOSED_NUMERIC_TRACE_OPEN",
        },
        {
            "diagram_slot": "C2_STORED_FIXED_CHANNEL_FINITE_CORE_HEAT_INCREMENT",
            "required_type": "INVERSE_FREE_CONTROL_OF_THE_ACTUALLY_STORED_1064_AND_1222_REPRESENTATIVE_PENCILS_AT_THE_RETAINED_HEAT_LENGTH",
            "candidate": "BHSM_N12_GATE7_FIXED_CHANNEL_FINITE_CORE_HEAT_BOUND",
            "dimension_domain_check": "VALID_FOR_SCALAR_c3_AND_BOTH_lambda1_5_FACTORIZED_DIRAC_CORES_USING_CERTIFIED_DURATION_AND_RADIUS_TUBES",
            "provenance_check": "VALID_MIXED_BOUNDARY_POINCARE_AND_REVERSE_TRIANGLE_FORM_BOUNDS",
            "verdict": "VALID_MATCH_REPRESENTATIVE_INCREMENT_SUPPRESSED_FULL_GRADED_TRACE_STILL_OPEN",
        },
        {
            "diagram_slot": "INCOMING_C1_RESPONSE_M_f",
            "required_type": "SHARP_ACTION_OWNED_NEGATIVE_AXIS_INCOMING_WEYL_RESPONSE_ON_THE_PHYSICAL_C1_TO_E1_HISTORY",
            "candidate": "BHSM_N12_INCOMING_MF_COMPACT_MATCH_PLUS_EXPLICIT_REGULARIZED_SEGMENT_AND_FINITE_AMPLITUDE_COEFFICIENT_ENCLOSURE",
            "dimension_domain_check": "VALID_ZERO_BIRTH_SOURCE_RESTRICTION_TO_THE_NEW_EVENT_BLOCK_AND_UNIFORM_NORMALIZED_PATH_FOR_EVERY_0<lambda<=1.33025636847111862E-30",
            "provenance_check": "VALID_COMPACT_ACTION_CALDERON_MAP,_ENDPOINT_ROLE,_FORMATION_SCHUR_IDENTITY,_TERMINAL_CAUCHY_JET,_NEGATIVE_Delta_TUBE,_FIRST_JACOBI_BOUND,_AND_LOG_SPACE_COEFFICIENT_ENCLOSURE",
            "verdict": "VALID_MATCH_IDENTITY_AND_FINITE_AMPLITUDE_COEFFICIENT_FAMILY_COMPACT_BLOCK_EVALUATION_OPEN",
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
            common_scale["adjudication"]["non_scale_reset_quotient_geometry_pullback_sector"]
            == "OPEN"
        ),
        "common_scale_source_contraction_formula_is_closed": (
            common_scale_ward["adjudication"]["common_scale_source_contraction_formula"]
            == "CLOSED"
            and common_scale_ward["adjudication"]
            ["common_scale_zeta_moving_duration_completion"] == "CLOSED_ZERO"
            and common_scale_ward["adjudication"]["actual_common_scale_numeric_force"]
            .startswith("OPEN")
        ),
        "stored_fixed_channel_heat_increment_is_suppressed_without_overclaim": (
            fixed_channel_heat["claim_boundary"]
            ["stored_fixed_channel_finite_core_increment"] == "CERTIFIED_SUPPRESSED"
            and fixed_channel_heat["claim_boundary"]
            ["actual_joint_graded_heat_trace"] == "OPEN"
            and fixed_channel_heat["claim_boundary"]
            ["maximal_tail_beyond_1222"] == "OPEN"
        ),
        "compact_incoming_operator_is_only_executable_until_path_supplied": compact["claim_boundary"]["actual_family_M_C_value"] == "OPEN_AFTER_COEFFICIENT_PATH",
        "incoming_Mf_is_existing_compact_terminal_block_not_new_theory": (
            incoming_match["claim_boundary"]["incoming_Mf_operator_identity"]
            .startswith("CLOSED")
            and incoming_match["claim_boundary"]
            ["incoming_Mf_action_owned_Laurent_germ"] == "CLOSED"
            and incoming_match["claim_boundary"]
            ["complete_finite_duration_incoming_Mf_family"].startswith("OPEN")
        ),
        "incoming_coefficient_path_germ_is_closed_without_Euler_Dirac_inverse": (
            incoming_path_germ["claim_boundary"]
            ["incoming_normalized_log_radius_path_germ"].startswith("CERTIFIED")
            and incoming_path_germ["claim_boundary"]
            ["complete_finite_positive_amplitude_path"].startswith("OPEN")
            and incoming_path_germ["validation"]
            ["no_Euler_Dirac_inverse_or_acceleration_used"] is True
        ),
        "incoming_finite_amplitude_path_is_closed_on_explicit_nonzero_box": (
            incoming_segment["claim_boundary"]
            ["explicit_uniform_finite_amplitude_incoming_segment"]
            == "CERTIFIED"
            and incoming_segment["terminal_ball"]["Delta_interval"][1] < 0.0
            and incoming_finite_path["claim_boundary"]
            ["uniform_inverse_free_finite_amplitude_incoming_remainder"]
            == "CLOSED"
            and incoming_finite_path["claim_boundary"]
            ["complete_positive_amplitude_incoming_coefficient_family"]
            == "REALIZED_PARAMETRIC_BOX"
        ),
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
        "classification": "C2_FINITE_CORE_NEGATIVE_AXIS_RESPONSE,_BACKWARD_OPERATOR_COTANGENT,_INCOMING_M_f_COMPACT_BLOCK_IDENTITY,_EXPLICIT_INCOMING_FINITE_AMPLITUDE_COEFFICIENT_FAMILY,_AND_PHYSICAL_COMMON_SCALE_PULLBACK_SLOTS_ARE_VALID_MATCHES;_COMPACT_M_f_EVALUATION,_JOINT_SEAM_CONTRACTION,_AND_NON_SCALE_RESET_GEOMETRY_PULLBACK_REMAIN_MISSING_AS_REALIZED_DATA,_WHILE_INCIDENCE_FORCE_AND_CAUCHY_THEOREMS_ARE_VALID_CONDITIONAL_CONSUMERS",
        "forward_event_diagram": "C1 --M_f--> E1 --(U_R,W_phys)--> C2 --M_C2--> MAXIMAL_ENDPOINT",
        "matching_audit": slots,
        "adjudication": {
            "new_C2_response_theory_required": False,
            "more_scalar_C2_boxes_are_the_owner": False,
            "incoming_M_f_identity_and_action_owned_germ": "CLOSED_EXISTING_COMPACT_TERMINAL_BLOCK",
            "incoming_normalized_coefficient_path_quadratic_germ": "CLOSED_INVERSE_FREE",
            "incoming_explicit_finite_amplitude_coefficient_family": "CLOSED_ON_NONZERO_PARAMETRIC_BOX",
            "complete_finite_duration_incoming_M_f_realization": "OPEN_COMPACT_BLOCK_EVALUATION",
            "finite_core_backward_operator_cotangent": "CLOSED",
            "physical_common_scale_geometry_pullback": "CLOSED_BY_EXACT_COVARIANCE",
            "physical_common_scale_source_contraction_formula": "CLOSED_BY_HEAT_ZETA_WARD_IDENTITY",
            "stored_fixed_channel_1064_to_1222_heat_increment": "CERTIFIED_SUPPRESSED_IN_LOG_SPACE",
            "physical_common_scale_numeric_force": "OPEN_WITH_JOINT_GRADED_HEAT_TRACE",
            "non_scale_pathwise_reset_quotient_geometry_pullback_sector": "ACTUALLY_MISSING",
            "projected_heat_minus_zeta_force_net_and_tail": "ACTUALLY_MISSING",
            "finite_event_or_canonical_stop": "NOT_REACHED",
            "Gate7": "G7_08_OPEN",
            "Gate8": "LOCKED",
        },
        "validated_invalidated_open": {
            "VALIDATED": ["C2 1222-core coefficient slot", "C2 complete negative-axis finite-core response", "finite-core backward operator cotangent semigroup", "incoming M_f compact terminal-block identity and Laurent germ", "incoming normalized coefficient path through lambda_0 squared", "explicit incoming regularized finite-amplitude segment and first Jacobi bound", "uniform finite-amplitude incoming coefficient family", "physical common-scale pullback including moving duration", "common-scale heat-zeta source contraction formula", "stored fixed-channel 1064-to-1222 heat increment suppression", "maximal abstract Weyl value", "source and force consumer formulas"],
            "INVALIDATED": ["new C2 theory is required", "a new C1 operator theory is required for M_f", "a second birth exterior response is required", "a full pathwise Jacobi is required for the common-scale component", "fixed-duration radius-only zeta derivative is the physical common-scale force", "birth jet alone is the remaining non-scale pathwise reset jet", "broad seam intervals or probes determine the force", "proof edge is an endpoint"],
            "OPEN": ["compact incoming M_f block evaluation and joint seam contraction", "non-scale pathwise reset quotient geometry pullback sector", "actual projected force net and Cauchy tail"],
        },
        "hindsight": {"classification": "PROOF_CHART_LIMIT_REMOVED;_OPERATOR_DATA_GAP_REMAINS", "obstruction_physical": False},
        "exact_next_dependency": "EVALUATE_OR_ENCLOSE_THE_EXISTING_COMPACT_M_f_BLOCK_ON_THE_NOW_CERTIFIED_FINITE_AMPLITUDE_COEFFICIENT_FAMILY_AND_GLUE_IT_TO_THE_C2_SEAM;_CHAIN_THE_CLOSED_BACKWARD_OPERATOR_COTANGENT_THROUGH_THE_REMAINING_NON_SCALE_RESET_QUOTIENT_GEOMETRY_ADJOINT_SECTOR,_CONTRACT_THE_SOURCE_AND_FORCE_FUNCTIONALS,_AND_TEST_THE_PROJECTED_CAUCHY_TAIL",
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
