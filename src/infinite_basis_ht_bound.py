"""Infinite-basis H_T bound closure attempt.

The repository contains strong corrected formal-kernel finite/semi-analytic
evidence. This module records the extra assumptions needed to upgrade that
evidence to an infinite-basis theorem.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


FORMAL_KERNEL_SCAFFOLD_STRONG = "FORMAL_KERNEL_SCAFFOLD_STRONG"
INFINITE_BASIS_OPEN = "INFINITE_BASIS_OPEN"


@dataclass(frozen=True)
class InfiniteBasisBoundNode:
    """One infinite-basis lower-bound proof node."""

    id: str
    statement: str
    status: str
    finite_evidence: tuple[str, ...]
    open_obligations: tuple[str, ...]


@dataclass(frozen=True)
class InfiniteBasisHTBoundReport:
    """Infinite-basis H_T bound closure report."""

    title: str
    required_dirac_lower_bound: float
    structured_relative_lower_bound: float
    exact_finite_lower_bound: float
    heat_lift_lower_bound: float
    nodes: tuple[InfiniteBasisBoundNode, ...]
    status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def infinite_basis_bound_nodes() -> tuple[InfiniteBasisBoundNode, ...]:
    """Return the infinite-basis proof nodes."""

    return (
        InfiniteBasisBoundNode(
            id="finite_formal_kernel_bound",
            statement="Corrected formal-kernel finite/semi-analytic lower bound clears the required threshold.",
            status=FORMAL_KERNEL_SCAFFOLD_STRONG,
            finite_evidence=(
                "structured relative lower bound = 6.729508865520464",
                "exact finite lower bound = 6.8171156827281205",
                "heat-lift lower bound = 19591.98933512353",
            ),
            open_obligations=(),
        ),
        InfiniteBasisBoundNode(
            id="infinite_basis_complement",
            statement="H_perp complement lower bound survives the infinite-basis limit.",
            status=INFINITE_BASIS_OPEN,
            finite_evidence=("formal-kernel convergence scans pass in finite truncations",),
            open_obligations=(
                "Prove an infinite-basis uniform complement lower bound independent of k_max.",
                "Prove compactness/relative-bound hypotheses for the complete operator.",
            ),
        ),
        InfiniteBasisBoundNode(
            id="operator_domain",
            statement="The complete H_T operator domain is self-adjoint with the same complement split.",
            status=INFINITE_BASIS_OPEN,
            finite_evidence=("finite matrices are symmetric/Hermitian in the Level 2 scaffold",),
            open_obligations=(
                "Specify the full Hilbert-space domain.",
                "Prove self-adjointness and domain stability under twist/profile terms.",
            ),
        ),
    )


def build_infinite_basis_ht_bound_report() -> InfiniteBasisHTBoundReport:
    """Build the infinite-basis H_T bound closure attempt report."""

    nodes = infinite_basis_bound_nodes()
    theorem_complete = all(node.status != INFINITE_BASIS_OPEN for node in nodes)
    status = FORMAL_KERNEL_SCAFFOLD_STRONG if not theorem_complete else "FULL_INFINITE_BASIS_BOUND_PROVEN"
    return InfiniteBasisHTBoundReport(
        title="BHSM Infinite-Basis H_T Bound Closure Attempt",
        required_dirac_lower_bound=0.8038064161349437,
        structured_relative_lower_bound=6.729508865520464,
        exact_finite_lower_bound=6.8171156827281205,
        heat_lift_lower_bound=19591.98933512353,
        nodes=nodes,
        status=status,
        theorem_complete=False,
        limitations=(
            "Finite/semi-analytic evidence is strong but is not an infinite-basis theorem.",
            "The full operator domain and topological index theorem remain open.",
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


def export_infinite_basis_ht_bound_json(path: str | Path) -> None:
    """Export the infinite-basis H_T bound report as JSON."""

    Path(path).write_text(json.dumps(_jsonable(build_infinite_basis_ht_bound_report()), indent=2, sort_keys=True) + "\n")


def export_infinite_basis_ht_bound_markdown(path: str | Path) -> None:
    """Export the infinite-basis H_T bound report as Markdown."""

    report = build_infinite_basis_ht_bound_report()
    lines = [
        "# BHSM Infinite-Basis H_T Bound Closure Attempt",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        "## Corrected Bounds",
        "",
        "| Quantity | Value |",
        "| --- | --- |",
        f"| required Dirac lower bound | `{report.required_dirac_lower_bound}` |",
        f"| structured relative lower bound | `{report.structured_relative_lower_bound}` |",
        f"| exact finite lower bound | `{report.exact_finite_lower_bound}` |",
        f"| heat-lift lower bound | `{report.heat_lift_lower_bound}` |",
        "",
        "## Proof Nodes",
        "",
        "| Node | Status | Open obligations |",
        "| --- | --- | --- |",
    ]
    for node in report.nodes:
        lines.append(f"| `{node.id}` | `{node.status}` | {'<br>'.join(node.open_obligations) or 'none'} |")
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
