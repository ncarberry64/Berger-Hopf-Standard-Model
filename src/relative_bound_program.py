"""Structured relative-bound helpers for BHSM v1.3C."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class RelativeBoundCertificate:
    """Structured finite-basis relative-bound certificate."""

    name: str
    a_k: float
    b_k: float
    required_dirac_lower_bound: float
    structured_lower_bound: float
    baseline_lower_bound: float
    full_lower_bound: float
    sufficient: bool
    classification: str
    theorem_complete: bool
    evidence: tuple[str, ...]
    assumptions: tuple[str, ...]
    limitations: tuple[str, ...]


def rayleigh_relative_bound(
    base_operator: np.ndarray,
    perturbation: np.ndarray,
    *,
    epsilon: float = 1e-12,
) -> float:
    """Return the exact finite generalized relative bound on the base range.

    For a positive finite matrix ``B`` and symmetric perturbation ``K``, this
    computes ``|| B^{-1/2} K B^{-1/2} ||``. It is stronger than the raw norm
    estimate when the base operator grows across the basis.
    """

    base = 0.5 * (np.asarray(base_operator, dtype=float) + np.asarray(base_operator, dtype=float).T)
    perturb = 0.5 * (np.asarray(perturbation, dtype=float) + np.asarray(perturbation, dtype=float).T)
    if base.shape != perturb.shape or base.ndim != 2 or base.shape[0] != base.shape[1]:
        raise ValueError("base_operator and perturbation must be square matrices of the same shape")
    eigenvalues, eigenvectors = np.linalg.eigh(base)
    if np.any(eigenvalues <= epsilon):
        raise ValueError("base_operator must be positive on the audited subspace")
    inv_sqrt = eigenvectors @ np.diag(1.0 / np.sqrt(eigenvalues)) @ eigenvectors.T
    relative = inv_sqrt @ perturb @ inv_sqrt
    return float(np.max(np.abs(np.linalg.eigvalsh(0.5 * (relative + relative.T)))))


def structured_relative_certificate(
    *,
    a_k: float,
    base_lower_bound: float,
    full_lower_bound: float,
    required_dirac_lower_bound: float,
    b_k: float = 0.0,
    finite_basis_only: bool = True,
) -> RelativeBoundCertificate:
    """Return a conservative structured relative-bound certificate."""

    structured_lower = (1.0 - float(a_k)) * float(base_lower_bound) - float(b_k)
    sufficient = bool(structured_lower >= float(required_dirac_lower_bound))
    if sufficient and finite_basis_only:
        classification = "RELATIVE_BOUND_CANDIDATE"
    elif sufficient:
        classification = "STRUCTURED_BOUND_SUFFICIENT"
    elif float(full_lower_bound) >= float(required_dirac_lower_bound):
        classification = "FINITE_BASIS_ONLY"
    else:
        classification = "FAILS_BOUND"
    return RelativeBoundCertificate(
        name="structured_sector_relative_bound",
        a_k=float(a_k),
        b_k=float(b_k),
        required_dirac_lower_bound=float(required_dirac_lower_bound),
        structured_lower_bound=float(structured_lower),
        baseline_lower_bound=float(base_lower_bound),
        full_lower_bound=float(full_lower_bound),
        sufficient=sufficient,
        classification=classification,
        theorem_complete=False,
        evidence=(
            "Computed finite generalized relative bound ||B^{-1/2} K B^{-1/2}||.",
            "Compared structured lower bound (1-a_K) lambda_1(B)-b_K to the required Dirac lower bound.",
        ),
        assumptions=(
            "The base operator is positive on the protected finite complement.",
            "The sector perturbation is symmetric on the audited finite complement.",
        ),
        limitations=(
            "The certificate is finite-basis unless the same relative bound is proven uniformly as k_max grows.",
            "It does not prove the full H_T theorem or the zero-mode/complement decomposition.",
        ),
    )
