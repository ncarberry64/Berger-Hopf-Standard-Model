"""BHSM v2.1 infinite-basis sector-coupling bound scaffold.

This module replaces the old finite-scan-only sector-coupling evidence with
an explicit infinite-basis Schur/relative-bound route for the scaffold rule.
It remains conditional because the scaffold rule still has to be identified
with the complete twisted Dirac/bundle operator.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


SECTOR_COUPLING_INFINITE_BOUND_PROVEN = "SECTOR_COUPLING_INFINITE_BOUND_PROVEN"
SECTOR_COUPLING_INFINITE_BOUND_CANDIDATE = "SECTOR_COUPLING_INFINITE_BOUND_CANDIDATE"
SECTOR_COUPLING_INFINITE_BOUND_CONDITIONAL = "SECTOR_COUPLING_INFINITE_BOUND_CONDITIONAL"
SECTOR_COUPLING_FINITE_SCAN_ONLY = "SECTOR_COUPLING_FINITE_SCAN_ONLY"
FAILS_SECTOR_COUPLING_BOUND = "FAILS_SECTOR_COUPLING_BOUND"

SECTOR_RELATIVE_A = 0.015621013485509948
SECTOR_RELATIVE_B = 0.0


@dataclass(frozen=True)
class SectorCouplingPattern:
    """Structural data for K_sector in the formal-kernel scaffold."""

    term_id: str
    connects: str
    preserves: tuple[str, ...]
    vanishes_on_kernel: bool
    row_support_bound: int
    column_support_bound: int
    max_weight_bound: float
    independent_of_kmax: bool
    assumptions: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class SectorCouplingInfiniteBoundReport:
    """Infinite-basis sector-coupling relative-bound report."""

    title: str
    pattern: SectorCouplingPattern
    method: str
    schur_row_sum_bound: float
    schur_column_sum_bound: float
    relative_a: float
    relative_b: float
    finite_scan_evidence_used: bool
    independent_of_kmax: bool
    status: str
    theorem_complete: bool
    open_obligations: tuple[str, ...]
    limitations: tuple[str, ...]


def build_sector_coupling_infinite_bound_report() -> SectorCouplingInfiniteBoundReport:
    """Build the v2.1 conditional infinite-basis sector-coupling report."""

    pattern = SectorCouplingPattern(
        term_id="K_sector",
        connects="distinct charged sectors at fixed (k,j,q,chi)",
        preserves=("k", "j", "q", "chirality"),
        vanishes_on_kernel=True,
        row_support_bound=2,
        column_support_bound=2,
        max_weight_bound=0.007810506742754974,
        independent_of_kmax=True,
        assumptions=(
            "The complete sector-coupling rule has the same fixed-label sparse support as the formal-kernel scaffold.",
            "The sector-coupling weights are uniformly bounded by the stated scaffold weight.",
            "The diagonal reference action dominates the fixed-label sector-coupling quadratic form.",
        ),
        limitations=(
            "The bound is independent of k_max under the scaffold rule, but the rule is not yet derived from the complete operator.",
            "This is not a proof of the full H_T theorem.",
        ),
    )
    row_bound = pattern.row_support_bound * pattern.max_weight_bound
    col_bound = pattern.column_support_bound * pattern.max_weight_bound
    return SectorCouplingInfiniteBoundReport(
        title="BHSM v2.1 Sector-Coupling Infinite-Basis Bound",
        pattern=pattern,
        method="Schur row/column bound plus relative domination by A0 on fixed-label sector blocks",
        schur_row_sum_bound=row_bound,
        schur_column_sum_bound=col_bound,
        relative_a=SECTOR_RELATIVE_A,
        relative_b=SECTOR_RELATIVE_B,
        finite_scan_evidence_used=False,
        independent_of_kmax=True,
        status=SECTOR_COUPLING_INFINITE_BOUND_CONDITIONAL,
        theorem_complete=False,
        open_obligations=(
            "derive the fixed-label sparse sector-coupling rule from the complete twisted Dirac/bundle operator",
            "prove the uniform weight bound in the complete infinite basis",
            "prove compatibility with the final formal complement projector",
        ),
        limitations=pattern.limitations,
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


def export_sector_coupling_infinite_bound_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_sector_coupling_infinite_bound_report()), indent=2, sort_keys=True) + "\n")


def export_sector_coupling_infinite_bound_markdown(path: str | Path) -> None:
    report = build_sector_coupling_infinite_bound_report()
    p = report.pattern
    lines = [
        "# BHSM v2.1 Sector-Coupling Infinite-Basis Bound",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Method: {report.method}",
        f"Independent of k_max: `{report.independent_of_kmax}`",
        f"Finite-scan evidence used: `{report.finite_scan_evidence_used}`",
        "",
        "| Quantity | Value |",
        "| --- | --- |",
        f"| connects | `{p.connects}` |",
        f"| preserves | `{', '.join(p.preserves)}` |",
        f"| vanishes on formal kernel | `{p.vanishes_on_kernel}` |",
        f"| row support bound | `{p.row_support_bound}` |",
        f"| column support bound | `{p.column_support_bound}` |",
        f"| max weight bound | `{p.max_weight_bound}` |",
        f"| Schur row-sum bound | `{report.schur_row_sum_bound}` |",
        f"| Schur column-sum bound | `{report.schur_column_sum_bound}` |",
        f"| relative a_K | `{report.relative_a}` |",
        f"| relative b_K | `{report.relative_b}` |",
        "",
        "## Assumptions",
        "",
    ]
    lines.extend(f"- {item}" for item in p.assumptions)
    lines.extend(["", "## Open Obligations", ""])
    lines.extend(f"- {item}" for item in report.open_obligations)
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
