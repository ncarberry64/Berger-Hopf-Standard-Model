"""BHSM v1.3N semi-analytic complement-bound scaffold."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np

from formal_kernel_operator import (
    DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL,
    coordinate_modes,
    default_formal_kernel_operator_config,
    formal_kernel_coordinates,
)
from formal_kernel_regression import formal_kernel_lower_bound_row, formal_kernel_sector_coupling_row
from spectral_bounds import required_dirac_lower_bound
from spectral_gap import MU_H, natural_lambda2
from twisted_dirac import (
    DiracMode,
    level2_boundary_term,
    level2_chirality_term,
    level2_hopf_twist_term,
    level2_spin_connection_term,
)


@dataclass(frozen=True)
class SemiAnalyticComplementMode:
    """One semi-analytic diagonal complement candidate."""

    coordinate: int
    sector: str
    k: int
    j: int
    q: int
    chirality: int
    diagonal_dirac_value: float
    diagonal_square: float
    protected_formal_kernel: bool
    old_coordinate_first_protected: bool
    explanation: str


@dataclass(frozen=True)
class SemiAnalyticComplementBound:
    """Semi-analytic complement lower-bound scaffold result."""

    model_level: str
    protected_coordinates: tuple[int, ...]
    old_coordinate_first_coordinates: tuple[int, ...]
    first_diagonal_complement_mode: SemiAnalyticComplementMode
    diagonal_lower_bound: float
    gershgorin_lower_bound: float
    structured_relative_lower_bound: float
    exact_finite_lower_bound: float
    required_dirac_lower_bound: float
    clears_required_bound: bool
    status: str
    theorem_complete: bool
    assumptions: tuple[str, ...]
    limitations: tuple[str, ...]


def diagonal_level2_value(mode: DiracMode, complement_floor: float = 1.1, a: float = 1.0) -> float:
    """Return the Level 2 diagonal formula for a nonprotected complement mode."""

    config = default_formal_kernel_operator_config(a=a).base_config
    radial = np.sqrt((a * mode.q) ** 2 + (2 * mode.j + 1) * (mode.k + 1))
    scale = float(config.twist_params.get("dirac_scale", 2.0))
    return float(
        mode.chirality * scale * radial
        + level2_spin_connection_term(mode, config)
        + level2_hopf_twist_term(mode, config)
        + level2_boundary_term(mode, config)
        + level2_chirality_term(mode, config)
        + complement_floor
    )


def diagonal_complement_modes(k_max: int = 4, a: float = 1.0) -> tuple[SemiAnalyticComplementMode, ...]:
    """Return sorted diagonal complement modes after removing formal kernel."""

    config = default_formal_kernel_operator_config(k_max=k_max, a=a)
    protected = set(formal_kernel_coordinates(config))
    old = {0, 1, 2}
    rows = []
    for coordinate, mode in enumerate(coordinate_modes(config)):
        if coordinate in protected:
            continue
        value = diagonal_level2_value(mode, complement_floor=float(config.base_config.boundary_params["complement_floor"]), a=a)
        rows.append(
            SemiAnalyticComplementMode(
                coordinate=coordinate,
                sector=mode.sector,
                k=mode.k,
                j=mode.j,
                q=mode.q,
                chirality=mode.chirality,
                diagonal_dirac_value=value,
                diagonal_square=float(value**2),
                protected_formal_kernel=False,
                old_coordinate_first_protected=coordinate in old,
                explanation=(
                    "Old coordinate-first lepton modes are complement states unless they are the formal sector-labeled heavy mode."
                    if coordinate in {1, 2}
                    else "Finite Level 2 formal-kernel complement state."
                ),
            )
        )
    return tuple(sorted(rows, key=lambda row: (row.diagonal_square, row.coordinate)))


def build_semi_analytic_complement_bound(k_max: int = 4, a: float = 1.0) -> SemiAnalyticComplementBound:
    """Build the semi-analytic complement lower-bound scaffold."""

    config = default_formal_kernel_operator_config(k_max=k_max, a=a)
    diagonal_modes = diagonal_complement_modes(k_max, a)
    first = diagonal_modes[0]
    lower = formal_kernel_lower_bound_row(config)
    sector = formal_kernel_sector_coupling_row(config)
    required = required_dirac_lower_bound(natural_lambda2(), MU_H)
    conservative = min(lower.gershgorin_lower_bound, sector.structured_lower_bound, lower.direct_finite_spectrum_lower_bound)
    return SemiAnalyticComplementBound(
        model_level=DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL,
        protected_coordinates=formal_kernel_coordinates(config),
        old_coordinate_first_coordinates=(0, 1, 2),
        first_diagonal_complement_mode=first,
        diagonal_lower_bound=first.diagonal_square,
        gershgorin_lower_bound=lower.gershgorin_lower_bound,
        structured_relative_lower_bound=sector.structured_lower_bound,
        exact_finite_lower_bound=lower.direct_finite_spectrum_lower_bound,
        required_dirac_lower_bound=required,
        clears_required_bound=bool(conservative >= required),
        status="SEMI_ANALYTIC_BOUND_SCAFFOLD_PASSES" if conservative >= required else "SEMI_ANALYTIC_BOUND_FAILS",
        theorem_complete=False,
        assumptions=(
            "The Level 2 diagonal formula is evaluated symbolically for complement modes.",
            "The formal sector-labeled kernel is removed before the complement is scanned.",
            "Sector-coupling control uses the corrected formal-kernel structured relative-bound row.",
        ),
        limitations=(
            "The bound is semi-analytic inside DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL, not the full twisted Dirac operator.",
            "Gershgorin and structured-relative estimates remain finite-basis scaffold bounds.",
            "The full H_T theorem remains open.",
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


def export_semi_analytic_complement_bound_json(path: str | Path) -> None:
    """Export semi-analytic complement-bound scaffold as JSON."""

    Path(path).write_text(json.dumps(_jsonable(build_semi_analytic_complement_bound()), indent=2, sort_keys=True) + "\n")


def export_semi_analytic_complement_bound_markdown(path: str | Path) -> None:
    """Export semi-analytic complement-bound scaffold as Markdown."""

    report = build_semi_analytic_complement_bound()
    first = report.first_diagonal_complement_mode
    lines = [
        "# BHSM v1.3N Semi-Analytic Complement-Bound Scaffold",
        "",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Status: `{report.status}`",
        "",
        "## Protected Kernel",
        "",
        f"- Formal protected coordinates: `{report.protected_coordinates}`",
        f"- Old coordinate-first block: `{report.old_coordinate_first_coordinates}`",
        "",
        "## First Diagonal Complement Mode",
        "",
        "| coordinate | sector | k | j | q | chi | diagonal D | diagonal D^2 | old coordinate-first protected |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        f"| `{first.coordinate}` | `{first.sector}` | `{first.k}` | `{first.j}` | `{first.q}` | `{first.chirality}` | `{first.diagonal_dirac_value}` | `{first.diagonal_square}` | `{first.old_coordinate_first_protected}` |",
        "",
        "## Lower-Bound Table",
        "",
        "| Bound | Value | Clears required bound |",
        "| --- | --- | --- |",
        f"| Required Dirac lower bound | `{report.required_dirac_lower_bound}` | `target` |",
        f"| Diagonal complement lower bound | `{report.diagonal_lower_bound}` | `{report.diagonal_lower_bound >= report.required_dirac_lower_bound}` |",
        f"| Gershgorin lower bound | `{report.gershgorin_lower_bound}` | `{report.gershgorin_lower_bound >= report.required_dirac_lower_bound}` |",
        f"| Structured relative lower bound | `{report.structured_relative_lower_bound}` | `{report.structured_relative_lower_bound >= report.required_dirac_lower_bound}` |",
        f"| Exact finite lower bound | `{report.exact_finite_lower_bound}` | `{report.exact_finite_lower_bound >= report.required_dirac_lower_bound}` |",
        "",
        "## Why Old Coordinate-First Lepton Modes Are Not Protected",
        "",
        "Coordinates `(1,2)` are lepton-sector complement states in the formal-kernel variant. They are not the sector-labeled heavy `(0,0)` protected states for up and down sectors.",
        "",
        "## Limitations",
        "",
        *[f"- {item}" for item in report.limitations],
        "",
    ]
    Path(path).write_text("\n".join(lines))
