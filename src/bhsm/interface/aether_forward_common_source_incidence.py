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


def canonical_temporal_form_laplacian(
    temporal_first_derivative: np.ndarray,
    endpoint_form: np.ndarray | None = None,
) -> np.ndarray:
    """Return the form-owned temporal Laplacian on one realized graph.

    The proper-time bulk form owns ``D_tau^* D_tau``.  An endpoint matrix is
    admissible only when it is the Hermitian nonnegative form induced by the
    retained reset/Wentzell graph; it is not a second freely chosen temporal
    operator.
    """

    derivative = np.asarray(temporal_first_derivative, dtype=complex)
    if (
        derivative.ndim != 2
        or derivative.shape[0] != derivative.shape[1]
        or not np.all(np.isfinite(derivative))
    ):
        raise ValueError("finite square temporal first derivative required")
    laplacian = derivative.conj().T @ derivative
    if endpoint_form is None:
        return laplacian
    boundary = np.asarray(endpoint_form, dtype=complex)
    if boundary.shape != derivative.shape or not np.all(np.isfinite(boundary)):
        raise ValueError("endpoint form must match the temporal derivative")
    if not np.allclose(boundary, boundary.conj().T, rtol=0.0, atol=1.0e-12):
        raise ValueError("endpoint form must be Hermitian")
    if float(np.min(np.linalg.eigvalsh(boundary))) < -1.0e-12:
        raise ValueError("endpoint form must be nonnegative")
    return laplacian + boundary


def temporal_form_pair_residual(
    temporal_first_derivative: np.ndarray,
    temporal_laplacian: np.ndarray,
    endpoint_form: np.ndarray | None = None,
) -> float:
    """Return the spectral norm residual of the proper-time form identity."""

    derivative = np.asarray(temporal_first_derivative, dtype=complex)
    laplacian = np.asarray(temporal_laplacian, dtype=complex)
    if laplacian.shape != derivative.shape or not np.all(np.isfinite(laplacian)):
        raise ValueError("temporal Laplacian must match the first derivative")
    owned = canonical_temporal_form_laplacian(derivative, endpoint_form)
    return float(np.linalg.norm(laplacian - owned, ord=2))


