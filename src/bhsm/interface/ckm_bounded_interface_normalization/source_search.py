"""Classify local evidence for promoting the bounded CKM interface term."""

from __future__ import annotations

from bhsm.interface.charged_current_action.source_search import search_charged_current_action_sources

from .common import STATUS_BOUNDED, input_guard


def search_ckm_bounded_interface_sources(max_hits: int = 180) -> dict[str, object]:
    upstream = search_charged_current_action_sources(max_hits=max_hits)
    bounded = next(row for row in upstream["candidate_action_terms"] if row["term_id"] == "L_CKM_charged_current_bounded")
    return {
        "audit": "ckm_bounded_interface_normalization_source_search",
        "files_scanned": upstream["files_scanned"],
        "hits": upstream["hits"],
        "total_hits": upstream["total_hits"],
        "bounded_interface_evidence": [
            bounded,
            "minimal bounded subset includes the term",
            "runtime parameter mode is BHSM_COLLIDER_INTERFACE",
        ],
        "normalization_evidence": ["coefficient uses g2_BH_runtime / sqrt(2) as a collider-interface target convention"],
        "projector_evidence": ["sector projector artifacts exist independently of this term"],
        "domain_codomain_evidence": ["the target bilinear suggests up/down directions but declares no operator domain or codomain"],
        "paired_term_evidence": ["symbolic target contains + h.c."],
        "ckm_identification_evidence": ["the target uses the local V_CKM_BH source matrix"],
        "evidence_against_promotion": [
            "the bounded subset says the term is not a complete 4D term",
            "the coefficient is a runtime interface parameter, not an action normalization",
            "no Pi_u/Pi_d projector sandwich occurs in the term",
            "no boundary/action measure is attached to the term",
            "no variational or Euler-Lagrange provenance is supplied",
            "no theorem identifies this interface term as the CKM transport law",
        ],
        "missing_sources": [
            "boundary/action measure for this term",
            "coefficient normalization derived from the BHSM action",
            "Pi_u/Pi_d sandwich attached to this term",
            "declared V_u/V_d operator domain and codomain",
            "shared normalization of forward and adjoint terms",
            "CKM identification theorem on the selected transport space",
        ],
        "status": STATUS_BOUNDED,
        **input_guard(),
    }
