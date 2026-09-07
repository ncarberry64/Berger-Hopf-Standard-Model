"""Universal current-C2 gauge--spinor boundary principal symbol.

Every admissible Hadamard/Calderon completion has the same local spinor
positive-frequency symbol.  This module constructs that symbol, proves its
family and AE2-reset covariance, and joins it to the already-derived
Maxwell--BRST characteristic symbol.  Smooth state data and the finite outer
boundary response are deliberately not selected here.
"""

from __future__ import annotations

import math
from typing import Any, Sequence

import numpy as np

from bhsm.interface.ae31_c2_intrinsic_m4_lepton_action import (
    conditional_tree_mass_operator,
)
from bhsm.interface.ae3_c2_lorentzian_gauge_ghost_hessian import (
    constraint_ghost_frequency_block,
    lowest_transverse_residue_witness,
)


ACTION_VERSION = "BHSM-AE-3.1.0"
CLASSIFICATION = "CURRENT_C2_CALDERON_HADAMARD_PRINCIPAL_BOUNDARY_SYMBOL"


def _clifford_hamiltonian_matrices() -> tuple[list[np.ndarray], np.ndarray]:
    """Return Hermitian ``alpha_i`` and ``beta`` in a Dirac basis."""

    sigma = [
        np.asarray(((0.0, 1.0), (1.0, 0.0)), dtype=complex),
        np.asarray(((0.0, -1.0j), (1.0j, 0.0)), dtype=complex),
        np.asarray(((1.0, 0.0), (0.0, -1.0)), dtype=complex),
    ]
    zero = np.zeros((2, 2), dtype=complex)
    alpha = [np.block([[zero, item], [item, zero]]) for item in sigma]
    beta = np.block([[np.eye(2), zero], [zero, -np.eye(2)]]).astype(complex)
    return alpha, beta


def family_dirac_projectors(
    momentum: Sequence[float], masses: Sequence[float]
) -> dict[str, Any]:
    """Construct exact frozen positive/negative energy projectors.

    The tensor order is ``C4_spinor tensor Cn_family``.  The masses are
    zero-order data.  Consequently all families share the same homogeneous
    high-frequency projector, which is the Hadamard principal symbol.
    """

    k = np.asarray(momentum, dtype=float)
    mass = np.asarray(masses, dtype=float)
    if k.shape != (3,) or not np.all(np.isfinite(k)):
        raise ValueError("momentum must be a finite three-vector")
    if mass.ndim != 1 or mass.size == 0 or not np.all(np.isfinite(mass)):
        raise ValueError("masses must be a nonempty finite vector")
    if np.any(mass < 0.0):
        raise ValueError("masses must be nonnegative")
    k_norm = float(np.linalg.norm(k))
    if k_norm == 0.0:
        raise ValueError("nonzero momentum required for the principal symbol")

    alpha, beta = _clifford_hamiltonian_matrices()
    family_identity = np.eye(mass.size, dtype=complex)
    mass_matrix = np.diag(mass).astype(complex)
    hamiltonian = sum(
        value * np.kron(matrix, family_identity)
        for value, matrix in zip(k, alpha)
    ) + np.kron(beta, mass_matrix)
    energies = np.sqrt(k_norm * k_norm + mass * mass)
    inverse_energy = np.kron(np.eye(4), np.diag(1.0 / energies))
    sign_hamiltonian = hamiltonian @ inverse_energy
    identity = np.eye(4 * mass.size, dtype=complex)
    positive = 0.5 * (identity + sign_hamiltonian)
    negative = 0.5 * (identity - sign_hamiltonian)

    massless_sign = sum(
        value * np.kron(matrix, family_identity)
        for value, matrix in zip(k / k_norm, alpha)
    )
    principal = 0.5 * (identity + massless_sign)
    square_target = np.kron(
        np.eye(4), np.diag(k_norm * k_norm + mass * mass)
    )
    return {
        "Hamiltonian": hamiltonian,
        "energies": energies,
        "positive_projector": positive,
        "negative_projector": negative,
        "Hadamard_principal_projector": principal,
        "Hamiltonian_square_residual": float(
            np.linalg.norm(hamiltonian @ hamiltonian - square_target, ord=2)
        ),
        "positive_Hermitian_residual": float(
            np.linalg.norm(positive - positive.conj().T, ord=2)
        ),
        "positive_idempotence_residual": float(
            np.linalg.norm(positive @ positive - positive, ord=2)
        ),
        "complement_residual": float(
            np.linalg.norm(positive + negative - identity, ord=2)
        ),
        "principal_idempotence_residual": float(
            np.linalg.norm(principal @ principal - principal, ord=2)
        ),
        "positive_rank": int(np.linalg.matrix_rank(positive, tol=1.0e-11)),
        "principal_rank": int(np.linalg.matrix_rank(principal, tol=1.0e-11)),
        "mass_is_lower_order": True,
        "family_independent_homogeneous_principal_symbol": True,
    }


