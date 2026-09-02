"""Evaluate the AE4 regulated HS Hessian on a current-C2 form core.

The AE4 owner fixes ``Gamma=-STr E1(ell_star^2 P)/2``.  This module derives
its exact finite-dimensional first and second variations for a positive
generalized form pencil ``K c=lambda M c``.  It then provides the bridge from
the already-derived current-C2 LR/HS vertex and contact forms to an AE4 pure
HS curvature, without importing the historical periodic-cycle kernel.
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np
from scipy.linalg import eigh
from scipy.special import exp1

from bhsm.interface.ae4_stratified_dirac_zeta_induced_owner import ACTION_VERSION


CLASSIFICATION = "AE4_CURRENT_C2_HS_FRECHET_HESSIAN"


def _hermitian(value: object, name: str) -> np.ndarray:
    matrix = np.asarray(value, dtype=complex)
    if (
        matrix.ndim != 2
        or matrix.shape[0] != matrix.shape[1]
        or not np.all(np.isfinite(matrix))
        or not np.allclose(matrix, matrix.conj().T, rtol=0.0, atol=1.0e-11)
    ):
        raise ValueError(f"{name} must be a finite Hermitian matrix")
    return matrix


def _positive(value: float, name: str) -> float:
    result = float(value)
    if not math.isfinite(result) or result <= 0.0:
        raise ValueError(f"{name} must be positive and finite")
    return result


def regulated_kernel(value: object, spectral_length: float = 1.0) -> np.ndarray:
    """Return ``r(lambda)=exp(-ell^2 lambda)/lambda`` for positive lambda."""

    eigenvalue = np.asarray(value, dtype=float)
    ell = _positive(spectral_length, "spectral_length")
    if not np.all(np.isfinite(eigenvalue)) or np.any(eigenvalue <= 0.0):
        raise ValueError("positive finite eigenvalues required")
    return np.exp(-(ell * ell) * eigenvalue) / eigenvalue


def regulated_kernel_divided_difference(
    eigenvalues: object, spectral_length: float = 1.0
) -> np.ndarray:
    """Return the Hermitian Fréchet divided-difference matrix of ``r``."""

    values = np.asarray(eigenvalues, dtype=float)
    ell = _positive(spectral_length, "spectral_length")
    kernel = regulated_kernel(values, ell)
    left = values[:, None]
    right = values[None, :]
    difference = left - right
    result = np.empty_like(difference)
    separated = np.abs(difference) > 1.0e-12 * np.maximum(
        1.0, np.maximum(np.abs(left), np.abs(right))
    )
    numerator = kernel[:, None] - kernel[None, :]
    np.divide(numerator, difference, out=result, where=separated)
    midpoint = 0.5 * (left + right)
    derivative = -np.exp(-(ell * ell) * midpoint) * (
        (ell * ell) / midpoint + 1.0 / (midpoint * midpoint)
    )
    result[~separated] = derivative[~separated]
    return result


def generalized_e1_coordinate_jet(
    *,
    stiffness: object,
    mass: object,
    vertex: object,
    contact: object,
    spectral_length: float = 1.0,
    supertrace_weight: float = -1.0,
) -> dict[str, Any]:
    """Differentiate one generalized AE4 block through second HS order.

    ``K(H)=K+H V+H^2 Q/2`` and ``K x=lambda M x`` with ``M>0``.
    Generalized eigenvectors are M-orthonormal, so ``X^dagger V X`` and
    ``X^dagger Q X`` are the source and contact forms in the spectral Hilbert
    basis.  For ``Gamma=-w Tr E1(ell^2 P)/2`` the exact derivatives are

    ``Gamma_H=(w/2) sum_i r_i V_ii`` and

    ``Gamma_HH=(w/2)[sum_i r_i Q_ii + sum_ij r[1]_ij V_ij V_ji]``.
    """

    K = _hermitian(stiffness, "stiffness")
    M = _hermitian(mass, "mass")
    V = _hermitian(vertex, "vertex")
    Q = _hermitian(contact, "contact")
    if any(matrix.shape != K.shape for matrix in (M, V, Q)):
        raise ValueError("all generalized form matrices must have the same shape")
    ell = _positive(spectral_length, "spectral_length")
    weight = float(supertrace_weight)
    if not math.isfinite(weight) or weight == 0.0:
        raise ValueError("nonzero finite supertrace_weight required")

    eigenvalues, eigenvectors = eigh(K, M, check_finite=True)
    if eigenvalues[0] <= 0.0:
        raise ValueError("positive generalized operator required")
    vertex_spectral = eigenvectors.conj().T @ V @ eigenvectors
    contact_spectral = eigenvectors.conj().T @ Q @ eigenvectors
    kernel = regulated_kernel(eigenvalues, ell)
    divided = regulated_kernel_divided_difference(eigenvalues, ell)
    source = 0.5 * weight * np.sum(kernel * np.diag(vertex_spectral))
    contact_term = np.sum(kernel * np.diag(contact_spectral))
    two_vertex_term = np.sum(divided * vertex_spectral * vertex_spectral.T)
    curvature = 0.5 * weight * (contact_term + two_vertex_term)
    action = -0.5 * weight * np.sum(exp1((ell * ell) * eigenvalues))
    return {
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "dimension": int(K.shape[0]),
        "spectral_length": ell,
        "supertrace_weight": weight,
        "minimum_generalized_eigenvalue": float(eigenvalues[0]),
        "maximum_generalized_eigenvalue": float(eigenvalues[-1]),
        "regulated_action": float(np.real(action)),
        "HS_source": float(np.real(source)),
        "HS_curvature": float(np.real(curvature)),
        "contact_contribution_before_weight": float(np.real(contact_term)),
        "two_vertex_contribution_before_weight": float(np.real(two_vertex_term)),
        "imaginary_source_residual": float(abs(np.imag(source))),
        "imaginary_curvature_residual": float(abs(np.imag(curvature))),
        "generalized_eigenbasis_M_orthonormality_residual": float(
            np.linalg.norm(eigenvectors.conj().T @ M @ eigenvectors - np.eye(K.shape[0]))
        ),
        "explicit_matrix_inverse_formed": False,
        "same_operator_supplies_source_and_curvature": True,
    }


def finite_difference_coordinate_jet(
    *,
    stiffness: object,
    mass: object,
    vertex: object,
    contact: object,
    spectral_length: float = 1.0,
    supertrace_weight: float = -1.0,
    step: float = 2.0e-5,
) -> dict[str, float]:
    """Check the analytic source and Hessian against the owner functional."""

    K = _hermitian(stiffness, "stiffness")
    M = _hermitian(mass, "mass")
    V = _hermitian(vertex, "vertex")
    Q = _hermitian(contact, "contact")
    h = _positive(step, "step")
    ell = _positive(spectral_length, "spectral_length")
    weight = float(supertrace_weight)

    def action(parameter: float) -> float:
        operator = K + parameter * V + 0.5 * parameter * parameter * Q
        eigenvalues = eigh(operator, M, eigvals_only=True, check_finite=True)
        if eigenvalues[0] <= 0.0:
            raise ValueError("finite-difference perturbation left the positive domain")
        return float(-0.5 * weight * np.sum(exp1((ell * ell) * eigenvalues)))

    center = action(0.0)
    plus = action(h)
    minus = action(-h)
    return {
        "centered_first_derivative": (plus - minus) / (2.0 * h),
        "centered_second_derivative": (plus - 2.0 * center + minus) / (h * h),
    }


def claim_boundary() -> dict[str, Any]:
    return {
        "AE4_E1_GENERALIZED_FORM_SOURCE_FORMULA_DERIVED": True,
        "AE4_E1_GENERALIZED_FORM_HESSIAN_FORMULA_DERIVED": True,
        "AE4_CURRENT_C2_BIRTH_LOCAL_GALERKIN_HS_FRECHET_HESSIAN_EVALUATED": True,
        "AE4_CURRENT_C2_BIRTH_LOCAL_CONDITIONED_HS_CURVATURE_POSITIVE": True,
        "AE4_CURRENT_C2_BIRTH_LOCAL_CHIRAL_HS_JETS_EQUAL": True,
        "AE4_HISTORICAL_PERIODIC_CYCLE_HS_KERNEL_TRANSPLANTED": False,
        "AE4_PHYSICAL_ELL_STAR_NUMERICALLY_EVALUATED": False,
        "AE4_MAXIMAL_HISTORY_HS_CALDERON_BLOCK_EVALUATED": False,
        "AE4_BROKEN_LR_HS_SADDLE_DERIVED": False,
        "AE4_PHYSICAL_HS_DIRECTION_SELECTED": False,
        "PHYSICAL_ENCAPSULATION_IDENTIFIED": False,
        "FULL_BHSM_COMPLETE": False,
        "exact_next_calculation": (
            "EXTEND_THE_CURRENT_C2_BIRTH_LOCAL_AE4_HS_HESSIAN_TO_THE_FULL_"
            "FINITE_CORE_THEN_THE_RESET_"
            "GLUED_MAXIMAL_HISTORY_RETARDED_RESOLVENT_AND_COMBINE_ALL_FOUR_"
            "HS_CHANNELS_WITH_THE_EXISTING_NONCENTRAL_FERMION_OPERATOR_BEFORE_"
            "TESTING_THE_BROKEN_SADDLE_IN_THE_EVENT_FLUX_ASSEMBLY"
        ),
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "claim_boundary",
    "finite_difference_coordinate_jet",
    "generalized_e1_coordinate_jet",
    "regulated_kernel",
    "regulated_kernel_divided_difference",
]
