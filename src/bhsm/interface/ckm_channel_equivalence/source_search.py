"""Locate CKM transport/channel evidence without treating occurrences as proof."""

from __future__ import annotations

from .common import input_guard, repository_root


SOURCES = (
    "artifacts/BHSM_common_16_ckm_transport_audit_v1_8.json",
    "artifacts/BHSM_ckm_log_transport_application_gate_v2_1.json",
    "artifacts/BHSM_primitive_charged_incidence_closure_report_v2_0.json",
    "src/bhsm/interface/common_16/ckm_transport_audit.py",
    "src/ckm_structural_source.py",
)


def search_ckm_channel_sources() -> dict[str, object]:
    root = repository_root()
    return {
        "audit": "ckm_channel_source_search",
        "sources": list(SOURCES),
        "present_sources": [path for path in SOURCES if (root / path).is_file()],
        "all_sources_present": all((root / path).is_file() for path in SOURCES),
        "N_16_occurs_in_artifacts": True,
        "bilinear_Vd_tensor_dual_identified": False,
        "maximal_sector_selection_rule_found": False,
        "alternative_channel_spaces_excluded": False,
        "status": "CKM_CHANNEL_SOURCES_LOCATED_SELECTION_THEOREM_OPEN",
        "claim_boundary": "Occurrences of N_16 and 1/16 do not identify the physical CKM channel space.",
        **input_guard(),
    }
