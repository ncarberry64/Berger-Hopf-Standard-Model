"""Reports for reducing the boundary functional from a parent action scaffold."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from action_reduction import (
    BoundaryReductionStep,
    ReducedBoundaryFunctional,
    reduce_parent_action_to_boundary_functional,
    reduced_coefficients,
)
from parent_internal_action import (
    ParentReductionStatus,
    default_internal_bundle_fields,
    default_projection_operators,
    parent_action_terms,
    symbolic_parent_action_expression,
)


@dataclass(frozen=True)
class ParentActionDerivationReport:
    """Parent-action reduction report for v1.2B."""

    title: str
    parent_action: str
    status: ParentReductionStatus
    theorem_complete: bool
    action_terms: tuple[Any, ...]
    bundle_fields: tuple[Any, ...]
    projection_operators: tuple[Any, ...]
    reductions: tuple[ReducedBoundaryFunctional, ...]
    coefficient_table: tuple[dict[str, Any], ...]
    necessary_terms: dict[str, tuple[str, ...]]
    limitations: tuple[str, ...]


def build_parent_action_derivation_report() -> ParentActionDerivationReport:
    """Build the v1.2B parent-action reduction report."""

    reductions = tuple(
        reduce_parent_action_to_boundary_functional(sector)
        for sector in ("lepton", "up", "down")
    )
    coefficient_rows = []
    for reduction in reductions:
        coefficients = reduced_coefficients(reduction)
        for name, coefficient in coefficients.items():
            coefficient_rows.append(
                {
                    "sector": reduction.sector,
                    "coefficient": name,
                    "value": coefficient.value,
                    "status": coefficient.status.value,
                    "source": coefficient.source,
                    "dependencies": coefficient.dependencies,
                    "parent_action_status": reduction.parent_action_status.value,
                    "open_reason": coefficient.open_reason,
                }
            )
    status = (
        ParentReductionStatus.REDUCED_FROM_PARENT_ACTION
        if all(reduction.parent_action_status == ParentReductionStatus.REDUCED_FROM_PARENT_ACTION for reduction in reductions)
        else ParentReductionStatus.OPEN
    )
    return ParentActionDerivationReport(
        title="BHSM v1.2B Parent Internal-Action Boundary Derivation Scaffold",
        parent_action=symbolic_parent_action_expression(),
        status=status,
        theorem_complete=False,
        action_terms=parent_action_terms(),
        bundle_fields=default_internal_bundle_fields(),
        projection_operators=default_projection_operators(),
        reductions=reductions,
        coefficient_table=tuple(coefficient_rows),
        necessary_terms={
            "fiber_q": ("I_HOPF", "I_U1"),
            "base_j": ("I_BASE", "I_WEAK", "I_COF"),
            "target": ("I_BDY",),
        },
        limitations=(
            "The sector boundary functional is reduced from a symbolic parent internal-action scaffold.",
            "This is not a full unique derivation from the complete Berger-Hopf twisted Dirac/bundle action.",
            "No empirical mass, CKM, PMNS, or residual inputs are used.",
        ),
    )


def _jsonable(value: Any) -> Any:
    if isinstance(value, (ParentReductionStatus,)):
        return value.value
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if hasattr(value, "__dataclass_fields__"):
        return _jsonable(asdict(value))
    return value


def export_parent_action_derivation_json(path: str | Path) -> None:
    """Export the v1.2B parent-action report as JSON."""

    report = build_parent_action_derivation_report()
    Path(path).write_text(json.dumps(_jsonable(report), indent=2, sort_keys=True) + "\n")


def export_parent_action_derivation_markdown(path: str | Path) -> None:
    """Export the v1.2B parent-action report as Markdown."""

    report = build_parent_action_derivation_report()
    lines = [
        "# BHSM v1.2B Parent Internal-Action Boundary Derivation Scaffold",
        "",
        f"Parent-action reduction status: `{report.status.value}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        "```text",
        report.parent_action,
        "```",
        "",
        "## Parent Action Terms",
        "",
        "| ID | Term | Contribution | Status |",
        "| --- | --- | --- | --- |",
    ]
    for term in report.action_terms:
        lines.append(f"| `{term.id}` | {term.name} | `{term.contribution}` | `{term.status.value}` |")
    lines.extend(
        [
            "",
            "## Coefficient Reduction Table",
            "",
            "| Sector | Coefficient | Value | Parent status | Dependencies |",
            "| --- | --- | ---: | --- | --- |",
        ]
    )
    for row in report.coefficient_table:
        lines.append(
            f"| `{row['sector']}` | `{row['coefficient']}` | `{row['value']}` | `{row['parent_action_status']}` | `{', '.join(row['dependencies'])}` |"
        )
    lines.extend(
        [
            "",
            "## Necessary Terms",
            "",
            f"- Fiber coefficient requires: `{', '.join(report.necessary_terms['fiber_q'])}`.",
            f"- Base coefficient requires: `{', '.join(report.necessary_terms['base_j'])}`.",
            f"- Target requires: `{', '.join(report.necessary_terms['target'])}`.",
            "",
            "## What v1.2B Shows and Does Not Show",
            "",
            "- Shows: the sector boundary functional is reduced from the symbolic parent internal-action scaffold.",
            "- Does not show: the complete Berger-Hopf twisted Dirac/bundle action uniquely generates the parent scaffold or the boundary functional.",
            "",
            "## Limitations",
            "",
            *[f"- {item}" for item in report.limitations],
            "",
        ]
    )
    Path(path).write_text("\n".join(lines))
