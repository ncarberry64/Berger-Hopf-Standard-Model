"""Operator-norm and relative-bound utilities for BHSM v1.3B.

These are finite-matrix bound helpers used by the Level 2 H_T audit. They do
not alter the BHSM model and do not complete the full H_T theorem.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class OperatorNormBound:
    """A named upper bound on a finite Hermitian perturbation norm."""

    name: str
    value: float
    method: str
    assumptions: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class RelativeBoundEstimate:
    """Finite-matrix relative-bound estimate for a perturbation K."""

    name: str
    a_k: float
    b_k: float
    base_lower_bound: float
    perturbation_norm: float
    stability_lower_bound: float
    required_lower_bound: float
    sufficient: bool
    assumptions: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class GapStabilityResult:
    """Weyl-style lower-bound result for a base operator plus perturbation."""

    name: str
    base_lower_bound: float
    perturbation_norm: float
    weyl_lower_bound: float
    exact_full_lower_bound: float
    required_lower_bound: float
    norm_bound_sufficient: bool
    finite_basis_passes: bool
    classification: str
    theorem_complete: bool
    assumptions: tuple[str, ...]
    limitations: tuple[str, ...]


def as_symmetric_matrix(matrix: np.ndarray) -> np.ndarray:
    """Return the Hermitian/symmetric part of a finite square matrix."""

    arr = np.asarray(matrix, dtype=float)
    if arr.ndim != 2 or arr.shape[0] != arr.shape[1]:
        raise ValueError("matrix must be square")
    return 0.5 * (arr + arr.T)


def spectral_norm(matrix: np.ndarray) -> float:
    """Return the finite-matrix spectral norm for a symmetric perturbation."""

    arr = as_symmetric_matrix(matrix)
    if arr.size == 0:
        return 0.0
    return float(np.max(np.abs(np.linalg.eigvalsh(arr))))


def frobenius_norm(matrix: np.ndarray) -> float:
    """Return the Frobenius norm upper bound for the spectral norm."""

    arr = np.asarray(matrix, dtype=float)
    return float(np.linalg.norm(arr, ord="fro"))


def row_sum_norm(matrix: np.ndarray) -> float:
    """Return the maximum absolute row-sum norm."""

    arr = np.asarray(matrix, dtype=float)
    if arr.ndim != 2:
        raise ValueError("matrix must be two-dimensional")
    if arr.size == 0:
        return 0.0
    return float(np.max(np.sum(np.abs(arr), axis=1)))


def operator_norm_bounds(matrix: np.ndarray) -> tuple[OperatorNormBound, ...]:
    """Return spectral, Frobenius, and row-sum norm bounds for a perturbation."""

    return (
        OperatorNormBound(
            name="spectral_norm",
            value=spectral_norm(matrix),
            method="finite matrix |K|_2 from Hermitian eigenvalues",
            assumptions=("The perturbation is represented by the finite Level 2 matrix.",),
            limitations=("Finite-matrix norm only; not an infinite-basis operator norm.",),
        ),
        OperatorNormBound(
            name="frobenius_norm",
            value=frobenius_norm(matrix),
            method="Frobenius upper bound |K|_2 <= |K|_F",
            assumptions=("The matrix entries are finite and explicitly represented.",),
            limitations=("Usually conservative; not a sharp spectral lower-bound certificate.",),
        ),
        OperatorNormBound(
            name="row_sum_norm",
            value=row_sum_norm(matrix),
            method="maximum absolute row-sum bound |K|_infinity",
            assumptions=("The finite matrix row sums bound perturbation size.",),
            limitations=("Row-sum bound is finite-basis and can overestimate |K|_2.",),
        ),
    )


def weyl_lower_bound(base_lower_bound: float, perturbation_norm: float) -> float:
    """Return Weyl's conservative lower bound lambda_1(B+K) >= lambda_1(B)-|K|."""

    return float(base_lower_bound - perturbation_norm)


def relative_bound_estimate(
    perturbation_norm: float,
    base_lower_bound: float,
    required_lower_bound: float,
    *,
    name: str = "relative_bound_a_only",
) -> RelativeBoundEstimate:
    """Return a finite-matrix relative-bound estimate.

    Since ``<psi, B psi> >= base_lower_bound ||psi||^2`` on the audited
    complement, ``|<psi,K psi>| <= ||K|| ||psi||^2`` implies
    ``|<psi,K psi>| <= a_K <psi,B psi>`` with
    ``a_K = ||K|| / base_lower_bound`` when the base lower bound is positive.
    """

    base = float(base_lower_bound)
    norm = float(perturbation_norm)
    required = float(required_lower_bound)
    if base <= 0:
        a_k = float("inf")
        stability = float("-inf")
    else:
        a_k = norm / base
        stability = (1.0 - a_k) * base
    return RelativeBoundEstimate(
        name=name,
        a_k=float(a_k),
        b_k=0.0,
        base_lower_bound=base,
        perturbation_norm=norm,
        stability_lower_bound=float(stability),
        required_lower_bound=required,
        sufficient=bool(stability >= required),
        assumptions=(
            "Finite complement base operator is positive with the stated lower bound.",
            "The perturbation quadratic form is bounded by its finite spectral norm.",
        ),
        limitations=(
            "This is a finite-matrix relative-bound estimate.",
            "It does not prove an infinite-basis relative bound for the complete H_T operator.",
        ),
    )


def gap_stability_from_norm(
    base_lower_bound: float,
    perturbation_norm: float,
    exact_full_lower_bound: float,
    required_lower_bound: float,
) -> GapStabilityResult:
    """Classify whether a perturbation norm bound certifies the complement gap."""

    weyl = weyl_lower_bound(base_lower_bound, perturbation_norm)
    norm_sufficient = bool(weyl >= required_lower_bound)
    finite_passes = bool(float(exact_full_lower_bound) >= required_lower_bound)
    if norm_sufficient:
        classification = "NORM_BOUND_SUFFICIENT"
    elif finite_passes:
        classification = "NORM_BOUND_INSUFFICIENT_BUT_FINITE_BASIS_PASSES"
    else:
        classification = "FAILS_GAP"
    return GapStabilityResult(
        name="weyl_sector_coupling_stability",
        base_lower_bound=float(base_lower_bound),
        perturbation_norm=float(perturbation_norm),
        weyl_lower_bound=float(weyl),
        exact_full_lower_bound=float(exact_full_lower_bound),
        required_lower_bound=float(required_lower_bound),
        norm_bound_sufficient=norm_sufficient,
        finite_basis_passes=finite_passes,
        classification=classification,
        theorem_complete=False,
        assumptions=(
            "Weyl lower bound is applied on the finite protected complement.",
            "The sector-coupling perturbation norm is computed before residual comparison.",
        ),
        limitations=(
            "A finite-basis pass is not reported as an analytic theorem.",
            "The full no-extra-light-state theorem remains open.",
        ),
    )
