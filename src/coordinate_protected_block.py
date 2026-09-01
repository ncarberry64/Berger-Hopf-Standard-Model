"""BHSM v1.3J finite coordinate-protected block audit."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ht_operator import default_level2_config
from sector_coupling_bounds import level2_sector_coupling_dirac_block
from spectral_gap import heat_lift, natural_lambda2
from twisted_dirac import DiracOperatorConfig, build_dirac_basis, build_level2_dirac_matrix


@dataclass(frozen=True)
class CoordinateProtectedState:
    """One coordinate-basis state in the finite Level 2 protected block."""

    coordinate_index: int
    sector: str
    k: int
    j: int
    q: int
    chirality: int
    coordinate_protected: bool
    dirac_squared: float
    heat_lift_preserves: bool
    sector_coupling_vanishes: bool
    protection_mechanism: str
    limitations: tuple[str, ...]


def coordinate_protected_states(config: DiracOperatorConfig | None = None) -> tuple[CoordinateProtectedState, ...]:
    """Return the finite coordinate-protected block states."""

    resolved = default_level2_config() if config is None else config
    basis = build_dirac_basis(
        resolved.k_max,
        sectors=resolved.sectors,
        include_chirality=resolved.include_chirality,
    )
    zero_count = int(resolved.boundary_params.get("zero_mode_count", 3))
    dirac = build_level2_dirac_matrix(resolved)
    sector_block = level2_sector_coupling_dirac_block(resolved)
    rows = []
    for index in range(zero_count):
        mode = basis[index]
        d2 = float((dirac.T @ dirac)[index, index])
        sector_zero = bool(
            np.allclose(sector_block[index, :], 0.0)
            and np.allclose(sector_block[:, index], 0.0)
        )
        rows.append(
            CoordinateProtectedState(
                coordinate_index=index,
                sector=mode.sector,
                k=mode.k,
                j=mode.j,
                q=mode.q,
                chirality=mode.chirality,
                coordinate_protected=True,
                dirac_squared=d2,
                heat_lift_preserves=bool(abs(d2) <= 1e-12 and abs(heat_lift(d2, natural_lambda2())) <= 1e-12),
                sector_coupling_vanishes=sector_zero,
                protection_mechanism="finite Level 2 coordinate zero block",
                limitations=(
                    "Coordinate protection is by finite-matrix construction.",
                    "The coordinate block is not automatically identical to the formal sector-labeled kernel.",
                ),
            )
        )
    return tuple(rows)
