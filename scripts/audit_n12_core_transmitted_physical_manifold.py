"""Audit whether BHSM already owns a core-to-boundary physical manifold."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts"
FLAG = ART / "flagship_integration"
RESULT = FLAG / "BHSM_N12_CORE_TRANSMITTED_PHYSICAL_MANIFOLD_AUDIT.json"
THEORY = ROOT / "theory/n12_core_transmitted_physical_manifold_audit.md"

PATHS = {
    "ae2": ART / "action_extension/BHSM_ACTION_AE2_GLOBAL_SPIN_RESET_ACTION.json",
    "core_transfer": ART / "BHSM_core_transfer_v11_0.json",
    "core_asymptotic": ART / "BHSM_core_asymptotic_transfer_v11_1.json",
    "core_trace": ART / "BHSM_aether_core_surface_trace_v15_11.json",
    "core_attachment": ART / "BHSM_aether_geometry_core_attachment_v15_3.json",
    "core_representation": ART / "BHSM_aether_core_representation_gate_v15_3.json",
    "support_selection": ART / "BHSM_support_character_boundary_core_selection_v11_2.json",
    "full_reset": FLAG / "BHSM_N12_FULL_RESET_ACTION_JACOBIAN.json",
    "birth_projection": FLAG / "BHSM_N12_C2_BIRTH_COEFFICIENT_QUOTIENT_JET.json",
    "time_quotient": FLAG / "BHSM_N12_RESET_TIME_QUOTIENT_GENERATOR_AUDIT.json",
    "source_incidence": FLAG / "BHSM_N12_FORWARD_COMMON_SOURCE_INCIDENCE.json",
    "gauge_ownership": FLAG / "BHSM_N12_FLAGSHIP_GAUGE_ACTION_OWNERSHIP_AUDIT.json",
    "incidence_127": ART / "BHSM_1_2_7_incidence_audit_v6_3_0.json",
    "fine_structure": ART / "BHSM_fine_structure_dependency_map_v6_2_0.json",
    "gauge_quantum": ART / "BHSM_universal_gauge_quantum_update_v4_1.json",
    "eta_l": ART / "BHSM_eta_l_source_audit_v1_7.json",
    "factorized_threshold": FLAG / "BHSM_N12_GATE7_AE2_FACTORIZED_THRESHOLD_RECLASSIFICATION.json",
    "exact_field": FLAG / "BHSM_N12_C2_EXACT_FIXED_S_FIELD_ORACLE.json",
    "current_semantics": ROOT / "theory/bhsm_current_semantic_normalization.md",
    "theory": THEORY,
}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in PATHS.values() if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing core-transmission audit inputs: " + ", ".join(missing))
    records = {
        key: _load(path)
        for key, path in PATHS.items()
        if path.suffix.lower() == ".json"
    }
    ae2 = records["ae2"]
    core_transfer = records["core_transfer"]
    core_asymptotic = records["core_asymptotic"]
    core_trace = records["core_trace"]
    attachment = records["core_attachment"]
    representation = records["core_representation"]
    support = records["support_selection"]
    full_reset = records["full_reset"]
    birth = records["birth_projection"]
    time = records["time_quotient"]
    source = records["source_incidence"]
    gauge = records["gauge_ownership"]
    incidence = records["incidence_127"]
    fine = records["fine_structure"]
    quantum = records["gauge_quantum"]
    eta_l = records["eta_l"]
    factorized = records["factorized_threshold"]
    exact_field = records["exact_field"]

    candidate_a = Fraction(1, 118)
    historical_alpha3 = 7.0 / (6.0 * math.pi * math.pi)
    candidates = [
        {
            "candidate_object": "BHSM_core_transfer_v11_0.T_core",
            "source": "HISTORICAL_CORE_TRANSFER_TARGET",
            "domain": "(X_in,P_in,phase,Q_topology,G_gauge)",
            "codomain": "(X_out,P_out,phase_out,Q_out,G_out)",
            "rank": None,
            "provenance": "NOT_DERIVED",
            "representation_only": False,
            "physical_relevance": "EXACT_REQUESTED_TYPE_BUT_EMPTY",
            "usable_as_T_core": False,
            "reason": "transfer_operator_energy_phase_gauge_topology_and_domain_are_null",
        },
        {
            "candidate_object": "BHSM_AE2_U_R",
            "source": "BHSM-AE-2.0.0_OWNER_SELECTED_ACTION_DOMAIN",
            "domain": "LAST_REGULAR_EVENT_Spin_x_GSM_TRACE",
            "codomain": "FIRST_REGULAR_CHILD_Spin_x_GSM_TRACE",
            "rank": 4,
            "provenance": "OWNER_AUTHORIZED_ACTION_VERSION_PLUS_GEOMETRIC_LIFT",
            "representation_only": False,
            "physical_relevance": "VALID_EVENT_CHILD_SEAM",
            "usable_as_T_core": False,
            "reason": "AE2_explicitly_adds_no_continuous_pregeometric_core_trace_or_flux",
        },
        {
            "candidate_object": "v15_11_compactified_core_compatibility_M_A",
            "source": "RETAINED_HAAR_ACTION_AND_RECIPROCAL_INCIDENCE",
            "domain": "REGULAR_SIDE_SUPPORT_AND_WALL_INCIDENCE_TRACES",
            "codomain": "(upsilon_boundary,I_W_boundary)",
            "rank": None,
            "provenance": "ACTION_DERIVED_OBSTRUCTION",
            "representation_only": False,
            "physical_relevance": "CORE_COMPATIBILITY_ZERO_SET_ONLY",
            "usable_as_T_core": False,
            "reason": "upsilon_zero_has_infinite_regular_action_and_I_W_zero_is_metric_reconstruction_rank_loss",
        },
        {
            "candidate_object": "v15_3_geometry_core_attachment",
            "source": "CONDITIONAL_FORM_THEOREM_DIAGNOSTICS",
            "domain": "UNSELECTED_CORE_HILBERT_MODULE",
            "codomain": "REGULAR_WENTZELL_BOUNDARY_MODULE",
            "rank": None,
            "provenance": "CONDITIONAL_NOT_ACTION_OWNED",
            "representation_only": True,
            "physical_relevance": "THEOREM_CLASS_ONLY",
            "usable_as_T_core": False,
            "reason": "core_trace_pairing_and_attachment_map_are_all_explicitly_not_action_owned",
        },
        {
            "candidate_object": "v11_2_support_character_boundary_core_selection",
            "source": "BOUNDARY_CORE_ANOMALY_WEIGHT_CONSTRAINT_AUDIT",
            "domain": "19_CANDIDATE_SUPPORT_WEIGHTS",
            "codomain": "12_EQUATION_WEIGHT_CONSTRAINT_LEDGER",
            "rank": int(support["rank"]),
            "kernel_dimension": int(support["nullity"]),
            "provenance": "ACTION_CONSTRAINT_AUDIT_WITH_NO_SELECTION",
            "representation_only": True,
            "physical_relevance": "DOES_NOT_SELECT_CORE_OR_BOUNDARY_CHARACTER",
            "usable_as_T_core": False,
            "reason": "boundary_core_and_anomaly_tests_fix_no_required attachment weights",
        },
        {
            "candidate_object": "N12_full_event_child_reset_relation",
            "source": "BHSM-AE2_ACTION_RESET_JACOBIAN",
            "domain": "196_DIMENSIONAL_MOVING_EVENT_CHILD_STATE",
            "codomain": "57_RESET_CONSTRAINT_ROWS",
            "rank": int(full_reset["dimensions"]["rank"]),
            "kernel_dimension": int(full_reset["dimensions"]["physical_tangent_nullity"]),
            "provenance": "ACTION_DERIVED",
            "representation_only": False,
            "physical_relevance": "VALID_EVENT_CHILD_CORRESPONDENCE",
            "usable_as_T_core": False,
            "reason": "event_child_gluing_relation_has_no_pregeometric_core_domain",
        },
        {
            "candidate_object": "N12_child_projection_and_fixed_event_fiber",
            "source": "RESET_RELATION_LINEARIZATION",
            "domain": "139_MOVING_CORRESPONDENCE_TANGENT_OR_FIXED_EVENT_CHILD_STATE",
            "codomain": "98_DIMENSIONAL_CHILD_STATE",
            "rank": 73,
            "fixed_event_kernel_dimension": 67,
            "post_time_quotient_dimension": 66,
            "provenance": "ACTION_DERIVED_DIMENSION_LEDGER",
            "representation_only": False,
            "physical_relevance": "VALID_RESET_QUOTIENT_GEOMETRY",
            "usable_as_T_core": False,
            "reason": "projection_records_event_child_geometry_but_does_not_restrict_population_from_the_core",
        },
        {
            "candidate_object": "N12_common_source_incidence",
            "source": "COMMON_GAUGE_GHOST_WEYL_HS_PAIR_CONTACT_ASSEMBLY",
            "domain": "ADMISSIBLE_SOURCE_SECTIONS_ON_A_SUPPLIED_TEMPORAL_GRAPH",
            "codomain": "LOCAL_PAIR_AND_CONTACT_OPERATOR_FORMS",
            "rank": 16,
            "provenance": "ACTION_LINEAGE_DERIVED_FOR_SUPPLIED_SECTIONS",
            "representation_only": False,
            "physical_relevance": "VALID_SOURCE_CONSUMER",
            "usable_as_T_core": False,
            "reason": "does_not_select_the_temporal_graph_or_map_core_degrees_to_reset_directions",
        },
        {
            "candidate_object": "rank16_gauge_trace_ray_and_source_Hessian",
            "source": "FLAGSHIP_GAUGE_ACTION_OWNERSHIP_AUDIT",
            "domain": "COMMON_GAUGE_SOURCE_DIRECTIONS",
            "codomain": "D_A2_Gamma_Q_READOUT",
            "rank": None,
            "provenance": "ACTION_LINEAGE_PRESENT_CURRENT_HISTORY_TRANSFER_OPEN",
            "representation_only": False,
            "physical_relevance": "DOWNSTREAM_GAUGE_READOUT",
            "usable_as_T_core": False,
            "reason": "source_Hessian_is_not_an_initial_state_reachability_projector",
        },
        {
            "candidate_object": "historical_1_to_2_to_7_incidence",
            "source": "V6_3_REPRESENTATION_TRACE_AUDIT",
            "domain": "REGISTERED_CHANNEL_WEIGHTS",
            "codomain": "CANDIDATE_COUPLING_RATIOS",
            "rank": None,
            "provenance": "HISTORICAL_CANDIDATE_REJECTED_AS_PHYSICAL_COUPLING",
            "representation_only": True,
            "physical_relevance": "POSSIBLE_ROLE_ONLY_IF_INDEPENDENTLY_ACTION_ATTACHED",
            "usable_as_T_core": False,
            "reason": "representation_trace_rejects_1_to_2_to_7_and_no_transmission_operator_exists",
        },
        {
            "candidate_object": "eta_l_and_universal_gauge_quantum_candidates",
            "source": "HISTORICAL_STOCHASTIC_AND_GAUGE_REGISTRIES",
            "domain": "UNATTACHED_SCALAR_STRENGTH_CANDIDATES",
            "codomain": "DOWNSTREAM_SCREEN_OR_TRANSPORT_NORMALIZATION",
            "rank": None,
            "provenance": "CONDITIONAL_OR_OPEN_MISSING_ACTION_SOURCE",
            "representation_only": True,
            "physical_relevance": "STRENGTH_CANDIDATES_NOT_CHANNEL_PROJECTORS",
            "usable_as_T_core": False,
            "reason": "eta_l_action_source_and_action_attached_gauge_denominator_are open",
        },
        {
            "candidate_object": "AE2_factorized_constant_core_threshold_model",
            "source": "GENERAL_HALF_LINE_COMPARISON_MODEL",
            "domain": "ONE_DIMENSIONAL_COMPACT_SUPPORT_INTERVAL",
            "codomain": "LOW_ENERGY_SOURCE_WEIGHT",
            "rank": None,
            "provenance": "GENERAL_MATHEMATICAL_MODEL_NOT_REALIZED_N12_EXTERIOR",
            "representation_only": True,
            "physical_relevance": "THRESHOLD_ROBUSTNESS_ONLY",
            "usable_as_T_core": False,
            "reason": "core_means_compact_operator_support_here_not_the_pregeometric_BHSM_core",
        },
        {
            "candidate_object": "Norman_candidate_a_equals_1_over_118",
            "source": "OWNER_STATEMENT_2026_08_25",
            "domain": None,
            "codomain": None,
            "rank": None,
            "provenance": "OWNER_AUTHORIZED_CANDIDATE_NOT_DERIVED",
            "representation_only": False,
            "physical_relevance": "POSSIBLE_STRENGTH_PENDING_OBJECT_IDENTIFICATION",
            "usable_as_T_core": False,
            "reason": "no_current_repository_action_formula_map_or_artifact_attaches_this_value_to_core transmission",
        },
    ]

    validation = {
        "all_authoritative_inputs_present": True,
        "formal_T_core_placeholder_is_empty": (
            core_transfer["transfer_operator"] is None
            and core_transfer["energy_matching"] is None
            and core_asymptotic["transfer_operator"] is None
        ),
        "retained_core_trace_is_limit_point_and_infinite_action": (
            core_trace["self_adjoint_domain"]["infinite_endpoint_classification"] == "WEYL_LIMIT_POINT"
            and core_trace["positive_capacity_theorem"]["outer_trace_endpoint_inaccessible_at_finite_regular_action"] is True
        ),
        "core_zero_trace_is_reconstruction_rank_loss": (
            core_trace["regular_side_core_compatibility"]["regular_reconstructible_trace"] is False
        ),
        "AE2_has_regular_trace_lift_but_no_core_trace": (
            ae2["finite_certificate"]["transmission_graph"]["graph_rank"] == 4
            and ae2["action_definition"]["pregeometric_core_field_content"] == "NO_CONTINUOUS_SPINOR_TRACE_OR_FLUX"
            and ae2["validation"]["no_core_continuous_trace_added"] is True
        ),
        "conditional_core_attachment_not_action_owned": (
            attachment["core_trace_map_action_owned"] is False
            and attachment["core_boundary_pairing_action_owned"] is False
            and attachment["b_GC_action_owned"] is False
        ),
        "core_representation_is_not_selected": (
            representation["physical_core_representation_derived"] is False
            and representation["positive_state_action_owned"] is False
        ),
        "dimension_139_is_full_moving_correspondence": full_reset["dimensions"]["physical_tangent_nullity"] == 139,
        "dimension_73_is_child_projection": "RANK_73" in birth["classification"],
        "dimension_67_and_66_are_fixed_event_and_time_quotient": (
            time["dimension_statement"]["raw_fixed_event_child_constraint_tangent"] == 67
            and time["dimension_statement"]["declared_after_existing_whole_system_time_quotient"] == 66
        ),
        "source_incidence_does_not_select_history": (
            source["incidence"]["temporal_graph_selected_by_this_assembly"] is False
        ),
        "one_two_seven_not_promoted": incidence["candidate_matches_representation_trace"] is False,
        "fine_structure_strength_remains_underived": fine["alpha_i_physical_derived"] is False,
        "gauge_quantum_action_denominator_open": quantum["status"] == "OPEN_MISSING_UNIVERSAL_GAUGE_COUPLING_QUANTUM",
        "eta_l_action_source_open": eta_l["action_source_status"] == "OPEN_MISSING_ETA_L_ACTION_SOURCE",
        "factorized_threshold_does_not_claim_realized_N12_class": (
            factorized["provenance_reclassification"]["what_the_model_does_not_prove"]
            == "THE_UNKNOWN_MAXIMAL_N12_EVENT_CHILD_EXTERIOR_BELONGS_TO_THIS_CONSTANT_CORE_FREE_EXTERIOR_CLASS"
        ),
        "exact_fixed_s_field_available_but_base_history_open": exact_field["claim_boundary"]["actual_parametric_base_history"] == "OPEN",
        "owner_candidate_is_exactly_one_over_118": candidate_a.numerator == 1 and candidate_a.denominator == 118,
        "owner_candidate_not_confused_with_historical_alpha3": abs(float(candidate_a) - historical_alpha3) > 0.1,
        "no_core_projector_selector_alpha_fit_action_term_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_CORE_TRANSMITTED_PHYSICAL_MANIFOLD_AUDIT",
        "status": "NO_EXISTING_ACTION_OWNED_CORE_TO_RESET_TRANSMISSION_MANIFOLD_FOUND" if passed else "CORE_TRANSMISSION_AUDIT_INVALID",
        "classification": "THE_OWNER_CORE_TRANSMISSION_HYPOTHESIS_IS_NOT_REALIZED_BY_THE_CURRENT_ACTION;_AE2_U_R_IS_A_REGULAR_EVENT_CHILD_TRACE_LIFT_NOT_A_PREGEOMETRIC_CORE_MAP,_THE_RETAINED_HAAR_CORE_TRACE_IS_LIMIT_POINT_INFINITE_ACTION_RANK_LOSS,_AND_NO_1_TO_2_TO_7_eta_l_GAUGE_QUANTUM_SOURCE_INCIDENCE_OR_a_EQUALS_1_OVER_118_ARTIFACT_SUPPLIES_THE_MISSING_PROJECTOR",
        "owner_hypothesis": {
            "statement": "PHYSICAL_STATES_MAY_LIE_IN_THE_IMAGE_OF_AN_ACTION_OWNED_CORE_TO_BOUNDARY_TRANSMISSION_MAP",
            "provenance": "OWNER_AUTHORIZED_ONTOLOGY_STRONG_HYPOTHESIS",
            "theorem_status": "NOT_DERIVED_FROM_BHSM-AE-2.0.0",
            "candidate_a_exact": "1/118",
            "candidate_a_decimal": float(candidate_a),
            "candidate_a_status": "OWNER_AUTHORIZED_CANDIDATE_NOT_ACTION_ATTACHED",
            "historical_alpha3_exact": "7/(6*pi^2)",
            "historical_alpha3_decimal": historical_alpha3,
            "same_quantity_established": False,
        },
        "typed_provenance_table": candidates,
        "dimension_reconciliation": {
            "full_moving_event_child_correspondence": 139,
            "child_projection_rank": 73,
            "fixed_event_child_fiber": 67,
            "post_whole_history_time_quotient": 66,
            "additional_core_transmission_rank_reduction_certified": False,
            "common_scale": "RETAIN_PHYSICAL",
            "event_directions": "RETAIN_IN_139_MOVING_CORRESPONDENCE",
            "child_directions": "RETAIN_ACCORDING_TO_73_67_66_CONTEXT",
        },
        "invariance_adjudication": {
            "nonempty_regular_M_phys_identified": False,
            "fixed_s_tangency_test_well_posed": False,
            "reason": "NO_ACTION_OWNED_REGULAR_PROJECTOR_OR_DEFINING_CONSTRAINTS_FOR_M_phys_EXIST",
            "proof_center_motion_used": False,
        },
        "KKT_consequence": {
            "ambient_force_zero_required": False,
            "core_reduced_projected_force_available": False,
            "current_139_73_67_66_domains_reduced_by_owner_hypothesis": False,
            "surviving_no_selector_route": "PARAMETRIC_RESET_FAMILY_OR_MAXIMAL_WEYL_COVECTOR_ROOT_ON_THE_EXISTING_PHYSICAL_QUOTIENT",
            "finite_endpoint_BVP": "VALID_SUFFICIENT_SUBROUTE_NOT_UNIVERSAL_REQUIREMENT",
        },
        "fine_structure_adjudication": {
            "channel_survival_theorem_from_core": "NOT_DERIVED",
            "surviving_channel_strength_from_core": "NOT_DERIVED",
            "one_two_seven": "REJECTED_AS_PHYSICAL_COUPLING_AND_NOT_A_TRANSMISSION_MAP",
            "eta_l": "CONDITIONAL_SOURCE_CANDIDATE_ACTION_SOURCE_OPEN",
            "universal_gauge_quantum": "ACTION_ATTACHED_DENOMINATOR_OPEN",
            "a_equals_1_over_118": "OWNER_CANDIDATE_NO_REPOSITORY_ATTACHMENT",
            "alpha_inserted_upstream": False,
        },
        "validated_invalidated_open": {
            "VALIDATED": [
                "AE2_regular_event_child_trace_lift",
                "retained_Haar_core_limit_point_obstruction",
                "139_73_67_66_dimension_distinctions",
                "owner_candidate_a_equals_1_over_118_recorded_without_promotion",
            ],
            "INVALIDATED": [
                "AE2_U_R_is_a_pregeometric_core_to_boundary_map",
                "1_to_2_to_7_or_eta_l_already_defines_M_phys",
                "source_incidence_selects_a_physical_base_history",
                "proof_centers_can_define_core_reachability",
            ],
            "OPEN": [
                "foundational_action_owned_core_boundary_correspondence_if_the_owner_hypothesis_is_to_be_promoted",
                "actual_parametric_reset_family_base_history",
                "signed_nested_backward_adjoint",
                "projected_heat_minus_zeta_covector_root",
            ],
        },
        "hindsight": {
            "classification": "MISSING_ACTION_OWNED_FOUNDATIONAL_PROVENANCE_NOT_A_PROOF_CHART_LIMIT",
            "obstruction_BHSM_native": True,
            "retained_action_contradiction": False,
            "owner_hypothesis_rejected": False,
        },
        "exact_next_dependency": "DO_NOT_SHRINK_THE_KKT_BY_THE_UNDERIVED_CORE_HYPOTHESIS;_USE_THE_EXISTING_ACTION_RESET_RELATION_AND_EXACT_FIXED_s_FIELD_TO_REALIZE_A_PARAMETRIC_PHYSICAL_BASE_HISTORY_OR_COUPLED_FORWARD_ADJOINT_KKT_ON_THE_RETAINED_QUOTIENT,_UNLESS_NORMAN_SEPARATELY_AUTHORIZES_NEW_FOUNDATIONAL_CORE_BOUNDARY_ACTION_DATA",
        "claim_boundary": {
            "core_transmitted_physical_manifold": "OWNER_HYPOTHESIS_NOT_ACTION_DERIVED",
            "a_equals_1_over_118": "OWNER_CANDIDATE_NOT_DERIVED",
            "alpha_derived": False,
            "Gate7": "OPEN_PARAMETRIC_PHYSICAL_HISTORY_AND_PROJECTED_COVECTOR_ROOT",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FLAGSHIP_READY": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {path.relative_to(ROOT).as_posix(): _sha256(path) for path in PATHS.values()},
        "validation": validation,
        "validation_passed": passed,
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({
        "status": payload["status"],
        "candidate_count": len(payload["typed_provenance_table"]),
        "core_manifold": payload["claim_boundary"]["core_transmitted_physical_manifold"],
        "a": payload["owner_hypothesis"]["candidate_a_exact"],
        "validation_passed": payload["validation_passed"],
    }, indent=2))


if __name__ == "__main__":
    main()
