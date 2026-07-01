"""Fail-closed maximal primitive-overlap bridge action lemma."""

from __future__ import annotations

from fractions import Fraction

from .common import fraction_text, input_guard
from .source_search import search_action_lemma_sources


def audit_maximal_overlap_bridge_rule() -> dict[str, object]:
    overlap = Fraction(4, 3)
    bridge = overlap**2 / 21
    selection_evidence = search_action_lemma_sources()["maximal_bridge_selection_evidence_found"]
    return {
        "lemma": "maximal_overlap_bridge_rule",
        "max_primitive_channel": 4,
        "rho_ch": 3,
        "overlap": fraction_text(overlap),
        "charged_trace": 21,
        "g_bridge": fraction_text(bridge),
        "exact_conditional_identity": bridge == Fraction(16, 189),
        "candidate_status": "CONDITIONAL_MAXIMAL_OVERLAP_BRIDGE_RULE",
        "status": (
            "ARTIFACT_BACKED_MAXIMAL_OVERLAP_BRIDGE_RULE"
            if selection_evidence
            else "OPEN_MISSING_ACTION_RULE_THAT_BRIDGE_USES_MAX_PRIMITIVE_OVERLAP"
        ),
        "bridge_action_selects_maximal_channel": selection_evidence,
        "action_derived": selection_evidence,
        "claim_boundary": "The maximal-overlap bridge rule is not action-derived unless the BHSM charged bridge/Hessian action selects the maximal primitive overlap channel.",
        **input_guard(),
    }
