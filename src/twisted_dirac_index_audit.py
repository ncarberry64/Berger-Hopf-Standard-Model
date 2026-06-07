"""BHSM v1.3H combined twisted-Dirac index audit."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from diagonal_complement_bound import ComplementLowerBoundReport, build_complement_lower_bound_report
from mirror_mode_exclusion import MirrorModeAuditReport, build_mirror_mode_audit_report
from zero_mode_index import ZeroModeSplitReport, build_zero_mode_split_report


@dataclass(frozen=True)
class TwistedDiracIndexAudit:
    """Combined diagonal-bound and mirror-mode index audit."""

    title: str
    finite_scaffold_index: int
    boundary_functional_index: int
    topological_index_assumption: int
    target_index: int
    target_kernel_dimension: int
    diagonal_report: ComplementLowerBoundReport
    mirror_report: MirrorModeAuditReport
    zero_mode_report: ZeroModeSplitReport
    diagonal_bound_clears_required: bool
    open_mirror_risk_count: int
    index_status: str
    full_theorem_status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def build_twisted_dirac_index_audit() -> TwistedDiracIndexAudit:
    """Return the v1.3H combined index audit."""

    zero_report = build_zero_mode_split_report()
    diagonal_report = build_complement_lower_bound_report()
    mirror_report = build_mirror_mode_audit_report()
    finite_index = sum(item.index_contribution for item in zero_report.candidates)
    return TwistedDiracIndexAudit(
        title="BHSM v1.3H Twisted Dirac Index Audit",
        finite_scaffold_index=finite_index,
        boundary_functional_index=finite_index,
        topological_index_assumption=3,
        target_index=3,
        target_kernel_dimension=zero_report.target_kernel_dimension,
        diagonal_report=diagonal_report,
        mirror_report=mirror_report,
        zero_mode_report=zero_report,
        diagonal_bound_clears_required=diagonal_report.passes_required_bound,
        open_mirror_risk_count=mirror_report.open_mirror_risk_count,
        index_status="INDEX_SCAFFOLD",
        full_theorem_status="OPEN",
        theorem_complete=False,
        limitations=(
            "Finite scaffold index and boundary-functional index are not a full topological index theorem.",
            "Mirror-mode exclusion remains open in the complete twisted Dirac operator.",
            "The diagonal complement bound is finite-scaffold evidence, not an infinite-basis theorem.",
        ),
    )


def _jsonable(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if hasattr(value, "__dataclass_fields__"):
        return _jsonable(asdict(value))
    return value


def export_twisted_dirac_index_audit_json(path: str | Path) -> None:
    """Export the combined twisted-Dirac index audit as JSON."""

    Path(path).write_text(json.dumps(_jsonable(build_twisted_dirac_index_audit()), indent=2, sort_keys=True) + "\n")


def export_twisted_dirac_index_audit_markdown(path: str | Path) -> None:
    """Export the combined twisted-Dirac index audit as Markdown."""

    report = build_twisted_dirac_index_audit()
    first = report.diagonal_report.first_complement_mode
    lines = [
        "# BHSM v1.3H Twisted Dirac Index Audit",
        "",
        f"Index status: `{report.index_status}`",
        f"Full theorem status: `{report.full_theorem_status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        "## Index Summary",
        "",
        "| Quantity | Value |",
        "| --- | --- |",
        f"| Finite scaffold index | `{report.finite_scaffold_index}` |",
        f"| Boundary-functional index | `{report.boundary_functional_index}` |",
        f"| Topological index assumption | `{report.topological_index_assumption}` |",
        f"| Target index | `{report.target_index}` |",
        f"| Target kernel dimension | `{report.target_kernel_dimension}` |",
        "",
        "## Diagonal Bound Summary",
        "",
        "| Quantity | Value |",
        "| --- | --- |",
        f"| Required Dirac lower bound | `{report.diagonal_report.required_dirac_lower_bound}` |",
        f"| Finite diagonal complement lower bound | `{report.diagonal_report.finite_coordinate_complement_lower_bound}` |",
        f"| Margin | `{report.diagonal_report.margin}` |",
        f"| Passes | `{report.diagonal_bound_clears_required}` |",
        f"| First complement mode | `index={first.basis_index}, sector={first.sector}, k={first.k}, j={first.j}, q={first.q}, chi={first.chirality}` |",
        "",
        "## Mirror Summary",
        "",
        f"Open mirror risk count: `{report.open_mirror_risk_count}`",
        "",
        "## Limitations",
        "",
        *[f"- {item}" for item in report.limitations],
        "",
    ]
    Path(path).write_text("\n".join(lines))
