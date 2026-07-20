"""Claim-safe b -> s mu+ mu- operator-matching kill screen for BHSM v5.2."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any


VERSION = "v5.2"
PRIMARY_VERDICT = "B_TO_S_MUMU_OPERATOR_MATCHING_BLOCKED"
EARLIEST_BLOCKER = "OPEN_MISSING_RARE_B_FCNC_GENERATION_MECHANISM"
CHANNEL = "b -> s mu+ mu-"
V5_1_VERDICT = "RARE_B_OBSERVABLE_MAP_INTERFACE_COMPLETE"

ARTIFACT_FILES = {
    "operator_source_inventory": "BHSM_rare_b_bhsm_operator_source_inventory_v5_2.json",
    "transition_dependency_graph": "BHSM_b_to_s_mumu_transition_dependency_graph_v5_2.json",
    "operator_matching_candidate": "BHSM_b_to_s_mumu_operator_matching_candidate_v5_2.json",
    "operator_matching_audit": "BHSM_b_to_s_mumu_operator_matching_audit_v5_2.json",
    "operator_matching_verdict": "BHSM_b_to_s_mumu_operator_matching_verdict_v5_2.json",
}

PRESERVED_STATUSES = (
    "ACTION_ATTACHMENT_BLOCKED",
    "CKM_RELATIVE_CURRENT_NORMALIZATION_BLOCKED",
    "COUPLING_BRIDGE_BLOCKED_PENDING_ACTION_PRINCIPLE",
    "RARE_B_AFB_ZERO_PREDICTION_BLOCKED",
    "RARE_B_MICROPLATEAU_NODE_PREDICTION_BLOCKED",
    V5_1_VERDICT,
)

PRESERVED_OPEN_GATES = (
    "OPEN_MISSING_B_TO_S_MUMU_TRANSITION_OPERATOR",
    "OPEN_MISSING_BHSM_TO_RARE_B_OPERATOR_MATCHING",
    "OPEN_MISSING_BHSM_WILSON_COEFFICIENT_DERIVATION",
    "OPEN_MISSING_BHSM_HADRONIC_MATRIX_ELEMENTS",
    "OPEN_MISSING_RARE_B_Q2_PHYSICAL_BRIDGE",
    "OPEN_MISSING_EXACT_MICROPLATEAU_NODE_MAP",
    "OPEN_MISSING_GAUGE_COUPLING_ACTION_ATTACHMENT",
    "OPEN_MISSING_ALPHA_I_ACTION_DERIVATION",
    "OPEN_MISSING_ALPHA2_ACTION_DERIVATION",
    "OPEN_MISSING_G2_BH_ACTION_SOURCE",
    "OPEN_MISSING_CKM_COEFFICIENT_VALUE_SOURCE",
    "CKM_EXPONENT_NOT_DERIVED",
    "FULL_BHSM_NOT_COMPLETE",
)

REFINED_OPEN_BLOCKERS = (
    "OPEN_MISSING_RARE_B_FCNC_GENERATION_MECHANISM",
    "OPEN_MISSING_NORMALIZED_B_TO_S_QUARK_CURRENT",
    "OPEN_MISSING_NORMALIZED_MUON_CURRENT_ATTACHMENT",
    "OPEN_MISSING_RARE_B_OPERATOR_CHIRALITY_MAP",
    "OPEN_MISSING_RARE_B_LOOP_MATCHING_PRINCIPLE",
    "OPEN_MISSING_RARE_B_OPERATOR_ACTION_NORMALIZATION",
    "OPEN_MISSING_RARE_B_OPERATOR_DIMENSIONFUL_BRIDGE",
    "OPEN_MISSING_RARE_B_RENORMALIZATION_SCALE_MAP",
)

FORBIDDEN_POSITIVE_CLAIMS = (
    "BHSM predicts the rare-B anomaly",
    "BHSM explains LHCb",
    "BHSM derives Wilson coefficients from CKM alone",
    "BHSM produces FCNCs automatically",
    "BHSM derives a loop factor from geometric resemblance",
    "BHSM derives g2_BH",
    "BHSM derives alpha_i",
    "BHSM derives the CKM coefficient value or exponent",
    "BHSM predicts q0^2",
    "BHSM predicts micro-plateaus",
    "BHSM falsifies continuous QFT",
    "BHSM is complete",
)

PREDICTION_GATE_ORDER = (
    "b_to_s_flavor_map_closed",
    "fcnc_generation_mechanism_closed",
    "quark_current_normalization_closed",
    "muon_current_normalization_closed",
    "lorentz_structure_closed",
    "chirality_map_closed",
    "action_attachment_closed",
    "loop_matching_closed",
    "dimensionful_scale_closed",
    "renormalization_map_closed",
    "wilson_matching_closed",
    "hadronic_inputs_closed",
    "afb_null_balance_closed",
    "q2_physical_bridge_closed",
    "no_fit_discipline_satisfied",
)


class ClaimStatus(str, Enum):
    DERIVED = "DERIVED"
    CONDITIONAL = "CONDITIONAL"
    CANDIDATE = "CANDIDATE"
    EXTERNAL_CONVENTION = "EXTERNAL_EFT_CONVENTION"
    BLOCKED = "BLOCKED"
    ABSENT = "ABSENT"


class OrderStatus(str, Enum):
    TREE_LEVEL_FORBIDDEN_OR_UNPROVED = "TREE_LEVEL_FCNC_FORBIDDEN_OR_UNPROVED"
    LOOP_OPEN = "LOOP_MATCHING_OPEN"
    EXTERNAL_CONVENTION = "EXTERNAL_CONVENTION"
    UNSPECIFIED = "UNSPECIFIED"


@dataclass(frozen=True)
class OperatorSourceEntry:
    artifact_or_symbol: str
    repository_location: str
    scientific_role: str
    input_space: str
    output_space: str
    units: str
    normalization: str
    action_attached: str
    flavor_changing: str
    lepton_coupled: str
    lorentz_structure: str
    chirality: str
    loop_order_status: str
    claim_status: str
    executable: bool
    documentation_only: bool
    usable_for_matching: bool
    blocking_reason: str

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
class CandidateOperator:
    name: str
    channel: str
    basis_convention: str
    initial_flavor_state: str | None
    final_flavor_state: str | None
    lepton_current: str | None
    lorentz_structure: str | None
    chirality: str | None
    coefficient_symbol: str | None
    coefficient_dimensions: str | None
    coefficient_provenance: str | None
    action_attachment_status: str
    fcnc_mechanism_status: str
    loop_order_status: str
    dimensionful_bridge_status: str
    renormalization_scale_status: str
    wilson_slot: str | None
    numerical_wilson_value: float | None
    prediction_claimed: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PredictionGateState:
    b_to_s_flavor_map_closed: bool = False
    fcnc_generation_mechanism_closed: bool = False
    quark_current_normalization_closed: bool = False
    muon_current_normalization_closed: bool = False
    lorentz_structure_closed: bool = False
    chirality_map_closed: bool = False
    action_attachment_closed: bool = False
    loop_matching_closed: bool = False
    dimensionful_scale_closed: bool = False
    renormalization_map_closed: bool = False
    wilson_matching_closed: bool = False
    hadronic_inputs_closed: bool = False
    afb_null_balance_closed: bool = True
    q2_physical_bridge_closed: bool = False
    no_fit_discipline_satisfied: bool = True

    def to_dict(self) -> dict[str, bool]:
        return asdict(self)


def _common_payload(artifact: str) -> dict[str, Any]:
    return {
        "artifact": artifact,
        "version": VERSION,
        "channel": CHANNEL,
        "primary_verdict": PRIMARY_VERDICT,
        "claim_boundary": (
            "Operator-matching kill screen only. BHSM v5.2 does not derive a "
            "physical b -> s mu+ mu- transition operator, Wilson coefficients, "
            "q0^2, or exact rare-B node coordinates."
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


def operator_source_inventory_entries() -> tuple[OperatorSourceEntry, ...]:
    return (
        OperatorSourceEntry(
            "CKM_no_fit_operator_output_v1",
            "artifacts/CKM_no_fit_operator_output_v1.json",
            "dimensionless flavor-mixing geometry",
            "BHSM flavor transport artifact",
            "CKM matrix/provenance adapter",
            "dimensionless",
            "relative only; no absolute current normalization",
            "no",
            "mixing geometry only; no explicit b -> s neutral transition",
            "no",
            "not an operator Lorentz structure",
            "not specified",
            "not an EFT matching calculation",
            ClaimStatus.CANDIDATE.value,
            True,
            False,
            False,
            "CKM matrix alone cannot close an FCNC semileptonic operator map",
        ),
        OperatorSourceEntry(
            "BHSM_rare_b_transition_operator_interface_v5_1",
            "artifacts/BHSM_rare_b_transition_operator_interface_v5_1.json",
            "external EFT operator-basis slots O7/O9/O10",
            "v5.1 observable-map interface",
            "basis slots and Wilson slots",
            "external convention",
            "not BHSM-normalized",
            "no",
            "interface names b -> s only; no BHSM mechanism",
            "external muon labels only",
            "dipole/vector/axial slots as convention",
            "external basis convention",
            "external convention, not BHSM loop derivation",
            ClaimStatus.EXTERNAL_CONVENTION.value,
            True,
            False,
            False,
            "basis compatibility is not a BHSM derivation",
        ),
        OperatorSourceEntry(
            "BHSM_rare_b_bhsm_matching_map_v5_1",
            "artifacts/BHSM_rare_b_bhsm_matching_map_v5_1.json",
            "open dependency graph for rare-B matching",
            "BHSM flavor/current/geometric dependencies",
            "open matching blockers",
            "mixed/open",
            "not closed",
            "no",
            "declares matching open",
            "not normalized",
            "not closed",
            "not closed",
            "open",
            ClaimStatus.BLOCKED.value,
            True,
            False,
            False,
            "records missing BHSM-to-rare-B operator matching",
        ),
        OperatorSourceEntry(
            "BHSM_charged_current_transport_space_audit_v2_6",
            "artifacts/BHSM_charged_current_transport_space_audit_v2_6.json",
            "charged-current transport-space audit",
            "charged-current target/interface evidence",
            "transport-space gates",
            "dimensionless/action units open",
            "normalized charged-current action term remains open",
            "no",
            "charged-current structure, not neutral FCNC",
            "no rare-B muon current attachment",
            "target/interface only",
            "not sufficient for rare-B chirality map",
            "not a rare-B loop calculation",
            ClaimStatus.CONDITIONAL.value,
            True,
            False,
            False,
            "charged-current target does not define b -> s mu+ mu- neutral semileptonic matching",
        ),
        OperatorSourceEntry(
            "BHSM_normalized_charged_current_action_term_v2_6",
            "artifacts/BHSM_normalized_charged_current_action_term_v2_6.json",
            "normalized charged-current action-term kill screen",
            "charged-current source search",
            "blocked action-term status",
            "dimensionless/action units open",
            "open",
            "no",
            "no FCNC",
            "no",
            "not an explicit rare-B operator",
            "not closed",
            "not a rare-B loop calculation",
            ClaimStatus.BLOCKED.value,
            True,
            False,
            False,
            "current normalization/action selection remains open",
        ),
        OperatorSourceEntry(
            "BHSM_ckm_relative_current_normalization_killscreen_v4_8",
            "artifacts/BHSM_ckm_relative_current_normalization_killscreen_v4_8.json",
            "CKM-relative current-normalization blocker",
            "CKM relative geometry",
            "blocked current normalization",
            "dimensionless",
            "c_rel^2=4*pi not derived",
            "no",
            "does not supply FCNC",
            "no",
            "not an operator",
            "not specified",
            "not applicable",
            ClaimStatus.BLOCKED.value,
            True,
            False,
            False,
            "relative CKM geometry does not fix absolute current normalization",
        ),
        OperatorSourceEntry(
            "BHSM_gauge_coupling_action_attachment_killscreen_v4_7",
            "artifacts/BHSM_gauge_coupling_action_attachment_killscreen_v4_7.json",
            "gauge-coupling action-attachment blocker",
            "spectral/gauge coupling candidates",
            "blocked physical coupling attachment",
            "dimensionless candidates only",
            "lambda_i to alpha_i not derived",
            "no",
            "no flavor transition",
            "no",
            "not an EFT operator",
            "not specified",
            "not a loop matching theorem",
            ClaimStatus.BLOCKED.value,
            True,
            False,
            False,
            "physical gauge/current coefficient cannot be imported as derived",
        ),
        OperatorSourceEntry(
            "BHSM_coupling_bridge_blocker_consolidation_v4_9",
            "artifacts/BHSM_coupling_bridge_blocker_consolidation_v4_9.json",
            "consolidated coupling/current blocker",
            "v4.5-v4.8 bridge attempts",
            "blocked coupling bridge",
            "dimensionless",
            "direct action and CKM-relative bridges both blocked",
            "no",
            "no FCNC mechanism",
            "no",
            "not an EFT operator",
            "not specified",
            "not a loop matching theorem",
            ClaimStatus.BLOCKED.value,
            True,
            False,
            False,
            "no action/current principle closes physical coupling normalization",
        ),
        OperatorSourceEntry(
            "BHSM_sector_boundary_operator_v4_6",
            "artifacts/BHSM_sector_boundary_operator_v4_6.json",
            "conditional boundary gauge kinetic operator candidate",
            "adjoint-valued boundary one-forms",
            "conditional Laplace-type operator class",
            "dimensionless/operator class",
            "operator action source and alpha_i identification open",
            "no",
            "no flavor transition",
            "no",
            "gauge one-form, not semileptonic four-fermion operator",
            "not specified",
            "not a rare-B loop calculation",
            ClaimStatus.CONDITIONAL.value,
            True,
            False,
            False,
            "boundary kinetic candidate does not provide b -> s semileptonic matching",
        ),
        OperatorSourceEntry(
            "BHSM_neutral_action_closure_report_v1_5",
            "artifacts/BHSM_neutral_action_closure_report_v1_5.json",
            "neutral response/action support audit",
            "neutral response cone and stiffness candidates",
            "conditional neutral action closure report",
            "dimensionless/neutral-scale open",
            "neutral action normalization open",
            "no",
            "generic neutral response only; no flavor-changing b -> s theorem",
            "no rare-B muon current attachment",
            "not an EFT semileptonic operator",
            "not specified",
            "not a rare-B loop calculation",
            ClaimStatus.CONDITIONAL.value,
            True,
            False,
            False,
            "generic neutral response does not automatically generate FCNC",
        ),
        OperatorSourceEntry(
            "BHSM_chiral_current_attachment_map_v0_6",
            "artifacts/BHSM_chiral_current_attachment_map_v0_6.json",
            "chiral current attachment map for handoff targets",
            "bounded collider-interface source map",
            "target current labels",
            "external/interface units",
            "not an action-normalized rare-B coefficient",
            "no",
            "CKM/PMNS charged-current target context only",
            "not a normalized muon current for rare-B",
            "target convention",
            "partial/interface only",
            "not a rare-B loop calculation",
            ClaimStatus.CANDIDATE.value,
            True,
            False,
            False,
            "does not derive FCNC or normalized muon current attachment",
        ),
        OperatorSourceEntry(
            "CMS dimuon benchmark/animation sources",
            "src/bhsm/interface/benchmarks/cern_open_data.py; docs/assets/pr98_cms_open_data_animation/",
            "published CMS muon four-vector coordinate benchmark",
            "external collision-derived four-vectors",
            "coordinate-engine validation",
            "GeV four-vector components from source data",
            "benchmark normalization only",
            "no",
            "no",
            "external muon kinematics only",
            "not a field-theory current",
            "not specified",
            "not an EFT matching calculation",
            ClaimStatus.EXTERNAL_CONVENTION.value,
            True,
            False,
            False,
            "external muon data are not BHSM muon-current derivation or rare-B fitting input",
        ),
    )


def transition_dependency_edges() -> tuple[DependencyEdge, ...]:
    return (
        DependencyEdge(
            "BHSM flavor geometry",
            "CKM/relative transport",
            "load artifact-backed CKM geometry",
            "ARTIFACT_BACKED_INPUT_ONLY",
            "artifacts/CKM_no_fit_operator_output_v1.json",
            "dimensionless -> dimensionless",
            "none; relative geometry only",
            "OPEN_MISSING_NORMALIZED_B_TO_S_QUARK_CURRENT",
        ),
        DependencyEdge(
            "CKM/relative transport",
            "b -> s flavor selector",
            "select rare-B flavor transition",
            "OPEN",
            "v5.1 dependency graph; v5.2 audit",
            "dimensionless -> dimensionless",
            "absolute current normalization absent",
            "OPEN_MISSING_NORMALIZED_B_TO_S_QUARK_CURRENT",
        ),
        DependencyEdge(
            "b -> s flavor selector",
            "FCNC generation mechanism",
            "generate neutral semileptonic flavor change",
            "BLOCKED",
            "v5.2 kill screen",
            "none closed",
            "none closed",
            EARLIEST_BLOCKER,
        ),
        DependencyEdge(
            "FCNC generation mechanism",
            "quark current",
            "construct b-to-s quark bilinear",
            "BLOCKED",
            "v5.2 kill screen",
            "not available",
            "not available",
            "OPEN_MISSING_NORMALIZED_B_TO_S_QUARK_CURRENT",
        ),
        DependencyEdge(
            "quark current",
            "muon current",
            "attach semileptonic lepton current",
            "BLOCKED",
            "v5.2 kill screen",
            "not available",
            "not available",
            "OPEN_MISSING_NORMALIZED_MUON_CURRENT_ATTACHMENT",
        ),
        DependencyEdge(
            "muon current",
            "Lorentz/chirality structure",
            "select vector/axial/dipole/chiral tensor type",
            "BLOCKED",
            "external EFT slots exist in v5.1; BHSM derivation absent",
            "external convention only",
            "not BHSM-normalized",
            "OPEN_MISSING_RARE_B_OPERATOR_CHIRALITY_MAP",
        ),
        DependencyEdge(
            "Lorentz/chirality structure",
            "action normalization",
            "attach operator coefficient to normalized action",
            "BLOCKED",
            "v4.7-v4.9 blockers",
            "not available",
            "not available",
            "OPEN_MISSING_RARE_B_OPERATOR_ACTION_NORMALIZATION",
        ),
        DependencyEdge(
            "action normalization",
            "gauge/current coefficient",
            "derive coefficient provenance",
            "BLOCKED",
            "v4.7 action attachment and v4.8 current normalization blockers",
            "not available",
            "lambda_i, alpha_i, g2_BH not derived",
            "OPEN_MISSING_GAUGE_COUPLING_ACTION_ATTACHMENT",
        ),
        DependencyEdge(
            "gauge/current coefficient",
            "loop/order matching",
            "derive tree/loop matching order and factors",
            "BLOCKED",
            "v5.2 kill screen",
            "not available",
            "not available",
            "OPEN_MISSING_RARE_B_LOOP_MATCHING_PRINCIPLE",
        ),
        DependencyEdge(
            "loop/order matching",
            "dimensionful scale",
            "map geometric quantities to effective-Hamiltonian dimensions",
            "BLOCKED",
            "v5.1 q^2 bridge and neutral/unit blockers",
            "dimensionless -> physical units not closed",
            "not available",
            "OPEN_MISSING_RARE_B_OPERATOR_DIMENSIONFUL_BRIDGE",
        ),
        DependencyEdge(
            "dimensionful scale",
            "renormalization scale",
            "define mu-dependent matching",
            "BLOCKED",
            "v5.2 kill screen",
            "not available",
            "not available",
            "OPEN_MISSING_RARE_B_RENORMALIZATION_SCALE_MAP",
        ),
        DependencyEdge(
            "renormalization scale",
            "operator-basis projection",
            "project into O7/O9/O10 or equivalent",
            "BLOCKED",
            "v5.1 external interface only",
            "external convention only",
            "not BHSM-normalized",
            "OPEN_MISSING_BHSM_TO_RARE_B_OPERATOR_MATCHING",
        ),
        DependencyEdge(
            "operator-basis projection",
            "Wilson-coefficient slot",
            "populate C7/C9/C10 slots",
            "BLOCKED",
            "v5.1 Wilson slots",
            "not available",
            "not available",
            "OPEN_MISSING_BHSM_WILSON_COEFFICIENT_DERIVATION",
        ),
        DependencyEdge(
            "Wilson-coefficient slot",
            "v5.1 observable map",
            "feed observable interface",
            "BLOCKED_DOWNSTREAM",
            "artifacts/BHSM_rare_b_observable_map_scaffold_verdict_v5_1.json",
            "external observable units remain open",
            "hadronic and q^2 gates open",
            "RARE_B_AFB_ZERO_PREDICTION_BLOCKED",
        ),
    )


def audit_answers() -> dict[str, bool]:
    return {
        "explicit_b_to_s_flavor_transition_exists": False,
        "explicit_bhsm_fcnc_mechanism_exists": False,
        "explicit_normalized_quark_current_exists": False,
        "explicit_normalized_muon_current_exists": False,
        "explicit_lorentz_structure_exists": False,
        "explicit_chirality_structure_exists": False,
        "action_attached_coefficient_exists": False,
        "loop_order_mechanism_exists": False,
        "dimensionful_coefficient_bridge_exists": False,
        "renormalization_scale_map_exists": False,
        "projection_into_O7_exists": False,
        "projection_into_O9_exists": False,
        "projection_into_O10_exists": False,
        "equivalent_basis_independent_map_exists": False,
        "numerical_wilson_coefficients_exist": False,
        "connection_to_v5_1_interface_exists": True,
    }


def prediction_kill_screen(gates: PredictionGateState | None = None) -> dict[str, Any]:
    gates = gates or PredictionGateState()
    gate_dict = gates.to_dict()
    missing = [name for name in PREDICTION_GATE_ORDER if not gate_dict[name]]
    return {
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
        "no_fit_discipline_preserved": gates.no_fit_discipline_satisfied,
        "all_required_gates_closed": not missing,
        "blocking_gates": missing,
        "rejection_reason": "No transition operator, no Wilson map. No Wilson map, no rare-B prediction.",
    }


def validate_candidate_operator(candidate: CandidateOperator) -> CandidateOperator:
    if not candidate.initial_flavor_state or not candidate.final_flavor_state:
        raise ValueError("candidate operator requires explicit initial and final flavor states")
    if candidate.fcnc_mechanism_status in {"ABSENT", "OPEN", EARLIEST_BLOCKER}:
        raise ValueError("candidate operator requires a closed FCNC generation mechanism")
    if not candidate.lepton_current:
        raise ValueError("candidate operator requires an explicit lepton-current structure")
    if not candidate.lorentz_structure:
        raise ValueError("candidate operator requires explicit Lorentz structure")
    if not candidate.chirality:
        raise ValueError("candidate operator requires explicit chirality metadata")
    if not candidate.coefficient_dimensions:
        raise ValueError("candidate coefficient requires dimensions")
    if not candidate.coefficient_provenance:
        raise ValueError("candidate coefficient requires provenance")
    if candidate.coefficient_provenance == "BHSM-derived" and "OPEN" in candidate.action_attachment_status:
        raise ValueError("external/open coefficient cannot be labeled BHSM-derived")
    if candidate.numerical_wilson_value is not None and (
        "OPEN" in candidate.loop_order_status
        or "OPEN" in candidate.dimensionful_bridge_status
        or "OPEN" in candidate.renormalization_scale_status
    ):
        raise ValueError("numerical Wilson output is forbidden while matching gates remain open")
    if candidate.action_attachment_status == "ACTION_NORMALIZED" and "BLOCKED" in candidate.fcnc_mechanism_status:
        raise ValueError("action-normalized status cannot coexist with blocked FCNC mechanism")
    return candidate


def reject_tree_level_fcnc_without_theorem(theorem_status: str) -> dict[str, Any]:
    if theorem_status not in {"DERIVED", "ARTIFACT_BACKED_DERIVED"}:
        return {
            "allowed": False,
            "status": OrderStatus.TREE_LEVEL_FORBIDDEN_OR_UNPROVED.value,
            "reason": "No artifact-backed theorem permits a tree-level b-s neutral current.",
        }
    return {"allowed": True, "status": "TREE_LEVEL_FCNC_THEOREM_PRESENT"}


def reject_geometric_loop_factor_identification(source: str, provenance: str) -> dict[str, Any]:
    if provenance not in {"DERIVED", "EXTERNAL_EFT_CONVENTION"}:
        return {
            "allowed": False,
            "status": "LOOP_FACTOR_IDENTIFICATION_REJECTED",
            "source": source,
            "reason": "Numerical resemblance to a loop factor is not a derivation.",
        }
    return {"allowed": True, "status": provenance}


def operator_source_inventory_artifact(repo_root: Path | None = None) -> dict[str, Any]:
    payload = _common_payload("BHSM_rare_b_bhsm_operator_source_inventory_v5_2")
    payload.update(
        {
            "status": "RARE_B_OPERATOR_SOURCE_INVENTORY_ARTIFACTED",
            "entries": [entry.to_dict() for entry in operator_source_inventory_entries()],
            "repository_scan_summary": repository_scan_summary(repo_root),
            "inventory_verdict": "No inventoried BHSM source supplies a normalized b -> s mu+ mu- FCNC operator.",
        }
    )
    return payload


def transition_dependency_graph_artifact() -> dict[str, Any]:
    payload = _common_payload("BHSM_b_to_s_mumu_transition_dependency_graph_v5_2")
    payload.update(
        {
            "status": "B_TO_S_MUMU_TRANSITION_DEPENDENCY_GRAPH_ARTIFACTED",
            "nodes": [
                "BHSM flavor geometry",
                "CKM/relative transport",
                "b -> s flavor selector",
                "FCNC generation mechanism",
                "quark current",
                "muon current",
                "Lorentz/chirality structure",
                "action normalization",
                "gauge/current coefficient",
                "loop/order matching",
                "dimensionful scale",
                "renormalization scale",
                "operator-basis projection",
                "Wilson-coefficient slot",
                "v5.1 observable map",
            ],
            "edges": [edge.to_dict() for edge in transition_dependency_edges()],
            "first_open_edge": {
                "source": "b -> s flavor selector",
                "target": "FCNC generation mechanism",
                "blocking_dependency": EARLIEST_BLOCKER,
            },
        }
    )
    return payload


def operator_matching_candidate_artifact() -> dict[str, Any]:
    payload = _common_payload("BHSM_b_to_s_mumu_operator_matching_candidate_v5_2")
    payload.update(
        {
            "status": "B_TO_S_MUMU_OPERATOR_MATCHING_CANDIDATE_EMPTY_BLOCKED",
            "basis_convention": "external EFT O7/O9/O10 slots exist in v5.1; BHSM projection absent",
            "candidate_operators": [],
            "external_operator_patterns_not_derived": [
                {
                    "slot": "O7",
                    "pattern": "(sbar sigma_mu_nu P_R b) F^mu_nu",
                    "status": "EXTERNAL_EFT_CONVENTION_NOT_BHSM_DERIVATION",
                    "C7_BHSM": None,
                },
                {
                    "slot": "O9",
                    "pattern": "(sbar gamma_mu P_L b)(mubar gamma^mu mu)",
                    "status": "EXTERNAL_EFT_CONVENTION_NOT_BHSM_DERIVATION",
                    "C9_BHSM": None,
                },
                {
                    "slot": "O10",
                    "pattern": "(sbar gamma_mu P_L b)(mubar gamma^mu gamma5 mu)",
                    "status": "EXTERNAL_EFT_CONVENTION_NOT_BHSM_DERIVATION",
                    "C10_BHSM": None,
                },
            ],
            "bhsm_source_objects": [entry.artifact_or_symbol for entry in operator_source_inventory_entries()],
            "flavor_mechanism": EARLIEST_BLOCKER,
            "lepton_current_map": "OPEN_MISSING_NORMALIZED_MUON_CURRENT_ATTACHMENT",
            "lorentz_structure": "ABSENT_FOR_BHSM_DERIVED_OPERATOR",
            "chirality": "ABSENT_FOR_BHSM_DERIVED_OPERATOR",
            "normalization": {
                "expression": None,
                "status": "OPEN_MISSING_RARE_B_OPERATOR_ACTION_NORMALIZATION",
            },
            "action_attachment": "ACTION_ATTACHMENT_BLOCKED",
            "loop_order": "OPEN_MISSING_RARE_B_LOOP_MATCHING_PRINCIPLE",
            "physical_dimensions": {
                "operator_dimension": None,
                "coefficient_dimension": None,
                "status": "OPEN_MISSING_RARE_B_OPERATOR_DIMENSIONFUL_BRIDGE",
            },
            "scale_dependence": "OPEN_MISSING_RARE_B_RENORMALIZATION_SCALE_MAP",
            "wilson_mapping": "ABSENT_BHSM_DERIVATION",
            "numerical_wilson_values": {
                "C7_BHSM": None,
                "C9_BHSM": None,
                "C10_BHSM": None,
                "delta_C7_BHSM": None,
                "delta_C9_BHSM": None,
                "delta_C10_BHSM": None,
            },
            "prediction_claimed": False,
        }
    )
    return payload


def operator_matching_audit_artifact(repo_root: Path | None = None) -> dict[str, Any]:
    payload = _common_payload("BHSM_b_to_s_mumu_operator_matching_audit_v5_2")
    payload.update(
        {
            "status": "B_TO_S_MUMU_OPERATOR_MATCHING_AUDIT_ARTIFACTED",
            "audit_answers": audit_answers(),
            "kill_screens": {
                "flavor_changing_neutral_current": {
                    "status": EARLIEST_BLOCKER,
                    "tree_level_fcnc": reject_tree_level_fcnc_without_theorem("OPEN"),
                    "generic_neutral_current_is_sufficient": False,
                },
                "lepton_current": {
                    "normalized_muon_current_exists": False,
                    "status": "OPEN_MISSING_NORMALIZED_MUON_CURRENT_ATTACHMENT",
                },
                "lorentz_and_chirality": {
                    "lorentz_structure_closed": False,
                    "chirality_map_closed": False,
                    "status": "OPEN_MISSING_RARE_B_OPERATOR_CHIRALITY_MAP",
                },
                "action_normalization": {
                    "lambda_i_equals_alpha_i_derived": False,
                    "alpha2_equals_lambda2_derived": False,
                    "c_rel_squared_equals_4pi_derived": False,
                    "g2_BH_derived": False,
                    "status": "OPEN_MISSING_RARE_B_OPERATOR_ACTION_NORMALIZATION",
                },
                "loop_order": {
                    "loop_generating_mechanism": "OPEN",
                    "geometric_loop_factor_rejection": reject_geometric_loop_factor_identification("1/(16*pi^2)", "OPEN"),
                },
                "dimension_and_scale": {
                    "dimensionful_coefficient_bridge_exists": False,
                    "renormalization_scale_map_exists": False,
                    "q2_physical_bridge": "OPEN_MISSING_RARE_B_Q2_PHYSICAL_BRIDGE",
                },
                "wilson_coefficients": {
                    "C7_BHSM": None,
                    "C9_BHSM": None,
                    "C10_BHSM": None,
                    "delta_C7_BHSM": None,
                    "delta_C9_BHSM": None,
                    "delta_C10_BHSM": None,
                },
            },
            "repository_scan_summary": repository_scan_summary(repo_root),
        }
    )
    return payload


def operator_matching_verdict_artifact(repo_root: Path | None = None) -> dict[str, Any]:
    payload = _common_payload("BHSM_b_to_s_mumu_operator_matching_verdict_v5_2")
    payload.update(
        {
            "primary_verdict": PRIMARY_VERDICT,
            "earliest_blocking_dependency": EARLIEST_BLOCKER,
            "validated_structures": [
                "v5.1 rare-B observable-map interface remains machine-readable",
                "external O7/O9/O10 operator slots are available as convention slots",
                "CKM geometry is artifact-backed as relative flavor input",
                "operator-layer dependency graph is explicit",
                "prediction kill screen emits no Wilson, q0^2, or node values",
            ],
            "invalidated_candidate_identifications": [
                "CKM geometry alone is not a b -> s mu+ mu- transition operator",
                "generic neutral response is not an FCNC generation theorem",
                "external O7/O9/O10 compatibility is not a BHSM derivation",
                "tree-level b-s neutral current is forbidden or unproved without a theorem",
                "geometric factors are not loop factors by numerical resemblance",
            ],
            "still_open": list(REFINED_OPEN_BLOCKERS + PRESERVED_OPEN_GATES),
            "preserved_historical_blockers": list(PRESERVED_STATUSES),
            "new_blockers": list(REFINED_OPEN_BLOCKERS),
            "prediction_kill_screen": prediction_kill_screen(),
            "audit_answers": audit_answers(),
            "v5_1_interface_verdict_preserved": V5_1_VERDICT,
            "wilson_values_emitted": False,
            "recommended_next_sprint": "bhsm-rare-b-fcnc-generation-mechanism-v5-3",
            "claim_safe_conclusion": (
                "BHSM v5.2 does not derive a physical b -> s mu+ mu- transition operator. "
                "The kill screen identifies the earliest missing matching dependency while preserving "
                "the v5.1 observable-map interface. Numerical Wilson coefficients, q0^2, and exact "
                "node positions remain absent, and prediction claimed remains no."
            ),
        }
    )
    return payload


def repository_scan_summary(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[3]
    terms = (
        "b -> s",
        "mumu",
        "muon current",
        "rare-B",
        "FCNC",
        "flavor changing neutral current",
        "neutral current",
        "charged current",
        "CKM",
        "V_tb",
        "V_ts",
        "O7",
        "O9",
        "O10",
        "C7",
        "C9",
        "C10",
        "chirality",
        "gamma5",
        "loop",
        "penguin",
        "box",
        "Wilson",
        "renormalization",
        "action coefficient",
        "neutral response",
    )
    paths = _iter_scan_paths(root)
    findings: list[dict[str, Any]] = []
    for path in paths:
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        relative = str(path.relative_to(root)).replace("\\", "/")
        for term in terms:
            first: tuple[int, str] | None = None
            count = 0
            term_lower = term.lower()
            for line_no, line in enumerate(lines, 1):
                if term_lower in line.lower():
                    count += 1
                    if first is None:
                        first = (line_no, line)
            if first:
                line_no, line = first
                findings.append(
                    {
                        "search_term": term,
                        "file": relative,
                        "line": line_no,
                        "match_count_in_file": count,
                        "matched_content_summary": _summarize_line(line),
                        "classification": _classify_scan_line(line),
                    }
                )
    return {
        "scan_scope": [
            "src/",
            "tests/",
            "artifacts/",
            "docs/",
            "scripts/",
            "manuscript/",
            "CLAIMS.md",
            "STATUS.md",
            "ARTIFACT_INDEX.md",
            "README.md",
            "ROADMAP.md",
        ],
        "terms": list(terms),
        "finding_policy": "one summarized finding per search term per file",
        "findings": sorted(findings, key=lambda row: (row["file"], row["search_term"], row["line"])),
        "scan_verdict": "No scanned repository object closes the BHSM FCNC, normalized muon-current, action-normalization, loop, dimension, or Wilson gates.",
    }


def _iter_scan_paths(root: Path) -> list[Path]:
    roots = [root / name for name in ("src", "tests", "artifacts", "docs", "scripts", "manuscript")]
    direct = [root / name for name in ("CLAIMS.md", "STATUS.md", "ARTIFACT_INDEX.md", "README.md", "ROADMAP.md")]
    suffixes = {".py", ".md", ".json", ".txt", ".yml", ".yaml", ".toml", ".cff"}
    paths: list[Path] = []
    for scan_root in roots:
        if not scan_root.exists():
            continue
        for path in scan_root.rglob("*"):
            if path.name in ARTIFACT_FILES.values():
                continue
            if path.is_file() and path.suffix.lower() in suffixes:
                paths.append(path)
    paths.extend(path for path in direct if path.exists())
    return sorted(set(paths))


def _classify_scan_line(line: str) -> str:
    lowered = line.lower()
    if "open_missing" in lowered or "blocked" in lowered:
        return "open_or_blocked_status_context"
    if "v5.1" in lowered or "interface" in lowered:
        return "interface_context"
    if "ckm" in lowered:
        return "ckm_or_flavor_geometry_context"
    if "muon" in lowered or "dimuon" in lowered:
        return "external_muon_or_benchmark_context"
    return "search_context"


def _summarize_line(line: str) -> str:
    summary = line.strip()[:220]
    if any(phrase in summary for phrase in FORBIDDEN_POSITIVE_CLAIMS):
        return "[redacted forbidden-claim fixture or no-go phrase]"
    return summary


def build_artifact_payloads(repo_root: Path | None = None) -> dict[str, dict[str, Any]]:
    return {
        "operator_source_inventory": operator_source_inventory_artifact(repo_root),
        "transition_dependency_graph": transition_dependency_graph_artifact(),
        "operator_matching_candidate": operator_matching_candidate_artifact(),
        "operator_matching_audit": operator_matching_audit_artifact(repo_root),
        "operator_matching_verdict": operator_matching_verdict_artifact(repo_root),
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


def b_to_s_mumu_status_report(repo_root: Path | None = None) -> dict[str, Any]:
    payloads = build_artifact_payloads(repo_root)
    verdict = payloads["operator_matching_verdict"]
    candidate = payloads["operator_matching_candidate"]
    graph = payloads["transition_dependency_graph"]
    return {
        "report": "BHSM v5.2 b -> s mu+ mu- operator-matching kill screen",
        "version": VERSION,
        "primary_verdict": verdict["primary_verdict"],
        "earliest_blocking_dependency": verdict["earliest_blocking_dependency"],
        "operator_layer_status": operator_layer_status(),
        "audit_answers": audit_answers(),
        "prediction_state": verdict["prediction_kill_screen"],
        "candidate_operator_count": len(candidate["candidate_operators"]),
        "first_open_edge": graph["first_open_edge"],
        "artifacts": {key: f"artifacts/{filename}" for key, filename in ARTIFACT_FILES.items()},
        "preserved_statuses": list(PRESERVED_STATUSES),
        "new_or_refined_open_blockers": list(REFINED_OPEN_BLOCKERS),
        "claim_safe_conclusion": verdict["claim_safe_conclusion"],
    }


def operator_layer_status() -> dict[str, str]:
    return {
        "BHSM flavor-transition selector": "OPEN_MISSING_NORMALIZED_B_TO_S_QUARK_CURRENT",
        "FCNC generation mechanism": EARLIEST_BLOCKER,
        "Quark-current construction": "OPEN_MISSING_NORMALIZED_B_TO_S_QUARK_CURRENT",
        "Muon-current construction": "OPEN_MISSING_NORMALIZED_MUON_CURRENT_ATTACHMENT",
        "Lorentz structure": "ABSENT_FOR_BHSM_DERIVED_OPERATOR",
        "Chirality structure": "OPEN_MISSING_RARE_B_OPERATOR_CHIRALITY_MAP",
        "Action normalization": "OPEN_MISSING_RARE_B_OPERATOR_ACTION_NORMALIZATION",
        "Gauge/current coefficient": "OPEN_MISSING_GAUGE_COUPLING_ACTION_ATTACHMENT",
        "Loop/order matching": "OPEN_MISSING_RARE_B_LOOP_MATCHING_PRINCIPLE",
        "Dimensionful coefficient bridge": "OPEN_MISSING_RARE_B_OPERATOR_DIMENSIONFUL_BRIDGE",
        "Renormalization-scale map": "OPEN_MISSING_RARE_B_RENORMALIZATION_SCALE_MAP",
        "O7 projection": "ABSENT_BHSM_DERIVATION",
        "O9 projection": "ABSENT_BHSM_DERIVATION",
        "O10 projection": "ABSENT_BHSM_DERIVATION",
        "Basis-independent equivalent": "ABSENT_BHSM_DERIVATION",
        "v5.1 interface connection": V5_1_VERDICT,
    }


def b_to_s_mumu_status_to_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# BHSM v5.2 b -> s mu+ mu- Operator-Matching Kill Screen",
        "",
        f"Primary verdict: `{report['primary_verdict']}`",
        f"Earliest blocking dependency: `{report['earliest_blocking_dependency']}`",
        "",
        "## Operator-Layer Status",
    ]
    for key, value in report["operator_layer_status"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Prediction State"])
    for key in ("prediction_claimed", "C7_BHSM", "C9_BHSM", "C10_BHSM", "q0_squared_value", "microplateau_node_coordinates"):
        lines.append(f"- `{key}`: `{report['prediction_state'][key]}`")
    lines.extend(["", "## Claim-Safe Conclusion", "", report["claim_safe_conclusion"], ""])
    return "\n".join(lines)
