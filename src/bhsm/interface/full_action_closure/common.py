"""Shared status contracts for the BHSM v4.0 full-action closure audit."""

from __future__ import annotations

from copy import deepcopy


REQUIRED_STATEMENTS = (
    "BHSM is not complete until the full action-normalization and scale gates close.",
    "The 1:2:7 gauge-coupling registry pattern is artifact-backed but not action-derived.",
    "The candidate denominator 6π² = 3 Vol(S³) is not a coupling derivation unless attached to the normalized gauge action.",
    "Sector weights do not derive gauge couplings without action attachment.",
    "The overall gauge-action coefficient k remains open unless fixed by the action.",
    "The CKM coefficient form is artifact-backed, but the CKM coefficient value remains open unless g2_BH is action-derived.",
    "The CKM exponent remains not derived unless all CKM action, transport, identification, and log-averaging gates close.",
    "Dimensionless neutral/PMNS structure does not imply physical neutrino masses.",
    "Physical Delta m², matter effects, radiative corrections, stiffness length, curvature, and unit normalization remain open unless separately derived.",
    "Full BHSM completion is not claimed by this repository unless every completion gate passes.",
)

INPUT_GUARD = {
    "empirical_inputs_used": False,
    "pdg_reference_values_used": False,
    "w_calibration_used": False,
    "charged_mass_fitting_used": False,
    "ckm_fitting_used": False,
    "neutrino_limits_used": False,
    "legacy_threshold_tables_used": False,
    "frozen_predictions_changed": False,
    "official_prediction_logic_changed": False,
}


def _gate(status: str, claim_boundary: str, evidence_for: list[str], evidence_against: list[str],
          dependencies: list[str], blocking_conditions: list[str], promoted_from: str | None = None,
          not_promoted_because: list[str] | None = None, **extra: object) -> dict[str, object]:
    return {
        "status": status,
        "claim_boundary": claim_boundary,
        "evidence_for": evidence_for,
        "evidence_against": evidence_against,
        "dependencies": dependencies,
        "blocking_conditions": blocking_conditions,
        "promoted_from": promoted_from,
        "not_promoted_because": not_promoted_because or blocking_conditions,
        **INPUT_GUARD,
        **extra,
    }


