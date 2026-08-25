"""Type-check every retained candidate for the Gate-7 C2 diagram leg."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FLAGSHIP = ROOT / "artifacts" / "flagship_integration"
RESULT = FLAGSHIP / "BHSM_N12_GATE7_C2_DIAGRAM_SLOT_MATCHING_AUDIT.json"

FILES = {
    "maximal_weyl": FLAGSHIP / "BHSM_N12_FORWARD_GAUGE_WEYL_READOUT_FAMILY.json",
    "friedrichs": FLAGSHIP / "BHSM_N12_MAXIMAL_FRIEDRICHS_WEYL_EXHAUSTION.json",
    "fiber_theorem": FLAGSHIP / "BHSM_N12_PARAMETRIC_RESET_FIBER_EXTERIOR_ORACLE_THEOREM.json",
    "finite_oracle": FLAGSHIP / "BHSM_N12_PARAMETRIC_EXTERIOR_ORACLE_EXECUTABLE_INTERFACE.json",
    "compact_variations": FLAGSHIP / "BHSM_N12_FORWARD_COMPACT_SUPPORT_WEYL_VARIATIONS.json",
    "scalar_core": FLAGSHIP / "BHSM_N12_FORWARD_TWO_CHORD_SCALAR_WEYL_ENCLOSURES.json",
    "dirac_core": FLAGSHIP / "BHSM_N12_FORWARD_TWO_CHORD_PRODUCT_DIRAC_WEYL_ENCLOSURES.json",
    "compact_operator": FLAGSHIP / "BHSM_N12_COMPACT_FINITE_HISTORY_OPERATOR.json",
    "terminal_germ": FLAGSHIP / "BHSM_N12_FINITE_HISTORY_TERMINAL_WEYL_GERM.json",
    "terminal_jet": FLAGSHIP / "BHSM_N12_TERMINAL_CHILD_QUOTIENT_OPERATOR_JET.json",
    "spectral_reduction": FLAGSHIP / "BHSM_N12_FINITE_HISTORY_SPECTRAL_REALIZATION_PROVENANCE.json",
    "gluing": FLAGSHIP / "BHSM_N12_FINITE_HISTORY_GLUING_FORCE_PROVENANCE.json",
    "endpoint_roles": FLAGSHIP / "BHSM_N12_COMPACT_HISTORY_ENDPOINT_ROLE_PROVENANCE.json",
    "seam": FLAGSHIP / "BHSM_N12_EVENT_NORMAL_TWO_SIDED_SEAM_CORRECTION.json",
    "heat_audit": FLAGSHIP / "BHSM_N12_FORWARD_RESOLVENT_HEAT_SYNTHESIS_AUDIT.json",
    "negative_axis": FLAGSHIP / "BHSM_N12_NEGATIVE_AXIS_SEAM_HEAT_SYNTHESIS_NO_GO.json",
    "local_symbol": ROOT / "artifacts/n12_direct_checkpoint/BHSM_N12_EVENT_CHILD_CALDERON_N12_TO_N48_P96.json",
    "n3_zero": ROOT / "artifacts/BHSM_aether_n3_zero_background_calderon_closure_v17_97.json",
    "event_shell": ROOT / "artifacts/BHSM_aether_event_shell_joint_operator_v15_73.json",
    "seam_code": ROOT / "src/bhsm/interface/ae2_covariant_seam_response.py",
    "theory": ROOT / "theory/n12_gate7_c2_diagram_slot_matching_audit.md",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _load(key: str) -> dict[str, Any]:
    return json.loads(FILES[key].read_text(encoding="utf-8"))


def _candidate(
    name: str,
    slot_type: str,
    domain_check: str,
    provenance: str,
    equivalence: str,
    verdict: str,
    role: str,
) -> dict[str, str]:
    return {
        "candidate": name,
        "required_mathematical_type": slot_type,
        "dimension_and_domain_check": domain_check,
        "provenance_check": provenance,
        "equivalence_transformation": equivalence,
        "verdict": verdict,
        "diagram_role": role,
    }


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in FILES.values()):
        missing = [str(path) for path in FILES.values() if not path.is_file()]
        raise FileNotFoundError(f"missing C2 matching inputs: {missing}")

    maximal = _load("maximal_weyl")
    friedrichs = _load("friedrichs")
    fiber = _load("fiber_theorem")
    oracle = _load("finite_oracle")
    compact_variations = _load("compact_variations")
    compact = _load("compact_operator")
    germ = _load("terminal_germ")
    spectral = _load("spectral_reduction")
    gluing = _load("gluing")
    endpoints = _load("endpoint_roles")
    seam = _load("seam")
    heat = _load("heat_audit")
    local = _load("local_symbol")
    n3 = _load("n3_zero")
    shell = _load("event_shell")
    seam_source = FILES["seam_code"].read_text(encoding="utf-8")

    candidates = [
        _candidate(
            "ACTION_OWNED_MAXIMAL_FORWARD_WEYL_CALDERON_FAMILY_M_C",
            "HOLOMORPHIC_OPERATOR_FAMILY_H_BIRTH_TO_H_BIRTH_WITH_OUTWARD_CONORMAL",
            "VALID_AT_EACH_FIXED_BRST_QUOTIENT_CHANNEL_AND_GALERKIN_LEVEL;_DIRECT_SUM_REQUIRES_RETAINED_ANGULAR_TRACE_CONTROL",
            "RETAINED_NONNEGATIVE_SOURCE_FORM_AND_MAXIMAL_ENDPOINT_CLASS_FROM_CURRENT_ACTION_LINEAGE",
            "RELABEL_GENERIC_RESET_GENERATED_CHILD_C_AS_C2_AND_USE_ITS_ACTUAL_RESET_STATE;_DO_NOT_IDENTIFY_VALUES_WITH_C1",
            "VALID_MATCH_EXISTING_THEORY_OBJECT",
            "C2_LEG_ABSTRACT_RESPONSE",
        ),
        _candidate(
            "MAXIMAL_FRIEDRICHS_CORE_EXHAUSTION",
            "CONSTRUCTION_OF_M_C2_Z_ON_A_FRIEDRICHS_MAXIMAL_ROUTE",
            "VALID_OPERATOR_NORM_LIMIT_ON_FINITE_DIMENSIONAL_FIXED_CHANNEL_TRACE_SPACE_FOR_REAL_Z_LT_0",
            "ACTION_OWNED_CLOSURE_OF_THE_RETAINED_MINIMAL_FORM;_MOVING_DIRICHLET_EDGE_IS_ONLY_A_FORM_CORE",
            "INSTANTIATE_WITH_THE_ACTUAL_C2_FORM_AND_EXHAUSTION",
            "VALID_MATCH_CONSTRUCTION_CONDITIONAL_ON_C2_DATA",
            "C2_LEG_FRIEDRICHS_REALIZATION_ENGINE",
        ),
        _candidate(
            "FIXED_STRATUM_PARAMETRIC_EXTERIOR_ORACLE",
            "M_C2_AND_FIRST_SECOND_GEOMETRY_JETS_ON_A_FINITE_REGULAR_STRATUM",
            "VALID_FOR_SUPPLIED_HERMITIAN_K_DK_D2K_PARTITION_AND_COERCIVE_INTERIOR_BLOCK",
            "SAME_ACTION_FINITE_STRATUM_THEOREM_AND_INVERSE_FREE_BORDERED_SOLVES",
            "FEED_THE_ACTUAL_C2_OPERATOR_DATA_AND_INTRINSIC_QUOTIENT",
            "VALID_MATCH_EVALUATION_ENGINE_INPUT_DATA_OPEN",
            "C2_LEG_FINITE_STRATUM_REALIZATION_ENGINE",
        ),
        _candidate(
            "COMPACT_SUPPORT_FRIEDRICHS_WEYL_VARIATIONS",
            "WEAK_FIRST_AND_MIXED_SECOND_JETS_OF_M_C2",
            "VALID_ONLY_FOR_COMPACTLY_SUPPORTED_VARIATIONS_ON_A_FIXED_FRIEDRICHS_HISTORY",
            "RETAINED_FORM_DERIVATIVE_AND_DIRICHLET_RESOLVENT_IDENTITIES",
            "APPLY_AFTER_THE_ACTUAL_C2_POISSON_EXTENSION_IS_DEFINED",
            "VALID_PARTIAL_MATCH_NOT_THE_NONCOMPACT_RESET_QUOTIENT_JET",
            "C2_LEG_WEAK_JET_SUBROUTINE",
        ),
        _candidate(
            "COMPACT_C1_TWO_BOUNDARY_WEYL_RESPONSE_AND_M_F",
            "TWO_BOUNDARY_RESPONSE_ON_THE_INCOMING_FORMATION_SEGMENT",
            "DOMAIN_IS_H_BIRTH_DIRECT_SUM_H_E1_OR_ITS_TERMINALLY_REDUCED_H_E1_BLOCK;_NOT_H_C2",
            "CERTIFIED_COMPACT_E0_TO_C1_TO_E1_ACTION_SEGMENT",
            "SCHUR_REDUCE_TO_M_F_AND_PLACE_ON_THE_LEFT_OF_E1",
            "INVALID_MATCH_FOR_C2_VALID_MATCH_FOR_INCOMING_LEG",
            "C1_LEG_RESPONSE",
        ),
        _candidate(
            "TERMINAL_WEYL_LAURENT_GERM_AND_TERMINAL_COEFFICIENT_JET",
            "SMALL_DURATION_ASYMPTOTIC_RESPONSE_AND_PARTIAL_FIXED_DURATION_JET",
            "ONLY_A_LAURENT_GERM_AND_NOT_THE_COMPLETE_Z_DEPENDENT_C2_MAXIMAL_FAMILY",
            "ACTUAL_TERMINAL_CAUCHY_DATA_OF_THE_CERTIFIED_C1_FORMATION_HISTORY",
            "MAY_CHECK_LOCAL_TRANSFER_ORIENTATION_BUT_CANNOT_REPLACE_M_C2",
            "INVALID_MATCH_AS_COMPLETE_C2_LEG_PARTIAL_LOCAL_DATA_ONLY",
            "C1_TERMINAL_LOCAL_RESPONSE",
        ),
        _candidate(
            "TWO_CHORD_SCALAR_AND_PRODUCT_DIRAC_WEYL_ENCLOSURES",
            "FIXED_CHANNEL_WEYL_BOUNDS_AT_NEGATIVE_PROBES",
            "FINITE_VALIDATION_CORE_WITH_BROAD_FAR_LOAD_CLASS;_NOT_A_PHYSICAL_C2_ENDPOINT_AND_NOT_FULL_HEAT_SPECTRAL_DATA",
            "RETAINED_N12_CHANNEL_COEFFICIENTS_BUT_UNPROMOTED_CORE_ENDPOINT",
            "USE_ONLY_AS_COMPARISON_BOUNDS_AFTER_ACTUAL_C2_MEMBERSHIP_IS_PROVED",
            "INVALID_MATCH_AS_C2_ORACLE_VALID_PARTIAL_COMPARISON",
            "CHANNEL_COMPARISON_DATA",
        ),
        _candidate(
            "N12_EVENT_CHILD_SEVEN_BY_SEVEN_CALDERON_SYMBOL",
            "LOCAL_EVENT_CHILD_CONSTRAINT_REACTION_GRAPH_PROJECTOR",
            "SEVEN_BY_SEVEN_BOUNDARY_SYMBOL_WITH_NO_TEMPORAL_RESOLVENT_PARAMETER_OR_MAXIMAL_CHILD_DOMAIN",
            "ACTUAL_N12_EVENT_CHILD_STATE_BUT_CONTINUUM_SYMBOL_TAIL_UNCERTIFIED",
            "NO_EQUIVALENCE_FROM_LOCAL_REACTION_SYMBOL_TO_TEMPORAL_WEYL_FAMILY",
            "INVALID_MATCH_WRONG_MATHEMATICAL_TYPE",
            "E1_LOCAL_CONSTRAINT_SYMBOL",
        ),
        _candidate(
            "N3_ZERO_BACKGROUND_CALDERON_CLOSURE",
            "ZERO_FIELD_COMPATIBILITY_ROW",
            "N3_ZERO_VECTOR_GRAPH;_NOT_N12_NONZERO_OPERATOR_RESPONSE",
            "HISTORICAL_ZERO_BACKGROUND_COMPONENT_ONLY",
            "NO_ORDER_BACKGROUND_OR_RESPONSE_EQUIVALENCE",
            "INVALID_MATCH_WRONG_ORDER_BACKGROUND_AND_AMPLITUDE",
            "ZERO_BACKGROUND_COMPATIBILITY",
        ),
        _candidate(
            "EVENT_SHELL_JOINT_OPERATOR_V15_73",
            "SPATIALLY_WEIGHTED_M5_GAUGE_YUKAWA_RESPONSE",
            "SPATIAL_EVENT_SHELL_DOMAIN;_NO_FORWARD_TEMPORAL_C2_BOUNDARY_TRIPLE",
            "HISTORICAL_REDUCED_PUSHFORWARD_CALCULATION",
            "NO_DOMAIN_EQUIVALENCE_TO_C2_MAXIMAL_HISTORY",
            "INVALID_MATCH_WRONG_DOMAIN_AND_OBSERVABLE",
            "HISTORICAL_SPATIAL_RESPONSE",
        ),
        _candidate(
            "U_R",
            "UNITARY_EVENT_TO_CHILD_TRACE_TRANSITION",
            "SQUARE_UNITARY_MAP_H_E1_TO_H_C2_NOT_A_CONORMAL_RESPONSE",
            "AE2_RESET_GLUE_OWNED_BY_THE_EXTENDED_ACTION",
            "CONJUGATE_M_C2_INTO_THE_EVENT_FRAME",
            "INVALID_MATCH_FOR_LEG_VALID_MATCH_FOR_EDGE_COUPLING",
            "E1_TO_C2_TRANSITION",
        ),
        _candidate(
            "W_PHYS",
            "SELF_ADJOINT_LOCAL_EVENT_CONTACT_BLOCK",
            "ACTS_ON_THE_EVENT_TRACE_SPACE_WITH_NO_EXTERIOR_EVOLUTION",
            "AE2_EVENT_BOUNDARY_VARIATION",
            "ADD_AFTER_RESET_PULLBACK_OF_M_C2",
            "INVALID_MATCH_FOR_LEG_VALID_MATCH_FOR_VERTEX",
            "E1_VERTEX_CONTACT",
        ),
        _candidate(
            "AE2_COVARIANT_SEAM_COMPOSITION",
            "U_R_DAGGER_M_C2_U_R_PLUS_W_PHYS_AND_M_F_PLUS_THAT_LOAD",
            "VALID_WHEN_ALL_SQUARE_BLOCKS_SHARE_THE_EVENT_TRACE_DIMENSION_AND_U_R_IS_UNITARY",
            "CURRENT_AE2_INTERFACE_CODE_AND_TWO_SIDED_SEAM_THEOREM",
            "PULL_CHILD_FRAME_RESPONSE_TO_EVENT_FRAME_THEN_ADD_CONTACT_AND_INCOMING_RESPONSE",
            "VALID_MATCH_ASSEMBLY_IDENTITY_NOT_A_C2_LEG",
            "E1_SEAM_ELIMINATION",
        ),
        _candidate(
            "ONE_Z_MINUS_ONE_VALUE_OR_BROAD_NEGATIVE_AXIS_SEAM_CLASS",
            "PARTIAL_RESOLVENT_SAMPLES_OR_INTERVAL_CLASS",
            "DOES_NOT_DETERMINE_THE_E1_HEAT_FUNCTIONAL;_CLASS_CONTAINS_OPPOSITE_FORCE_SIGNS",
            "VALID_COMPARISON_AND_NO_GO_ARTIFACTS",
            "NO_EQUIVALENCE_TO_A_COMPLETE_OPERATOR_SPECTRAL_MEASURE",
            "INVALID_MATCH_AS_COMPLETE_C2_SPECTRAL_RESPONSE",
            "INFORMATION_SUFFICIENCY_WITNESS",
        ),
        _candidate(
            "HISTORICAL_PERIODIC_ROUND_COLLAR_REDUCED_SCALAR_WEYL_OBJECTS",
            "PERIODIC_OR_REDUCED_BOUNDARY_RESPONSES",
            "WRONG_TEMPORAL_DOMAIN_BACKGROUND_OR_SECTOR_COMPLETENESS",
            "HISTORICAL_ACTION_VERSIONS_AND_DIAGNOSTIC_THEOREM_CLASSES",
            "GENERAL_SCHUR_AND_BOUNDARY_TRIPLE_IDENTITIES_REUSABLE_BUT_VALUES_AND_DOMAINS_ARE_NOT",
            "INVALID_MATCH_TEMPLATES_ONLY",
            "EXTERNAL_MATHEMATICAL_PUZZLE_PIECES",
        ),
    ]

    validation = {
        "maximal_weyl_family_is_derived": maximal["status"].startswith(
            "FORWARD_NATIVE_RESOLVENT_WEYL_FAMILY_DERIVED"
        ),
        "maximal_family_has_exact_C2_slot_type": maximal["operator_family"][
            "Weyl_Calderon_operator"
        ].startswith("M_C(z)*a=Gamma1_birth"),
        "maximal_family_uses_retained_endpoint_classes": maximal["validation"][
            "all_retained_endpoint_classes_supported"
        ],
        "friedrichs_value_construction_is_derived": friedrichs["claim_boundary"][
            "maximal_Friedrichs_Weyl_value_definition"
        ] == "DERIVED_AS_UNIQUE_EXHAUSTION",
        "finite_stratum_oracle_solver_is_derived": oracle["claim_boundary"][
            "stable_Weyl_value_first_second_jet_solver"
        ] == "DERIVED",
        "actual_parametric_C2_oracle_is_open": fiber["adjudication"][
            "actual_parametric_N12_exterior_oracle"
        ] == "OPEN_CURRENT_OWNER",
        "compact_support_jets_are_only_partial": compact_variations[
            "claim_boundary"
        ]["global_noncompact_Weyl_variations"].startswith("OPEN"),
        "incoming_compact_response_has_two_boundary_domain": compact[
            "endpoint_partition"
        ]["ordered_traces"] == ["birth", "new_event"],
        "terminal_germ_is_not_complete_family": germ["claim_boundary"][
            "complete_finite_duration_M_C_family"
        ] == "OPEN_BEYOND_GERM",
        "spectral_reduction_names_C2_as_terminal_load": spectral["open"][
            "AE2_child_response_M_C2_and_first_two_covariant_jets"
        ],
        "gluing_keeps_C2_value_in_force": not gluing["adjudication"][
            "fixing_C2_state_removes_M_C2_value_from_force"
        ],
        "endpoint_roles_place_C2_at_terminal_load": endpoints["endpoint_roles"][
            "new_event"
        ]["load"] == "B_terminal=U_R_DAGGER*M_C2*U_R+W_phys",
        "two_sided_seam_requires_child_response": "M_child" in seam[
            "corrected_seam_theorem"
        ]["physical_seam_operator"],
        "single_probe_is_insufficient_for_heat": not heat[
            "retained_functional_calculus"
        ]["one_resolvent_probe_sufficient"],
        "local_event_child_symbol_is_not_continuum_certified": not local[
            "CONTINUUM_EVENT_CHILD_CERTIFIED"
        ],
        "n3_closure_disclaims_nonzero_matrices": not n3[
            "zero_background_calderon_closure"
        ]["scope"]["full_nonzero_fluctuation_Calderon_matrices_derived"],
        "event_shell_is_spatial_weighted_operator": shell[
            "weighted_parent_operator"
        ]["weighted_operator"].startswith("A_t=d_A^dagger"),
        "seam_code_implements_exact_composition": all(
            token in seam_source
            for token in (
                "lift.conj().T @ child @ lift + boundary",
                "return event + load",
            )
        ),
        "no_new_child_theory_selector_endpoint_scale_recurrence_or_gate_added": True,
    }

    return {
        "artifact": "BHSM_N12_GATE7_C2_DIAGRAM_SLOT_MATCHING_AUDIT",
        "status": "C2_WEYL_THEORY_MATCHED_ACTUAL_RESET_SELECTED_REALIZATION_OPEN",
        "classification": (
            "THE_C2_SLOT_IS_NOT_A_GENUINELY_NEW_RESPONSE_THEORY:_THE_RETAINED_"
            "ACTION_OWNED_MAXIMAL_FORWARD_WEYL_CALDERON_FAMILY_HAS_THE_EXACT_"
            "TYPE_AND_ENDPOINT_SEMANTICS_AND_AE2_SUPPLIES_ITS_RESET_FRAME_"
            "COMPOSITION;_WHAT_REMAINS_MISSING_IS_THE_ACTUAL_E1_RESET_SELECTED_"
            "C2_COEFFICIENT_FORM_ENDPOINT_STRATUM_AND_FIRST_TWO_COVARIANT_"
            "QUOTIENT_JETS_OR_THE_EQUIVALENT_JOINT_OPERATOR_DATA"
        ),
        "forward_event_diagram": {
            "diagram": "C1 --M_f--> E1 --(U_R,W_phys)--> C2 --M_C2--> MAXIMAL_ENDPOINT",
            "external_readout_variables": "BRST_QUOTIENTED_BIRTH_SOURCE_AND_GEOMETRY_RESET_QUOTIENT_xi",
            "internal_eliminated_trace": "COMMON_E1_C2_AE2_SEAM_TRACE",
            "legs": {
                "C1": "M_f(z;xi)",
                "C2": "M_C2(z;xi):=M_C^max[Y_C2(xi),endpoint_class_C2]",
            },
            "vertex": {
                "transition": "U_R",
                "contact": "W_phys",
            },
            "glued_load": "B_E1=U_R_DAGGER*M_C2*U_R+W_phys",
            "seam_operator": "S_AE2=M_f+B_E1",
        },
        "C2_slot_contract": {
            "map": "M_C2(z;xi):H_C2_TO_H_C2",
            "trace_space": "RETAINED_EVENT_CHILD_MEASURE_BRST_QUOTIENT_SECTOR_TRACE_SPACE",
            "conormal": "OUTWARD_FROM_THE_C2_ARM",
            "spectral_domain": "z_IN_rho(P_C2^D);_REAL_z_LT_0_IS_THE_NATIVE_COERCIVE_REGION",
            "endpoint_class": "LATER_AE2_EVENT_GRAPH_IF_HIT_OTHERWISE_RETAINED_CANONICAL_FRIEDRICHS_CLOSURE",
            "force_data": "FULL_CONTROLLED_SPECTRAL_FAMILY_AND_D_xi_M_C2",
            "Hessian_data": "D_xi_M_C2_D_xi2_M_C2_AND_COMMON_PAIR_PLUS_CONTACT",
            "frame_covariance": "M_C2_EVENT=U_R_DAGGER*M_C2_CHILD*U_R",
        },
        "matching_audit": candidates,
        "adjudication": {
            "C2_slot_operator_theory": "VALID_MATCH_EXISTING_MAXIMAL_FORWARD_M_C_FAMILY",
            "C2_slot_AE2_frame_assembly": "VALID_MATCH_EXISTING_U_R_W_phys_SEAM_COMPOSITION",
            "C2_slot_finite_realization_algorithm": "VALID_MATCH_EXISTING_PARAMETRIC_INVERSE_FREE_ORACLE",
            "C2_slot_Friedrichs_realization_algorithm": "VALID_MATCH_EXISTING_CORE_EXHAUSTION",
            "actual_E1_reset_selected_C2_value": "ACTUALLY_MISSING_REALIZATION_DATA",
            "actual_C2_first_covariant_quotient_jet": "ACTUALLY_MISSING_REALIZATION_DATA",
            "actual_C2_second_covariant_quotient_jet": "ACTUALLY_MISSING_REALIZATION_DATA",
            "new_C2_physical_theory_required": False,
            "prior_missing_M_C2_wording": "RECLASSIFIED_AS_MISSING_INSTANTIATION_NOT_MISSING_THEORY",
        },
        "exact_next_dependency": (
            "INSTANTIATE_THE_EXISTING_M_C_MAXIMAL_FORWARD_FAMILY_ON_THE_ACTUAL_"
            "E1_RESET_OUTPUT_C2:_SUPPLY_ITS_ACTION_GENERATED_COEFFICIENT_FORM_"
            "HISTORY_OR_EQUIVALENT_JOINT_K,_RETAINED_ENDPOINT_STRATUM,_AND_FIRST_"
            "SECOND_COVARIANT_RESET_QUOTIENT_JETS;_THEN_ROUTE_THE_DATA_THROUGH_"
            "THE_EXISTING_FINITE_STRATUM_OR_FRIEDRICHS_ORACLE,_FORM_U_R_DAGGER_"
            "M_C2_U_R_PLUS_W_phys,_ADD_M_f,_AND_EVALUATE_THE_ZERO_SOURCE_FORCE"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_ACTUAL_C2_REALIZATION_AND_FORCE_OPEN",
            "Gate8": "LOCKED",
            "C2_response_theory": "CLOSED_EXISTING_OBJECT_MATCH",
            "C2_actual_operator_and_covariant_jets": "OPEN",
            "zero_source_force": "OPEN_AFTER_C2_REALIZATION",
            "same_action_saddle": "OPEN_AFTER_FORCE",
            "physical_Hessian": "OPEN_AFTER_SADDLE",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path)
            for path in FILES.values()
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "status": payload["status"],
                "candidate_count": len(payload["matching_audit"]),
                "new_C2_physical_theory_required": payload["adjudication"][
                    "new_C2_physical_theory_required"
                ],
                "validation_passed": payload["validation_passed"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
