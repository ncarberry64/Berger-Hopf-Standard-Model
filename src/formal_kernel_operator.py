"""BHSM v1.3L corrected Level 2 formal-kernel operator variant.

This module keeps the legacy coordinate-first Level 2 scaffold intact and
builds a separate variant whose protected block is the formal sector-labeled
kernel identified in v1.3K. It does not alter frozen BHSM predictions.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from ht_operator import default_level2_config
from sector_labeled_kernel import coordinate_first_projector, sector_labeled_zero_modes
from twisted_dirac import (
    DIRAC_PROXY_LEVEL_2,
    DEFAULT_SECTORS,
    DiracMode,
    DiracOperatorConfig,
    build_dirac_basis,
    level2_boundary_term,
    level2_chirality_term,
    level2_hopf_twist_term,
    level2_sector_coupling_term,
    level2_spin_connection_term,
)


DIRAC_PROXY_LEVEL_2_COORDINATE_FIRST = "DIRAC_PROXY_LEVEL_2_COORDINATE_FIRST"
DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL = "DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL"


@dataclass(frozen=True)
class FormalKernelOperatorConfig:
    """Configuration for the corrected formal-kernel Level 2 variant."""

    base_config: DiracOperatorConfig
    operator_variant: str = DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL
    protected_coordinates: tuple[int, ...] = ()
    protection_method: str = "formal_sector_labeled_projection"
    theorem_complete: bool = False
    limitations: tuple[str, ...] = (
        "The corrected operator is still a finite-basis Level 2 scaffold.",
        "It does not prove the full twisted Dirac or H_T theorem.",
    )


@dataclass(frozen=True)
class FormalKernelProtectionTerm:
    """Metadata for the projection term that protects formal kernel states."""

    name: str
    protected_coordinates: tuple[int, ...]
    protected_sectors: tuple[str, ...]
    projector_rank: int
    idempotent: bool
    orthogonal_to_complement: bool
    old_coordinate_first_coordinates: tuple[int, ...]
    avoids_old_lepton_only_modes: bool
    limitations: tuple[str, ...]


def default_formal_kernel_operator_config(
    k_max: int = 4,
    a: float = 1.0,
    sectors: tuple[str, ...] = DEFAULT_SECTORS,
) -> FormalKernelOperatorConfig:
    """Return the default v1.3L corrected operator configuration."""

    base = default_level2_config(k_max=k_max, a=a, sectors=sectors)
    protected = tuple(
        int(mode.coordinate_index)
        for mode in sector_labeled_zero_modes(base)
        if mode.coordinate_index is not None
    )
    return FormalKernelOperatorConfig(base_config=base, protected_coordinates=protected)


def formal_kernel_coordinates(config: FormalKernelOperatorConfig | DiracOperatorConfig | None = None) -> tuple[int, ...]:
    """Return formal sector-labeled kernel coordinates for ``config``."""

    if config is None:
        return default_formal_kernel_operator_config().protected_coordinates
    base = config.base_config if isinstance(config, FormalKernelOperatorConfig) else config
    return tuple(
        int(mode.coordinate_index)
        for mode in sector_labeled_zero_modes(base)
        if mode.coordinate_index is not None
    )


def formal_kernel_basis_matrix(config: FormalKernelOperatorConfig | DiracOperatorConfig | None = None) -> np.ndarray:
    """Return coordinate unit-vector basis for the formal protected kernel."""

    base = (
        default_level2_config()
        if config is None
        else config.base_config
        if isinstance(config, FormalKernelOperatorConfig)
        else config
    )
    basis_size = len(build_dirac_basis(base.k_max, sectors=base.sectors, include_chirality=base.include_chirality))
    coordinates = formal_kernel_coordinates(base)
    matrix = np.zeros((basis_size, len(coordinates)))
    for col, index in enumerate(coordinates):
        matrix[index, col] = 1.0
    return matrix


def formal_kernel_projectors(
    config: FormalKernelOperatorConfig | DiracOperatorConfig | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Return ``(P0, P_perp)`` for the formal sector-labeled kernel."""

    basis = formal_kernel_basis_matrix(config)
    p0 = basis @ basis.T
    return p0, np.eye(p0.shape[0]) - p0