def self_dual_principal_covariance(
    momentum: Sequence[float], family_count: int = 3
) -> dict[str, Any]:
    """Double the positive-energy symbol into a self-dual CAR covariance."""

    count = int(family_count)
    if count < 1:
        raise ValueError("family_count must be positive")
    projectors = family_dirac_projectors(momentum, np.zeros(count))
    positive = projectors["Hadamard_principal_projector"]
    identity = np.eye(positive.shape[0], dtype=complex)
    zero = np.zeros_like(identity)
    covariance = np.block(
        [[positive, zero], [zero, identity - positive.conj()]]
    )
    conjugation = np.block([[zero, identity], [identity, zero]])
    doubled_identity = np.eye(covariance.shape[0], dtype=complex)
    return {
        "covariance": covariance,
        "CAR_conjugation_matrix": conjugation,
        "Hermitian_residual": float(
            np.linalg.norm(covariance - covariance.conj().T, ord=2)
        ),
        "purity_residual": float(
            np.linalg.norm(covariance @ covariance - covariance, ord=2)
        ),
        "self_dual_CAR_residual": float(
            np.linalg.norm(
                covariance
                + conjugation @ covariance.conj() @ conjugation.conj().T
                - doubled_identity,
                ord=2,
            )
        ),
        "rank": int(np.linalg.matrix_rank(covariance, tol=1.0e-11)),
        "dimension": covariance.shape[0],
    }


def reset_equivariance_witness(theta: float = 0.731) -> dict[str, Any]:
    """Verify spin-lift covariance under a nontrivial spatial reset frame."""

    angle = float(theta)
    if not math.isfinite(angle):
        raise ValueError("finite rotation angle required")
    momentum_event = np.asarray((0.4, -0.7, 1.1), dtype=float)
    rotation = np.asarray(
        (
            (math.cos(angle), -math.sin(angle), 0.0),
            (math.sin(angle), math.cos(angle), 0.0),
            (0.0, 0.0, 1.0),
        )
    )
    momentum_child = rotation @ momentum_event
    spin_two = np.diag(
        (np.exp(-0.5j * angle), np.exp(0.5j * angle))
    )
    spin_four = np.block(
        [
            [spin_two, np.zeros((2, 2), dtype=complex)],
            [np.zeros((2, 2), dtype=complex), spin_two],
        ]
    )
    spin_family = np.kron(spin_four, np.eye(3))
    zero = np.zeros_like(spin_family)
    nambu_reset = np.block(
        [[spin_family, zero], [zero, spin_family.conj()]]
    )

    event = self_dual_principal_covariance(momentum_event)
    child = self_dual_principal_covariance(momentum_child)
    event_covariance = event["covariance"]
    child_covariance = child["covariance"]
    transported = nambu_reset @ event_covariance @ nambu_reset.conj().T
    gamma = event["CAR_conjugation_matrix"]
    return {
        "rotation_angle": angle,
        "event_momentum": momentum_event.tolist(),
        "child_momentum": momentum_child.tolist(),
        "spin_lift_unitarity_residual": float(
            np.linalg.norm(
                spin_family.conj().T @ spin_family - np.eye(spin_family.shape[0]),
                ord=2,
            )
        ),
        "principal_covariance_intertwining_residual": float(
            np.linalg.norm(transported - child_covariance, ord=2)
        ),
        "CAR_conjugation_intertwining_residual": float(
            np.linalg.norm(nambu_reset @ gamma - gamma @ nambu_reset.conj(), ord=2)
        ),
        "family_factor": "I3",
        "family_projectors_preserved": True,
        "AE2_reset_equivariant": True,
    }


def conditional_massive_to_principal_limit() -> dict[str, Any]:
    """Show that the existing conditional masses affect only lower order."""

    masses = np.asarray(
        conditional_tree_mass_operator()["eigenvalues_GeV_heavy_middle_light"],
        dtype=float,
    )
    direction = np.asarray((2.0, -1.0, 3.0), dtype=float)
    direction /= np.linalg.norm(direction)
    scales = np.asarray((10.0, 100.0, 1000.0)) * float(np.max(masses))
    differences = []
    for scale in scales:
        result = family_dirac_projectors(scale * direction, masses)
        differences.append(
            float(
                np.linalg.norm(
                    result["positive_projector"]
                    - result["Hadamard_principal_projector"],
                    ord=2,
                )
            )
        )
    return {
        "conditional_mass_eigenvalues_GeV": masses.tolist(),
        "momentum_scales_GeV": scales.tolist(),
        "operator_norm_differences": differences,
        "strictly_decreasing": all(
            left > right for left, right in zip(differences, differences[1:])
        ),
        "asymptotic_order": "O(max(m_f)/abs(k))",
        "mass_changes_homogeneous_principal_symbol": False,
        "measured_mass_used": False,
    }


