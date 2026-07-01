"""Locate adjoint-pair evidence while preserving its target-convention status."""

from __future__ import annotations

import json

from .common import input_guard, repository_root


SOURCES = (
    "artifacts/BHSM_chiral_current_attachment_map_v0_6.json",
    "artifacts/BHSM_bounded_vertex_promotion_audit_v1_0.json",
    "artifacts/BHSM_ckm_channel_equivalence_report_v2_2.json",
    "src/bhsm/interface/action_lemmas/log_transport_averaging.py",
    "src/claims.py",
)


def search_ckm_bidirectional_sources() -> dict[str, object]:
    root = repository_root()
    current_map = json.loads((root / SOURCES[0]).read_text(encoding="utf-8"))
    ckm = next(row for row in current_map["entries"] if row["current_family_id"] == "q_charged_current_CKM_BH")
    has_hc = "+ h.c." in ckm["target_expression"]
    target_only = ckm["lorentz_structure_status"] == "STANDARD_HEP_TARGET_CONVENTION"
    return {
        "audit": "ckm_bidirectional_source_search",
        "sources": list(SOURCES),
        "present_sources": [path for path in SOURCES if (root / path).is_file()],
        "all_sources_present": all((root / path).is_file() for path in SOURCES),
        "ckm_charged_current_target_identified": current_map["CKM_current_target_identified"],
        "target_expression": ckm["target_expression"],
        "hermitian_conjugate_present": has_hc,
        "up_down_off_diagonal_interpretation_present": "ubar_i" in ckm["target_expression"] and "d_j" in ckm["target_expression"],
        "target_convention_only": target_only,
        "bhsm_action_selects_adjoint_pair": False,
        "status": "CKM_BIDIRECTIONAL_SOURCES_LOCATED_ACTION_SELECTION_OPEN",
        "claim_boundary": "The charged-current target contains its Hermitian conjugate, but its Lorentz/gauge structure is explicitly a target convention rather than a BHSM action derivation.",
        **input_guard(),
    }