def protection_term(config: FormalKernelOperatorConfig | None = None) -> FormalKernelProtectionTerm:
    """Return metadata for the v1.3L formal-kernel protection term."""

    resolved = default_formal_kernel_operator_config() if config is None else config
    base = resolved.base_config
    labels = sector_labeled_zero_modes(base)
    coordinates = formal_kernel_coordinates(base)
    p0, p_perp = formal_kernel_projectors(base)
    old = coordinate_first_projector(base)
    return FormalKernelProtectionTerm(
        name="P0_formal_sector_labeled",
        protected_coordinates=coordinates,
        protected_sectors=tuple(label.sector for label in labels),
        projector_rank=int(np.linalg.matrix_rank(p0)),
        idempotent=bool(np.allclose(p0 @ p0, p0, atol=1e-10)),
        orthogonal_to_complement=bool(np.allclose(p0 @ p_perp, np.zeros_like(p0), atol=1e-10)),
        old_coordinate_first_coordinates=old.coordinate_indices,
        avoids_old_lepton_only_modes=bool(set(coordinates).isdisjoint({1, 2})),
        limitations=(
            "The projection is a corrected Level 2 scaffold term.",
            "A full action derivation of this projection remains open.",
        ),
    )


def _unprotected_level2_dirac_matrix(config: DiracOperatorConfig) -> np.ndarray:
    """Build Level 2 matrix before inserting any protected zero block."""

    if config.operator_level != DIRAC_PROXY_LEVEL_2:
        raise ValueError("base config must use DIRAC_PROXY_LEVEL_2")
    basis = build_dirac_basis(config.k_max, sectors=config.sectors, include_chirality=config.include_chirality)
    size = len(basis)
    matrix = np.zeros((size, size), dtype=float)
    scale = float(config.twist_params.get("dirac_scale", 2.0))
    if scale <= 0:
        raise ValueError("dirac_scale must be positive")
    for idx, mode in enumerate(basis):
        radial = np.sqrt((config.a * mode.q) ** 2 + (2 * mode.j + 1) * (mode.k + 1))
        matrix[idx, idx] = (
            mode.chirality * scale * radial
            + level2_spin_connection_term(mode, config)
            + level2_hopf_twist_term(mode, config)
            + level2_boundary_term(mode, config)
            + level2_chirality_term(mode, config)
        )
    for i, mode_i in enumerate(basis):
        for j in range(i + 1, size):
            coupling = level2_sector_coupling_term(mode_i, basis[j], config)
            matrix[i, j] = coupling
            matrix[j, i] = coupling
    return matrix


def build_formal_kernel_dirac_matrix(config: FormalKernelOperatorConfig | None = None) -> np.ndarray:
    """Build the corrected Level 2 Dirac matrix protecting the formal kernel."""

    resolved = default_formal_kernel_operator_config() if config is None else config
    base = resolved.base_config
    matrix = _unprotected_level2_dirac_matrix(base)
    size = matrix.shape[0]
    coordinates = tuple(resolved.protected_coordinates or formal_kernel_coordinates(base))
    if len(coordinates) != 3:
        raise ValueError("formal-kernel variant requires exactly three protected coordinates")
    if any(index < 0 or index >= size for index in coordinates):
        raise ValueError("formal protected coordinate is outside the basis")
    complement_floor = float(base.boundary_params.get("complement_floor", 1.1))
    if complement_floor < 0:
        raise ValueError("complement_floor must be nonnegative")
    protected = set(coordinates)
    for index in range(size):
        if index not in protected:
            matrix[index, index] += complement_floor
    for index in coordinates:
        matrix[index, :] = 0.0
        matrix[:, index] = 0.0
    return 0.5 * (matrix + matrix.T)


def formal_kernel_sector_coupling_block(config: FormalKernelOperatorConfig | None = None) -> np.ndarray:
    """Return the corrected Dirac-level sector-coupling block."""

    resolved = default_formal_kernel_operator_config() if config is None else config
    base = resolved.base_config
    with_coupling = build_formal_kernel_dirac_matrix(resolved)
    boundary = dict(base.boundary_params)
    boundary["sector_coupling"] = 0.0
    boundary["offdiag_boundary_coupling"] = 0.0
    no_sector = FormalKernelOperatorConfig(
        base_config=DiracOperatorConfig(
            a=base.a,
            k_max=base.k_max,
            sectors=base.sectors,
            twist_params=dict(base.twist_params),
            boundary_params=boundary,
            include_chirality=base.include_chirality,
            operator_level=base.operator_level,
        ),
        protected_coordinates=resolved.protected_coordinates,
    )
    return with_coupling - build_formal_kernel_dirac_matrix(no_sector)


