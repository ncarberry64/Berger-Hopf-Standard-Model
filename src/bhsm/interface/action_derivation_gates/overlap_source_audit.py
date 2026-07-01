"""Audit the action source of the charged overlap factor 4/3."""

from __future__ import annotations

from .common import FORBIDDEN_INPUTS, source_evidence


def audit_charged_overlap_source() -> dict[str, object]:
    evidence = source_evidence(
        (
            "docs/incidence_normalized_overlap_bridge_source.md",
            "data/incidence_normalized_overlap_bridge_source.json",
            "src/incidence_normalized_overlap_bridge.py",
        ),
        ("4/3", "OPEN_LOCALIZABLE", "g_sector"),
    )
    return {
        "audit": "charged_overlap_4_over_3_source",
        "status": "OPEN_MISSING_CHARGED_OVERLAP_4_OVER_3_ACTION_SOURCE",
        "target": "O_ch=4/3",
        "bridge_identity": "O_ch^2/I_ch=(4/3)^2/21=16/189",
        "evidence": evidence,
        "remaining_blockers": [
            "derive O_ch=4/3 from the normalized charged boundary action",
            "prove the overlap is not an inserted bridge amplitude",
        ],
        "forbidden_inputs_used": [],
        "forbidden_inputs": FORBIDDEN_INPUTS,
        "claim_boundary": "The incidence bridge is exact conditional on 4/3; the action source of 4/3 remains open.",
    }
