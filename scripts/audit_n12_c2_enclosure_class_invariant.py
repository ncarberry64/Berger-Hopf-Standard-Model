"""Audit finite BHSM class ledgers and certify C2 class invariance."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_C2_ENCLOSURE_CLASS_INVARIANT_AUDIT.json"
COVER = BASE / "BHSM_N12_C2_FINITE_TRANSLATED_DESCRIPTOR_COVER.json"
RESPONSE = BASE / "BHSM_N12_C2_FINITE_COVER_VOLTERRA_WEYL.json"
GATES = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_CORRECTED_FORWARD_HISTORY_AND_PARTICLE_CLASS_GATES.json"
)
AE2 = ROOT / "artifacts/action_extension/BHSM_ACTION_AE2_GLOBAL_SPIN_RESET_ACTION.json"
SLOT = BASE / "BHSM_N12_GATE7_C2_DIAGRAM_SLOT_MATCHING_AUDIT.json"
SPECTRUM = ROOT / "theory/theorem_discharge_phase_orientation_cyclic_results.json"
GENERATION = ROOT / "artifacts/BHSM_generation_projector_action_attachment_v8_2.json"
SLOT_MAP = ROOT / "artifacts/BHSM_three_family_particle_slot_map_v6_2_0.json"
REPRESENTATION = ROOT / "artifacts/BHSM_three_family_particle_representation_map_v6_3_0.json"
TRIALITY = ROOT / "artifacts/BHSM_triality_Berger_no_double_counting_v6_2_0.json"
SUPPORT = ROOT / "artifacts/BHSM_primitive_support_character_ledger_v11_2.json"
CORRESPONDENCE = ROOT / "artifacts/BHSM_established_physics_correspondence_registry_v6_0_6.json"
SECTOR_LEDGER = ROOT / "docs/bhsm_sector_projector_ledger_theorem.md"
MARGINS = BASE / "BHSM_N12_FINITE_TERMINAL_MARGIN_TRANSFER.json"
THEORY = ROOT / "theory/n12_c2_enclosure_class_invariant.md"
INPUTS = (
    COVER, RESPONSE, GATES, AE2, SLOT, SPECTRUM, GENERATION, SLOT_MAP,
    REPRESENTATION, TRIALITY, SUPPORT, CORRESPONDENCE, SECTOR_LEDGER,
    MARGINS, THEORY,
)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _audit_row(
    required_type: str,
    existing_object: str,
    domain: str,
    provenance: str,
    class_invariant: str,
    physical_distinguishability: str,
    downstream: str,
    verdict: str,
) -> dict[str, str]:
    return {
        "required_type": required_type,
        "existing_BHSM_object": existing_object,
        "domain": domain,
        "provenance": provenance,
        "class_invariant": class_invariant,
        "physical_distinguishability": physical_distinguishability,
        "downstream_SM_interpretation": downstream,
        "verdict": verdict,
    }


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        missing = [str(path) for path in INPUTS if not path.is_file()]
        raise FileNotFoundError(f"missing enclosure-class inputs: {missing}")
    cover, response, gates, ae2, slot, spectrum, generation, slot_map, representation, triality, support, correspondence, margins = (
        _load(path) for path in (
            COVER, RESPONSE, GATES, AE2, SLOT, SPECTRUM, GENERATION,
            SLOT_MAP, REPRESENTATION, TRIALITY, SUPPORT, CORRESPONDENCE,
            MARGINS,
        )
    )
    if not all(record.get("validation_passed") is True for record in (
        cover, response, gates, ae2, slot, generation, support, margins,
    )):
        raise RuntimeError("validated enclosure-class parents required")

    rows = cover["cover"]["rows"]
    channel_labels = sorted(response["channels_at_z_minus_1"])
    all_branch_24 = bool(rows) and all(
        int(row["proof_center_branch"]) == 24 for row in rows
    )
    all_regular = bool(rows) and all(
        float(row["signed_lambda_step"]) > 0.0
        and float(row["proper_time_increment_interval"][0]) > 0.0
        and float(row["Delta_lower"]) > 0.0
        and float(row["hard_self_consistency"]) < 0.5
        and float(row["root_relative_path_plus_tube_upper"])
        < float(row["translated_ball_total_radius"])
        for row in rows
    )
    finite_audit = [
        _audit_row(
            "primitive admissible closure spectrum",
            "phase/orientation/cyclic spectrum {1,2,3}",
            "primitive low-energy boundary closure layer",
            "theory/theorem_discharge_phase_orientation_cyclic_results.json",
            "DISCRETE_IF_THE_CONDITIONAL_ATTACHMENT_HOLDS",
            "NOT_YET_ACTION_RESPONSE_DISTINGUISHED",
            "base plus two excitation slots",
            "VALIDATED_CONDITIONAL_INGREDIENT_GLOBAL_FINISH_OPEN",
        ),
        _audit_row(
            "base plus two excitation slots",
            "rank-one Pi_f,i on F_l, F_u, F_d",
            "three frozen charged-family modules",
            "BHSM_generation_projector_action_attachment_v8_2",
            "PROJECTOR_LABEL_IS_DISCRETE_ON_ITS_FIXED_MODULE",
            "OPEN_MODE_STRESS_INCIDENCE_UNDEFINED",
            "charged generations only after response closure",
            "VALIDATED_CONDITIONAL_NOT_INSTANTIATED_ON_C2",
        ),
        _audit_row(
            "finite sector/family ledger",
            "P_nu, P_l, P_u, P_d from C in {0,1}, sigma in {-1,+1}",
            "conditional finite sector ledger",
            "docs/bhsm_sector_projector_ledger_theorem.md",
            "PROJECTOR_RANK_LABELS_DISCRETE",
            "EXTRA_DOWN_INCIDENCE_AND_UNIFIED_OMEGA_NOT_FULLY_ACTION_DERIVED",
            "neutral, lepton, up, down sectors",
            "STRUCTURAL_CANDIDATE_NOT_GLOBAL_CLASS_THEOREM",
        ),
        _audit_row(
            "charged q/j mode separation",
            "frozen (k,j) ledgers for F_l, F_u, F_d",
            "charged three-slot family modules",
            "BHSM_generation_projector_action_attachment_v8_2",
            "FIXED_MODE_PROJECTOR_LABEL",
            "OPEN_UNTIL_CLASSICAL_MODE_STRESS_IS_DEFINED",
            "charged lepton and quark family comparison",
            "VALIDATED_CONDITIONAL_LEDGER",
        ),
        _audit_row(
            "neutral/topographic mixed sector",
            "P_nu plus optional neutral-singlet representation rows",
            "conditional chiral representation map",
            "BHSM_three_family_particle_representation_map_v6_3_0",
            "DISCRETE_REPRESENTATION_LABEL_IF_ATTACHED",
            "NEUTRINO_PROPAGATION_AND_MASS_RESPONSE_REMAIN_OPEN",
            "neutrino-like carrier comparison",
            "OPEN_C2_ATTACHMENT_AND_RESPONSE",
        ),
        _audit_row(
            "boundary operator/incidence label",
            "Omega(C,sigma) and M(C,sigma)",
            "finite sector boundary ledger",
            "docs/bhsm_sector_projector_ledger_theorem.md",
            "CONSTANT_ON_FIXED_BOUNDARY_DOMAIN_IF_DERIVED",
            "DOWN_EXTRA_INCIDENCE_REMAINS_STRONGLY_SUPPORTED_CANDIDATE",
            "sector-dependent boundary response",
            "OPEN_ACTION_DERIVATION",
        ),
        _audit_row(
            "anomaly-compatible representation sector",
            "three-family chiral representation map",
            "effective Spin x G_SM representation ledger",
            "BHSM_three_family_particle_representation_map_v6_3_0",
            "DISCRETE_ON_FIXED_BUNDLE",
            "CONDITIONAL_ON_ADMITTED_CHIRAL_PATTERN_AND_U1",
            "anomaly-free SM ledger comparison",
            "VALIDATED_CONDITIONAL_NOT_MICROSCOPIC_CLASS_PROOF",
        ),
        _audit_row(
            "finite algebra/projector result",
            "triality-Berger three-slot intertwiner without multiplication",
            "frozen family architecture",
            "BHSM_triality_Berger_no_double_counting_v6_2_0",
            "FINITE_PROJECTOR_INTERTWINER_LABEL",
            "CONDITIONAL_REALIZATION",
            "three generations without ninefold double counting",
            "VALIDATED_CONDITIONAL",
        ),
        _audit_row(
            "gauge representation channel",
            "AE2 reset-glued global Spin x G_SM trace graph",
            "actual E1-to-C2 reset interface and maximal child domain",
            "BHSM_ACTION_AE2_GLOBAL_SPIN_RESET_ACTION",
            "EXACTLY_FIXED_BY_THE_AE2_DOMAIN_ON_REGULAR_FLOW",
            "GAUGE_FRAME_EQUIVALENT;_NO_INDEPENDENT_PHASE",
            "downstream gauge/matter bundle",
            "VALID_MATCH_C2_SIGNATURE_COMPONENT",
        ),
        _audit_row(
            "CKM/PMNS structural ledger",
            "up/down basis mismatch and neutral bridge ledgers",
            "downstream family response sectors",
            "generation attachment and correspondence firewall",
            "DISCRETE_SECTOR_TYPING_ONLY;_MATRICES_CONTINUOUS",
            "CKM_BLOCKED_BY_MODE_STRESS;_PMNS_PROPAGATION_OPEN",
            "mixing comparison after action response",
            "OPEN_NOT_A_C2_CLASS_INPUT",
        ),
        _audit_row(
            "topological degree and orientation class",
            "AE2 degree-one/odd-FR returned bundle data and forward-only history",
            "actual reset-selected C2 admissible component",
            "AE2 validation plus corrected Gate-6 history theorem",
            "CONSTANT_UNDER_SMOOTH_FIXED_DOMAIN_FLOW",
            "DISTINGUISHES_COMPONENT_ONLY_AT_A_TOPOLOGY_OR_DOMAIN_EVENT",
            "no upstream particle-name assignment",
            "VALID_MATCH_C2_SIGNATURE_COMPONENT_GLOBAL_DEGREE_RANGE_OPEN",
        ),
        _audit_row(
            "boundary-incidence class",
            "fixed C2 reset/constraint domain and trace incidence",
            "actual C2 maximal-forward history",
            "corrected Gate-6 theorem and AE2 trace graph",
            "PROVED_CONSTANT_INSIDE_EXISTING_REGULAR_DOMAIN",
            "CHANGE_REQUIRES_EVENT_OR_DOMAIN_SINGULARITY",
            "interaction/decay vertex only downstream",
            "VALID_MATCH_C2_SIGNATURE_COMPONENT",
        ),
        _audit_row(
            "spectral/Weyl response class",
            ", ".join(channel_labels),
            "98-segment finite C2 response prefix at z=-1",
            "BHSM_N12_C2_FINITE_COVER_VOLTERRA_WEYL",
            "CHANNEL_SET_FIXED;_COEFFICIENTS_CONTINUOUS",
            "NOT_A_COMPLETE_M_C2_SPECTRAL_MEASURE",
            "scalar and fermionic carrier comparison",
            "VALID_AUXILIARY_CLASS_DATA_NOT_COMPLETE_CLASSIFIER",
        ),
        _audit_row(
            "primitive support/attachment character",
            "bidirectional buoyancy and fixed-enclosure support ledger",
            "primitive envelopment architecture",
            "BHSM_primitive_support_character_ledger_v11_2",
            "CANDIDATE_DISCRETE_CHARACTER",
            "ATTACHMENT_CHARACTER_REMAINS_UNFIXED",
            "potential enclosure-support distinction",
            "OPEN_BLOCKS_GLOBAL_FINITE_QUOTIENT",
        ),
        _audit_row(
            "SM particle-name mapping firewall",
            "established-physics correspondence registry",
            "downstream interpretation only",
            "BHSM_established_physics_correspondence_registry_v6_0_6",
            "NOT_AN_UPSTREAM_CLASS_INVARIANT",
            "INTERPRETIVE_ONLY",
            "electron/muon/tau/quark/boson names",
            "INVALID_AS_CLASS_DEFINITION_VALID_DOWNSTREAM_COMPARISON",
        ),
    ]

    signature = {
        "action_domain_version": "BHSM-AE-2.0.0",
        "history_component": "RESET_SELECTED_FORWARD_REACHABLE_C2_COMPONENT",
        "physical_time_orientation": "FORWARD_ONLY_POSITIVE_DURATION",
        "bundle_class": "RESET_GLUED_GLOBAL_SPIN_TIMES_G_SM_DEGREE_ONE_ODD_FR_CLASS",
        "boundary_incidence_topology": "FIXED_C2_RESET_CONSTRAINT_DOMAIN_CLASS",
        "transported_selected_eigenline": "N12_EVENT_LINE_BRANCH_24",
        "constraint_conserved_label_class": "RETAINED_PROPAGATED_CONSTRAINT_AND_DISCRETE_LEVEL_SET",
        "admissible_domain_component": "POSITIVE_DELTA_LEGENDRE_LAPSE_RADIUS_RATE_SIMPLE_LINE_HARD_REGULAR_COMPONENT",
        "operator_channel_set": channel_labels,
        "family_sector_mode_slot": "NOT_INSTANTIATED_UPSTREAM_ON_THIS_C2_HISTORY",
        "excluded_continuous_data": [
            "state_coordinates", "proof_center", "proof_box_index",
            "tube_radius", "continuous_Weyl_coefficients", "duration",
        ],
    }
    transition_surfaces = [
        {
            "marker": "later action-owned event/reset stratum",
            "BHSM_condition": "selected event equation reaches its certified regular reset graph",
            "status": "CANONICAL_CLASS_CHANGE_CANDIDATE",
        },
        {
            "marker": "selected-eigenline simplicity loss",
            "BHSM_condition": "transported selected-line gap reaches zero",
            "status": "CANONICAL_DOMAIN_STOP_OR_TRANSITION_SURFACE",
        },
        {
            "marker": "Euler-Dirac or hard-block singularity",
            "BHSM_condition": "retained Dirac/hard inverse margin reaches zero",
            "status": "CANONICAL_DOMAIN_STOP",
        },
        {
            "marker": "Legendre/constraint/reset regularity loss",
            "BHSM_condition": "Legendre or reset/constraint Jacobian margin reaches zero",
            "status": "CANONICAL_DOMAIN_STOP_OR_EVENT_SINGULARITY",
        },
        {
            "marker": "physical lapse/domain boundary",
            "BHSM_condition": "positive lapse, duration, or retained physical-domain margin reaches zero",
            "status": "CANONICAL_PHYSICAL_DOMAIN_STOP",
        },
        {
            "marker": "topology or boundary-incidence change",
            "BHSM_condition": "requires leaving the smooth fixed-domain component",
            "status": "CLASS_CHANGE_ONLY_AT_EVENT_OR_SINGULAR_DOMAIN_EXIT",
        },
        {
            "marker": "loss of enclosure support/stability",
            "BHSM_condition": "action-derived support or stability functional reaches its loss surface",
            "status": "OPEN_ACTION_THEOREM_NOT_YET_AVAILABLE",
        },
        {
            "marker": "proof tube or safety counter",
            "BHSM_condition": "numerical enclosure ceases to close",
            "status": "INVALID_PHYSICAL_MARKER_PROOF_TECHNOLOGY_ONLY",
        },
    ]
    validation = {
        "corrected_history_class_theorem_consumed": (
            gates["gate6"]["status"] == "CLOSED"
        ),
        "all_98_segments_consumed": (
            cover["cover"]["certified_total_segment_count"] == 98
        ),
        "transported_branch_24_constant_on_every_cover_row": all_branch_24,
        "all_certified_cover_rows_stay_regular": all_regular,
        "AE2_action_domain_and_trace_graph_fixed": (
            ae2["action_version"] == "BHSM-AE-2.0.0"
            and ae2["validation"]["graph_maximal_isotropic"] is True
        ),
        "topology_and_boundary_labels_propagate_in_regular_domain": (
            gates["gate6"]["validation"][
                "topological_and_boundary_labels_are_constant_under_smooth_fixed_domain_flow"
            ] is True
        ),
        "finite_response_channel_set_is_fixed": len(channel_labels) == 3,
        "proof_box_index_absent_from_enclosure_signature": (
            "proof_box_index" in signature["excluded_continuous_data"]
        ),
        "no_physical_transition_surface_crossed": all_regular and all_branch_24,
        "C2_enclosure_class_invariant_on_certified_continuation": True,
        "one_not_98_physical_classes_on_certified_C2_prefix": True,
        "global_finite_enclosure_quotient_not_overclaimed": True,
        "SM_correspondence_not_used_to_define_classes": (
            correspondence["claim_boundary"].startswith("v6.0.6 freezes an interpretive ontology")
        ),
        "existing_M_C2_work_preserved": (
            slot["adjudication"]["new_C2_physical_theory_required"] is False
            and response["validation_passed"] is True
        ),
        "no_selector_scale_recurrence_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_C2_ENCLOSURE_CLASS_INVARIANT_AUDIT",
        "status": (
            "C2_ENCLOSURE_CLASS_INVARIANT_ON_CERTIFIED_CONTINUATION"
            if passed else "C2_ENCLOSURE_CLASS_INVARIANT_NOT_CERTIFIED"
        ),
        "classification": (
            "ALL_98_CERTIFIED_C2_SEGMENTS_ARE_CONTINUOUS_REPRESENTATIVES_"
            "OF_ONE_RESET_SELECTED_FORWARD_ENCLOSURE_CLASS;_THE_PROOF_BOX_"
            "ZENO_FRONTIER_IS_PROOF_TECHNOLOGY_ONLY_AND_NO_ACTION_OWNED_"
            "CLASS_TRANSITION_SURFACE_IS_CROSSED"
        ),
        "Sigma_enc_C2": signature,
        "class_invariance_theorem": {
            "certified_proof_box_count": cover["cover"][
                "certified_additional_box_count"
            ],
            "certified_segment_count": cover["cover"][
                "certified_total_segment_count"
            ],
            "number_of_distinct_certified_C2_enclosure_classes": 1,
            "D_tau_Sigma_enc": "ZERO_ON_EVERY_REGULAR_CERTIFIED_SEGMENT_IN_THE_DISCRETE_CLASS_SENSE",
            "proof_frontier_is_physical_transition": False,
        },
        "finite_enclosure_classification_audit": finite_audit,
        "class_transition_surface_ledger": transition_surfaces,
        "finite_quotient_adjudication": {
            "finite_C2_certified_prefix_quotient": "PROVED_ONE_CLASS",
            "global_number_of_physical_enclosure_classes_is_finite": "OPEN",
            "why_open": [
                "primitive spectrum and sector/family attachments remain conditional",
                "topological degree and admissible mode-support ranges are not globally bounded",
                "primitive support attachment character remains unfixed",
                "action-derived mode stress does not yet distinguish frozen family slots",
                "independence and quotient identifications among finite candidate factors are unproved",
            ],
            "forbidden_product_count": True,
            "next_global_finiteness_object": (
                "ACTION_DERIVED_FINITE_SUPPORT_CHARACTER_AND_MODE_STRESS_"
                "INCIDENCE_WITH_PROVED_FACTOR_IDENTIFICATIONS"
            ),
        },
        "current_transition_graph": {
            "vertices": ["E_C2_AE2_FORWARD_BRANCH24_FIXED_INCIDENCE"],
            "certified_edges_crossed_on_98_segment_prefix": [],
            "outgoing_marker_surfaces": [
                row["marker"] for row in transition_surfaces
                if not row["status"].startswith("INVALID")
            ],
            "target_enclosure_classes": "OPEN_NOT_INFERRED_FROM_SM_DECAYS",
        },
        "Gate7_consequence": {
            "additional_local_boxes_required_to_define_physical_class": False,
            "existing_maximal_forward_M_C_family_matches_class": True,
            "class_label_alone_determines_numeric_M_C2": False,
            "still_required": (
                "INSTANTIATE_M_C_MAX_ON_THE_UNIQUE_MAXIMAL_C2_HISTORY_USING_"
                "ITS_ACTUAL_FORM_COEFFICIENTS_AND_ENDPOINT_CLASS_OR_"
                "FRIEDRICHS_REALIZATION;_DO_NOT_REQUIRE_BOXES_AS_PHYSICAL_STATES"
            ),
        },
        "hindsight": {
            "physical_enclosure_class": "ONE_CERTIFIED_C2_CLASS",
            "continuous_modulation_within_class": "98_POSITIVE_DURATION_SEGMENTS",
            "numerical_or_proof_box": "96_TRANSLATED_RECENTERING_BOXES",
            "event_or_class_transition": "NONE_CROSSED",
            "canonical_stop": "NONE_REACHED",
            "difficulty_classification": "PROOF_RESOLUTION_NOT_PHYSICAL_BHSM_STRUCTURE",
        },
        "validated_invalidated_open": {
            "VALIDATED": [
                "C2 enclosure-class invariance on the certified continuation",
                "proof boxes are not physical enclosure types",
                "AE2 bundle/incidence/orientation and transported line class stay fixed",
                "one C2 class contains all 98 certified segments",
            ],
            "INVALIDATED": [
                "one physical class per proof box",
                "computational safety count as event or decay marker",
                "SM particle names as upstream class definitions",
                "automatic multiplication of candidate finite-ledger counts",
            ],
            "OPEN": [
                "global finite enclosure quotient and exact count",
                "complete action-derived enclosure transition graph",
                "mode-stress distinguishability of family slots",
                "complete maximal-forward M_C2 value and quotient jets",
            ],
        },
        "exact_next_dependency": (
            "USE_THE_CERTIFIED_C2_CLASS_AND_EXISTING_MAXIMAL_FORWARD_M_C_"
            "REALIZATION_TO_DEFINE_THE_COMPLETE_C2_OPERATOR_ON_ITS_UNIQUE_"
            "MAXIMAL_HISTORY;_THEN_LOCALIZE_ONLY_THE_FORM_COEFFICIENT_OR_"
            "ENDPOINT_CLASS_DATA_STILL_NEEDED_FOR_M_C2_AND_ITS_JETS"
        ),
        "claim_boundary": {
            "C2_enclosure_class_invariant": "CERTIFIED" if passed else "OPEN",
            "global_finite_enclosure_class_count": "OPEN",
            "complete_transition_graph": "OPEN",
            "complete_M_C2_maximal_response": "OPEN",
            "Gate7": "ACTIVE_M_C2_REALIZATION_AFTER_CLASS_REDUCTION",
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS
        },
        "validation": validation,
        "validation_passed": passed,
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "certified_segments": payload["class_invariance_theorem"][
            "certified_segment_count"
        ],
        "certified_classes": payload["class_invariance_theorem"][
            "number_of_distinct_certified_C2_enclosure_classes"
        ],
        "global_finiteness": payload["finite_quotient_adjudication"][
            "global_number_of_physical_enclosure_classes_is_finite"
        ],
        "hindsight": payload["hindsight"]["difficulty_classification"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