def formal_kernel_level2_spectrum(config: FormalKernelOperatorConfig | None = None) -> np.ndarray:
    """Return sorted squared eigenvalues for the corrected formal-kernel variant."""

    matrix = build_formal_kernel_dirac_matrix(config)
    values = np.linalg.eigvalsh(matrix)
    return np.array(
        sorted(
            (
                {
                    "index": index,
                    "dirac_eigenvalue": float(value),
                    "eigenvalue": float(value**2),
                    "model_level": DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL,
                    "theorem_complete": False,
                }
                for index, value in enumerate(values)
            ),
            key=lambda row: (row["eigenvalue"], row["index"]),
        ),
        dtype=object,
    )


def coordinate_modes(config: FormalKernelOperatorConfig | None = None) -> tuple[DiracMode, ...]:
    """Return basis modes for the corrected operator's base config."""

    resolved = default_formal_kernel_operator_config() if config is None else config
    base = resolved.base_config
    return tuple(build_dirac_basis(base.k_max, sectors=base.sectors, include_chirality=base.include_chirality))


def operator_variant_summary(config: FormalKernelOperatorConfig | None = None) -> dict[str, object]:
    """Return a compact summary of old and corrected Level 2 variants."""

    resolved = default_formal_kernel_operator_config() if config is None else config
    term = protection_term(resolved)
    matrix = build_formal_kernel_dirac_matrix(resolved)
    p0, p_perp = formal_kernel_projectors(resolved)
    d2 = matrix.T @ matrix
    coordinates = set(term.protected_coordinates)
    return {
        "old_variant": DIRAC_PROXY_LEVEL_2_COORDINATE_FIRST,
        "new_variant": DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL,
        "old_protected_coordinates": term.old_coordinate_first_coordinates,
        "formal_protected_coordinates": term.protected_coordinates,
        "protected_sectors": term.protected_sectors,
        "projector_rank": term.projector_rank,
        "projector_idempotent": term.idempotent,
        "projector_orthogonal_to_complement": term.orthogonal_to_complement,
        "matrix_symmetric": bool(np.allclose(matrix, matrix.T, atol=1e-12)),
        "heat_lift_preserves_formal_kernel": bool(
            all(abs(float(d2[index, index])) <= 1e-12 for index in coordinates)
        ),
        "avoids_old_lepton_only_modes": term.avoids_old_lepton_only_modes,
        "p0_pperp_zero": bool(np.allclose(p0 @ p_perp, np.zeros_like(p0), atol=1e-10)),
        "theorem_complete": False,
    }


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


def export_formal_kernel_operator_json(path: str | Path) -> None:
    """Export corrected formal-kernel operator metadata as JSON."""

    payload = {
        "title": "BHSM v1.3L Formal-Kernel Level 2 Operator Variant",
        "summary": operator_variant_summary(),
        "protection_term": protection_term(),
        "theorem_complete": False,
        "correct_claim": (
            "BHSM v1.3L corrects the Level 2 H_T scaffold to protect the formal "
            "sector-labeled kernel rather than the old coordinate-first block."
        ),
    }
    Path(path).write_text(json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n")


def export_formal_kernel_operator_markdown(path: str | Path) -> None:
    """Export corrected formal-kernel operator metadata as Markdown."""

    summary = operator_variant_summary()
    term = protection_term()
    lines = [
        "# BHSM v1.3L Formal-Kernel Level 2 Operator Variant",
        "",
        "Theorem complete: `False`",
        "",
        "## Variant Summary",
        "",
        "| Quantity | Value |",
        "| --- | --- |",
        f"| Old variant | `{summary['old_variant']}` |",
        f"| New variant | `{summary['new_variant']}` |",
        f"| Old protected coordinates | `{summary['old_protected_coordinates']}` |",
        f"| Formal protected coordinates | `{summary['formal_protected_coordinates']}` |",
        f"| Protected sectors | `{summary['protected_sectors']}` |",
        f"| Projector rank | `{summary['projector_rank']}` |",
        f"| Projector idempotent | `{summary['projector_idempotent']}` |",
        f"| P0 P_perp zero | `{summary['p0_pperp_zero']}` |",
        f"| Matrix symmetric | `{summary['matrix_symmetric']}` |",
        f"| Heat lift preserves formal kernel | `{summary['heat_lift_preserves_formal_kernel']}` |",
        f"| Avoids old lepton-only modes `(1,2)` | `{summary['avoids_old_lepton_only_modes']}` |",
        "",
        "## Protection Term",
        "",
        f"`{term.name}` protects `{term.protected_coordinates}` with sectors `{term.protected_sectors}`.",
        "",
        "## Limitations",
        "",
        *[f"- {item}" for item in term.limitations],
        "- The corrected finite-basis variant does not prove the full `H_T` theorem.",
        "",
    ]
    Path(path).write_text("\n".join(lines))