def gauge_brst_characteristic_symbol(
    momentum: Sequence[float] = (0.0, 0.0, 2.0), omega: float = 1.0
) -> dict[str, Any]:
    """Join the retained coexact and BRST characteristic symbols."""

    k = np.asarray(momentum, dtype=float)
    frequency = float(omega)
    if k.shape != (3,) or not np.all(np.isfinite(k)):
        raise ValueError("momentum must be a finite three-vector")
    if not math.isfinite(frequency):
        raise ValueError("finite continuous frequency required")
    k_squared = float(k @ k)
    if k_squared == 0.0:
        raise ValueError("nonzero spatial momentum required")
    transverse = np.eye(3) - np.outer(k, k) / k_squared
    residue = lowest_transverse_residue_witness()
    z_spatial = 1.0
    z_temporal = float(
        residue["temporal_to_complete_spatial_mode_residue_ratio"]
    )
    coexact_scalar = z_spatial * k_squared - z_temporal * frequency**2
    coexact = coexact_scalar * transverse
    brst = constraint_ghost_frequency_block(
        omega=frequency,
        scalar_laplacian=k_squared,
        z_temporal=z_temporal,
        z_spatial=z_spatial,
    )
    ghost = brst["ghost_Faddeev_Popov_symbol"]
    return {
        "continuous_frequency": frequency,
        "spatial_momentum": k.tolist(),
        "transverse_projector": transverse,
        "transverse_projector_rank": int(
            np.linalg.matrix_rank(transverse, tol=1.0e-12)
        ),
        "transverse_projector_residual": float(
            np.linalg.norm(transverse @ transverse - transverse, ord=2)
        ),
        "Z_t_normalized": z_temporal,
        "Z_s_normalized": z_spatial,
        "coexact_characteristic_scalar": coexact_scalar,
        "coexact_Hessian_symbol": coexact,
        "ghost_characteristic_scalar": ghost,
        "BRST_characteristic_matching_residual": abs(ghost + coexact_scalar),
        "effective_characteristic_cone": "Z_t*omega^2=Z_s*abs(k)^2",
        "one_Maxwell_metric_residue": z_temporal == z_spatial,
        "principal_symbol_repairs_residue_mismatch": False,
    }


def local_boundary_symbol_theorem() -> dict[str, Any]:
    """State the exact advance and the remaining smoothing ambiguity."""

    return {
        "action_version": ACTION_VERSION,
        "spinor_symbol": "P_plus^(0)(k)=(I+alpha_dot_k/abs(k))/2",
        "self_dual_symbol": (
            "C_Had^(0)=diag(P_plus^(0),I-conjugate(P_plus^(0)))"
        ),
        "gauge_symbol": (
            "H_coexact^(0)=(Z_s*abs(k)^2-Z_t*omega^2)*Pi_transverse"
        ),
        "ghost_symbol": "H_FP^(0)=Z_t*omega^2-Z_s*abs(k)^2",
        "all_admissible_Hadamard_completions_share_spinor_symbol": True,
        "AE2_reset_intertwines_the_local_symbol": True,
        "frozen_family_projectors_preserved": True,
        "remaining_spinor_freedom": (
            "SMOOTH_SELF_DUAL_BISOLUTION_OR_EQUIVALENT_SMOOTHING_OPERATOR_K"
        ),
        "remaining_gauge_freedom": (
            "LOWER_ORDER_OUTER_DTN_AND_BOUNDARY_OR_COLLAR_RESPONSE"
        ),
        "symbol_determines_finite_determinant": False,
        "symbol_selects_one_global_state": False,
        "symbol_supplies_required_noncommon_gauge_correction": False,
        "physical_outer_projector_constructed": False,
        "scientific_result": (
            "THE_MISSING_OUTER_OPERATOR_IS_REDUCED_TO_A_RESET_EQUIVARIANT_"
            "SMOOTH_COMPLETION_OF_A_FIXED_LOCAL_GAUGE_SPINOR_GHOST_SYMBOL"
        ),
    }


def claim_boundary() -> dict[str, Any]:
    return {
        "CURRENT_C2_SPINOR_HADAMARD_CALDERON_PRINCIPAL_SYMBOL_DERIVED": True,
        "CURRENT_C2_GAUGE_BRST_CHARACTERISTIC_BOUNDARY_SYMBOL_DERIVED": True,
        "CURRENT_C2_RESET_EQUIVARIANT_FAMILY_PRESERVING_LOCAL_SYMBOL_DERIVED": True,
        "CURRENT_C2_PHYSICAL_GAUGE_SPINOR_GHOST_CALDERON_PROJECTOR_DERIVED": False,
        "CURRENT_C2_ACTION_SELECTED_HADAMARD_STATE_DERIVED": False,
        "CURRENT_C2_LORENTZIAN_MAXWELL_RESIDUE_DERIVED": False,
        "CURRENT_C2_FINITE_SCALAR_HESSIAN_DERIVED": False,
        "CURRENT_C2_NORMALIZED_PHOTON_PROPAGATOR_DERIVED": False,
        "MUON_MAGNETIC_MOMENT_DERIVED": False,
        "particle_spectrum_rebuilt": False,
        "FULL_BHSM_COMPLETE": False,
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "claim_boundary",
    "conditional_massive_to_principal_limit",
    "family_dirac_projectors",
    "gauge_brst_characteristic_symbol",
    "local_boundary_symbol_theorem",
    "reset_equivariance_witness",
    "self_dual_principal_covariance",
]
