"""Stable Schur/Weyl value and directional jets on a fixed finite stratum."""

from __future__ import annotations

from typing import Any, Iterable

import numpy as np


def _hermitian_matrix(value: np.ndarray, name: str) -> np.ndarray:
    matrix = np.asarray(value, dtype=complex)
    if (
        matrix.ndim != 2
        or matrix.shape[0] != matrix.shape[1]
        or not np.all(np.isfinite(matrix))
    ):
        raise ValueError(f"{name} must be a finite square matrix")
    if not np.allclose(matrix, matrix.conj().T, rtol=0.0, atol=1.0e-12):
        raise ValueError(f"{name} must be Hermitian")
    return matrix


def _partition(size: int, boundary_indices: Iterable[int]) -> tuple[np.ndarray, np.ndarray]:
    boundary = np.asarray(tuple(boundary_indices), dtype=int)
    if (
        boundary.ndim != 1
        or len(boundary) == 0
        or len(boundary) >= size
        or len(set(boundary.tolist())) != len(boundary)
        or np.any(boundary < 0)
        or np.any(boundary >= size)
    ):
        raise ValueError("a nonempty proper set of unique boundary indices is required")
    mask = np.ones(size, dtype=bool)
    mask[boundary] = False
    return boundary, np.flatnonzero(mask)


def _blocks(
    matrix: np.ndarray,
    boundary: np.ndarray,
    interior: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    return (
        matrix[np.ix_(boundary, boundary)],
        matrix[np.ix_(boundary, interior)],
        matrix[np.ix_(interior, boundary)],
        matrix[np.ix_(interior, interior)],
    )


def schur_weyl_directional_jet(
    operator: np.ndarray,
    first_directional_operator: np.ndarray,
    second_directional_operator: np.ndarray,
    boundary_indices: Iterable[int],
    *,
    z: float,
    coercivity_tolerance: float = 1.0e-12,
) -> dict[str, Any]:
    """Return the Weyl value and first two directional geometry jets.

    The fixed-stratum pencil is ``P(xi,z)=K(xi)-z I``.  The supplied first
    and second matrices are directional derivatives of ``K`` at the base
    point.  Interior linear systems are solved directly; neither the full
    operator nor its interior block is explicitly inverted.
    """

    base = _hermitian_matrix(operator, "operator")
    first = _hermitian_matrix(
        first_directional_operator, "first directional operator"
    )
    second = _hermitian_matrix(
        second_directional_operator, "second directional operator"
    )
    if first.shape != base.shape or second.shape != base.shape:
        raise ValueError("operator jets must have the base shape")
    probe = float(z)
    tolerance = float(coercivity_tolerance)
    if not np.isfinite(probe) or not np.isfinite(tolerance) or tolerance <= 0.0:
        raise ValueError("finite probe and positive coercivity tolerance required")

    boundary, interior = _partition(base.shape[0], boundary_indices)
    pencil = base - probe * np.eye(base.shape[0])
    p_bb, p_bi, p_ib, p_ii = _blocks(pencil, boundary, interior)
    h_bb, h_bi, h_ib, h_ii = _blocks(first, boundary, interior)
    j_bb, j_bi, j_ib, j_ii = _blocks(second, boundary, interior)
    eigenvalues = np.linalg.eigvalsh(p_ii)
    minimum = float(np.min(eigenvalues))
    if minimum <= tolerance:
        raise np.linalg.LinAlgError(
            "shifted interior pencil is not certified coercive"
        )

    poisson_tail = np.linalg.solve(p_ii, p_ib)
    poisson_tail_first = np.linalg.solve(
        p_ii, h_ib - h_ii @ poisson_tail
    )
    poisson_tail_second = np.linalg.solve(
        p_ii,
        j_ib - j_ii @ poisson_tail - 2.0 * h_ii @ poisson_tail_first,
    )
    value = p_bb - p_bi @ poisson_tail
    first_value = (
        h_bb - h_bi @ poisson_tail - p_bi @ poisson_tail_first
    )
    second_value = (
        j_bb
        - j_bi @ poisson_tail
        - 2.0 * h_bi @ poisson_tail_first
        - p_bi @ poisson_tail_second
    )
    return {
        "value": value,
        "first": first_value,
        "second": second_value,
        "Poisson_tail": -poisson_tail,
        "Poisson_tail_first": -poisson_tail_first,
        "Poisson_tail_second": -poisson_tail_second,
        "boundary_indices": boundary,
        "interior_indices": interior,
        "minimum_shifted_interior_eigenvalue": minimum,
        "interior_value_residual_norm": float(
            np.linalg.norm(p_ii @ poisson_tail - p_ib)
        ),
        "interior_first_residual_norm": float(
            np.linalg.norm(
                p_ii @ poisson_tail_first + h_ii @ poisson_tail - h_ib
            )
        ),
        "interior_second_residual_norm": float(
            np.linalg.norm(
                p_ii @ poisson_tail_second
                + 2.0 * h_ii @ poisson_tail_first
                + j_ii @ poisson_tail
                - j_ib
            )
        ),
        "value_hermitian_residual_norm": float(
            np.linalg.norm(value - value.conj().T)
        ),
        "first_hermitian_residual_norm": float(
            np.linalg.norm(first_value - first_value.conj().T)
        ),
        "second_hermitian_residual_norm": float(
            np.linalg.norm(second_value - second_value.conj().T)
        ),
        "explicit_matrix_inverse_formed": False,
    }


__all__ = ["schur_weyl_directional_jet"]