def _log_radius_directions(
    radii: np.ndarray,
    first: np.ndarray,
    second: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    r = np.asarray(radii, dtype=float)
    h = np.asarray(first, dtype=float)
    k = np.asarray(second, dtype=float)
    if r.ndim != 1 or h.shape != r.shape or k.shape != r.shape:
        raise ValueError("log-radius directions must match the radii")
    if np.any(r <= 0.0) or not all(
        np.all(np.isfinite(value)) for value in (r, h, k)
    ):
        raise ValueError("finite directions and positive radii required")
    return r, h, k


def _weyl_dirac_and_source_matrix(
    level: int,
    radii: np.ndarray,
    temporal_first_derivative: np.ndarray,
    profile: np.ndarray,
    source: str,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
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
        source_matrix = np.block(
            [[zero, local_spatial], [local_spatial, zero]]
        )
    elif source == "HS":
        source_matrix = np.block(
            [[local_scalar, zero], [zero, -local_scalar]]
        )
    else:
        raise ValueError("source must be coexact_gauge or HS")
    return dirac, source_matrix, spatial


def forward_weyl_squared_operator_and_vertices(
    level: int,
    radii: np.ndarray,
    temporal_first_derivative: np.ndarray,
    profile: np.ndarray,
    *,
    source: str,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Rank-16 Weyl/HS product-Dirac incidence for a realized time graph."""

    dirac, first_order_vertex, _ = _weyl_dirac_and_source_matrix(
        level, radii, temporal_first_derivative, profile, source
    )
    operator = dirac @ dirac
    vertex = dirac @ first_order_vertex + first_order_vertex @ dirac
    contact = 2.0 * first_order_vertex @ first_order_vertex
    return operator, vertex, contact


def forward_weyl_log_radius_jets(
    level: int,
    radii: np.ndarray,
    temporal_first_derivative: np.ndarray,
    profile: np.ndarray,
    first_log_radius: np.ndarray,
    second_log_radius: np.ndarray,
    *,
    source: str,
) -> dict[str, tuple[np.ndarray, np.ndarray, np.ndarray]]:
    """Exact first and mixed second log-radius jets of Weyl incidence."""

    r, h, k = _log_radius_directions(
        radii, first_log_radius, second_log_radius
    )
    dirac, source_matrix, spatial = _weyl_dirac_and_source_matrix(
        level, r, temporal_first_derivative, profile, source
    )
    angular_dimension = 2 * (int(level) + 1)
    spatial_h = block_diag(
        *[
            -h[index]
            * spatial[
                index * angular_dimension : (index + 1) * angular_dimension,
                index * angular_dimension : (index + 1) * angular_dimension,
            ]
            for index in range(len(r))
        ]
    )
    spatial_k = block_diag(
        *[
            -k[index]
            * spatial[
                index * angular_dimension : (index + 1) * angular_dimension,
                index * angular_dimension : (index + 1) * angular_dimension,
            ]
            for index in range(len(r))
        ]
    )
    spatial_hk = block_diag(
        *[
            h[index]
            * k[index]
            * spatial[
                index * angular_dimension : (index + 1) * angular_dimension,
                index * angular_dimension : (index + 1) * angular_dimension,
            ]
            for index in range(len(r))
        ]
    )

    zero = np.zeros_like(spatial)

    def lift(value: np.ndarray) -> np.ndarray:
        return np.block([[zero, value], [value.conj().T, zero]])

    dirac_h = lift(spatial_h)
    dirac_k = lift(spatial_k)
    dirac_hk = lift(spatial_hk)
    base = (
        dirac @ dirac,
        dirac @ source_matrix + source_matrix @ dirac,
        2.0 * source_matrix @ source_matrix,
    )
    first = (
        dirac_h @ dirac + dirac @ dirac_h,
        dirac_h @ source_matrix + source_matrix @ dirac_h,
        np.zeros_like(base[2]),
    )
    mixed_second = (
        dirac_hk @ dirac
        + dirac_h @ dirac_k
        + dirac_k @ dirac_h
        + dirac @ dirac_hk,
        dirac_hk @ source_matrix + source_matrix @ dirac_hk,
        np.zeros_like(base[2]),
    )
    return {"base": base, "first": first, "mixed_second": mixed_second}


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


def forward_hs_scalar_log_radius_jets(
    level: int,
    radii: np.ndarray,
    temporal_laplacian: np.ndarray,
    profile: np.ndarray,
    first_log_radius: np.ndarray,
    second_log_radius: np.ndarray,
) -> dict[str, tuple[np.ndarray, np.ndarray, np.ndarray]]:
    """Exact log-radius jets of complex-HS scalar source incidence."""

    r, h, k = _log_radius_directions(
        radii, first_log_radius, second_log_radius
    )
    section = np.asarray(profile, dtype=float)
    if section.shape != r.shape:
        raise ValueError("source section must match the radii")
    base = forward_hs_scalar_operator_and_gauge_vertices(
        level, r, temporal_laplacian, section
    )
    orbital = int(level) + 1
    if orbital <= 0:
        raise ValueError("nonnegative level required")
    identity = np.eye(orbital)
    j_z = spin_matrices(int(level))[2]
    spatial_blocks = [((orbital / radius) ** 2) * identity for radius in r]
    vertex_blocks = [
        value * (4.0 / radius) * j_z
        for value, radius in zip(section, r, strict=True)
    ]
    first = (
        block_diag(
            *[-2.0 * value * block for value, block in zip(h, spatial_blocks)]
        ).astype(complex),
        block_diag(
            *[-value * block for value, block in zip(h, vertex_blocks)]
        ).astype(complex),
        np.zeros_like(base[2]),
    )
    mixed_second = (
        block_diag(
            *[
                4.0 * left * right * block
                for left, right, block in zip(h, k, spatial_blocks, strict=True)
            ]
        ).astype(complex),
        block_diag(
            *[
                left * right * block
                for left, right, block in zip(h, k, vertex_blocks, strict=True)
            ]
        ).astype(complex),
        np.zeros_like(base[2]),
    )
    return {"base": base, "first": first, "mixed_second": mixed_second}


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


def forward_oneform_ghost_log_radius_jets(
    level: int,
    radii: np.ndarray,
    temporal_first_derivative: np.ndarray,
    temporal_laplacian: np.ndarray,
    profile: np.ndarray,
    first_log_radius: np.ndarray,
    second_log_radius: np.ndarray,
) -> dict[str, dict[str, np.ndarray]]:
    """Exact log-radius jets of one-form minus ghost incidence."""

    n = int(level)
    r, h, k = _log_radius_directions(
        radii, first_log_radius, second_log_radius
    )
    section = np.asarray(profile, dtype=float)
    if n < 0 or section.shape != r.shape:
        raise ValueError("invalid level or source section")
    base = forward_oneform_ghost_matrices(
        n, r, temporal_first_derivative, temporal_laplacian, section
    )
    points = len(r)
    scalar_dimension = n + 1
    vector_dimension = 3 * scalar_dimension
    blocks = [angular_derham_blocks(n, float(radius)) for radius in r]
    scalar_basis = np.eye(points * scalar_dimension, dtype=complex)
    if n == 0:
        constant = np.ones((1, points), dtype=complex) / math.sqrt(points)
        scalar_basis = null_space(constant)

    def derivative_payload(
        operator_scale: np.ndarray,
        vertex_scale: np.ndarray,
    ) -> dict[str, np.ndarray]:
        scalar_operator = block_diag(
            *[
                value * row["scalar_operator"]
                for value, row in zip(operator_scale, blocks, strict=True)
            ]
        )
        spatial_operator = block_diag(
            *[
                value * row["vector_operator"]
                for value, row in zip(operator_scale, blocks, strict=True)
            ]
        )
        scalar_vertex = block_diag(
            *[
                value * source_value * row["scalar_vertex"]
                for value, source_value, row in zip(
                    vertex_scale, section, blocks, strict=True
                )
            ]
        )
        spatial_vertex = block_diag(
            *[
                value * source_value * row["vector_vertex"]
                for value, source_value, row in zip(
                    vertex_scale, section, blocks, strict=True
                )
            ]
        )
        scalar_operator = scalar_basis.conj().T @ scalar_operator @ scalar_basis
        scalar_vertex = scalar_basis.conj().T @ scalar_vertex @ scalar_basis
        cross = np.zeros(
            (scalar_operator.shape[0], points * vector_dimension), dtype=complex
        )
        oneform_operator = block_diag(scalar_operator, spatial_operator)
        oneform_vertex = np.block(
            [[scalar_vertex, cross], [cross.conj().T, spatial_vertex]]
        )
        return {
            "oneform_operator": oneform_operator,
            "oneform_vertex": oneform_vertex,
            "oneform_contact": np.zeros_like(base["oneform_contact"]),
            "ghost_operator": scalar_operator,
            "ghost_vertex": scalar_vertex,
            "ghost_contact": np.zeros_like(base["ghost_contact"]),
        }

    first = derivative_payload(-2.0 * h, -h)
    mixed_second = derivative_payload(4.0 * h * k, h * k)
    return {"base": base, "first": first, "mixed_second": mixed_second}


__all__ = [
    "canonical_temporal_form_laplacian",
    "temporal_form_pair_residual",
    "forward_weyl_squared_operator_and_vertices",
    "forward_weyl_log_radius_jets",
    "forward_hs_scalar_operator_and_gauge_vertices",
    "forward_hs_scalar_log_radius_jets",
    "forward_oneform_ghost_matrices",
    "forward_oneform_ghost_log_radius_jets",
]
