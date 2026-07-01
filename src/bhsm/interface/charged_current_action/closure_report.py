"""Combined v2.6 charged-current action transport-space report."""

from __future__ import annotations

import json

from .charged_current_term_audit import audit_normalized_charged_current_action_term
from .ckm_application_gate import audit_ckm_transport_space_application_gate
from .common import REQUIRED_BOUNDARY_STATEMENTS, STATUS_OPEN_ACTION, STATUS_OPEN_SPACE, STATUS_REJECTED_OVERCLAIM, STATUS_RETIRED_MAXIMAL, input_guard
from .hermitian_adjoint_pair_gate import audit_hermitian_adjoint_pair_transport_gate
from .source_search import search_charged_current_action_sources
from .transport_space_audit import audit_charged_current_transport_space


def build_charged_current_action_report() -> dict[str, object]:
    source_search = search_charged_current_action_sources()
    action = audit_normalized_charged_current_action_term()
    space = audit_charged_current_transport_space()
    adjoint = audit_hermitian_adjoint_pair_transport_gate()
    ckm = audit_ckm_transport_space_application_gate()
    return {
        "version": "2.6",
        "audit": "charged_current_action_report",
        "source_search": source_search,
        "normalized_charged_current_action_term": action,
        "charged_current_transport_space": space,
        "hermitian_adjoint_pair_transport_gate": adjoint,
        "ckm_transport_space_application_gate": ckm,
        "artifact_backed_closures": [],
        "conditional_closures": [],
        "open_blockers": [STATUS_OPEN_ACTION, STATUS_OPEN_SPACE, adjoint["status"], ckm["ckm_identification_status"]],
        "retired_or_rejected_claims": [STATUS_RETIRED_MAXIMAL, STATUS_REJECTED_OVERCLAIM],
        "final_public_status": STATUS_OPEN_ACTION,
        "required_boundary_statements": list(REQUIRED_BOUNDARY_STATEMENTS),
        **input_guard(),
    }


def charged_current_action_report_to_markdown(payload: dict[str, object] | None = None) -> str:
    report = payload or build_charged_current_action_report()
    action = report["normalized_charged_current_action_term"]
    space = report["charged_current_transport_space"]
    ckm = report["ckm_transport_space_application_gate"]
    lines = [
        "# Charged-Current Action Transport-Space Audit",
        "",
        f"Status: {report['final_public_status']}",
        f"Normalized charged-current action term: {action['status']}",
        f"Charged-current transport space: {space['transport_space_status']}",
        f"Hermitian adjoint-pair gate: {report['hermitian_adjoint_pair_transport_gate']['status']}",
        f"CKM application: {ckm['application_status']}",
        f"CKM exponent: {ckm['ckm_exponent_status']}",
        "",
        "## Claim Boundary",
    ]
    lines.extend(f"- {statement}" for statement in report["required_boundary_statements"])
    lines.extend(["", "## Machine Payload", "```json", json.dumps(report, indent=2, sort_keys=True), "```"])
    return "\n".join(lines)
