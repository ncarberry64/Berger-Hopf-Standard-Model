"""Combined v2.7 report and Markdown renderer."""

from __future__ import annotations

import json

from .bounded_interface_term import audit_ckm_bounded_interface_term
from .ckm_identification_gate import audit_ckm_identification_gate
from .common import REQUIRED_BOUNDARY_STATEMENTS, STATUS_REJECTED_ARITHMETIC, STATUS_REJECTED_BOUNDED, STATUS_RETIRED_MAXIMAL, channel_dimensions, input_guard
from .normalized_projector_sandwich import audit_normalized_projector_sandwich
from .paired_term_normalization import audit_paired_term_normalization
from .projector_domain_codomain import audit_projector_domain_codomain
from .source_search import search_ckm_bounded_interface_sources
from .transport_space_selection import audit_ckm_transport_space_selection


def build_ckm_bounded_interface_report() -> dict[str, object]:
    return {
        "audit": "ckm_bounded_interface_normalization_report",
        "source_search": search_ckm_bounded_interface_sources(),
        "bounded_interface_term": audit_ckm_bounded_interface_term(),
        "normalized_projector_sandwich": audit_normalized_projector_sandwich(),
        "projector_domain_codomain": audit_projector_domain_codomain(),
        "paired_term_normalization": audit_paired_term_normalization(),
        "ckm_identification_gate": audit_ckm_identification_gate(),
        "transport_space_selection": audit_ckm_transport_space_selection(),
        "channel_dimensions": channel_dimensions(),
        "artifact_backed_closures": ["ARTIFACT_BACKED_BOUNDED_CKM_INTERFACE_TERM"],
        "conditional_closures": [],
        "retired_or_rejected_claims": [STATUS_REJECTED_BOUNDED, STATUS_REJECTED_ARITHMETIC, STATUS_RETIRED_MAXIMAL],
        "required_boundary_statements": list(REQUIRED_BOUNDARY_STATEMENTS),
        **input_guard(),
    }


def ckm_bounded_interface_report_to_markdown(payload: dict[str, object] | None = None) -> str:
    report = payload or build_ckm_bounded_interface_report()
    selection = report["transport_space_selection"]
    lines = [
        "# CKM Bounded Interface Normalization Audit",
        "",
        f"Bounded interface: `{report['bounded_interface_term']['status']}`",
        f"Normalized projector sandwich: `{report['normalized_projector_sandwich']['status']}`",
        f"CKM transport-space selection: `{selection['selection_status']}`",
        f"CKM exponent: `{selection['ckm_exponent_status']}`",
        "",
        "## Claim Boundaries",
    ]
    lines.extend(f"- {statement}" for statement in report["required_boundary_statements"])
    lines.extend(["", "## Machine Payload", "```json", json.dumps(report, indent=2, sort_keys=True), "```"])
    return "\n".join(lines)
