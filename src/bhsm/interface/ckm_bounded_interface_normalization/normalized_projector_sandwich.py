"""Gate promotion to a normalized projector-sandwiched action term."""

from __future__ import annotations

from .common import CANDIDATE_ACTION_FORM, STATUS_OPEN_ACTION, input_guard


def audit_normalized_projector_sandwich() -> dict[str, object]:
    return {
        "audit": "normalized_projector_sandwich_action_term",
        "candidate_action_form": CANDIDATE_ACTION_FORM,
        "boundary_measure_source": None,
        "coefficient_normalization_source": None,
        "projector_sources": [
            "artifacts/BHSM_primitive_charged_incidence_closure_report_v2_0.json",
            "artifacts/BHSM_projector_reduction_audit_v2_0.json",
        ],
        "sector_domain_sources": [],
        "variational_action_source": None,
        "evidence_for": [
            "bounded interface target has an off-diagonal up/down bilinear",
            "independent BHSM artifacts contain charged-sector projectors",
            "target expression contains + h.c.",
        ],
        "evidence_against": [
            "no boundary/action measure is attached to L_CKM_charged_current_bounded",
            "g2_BH_runtime is a collider-interface parameter, not action-derived normalization",
            "the term does not contain Pi_u and Pi_d or an equivalent projector sandwich",
            "the bounded subset explicitly marks the term incomplete",
            "no variational action source generates the term",
        ],
        "missing_requirements": [
            "boundary/action measure",
            "coefficient normalization",
            "sector projector sandwich",
            "action/variational provenance",
        ],
        "status": STATUS_OPEN_ACTION,
        "claim_boundary": "A normalized projector-sandwiched action term requires boundary/action measure, coefficient normalization, sector projectors, and action provenance.",
        **input_guard(),
    }
