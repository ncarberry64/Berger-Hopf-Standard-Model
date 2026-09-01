"""BHSM v1.3O coordinate-free formal-kernel subspace scaffold.

This module separates the invariant sector-labeled protected subspace from
its finite Level 2 coordinate realization. It does not alter the frozen BHSM
model or prove the full twisted Dirac / H_T theorem.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

from formal_kernel_action_origin import (
    basis_coordinate_for_sector_zero,
    modes_per_chirality_sector,
)
from formal_kernel_operator import (
    default_formal_kernel_operator_config,
    formal_kernel_coordinates,
)


COORDINATE_FREE_SCAFFOLD = "COORDINATE_FREE_SCAFFOLD"
BASIS_REALIZED = "BASIS_REALIZED"
FINITE_BASIS_VERIFIED = "FINITE_BASIS_VERIFIED"
SEMI_ANALYTIC_BOUND = "SEMI_ANALYTIC_BOUND"
FULL_OPERATOR_PROVEN = "FULL_OPERATOR_PROVEN"
OPEN = "OPEN"


@dataclass(frozen=True)
class FormalKernelSubspace:
    """Coordinate-free protected formal-kernel subspace."""

    name: str
    spanning_states: tuple[str, ...]
    sectors: tuple[str, ...]
    k: int
    j: int
    q: int
    chirality: int
    dimension: int
    status: str
    theorem_complete: bool
    assumptions: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class CoordinateFreeProjector:
    """Coordinate-free projector notation for the protected/complement split."""

    name: str
    protected_subspace: str
    complement_subspace: str
    rank: int
    idempotent_statement: str
    orthogonality_statement: str
    status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class BasisRealizationMap:
    """Finite Level 2 coordinate realization of the formal kernel."""

    k_max: int
    modes_per_chirality_sector: int
    formula: str
    sector_coordinates: dict[str, int]
    realized_coordinates: tuple[int, ...]
    operator_coordinates: tuple[int, ...]
    old_coordinate_first_block: tuple[int, ...]
    matches_current_basis: bool
    avoids_old_coordinate_first_block: bool
    status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def formal_kernel_subspace() -> FormalKernelSubspace:
    """Return the coordinate-free formal-kernel subspace K_formal."""

    states = (
        "|ell,0,0,q=0,chi=-1>",
        "|u,0,0,q=0,chi=-1>",
        "|d,0,0,q=0,chi=-1>",
    )
    return FormalKernelSubspace(
        name="K_formal",
        spanning_states=states,
        sectors=("lepton", "up", "down"),
        k=0,
        j=0,
        q=0,
        chirality=-1,
        dimension=3,
        status=COORDINATE_FREE_SCAFFOLD,
        theorem_complete=False,
        assumptions=(
            "The protected BHSM family labels are the heavy (0,0) sector labels for lepton, up, and down sectors.",
            "The protected chirality convention is chi=-1.",
            "The v1.2 boundary functional supplies the sector labels without using empirical masses.",
        ),
        limitations=(
            "This is the coordinate-free scaffold subspace, not a full index theorem.",
            "Mirror-mode exclusion and the full infinite-basis complement split remain proof obligations.",
        ),
    )


def coordinate_free_projector() -> CoordinateFreeProjector:
    """Return symbolic P_formal and P_perp statements."""

    return CoordinateFreeProjector(
        name="P_formal",
        protected_subspace="K_formal = span{|ell,0,0,q=0,chi=-1>, |u,0,0,q=0,chi=-1>, |d,0,0,q=0,chi=-1>}",
        complement_subspace="H_perp = K_formal^perp",
        rank=3,
        idempotent_statement="P_formal^2 = P_formal",
        orthogonality_statement="P_formal P_perp = 0, P_perp = I - P_formal",
        status=COORDINATE_FREE_SCAFFOLD,
        theorem_complete=False,
        limitations=(
            "The coordinate-free projector is realized in the current finite basis but not proven for the complete Hilbert space.",
        ),
    )


def sector_major_coordinate_formula(k_max: int) -> dict[str, int]:
    """Return the sector-major coordinate formula ell=0, up=2M, down=4M."""

    modes = modes_per_chirality_sector(k_max)
    return {"lepton": 0, "up": 2 * modes, "down": 4 * modes}


def basis_realization_map(k_max: int = 4) -> BasisRealizationMap:
    """Map K_formal into the current Level 2 sector-major coordinate basis."""

    if k_max < 0:
        raise ValueError("k_max must be nonnegative")
    config = default_formal_kernel_operator_config(k_max=k_max)
    formula_coordinates = sector_major_coordinate_formula(k_max)
    derived = {
        sector: basis_coordinate_for_sector_zero(sector, k_max, config.base_config.sectors)
        for sector in ("lepton", "up", "down")
    }
    if formula_coordinates != derived:
        status = OPEN
    else:
        status = BASIS_REALIZED
    operator_coordinates = formal_kernel_coordinates(config)
    realized = tuple(derived[sector] for sector in ("lepton", "up", "down"))
    return BasisRealizationMap(
        k_max=k_max,
        modes_per_chirality_sector=modes_per_chirality_sector(k_max),
        formula="M(k_max)=sum_{k=0}^{k_max}(floor(k/2)+1); ell=0, u=2M, d=4M",
        sector_coordinates=derived,
        realized_coordinates=realized,
        operator_coordinates=operator_coordinates,
        old_coordinate_first_block=(0, 1, 2),
        matches_current_basis=bool(realized == operator_coordinates),
        avoids_old_coordinate_first_block=bool(realized != (0, 1, 2)),
        status=status if realized == operator_coordinates else OPEN,
        theorem_complete=False,
        limitations=(
            "Coordinates are finite-basis labels; K_formal is the coordinate-free object.",
            "The old coordinate-first block is retained only as a regression comparison.",
        ),
    )


def basis_realization_scan(k_max_values: Iterable[int] = (4, 6, 8, 10, 12)) -> tuple[BasisRealizationMap, ...]:
    """Return basis-realization rows for several finite truncations."""

    return tuple(basis_realization_map(int(k_max)) for k_max in k_max_values)


def build_coordinate_free_subspace_report(k_max: int = 4) -> dict[str, Any]:
    """Return the v1.3O coordinate-free subspace report payload."""

    return {
        "title": "BHSM v1.3O Coordinate-Free Formal-Kernel Subspace",
        "subspace": formal_kernel_subspace(),
        "projector": coordinate_free_projector(),
        "basis_realization": basis_realization_map(k_max),
        "basis_realization_scan": basis_realization_scan(),
        "theorem_complete": False,
        "correct_claim": (
            "BHSM v1.3O separates K_formal and H_perp as coordinate-free scaffold "
            "objects and verifies their current finite Level 2 basis realization."
        ),
        "limitations": (
            "This does not prove the full index theorem or complete H_T spectrum.",
            "Finite coordinate checks remain scaffold evidence.",
        ),
    }


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


def export_coordinate_free_subspace_json(path: str | Path) -> None:
    """Export coordinate-free formal-kernel subspace report as JSON."""

    Path(path).write_text(json.dumps(_jsonable(build_coordinate_free_subspace_report()), indent=2, sort_keys=True) + "\n")


def export_coordinate_free_subspace_markdown(path: str | Path) -> None:
    """Export coordinate-free formal-kernel subspace report as Markdown."""

    report = build_coordinate_free_subspace_report()
    subspace: FormalKernelSubspace = report["subspace"]
    projector: CoordinateFreeProjector = report["projector"]
    realization: BasisRealizationMap = report["basis_realization"]
    lines = [
        "# BHSM v1.3O Coordinate-Free Formal-Kernel Subspace",
        "",
        f"Theorem complete: `{report['theorem_complete']}`",
        f"Subspace status: `{subspace.status}`",
        f"Basis realization status: `{realization.status}`",
        "",
        "## Coordinate-Free Kernel",
        "",
        f"`{projector.protected_subspace}`",
        "",
        f"`{projector.complement_subspace}`",
        "",
        "| sector | state |",
        "| --- | --- |",
    ]
    for sector, state in zip(subspace.sectors, subspace.spanning_states):
        lines.append(f"| `{sector}` | `{state}` |")
    lines.extend(
        [
            "",
            "## Basis Realization",
            "",
            f"Formula: `{realization.formula}`",
            "",
            "| k_max | M(k_max) | lepton | up | down | operator coordinates | matches |",
            "| --- | --- | --- | --- | --- | --- | --- |",
            f"| `{realization.k_max}` | `{realization.modes_per_chirality_sector}` | `{realization.sector_coordinates['lepton']}` | `{realization.sector_coordinates['up']}` | `{realization.sector_coordinates['down']}` | `{realization.operator_coordinates}` | `{realization.matches_current_basis}` |",
            "",
            "## Realization Scan",
            "",
            "| k_max | M(k_max) | realized coordinates | matches current basis |",
            "| --- | --- | --- | --- |",
        ]
    )
    for row in report["basis_realization_scan"]:
        lines.append(
            f"| `{row.k_max}` | `{row.modes_per_chirality_sector}` | `{row.realized_coordinates}` | `{row.matches_current_basis}` |"
        )
    lines.extend(["", "## Limitations", "", *[f"- {item}" for item in report["limitations"]], ""])
    Path(path).write_text("\n".join(lines))
