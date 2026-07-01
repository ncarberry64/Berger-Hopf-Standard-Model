"""Alternative channel assignments that block premature CKM closure."""

from __future__ import annotations

from .common import STATUS_COMPETING_ASSIGNMENTS, STATUS_RETIRED_MAXIMAL, channel_dimensions, input_guard


def audit_ckm_alternative_channel_blockers() -> dict[str, object]:
    dims = channel_dimensions()
    alternatives = [
        {
            "id": "one_way_up_down",
            "dimension": dims["one_way_up_down"],
            "interpretation": "Hom(V_u,V_d)",
            "why_it_might_apply": "The CKM target is an up/down charged-current cross-sector map.",
            "why_it_might_not_apply": "A real/Hermitian charged-current action would normally include the adjoint direction.",
            "current_status": "UNSELECTED_COMPETING_CHANNEL_ASSIGNMENT",
            "what_would_select_it": "An action theorem proving CKM transport is oriented one-way before Hermitian completion.",
            "what_would_falsify_it": "A normalized-action theorem requiring Hermitian adjoint-pair transport.",
        },
        {
            "id": "bidirectional_adjoint_pair",
            "dimension": dims["bidirectional_adjoint_pair"],
            "interpretation": "Hom(V_u,V_d) direct_sum Hom(V_d,V_u)",
            "why_it_might_apply": "The charged-current target is off-diagonal and contains an explicit Hermitian-conjugate term.",
            "why_it_might_not_apply": "The located evidence is target-level; normalized action selection remains missing.",
            "current_status": "CONDITIONAL_NORMALIZED_ACTION_ADJOINT_PAIR_SELECTION",
            "what_would_select_it": "A normalized BHSM action derivation selecting the off-diagonal Hermitian charged-current adjoint pair.",
            "what_would_falsify_it": "An action theorem selecting a different CKM transport space or proving the h.c. term is not CKM-counting input.",
        },
        {
            "id": "maximal_self_response",
            "dimension": dims["maximal_self_response"],
            "interpretation": "End(V_d)",
            "why_it_might_apply": "It has the same numerical dimension, 16.",
            "why_it_might_not_apply": "Same numerical dimension does not prove same physical source; End(V_d) is a self-response, not the off-diagonal CKM target.",
            "current_status": STATUS_RETIRED_MAXIMAL,
            "what_would_select_it": "New action evidence reviving maximal self-response as the CKM transport source.",
            "what_would_falsify_it": "A normalized-action theorem selecting the adjoint-pair or another non-self-response space.",
        },
        {
            "id": "sector_self_response_sum",
            "dimension": dims["sector_self_response_sum"],
            "interpretation": "End(V_l) direct_sum End(V_u) direct_sum End(V_d)",
            "why_it_might_apply": "It captures all sectorwise charged self-responses.",
            "why_it_might_not_apply": "It includes diagonal self blocks rather than the off-diagonal CKM charged-current pair.",
            "current_status": "UNSELECTED_COMPETING_CHANNEL_ASSIGNMENT",
            "what_would_select_it": "An action theorem showing CKM transport averages over all sector self-responses.",
            "what_would_falsify_it": "A theorem restricting CKM transport to cross-sector charged-current blocks.",
        },
        {
            "id": "total_charged_endomorphism",
            "dimension": dims["total_charged_endomorphism"],
            "interpretation": "End(V_l direct_sum V_u direct_sum V_d)",
            "why_it_might_apply": "It is the complete charged endomorphism algebra.",
            "why_it_might_not_apply": "It includes non-CKM diagonal and cross-sector blocks and has no current action selection.",
            "current_status": "UNSELECTED_COMPETING_CHANNEL_ASSIGNMENT",
            "what_would_select_it": "An action theorem proving CKM transport acts on the full charged endomorphism algebra.",
            "what_would_falsify_it": "A theorem selecting the smaller charged-current adjoint pair or one-way block.",
        },
    ]
    return {
        "audit": "ckm_alternative_channel_blockers",
        "alternatives": alternatives,
        "same_dimension_warning": "Same numerical dimension does not prove same physical source.",
        "status": STATUS_COMPETING_ASSIGNMENTS,
        "claim_boundary": "The maximal self-response channel also has dimension 16, but it is retired as the primary CKM source unless action evidence revives it.",
        **input_guard(),
    }

