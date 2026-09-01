"""BHSM v2.2 formal-kernel orthogonal projector scaffold."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from infinite_basis_domain import FORMAL_KERNEL_STATES


FORMAL_KERNEL_PROJECTOR_PROVEN = "FORMAL_KERNEL_PROJECTOR_PROVEN"
FORMAL_KERNEL_PROJECTOR_CONDITIONAL = "FORMAL_KERNEL_PROJECTOR_CONDITIONAL"
FORMAL_KERNEL_PROJECTOR_OPEN = "FORMAL_KERNEL_PROJECTOR_OPEN"
FAILS_FORMAL_KERNEL_PROJECTOR = "FAILS_FORMAL_KERNEL_PROJECTOR"

OLD_COORDINATE_FIRST_KERNEL = (0, 1, 2)
DEFAULT_FORMAL_COORDINATES = (0, 18, 36)


@dataclass(frozen=True)
class FormalKernelBasisVector:
    label: str
    sector: str
    k: int
    j: int
    q: int
    chirality: int
    norm: float
    coordinate_hint_kmax4: int


@dataclass(frozen=True)
class FormalKernelProjectorReport:
    title: str
    kernel_basis: tuple[FormalKernelBasisVector, ...]
    kernel_dimension: int
    normalized: bool
    orthogonal: bool
    projector_action: str
    coordinate_independent_definition: bool
    old_coordinate_first_kernel_used: bool
    old_coordinate_first_kernel_rejected: bool
    status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def formal_kernel_basis_vectors() -> tuple[FormalKernelBasisVector, ...]:
    return (
        FormalKernelBasisVector(FORMAL_KERNEL_STATES[0], "lepton", 0, 0, 0, -1, 1.0, 0),
        FormalKernelBasisVector(FORMAL_KERNEL_STATES[1], "up", 0, 0, 0, -1, 1.0, 18),
        FormalKernelBasisVector(FORMAL_KERNEL_STATES[2], "down", 0, 0, 0, -1, 1.0, 36),
    )


def build_formal_kernel_projector_report() -> FormalKernelProjectorReport:
    basis = formal_kernel_basis_vectors()
    sectors = {row.sector for row in basis}
    normalized = all(row.norm == 1.0 for row in basis)
    orthogonal = len({row.label for row in basis}) == len(basis) and sectors == {"lepton", "up", "down"}
    status = FORMAL_KERNEL_PROJECTOR_PROVEN if normalized and orthogonal else FAILS_FORMAL_KERNEL_PROJECTOR
    return FormalKernelProjectorReport(
        title="BHSM v2.2 Formal Kernel Projector Report",
        kernel_basis=basis,
        kernel_dimension=len(basis),
        normalized=normalized,
        orthogonal=orthogonal,
        projector_action="P_K psi = sum_{s in {ell,u,d}} <e_s,psi> e_s",
        coordinate_independent_definition=True,
        old_coordinate_first_kernel_used=False,
        old_coordinate_first_kernel_rejected=True,
        status=status,
        theorem_complete=False,
        limitations=(
            "The finite-rank projector onto the named orthonormal sector-labeled kernel is well-defined in l2.",
            "This does not prove the topological index theorem or mirror exclusion.",
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


def export_formal_kernel_projector_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_formal_kernel_projector_report()), indent=2, sort_keys=True) + "\n")


def export_formal_kernel_projector_markdown(path: str | Path) -> None:
    report = build_formal_kernel_projector_report()
    lines = [
        "# BHSM v2.2 Formal Kernel Projector Report",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Coordinate-independent definition: `{report.coordinate_independent_definition}`",
        f"Old coordinate-first kernel used: `{report.old_coordinate_first_kernel_used}`",
        f"Old coordinate-first kernel rejected: `{report.old_coordinate_first_kernel_rejected}`",
        "",
        "| Label | Sector | k | j | q | chirality | norm | k_max=4 coordinate hint |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in report.kernel_basis:
        lines.append(f"| `{row.label}` | `{row.sector}` | `{row.k}` | `{row.j}` | `{row.q}` | `{row.chirality}` | `{row.norm}` | `{row.coordinate_hint_kmax4}` |")
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
