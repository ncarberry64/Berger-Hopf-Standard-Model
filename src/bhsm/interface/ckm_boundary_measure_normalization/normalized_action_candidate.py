"""Combine the normalization gates."""

from .common import CANDIDATE_FORM, STATUS_ACTION, STATUS_COEFFICIENT, STATUS_MEASURE, STATUS_PAIRED, STATUS_PROJECTOR, input_guard


def audit_normalized_ckm_action_candidate() -> dict[str, object]:
    blockers = ["normalized CKM-term measure", "fixed geometric C_CKM", "projector sandwich", "paired normalization", "variational/action provenance"]
    return {
        "audit": "normalized_ckm_action_candidate",
        "bounded_interface_status": "ARTIFACT_BACKED_BOUNDED_CKM_INTERFACE_TERM",
        "measure_status": STATUS_MEASURE,
        "coefficient_status": STATUS_COEFFICIENT,
        "projector_status": STATUS_PROJECTOR,
        "paired_normalization_status": STATUS_PAIRED,
        "variational_provenance_status": "open_missing_ckm_variational_provenance",
        "candidate_action_form": CANDIDATE_FORM,
        "promotion_status": "not_promoted",
        "blocking_conditions": blockers,
        "status": STATUS_ACTION,
        "claim_boundary": "L_CKM_charged_current_bounded remains an interface term until every normalization and action-provenance gate closes.",
        **input_guard(),
    }
