"""Finite-basis positivity utilities for Gate 28D.

The constructions here are proxy linear algebra audits. They formalize a
sufficient positive-semidefinite profile condition on the complement of the
protected zero-mode subspace; they do not compute the full twisted Dirac
``H_T`` spectrum.
"""

from __future__ import annotations

from typing import Iterable

import numpy as np

from berger_spectrum import berger_lambda
from spectral_gap import MU_H, heat_lift, natural_lambda2


def _as_matrix(matrix: np.ndarray) -> np.ndarray:
    arr = np.asarray(matrix, dtype=float)
    if arr.ndim != 2 or arr.shape[0] != arr.shape[1]:
        raise ValueError("matrix must be square")
    return arr


def _basis_matrix(zero_mode_basis: np.ndarray) -> np.ndarray:
    basis = np.asarray(zero_mode_basis, dtype=float)
    if basis.ndim == 1:
        basis = basis.reshape((-1, 1))
    if basis.ndim != 2:
        raise ValueError("zero_mode_basis must be a vector or a 2D matrix")
    return basis


def _orthonormal_basis(zero_mode_basis: np.ndarray, tol: float = 1e-12) -> np.ndarray:
    basis = _basis_matrix(zero_mode_basis)
    if basis.shape[1] == 0:
        return basis
    q, r = np.linalg.qr(basis)
    keep = np.abs(np.diag(r)) > tol
    return q[:, keep]


def is_symmetric(matrix: np.ndarray, tol: float = 1e-10) -> bool:
    """Return True if ``matrix`` is symmetric/Hermitian to tolerance."""

    arr = _as_matrix(matrix)
    return bool(np.allclose(arr, arr.T.conj(), atol=tol))


def min_eigenvalue(matrix: np.ndarray) -> float:
    """Return the minimum eigenvalue of the Hermitian part of ``matrix``."""

    arr = _as_matrix(matrix)
    hermitian = 0.5 * (arr + arr.T.conj())
    return float(np.linalg.eigvalsh(hermitian)[0])


def is_psd(matrix: np.ndarray, tol: float = 1e-10) -> bool:
    """Return True if ``matrix`` is symmetric/Hermitian positive semidefinite."""

    return bool(is_symmetric(matrix, tol=tol) and min_eigenvalue(matrix) >= -tol)


def orthogonal_projector(zero_mode_basis: np.ndarray) -> np.ndarray:
    """Return the orthogonal projector onto the supplied zero-mode span."""

    basis = _basis_matrix(zero_mode_basis)
    q = _orthonormal_basis(basis)
    if q.shape[1] == 0:
        return np.zeros((basis.shape[0], basis.shape[0]))
    return q @ q.T.conj()


def complement_projector(zero_mode_basis: np.ndarray) -> np.ndarray:
    """Return the projector onto the orthogonal complement of zero modes."""

    p0 = orthogonal_projector(zero_mode_basis)
    return np.eye(p0.shape[0]) - p0


def _complement_basis(zero_mode_basis: np.ndarray, tol: float = 1e-10) -> np.ndarray:
    p_perp = complement_projector(zero_mode_basis)
    eigenvalues, eigenvectors = np.linalg.eigh(0.5 * (p_perp + p_perp.T.conj()))
    keep = eigenvalues > 1.0 - tol
    return eigenvectors[:, keep]


def restrict_to_complement(operator: np.ndarray, zero_mode_basis: np.ndarray) -> np.ndarray:
    """Return ``operator`` represented on the zero-mode orthogonal complement."""

    arr = _as_matrix(operator)
    basis = _basis_matrix(zero_mode_basis)
    if arr.shape[0] != basis.shape[0]:
        raise ValueError("operator and zero_mode_basis dimensions differ")
    comp = _complement_basis(basis)
    return comp.T.conj() @ arr @ comp


def psd_barrier_from_q(q_matrix: np.ndarray) -> np.ndarray:
    """Return the positive-semidefinite barrier ``Q^dagger Q``."""

    q = np.asarray(q_matrix, dtype=float)
    if q.ndim != 2:
        raise ValueError("q_matrix must be two-dimensional")
    return q.T.conj() @ q


def compensated_barrier(
    q_matrix: np.ndarray,
    zero_mode_basis: np.ndarray,
    zero_mode_shift: float = 0.0,
) -> np.ndarray:
    """Return ``Q^dagger Q - zero_mode_shift * Pi_0``.

    The subtraction is confined to the protected zero-mode projector. The
    resulting operator is intended to be tested on ``H_perp``.
    """

    if zero_mode_shift < 0:
        raise ValueError("zero_mode_shift must be nonnegative")
    barrier = psd_barrier_from_q(q_matrix)
    p0 = orthogonal_projector(zero_mode_basis)
    if barrier.shape != p0.shape:
        raise ValueError("q_matrix and zero_mode_basis dimensions differ")
    return barrier - zero_mode_shift * p0


def gap_condition_with_operator(
    base_operator: np.ndarray,
    profile_operator: np.ndarray,
    zero_mode_basis: np.ndarray,
    mu_h: float,
) -> dict[str, float | bool]:
    """Evaluate the restricted complement gap for base plus profile operator."""

    base = _as_matrix(base_operator)
    profile = _as_matrix(profile_operator)
    if base.shape != profile.shape:
        raise ValueError("base_operator and profile_operator dimensions differ")
    if mu_h <= 0:
        raise ValueError("mu_h must be positive")
    restricted_base = restrict_to_complement(base, zero_mode_basis)
    restricted_profile = restrict_to_complement(profile, zero_mode_basis)
    restricted_total = restricted_base + restricted_profile
    base_min = min_eigenvalue(restricted_base)
    profile_min = min_eigenvalue(restricted_profile)
    total_min = min_eigenvalue(restricted_total)
    return {
        "restricted_base_min_eigenvalue": base_min,
        "restricted_profile_min_eigenvalue": profile_min,
        "restricted_min_eigenvalue": total_min,
        "margin": total_min - mu_h,
        "passes": bool(total_min >= mu_h),
    }


def finite_berger_modes(n_max: int) -> list[tuple[int, int]]:
    """Return finite proxy modes ``0 <= k <= n_max`` and ``0 <= j <= k``."""

    if n_max < 0:
        raise ValueError("n_max must be nonnegative")
    return [(k, j) for k in range(n_max + 1) for j in range(k + 1)]


def diagonal_proxy_operator(
    modes: Iterable[tuple[int, int]],
    *,
    a: float = 1.0,
    lambda2: float | None = None,
    mu_h: float = MU_H,
) -> np.ndarray:
    """Build the diagonal heat-lifted Berger proxy operator."""

    resolved_lambda2 = natural_lambda2() if lambda2 is None else lambda2
    if resolved_lambda2 <= 0:
        raise ValueError("lambda2 must be positive")
    values = [heat_lift(berger_lambda(k, j, a=a), resolved_lambda2, mu_h=mu_h) for k, j in modes]
    return np.diag(values)


def zero_mode_basis_from_modes(modes: Iterable[tuple[int, int]]) -> np.ndarray:
    """Return coordinate vectors for modes with zero Berger proxy eigenvalue."""

    mode_list = list(modes)
    indices = [idx for idx, (k, j) in enumerate(mode_list) if berger_lambda(k, j) == 0]
    basis = np.zeros((len(mode_list), len(indices)))
    for col, idx in enumerate(indices):
        basis[idx, col] = 1.0
    return basis
