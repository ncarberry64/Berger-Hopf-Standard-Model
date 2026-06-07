"""BHSM v1.3H diagonal complement lower-bound scaffold.

This module audits the diagonal Level 2 twisted-Dirac complement block before
sector coupling. It distinguishes the finite coordinate-protected scaffold
from the still-open formal/infinite index theorem.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np

from ht_operator import default_level2_config
from sector_coupling_bounds import config_without_sector_coupling
from spectral_bounds import required_dirac_lower_bound
from spectral_gap import MU_H, natural_lambda2
from twisted_dirac import (
    DIRAC_PROXY_LEVEL_2,
    DiracMode,
    DiracOperatorConfig,
    build_dirac_basis,
    build_level2_dirac_matrix,
)
from zero_mode_index import protected_family_zero_modes


@dataclass(frozen=True)
class DiagonalModeBound:
    """One finite-basis diagonal mode bound row."""

    basis_index: int
    sector: str
    k: int
    j: int
    q: int
    chirality: int
    dirac_diagonal_value: float
    dirac_squared_diagonal: float
    coordinate_protected: bool
    formal_zero_candidate: bool
    included_in_complement_bound: bool
    assumptions: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class ComplementLowerBoundReport:
    """Diagonal complement lower-bound report."""

    model_level: str
    k_max: int
    a: float
    basis_size: int
    coordinate_zero_mode_count: int
    formal_zero_candidate_count: int
    lambda2: float
    required_dirac_lower_bound: float
    first_complement_mode: DiagonalModeBound
    finite_coordinate_complement_lower_bound: float
    margin: float
    passes_required_bound: bool
    formal_coordinate_alignment_status: str
    bound_status: str
    theorem_complete: bool
    mode_inventory: tuple[DiagonalModeBound, ...]
    assumptions: tuple[str, ...]
    limitations: tuple[str, ...]


def _formal_zero_keys() -> set[tuple[str, int, int, int, int]]:
    return {
        (candidate.sector, candidate.k, candidate.j, candidate.q, candidate.chirality)
        for candidate in protected_family_zero_modes()
    }


def _mode_key(mode: DiracMode) -> tuple[str, int, int, int, int]:
    return (mode.sector, mode.k, mode.j, mode.q, mode.chirality)


def diagonal_mode_inventory(config: DiracOperatorConfig | None = None) -> tuple[DiagonalModeBound, ...]:
    """Return finite diagonal mode rows before sector coupling."""

    resolved = default_level2_config() if config is None else config
    no_sector = config_without_sector_coupling(resolved)
    matrix = build_level2_dirac_matrix(no_sector)
    basis = build_dirac_basis(
        no_sector.k_max,
        sectors=no_sector.sectors,
        include_chirality=no_sector.include_chirality,
    )
    coordinate_zero_count = int(no_sector.boundary_params.get("zero_mode_count", 3))
    formal_keys = _formal_zero_keys()
    rows = []
    for index, mode in enumerate(basis):
        coordinate_protected = index < coordinate_zero_count
        formal_zero = _mode_key(mode) in formal_keys
        value = float(matrix[index, index])
        rows.append(
            DiagonalModeBound(
                basis_index=index,
                sector=mode.sector,
                k=mode.k,
                j=mode.j,
                q=mode.q,
                chirality=mode.chirality,
                dirac_diagonal_value=value,
                dirac_squared_diagonal=float(value**2),
                coordinate_protected=coordinate_protected,
                formal_zero_candidate=formal_zero,
                included_in_complement_bound=not coordinate_protected,
                assumptions=(
                    "This row uses the Level 2 finite matrix with sector coupling disabled.",
                    "Coordinate-protected rows are excluded from the finite complement bound.",
                ),
                limitations=(
                    "The formal protected-sector labels and finite coordinate block are not yet proven identical.",
                    "This is not an infinite-basis diagonal lower-bound theorem.",
                ),
            )
        )
    return tuple(rows)


def first_diagonal_complement_mode(config: DiracOperatorConfig | None = None) -> DiagonalModeBound:
    """Return the first finite coordinate-complement diagonal mode."""

    rows = [row for row in diagonal_mode_inventory(config) if row.included_in_complement_bound]
    if not rows:
        raise ValueError("empty diagonal complement inventory")
    return min(rows, key=lambda row: (row.dirac_squared_diagonal, row.basis_index))


def build_complement_lower_bound_report(
    config: DiracOperatorConfig | None = None,
    lambda2: float | None = None,
    mu_h: float = MU_H,
) -> ComplementLowerBoundReport:
    """Return the v1.3H diagonal complement lower-bound report."""

    resolved = default_level2_config() if config is None else config
    resolved_lambda2 = natural_lambda2() if lambda2 is None else float(lambda2)
    required = required_dirac_lower_bound(resolved_lambda2, mu_h)
    inventory = diagonal_mode_inventory(resolved)
    first = first_diagonal_complement_mode(resolved)
    formal_zero_count = sum(row.formal_zero_candidate for row in inventory)
    coordinate_zero_count = int(resolved.boundary_params.get("zero_mode_count", 3))
    formal_indices = {row.basis_index for row in inventory if row.formal_zero_candidate}
    coordinate_indices = set(range(coordinate_zero_count))
    alignment = "OPEN_ALIGNMENT_GAP" if formal_indices != coordinate_indices else "FINITE_COORDINATE_ALIGNED"
    lower = float(first.dirac_squared_diagonal)
    return ComplementLowerBoundReport(
        model_level=DIRAC_PROXY_LEVEL_2,
        k_max=int(resolved.k_max),
        a=float(resolved.a),
        basis_size=len(inventory),
        coordinate_zero_mode_count=coordinate_zero_count,
        formal_zero_candidate_count=int(formal_zero_count),
        lambda2=resolved_lambda2,
        required_dirac_lower_bound=float(required),
        first_complement_mode=first,
        finite_coordinate_complement_lower_bound=lower,
        margin=lower - float(required),
        passes_required_bound=bool(lower >= required),
        formal_coordinate_alignment_status=alignment,
        bound_status="FINITE_DIAGONAL_BOUND_PASSES" if lower >= required else "FINITE_DIAGONAL_BOUND_FAILS",
        theorem_complete=False,
        mode_inventory=inventory,
        assumptions=(
            "The finite Level 2 coordinate zero block has dimension three.",
            "The diagonal complement bound is computed before sector coupling.",
            "The natural cutoff Lambda^2 = 1/(4*pi) defines d_required.",
        ),
        limitations=(
            "The finite diagonal lower bound is not the full infinite-basis bound.",
            "Formal zero-mode labels are not yet proven identical to the finite coordinate protected block.",
            "The complete twisted Dirac operator may modify the diagonal spectrum.",
        ),
    )


def _jsonable(value: Any) -> Any:
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if hasattr(value, "__dataclass_fields__"):
        return _jsonable(asdict(value))
    return value


def export_diagonal_complement_bound_json(path: str | Path) -> None:
    """Export the diagonal complement lower-bound report as JSON."""

    Path(path).write_text(json.dumps(_jsonable(build_complement_lower_bound_report()), indent=2, sort_keys=True) + "\n")


def export_diagonal_complement_bound_markdown(path: str | Path) -> None:
    """Export the diagonal complement lower-bound report as Markdown."""

    report = build_complement_lower_bound_report()
    first = report.first_complement_mode
    lines = [
        "# BHSM v1.3H Diagonal Complement Lower-Bound Report",
        "",
        f"Bound status: `{report.bound_status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Formal/coordinate alignment: `{report.formal_coordinate_alignment_status}`",
        "",
        "## Bound Summary",
        "",
        "| Quantity | Value |",
        "| --- | --- |",
        f"| Required Dirac lower bound | `{report.required_dirac_lower_bound}` |",
        f"| Finite coordinate complement lower bound | `{report.finite_coordinate_complement_lower_bound}` |",
        f"| Margin | `{report.margin}` |",
        f"| Passes required bound | `{report.passes_required_bound}` |",
        "",
        "## First Complement Mode",
        "",
        "| basis index | sector | k | j | q | chirality | diagonal D | diagonal D^2 |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
        f"| `{first.basis_index}` | `{first.sector}` | `{first.k}` | `{first.j}` | `{first.q}` | `{first.chirality}` | `{first.dirac_diagonal_value}` | `{first.dirac_squared_diagonal}` |",
        "",
        "## First Ten Inventory Rows",
        "",
        "| basis index | sector | k | j | q | chi | D^2 | coordinate protected | formal zero candidate | complement included |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in sorted(report.mode_inventory, key=lambda item: (item.dirac_squared_diagonal, item.basis_index))[:10]:
        lines.append(
            f"| `{row.basis_index}` | `{row.sector}` | `{row.k}` | `{row.j}` | `{row.q}` | `{row.chirality}` | `{row.dirac_squared_diagonal}` | `{row.coordinate_protected}` | `{row.formal_zero_candidate}` | `{row.included_in_complement_bound}` |"
        )
    lines.extend(["", "## Limitations", "", *[f"- {item}" for item in report.limitations], ""])
    Path(path).write_text("\n".join(lines))
