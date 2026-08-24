"""Constraint-tangent force tests for a same-action replacement saddle.

The functions in this module separate a covector into its physical tangent
part and a constraint-normal part.  They never choose a representative of a
set-valued reset relation.  All adjoints are Hermitian adjoints, so the same
identities apply to real and complex finite-dimensional realizations.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from scipy.linalg import null_space


def _matrix(value: Any, name: str) -> np.ndarray:
    result = np.asarray(value)
    if result.ndim != 2:
        raise ValueError(f"{name} must be a matrix")
    if not np.isfinite(result).all():
        raise ValueError(f"{name} must be finite")
    return result


def _vector(value: Any, size: int, name: str) -> np.ndarray:
    result = np.asarray(value)
    if result.ndim != 1 or result.shape[0] != size:
        raise ValueError(f"{name} must be a vector of length {size}")
    if not np.isfinite(result).all():
        raise ValueError(f"{name} must be finite")
    return result


def constraint_tangent_basis(
    constraint_jacobian: Any,
    *,
    rcond: float | None = None,
) -> np.ndarray:
    """Return an orthonormal basis for ``ker(constraint_jacobian)``."""

    jacobian = _matrix(constraint_jacobian, "constraint_jacobian")
    if rcond is not None and (not np.isfinite(rcond) or rcond < 0.0):
        raise ValueError("rcond must be finite and nonnegative")
    if jacobian.shape[0] == 0:
        return np.eye(jacobian.shape[1], dtype=jacobian.dtype)
    return null_space(jacobian, rcond=rcond)


def projected_force(
    force_covector: Any,
    constraint_jacobian: Any,
    *,
    rcond: float | None = None,
) -> dict[str, Any]:
    """Project an ambient force covector onto the constraint tangent.

    If ``N`` has orthonormal columns spanning ``ker J``, constrained
    stationarity is exactly ``N^* q = 0``.  The ambient condition ``q=0`` is
    stronger and is not invariant under a change of KKT multiplier.
    """

    jacobian = _matrix(constraint_jacobian, "constraint_jacobian")
    force = _vector(force_covector, jacobian.shape[1], "force_covector")
    tangent_basis = constraint_tangent_basis(jacobian, rcond=rcond)
    coordinates = tangent_basis.conj().T @ force
    tangent = tangent_basis @ coordinates
    normal = force - tangent
    return {
        "tangent_basis": tangent_basis,
        "tangent_coordinates": coordinates,
        "tangent_component": tangent,
        "normal_component": normal,
        "ambient_norm": float(np.linalg.norm(force)),
        "tangent_norm": float(np.linalg.norm(coordinates)),
        "normal_norm": float(np.linalg.norm(normal)),
        "kernel_residual_norm": float(np.linalg.norm(jacobian @ tangent_basis)),
        "orthonormality_residual_norm": float(
            np.linalg.norm(
                tangent_basis.conj().T @ tangent_basis
                - np.eye(tangent_basis.shape[1])
            )
        ),
    }


def kkt_force_decomposition(
    force_covector: Any,
    constraint_jacobian: Any,
    *,
    rcond: float | None = None,
) -> dict[str, Any]:
    """Decompose a force into tangent force and multiplier-absorbable load.

    The returned multiplier shift solves ``J^* delta_lambda=-q_normal``.
    Consequently ``q+J^*delta_lambda`` equals the tangent component up to
    roundoff.  Redundant constraint rows are allowed; the minimum-norm
    multiplier is used.
    """

    projection = projected_force(
        force_covector, constraint_jacobian, rcond=rcond
    )
    jacobian = _matrix(constraint_jacobian, "constraint_jacobian")
    normal = projection["normal_component"]
    if jacobian.shape[0] == 0:
        multiplier = np.zeros(0, dtype=np.result_type(jacobian, normal))
    else:
        multiplier = np.linalg.lstsq(
            jacobian.conj().T, -normal, rcond=rcond
        )[0]
    normal_residual = normal + jacobian.conj().T @ multiplier
    shifted_force = np.asarray(force_covector) + jacobian.conj().T @ multiplier
    return {
        **projection,
        "multiplier_shift": multiplier,
        "normal_absorption_residual": normal_residual,
        "normal_absorption_residual_norm": float(np.linalg.norm(normal_residual)),
        "shifted_force": shifted_force,
        "shifted_force_minus_tangent_residual_norm": float(
            np.linalg.norm(shifted_force - projection["tangent_component"])
        ),
    }


def linearized_tangent_correction(
    hessian: Any,
    force_covector: Any,
    constraint_jacobian: Any,
    *,
    rcond: float | None = None,
    hermitian_tolerance: float = 1.0e-11,
    invertibility_tolerance: float = 1.0e-12,
) -> dict[str, Any]:
    """Solve the linearized saddle equation on the physical tangent.

    This is the finite-dimensional identity

    ``(N^* H N) delta_xi = -N^* q``.

    It is a geometry/reset KKT Hessian test.  It is not the later
    pair-plus-contact source Hessian.
    """

    jacobian = _matrix(constraint_jacobian, "constraint_jacobian")
    force = _vector(force_covector, jacobian.shape[1], "force_covector")
    hess = _matrix(hessian, "hessian")
    if hess.shape != (jacobian.shape[1], jacobian.shape[1]):
        raise ValueError("hessian has the wrong square shape")
    if not np.isfinite(hermitian_tolerance) or hermitian_tolerance < 0.0:
        raise ValueError("hermitian_tolerance must be finite and nonnegative")
    if not np.isfinite(invertibility_tolerance) or invertibility_tolerance < 0.0:
        raise ValueError("invertibility_tolerance must be finite and nonnegative")
    hermitian_residual = float(np.linalg.norm(hess - hess.conj().T))
    scale = max(1.0, float(np.linalg.norm(hess)))
    if hermitian_residual > hermitian_tolerance * scale:
        raise ValueError("hessian must be Hermitian within tolerance")
    tangent_basis = constraint_tangent_basis(jacobian, rcond=rcond)
    reduced = tangent_basis.conj().T @ hess @ tangent_basis
    reduced = 0.5 * (reduced + reduced.conj().T)
    projected_initial = tangent_basis.conj().T @ force
    eigenvalues = np.linalg.eigvalsh(reduced)
    if eigenvalues.size == 0:
        tangent_coordinates = np.zeros(0, dtype=np.result_type(hess, force))
        minimum_absolute_eigenvalue = float("inf")
    else:
        minimum_absolute_eigenvalue = float(np.min(np.abs(eigenvalues)))
        reduced_scale = max(1.0, float(np.max(np.abs(eigenvalues))))
        if minimum_absolute_eigenvalue <= invertibility_tolerance * reduced_scale:
            raise np.linalg.LinAlgError("reduced tangent Hessian is not certified invertible")
        tangent_coordinates = np.linalg.solve(reduced, -projected_initial)
    correction = tangent_basis @ tangent_coordinates
    projected_residual = tangent_basis.conj().T @ (force + hess @ correction)
    inertia_tolerance = invertibility_tolerance * max(
        1.0, float(np.max(np.abs(eigenvalues))) if eigenvalues.size else 1.0
    )
    return {
        "tangent_basis": tangent_basis,
        "reduced_hessian": reduced,
        "reduced_hessian_eigenvalues": eigenvalues,
        "minimum_absolute_reduced_eigenvalue": minimum_absolute_eigenvalue,
        "positive_eigenvalue_count": int(np.sum(eigenvalues > inertia_tolerance)),
        "negative_eigenvalue_count": int(np.sum(eigenvalues < -inertia_tolerance)),
        "center_eigenvalue_count": int(np.sum(np.abs(eigenvalues) <= inertia_tolerance)),
        "positive_definite_on_tangent": bool(
            eigenvalues.size == 0 or np.all(eigenvalues > inertia_tolerance)
        ),
        "projected_initial_force": projected_initial,
        "tangent_coordinates": tangent_coordinates,
        "ambient_correction": correction,
        "projected_linearized_residual": projected_residual,
        "projected_linearized_residual_norm": float(np.linalg.norm(projected_residual)),
        "hermitian_residual_norm": hermitian_residual,
    }


def bordered_kkt_correction(
    hessian: Any,
    force_covector: Any,
    constraint_jacobian: Any,
    *,
    hermitian_tolerance: float = 1.0e-11,
    invertibility_tolerance: float = 1.0e-12,
) -> dict[str, Any]:
    """Solve the bordered linearized KKT system without inverting ``H``.

    The system is

    ``[[H,J^*],[J,0]] [delta_y,delta_lambda]^T=[-q,0]^T``.

    No inverse of the kinetic/Hessian block is formed.  A unique bordered
    solve requires independent constraint rows and a nonsingular reduced
    Hessian.  The nullspace implementation remains the primary quotient
    formulation; this routine supplies an algebraically independent
    cross-check.
    """

    jacobian = _matrix(constraint_jacobian, "constraint_jacobian")
    force = _vector(force_covector, jacobian.shape[1], "force_covector")
    hess = _matrix(hessian, "hessian")
    dimension = jacobian.shape[1]
    constraints = jacobian.shape[0]
    if hess.shape != (dimension, dimension):
        raise ValueError("hessian has the wrong square shape")
    hermitian_residual = float(np.linalg.norm(hess - hess.conj().T))
    scale = max(1.0, float(np.linalg.norm(hess)))
    if hermitian_residual > hermitian_tolerance * scale:
        raise ValueError("hessian must be Hermitian within tolerance")
    singular_values = np.linalg.svd(jacobian, compute_uv=False)
    row_scale = max(1.0, float(singular_values[0]) if singular_values.size else 1.0)
    rank = int(np.sum(singular_values > invertibility_tolerance * row_scale))
    if rank != constraints:
        raise np.linalg.LinAlgError("constraint rows are not certified independent")
    zero = np.zeros((constraints, constraints), dtype=np.result_type(hess, jacobian))
    bordered = np.block([[hess, jacobian.conj().T], [jacobian, zero]])
    rhs = np.concatenate((
        -force,
        np.zeros(constraints, dtype=np.result_type(force, jacobian)),
    ))
    bordered_singular_values = np.linalg.svd(bordered, compute_uv=False)
    bordered_scale = max(1.0, float(bordered_singular_values[0]))
    minimum = float(bordered_singular_values[-1])
    if minimum <= invertibility_tolerance * bordered_scale:
        raise np.linalg.LinAlgError("bordered KKT system is not certified invertible")
    solution = np.linalg.solve(bordered, rhs)
    correction = solution[:dimension]
    multiplier = solution[dimension:]
    stationarity_residual = hess @ correction + jacobian.conj().T @ multiplier + force
    constraint_residual = jacobian @ correction
    return {
        "ambient_correction": correction,
        "multiplier_correction": multiplier,
        "stationarity_residual": stationarity_residual,
        "constraint_residual": constraint_residual,
        "stationarity_residual_norm": float(np.linalg.norm(stationarity_residual)),
        "constraint_residual_norm": float(np.linalg.norm(constraint_residual)),
        "constraint_rank": rank,
        "minimum_bordered_singular_value": minimum,
        "bordered_condition_number": float(
            bordered_singular_values[0] / bordered_singular_values[-1]
        ),
        "hermitian_residual_norm": hermitian_residual,
    }


__all__ = [
    "bordered_kkt_correction",
    "constraint_tangent_basis",
    "kkt_force_decomposition",
    "linearized_tangent_correction",
    "projected_force",
]
