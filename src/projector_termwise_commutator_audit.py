"""BHSM v2.14 aggregate audit for termwise projector commutators."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from projector_commutator_control import PROJECTOR_DEFINITION_PROVEN, build_projector_definition_audit_report
from projector_operator_commutators import BLOCKING_COMMUTATOR_CLASSIFICATIONS, build_projector_operator_commutators_report


TERMWISE_COMMUTATOR_AUDIT_CLOSED = "TERMWISE_COMMUTATOR_AUDIT_CLOSED"
TERMWISE_COMMUTATOR_AUDIT_BLOCKED = "TERMWISE_COMMUTATOR_AUDIT_BLOCKED"


@dataclass(frozen=True)
class ProjectorTermwiseCommutatorAuditReport:
    title: str
    projector_definition_status: str
    operator_commutator_status: str
    all_terms_classified: bool
    blocking_terms: tuple[str, ...]
    nonzero_terms: tuple[str, ...]
    status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def build_projector_termwise_commutator_audit_report() -> ProjectorTermwiseCommutatorAuditReport:
    projector = build_projector_definition_audit_report()
    commutators = build_projector_operator_commutators_report()
    blocking = tuple(
        row.term_id for row in commutators.rows if row.classification in BLOCKING_COMMUTATOR_CLASSIFICATIONS
    )
    closed = projector.status == PROJECTOR_DEFINITION_PROVEN and commutators.theorem_complete and not blocking
    return ProjectorTermwiseCommutatorAuditReport(
        title="BHSM v2.14 Termwise Projector Commutator Audit",
        projector_definition_status=projector.status,
        operator_commutator_status=commutators.status,
        all_terms_classified=commutators.all_terms_classified,
        blocking_terms=blocking,
        nonzero_terms=commutators.nonzero_terms,
        status=TERMWISE_COMMUTATOR_AUDIT_CLOSED if closed else TERMWISE_COMMUTATOR_AUDIT_BLOCKED,
        theorem_complete=closed,
        limitations=(
            "All complete-operator terms are classified before any commutator-control upgrade.",
            "Graph-domain stability is not closed by this aggregate audit alone.",
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


def export_projector_termwise_commutator_audit_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_projector_termwise_commutator_audit_report()), indent=2, sort_keys=True) + "\n")


def export_projector_termwise_commutator_audit_markdown(path: str | Path) -> None:
    report = build_projector_termwise_commutator_audit_report()
    lines = [
        "# BHSM v2.14 Termwise Projector Commutator Audit",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Projector definition status: `{report.projector_definition_status}`",
        f"Operator commutator status: `{report.operator_commutator_status}`",
        f"All terms classified: `{report.all_terms_classified}`",
        f"Nonzero terms: `{report.nonzero_terms}`",
        "",
        "## Blocking Terms",
        "",
    ]
    lines.extend(f"- `{item}`" for item in report.blocking_terms)
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
