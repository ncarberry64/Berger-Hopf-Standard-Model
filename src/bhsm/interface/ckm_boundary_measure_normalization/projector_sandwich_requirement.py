"""Audit projector attachment to the CKM term."""

from .common import CANDIDATE_FORM, STATUS_PROJECTOR, input_guard


def audit_projector_sandwich_requirement() -> dict[str, object]:
    return {
        "audit": "ckm_projector_sandwich_requirement",
        "projector_sources": ["artifacts/BHSM_projector_reduction_audit_v2_0.json"],
        "Pi_u_source": None,
        "Pi_d_source": None,
        "domain_codomain_sources": [],
        "candidate_projector_sandwich": CANDIDATE_FORM,
        "evidence_for": ["independent charged projector identities exist"],
        "evidence_against": ["no projector source is attached to L_CKM_charged_current_bounded"],
        "status": STATUS_PROJECTOR,
        "claim_boundary": "Projector existence elsewhere does not establish the CKM action sandwich.",
        **input_guard(),
    }
