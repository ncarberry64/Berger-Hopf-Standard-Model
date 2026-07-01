"""Gate the Hermitian charged-current adjoint-pair selection rule."""

from __future__ import annotations

from .common import input_guard
from .source_search import search_ckm_bidirectional_sources


def audit_ckm_adjoint_pair_selection() -> dict[str, object]:
    sources = search_ckm_bidirectional_sources()
    proven = sources["hermitian_conjugate_present"] and sources["bhsm_action_selects_adjoint_pair"]
    return {
        "audit": "ckm_adjoint_pair_selection",
        "evidence_for_adjoint_pair": [
            "CKM charged-current target is off-diagonal in up/down fields",
            "target expression explicitly includes its Hermitian conjugate",
        ],
        "evidence_against_one_way_only": ["a Hermitian target convention includes the conjugate direction"],
        "evidence_against_maximal_self_response_as_primary_source": ["CKM target is cross-sector charged-current transport, not a sector self-response"],
        "artifact_limitations": ["charged-current Lorentz and gauge structures are STANDARD_HEP_TARGET_CONVENTION", "no complete BHSM action selects the adjoint-pair subspace"],
        "missing_action_rule": "derive the off-diagonal charged-current block and its adjoint closure from the normalized BHSM action",
        "selection_rule_proven": proven,
        "selected_N_CKM": 16 if proven else None,
        "status": "ARTIFACT_BACKED_CKM_ADJOINT_PAIR_SELECTION" if proven else "OPEN_MISSING_CKM_ADJOINT_PAIR_SELECTION_RULE",
        "candidate_status": "CONDITIONAL_CKM_ADJOINT_PAIR_SELECTION",
        "claim_boundary": "Target-level Hermitian conjugation motivates the pair but does not prove action-level CKM channel selection.",
        **input_guard(),
    }

