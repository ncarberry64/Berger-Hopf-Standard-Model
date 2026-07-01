"""Summarize repository evidence for CKM action normalization."""

from bhsm.interface.ckm_bounded_interface_normalization import search_ckm_bounded_interface_sources

from .common import STATUS_MEASURE, input_guard


def search_boundary_measure_normalization_sources() -> dict[str, object]:
    upstream = search_ckm_bounded_interface_sources()
    return {
        "audit": "ckm_boundary_measure_normalization_source_search",
        "files_scanned": upstream["files_scanned"],
        "hits": upstream["hits"],
        "measure_evidence": [
            "artifacts/BHSM_author_ontology_v0_8.json names dmu_boundary and dmu_boundary dt",
            "artifacts/BHSM_minimal_action_report_v0_8.json uses symbolic boundary measures",
            "artifacts/BHSM_neutral_boundary_measure_v1_0.json keeps physical normalization open",
        ],
        "coefficient_evidence": ["bounded target contains g2_BH_runtime / sqrt(2), explicitly runtime/scheme scoped"],
        "projector_evidence": ["independent sector projectors exist but are not attached to the bounded term"],
        "paired_normalization_evidence": ["target contains + h.c.; no shared action normalization source"],
        "action_provenance_evidence": ["symbolic boundary actions exist in other sectors; bounded CKM term remains interface scoped"],
        "transport_space_evidence": ["v2.7 records competing spaces and no selection"],
        "evidence_against_promotion": [
            "symbolic measure lacks physical normalization and same-term attachment",
            "runtime coupling is not action-derived coefficient normalization",
            "no projector sandwich or variational source attaches to the term",
        ],
        "missing_sources": ["CKM-term measure attachment", "fixed C_CKM", "projector sandwich", "shared paired normalization", "variational provenance"],
        "status": STATUS_MEASURE,
        **input_guard(),
    }
