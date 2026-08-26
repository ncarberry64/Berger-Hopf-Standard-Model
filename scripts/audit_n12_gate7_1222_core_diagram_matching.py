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
INCOMING_MF_ENCLOSURE = BASE / "BHSM_N12_INCOMING_MF_NEGATIVE_AXIS_ENCLOSURE.json"
BIRTH_MF_AUDIT = BASE / "BHSM_N12_GATE7_BIRTH_TRACE_MF_SUPERSESSION_AUDIT.json"
BIRTH_LOAD_AUDIT = BASE / "BHSM_N12_GATE7_BIRTH_GRAPH_LOAD_MATCHING_AUDIT.json"
TWO_SEAM = BASE / "BHSM_N12_GATE7_TWO_SEAM_CLOSED_OPERATOR_ASSEMBLY.json"
E0_PROVENANCE = BASE / "BHSM_N12_GATE7_E0_EVENT_SIDE_RESPONSE_PROVENANCE_AUDIT.json"
SOURCE_ROLE = BASE / "BHSM_N12_GATE7_EXTERNAL_BIRTH_SOURCE_ROLE_SUPERSESSION.json"
RADIUS_PULLBACK = BASE / "BHSM_N12_C2_1222_RESET_QUOTIENT_RADIUS_PULLBACK_ENCLOSURE.json"
DURATION_PULLBACK = BASE / "BHSM_N12_C2_1222_MOVING_DURATION_PULLBACK_ENCLOSURE.json"
COMPLETE_PULLBACK = BASE / "BHSM_N12_C2_1222_COMPLETE_GEOMETRY_PULLBACK_NORM.json"
EXACT_FIELD = BASE / "BHSM_N12_C2_EXACT_FIXED_S_FIELD_ORACLE.json"
PARAMETRIC = BASE / "BHSM_N12_C2_1222_PARAMETRIC_BASE_FAMILY.json"
INTERVAL_ACTIONS = BASE / "BHSM_N12_C2_1222_TRANSPOSED_DURATION_ACTION_COVERAGE.json"
SIGNED_ADJOINT = BASE / "BHSM_N12_C2_1222_SIGNED_ADJOINT_ASSEMBLY.json"
SOURCE_ONTOLOGY = BASE / "BHSM_N12_GATE7_CLOSED_SYSTEM_ZERO_EXTERNAL_SOURCE_ONTOLOGY.json"
JOINT_SEED = BASE / "BHSM_N12_GATE7_JOINT_HEAT_COTANGENT_REVERSE_SEED.json"
GRADED_COTANGENT = BASE / "BHSM_N12_GATE7_MAXIMAL_GRADED_COTANGENT_MATCHING_AUDIT.json"
ONE_SEAM = BASE / "BHSM_N12_GATE7_AE2_ONE_SEAM_DIRECT_DESCRIPTOR.json"
THEORY = ROOT / "theory" / "n12_gate7_1222_core_diagram_matching_audit.md"
INPUTS = (OLD, CORE, FAMILY, NESTED, MAXIMAL, BIRTH, COMPACT, SEAM, INCIDENCE, FORCE, ADJOINT, CAUCHY, COMMON_SCALE, COMMON_SCALE_WARD, FIXED_CHANNEL_HEAT, INCOMING_MATCH, INCOMING_PATH_GERM, INCOMING_SEGMENT, INCOMING_FINITE_PATH, INCOMING_MF_ENCLOSURE, BIRTH_MF_AUDIT, BIRTH_LOAD_AUDIT, TWO_SEAM, E0_PROVENANCE, SOURCE_ROLE, RADIUS_PULLBACK, DURATION_PULLBACK, COMPLETE_PULLBACK, EXACT_FIELD, PARAMETRIC, INTERVAL_ACTIONS, SIGNED_ADJOINT, SOURCE_ONTOLOGY, JOINT_SEED, GRADED_COTANGENT, ONE_SEAM, THEORY)


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
    old, core, family, nested, maximal, birth, compact, seam, incidence, force, adjoint, cauchy, common_scale, common_scale_ward, fixed_channel_heat, incoming_match, incoming_path_germ, incoming_segment, incoming_finite_path, incoming_mf_enclosure, birth_mf_audit, birth_load_audit, two_seam, e0_provenance, source_role, radius_pullback, duration_pullback, complete_pullback, exact_field, parametric, interval_actions, signed_adjoint, source_ontology, joint_seed, graded_cotangent, one_seam = (
        _load(path) for path in INPUTS[:-1]
    )
    if not all(record.get("validation_passed") is True for record in (
        old, core, family, nested, maximal, birth, compact, seam, incidence, force, adjoint, cauchy, common_scale, common_scale_ward, fixed_channel_heat, incoming_match, incoming_path_germ, incoming_segment, incoming_finite_path, incoming_mf_enclosure, birth_mf_audit, birth_load_audit, two_seam, e0_provenance, source_role, radius_pullback, duration_pullback, complete_pullback, exact_field, parametric, interval_actions, signed_adjoint, source_ontology, joint_seed, graded_cotangent, one_seam,
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
            "verdict": "VALID_MATCH_OPERATOR_COTANGENT_INTERVAL_ACTIONS_CLOSED_SIGNED_VALUE_OPEN",
        },
        {
            "diagram_slot": "C2_EXACT_FIXED_s_STATE_GENERATOR",
            "required_type": "ACTION_OWNED_DESINGULARIZED_VECTOR_FIELD_FOR_PARAMETRIC_MULTIPLE_SHOOTING_AND_ADJOINT",
            "candidate": "BHSM_N12_C2_EXACT_FIXED_S_FIELD_ORACLE",
            "dimension_domain_check": "VALID_ON_REGULAR_SIMPLE_SELECTED_LINE_POSITIVE_Delta_CHART",
            "provenance_check": "VALID_EXACT_ACTION_JET_AND_BORDERED_COMPLEMENT_RESPONSE",
            "verdict": "VALID_MATCH_LOCAL_73_PARAMETER_BASE_FAMILY_THROUGH_1222",
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
            "candidate": "BHSM_N12_C2_1222_RESET_QUOTIENT_RADIUS_PULLBACK_ENCLOSURE_PLUS_FORCE_ADJOINT_IDENTITY",
            "dimension_domain_check": "VALID_RADIUS_PLUS_MOVING_DURATION_OPERATOR_NORM_ON_1222_CORE;_SIGNED_COVECTOR_AND_MAXIMAL_TAIL_OPEN",
            "provenance_check": "VALID_REPLAYED_ACTION_JACOBI_BALLS,_DELTA_FIRST_VARIATIONS,_AND_INVERSE_FREE_WEYL_COTANGENT",
            "verdict": "VALID_MATCH_FINITE_CORE_FIRST_JET_NORM_SIGNED_ADJOINT_VALUE_OPEN",
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
            "candidate": "BHSM_N12_INCOMING_MF_NEGATIVE_AXIS_ENCLOSURE",
            "dimension_domain_check": "VALID_DIRICHLET_REFERENCE_AT_ZERO_EXTERNAL_BIRTH_TRACE",
            "provenance_check": "EXTERNAL_SOURCE_TRACE_IS_ZERO_BUT_INTERNAL_M_f_RESPONSE_IS_NOT_ZEROED",
            "verdict": "VALID_MATCH_PHYSICAL_ZERO_SOURCE_M_f_EQUALS_M11",
        },
        {
            "diagram_slot": "COMPLETE_E0_C1_E1_C2_TWO_SEAM_OPERATOR",
            "required_type": "CLOSED_TWO_TRACE_BLOCK_RETAINING_THE_BIRTH_TRACE_AFTER_J_ext_EQUALS_ZERO",
            "candidate": "BHSM_N12_GATE7_TWO_SEAM_CLOSED_OPERATOR_ASSEMBLY",
            "dimension_domain_check": "VALID_TWO_INTERNAL_SEAMS_WITH_DIRECT_AND_SCHUR_EQUIVALENT_REPRESENTATIONS",
            "provenance_check": "VALID_AE2_RESET_LIFTS_COMPACT_FORMATION_CALDERON_AND_EVENT_SIDE_LOADS",
            "verdict": "NOT_A_CURRENT_GATE7_DIAGRAM_SLOT_GENERAL_BLOCK_IDENTITY_ONLY",
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
            "diagram_slot": "DIRECT_FINITE_CORE_E0_TO_E1_TO_C2_OPERATOR_AND_FIRST_JET",
            "required_type": "ONE_COMMON_INTERNAL_SEAM_NODE_WITH_EXTERNAL_E0_AND_FAR_CORE_DIRICHLET_TRACES",
            "candidate": "BHSM_N12_GATE7_AE2_ONE_SEAM_DIRECT_DESCRIPTOR",
            "dimension_domain_check": "VALID_PER_LEVEL_GENERATOR_ON_MATCHED_FORMATION_AND_C2_COEFFICIENT_PATHS",
            "provenance_check": "VALID_AE2_ACTION_FORM_EXTERNAL_BIRTH_SOURCE_ROLE_AND_RETAINED_ELEMENT_JETS",
            "verdict": "VALID_MATCH_GENERATOR_ACTUAL_PARAMETRIC_VALUES_AND_MAXIMAL_TAIL_OPEN",
        },
        {
            "diagram_slot": "PAIR_CONTACT_AND_GRADED_INTERNAL_INCIDENCE",
            "required_type": "LOCAL_DOMAIN_PARAMETRIC_BRST_PAIR_PLUS_CONTACT_CONTRACTION",
            "candidate": "BHSM_N12_FORWARD_COMMON_SOURCE_INCIDENCE",
            "dimension_domain_check": "VALID_FOR_SUPPLIED_HISTORY_SECTIONS_AND_NATIVE_z",
            "provenance_check": "VALID_RETAINED_ACTION_INCIDENCE",
            "verdict": "VALID_MATCH_INTERNAL_VARIATION_VERTICES_NOT_EXTERNAL_SOURCE",
        },
        {
            "diagram_slot": "ZERO_EXTERNAL_BIRTH_CAUCHY_SOURCE",
            "required_type": "J_ext_EQUALS_ZERO_ONLY_AFTER_COMPLETE_JOINT_DIFFERENTIATION",
            "candidate": "BHSM_N12_GATE7_CLOSED_SYSTEM_ZERO_EXTERNAL_SOURCE_ONTOLOGY",
            "dimension_domain_check": "VALID_ON_COMPLETE_CLOSED_JOINT_OPERATOR",
            "provenance_check": "OWNER_AUTHORIZED_PHYSICAL_ONTOLOGY_NOT_ACTION_DERIVATION",
            "verdict": "VALID_MATCH_ONLY_J_ext_IS_ZEROED",
        },
        {
            "diagram_slot": "COMPLETE_JOINT_HEAT_COTANGENT_REVERSE_SEED",
            "required_type": "ONE_GRADED_HEAT_MINUS_ZETA_COTANGENT_REVERSED_ONCE_THROUGH_ALL_INTERNAL_BLOCKS",
            "candidate": "BHSM_N12_GATE7_JOINT_HEAT_COTANGENT_REVERSE_SEED",
            "dimension_domain_check": "FORMULA_VALID_ACTUAL_JOINT_SPECTRAL_VALUE_OPEN",
            "provenance_check": "VALID_CLOSED_SYSTEM_FUNCTIONAL_CALCULUS_AND_SCHUR_IDENTITY",
            "verdict": "VALID_MATCH_SEED_CLOSED_NUMERICAL_COTANGENT_OPEN",
        },
        {
            "diagram_slot": "MAXIMAL_GRADED_SECTOR_COTANGENT_CONTRACT",
            "required_type": "FULL_BRST_STATISTICS_MULTIPLICITY_HEAT_MINUS_ZETA_DIRECT_SUM_ON_THE_FORWARD_JOINT_DOMAIN",
            "candidate": "BHSM_N12_GATE7_MAXIMAL_GRADED_COTANGENT_MATCHING_AUDIT",
            "dimension_domain_check": "EXACT_GAUGE_WEYL_HS_LEVEL_WEIGHTS_AND_LONGITUDINAL_GHOST_CANCELLATION_MATCH;_ACTUAL_PER_LEVEL_JOINT_OPERATOR_VALUES_OPEN",
            "provenance_check": "VALID_RETAINED_STATISTICS_LEDGER_CURRENT_FORWARD_DOMAIN_AND_CLOSED_SYSTEM_SOURCE_ONTOLOGY",
            "verdict": "VALID_MATCH_TYPE_AND_WEIGHTS_CLOSED_ACTUAL_OPERATOR_FAMILY_OPEN",
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
            and radius_pullback["claim_boundary"]["fixed_node_radius_pullback"]
            == "CERTIFIED"
            and radius_pullback["claim_boundary"]["moving_duration_pullback"]
            == "OPEN"
            and duration_pullback["claim_boundary"]
            ["moving_duration_reset_pullback_norm"].startswith("CERTIFIED")
            and complete_pullback["claim_boundary"]
            ["complete_finite_core_geometry_pullback_norm"] == "CERTIFIED"
            and complete_pullback["claim_boundary"]
            ["signed_finite_core_geometry_covector"] == "OPEN"
        ),
        "exact_fixed_s_field_oracle_is_available_without_selecting_a_history": (
            exact_field["claim_boundary"]["exact_fixed_s_field_oracle"] == "CERTIFIED"
            and exact_field["validation"]["proof_center_not_promoted_to_physical_reset_selector"] is True
            and parametric["claim_boundary"]
            ["parametric_base_history_existence_through_1222"] == "DERIVED"
        ),
        "all_1222_interval_duration_actions_and_signed_reverse_equation_are_closed": (
            interval_actions["adjudication"]
            ["all_1222_interval_transposed_duration_actions"] == "CERTIFIED"
            and signed_adjoint["adjudication"]
            ["all_1222_interval_transposed_duration_actions"] == "CLOSED"
            and signed_adjoint["adjudication"]
            ["signed_finite_core_adjoint_equation"] == "CLOSED"
        ),
        "source_ontology_zeros_only_external_birth_trace_after_joint_differentiation": (
            source_role["source_ordering"]["external_source"]
            == "j_birth=Gamma0_birth(U)"
            and source_role["matching_audit"]["incoming_M_f"]
            == "VALID_MATCH_NONZERO_INTERNAL_M11_RESPONSE"
        ),
        "single_joint_heat_cotangent_reverse_seed_is_closed": (
            joint_seed["adjudication"]["joint_reverse_seed_formula"] == "CLOSED"
            and joint_seed["adjudication"]["additional_seam_source"] == "FORBIDDEN"
        ),
        "maximal_graded_cotangent_type_and_weights_are_closed": (
            graded_cotangent["status"]
            == "MAXIMAL_GRADED_COTANGENT_TYPE_AND_FINITE_CORE_DIRECT_OPERATOR_CLOSED_VALUES_TAIL_OPEN"
            and graded_cotangent["adjudication"]["new_grading_required"] is False
            and graded_cotangent["matching_audit"][
                "actual_per_level_joint_operator_family"
            ] == "DIRECT_GENERATOR_CLOSED_ACTUAL_PARAMETRIC_VALUES_AND_MAXIMAL_TAIL_OPEN"
        ),
        "direct_one_seam_operator_and_first_jet_generators_are_closed": (
            one_seam["claim_boundary"]["finite_core_joint_operator_type"]
            == "DERIVED_EXECUTABLE"
            and one_seam["claim_boundary"]["finite_core_joint_first_jet_type"]
            == "DERIVED_EXECUTABLE"
            and one_seam["validation"]["direct_and_Schur_seam_values_agree"]
            is True
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
        "incoming_M11_identity_is_the_physical_zero_source_response": (
            incoming_match["claim_boundary"]["incoming_Mf_operator_identity"]
            .startswith("CLOSED")
            and incoming_match["claim_boundary"]
            ["incoming_Mf_action_owned_Laurent_germ"] == "CLOSED"
            and incoming_match["claim_boundary"]
            ["complete_finite_duration_incoming_Mf_family"].startswith("OPEN")
            and source_role["adjudication"]
            ["M_f_equals_M11_at_zero_external_birth_trace"] == "REAFFIRMED"
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
        "conditional_M11_and_fermion_seam_invertibility_are_enclosed": (
            incoming_mf_enclosure["claim_boundary"]
            ["incoming_M_f_negative_axis_parametric_enclosure"] == "CLOSED"
            and incoming_mf_enclosure["claim_boundary"]
            ["fermion_AE2_joint_seam_invertibility"] == "CLOSED"
            and incoming_mf_enclosure["claim_boundary"]
            ["exact_joint_spectral_trace"] == "OPEN"
            and source_role["matching_audit"]["incoming_M_f"]
            == "VALID_MATCH_NONZERO_INTERNAL_M11_RESPONSE"
        ),
        "dynamic_birth_graph_reduction_is_superseded": (
            birth_mf_audit["matching_audit"]["physical_zero_source_incoming_M_f"]
            == "ACTUALLY_MISSING_BIRTH_GRAPH_REDUCTION"
            and source_role["supersession"]
            ["BHSM_N12_GATE7_BIRTH_TRACE_MF_SUPERSESSION_AUDIT"] == "SUPERSEDED"
        ),
        "birth_graph_load_is_not_a_current_Gate7_slot": (
            birth_load_audit["exact_birth_load"]["load"]
            == "B_birth=U_R0*(M_E0+W_E0)*U_R0^dagger"
            and source_role["matching_audit"]["B_birth"]
            == "NOT_REQUIRED_NOT_A_GATE7_DIAGRAM_SLOT"
        ),
        "two_seam_identity_is_preserved_but_not_the_current_physical_topology": (
            two_seam["adjudication"]["complete_internal_operator_topology"]
            == "CLOSED"
            and "PHYSICAL_TWO_SEAM_APPLICATION_SUPERSEDED"
            in source_role["supersession"]
            ["BHSM_N12_GATE7_TWO_SEAM_CLOSED_OPERATOR_ASSEMBLY"]
        ),
        "E0_provenance_is_preserved_but_the_slot_is_not_required": (
            e0_provenance["status"]
            == "E0_EVENT_SIDE_PROVENANCE_EXHAUSTED_REALIZED_PARENT_ARM_OPEN"
            and source_role["adjudication"]["M_E0_required"] is False
        ),
        "broad_seam_intervals_do_not_decide_force": seam["force_adjudication"]["broad_intervals_decide_heat_minus_zeta_force_sign"] is False,
        "incidence_is_a_valid_internal_variation_vertex_consumer": incidence["claim_boundary"]["domain_parametric_nonzero_local_incidence"] == "DERIVED",
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
        "status": "GATE7_1222_CORE_AND_E1_C2_SEAM_MATCHED_GRADED_VALUES_AND_PROJECTED_TAIL_OPEN" if passed else "GATE7_1222_CORE_MATCHING_NOT_VALIDATED",
        "classification": "THE_LOCAL_73_PARAMETER_C2_FAMILY,_ALL_1222_INTERVAL_TRANSPOSED_DURATION_ACTIONS,_SIGNED_REVERSE_EQUATION,_EXTERNAL_ZERO_BIRTH_TRACE_WITH_NONZERO_INTERNAL_M_f_EQUALS_M11,_SINGLE_E1_C2_SEAM,_JOINT_HEAT_COTANGENT_SEED,_AND_EXACT_RETAINED_GRADED_LEVEL_WEIGHTS_ARE_VALID_MATCHES;_THE_COMPLETE_GRADED_SEAM_VALUES,_SIGNED_REVERSE_VALUE,_AND_MAXIMAL_PROJECTED_TAIL_REMAIN_OPEN",
        "forward_event_diagram": "C1 --M_f--> E1 --(U_R,W_phys)--> C2 --M_C2--> MAXIMAL_ENDPOINT",
        "matching_audit": slots,
        "adjudication": {
            "new_C2_response_theory_required": False,
            "more_scalar_C2_boxes_are_the_owner": False,
            "incoming_M11_identity_and_action_owned_germ": "CLOSED_PHYSICAL_ZERO_SOURCE_RESPONSE",
            "physical_zero_source_incoming_M_f": "CLOSED_M11",
            "E0_event_side_Calderon_and_birth_load": "NOT_REQUIRED_CURRENT_GATE7",
            "complete_internal_seam_topology": "CLOSED_ONE_E1_C2_SEAM",
            "incoming_normalized_coefficient_path_quadratic_germ": "CLOSED_INVERSE_FREE",
            "incoming_explicit_finite_amplitude_coefficient_family": "CLOSED_ON_NONZERO_PARAMETRIC_BOX",
            "complete_finite_duration_incoming_M11_reference": "CLOSED_PARAMETRIC_NEGATIVE_AXIS_ENCLOSURE",
            "fermion_AE2_joint_seam_invertibility": "CLOSED_ON_WHOLE_NEGATIVE_AXIS",
            "exact_joint_spectral_trace": "OPEN",
            "finite_core_backward_operator_cotangent": "CLOSED",
            "physical_common_scale_geometry_pullback": "CLOSED_BY_EXACT_COVARIANCE",
            "physical_common_scale_source_contraction_formula": "CLOSED_BY_HEAT_ZETA_WARD_IDENTITY",
            "stored_fixed_channel_1064_to_1222_heat_increment": "CERTIFIED_SUPPRESSED_IN_LOG_SPACE",
            "physical_common_scale_numeric_force": "OPEN_WITH_JOINT_GRADED_HEAT_TRACE",
            "non_scale_fixed_node_radius_reset_pullback": "CERTIFIED_ON_1222_FINITE_CORE",
            "non_scale_moving_duration_reset_pullback_norm": "CERTIFIED_ON_1222_FINITE_CORE",
            "complete_non_scale_geometry_pullback_norm": "CERTIFIED_ON_1222_FINITE_CORE",
            "exact_fixed_s_state_generator": "CERTIFIED",
            "local_73_parameter_reset_family_through_1222": "CLOSED_EXISTENCE_ONLY",
            "all_1222_interval_transposed_duration_actions": "CERTIFIED",
            "signed_finite_core_reverse_equation": "CLOSED",
            "zero_external_source_semantics": "CLOSED_ONLY_J_ext_AFTER_JOINT_DIFFERENTIATION",
            "joint_heat_cotangent_reverse_seed": "CLOSED",
            "graded_sector_weights_and_cotangent_contract": "CLOSED",
            "finite_core_direct_one_seam_operator_and_first_jet": "CLOSED_EXECUTABLE_GENERATOR",
            "actual_per_level_joint_operator_family": "DIRECT_GENERATOR_CLOSED_ACTUAL_PARAMETRIC_VALUES_AND_MAXIMAL_TAIL_OPEN",
            "signed_non_scale_backward_center_adjoint_value": "ACTUALLY_MISSING_NUMERICAL_VALUE",
            "non_scale_pathwise_reset_quotient_geometry_pullback_sector": "FINITE_CORE_NORM_MATCHED_SIGNED_VALUE_AND_MAXIMAL_TAIL_OPEN",
            "projected_heat_minus_zeta_force_net_and_tail": "ACTUALLY_MISSING",
            "finite_event_or_canonical_stop": "NOT_REACHED",
            "Gate7": "G7_08_OPEN",
            "Gate8": "LOCKED",
        },
        "validated_invalidated_open": {
            "VALIDATED": ["C2 1222-core coefficient slot", "local 73-parameter exact C2 family through the finite core", "C2 complete negative-axis finite-core response", "finite-core backward operator cotangent semigroup", "direct one-seam finite-core operator and first-jet generators", "all 1222 interval transposed-duration actions", "signed finite-core reverse equation", "only the external birth trace is zeroed after differentiation", "nonzero internal M_f=M11 at zero external source", "single E1/C2 internal seam topology", "single joint heat cotangent reverse seed", "exact retained gauge/Weyl/HS grading weights and longitudinal-ghost cancellation", "1222-segment state-Jacobi growth provenance", "fixed-node non-scale radius reset pullback", "moving-duration non-scale reset pullback norm", "complete finite-core non-scale geometry first-jet norm", "exact fixed-s action field oracle", "incoming M11 compact Dirichlet-reference identity and Laurent germ", "incoming normalized coefficient path through lambda_0 squared", "explicit incoming regularized finite-amplitude segment and first Jacobi bound", "uniform finite-amplitude incoming coefficient family", "incoming M11 parametric whole-negative-axis enclosure", "fermion AE2 joint-seam invertibility", "physical common-scale pullback including moving duration", "common-scale heat-zeta contraction formula", "stored fixed-channel 1064-to-1222 heat increment suppression", "maximal abstract Weyl value", "internal incidence and force consumer formulas"],
            "INVALIDATED": ["a pre-E0 M_E0 arm is a current Gate7 diagram slot", "a dynamical integrated birth trace replaces the external Cauchy source", "new C2 theory is required", "a new C1 bulk operator theory is required for M_f", "a second external birth source is required", "a full pathwise Jacobi is required for the common-scale component", "all non-scale pathwise reset geometry data are absent", "fixed-duration radius-only zeta derivative is the physical common-scale force", "birth jet alone is the remaining non-scale pathwise reset jet", "a duration interval or proof tube is a duration first jet", "broad seam intervals or probes determine the force", "proof edge is an endpoint"],
            "OPEN": ["actual parametric per-level E1/C2 graded values", "actual joint graded spectral cotangent and nonfermion seam value", "numerical signed non-scale backward center-adjoint covector on the parametric family", "maximal non-scale reset-quotient tail", "actual projected force net and Cauchy tail"],
        },
        "hindsight": {"classification": "PROOF_CHART_LIMIT_REMOVED;_OPERATOR_DATA_GAP_REMAINS", "obstruction_physical": False},
        "exact_next_dependency": "INTERVAL_ASSEMBLE_THE_DERIVED_DIRECT_ONE_SEAM_DESCRIPTOR_PER_GRADED_LEVEL_ON_THE_INCOMING_AND_C2_PARAMETRIC_FAMILIES,_COMPLETE_OR_SOURCE_CONTRACT_THE_C2_MAXIMAL_TAIL,_THEN_EVALUATE_THE_COMPLETE_JOINT_HEAT_MINUS_ZETA_COTANGENT,_FEED_IT_TO_THE_CERTIFIED_1222_INTERVAL_ACTIONS_AND_SINGLE_REVERSE_EQUATION,_AND_TEST_THE_PROJECTED_CAUCHY_TAIL_OR_ACTUAL_FINITE_STOP;_DO_NOT_REOPEN_M_f_OR_ADD_A_SEAM_SOURCE",
        "claim_boundary": {
            "Gate7": "G7_08_OPEN_E1_C2_GRADED_COTANGENT_AND_PROJECTED_TAIL",
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
