"""Audit whether BHSM selects the maximal primitive self-response for CKM."""

from __future__ import annotations

from .alternative_channel_audit import audit_alternative_channel_assignments
from .common import input_guard
from .source_search import search_ckm_channel_sources


def audit_maximal_sector_selection() -> dict[str, object]:
    sources = search_ckm_channel_sources()
    alternatives = audit_alternative_channel_assignments()
    selection = sources["maximal_sector_selection_rule_found"] and alternatives["unique_surviving_assignment"] == "End_V_d"
    return {
        "audit": "ckm_maximal_sector_selection",
        "evidence_for_maximal_self_response": ["s_d=4 is maximal", "N_16=s_d^2 occurs in common-16 artifacts"],
        "evidence_against_alternatives": [],
        "competing_assignments": alternatives["rows"],
        "missing_action_rule": "CKM transport functional must select End(V_d) over Hom(V_u,V_d), End(V_ch), and direct-sum self responses",
        "status": "ARTIFACT_BACKED_MAXIMAL_SECTOR_CKM_SELECTION" if selection else "OPEN_MISSING_MAXIMAL_SECTOR_CKM_SELECTION_RULE",
        "candidate_status": "CONDITIONAL_MAXIMAL_SECTOR_CKM_SELECTION",
        "selection_rule_proven": selection,
        "selected_N_CKM": 16 if selection else None,
        "claim_boundary": "The N_16 channel assignment remains conditional unless the action selects maximal primitive charged self-response over competing channel assignments.",
        **input_guard(),
    }
