"""BHSM v2.6 strict missing-term audit for complete operator identification."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from operator_term_inventory import BLOCKING_CLASSIFICATIONS, build_operator_term_inventory_report


@dataclass(frozen=True)
class MissingTermAuditRow:
    audit_id: str
    candidate_contribution: str
    disposition: str
    blocking: bool
    evidence: str


@dataclass(frozen=True)
class OperatorMissingTermAuditReport:
    title: str
    rows: tuple[MissingTermAuditRow, ...]
    hidden_missing_terms: bool
    blocking_term: str
    unique_blocking_terms: tuple[str, ...]
    status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def build_operator_missing_term_audit_report() -> OperatorMissingTermAuditReport:
    inventory = build_operator_term_inventory_report()
    lookup = {term.term_id: term for term in inventory.terms}
    candidates = (
        ("connection_curvature_terms", "connection curvature terms", "lichnerowicz_bundle_curvature_remainder"),
        ("torsion_like_terms", "torsion-like terms if applicable", "lichnerowicz_bundle_curvature_remainder"),
        ("bundle_connection_terms", "bundle connection terms", "higgs_u1_connection"),
        ("sector_off_diagonal_terms", "sector off-diagonal terms", "sector_coupling"),
        ("mirror_channel_terms", "mirror-channel terms", "mirror_channel_terms"),
        ("higgs_u1_terms", "Higgs-U1 terms", "higgs_u1_connection"),
        ("boundary_functional_terms", "boundary-functional terms", "boundary_functional"),
        ("topographic_scalar_leakage", "topographic/scalar leakage into H_T", "scalar_topographic_leakage"),
        ("projection_lift_terms", "projection/lift terms", "formal_kernel_complement_lift"),
        ("heat_profile_terms", "heat-kernel/profile terms", "heat_lift"),
    )
    rows = []
    for audit_id, label, term_id in candidates:
        term = lookup[term_id]
        blocking = term.classification in BLOCKING_CLASSIFICATIONS
        rows.append(
            MissingTermAuditRow(
                audit_id=audit_id,
                candidate_contribution=label,
                disposition=term.classification,
                blocking=blocking,
                evidence="; ".join(term.evidence),
            )
        )
    blocking_terms = tuple(
        sorted(
            {
                lookup[term_id].term_id
                for _, _, term_id in candidates
                if lookup[term_id].classification in BLOCKING_CLASSIFICATIONS
            }
        )
    )
    blocking_term = blocking_terms[0] if blocking_terms else ""
    return OperatorMissingTermAuditReport(
        title="BHSM v2.6 Operator Missing-Term Audit",
        rows=tuple(rows),
        hidden_missing_terms=False,
        blocking_term=blocking_term,
        unique_blocking_terms=blocking_terms,
        status="OPERATOR_MISSING_TERM_AUDIT_BLOCKED" if blocking_term else "OPERATOR_MISSING_TERM_AUDIT_CLEAN",
        theorem_complete=not blocking_term,
        limitations=(
            "The audit does not hide the connection-curvature/torsion-like remainder.",
            "The first blocking item is treated as the single named theorem gap for the next branch.",
        ),
    )


def _jsonable(value: object) -> object:
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if hasattr(value, "__dataclass_fields__"):
        return _jsonable(asdict(value))
    return value


def export_operator_missing_term_audit_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_operator_missing_term_audit_report()), indent=2, sort_keys=True) + "\n")


def export_operator_missing_term_audit_markdown(path: str | Path) -> None:
    report = build_operator_missing_term_audit_report()
    lines = [
        "# BHSM v2.6 Operator Missing-Term Audit",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Hidden missing terms: `{report.hidden_missing_terms}`",
        f"Blocking term: `{report.blocking_term}`",
        f"Unique blocking terms: `{report.unique_blocking_terms}`",
        "",
        "| Audit | Candidate contribution | Disposition | Blocking | Evidence |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in report.rows:
        lines.append(f"| `{row.audit_id}` | {row.candidate_contribution} | `{row.disposition}` | `{row.blocking}` | {row.evidence} |")
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
