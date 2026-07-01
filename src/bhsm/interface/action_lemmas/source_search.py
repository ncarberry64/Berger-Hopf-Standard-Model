"""Search local sources for the three proposed action lemmas."""

from __future__ import annotations

from .common import input_guard, repository_root


SOURCES = {
    "primitive_lattice": (
        "theory/primitive_cyclic_monodromy_from_boundary_action.md",
        "theory/action_monodromy_remaining_assumptions.md",
        "artifacts/BHSM_rho_ch_gcd_selection_audit_v2_0.json",
    ),
    "maximal_overlap": (
        "docs/bhsm_freeze_protocol.md",
        "docs/incidence_normalized_overlap_bridge_source.md",
        "artifacts/BHSM_overlap_4_over_3_source_audit_v2_0.json",
    ),
    "ckm_transport": (
        "src/bhsm/interface/common_16/ckm_transport_audit.py",
        "artifacts/BHSM_common_16_ckm_transport_audit_v1_8.json",
        "artifacts/BHSM_ckm_log_transport_gate_v2_0.json",
    ),
}


def search_action_lemma_sources() -> dict[str, object]:
    root = repository_root()
    rows = {}
    for key, paths in SOURCES.items():
        rows[key] = {
            "paths": list(paths),
            "present": [path for path in paths if (root / path).is_file()],
            "all_present": all((root / path).is_file() for path in paths),
        }
    return {
        "audit": "action_lemma_source_search",
        "rows": rows,
        "action_quotient_evidence_found": False,
        "maximal_bridge_selection_evidence_found": False,
        "ckm_equivalent_channel_evidence_found": False,
        "status": "SOURCES_LOCATED_ACTION_LEMMAS_REMAIN_OPEN",
        "claim_boundary": "Source presence is provenance, not proof of the proposed action rules.",
        **input_guard(),
    }
