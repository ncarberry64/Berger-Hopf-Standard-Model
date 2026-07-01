"""Combined v2.5 normalized-action adjoint-pair report."""

from __future__ import annotations

import json

from .adjoint_pair_selection import audit_normalized_action_adjoint_pair_selection
from .alternative_channel_blockers import audit_ckm_alternative_channel_blockers
from .ckm_transport_space_gate import audit_ckm_transport_space_gate
from .common import REQUIRED_BOUNDARY_STATEMENTS, input_guard
from .hermitian_action_rule import audit_hermitian_charged_current_action_rule
from .source_search import search_normalized_action_adjoint_pair_sources


def build_normalized_action_adjoint_pair_report() -> dict[str, object]:
    source_search = search_normalized_action_adjoint_pair_sources()
    hermitian = audit_hermitian_charged_current_action_rule()
    selection = audit_normalized_action_adjoint_pair_selection()
    gate = audit_ckm_transport_space_gate()
    alternatives = audit_ckm_alternative_channel_blockers()
    return {
        "version": "2.5",
        "audit": "normalized_action_adjoint_pair_report",
        "source_search": source_search,
        "hermitian_charged_current_action_rule": hermitian,
        "normalized_action_adjoint_pair_selection": selection,
        "ckm_transport_space_gate": gate,
        "alternative_channel_blockers": alternatives,
        "artifact_backed_closures": [],
        "conditional_closures": [hermitian["status"]],
        "open_blockers": [
            selection["status"],
            gate["transport_space_theorem_status"],
            gate["application_status"],
        ],
        "retired_or_rejected_claims": [
            "RETIRED_MAXIMAL_SELF_RESPONSE_AS_PRIMARY_CKM_SOURCE",
            "REJECTED_ACTION_SELECTION_OVERCLAIM",
        ],
        "final_public_status": "OPEN_MISSING_NORMALIZED_ACTION_ADJOINT_PAIR_SELECTION",
        "required_boundary_statements": list(REQUIRED_BOUNDARY_STATEMENTS),
        **input_guard(),
    }


def normalized_action_adjoint_pair_report_to_markdown(payload: dict[str, object] | None = None) -> str:
    report = payload or build_normalized_action_adjoint_pair_report()
    gate = report["ckm_transport_space_gate"]
    selection = report["normalized_action_adjoint_pair_selection"]
    lines = [
        "# Normalized Action Adjoint-Pair CKM Audit",
        "",
        f"Status: {report['final_public_status']}",
        f"Hermitian charged-current action rule: {report['hermitian_charged_current_action_rule']['status']}",
        f"Normalized action adjoint-pair selection: {selection['status']}",
        f"CKM transport-space theorem: {gate['transport_space_theorem_status']}",
        f"CKM exponent: {gate['ckm_exponent_status']}",
        "",
        "## Claim Boundary",
    ]
    lines.extend(f"- {statement}" for statement in report["required_boundary_statements"])
    lines.extend(["", "## Machine Payload", "```json", json.dumps(report, indent=2, sort_keys=True), "```"])
    return "\n".join(lines)

