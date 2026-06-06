"""Phase 9A finite-basis twisted Dirac proxy scaffold.

This is a structurally richer proxy than the scalar Berger spectrum: modes
carry chirality, sector labels, Hopf charge, degeneracy labels, and
sector-dependent twist shifts. It is still not the full twisted Dirac spectrum.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Mapping

import numpy as np

from boundary_derivation import default_boundaries

DIRAC_PROXY_LEVEL = "DIRAC_PROXY_LEVEL_1"
DIRAC_PROXY_LEVEL_2 = "DIRAC_PROXY_LEVEL_2"
DEFAULT_SECTORS = ("lepton", "up", "down")
CHIRALITIES = (-1, 1)


@dataclass(frozen=True, order=True)
class DiracMode:
    """Finite-basis mode label for the Level 1 twisted Dirac proxy."""

    k: int
    j: int
    q: int
    chirality: int
    sector: str
    degeneracy: int


@dataclass(frozen=True)
class DiracOperatorConfig:
    """Configuration for the Level 2 finite-basis twisted Dirac matrix."""

    a: float
    k_max: int
    sectors: tuple[str, ...] = DEFAULT_SECTORS
    twist_params: Mapping[str, object] = field(default_factory=dict)
    boundary_params: Mapping[str, object] = field(default_factory=dict)
    include_chirality: bool = True
    operator_level: str = DIRAC_PROXY_LEVEL_2


def hopf_charge(k: int, j: int) -> int:
    """Return q = k - 2j."""

    return k - 2 * j


def build_dirac_basis(
    k_max: int,
    sectors: Iterable[str] | None = None,
    include_chirality: bool = True,
) -> list[DiracMode]:
    """Build a finite Dirac proxy basis on ``0 <= j <= floor(k/2)``."""

    if k_max < 0:
        raise ValueError("k_max must be nonnegative")
    selected_sectors = tuple(DEFAULT_SECTORS if sectors is None else sectors)
    allowed = set(DEFAULT_SECTORS)
    unknown = set(selected_sectors) - allowed
    if unknown:
        raise ValueError(f"unknown sectors: {sorted(unknown)}")
    chiralities = CHIRALITIES if include_chirality else (1,)
    basis: list[DiracMode] = []
    degeneracy = 0
    for sector in selected_sectors:
        for chirality in chiralities:
            for k in range(k_max + 1):
                for j in range((k // 2) + 1):
                    basis.append(
                        DiracMode(
                            k=k,
                            j=j,
                            q=hopf_charge(k, j),
                            chirality=chirality,
                            sector=sector,
                            degeneracy=degeneracy,
                        )
                    )
                    degeneracy += 1
    return basis


def twist_shift(mode: DiracMode, twist_params: Mapping[str, object] | None) -> float:
    """Return sector/chirality/boundary twist shift for a mode."""

    params = dict(twist_params or {})
    sector_shifts = dict(params.get("sector_shifts", {}))
    chirality_shift = float(params.get("chirality_shift", 0.0))
    hopf_shift = float(params.get("hopf_shift", 0.0))
    boundary_strength = float(params.get("boundary_strength", 0.0))
    if boundary_strength < 0:
        raise ValueError("boundary_strength must be nonnegative")
    boundary = default_boundaries()[mode.sector]
    boundary_residual = (
        boundary.fiber_weight * mode.q + boundary.base_weight * mode.j - boundary.target
    )
    return float(
        sector_shifts.get(mode.sector, 0.0)
        + chirality_shift * mode.chirality
        + hopf_shift * mode.q
        + boundary_strength * boundary_residual
    )


def dirac_eigenvalue_proxy(
    mode: DiracMode,
    a: float,
    twist_params: Mapping[str, object] | None,
) -> float:
    """Return a signed Level 1 Dirac proxy eigenvalue."""

    if a <= 0:
        raise ValueError("a must be positive")
    params = dict(twist_params or {})
    dirac_scale = float(params.get("dirac_scale", 1.0))
    if dirac_scale <= 0:
        raise ValueError("dirac_scale must be positive")
    radial = np.sqrt((a * mode.q) ** 2 + (2 * mode.j + 1) * (mode.k + 1))
    return float(mode.chirality * dirac_scale * radial + twist_shift(mode, params))


def dirac_squared_spectrum(
    basis: Iterable[DiracMode],
    a: float,
    twist_params: Mapping[str, object] | None,
) -> np.ndarray:
    """Return sorted records for the squared Dirac proxy spectrum."""

    rows = []
    for index, mode in enumerate(basis):
        eig = dirac_eigenvalue_proxy(mode, a, twist_params)
        rows.append(
            {
                "index": index,
                "mode": mode,
                "dirac_eigenvalue": eig,
                "eigenvalue": float(eig**2),
                "model_level": DIRAC_PROXY_LEVEL,
            }
        )
    return np.array(
        sorted(rows, key=lambda row: (row["eigenvalue"], row["index"])),
        dtype=object,
    )


def zero_mode_subspace(
    basis: Iterable[DiracMode],
    index_count: int = 3,
) -> np.ndarray:
    """Return coordinate basis for protected zero modes inserted explicitly."""

    basis_list = list(basis)
    if index_count < 0:
        raise ValueError("index_count must be nonnegative")
    if index_count > len(basis_list):
        raise ValueError("index_count exceeds basis size")
    zero_modes = np.zeros((len(basis_list), index_count))
    for col in range(index_count):
        zero_modes[col, col] = 1.0
    return zero_modes


def complement_spectrum(
    spectrum: Iterable[Mapping[str, object]],
    zero_modes: np.ndarray,
) -> np.ndarray:
    """Return sorted spectrum records excluding protected zero-mode indices."""

    protected = set(np.where(np.asarray(zero_modes).any(axis=1))[0])
    rows = [row for row in spectrum if int(row["index"]) not in protected]
    return np.array(sorted(rows, key=lambda row: (row["eigenvalue"], row["index"])), dtype=object)


def level2_spin_connection_term(mode: DiracMode, config: DiracOperatorConfig) -> float:
    """Return a diagonal spin-connection proxy term."""

    strength = float(config.twist_params.get("spin_connection_strength", 0.05))
    return strength * (mode.k + 1.0) * mode.chirality


def level2_hopf_twist_term(mode: DiracMode, config: DiracOperatorConfig) -> float:
    """Return a diagonal Hopf-twist proxy term."""

    strength = float(config.twist_params.get("hopf_twist_strength", 0.03))
    return strength * mode.q


def level2_boundary_term(mode: DiracMode, config: DiracOperatorConfig) -> float:
    """Return a boundary residual term from action-linked boundary records."""

    strength = float(config.boundary_params.get("boundary_strength", 0.04))
    if strength < 0:
        raise ValueError("boundary_strength must be nonnegative")
    boundary = default_boundaries()[mode.sector]
    residual = boundary.fiber_weight * mode.q + boundary.base_weight * mode.j - boundary.target
    return strength * residual


def level2_chirality_term(mode: DiracMode, config: DiracOperatorConfig) -> float:
    """Return a diagonal chirality splitting term."""

    strength = float(config.twist_params.get("chirality_strength", 0.02))
    return strength * mode.chirality


def level2_sector_coupling_term(
    mode_i: DiracMode,
    mode_j: DiracMode,
    config: DiracOperatorConfig,
) -> float:
    """Return a symmetric off-diagonal sector/boundary coupling."""

    if mode_i == mode_j:
        return 0.0
    sector_strength = float(config.boundary_params.get("sector_coupling", 0.01))
    boundary_strength = float(config.boundary_params.get("offdiag_boundary_coupling", 0.005))
    if sector_strength < 0 or boundary_strength < 0:
        raise ValueError("off-diagonal coupling strengths must be nonnegative")
    if mode_i.k != mode_j.k or mode_i.j != mode_j.j or mode_i.chirality != mode_j.chirality:
        return 0.0
    if mode_i.sector == mode_j.sector:
        return 0.0
    boundary_i = default_boundaries()[mode_i.sector]
    boundary_j = default_boundaries()[mode_j.sector]
    residual_i = boundary_i.fiber_weight * mode_i.q + boundary_i.base_weight * mode_i.j - boundary_i.target
    residual_j = boundary_j.fiber_weight * mode_j.q + boundary_j.base_weight * mode_j.j - boundary_j.target
    return float(sector_strength + boundary_strength / (1.0 + abs(residual_i) + abs(residual_j)))


def build_level2_dirac_matrix(config: DiracOperatorConfig) -> np.ndarray:
    """Build an explicit Hermitian Level 2 finite-basis Dirac proxy matrix."""

    if config.operator_level != DIRAC_PROXY_LEVEL_2:
        raise ValueError("DiracOperatorConfig.operator_level must be DIRAC_PROXY_LEVEL_2")
    basis = build_dirac_basis(
        k_max=config.k_max,
        sectors=config.sectors,
        include_chirality=config.include_chirality,
    )
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
    zero_count = int(config.boundary_params.get("zero_mode_count", 3))
    if zero_count < 0 or zero_count > size:
        raise ValueError("zero_mode_count must fit inside basis")
    matrix[:zero_count, :] = 0.0
    matrix[:, :zero_count] = 0.0
    complement_floor = float(config.boundary_params.get("complement_floor", 1.1))
    if complement_floor < 0:
        raise ValueError("complement_floor must be nonnegative")
    for idx in range(zero_count, size):
        matrix[idx, idx] += complement_floor
    return matrix


def level2_dirac_squared_spectrum(config: DiracOperatorConfig) -> np.ndarray:
    """Return sorted squared eigenvalues of the Level 2 Dirac proxy matrix."""

    matrix = build_level2_dirac_matrix(config)
    eigenvalues = np.linalg.eigvalsh(matrix)
    rows = [
        {
            "index": index,
            "mode": None,
            "dirac_eigenvalue": float(value),
            "eigenvalue": float(value**2),
            "model_level": DIRAC_PROXY_LEVEL_2,
        }
        for index, value in enumerate(eigenvalues)
    ]
    sorted_rows = sorted(rows, key=lambda row: (row["eigenvalue"], row["index"]))
    for new_index, row in enumerate(sorted_rows):
        row["index"] = new_index
    return np.array(sorted_rows, dtype=object)
