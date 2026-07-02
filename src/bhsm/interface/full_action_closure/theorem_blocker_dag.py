"""Machine-readable dependency DAG for the v4.0 completion gate."""

from .common import INPUT_GUARD


def build_theorem_blocker_dag() -> dict[str, object]:
    statuses = {
        "unified_action_skeleton": "CONDITIONAL_UNIFIED_ACTION_SKELETON",
        "boundary_measure": "OPEN_MISSING_PHYSICAL_BOUNDARY_MEASURE_NORMALIZATION",
        "boundary_frame_averaging": "OPEN_MISSING_BOUNDARY_FRAME_AVERAGING",
        "s3_volume_denominator": "OPEN_MISSING_GAUGE_COUPLING_VOLUME_DENOMINATOR",
        "sector_weights": "OPEN_MISSING_GAUGE_SECTOR_WEIGHT_ACTION_SOURCE",
        "gauge_action_coefficient_k": "OPEN_MISSING_GAUGE_ACTION_COEFFICIENT_K",
        "alpha_i_derivation": "OPEN_MISSING_ALPHA_I_ACTION_DERIVATION",
        "g_i_derivation": "OPEN_MISSING_G2_BH_ACTION_SOURCE",
        "ckm_coefficient_form": "ARTIFACT_BACKED_CKM_COEFFICIENT_FORM",
        "ckm_coefficient_value": "OPEN_MISSING_CKM_COEFFICIENT_VALUE_SOURCE",
        "ckm_measure_attachment": "OPEN_MISSING_CKM_MEASURE_COEFFICIENT_ATTACHMENT",
        "ckm_projector_sandwich": "CONDITIONAL_NORMALIZED_PROJECTOR_SANDWICH",
        "ckm_transport_selection": "OPEN_MISSING_CKM_TRANSPORT_SELECTION",
        "ckm_exponent": "not_derived",
        "neutral_dimensionless_structure": "CONDITIONAL_NEUTRAL_DIMENSIONLESS_STRUCTURE",
        "neutral_action_normalization": "OPEN_MISSING_NEUTRAL_ACTION_NORMALIZATION",
        "neutral_scale": "OPEN_MISSING_NEUTRAL_SCALE",
        "dimensionful_mass_bridge": "DIMENSIONFUL_MASS_NOT_AVAILABLE",
        "scalar_topographic_action": "OPEN_MISSING_SCALAR_TOPOGRAPHIC_ACTION_SOURCE",
        "scalar_topographic_decoupling": "OPEN_MISSING_SCALAR_TOPOGRAPHIC_DECOUPLING",
        "rg_threshold_transport": "OPEN_MISSING_RG_THRESHOLD_TRANSPORT",
        "full_bhsm_completion": "FULL_BHSM_NOT_COMPLETE",
    }
    edges = [
        ("boundary_measure", "boundary_frame_averaging"),
        ("unified_action_skeleton", "boundary_frame_averaging"),
        ("boundary_frame_averaging", "s3_volume_denominator"),
        ("unified_action_skeleton", "sector_weights"),
        ("boundary_measure", "gauge_action_coefficient_k"),
        ("s3_volume_denominator", "alpha_i_derivation"),
        ("sector_weights", "alpha_i_derivation"),
        ("gauge_action_coefficient_k", "alpha_i_derivation"),
        ("alpha_i_derivation", "g_i_derivation"),
        ("g_i_derivation", "ckm_coefficient_value"),
        ("ckm_coefficient_form", "ckm_coefficient_value"),
        ("ckm_measure_attachment", "ckm_exponent"),
        ("ckm_projector_sandwich", "ckm_exponent"),
        ("ckm_transport_selection", "ckm_exponent"),
        ("ckm_coefficient_value", "ckm_exponent"),
        ("neutral_dimensionless_structure", "neutral_action_normalization"),
        ("neutral_action_normalization", "neutral_scale"),
        ("neutral_scale", "dimensionful_mass_bridge"),
        ("scalar_topographic_action", "scalar_topographic_decoupling"),
        ("scalar_topographic_action", "dimensionful_mass_bridge"),
        ("rg_threshold_transport", "dimensionful_mass_bridge"),
    ]
    terminal_inputs = [name for name in statuses if name != "full_bhsm_completion"]
    edges.extend((name, "full_bhsm_completion") for name in terminal_inputs)
    return {
        "artifact_id": "BHSM_FULL_THEOREM_BLOCKER_DAG_V4_0",
        "status": "FULL_BHSM_NOT_COMPLETE",
        "claim_boundary": "The DAG records dependencies; it does not promote conditional or open nodes.",
        "evidence_for": ["repository-traced v3.1, neutrino, CKM, scalar, and completion ledgers"],
        "evidence_against": ["the conjunction required for full completion is false"],
        "dependencies": terminal_inputs,
        "blocking_conditions": [name for name, status in statuses.items() if status.startswith(("OPEN_", "DIMENSIONFUL_", "FULL_")) or status == "not_derived"],
        "promoted_from": "existing sector-specific blocker ledgers",
        "not_promoted_because": ["terminal action-normalization and scale nodes remain open"],
        "nodes": [{"id": name, "status": status} for name, status in statuses.items()],
        "edges": [{"from": source, "to": target} for source, target in edges],
        **INPUT_GUARD,
    }