GATES: dict[str, dict[str, object]] = {
    "unified_action_skeleton": _gate(
        "CONDITIONAL_UNIFIED_ACTION_SKELETON",
        "The sector sum is an organizing skeleton, not a single derived local action with fixed coefficients.",
        ["compatible boundary, gauge, fermion, scalar, charged-current, neutral, and scale terms are inventoried"],
        ["no unique variational principle generates and normalizes every sector"],
        ["boundary measure", "sector actions", "scale/RG layer"],
        ["unified local action principle", "normalized common measure", "all sector coefficients"],
        candidate_action="S_BHSM = S_boundary_geometry + S_gauge + S_fermion + S_scalar/topographic + S_charged_current + S_neutral_response + S_scale/RG",
    ),
    "boundary_frame_averaging": _gate(
        "OPEN_MISSING_BOUNDARY_FRAME_AVERAGING",
        "Three frame directions and the S^3 volume identity do not establish a gauge-action averaging theorem.",
        ["BHSM boundary sources contain Hopf/frame and collar geometry"],
        ["no source attaches a three-direction S^3 average to the gauge trace density"],
        ["boundary measure", "gauge trace density", "frame selection"],
        ["action-selected three-frame sum", "normalized boundary measure", "gauge-action attachment"],
        candidate_formula="<X>_B = [3 Vol(S^3_unit)]^-1 sum_a int_S3 X_a dmu_B",
    ),
    "gauge_denominator_source": _gate(
        "OPEN_MISSING_GAUGE_COUPLING_VOLUME_DENOMINATOR",
        "The identity 6π² = 3 Vol(S³) is not enough; the action must use it as gauge trace-density normalization.",
        ["the registry uses 6*pi^2", "Vol(S^3_unit)=2*pi^2 is a standard geometric identity"],
        ["the normalized gauge action does not select 3 Vol(S^3_unit)"],
        ["boundary-frame averaging", "normalized boundary measure", "gauge action"],
        ["action attachment of the denominator"],
        promoted_from="OPEN_MISSING_GAUGE_COUPLING_VOLUME_DENOMINATOR",
        candidate_denominator="6*pi^2 = 3 Vol(S^3_unit)",
    ),
    "sector_weight_action_attachment": _gate(
        "OPEN_MISSING_GAUGE_SECTOR_WEIGHT_ACTION_SOURCE",
        "The conditional active-generator interpretation of 1:2:7 is not an action-selected trace weight.",
        ["the 1:2:7 registry pattern is artifact-backed", "active-generator counts provide a conditional interpretation"],
        ["no normalized gauge action weights sector traces by 1, 2, and 7"],
        ["finite algebra", "sector projectors", "gauge trace"],
        ["action-selected sector weights"],
        promoted_from="CONDITIONAL_GAUGE_SECTOR_WEIGHT_SOURCE",
        candidate_weights={"w1": 1, "w2": 2, "w3": 7},
    ),
    "gauge_action_coefficient_k": _gate(
        "OPEN_MISSING_GAUGE_ACTION_COEFFICIENT_K",
        "Canonical kinetic conventions cannot supply a numeric BHSM coupling without BHSM action normalization.",
        ["the candidate gauge skeleton contains an overall coefficient k"],
        ["k is not fixed by a normalized measure, finite trace, boundary volume, or variational theorem"],
        ["normalized gauge action", "boundary measure", "finite trace"],
        ["action-derived overall coefficient k"],
        candidate_k="unspecified",
    ),
    "alpha_i_action_gate": _gate(
        "OPEN_MISSING_ALPHA_I_ACTION_DERIVATION",
        "The artifact-backed alpha_i registry pattern is not an action derivation.",
        ["alpha_i = w_i/(6*pi^2) is registered with w=(1,2,7)"],
        ["denominator, weights, k, and action attachment do not all pass"],
        ["gauge denominator", "sector weights", "coefficient k", "gauge action attachment"],
        ["all four upstream gauge-normalization gates"],
        promoted_from="ARTIFACT_BACKED_GAUGE_COUPLING_REGISTRY_PATTERN",
        candidate_values={"alpha1": "1/(6*pi^2)", "alpha2": "2/(6*pi^2)", "alpha3": "7/(6*pi^2)"},
    ),
    "g2_action_gate": _gate(
        "OPEN_MISSING_G2_BH_ACTION_SOURCE",
        "The convention g2_BH^2/(4*pi)=alpha2 does not derive alpha2 or g2_BH.",
        ["the weak-coupling convention is conditional", "g2_BH exists as runtime/input provenance"],
        ["alpha2 is not action-derived"],
        ["alpha_i action derivation", "weak-coupling convention"],
        ["action-derived alpha2", "action-attached convention"],
        candidate_g2="2/sqrt(3*pi), conditional only",
    ),
    "ckm_completion_gate": _gate(
        "OPEN_MISSING_NORMALIZED_CKM_ACTION",
        "The CKM coefficient form does not imply its value, and neither implies the exponent.",
        ["C_CKM = g2_BH/sqrt(2) is artifact-backed", "projector, adjoint-pair, and transport candidates are inventoried"],
        ["g2_BH value, same-term measure attachment, CKM identification, and transport application remain open"],
        ["g2 action source", "CKM measure", "projector sandwich", "transport selection", "identification theorem", "log averaging"],
        ["normalized CKM action", "action-derived coefficient value", "all exponent gates"],
        coefficient_value_status="OPEN_MISSING_CKM_COEFFICIENT_VALUE_SOURCE",
        exponent_status="not_derived",
        candidate_coefficient="sqrt(2/(3*pi)), conditional only",
    ),
    "neutral_scale_gate": _gate(
        "OPEN_MISSING_NEUTRAL_SCALE",
        "Dimensionless neutral/PMNS structure does not imply a physical neutrino mass or Delta m^2.",
        ["dimensionless PMNS constraints and neutral response structures are available conditionally"],
        ["neutral action normalization, stiffness length, physical curvature, and unit anchor are missing"],
        ["neutral action normalization", "complete-action response cone", "dimensionful bridge"],
        ["physical neutral scale", "Delta m^2 scale", "matter and radiative dynamics"],
        promoted_from="CONDITIONAL_NEUTRAL_DIMENSIONLESS_STRUCTURE",
        action_normalization_status="OPEN_MISSING_NEUTRAL_ACTION_NORMALIZATION",
        candidate_neutral_scale="none",
    ),
    "scalar_topographic_gate": _gate(
        "OPEN_MISSING_SCALAR_TOPOGRAPHIC_ACTION_SOURCE",
        "Localized scalar/topographic scaffolds do not constitute a complete normalized collar action or decoupling theorem.",
        ["bulk, boundary, level-set, profile, and collar ingredients are localized"],
        ["collar measure, orientation, edge data, admissible variations, Robin coefficients, and physical scale remain open"],
        ["complete collar Lagrangian", "profile EOM", "boundary embedding", "physical scale"],
        ["complete scalar/topographic action", "decoupling theorem", "electroweak scale bridge"],
        decoupling_status="OPEN_MISSING_SCALAR_TOPOGRAPHIC_DECOUPLING",
        electroweak_scale_status="OPEN_MISSING_ELECTROWEAK_SCALE_BRIDGE",
    ),
    "dimensionful_scale_bridge": _gate(
        "DIMENSIONFUL_MASS_NOT_AVAILABLE",
        "A dimensionless theorem cannot be promoted into a dimensionful prediction without an action-derived scale bridge.",
        ["dimensionless geometric and mixing structures are separated from dynamic-layer physics"],
        ["no shared physical unit normalization, electroweak bridge, or neutral mass scale is derived"],
        ["neutral scale", "scalar/electroweak scale", "RG transport", "unit normalization"],
        ["action-derived physical scale bridge"],
        candidate_bridge="none",
    ),
    "full_completion_gate": _gate(
        "FULL_BHSM_NOT_COMPLETE",
        "Full BHSM completion is false unless every required action, normalization, scale, and transport gate passes.",
        ["several dimensionless structures and integrity gates are artifact-backed"],
        ["unified action, gauge normalization, CKM value/exponent, neutral scale, scalar decoupling, and RG/scale gates remain open"],
        ["all v4.0 theorem DAG terminal prerequisites"],
        ["every completion gate"],
        completion=False,
    ),
}


def build_gate(name: str) -> dict[str, object]:
    """Return a detached JSON-serializable gate payload."""

    return deepcopy(GATES[name])


def build_status_snapshot() -> dict[str, object]:
    return {
        "artifact_id": "BHSM_FULL_ACTION_STATUS_SNAPSHOT_V4_0",
        "status": "FULL_BHSM_NOT_COMPLETE",
        "claim_boundary": REQUIRED_STATEMENTS[0],
        "evidence_for": ["machine-readable cross-sector gate inventory"],
        "evidence_against": ["multiple terminal theorem gates remain open"],
        "dependencies": list(GATES),
        "blocking_conditions": [name for name, gate in GATES.items() if str(gate["status"]).startswith(("OPEN_", "DIMENSIONFUL_", "FULL_"))],
        "promoted_from": "BHSM v3.1 gauge audit plus neutrino bedrock doctrine",
        "not_promoted_because": ["full completion conjunction is false"],
        "gate_statuses": {name: gate["status"] for name, gate in GATES.items()},
        "required_statements": list(REQUIRED_STATEMENTS),
        **INPUT_GUARD,
    }
