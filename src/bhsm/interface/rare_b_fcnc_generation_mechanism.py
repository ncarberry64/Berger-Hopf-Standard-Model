"""Claim-safe rare-B FCNC generation-mechanism kill screen for BHSM v5.3."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any


VERSION = "v5.3"
SPRINT = "bhsm-rare-b-fcnc-generation-mechanism-v5-3"
PRIMARY_VERDICT = "RARE_B_FCNC_GENERATION_MECHANISM_BLOCKED"
EARLIEST_BLOCKER = "OPEN_MISSING_RARE_B_CHARGED_CURRENT_PAIR_COMPOSITION"
CHANNEL = "b -> s neutral transition"
V5_1_VERDICT = "RARE_B_OBSERVABLE_MAP_INTERFACE_COMPLETE"
V5_2_VERDICT = "B_TO_S_MUMU_OPERATOR_MATCHING_BLOCKED"

ARTIFACT_FILES = {
    "neutral_current_flavor_structure_audit": "BHSM_rare_b_neutral_current_flavor_structure_audit_v5_3.json",
    "charged_current_pair_composition": "BHSM_rare_b_charged_current_pair_composition_v5_3.json",
    "intermediate_response_inventory": "BHSM_rare_b_intermediate_response_inventory_v5_3.json",
    "fcnc_generation_candidate": "BHSM_rare_b_fcnc_generation_candidate_v5_3.json",
    "gim_like_cancellation_audit": "BHSM_rare_b_gim_like_cancellation_audit_v5_3.json",
    "dependency_graph": "BHSM_rare_b_fcnc_generation_dependency_graph_v5_3.json",
    "verdict": "BHSM_rare_b_fcnc_generation_mechanism_verdict_v5_3.json",
}

PRESERVED_STATUSES = (
    "ACTION_ATTACHMENT_BLOCKED",
    "CKM_RELATIVE_CURRENT_NORMALIZATION_BLOCKED",
    "COUPLING_BRIDGE_BLOCKED_PENDING_ACTION_PRINCIPLE",
    "RARE_B_AFB_ZERO_PREDICTION_BLOCKED",
    "RARE_B_MICROPLATEAU_NODE_PREDICTION_BLOCKED",
    V5_1_VERDICT,
    V5_2_VERDICT,
)

PRESERVED_OPEN_GATES = (
    "OPEN_MISSING_RARE_B_FCNC_GENERATION_MECHANISM",
    "OPEN_MISSING_NORMALIZED_B_TO_S_QUARK_CURRENT",
    "OPEN_MISSING_NORMALIZED_MUON_CURRENT_ATTACHMENT",
    "OPEN_MISSING_RARE_B_OPERATOR_CHIRALITY_MAP",
    "OPEN_MISSING_RARE_B_LOOP_MATCHING_PRINCIPLE",
    "OPEN_MISSING_RARE_B_OPERATOR_ACTION_NORMALIZATION",
    "OPEN_MISSING_RARE_B_OPERATOR_DIMENSIONFUL_BRIDGE",
    "OPEN_MISSING_RARE_B_RENORMALIZATION_SCALE_MAP",
    "OPEN_MISSING_BHSM_TO_RARE_B_OPERATOR_MATCHING",
    "OPEN_MISSING_BHSM_WILSON_COEFFICIENT_DERIVATION",
    "OPEN_MISSING_BHSM_HADRONIC_MATRIX_ELEMENTS",
    "OPEN_MISSING_RARE_B_Q2_PHYSICAL_BRIDGE",
    "OPEN_MISSING_GAUGE_COUPLING_ACTION_ATTACHMENT",
    "OPEN_MISSING_ALPHA_I_ACTION_DERIVATION",
    "OPEN_MISSING_G2_BH_ACTION_SOURCE",
    "OPEN_MISSING_CKM_COEFFICIENT_VALUE_SOURCE",
    "CKM_EXPONENT_NOT_DERIVED",
    "FULL_BHSM_NOT_COMPLETE",
)

REFINED_OPEN_BLOCKERS = (
    "OPEN_MISSING_RARE_B_CHARGED_CURRENT_PAIR_COMPOSITION",
    "OPEN_MISSING_RARE_B_INTERMEDIATE_RESPONSE_KERNEL",
    "OPEN_MISSING_RARE_B_GENERATION_MODE_SUM",
    "OPEN_MISSING_RARE_B_DEGENERACY_CANCELLATION_LAW",
    "OPEN_MISSING_RARE_B_INDUCED_NEUTRAL_KERNEL",
    "OPEN_MISSING_RARE_B_FCNC_ACTION_SOURCE",
    "OPEN_MISSING_RARE_B_FCNC_CURRENT_NORMALIZATION",
    "OPEN_MISSING_RARE_B_FCNC_PERTURBATIVE_ORDER",
    "OPEN_MISSING_RARE_B_FCNC_PHASE_CONVENTION",
)

FORBIDDEN_POSITIVE_CLAIMS = (
    "BHSM automatically produces FCNCs",
    "BHSM reproduces the Standard Model penguin",
    "BHSM derives a loop factor from geometry",
    "BHSM explains LHCb",
    "BHSM predicts rare-B anomalies",
    "BHSM derives Wilson coefficients",
    "BHSM predicts q0^2",
    "BHSM predicts micro-plateaus",
    "BHSM falsifies QFT",
    "BHSM is complete",
)

PREDICTION_NULL_STATE = {
    "prediction_claimed": False,
    "C7_BHSM": None,
    "C9_BHSM": None,
    "C10_BHSM": None,
    "delta_C7_BHSM": None,
    "delta_C9_BHSM": None,
    "delta_C10_BHSM": None,
    "q0_squared_value": None,
    "q0_squared_units": None,
    "microplateau_node_coordinates": [],
    "no_fit_discipline_preserved": True,
}


class ClosureStatus(str, Enum):
    DERIVED = "DERIVED"
    CONDITIONAL = "CONDITIONAL"
    ARTIFACT_BACKED_INPUT = "ARTIFACT_BACKED_INPUT_ONLY"
    INTERFACE_ONLY = "INTERFACE_ONLY"
    BLOCKED = "BLOCKED"
    ABSENT = "ABSENT"
    OPEN = "OPEN"


@dataclass(frozen=True)
class MechanismObject:
    file: str
    symbol_or_artifact: str
    repository_location: str
    input_space: str
    output_space: str
    physical_or_geometric_role: str
    flavor_structure: str
    neutral_or_charged_character: str
    action_attachment: str
    normalization: str
    units: str
    perturbative_order: str
    supports_composition: bool
    supports_intermediate_propagation: bool
    supports_generation_sum: bool
    supports_complex_phases: bool
    can_generate_off_diagonal_neutral_matrix_element: bool
    claim_status: str
    blocking_dependency: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DependencyEdge:
    source: str
    target: str
    map_name: str
    status: str
    provenance: str
    units_transformation: str
    normalization_transformation: str
    blocking_dependency: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ChargedCurrentPairCandidate:
    initial_flavor: str
    final_flavor: str
    first_current_insertion: str | None
    intermediate_state: str | None
    second_current_insertion: str | None
    flavor_orientation: str | None
    complex_conjugation: str | None
    composition_law: str | None
    internal_response_object: str | None
    action_source: str | None
    normalization: str | None
    perturbative_status: str
    candidate_output: str | None
    closure_status: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _common_payload(artifact: str) -> dict[str, Any]:
    return {
        "artifact": artifact,
        "version": VERSION,
        "sprint": SPRINT,
        "channel": CHANNEL,
        "primary_verdict": PRIMARY_VERDICT,
        "claim_boundary": (
            "FCNC generation-mechanism kill screen only. BHSM v5.3 does not derive "
            "a physical b -> s neutral transition, Wilson coefficients, q0^2, or exact rare-B node coordinates."
        ),
        "empirical_inputs_used": False,
        "rare_b_data_fitting_used": False,
        "pdg_reference_values_used": False,
        "w_calibration_used": False,
        "charged_mass_fitting_used": False,
        "ckm_fitting_used": False,
        "neutrino_limits_used": False,
        "legacy_threshold_tables_used": False,
        "frozen_predictions_changed": False,
        "official_prediction_logic_changed": False,
        "physics_model_logic_changed": False,
    }


def audited_mechanism_objects() -> tuple[MechanismObject, ...]:
    return (
        MechanismObject(
            file="artifacts/CKM_no_fit_operator_output_v1.json",
            symbol_or_artifact="CKM_no_fit_operator_output_v1",
            repository_location="artifacts/CKM_no_fit_operator_output_v1.json",
            input_space="BHSM dimensionless flavor geometry",
            output_space="CKM relative mixing matrix/provenance adapter",
            physical_or_geometric_role="relative charged-current flavor geometry input",
            flavor_structure="off-diagonal mixing entries exist as relative geometry",
            neutral_or_charged_character="charged-current flavor transport context",
            action_attachment="not an FCNC action source",
            normalization="relative only; absolute current normalization remains open",
            units="dimensionless",
            perturbative_order="not a perturbative transition mechanism",
            supports_composition=False,
            supports_intermediate_propagation=False,
            supports_generation_sum=False,
            supports_complex_phases=True,
            can_generate_off_diagonal_neutral_matrix_element=False,
            claim_status=ClosureStatus.ARTIFACT_BACKED_INPUT.value,
            blocking_dependency="OPEN_MISSING_RARE_B_CHARGED_CURRENT_PAIR_COMPOSITION",
        ),
        MechanismObject(
            file="artifacts/BHSM_charged_current_transport_space_audit_v2_6.json",
            symbol_or_artifact="BHSM_charged_current_transport_space_audit_v2_6",
            repository_location="artifacts/BHSM_charged_current_transport_space_audit_v2_6.json",
            input_space="charged-current target/interface evidence",
            output_space="transport-space gates",
            physical_or_geometric_role="charged-current transport-space audit",
            flavor_structure="charged-current target structure only",
            neutral_or_charged_character="charged",
            action_attachment="normalized action source remains blocked",
            normalization="open",
            units="dimensionless/action units open",
            perturbative_order="not a second-order induced-transition theorem",
            supports_composition=False,
            supports_intermediate_propagation=False,
            supports_generation_sum=False,
            supports_complex_phases=False,
            can_generate_off_diagonal_neutral_matrix_element=False,
            claim_status=ClosureStatus.CONDITIONAL.value,
            blocking_dependency="OPEN_MISSING_RARE_B_CHARGED_CURRENT_PAIR_COMPOSITION",
        ),
        MechanismObject(
            file="artifacts/BHSM_normalized_charged_current_action_term_v2_6.json",
            symbol_or_artifact="BHSM_normalized_charged_current_action_term_v2_6",
            repository_location="artifacts/BHSM_normalized_charged_current_action_term_v2_6.json",
            input_space="charged-current source search",
            output_space="blocked normalized action-term status",
            physical_or_geometric_role="charged-current action-normalization kill screen",
            flavor_structure="charged-current structure, not neutral FCNC",
            neutral_or_charged_character="charged",
            action_attachment="blocked",
            normalization="open",
            units="dimensionless/action units open",
            perturbative_order="not a rare-B induced transition",
            supports_composition=False,
            supports_intermediate_propagation=False,
            supports_generation_sum=False,
            supports_complex_phases=False,
            can_generate_off_diagonal_neutral_matrix_element=False,
            claim_status=ClosureStatus.BLOCKED.value,
            blocking_dependency="OPEN_MISSING_RARE_B_FCNC_ACTION_SOURCE",
        ),
        MechanismObject(
            file="artifacts/BHSM_neutral_action_closure_report_v1_5.json",
            symbol_or_artifact="BHSM_neutral_action_closure_report_v1_5",
            repository_location="artifacts/BHSM_neutral_action_closure_report_v1_5.json",
            input_space="neutral response cone and stiffness candidates",
            output_space="conditional neutral action closure report",
            physical_or_geometric_role="generic neutral response/action support audit",
            flavor_structure="no explicit b-s off-diagonal flavor matrix element",
            neutral_or_charged_character="neutral",
            action_attachment="conditional neutral response; no rare-B FCNC term",
            normalization="neutral action normalization open",
            units="dimensionless/neutral-scale open",
            perturbative_order="not a tree-level FCNC theorem and not an induced loop theorem",
            supports_composition=False,
            supports_intermediate_propagation=False,
            supports_generation_sum=False,
            supports_complex_phases=False,
            can_generate_off_diagonal_neutral_matrix_element=False,
            claim_status=ClosureStatus.CONDITIONAL.value,
            blocking_dependency="OPEN_MISSING_RARE_B_INDUCED_NEUTRAL_KERNEL",
        ),
        MechanismObject(
            file="artifacts/BHSM_b_to_s_mumu_transition_dependency_graph_v5_2.json",
            symbol_or_artifact="BHSM_b_to_s_mumu_transition_dependency_graph_v5_2",
            repository_location="artifacts/BHSM_b_to_s_mumu_transition_dependency_graph_v5_2.json",
            input_space="operator-matching dependency nodes",
            output_space="blocked matching graph",
            physical_or_geometric_role="downstream v5.2 operator dependency graph",
            flavor_structure="b -> s selector is named but FCNC generation remains open",
            neutral_or_charged_character="rare-B neutral semileptonic target interface",
            action_attachment="not closed",
            normalization="not closed",
            units="not closed",
            perturbative_order="open",
            supports_composition=False,
            supports_intermediate_propagation=False,
            supports_generation_sum=False,
            supports_complex_phases=False,
            can_generate_off_diagonal_neutral_matrix_element=False,
            claim_status=ClosureStatus.BLOCKED.value,
            blocking_dependency="OPEN_MISSING_RARE_B_FCNC_GENERATION_MECHANISM",
        ),
        MechanismObject(
            file="artifacts/BHSM_rare_b_transition_operator_interface_v5_1.json",
            symbol_or_artifact="BHSM_rare_b_transition_operator_interface_v5_1",
            repository_location="artifacts/BHSM_rare_b_transition_operator_interface_v5_1.json",
            input_space="external EFT operator-basis convention slots",
            output_space="O7/O9/O10 and Wilson slots",
            physical_or_geometric_role="rare-B interface, not BHSM generation mechanism",
            flavor_structure="b -> s label appears as target convention",
            neutral_or_charged_character="external neutral semileptonic interface",
            action_attachment="no BHSM action source",
            normalization="not BHSM-normalized",
            units="external convention",
            perturbative_order="external convention, not BHSM loop derivation",
            supports_composition=False,
            supports_intermediate_propagation=False,
            supports_generation_sum=False,
            supports_complex_phases=False,
            can_generate_off_diagonal_neutral_matrix_element=False,
            claim_status=ClosureStatus.INTERFACE_ONLY.value,
            blocking_dependency="OPEN_MISSING_RARE_B_FCNC_GENERATION_MECHANISM",
        ),
        MechanismObject(
            file="artifacts/BHSM_ckm_relative_current_normalization_killscreen_v4_8.json",
            symbol_or_artifact="BHSM_ckm_relative_current_normalization_killscreen_v4_8",
            repository_location="artifacts/BHSM_ckm_relative_current_normalization_killscreen_v4_8.json",
            input_space="CKM relative geometry",
            output_space="blocked absolute current normalization",
            physical_or_geometric_role="current-normalization blocker",
            flavor_structure="relative CKM structure only",
            neutral_or_charged_character="charged-current normalization context",
            action_attachment="blocked",
            normalization="c_rel^2=4*pi not derived",
            units="dimensionless",
            perturbative_order="not an FCNC mechanism",
            supports_composition=False,
            supports_intermediate_propagation=False,
            supports_generation_sum=False,
            supports_complex_phases=False,
            can_generate_off_diagonal_neutral_matrix_element=False,
            claim_status=ClosureStatus.BLOCKED.value,
            blocking_dependency="OPEN_MISSING_RARE_B_FCNC_CURRENT_NORMALIZATION",
        ),
    )


def neutral_current_flavor_structure_audit_artifact() -> dict[str, Any]:
    payload = _common_payload("BHSM_rare_b_neutral_current_flavor_structure_audit_v5_3")
    neutral_sources = [row.to_dict() for row in audited_mechanism_objects() if row.neutral_or_charged_character.startswith("neutral") or "neutral" in row.neutral_or_charged_character]
    payload.update(
        {
            "status": "RARE_B_NEUTRAL_CURRENT_FLAVOR_STRUCTURE_AUDIT_ARTIFACTED",
            "neutral_current_source_artifacts": neutral_sources,
            "flavor_space_domain": "not action-backed for a b-s off-diagonal neutral current",
            "diagonal_off_diagonal_status": "NO_EXPLICIT_ACTION_BACKED_OFF_DIAGONAL_NEUTRAL_CURRENT",
            "sector_structure": "generic neutral response is sector/geometric context, not a rare-B flavor theorem",
            "generation_structure": "no generation-off-diagonal neutral matrix element is derived",
            "action_attachment": "OPEN_MISSING_RARE_B_FCNC_ACTION_SOURCE",
            "normalization": "OPEN_MISSING_RARE_B_FCNC_CURRENT_NORMALIZATION",
            "tree_level_b_s_permitted": False,
            "tree_level_b_s_derived": False,
            "blocking_reason": "No existing action or theorem permits a tree-level b-s neutral current.",
            "claim_safe_rule": "No explicit action-backed off-diagonal neutral current -> no tree-level BHSM FCNC claim.",
        }
    )
    return payload


def charged_current_pair_candidate() -> ChargedCurrentPairCandidate:
    return ChargedCurrentPairCandidate(
        initial_flavor="b",
        final_flavor="s",
        first_current_insertion=None,
        intermediate_state=None,
        second_current_insertion=None,
        flavor_orientation=None,
        complex_conjugation=None,
        composition_law=None,
        internal_response_object=None,
        action_source=None,
        normalization=None,
        perturbative_status="OPEN_MISSING_RARE_B_FCNC_PERTURBATIVE_ORDER",
        candidate_output=None,
        closure_status=EARLIEST_BLOCKER,
    )


def charged_current_pair_composition_artifact() -> dict[str, Any]:
    payload = _common_payload("BHSM_rare_b_charged_current_pair_composition_v5_3")
    candidate = charged_current_pair_candidate()
    payload.update(
        {
            "status": "RARE_B_CHARGED_CURRENT_PAIR_COMPOSITION_BLOCKED",
            "candidate": candidate.to_dict(),
            "required_route": [
                "explicit first charged-current insertion b -> up-type intermediate mode i",
                "intermediate-state propagation or response kernel",
                "explicit second charged-current insertion i -> s",
                "flavor orientation and complex-conjugation convention",
                "current normalization and action source",
            ],
            "structural_template_not_derived": "K_bs^(neutral) = sum_i T_si^dagger G_i T_ib",
            "template_status": "INTERFACE_PATTERN_ONLY_NOT_PHYSICAL_DERIVATION",
            "closure_status": candidate.closure_status,
        }
    )
    return payload


def intermediate_response_inventory_artifact() -> dict[str, Any]:
    payload = _common_payload("BHSM_rare_b_intermediate_response_inventory_v5_3")
    entries = [
        {
            "repository_source": "src/bhsm/interface/neutrino_propagation/neutral_kernel.py; artifacts/BHSM_neutral_projected_kernel_v1_4.json",
            "object_family": "neutral projected kernel",
            "input_output_spaces": "neutral response/channel space, not rare-B charged-current intermediate modes",
            "boundary_conditions": "neutral-sector domain only",
            "units": "dimensionless/neutral-scale open",
            "normalization": "not FCNC-normalized",
            "physical_interpretation": "neutral response support, not b -> up -> s propagation",
            "action_provenance": "conditional neutral-sector provenance",
            "usable_for_fcnc_generation": False,
            "blocking_reason": "does not define an internal up-type mode response between two charged-current insertions",
        },
        {
            "repository_source": "artifacts/BHSM_sector_boundary_operator_v4_6.json",
            "object_family": "sector boundary Laplace-type operator candidate",
            "input_output_spaces": "adjoint-valued boundary one-forms",
            "boundary_conditions": "gauge-fixed boundary domain remains open",
            "units": "operator class only",
            "normalization": "physical alpha_i identification open",
            "physical_interpretation": "gauge-boundary whitening candidate",
            "action_provenance": "OPEN_MISSING_SECTOR_BOUNDARY_OPERATOR_ACTION_SOURCE",
            "usable_for_fcnc_generation": False,
            "blocking_reason": "not a flavor intermediate-state propagator or mode-sum denominator",
        },
        {
            "repository_source": "artifacts/BHSM_b_to_s_mumu_transition_dependency_graph_v5_2.json",
            "object_family": "rare-B matching graph",
            "input_output_spaces": "dependency nodes only",
            "boundary_conditions": "not applicable",
            "units": "not closed",
            "normalization": "not closed",
            "physical_interpretation": "records missing FCNC mechanism",
            "action_provenance": "none",
            "usable_for_fcnc_generation": False,
            "blocking_reason": "graph marks FCNC generation as open; it is not itself a response kernel",
        },
    ]
    payload.update(
        {
            "status": "RARE_B_INTERMEDIATE_RESPONSE_KERNEL_ABSENT",
            "inventory": entries,
            "derived": False,
            "conditional": False,
            "candidate": False,
            "external": False,
            "absent": True,
            "blocking_dependency": "OPEN_MISSING_RARE_B_INTERMEDIATE_RESPONSE_KERNEL",
        }
    )
    return payload


def fcnc_generation_candidate_artifact() -> dict[str, Any]:
    payload = _common_payload("BHSM_rare_b_fcnc_generation_candidate_v5_3")
    payload.update(
        {
            "status": "RARE_B_FCNC_GENERATION_CANDIDATE_EMPTY_BLOCKED",
            "initial_flavor": "b",
            "final_flavor": "s",
            "external_channel": "neutral",
            "tree_level_fcnc_status": "TREE_LEVEL_FCNC_FORBIDDEN_OR_UNPROVED",
            "charged_current_pair_status": EARLIEST_BLOCKER,
            "intermediate_state_status": "OPEN_MISSING_RARE_B_INTERMEDIATE_RESPONSE_KERNEL",
            "generation_sum_status": "OPEN_MISSING_RARE_B_GENERATION_MODE_SUM",
            "cancellation_law_status": "OPEN_MISSING_RARE_B_DEGENERACY_CANCELLATION_LAW",
            "neutral_current_attachment_status": "OPEN_MISSING_RARE_B_INDUCED_NEUTRAL_KERNEL",
            "phase_conjugation_status": "OPEN_MISSING_RARE_B_FCNC_PHASE_CONVENTION",
            "action_source_status": "OPEN_MISSING_RARE_B_FCNC_ACTION_SOURCE",
            "normalization_status": "OPEN_MISSING_RARE_B_FCNC_CURRENT_NORMALIZATION",
            "dimension_status": "OPEN_MISSING_RARE_B_OPERATOR_DIMENSIONFUL_BRIDGE",
            "perturbative_order_status": "OPEN_MISSING_RARE_B_FCNC_PERTURBATIVE_ORDER",
            "candidate_expression": None,
            "symbolic_template_not_promoted": "A_bs = sum_i F_flavor(i; b,s) R_internal(i)",
            "candidate_nonzero_status": "NONZERO_TRANSITION_NOT_ESTABLISHED",
            "connection_to_v5_2": {
                "source_artifact": "artifacts/BHSM_b_to_s_mumu_transition_dependency_graph_v5_2.json",
                "v5_2_first_open_edge": "b -> s flavor selector -> FCNC generation mechanism",
                "v5_3_refinement": EARLIEST_BLOCKER,
            },
            "prediction_state": dict(PREDICTION_NULL_STATE),
        }
    )
    return payload


def gim_like_cancellation_audit_artifact() -> dict[str, Any]:
    payload = _common_payload("BHSM_rare_b_gim_like_cancellation_audit_v5_3")
    payload.update(
        {
            "status": "RARE_B_GIM_LIKE_CANCELLATION_THEOREM_ABSENT",
            "bhsm_generation_sum_exists": False,
            "flavor_independent_responses_canceled": False,
            "ckm_unitarity_or_equivalent_identity_used": "CKM unitarity alone is not a full weighted-response cancellation theorem",
            "degeneracy_cancellation_proved": False,
            "nonzero_mode_splitting_defined": False,
            "result_action_connected": False,
            "result_normalized": False,
            "cancellation_theorem_status": "OPEN_MISSING_RARE_B_DEGENERACY_CANCELLATION_LAW",
            "required_weighted_response_form": "sum_i flavor_weight_i * internal_response_i",
            "no_go_note": "Do not call a BHSM mechanism GIM-derived until the weighted response and degeneracy cancellation are artifact-backed.",
        }
    )
    return payload


def dependency_edges() -> tuple[DependencyEdge, ...]:
    return (
        DependencyEdge(
            "charged-current flavor transport",
            "first charged-current insertion",
            "select b -> intermediate charged-current transition",
            "BLOCKED",
            "v2.6 charged-current transport/action audits; v5.3 audit",
            "dimensionless -> not closed",
            "current normalization absent",
            "OPEN_MISSING_RARE_B_CHARGED_CURRENT_PAIR_COMPOSITION",
        ),
        DependencyEdge(
            "first charged-current insertion",
            "intermediate-state response",
            "propagate or resolve internal mode",
            "BLOCKED",
            "v5.3 intermediate-response inventory",
            "not available",
            "not available",
            "OPEN_MISSING_RARE_B_INTERMEDIATE_RESPONSE_KERNEL",
        ),
        DependencyEdge(
            "intermediate-state response",
            "second charged-current insertion",
            "complete intermediate -> s transition",
            "BLOCKED",
            "v5.3 charged-current pair-composition audit",
            "not available",
            "not available",
            "OPEN_MISSING_RARE_B_CHARGED_CURRENT_PAIR_COMPOSITION",
        ),
        DependencyEdge(
            "second charged-current insertion",
            "generation-mode sum",
            "sum over intermediate modes with orientation and conjugation",
            "BLOCKED",
            "v5.3 generation-sum audit",
            "not available",
            "not available",
            "OPEN_MISSING_RARE_B_GENERATION_MODE_SUM",
        ),
        DependencyEdge(
            "generation-mode sum",
            "cancellation/non-cancellation law",
            "prove degeneracy cancellation and mode-splitting residue",
            "BLOCKED",
            "v5.3 GIM-like cancellation audit",
            "not available",
            "not available",
            "OPEN_MISSING_RARE_B_DEGENERACY_CANCELLATION_LAW",
        ),
        DependencyEdge(
            "cancellation/non-cancellation law",
            "induced b -> s neutral kernel",
            "construct off-diagonal neutral effective kernel",
            "BLOCKED",
            "v5.3 FCNC candidate artifact",
            "not available",
            "not available",
            "OPEN_MISSING_RARE_B_INDUCED_NEUTRAL_KERNEL",
        ),
        DependencyEdge(
            "induced b -> s neutral kernel",
            "v5.2 operator matching",
            "feed normalized rare-B transition operator graph",
            "BLOCKED_DOWNSTREAM",
            "artifacts/BHSM_b_to_s_mumu_transition_dependency_graph_v5_2.json",
            "not available",
            "not available",
            "OPEN_MISSING_RARE_B_FCNC_GENERATION_MECHANISM",
        ),
        DependencyEdge(
            "v5.2 operator matching",
            "Wilson coefficients",
            "populate O7/O9/O10 coefficient slots",
            "BLOCKED_DOWNSTREAM",
            "artifacts/BHSM_b_to_s_mumu_operator_matching_verdict_v5_2.json",
            "not available",
            "not available",
            "OPEN_MISSING_BHSM_WILSON_COEFFICIENT_DERIVATION",
        ),
        DependencyEdge(
            "Wilson coefficients",
            "rare-B observables",
            "feed A_FB and node interfaces",
            "BLOCKED_DOWNSTREAM",
            "artifacts/BHSM_rare_b_observable_map_scaffold_verdict_v5_1.json",
            "external observable units remain open",
            "hadronic and q^2 gates open",
            "RARE_B_AFB_ZERO_PREDICTION_BLOCKED",
        ),
    )


def dependency_graph_artifact() -> dict[str, Any]:
    payload = _common_payload("BHSM_rare_b_fcnc_generation_dependency_graph_v5_3")
    payload.update(
        {
            "status": "RARE_B_FCNC_GENERATION_DEPENDENCY_GRAPH_ARTIFACTED",
            "nodes": [
                "charged-current flavor transport",
                "first charged-current insertion",
                "intermediate-state response",
                "second charged-current insertion",
                "generation-mode sum",
                "cancellation/non-cancellation law",
                "induced b -> s neutral kernel",
                "v5.2 operator matching",
                "Wilson coefficients",
                "rare-B observables",
            ],
            "edges": [edge.to_dict() for edge in dependency_edges()],
            "first_open_edge": {
                "source": "charged-current flavor transport",
                "target": "first charged-current insertion",
                "blocking_dependency": EARLIEST_BLOCKER,
            },
        }
    )
    return payload


def verdict_artifact() -> dict[str, Any]:
    payload = _common_payload("BHSM_rare_b_fcnc_generation_mechanism_verdict_v5_3")
    payload.update(
        {
            "status": PRIMARY_VERDICT,
            "primary_verdict": PRIMARY_VERDICT,
            "earliest_blocking_dependency": EARLIEST_BLOCKER,
            "tree_level_fcnc_status": "TREE_LEVEL_FCNC_FORBIDDEN_OR_UNPROVED",
            "charged_current_composition_status": EARLIEST_BLOCKER,
            "intermediate_response_status": "OPEN_MISSING_RARE_B_INTERMEDIATE_RESPONSE_KERNEL",
            "generation_sum_status": "OPEN_MISSING_RARE_B_GENERATION_MODE_SUM",
            "cancellation_law_status": "OPEN_MISSING_RARE_B_DEGENERACY_CANCELLATION_LAW",
            "action_source_status": "OPEN_MISSING_RARE_B_FCNC_ACTION_SOURCE",
            "normalization_status": "OPEN_MISSING_RARE_B_FCNC_CURRENT_NORMALIZATION",
            "perturbative_order_status": "OPEN_MISSING_RARE_B_FCNC_PERTURBATIVE_ORDER",
            "dimension_status": "OPEN_MISSING_RARE_B_OPERATOR_DIMENSIONFUL_BRIDGE",
            "nonzero_transition_established": False,
            "connection_to_v5_2": "refines OPEN_MISSING_RARE_B_FCNC_GENERATION_MECHANISM without changing B_TO_S_MUMU_OPERATOR_MATCHING_BLOCKED",
            "prediction_claimed": False,
            "wilson_values_emitted": False,
            "frozen_predictions_changed": False,
            "official_prediction_logic_changed": False,
            "validated": [
                "neutral-current artifacts do not permit a tree-level b-s neutral current by default",
                "charged-current transport exists only as upstream relative/interface structure",
                "v5.2 first open FCNC edge is refined into explicit generation-mechanism gates",
                "v5.1 observable interface and v5.2 operator-matching blocked verdict are preserved",
                "prediction kill screen remains null for C7/C9/C10, q0^2, and node coordinates",
            ],
            "invalidated_or_downgraded": [
                "CKM geometry alone is not an FCNC generation mechanism",
                "generic neutral response alone is not an FCNC theorem",
                "two named charged-current labels are not a loop or induced-transition theorem",
                "CKM unitarity alone is not a weighted-response cancellation theorem",
                "a symbolic flavor sum without an internal response cannot establish a nonzero b -> s kernel",
            ],
            "still_open": list(REFINED_OPEN_BLOCKERS + PRESERVED_OPEN_GATES),
            "preserved_statuses": list(PRESERVED_STATUSES),
            "new_or_refined_open_blockers": list(REFINED_OPEN_BLOCKERS),
            "prediction_state": dict(PREDICTION_NULL_STATE),
            "claim_safe_conclusion": (
                "BHSM v5.3 does not derive an FCNC-generation mechanism for b -> s. "
                "The kill screen identifies the earliest missing charged-current composition, "
                "intermediate-response, cancellation, action, or normalization dependency. "
                "Wilson coefficients, q0^2, and exact node positions remain absent, and prediction claimed remains no."
            ),
            "recommended_next_sprint": "bhsm-charged-current-pair-composition-v5-4",
        }
    )
    return payload


def audit_answers() -> dict[str, Any]:
    return {
        "explicit_tree_level_b_s_neutral_current_exists": False,
        "explicit_bhsm_charged_current_pair_composition_exists": False,
        "explicit_intermediate_response_kernel_exists": False,
        "explicit_generation_sum_exists": False,
        "explicit_gim_like_or_degeneracy_cancellation_theorem_exists": False,
        "explicit_nonzero_b_to_s_induced_kernel_exists": False,
        "explicit_action_source_exists": False,
        "explicit_current_normalization_exists": False,
        "explicit_perturbative_order_exists": False,
        "physical_fcnc_mechanism_derived": False,
        "numerical_C7_exists": False,
        "numerical_C9_exists": False,
        "numerical_C10_exists": False,
        "numerical_q0_squared_exists": False,
        "exact_node_coordinates_exist": False,
    }


def mechanism_layer_status() -> dict[str, str]:
    return {
        "Tree-level neutral-current flavor structure": "TREE_LEVEL_FCNC_FORBIDDEN_OR_UNPROVED",
        "Charged-current first insertion": EARLIEST_BLOCKER,
        "Intermediate-state response": "OPEN_MISSING_RARE_B_INTERMEDIATE_RESPONSE_KERNEL",
        "Charged-current second insertion": EARLIEST_BLOCKER,
        "Generation-mode sum": "OPEN_MISSING_RARE_B_GENERATION_MODE_SUM",
        "Flavor-factor orientation": "OPEN_MISSING_RARE_B_FCNC_PHASE_CONVENTION",
        "Complex conjugation": "OPEN_MISSING_RARE_B_FCNC_PHASE_CONVENTION",
        "Cancellation law": "OPEN_MISSING_RARE_B_DEGENERACY_CANCELLATION_LAW",
        "Mode-splitting dependence": "OPEN_MISSING_RARE_B_DEGENERACY_CANCELLATION_LAW",
        "Induced neutral kernel": "OPEN_MISSING_RARE_B_INDUCED_NEUTRAL_KERNEL",
        "Action source": "OPEN_MISSING_RARE_B_FCNC_ACTION_SOURCE",
        "Current normalization": "OPEN_MISSING_RARE_B_FCNC_CURRENT_NORMALIZATION",
        "Perturbative order": "OPEN_MISSING_RARE_B_FCNC_PERTURBATIVE_ORDER",
        "Physical dimensions": "OPEN_MISSING_RARE_B_OPERATOR_DIMENSIONFUL_BRIDGE",
        "Connection to v5.2 operator graph": "EXPLICIT_BLOCKED_MAPPING",
    }


def validate_charged_current_pair(candidate: ChargedCurrentPairCandidate) -> ChargedCurrentPairCandidate:
    if candidate.initial_flavor != "b" or candidate.final_flavor != "s":
        raise ValueError("FCNC pair candidate requires explicit b and s flavor endpoints")
    required = {
        "first charged-current insertion": candidate.first_current_insertion,
        "intermediate state": candidate.intermediate_state,
        "second charged-current insertion": candidate.second_current_insertion,
        "flavor orientation": candidate.flavor_orientation,
        "complex conjugation": candidate.complex_conjugation,
        "composition law": candidate.composition_law,
        "internal response object": candidate.internal_response_object,
        "action source": candidate.action_source,
        "normalization": candidate.normalization,
    }
    missing = [label for label, value in required.items() if value is None]
    if missing:
        raise ValueError("charged-current pair composition missing: " + ", ".join(missing))
    if candidate.closure_status != "RARE_B_FCNC_GENERATION_MECHANISM_DERIVED":
        raise ValueError("charged-current pair composition is not derived")
    return candidate


def reject_tree_level_fcnc_without_theorem(theorem_status: str) -> dict[str, Any]:
    if theorem_status not in {"DERIVED", "ARTIFACT_BACKED_DERIVED"}:
        return {
            "allowed": False,
            "status": "TREE_LEVEL_FCNC_FORBIDDEN_OR_UNPROVED",
            "reason": "No explicit action-backed off-diagonal neutral current permits tree-level b-s.",
        }
    return {"allowed": True, "status": "TREE_LEVEL_FCNC_THEOREM_PRESENT"}


def reject_loop_factor_without_provenance(loop_factor: str, provenance: str | None) -> dict[str, Any]:
    if provenance != "BHSM_ACTION_DERIVED_LOOP_OR_EQUIVALENT":
        return {
            "allowed": False,
            "status": "LOOP_FACTOR_PROVENANCE_REJECTED",
            "loop_factor": loop_factor,
            "reason": "A loop factor cannot be inserted from numerical resemblance or Standard Model memory.",
        }
    return {"allowed": True, "status": provenance}


def reject_symbolic_sum_as_nonzero_proof(candidate_expression: str | None, internal_response: str | None) -> dict[str, Any]:
    if not candidate_expression or not internal_response:
        return {
            "nonzero_established": False,
            "status": "NONZERO_TRANSITION_NOT_ESTABLISHED",
            "reason": "A symbolic sum without a derived internal response and cancellation law cannot prove a nonzero b -> s kernel.",
        }
    return {"nonzero_established": False, "status": "CONDITIONAL_NEEDS_WEIGHTED_RESPONSE_PROOF"}


def build_artifact_payloads(repo_root: Path | None = None) -> dict[str, dict[str, Any]]:
    _ = repo_root
    return {
        "neutral_current_flavor_structure_audit": neutral_current_flavor_structure_audit_artifact(),
        "charged_current_pair_composition": charged_current_pair_composition_artifact(),
        "intermediate_response_inventory": intermediate_response_inventory_artifact(),
        "fcnc_generation_candidate": fcnc_generation_candidate_artifact(),
        "gim_like_cancellation_audit": gim_like_cancellation_audit_artifact(),
        "dependency_graph": dependency_graph_artifact(),
        "verdict": verdict_artifact(),
    }


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def materialize_artifacts(root: Path) -> list[Path]:
    payloads = build_artifact_payloads(root)
    written: list[Path] = []
    for key, filename in ARTIFACT_FILES.items():
        path = root / "artifacts" / filename
        path.write_text(deterministic_json(payloads[key]), encoding="utf-8")
        written.append(path)
    return written


def rare_b_fcnc_generation_status_report(repo_root: Path | None = None) -> dict[str, Any]:
    payloads = build_artifact_payloads(repo_root)
    verdict = payloads["verdict"]
    graph = payloads["dependency_graph"]
    return {
        "report": "BHSM v5.3 rare-B FCNC generation-mechanism kill screen",
        "version": VERSION,
        "primary_verdict": verdict["primary_verdict"],
        "earliest_blocking_dependency": verdict["earliest_blocking_dependency"],
        "mechanism_layer_status": mechanism_layer_status(),
        "audit_answers": audit_answers(),
        "prediction_state": verdict["prediction_state"],
        "first_open_edge": graph["first_open_edge"],
        "artifacts": {key: f"artifacts/{filename}" for key, filename in ARTIFACT_FILES.items()},
        "preserved_statuses": list(PRESERVED_STATUSES),
        "new_or_refined_open_blockers": list(REFINED_OPEN_BLOCKERS),
        "claim_safe_conclusion": verdict["claim_safe_conclusion"],
        "recommended_next_sprint": verdict["recommended_next_sprint"],
    }


def rare_b_fcnc_generation_status_to_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# BHSM v5.3 Rare-B FCNC Generation-Mechanism Kill Screen",
        "",
        f"Primary verdict: `{report['primary_verdict']}`",
        f"Earliest blocking dependency: `{report['earliest_blocking_dependency']}`",
        "",
        "## Mechanism-Layer Status",
    ]
    for key, value in report["mechanism_layer_status"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Prediction State"])
    for key in ("prediction_claimed", "C7_BHSM", "C9_BHSM", "C10_BHSM", "q0_squared_value", "microplateau_node_coordinates"):
        lines.append(f"- `{key}`: `{report['prediction_state'][key]}`")
    lines.extend(["", "## Claim-Safe Conclusion", "", report["claim_safe_conclusion"], ""])
    return "\n".join(lines)
