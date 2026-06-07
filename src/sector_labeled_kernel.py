"""BHSM v1.3K sector-labeled protected-kernel construction.

This module builds the formal protected kernel from the sector-labeled BHSM
zero-mode candidates rather than from the first coordinates of the finite
basis. It is an audit scaffold and does not alter frozen predictions.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np

from boundary_derivation import default_boundaries, omega_from_boundary
from ht_operator import default_level2_config
from positivity import complement_projector, orthogonal_projector
from twisted_dirac import DiracOperatorConfig, build_dirac_basis
from zero_mode_index import protected_family_zero_modes


@dataclass(frozen=True)
class SectorLabeledZeroMode:
    """Formal sector-labeled protected zero mode and its finite coordinate."""

    id: str
    sector: str
    k: int
    j: int
    q: int
    chirality: int
    boundary_condition: str
    omega_value: int
    omega_target: int
    coordinate_index: int | None
    present_in_basis: bool
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class ProtectedKernelVector:
    """Coordinate vector for a sector-labeled protected zero mode."""

    label_id: str
    coordinate_index: int
    vector_norm: float
    nonzero_entries: tuple[int, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class ProtectedKernelProjector:
    """Projector built from protected kernel vectors."""

    name: str
    coordinate_indices: tuple[int, ...]
    rank: int
    matrix_shape: tuple[int, int]
    idempotent: bool
    orthogonal_to_complement: bool
    sector_distribution: dict[str, int]
    limitations: tuple[str, ...]


def sector_labeled_zero_modes(config: DiracOperatorConfig | None = None) -> tuple[SectorLabeledZeroMode, ...]:
    """Return formal lepton/up/down zero modes with finite basis coordinates."""

    resolved = default_level2_config() if config is None else config
    basis = build_dirac_basis(
        resolved.k_max,
        sectors=resolved.sectors,
        include_chirality=resolved.include_chirality,
    )
    lookup = {
        (mode.sector, mode.k, mode.j, mode.q, mode.chirality): index
        for index, mode in enumerate(basis)
    }
    boundaries = default_boundaries()
    rows = []
    for candidate in protected_family_zero_modes():
        boundary = boundaries[candidate.sector]
        omega = omega_from_boundary(candidate.k, candidate.j, boundary)
        index = lookup.get((candidate.sector, candidate.k, candidate.j, candidate.q, candidate.chirality))
        rows.append(
            SectorLabeledZeroMode(
                id=candidate.id,
                sector=candidate.sector,
                k=candidate.k,
                j=candidate.j,
                q=candidate.q,
                chirality=candidate.chirality,
                boundary_condition=candidate.boundary_condition,
                omega_value=int(omega),
                omega_target=int(boundary.target),
                coordinate_index=index,
                present_in_basis=index is not None,
                limitations=(
                    "The heavy (0,0) zero-mode label is formal sector data.",
                    "Presence in the finite basis does not by itself prove coordinate protection.",
                ),
            )
        )
    return tuple(rows)


def protected_kernel_vectors(config: DiracOperatorConfig | None = None) -> tuple[ProtectedKernelVector, ...]:
    """Return coordinate unit vectors for present formal protected labels."""

    resolved = default_level2_config() if config is None else config
    basis_size = len(build_dirac_basis(resolved.k_max, sectors=resolved.sectors, include_chirality=resolved.include_chirality))
    vectors = []
    for label in sector_labeled_zero_modes(resolved):
        if label.coordinate_index is None:
            continue
        vector = np.zeros(basis_size)
        vector[label.coordinate_index] = 1.0
        vectors.append(
            ProtectedKernelVector(
                label_id=label.id,
                coordinate_index=int(label.coordinate_index),
                vector_norm=float(np.linalg.norm(vector)),
                nonzero_entries=(int(label.coordinate_index),),
                limitations=("Coordinate unit vector for the formal sector-labeled zero-mode scaffold.",),
            )
        )
    return tuple(vectors)


def protected_kernel_basis_matrix(config: DiracOperatorConfig | None = None) -> np.ndarray:
    """Return an orthonormal coordinate-basis matrix for the formal kernel."""

    resolved = default_level2_config() if config is None else config
    basis_size = len(build_dirac_basis(resolved.k_max, sectors=resolved.sectors, include_chirality=resolved.include_chirality))
    vectors = protected_kernel_vectors(resolved)
    matrix = np.zeros((basis_size, len(vectors)))
    for col, vector in enumerate(vectors):
        matrix[vector.coordinate_index, col] = 1.0
    return matrix


def formal_protected_projector(config: DiracOperatorConfig | None = None) -> ProtectedKernelProjector:
    """Return projector metadata for the formal sector-labeled kernel."""

    resolved = default_level2_config() if config is None else config
    labels = sector_labeled_zero_modes(resolved)
    basis = protected_kernel_basis_matrix(resolved)
    p0 = orthogonal_projector(basis)
    p_perp = complement_projector(basis)
    indices = tuple(vector.coordinate_index for vector in protected_kernel_vectors(resolved))
    distribution: dict[str, int] = {}
    for label in labels:
        if label.coordinate_index is not None:
            distribution[label.sector] = distribution.get(label.sector, 0) + 1
    return ProtectedKernelProjector(
        name="P0_formal_sector_labeled",
        coordinate_indices=indices,
        rank=int(np.linalg.matrix_rank(p0)),
        matrix_shape=tuple(int(value) for value in p0.shape),
        idempotent=bool(np.allclose(p0 @ p0, p0, atol=1e-10)),
        orthogonal_to_complement=bool(np.allclose(p0 @ p_perp, np.zeros_like(p0), atol=1e-10)),
        sector_distribution=distribution,
        limitations=(
            "Projector is built from formal sector-labeled coordinates.",
            "It does not alter the Level 2 matrix construction.",
        ),
    )


def coordinate_first_projector(config: DiracOperatorConfig | None = None) -> ProtectedKernelProjector:
    """Return projector metadata for the legacy first-coordinate block."""

    resolved = default_level2_config() if config is None else config
    basis = build_dirac_basis(resolved.k_max, sectors=resolved.sectors, include_chirality=resolved.include_chirality)
    zero_count = int(resolved.boundary_params.get("zero_mode_count", 3))
    matrix = np.zeros((len(basis), zero_count))
    for col in range(zero_count):
        matrix[col, col] = 1.0
    p0 = orthogonal_projector(matrix)
    p_perp = complement_projector(matrix)
    distribution: dict[str, int] = {}
    for index in range(zero_count):
        mode = basis[index]
        distribution[mode.sector] = distribution.get(mode.sector, 0) + 1
    return ProtectedKernelProjector(
        name="P0_coordinate_first",
        coordinate_indices=tuple(range(zero_count)),
        rank=int(np.linalg.matrix_rank(p0)),
        matrix_shape=tuple(int(value) for value in p0.shape),
        idempotent=bool(np.allclose(p0 @ p0, p0, atol=1e-10)),
        orthogonal_to_complement=bool(np.allclose(p0 @ p_perp, np.zeros_like(p0), atol=1e-10)),
        sector_distribution=distribution,
        limitations=(
            "Legacy Level 2 scaffold protects the first coordinate positions.",
            "v1.3J showed this is not the same as the formal sector-labeled kernel.",
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


def export_sector_labeled_kernel_json(path: str | Path) -> None:
    """Export formal kernel labels and projector metadata."""

    payload = {
        "sector_labeled_zero_modes": sector_labeled_zero_modes(),
        "protected_kernel_vectors": protected_kernel_vectors(),
        "formal_projector": formal_protected_projector(),
        "coordinate_first_projector": coordinate_first_projector(),
        "theorem_complete": False,
    }
    Path(path).write_text(json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n")


def export_sector_labeled_kernel_markdown(path: str | Path) -> None:
    """Export formal kernel labels and projector metadata as Markdown."""

    formal = formal_protected_projector()
    old = coordinate_first_projector()
    lines = [
        "# BHSM v1.3K Sector-Labeled Kernel Report",
        "",
        "Theorem complete: `False`",
        "",
        "## Formal Protected Kernel",
        "",
        "| ID | Sector | k | j | q | chi | Omega | Target | Coordinate | Present |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for label in sector_labeled_zero_modes():
        lines.append(
            f"| `{label.id}` | `{label.sector}` | `{label.k}` | `{label.j}` | `{label.q}` | `{label.chirality}` | `{label.omega_value}` | `{label.omega_target}` | `{label.coordinate_index}` | `{label.present_in_basis}` |"
        )
    lines.extend(
        [
            "",
            "## Projector Comparison",
            "",
            "| Projector | Coordinates | Rank | Idempotent | Orthogonal to complement | Sector distribution |",
            "| --- | --- | --- | --- | --- | --- |",
            f"| `{old.name}` | `{old.coordinate_indices}` | `{old.rank}` | `{old.idempotent}` | `{old.orthogonal_to_complement}` | `{old.sector_distribution}` |",
            f"| `{formal.name}` | `{formal.coordinate_indices}` | `{formal.rank}` | `{formal.idempotent}` | `{formal.orthogonal_to_complement}` | `{formal.sector_distribution}` |",
            "",
        ]
    )
    Path(path).write_text("\n".join(lines))
