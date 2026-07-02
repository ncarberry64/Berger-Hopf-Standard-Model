"""Audit attachment of the candidate quantum to the normalized gauge action."""

from .common import STATUS_ATTACHMENT, STATUS_VOLUME, STATUS_WEIGHTS, input_guard


def audit_gauge_coupling_action_attachment() -> dict[str, object]:
    return {
        "candidate_action": "S_gauge=k[Tr(F_cyc^2)+Tr(F_orient^2)+eta_Y F_Y^2]",
        "gauge_action_skeleton_status": "CONDITIONAL_NORMALIZED_WEAK_GAUGE_ACTION_SKELETON",
        "measure_status": "OPEN_MISSING_PHYSICAL_GAUGE_ACTION_MEASURE_NORMALIZATION",
        "trace_status": "CONDITIONAL_WEAK_GAUGE_TRACE_NORMALIZATION",
        "volume_denominator_status": STATUS_VOLUME,
        "sector_weight_status": STATUS_WEIGHTS,
        "coefficient_k_status": "OPEN_MISSING_NORMALIZED_WEAK_GAUGE_ACTION_COEFFICIENT",
        "does_action_attach_alpha_i": False,
        "does_action_fix_k": False,
        "evidence_for": ["a relative gauge kinetic skeleton and relative trace normalization exist"],
        "evidence_against": [
            "k is unfixed",
            "no action term attaches 1/(6*pi^2)",
            "no action term attaches weights 1,2,7",
        ],
        "status": STATUS_ATTACHMENT,
        "claim_boundary": "The pattern α_i = w_i/(6π²) is not an action derivation unless attached to the normalized gauge action.",
        **input_guard(),
    }
