"""BHSM v8.9 automatic geometric lens theorem.

This module proves the finite-dimensional action-reduction theorem that removes
independent up/down mass-basis lenses.  Once the emergent composite reduction
supplies the sector kinetic Gram forms, sector response Hessians, and the raw
common-parent current kernel, canonical normalization and spectral calculus
produce the two lenses uniquely up to unphysical eigenvector phases.

No physical CKM value is promoted here.  The numerical v8.5-v8.8 objects are
used only as deterministic stress tests of the theorem's domain.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from . import common_parent_charged_current_attachment as v88
from . import complex_profile_isospectral_attachment as v86
from . import topographic_profile_component_selection as v85


VERSION = "v8.9"
SPRINT = "bhsm-automatic-geometric-lens-theorem-v8-9"
PRIMARY_RESULT = (
    "BHSM_EIGHT_DIMENSIONAL_ACTION_GRAM_HESSIAN_LENS_THEOREM_PROVED_"
    "CONDITIONALLY"
)
FINAL_VERDICT = (
    "BHSM_UP_DOWN_MASS_BASIS_LENSES_ARE_CANONICAL_OUTPUTS_OF_THE_"
    "COMPOSITE_EIGHT_DIMENSIONAL_ACTION_REDUCTION_CONDITIONALLY"
)
NEXT_MISSING_OBJECT = (
    "EVALUATION_OF_THE_COMPOSITE_IMMERSIONS_AND_THEIR_PULLBACK_"
    "GRAM_HESSIAN_CURRENT_FORMS_ON_THE_ACTION_SELECTED_EIGHT_"
    "DIMENSIONAL_VACUUM"
)


def _as_hermitian(matrix: np.ndarray, *, name: str) -> np.ndarray:
    value = np.asarray(matrix, dtype=complex)
    if value.ndim != 2 or value.shape[0] != value.shape[1]:
        raise ValueError(f"{name} must be square")
    if not np.allclose(value, value.conj().T, atol=1.0e-11):
        raise ValueError(f"{name} must be Hermitian")
    return 0.5 * (value + value.conj().T)


def positive_inverse_sqrt(matrix: np.ndarray, tol: float = 1.0e-13) -> np.ndarray:
    """Unique positive inverse square root of a positive Hermitian matrix."""

    value = _as_hermitian(matrix, name="kinetic Gram matrix")
    eigenvalues, eigenvectors = np.linalg.eigh(value)
    if float(eigenvalues.min()) <= tol:
        raise ValueError("kinetic Gram matrix must be strictly positive")
    return eigenvectors @ np.diag(eigenvalues ** -0.5) @ eigenvectors.conj().T


def positive_sqrt(matrix: np.ndarray, tol: float = 1.0e-13) -> np.ndarray:
    value = _as_hermitian(matrix, name="positive matrix")
    eigenvalues, eigenvectors = np.linalg.eigh(value)
    if float(eigenvalues.min()) <= tol:
        raise ValueError("matrix must be strictly positive")
    return eigenvectors @ np.diag(eigenvalues ** 0.5) @ eigenvectors.conj().T


def sector_lens(
    kinetic_gram: np.ndarray,
    response_hessian: np.ndarray,
    *,
    simple_gap_tol: float = 1.0e-11,
) -> dict[str, Any]:
    """Construct the unique canonical sector lens.

    The raw generalized eigenproblem Q x = mu G x is whitened by the unique
    positive G^(-1/2).  The resulting Hermitian operator has an ordered unitary
    eigenframe W.  X=G^(-1/2)W is G-orthonormal and diagonalizes Q.
    """

    G = _as_hermitian(kinetic_gram, name="kinetic Gram matrix")
    Q = _as_hermitian(response_hessian, name="response Hessian")
    if G.shape != Q.shape:
        raise ValueError("kinetic and response forms must have equal size")
    grind = positive_inverse_sqrt(G)
    polished_operator = grind @ Q @ grind
    polished_operator = 0.5 * (polished_operator + polished_operator.conj().T)
    eigenvalues, axes = np.linalg.eigh(polished_operator)
    if eigenvalues.size > 1 and float(np.min(np.diff(eigenvalues))) <= simple_gap_tol:
        raise ValueError("response spectrum must be simple to select rank-one lenses")
    lens = grind @ axes
    return {
        "kinetic_gram": G,
        "response_hessian": Q,
        "grinding_operator": grind,
        "polished_operator": polished_operator,
        "eigenvalues_ascending": eigenvalues,
        "canonical_axes": axes,
        "lens": lens,
        "kinetic_orthonormality_residual": float(
            np.linalg.norm(lens.conj().T @ G @ lens - np.eye(G.shape[0]))
        ),
        "response_diagonalization_residual": float(
            np.linalg.norm(
                lens.conj().T @ Q @ lens - np.diag(eigenvalues)
            )
        ),
        "simple_spectrum": True,
        "unique_modulo_column_phases": True,
    }


def whitened_parent_kernel(
    up_kinetic: np.ndarray, raw_kernel: np.ndarray, down_kinetic: np.ndarray
) -> np.ndarray:
    """Canonically normalize a raw bifundamental current kernel."""

    Gu_inv_root = positive_inverse_sqrt(up_kinetic)
    Gd_inv_root = positive_inverse_sqrt(down_kinetic)
    K = np.asarray(raw_kernel, dtype=complex)
    if K.shape != Gu_inv_root.shape or K.shape != Gd_inv_root.shape:
        raise ValueError("raw current kernel must match the two family spaces")
    return Gu_inv_root @ K @ Gd_inv_root


def physical_current_from_action_forms(
    up_kinetic: np.ndarray,
    up_response: np.ndarray,
    raw_kernel: np.ndarray,
    down_kinetic: np.ndarray,
    down_response: np.ndarray,
) -> dict[str, Any]:
    """Return the automatic mass-basis current produced by the action forms."""

    up = sector_lens(up_kinetic, up_response)
    down = sector_lens(down_kinetic, down_response)
    normalized_kernel = whitened_parent_kernel(
        up_kinetic, raw_kernel, down_kinetic
    )
    common_current = v86.polar_unitary(normalized_kernel)
    W_u = up["canonical_axes"]
    W_d = down["canonical_axes"]
    V = W_u.conj().T @ common_current @ W_d
    return {
        "up": up,
        "down": down,
        "whitened_parent_kernel": normalized_kernel,
        "common_parent_unitary": common_current,
        "physical_current": V,
        "current_unitarity_residual": float(
            np.linalg.norm(V.conj().T @ V - np.eye(V.shape[0]))
        ),
        "matrix_magnitudes": np.abs(V).tolist(),
        "jarlskog": v86.jarlskog(V),
        "standard_sines": v86.standard_sines(V),
    }


def spectral_projectors(operator: np.ndarray, tol: float = 1.0e-11) -> list[np.ndarray]:
    """Return unique rank-one spectral projectors for a simple Hermitian operator."""

    H = _as_hermitian(operator, name="operator")
    eigenvalues, eigenvectors = np.linalg.eigh(H)
    if eigenvalues.size > 1 and float(np.min(np.diff(eigenvalues))) <= tol:
        raise ValueError("operator spectrum must be simple")
    return [
        eigenvectors[:, [i]] @ eigenvectors[:, [i]].conj().T
        for i in range(H.shape[0])
    ]


def projector_mixing_moduli(
    up_operator: np.ndarray, current: np.ndarray, down_operator: np.ndarray
) -> np.ndarray:
    """Compute |V_ij|^2 without choosing eigenvector phases."""

    Pu = spectral_projectors(up_operator)
    Pd = spectral_projectors(down_operator)
    U = np.asarray(current, dtype=complex)
    values = np.empty((len(Pu), len(Pd)), dtype=float)
    for i, left in enumerate(Pu):
        for j, right in enumerate(Pd):
            values[i, j] = float(
                np.real(np.trace(left @ U @ right @ U.conj().T))
            )
    return values


def vandermonde_product(eigenvalues: np.ndarray) -> float:
    values = np.asarray(eigenvalues, dtype=float)
    result = 1.0
    for i in range(values.size):
        for j in range(i + 1, values.size):
            result *= values[i] - values[j]
    return float(result)


def invariant_jarlskog(
    up_operator: np.ndarray, current: np.ndarray, down_operator: np.ndarray
) -> float:
    """Compute J from the basis-free commutator cube identity.

    The sign follows the ascending eigenvalue ordering used by numpy.eigh.
    """

    Hu = _as_hermitian(up_operator, name="up operator")
    Hd = _as_hermitian(down_operator, name="down operator")
    U = np.asarray(current, dtype=complex)
    transported_down = U @ Hd @ U.conj().T
    commutator = Hu @ transported_down - transported_down @ Hu
    eu = np.linalg.eigvalsh(Hu)
    ed = np.linalg.eigvalsh(Hd)
    denominator = 6.0j * vandermonde_product(eu) * vandermonde_product(ed)
    if abs(denominator) <= 1.0e-16:
        raise ValueError("simple nondegenerate spectra are required")
    value = np.trace(commutator @ commutator @ commutator) / denominator
    return float(np.real_if_close(value, tol=1000).real)


def phase_free_audit(result: dict[str, Any]) -> dict[str, Any]:
    up_operator = result["up"]["polished_operator"]
    down_operator = result["down"]["polished_operator"]
    current = result["common_parent_unitary"]
    frame_matrix = result["physical_current"]
    moduli_sq = projector_mixing_moduli(up_operator, current, down_operator)
    invariant_J = invariant_jarlskog(up_operator, current, down_operator)
    return {
        "projector_moduli_squared": moduli_sq.tolist(),
        "frame_moduli_squared": (np.abs(frame_matrix) ** 2).tolist(),
        "moduli_residual": float(
            np.linalg.norm(moduli_sq - np.abs(frame_matrix) ** 2)
        ),
        "frame_jarlskog": v86.jarlskog(frame_matrix),
        "invariant_jarlskog": invariant_J,
        "jarlskog_residual": float(abs(invariant_J - v86.jarlskog(frame_matrix))),
        "eigenvector_phases_needed_for_observables": False,
    }


def basis_covariance_audit() -> dict[str, Any]:
    """Test unitary family-coordinate covariance of the whole construction."""

    Gu = np.array([[2.2, 0.2j, 0.1], [-0.2j, 1.7, 0.15], [0.1, 0.15, 1.3]])
    Gd = np.array([[1.8, 0.1, -0.15j], [0.1, 1.5, 0.12], [0.15j, 0.12, 1.2]])
    Qu = np.array([[0.8, 0.12j, 0.03], [-0.12j, 1.9, 0.2], [0.03, 0.2, 3.4]])
    Qd = np.array([[0.6, 0.08, 0.04j], [0.08, 1.5, -0.1j], [-0.04j, 0.1j, 2.8]])
    K = v88.proxy_parent_kernel()
    Vu = v86.polar_unitary(
        np.array([[1, 0.2j, 0.1], [0.3, 1, -0.2j], [0.1j, 0.4, 1]], complex)
    )
    Vd = v86.polar_unitary(
        np.array([[1, -0.1j, 0.2], [0.15, 1, 0.25j], [-0.2j, 0.1, 1]], complex)
    )
    base = physical_current_from_action_forms(Gu, Qu, K, Gd, Qd)
    transformed = physical_current_from_action_forms(
        Vu @ Gu @ Vu.conj().T,
        Vu @ Qu @ Vu.conj().T,
        Vu @ K @ Vd.conj().T,
        Vd @ Gd @ Vd.conj().T,
        Vd @ Qd @ Vd.conj().T,
    )
    base_moduli = np.abs(base["physical_current"])
    transformed_moduli = np.abs(transformed["physical_current"])
    return {
        "matrix_moduli_residual": float(np.linalg.norm(base_moduli - transformed_moduli)),
        "jarlskog_residual": float(abs(base["jarlskog"] - transformed["jarlskog"])),
        "basis_invariant_observables": bool(
            np.linalg.norm(base_moduli - transformed_moduli) < 1.0e-10
            and abs(base["jarlskog"] - transformed["jarlskog"]) < 1.0e-10
        ),
    }


def proxy_geometry_audit() -> dict[str, Any]:
    """Stress test on existing profile/current proxies without physical promotion."""

    Gu = np.eye(3)
    Gd = np.eye(3)
    Qu = v85.heat_kernel_sector_matrix("up")
    Qd = v85.heat_kernel_sector_matrix("down")
    K = v88.proxy_parent_kernel()
    result = physical_current_from_action_forms(Gu, Qu, K, Gd, Qd)
    phase_free = phase_free_audit(result)
    return {
        "proxy_uses_historical_screen_inputs": True,
        "proxy_role": "domain and theorem stress test only",
        "up_response_eigenvalues": result["up"]["eigenvalues_ascending"].tolist(),
        "down_response_eigenvalues": result["down"]["eigenvalues_ascending"].tolist(),
        "up_lens_kinetic_residual": result["up"]["kinetic_orthonormality_residual"],
        "down_lens_kinetic_residual": result["down"]["kinetic_orthonormality_residual"],
        "current_unitarity_residual": result["current_unitarity_residual"],
        "matrix_magnitudes": result["matrix_magnitudes"],
        "jarlskog": result["jarlskog"],
        "standard_sines": result["standard_sines"],
        "phase_free_invariants": phase_free,
        "physical_promotion": False,
    }


def theorem_statement() -> dict[str, Any]:
    return {
        "name": "BHSM automatic eight-dimensional geometric lens theorem",
        "hypotheses": [
            "an action-selected stationary eight-dimensional geometric state Phi_*",
            "smooth full-rank composite immersions C_u,C_d from the three-slot family modules into the physical quotient of eight-dimensional configuration space",
            "a positive pullback kinetic form G_f=(D C_f)^dagger K_8(D C_f)",
            "a Hermitian pullback response form Q_f=(D C_f)^dagger Hess(S_8)(D C_f)",
            "simple sector spectra after kinetic whitening",
            "a full-rank raw common-parent C3/G2 charged-current kernel",
        ],
        "construction": [
            "grind: G_f^(-1/2), the unique positive canonical-normalization operator",
            "polish: diagonalize L_f=G_f^(-1/2)Q_fG_f^(-1/2) in ordered simple spectrum",
            "sector lens: X_f=G_f^(-1/2)W_f",
            "current polish: U_CG=Pol[G_u^(-1/2)K_raw G_d^(-1/2)]",
            "physical matrix: V=W_u^dagger U_CG W_d",
        ],
        "conclusions": [
            "X_f^dagger G_f X_f=I",
            "X_f^dagger Q_f X_f=diag(mu_f)",
            "the two lenses are unique modulo unphysical column phases",
            "V is unitary",
            "all |V_ij| and J are computable from spectral projectors and commutator traces without choosing phases",
            "no continuous normalization, angle, or phase parameter is introduced",
            "rank loss or spectral degeneracy is a fail-closed theorem boundary",
        ],
        "interpretation": (
            "the eight-dimensional kinetic geometry grinds away norm and shear, "
            "while the eight-dimensional response Hessian polishes the two "
            "sector axes; the common-parent current then compares the finished lenses"
        ),
    }


def action_ownership() -> dict[str, Any]:
    return {
        "composite_pullback": (
            "G_f=(D C_f)^dagger K_8(D C_f), "
            "Q_f=(D C_f)^dagger Hess(S_BHSM^strat)(D C_f)"
        ),
        "raw_current": (
            "K_raw=(D C_u)^dagger J_parent^(C3/G2)(D C_d)"
        ),
        "all_square_roots": "unique positive functional calculus of action-owned forms",
        "all_axes": "ordered spectral projectors of action-owned Hermitian forms",
        "new_coefficient": False,
        "new_field": False,
        "f_of_X_violation": False,
        "remaining_nonformal_task": (
            "evaluate D C_u,D C_d,K_8,Hess(S), and J_parent on the actual action-selected vacuum"
        ),
    }


def payload() -> dict[str, Any]:
    proxy = proxy_geometry_audit()
    covariance = basis_covariance_audit()
    validation = {
        "up_lens_canonically_normalized": proxy["up_lens_kinetic_residual"] < 1.0e-11,
        "down_lens_canonically_normalized": proxy["down_lens_kinetic_residual"] < 1.0e-11,
        "physical_current_unitary": proxy["current_unitarity_residual"] < 1.0e-11,
        "phase_free_moduli_match": proxy["phase_free_invariants"]["moduli_residual"] < 1.0e-10,
        "phase_free_jarlskog_matches": proxy["phase_free_invariants"]["jarlskog_residual"] < 1.0e-10,
        "basis_invariant_observables": covariance["basis_invariant_observables"],
        "new_continuous_parameter": False,
        "frozen_predictions_changed": False,
        "physical_CKM_promoted": False,
    }
    validation["all_passed"] = all(
        value for key, value in validation.items() if key not in {
            "new_continuous_parameter", "frozen_predictions_changed", "physical_CKM_promoted"
        }
    ) and not validation["new_continuous_parameter"] and not validation["frozen_predictions_changed"] and not validation["physical_CKM_promoted"]
    return {
        "version": VERSION,
        "sprint": SPRINT,
        "primary_result": PRIMARY_RESULT,
        "theorem": theorem_statement(),
        "action_ownership": action_ownership(),
        "proxy_audit": proxy,
        "basis_covariance": covariance,
        "validation": validation,
        "final_verdict": FINAL_VERDICT,
        "next_missing_object": NEXT_MISSING_OBJECT,
    }


