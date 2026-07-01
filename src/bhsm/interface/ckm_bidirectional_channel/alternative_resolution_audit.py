"""Compare all v2.2 channel assignments against the bidirectional candidate."""

from __future__ import annotations

from .common import channel_dimensions, input_guard


def audit_ckm_channel_alternative_resolution() -> dict[str, object]:
    n = channel_dimensions()
    rows = [
        {"id": "one_way_up_down", "dimension": n["N_one_way_ud"], "interpretation": "Hom(V_u,V_d)", "evidence_for": ["cross-sector CKM target"], "evidence_against": ["omits the conjugate direction under Hermitian closure"], "status": "CONDITIONAL_ONE_WAY_CHANNEL_DISFAVORED"},
        {"id": "bidirectional_adjoint_pair", "dimension": n["N_bidirectional_ud_du"], "interpretation": "Hom(V_u,V_d) direct_sum Hom(V_d,V_u)", "evidence_for": ["off-diagonal CKM charged-current target", "explicit + h.c."], "evidence_against": ["adjoint-pair selection is not action-derived"], "status": "CONDITIONAL_HERMITIAN_BIDIRECTIONAL_CKM_CHANNEL_CANDIDATE"},
        {"id": "maximal_self_response", "dimension": n["N_max_self"], "interpretation": "End(V_d)", "evidence_for": ["same exact dimension 16"], "evidence_against": ["self-response does not match the cross-sector CKM target"], "status": "RETIRED_MAXIMAL_SELF_RESPONSE_AS_PRIMARY_CKM_SOURCE"},
        {"id": "sector_self_response_sum", "dimension": n["N_sum_self"], "interpretation": "direct sum of End(V_f)", "evidence_for": ["complete sectorwise self response"], "evidence_against": ["diagonal self blocks are not the off-diagonal CKM target"], "status": "UNSELECTED_COMPETING_ASSIGNMENT"},
        {"id": "total_charged_endomorphism", "dimension": n["N_total_end"], "interpretation": "End(V_ch)", "evidence_for": ["complete charged response algebra"], "evidence_against": ["includes diagonal and non-CKM blocks"], "status": "UNSELECTED_COMPETING_ASSIGNMENT"},
    ]
    return {
        "audit": "ckm_channel_alternative_resolution",
        "rows": rows,
        "preferred_candidate": "bidirectional_adjoint_pair",
        "theorem_level_unique_assignment": None,
        "status": "MULTIPLE_COMPETING_CHANNEL_ASSIGNMENTS",
        "claim_boundary": "The target convention prefers the bidirectional interpretation, but only the BHSM action can exclude competing transport spaces theoremically.",
        **input_guard(),
    }

