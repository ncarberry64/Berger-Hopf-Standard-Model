"""Kato-Rellich precondition ledger for BHSM after v1.9."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from essential_self_adjointness import (
    DIAGONAL_CORE_ESSENTIALLY_SELF_ADJOINT_PROVEN,
    build_essential_self_adjointness_report,
)
from graph_norm_domain import GRAPH_NORM_DOMAIN_PROVEN, build_graph_norm_domain_report
from uniform_relative_bound import build_uniform_relative_bound_report


KATO_RELLICH_PRECONDITIONS_COMPLETE = "KATO_RELLICH_PRECONDITIONS_COMPLETE"
KATO_RELLICH_PRECONDITIONS_CONDITIONAL = "KATO_RELLICH_PRECONDITIONS_CONDITIONAL"
KATO_RELLICH_PRECONDITIONS_BLOCKED_BY_DOMAIN = "KATO_RELLICH_PRECONDITIONS_BLOCKED_BY_DOMAIN"
KATO_RELLICH_PRECONDITIONS_OPEN = "KATO_RELLICH_PRECONDITIONS_OPEN"


@dataclass(frozen=True)
class KatoRellichPrecondition:
    """One Kato-Rellich precondition row."""

    id: str
    statement: str
    status: str
    passes: bool
    open_obligations: tuple[str, ...]


@dataclass(frozen=True)
class KatoRellichPreconditionReport:
    """Kato-Rellich precondition report."""

    title: str
    preconditions: tuple[KatoRellichPrecondition, ...]
    relative_bound_value: float
    relative_bound_below_one: bool
    status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def kato_rellich_preconditions() -> tuple[KatoRellichPrecondition, ...]:
    """Return Kato-Rellich precondition rows."""

    essential = build_essential_self_adjointness_report()
    graph = build_graph_norm_domain_report()
    relative = build_uniform_relative_bound_report()
    return (
        KatoRellichPrecondition(
            "reference_self_adjointness",
            "A0 is essentially self-adjoint on C_fin.",
            essential.status,
            essential.status == DIAGONAL_CORE_ESSENTIALLY_SELF_ADJOINT_PROVEN,
            (),
        ),
        KatoRellichPrecondition(
            "graph_domain",
            "D(A0) is the graph-norm closure of C_fin.",
            graph.status,
            graph.status == GRAPH_NORM_DOMAIN_PROVEN,
            (),
        ),
        KatoRellichPrecondition(
            "perturbation_symmetry",
            "Perturbations are symmetric on a common dense domain.",
            "CONDITIONAL",
            False,
            ("prove perturbation symmetry on D(A0) for the complete operator",),
        ),
        KatoRellichPrecondition(
            "relative_bound",
            "Perturbation relative bound satisfies a < 1.",
            relative.status,
            relative.all_a_below_one,
            tuple(item for term in relative.terms for item in term.open_obligations),
        ),
        KatoRellichPrecondition(
            "domain_inclusion",
            "Perturbations map D(A0) into the required Hilbert/domain space.",
            "OPEN",
            False,
            ("prove perturbation domain inclusion for Hopf, boundary, sector, lift, and projector terms",),
        ),
        KatoRellichPrecondition(
            "lower_bound_preservation",
            "The lower-bound chain survives the Kato-Rellich closure.",
            "CONDITIONAL",
            False,
            ("combine the closed reference operator with proven perturbation bounds and complement stability",),
        ),
    )


def build_kato_rellich_precondition_report() -> KatoRellichPreconditionReport:
    """Build Kato-Rellich precondition ledger."""

    rows = kato_rellich_preconditions()
    relative = build_uniform_relative_bound_report()
    complete = all(row.passes and not row.open_obligations for row in rows)
    reference_passes = rows[0].passes and rows[1].passes
    status = (
        KATO_RELLICH_PRECONDITIONS_COMPLETE
        if complete
        else KATO_RELLICH_PRECONDITIONS_CONDITIONAL
        if reference_passes and relative.all_a_below_one
        else KATO_RELLICH_PRECONDITIONS_BLOCKED_BY_DOMAIN
    )
    return KatoRellichPreconditionReport(
        title="BHSM v1.9 Kato-Rellich Precondition Report",
        preconditions=rows,
        relative_bound_value=relative.total_relative_a_upper,
        relative_bound_below_one=relative.all_a_below_one,
        status=status,
        theorem_complete=status == KATO_RELLICH_PRECONDITIONS_COMPLETE,
        limitations=(
            "The diagonal reference operator and graph-norm domain are closed.",
            "Kato-Rellich closure remains conditional because perturbation symmetry/domain inclusion and complete infinite-basis bounds are not all proven.",
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


def export_kato_rellich_preconditions_json(path: str | Path) -> None:
    """Export Kato-Rellich report as JSON."""

    Path(path).write_text(json.dumps(_jsonable(build_kato_rellich_precondition_report()), indent=2, sort_keys=True) + "\n")


def export_kato_rellich_preconditions_markdown(path: str | Path) -> None:
    """Export Kato-Rellich report as Markdown."""

    report = build_kato_rellich_precondition_report()
    lines = [
        "# BHSM v1.9 Kato-Rellich Precondition Report",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Relative-bound value: `{report.relative_bound_value}`",
        f"Relative bound below one: `{report.relative_bound_below_one}`",
        "",
        "| ID | Status | Passes | Open obligations |",
        "| --- | --- | --- | --- |",
    ]
    for row in report.preconditions:
        lines.append(f"| `{row.id}` | `{row.status}` | `{row.passes}` | {'<br>'.join(row.open_obligations) or 'none'} |")
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))

