"""Domain-parametric common gauge/ghost/rank-16/HS source incidence.

The historical v16.01/v16.04 builders hardwire a periodic temporal
derivative.  The retained local source vertices do not depend on that choice:
they depend only on the realized temporal first derivative/Laplacian, the
history radii, and the source section.  These builders expose precisely that
incidence without selecting a temporal graph, endpoint, source profile, or
quantum state.
"""

from __future__ import annotations

import math

import numpy as np
from scipy.linalg import block_diag, null_space

from bhsm.interface.aether_nonabelian_derham_response_v16_04 import (
    angular_derham_blocks,
)
from bhsm.interface.completion.exact_berger_dirac_cap_obstruction_v14_59 import (
    berger_dirac_block,
    pauli_matrices,
    spin_matrices,
)


def _temporal_matrix(value: np.ndarray, points: int, name: str) -> np.ndarray:
    matrix = np.asarray(value, dtype=complex)
    if matrix.shape != (points, points):
        raise ValueError(f"{name} must have shape ({points}, {points})")
    if not np.all(np.isfinite(matrix)):
        raise ValueError(f"{name} must be finite")
    return matrix


def forward_weyl_squared_operator_and_vertices(
    level: int,
    radii: np.ndarray,
    temporal_first_derivative: np.ndarray,
    profile: np.ndarray,
    *,
    source: str,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Rank-16 Weyl/HS product-Dirac incidence for a realized time graph."""

    n = int(level)
    r = np.asarray(radii, dtype=float)
    section = np.asarray(profile, dtype=float)
    if n < 0 or r.ndim != 1 or section.shape != r.shape or np.any(r <= 0.0):
        raise ValueError("invalid level, radii, or source section")
    points = len(r)
    derivative = _temporal_matrix(
        temporal_first_derivative, points, "temporal first derivative"
    )
    angular_dimension = 2 * (n + 1)
    time_derivative = np.kron(derivative, np.eye(angular_dimension))
    spatial = block_diag(
        *[berger_dirac_block(n, float(radius), 1.0) for radius in r]
    )
    off_diagonal = time_derivative + spatial
    zero = np.zeros_like(off_diagonal)
    dirac = np.block([[zero, off_diagonal], [off_diagonal.conj().T, zero]])
    sigma_z = pauli_matrices()[2]
    spatial_vertex = np.kron(sigma_z, np.eye(n + 1))
    local_spatial = block_diag(
        *[value * spatial_vertex for value in section]
    )
    local_scalar = np.kron(np.diag(section), np.eye(angular_dimension))
    if source == "coexact_gauge":
        first_order_vertex = np.block(
            [[zero, local_spatial], [local_spatial, zero]]
        )
    elif source == "HS":
        first_order_vertex = np.block(
            [[local_scalar, zero], [zero, -local_scalar]]
        )
    else:
        raise ValueError("source must be coexact_gauge or HS")
    operator = dirac @ dirac
    vertex = dirac @ first_order_vertex + first_order_vertex @ dirac
    contact = 2.0 * first_order_vertex @ first_order_vertex
    return operator, vertex, contact


def forward_hs_scalar_operator_and_gauge_vertices(
    level: int,
    radii: np.ndarray,
    temporal_laplacian: np.ndarray,
    profile: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Complex HS-doublet incidence for a realized temporal Laplacian."""

    k = int(level)
    r = np.asarray(radii, dtype=float)
    section = np.asarray(profile, dtype=float)
    if k < 0 or r.ndim != 1 or section.shape != r.shape or np.any(r <= 0.0):
        raise ValueError("invalid level, radii, or source section")
    points = len(r)
    laplacian = _temporal_matrix(
        temporal_laplacian, points, "temporal Laplacian"
    )
    orbital = k + 1
    j_z = spin_matrices(k)[2]
    operator = np.kron(laplacian, np.eye(orbital))
    operator += block_diag(
        *[((k + 1.0) / radius) ** 2 * np.eye(orbital) for radius in r]
    )
    vertex = block_diag(
        *[
            value * (4.0 / radius) * j_z
            for value, radius in zip(section, r, strict=True)
        ]
    )
    contact = block_diag(
        *[2.0 * value**2 * np.eye(orbital) for value in section]
    )
    return operator.astype(complex), vertex.astype(complex), contact.astype(complex)


def _remove_global_scalar_zero(
    operator: np.ndarray,
    vertex: np.ndarray,
    contact: np.ndarray,
    points: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    constant = np.ones((1, points), dtype=complex) / math.sqrt(points)
    basis = null_space(constant)
    return (
        basis.conj().T @ operator @ basis,
        basis.conj().T @ vertex @ basis,
        basis.conj().T @ contact @ basis,
        basis,
    )


def forward_oneform_ghost_matrices(
    level: int,
    radii: np.ndarray,
    temporal_first_derivative: np.ndarray,
    temporal_laplacian: np.ndarray,
    profile: np.ndarray,
) -> dict[str, np.ndarray]:
    """Non-Abelian one-form minus ghost incidence on a realized time graph."""

    n = int(level)
    r = np.asarray(radii, dtype=float)
    section = np.asarray(profile, dtype=float)
    if n < 0 or r.ndim != 1 or section.shape != r.shape or np.any(r <= 0.0):
        raise ValueError("invalid level, radii, or source section")
    points = len(r)
    derivative = _temporal_matrix(
        temporal_first_derivative, points, "temporal first derivative"
    )
    laplacian = _temporal_matrix(
        temporal_laplacian, points, "temporal Laplacian"
    )
    scalar_dimension = n + 1
    vector_dimension = 3 * scalar_dimension
    blocks = [angular_derham_blocks(n, float(radius)) for radius in r]
    scalar_operator = np.kron(laplacian, np.eye(scalar_dimension)) + block_diag(
        *[row["scalar_operator"] for row in blocks]
    )
    spatial_operator = np.kron(laplacian, np.eye(vector_dimension)) + block_diag(
        *[row["vector_operator"] for row in blocks]
    )
    scalar_vertex = block_diag(
        *[value * row["scalar_vertex"] for value, row in zip(section, blocks, strict=True)]
    )
    spatial_vertex = block_diag(
        *[value * row["vector_vertex"] for value, row in zip(section, blocks, strict=True)]
    )
    scalar_contact = block_diag(
        *[value**2 * row["scalar_contact"] for value, row in zip(section, blocks, strict=True)]
    )
    spatial_contact = block_diag(
        *[value**2 * row["vector_contact"] for value, row in zip(section, blocks, strict=True)]
    )
    source_derivative = derivative @ section
    cross = block_diag(
        *[
            -2.0j * value * row["temporal_spatial_injection"].conj().T
            for value, row in zip(source_derivative, blocks, strict=True)
        ]
    )
    scalar_basis = np.eye(points * scalar_dimension, dtype=complex)
    if n == 0:
        scalar_operator, scalar_vertex, scalar_contact, scalar_basis = (
            _remove_global_scalar_zero(
                scalar_operator, scalar_vertex, scalar_contact, points
            )
        )
        cross = scalar_basis.conj().T @ cross
    oneform_operator = block_diag(scalar_operator, spatial_operator)
    oneform_vertex = np.block(
        [[scalar_vertex, cross], [cross.conj().T, spatial_vertex]]
    )
    oneform_contact = block_diag(scalar_contact, spatial_contact)
    return {
        "oneform_operator": oneform_operator,
        "oneform_vertex": oneform_vertex,
        "oneform_contact": oneform_contact,
        "ghost_operator": scalar_operator,
        "ghost_vertex": scalar_vertex,
        "ghost_contact": scalar_contact,
    }


__all__ = [
    "forward_weyl_squared_operator_and_vertices",
    "forward_hs_scalar_operator_and_gauge_vertices",
    "forward_oneform_ghost_matrices",
]
