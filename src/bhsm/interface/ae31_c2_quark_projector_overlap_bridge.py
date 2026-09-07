"""Replace an unresolved harmonic-vector overlap by its projector invariant.

The historical ``(k,j)`` ledgers identify retained harmonic subspaces but do
not select the remaining orientation label ``m``.  This module derives the
basis-independent response carried by those subspaces.  It deliberately does
not identify that response with a physical Yukawa residue until the parent
action supplies the scalar multiplication operator and trace normalization.
"""

from __future__ import annotations

from typing import Any, Iterable

import numpy as np

from bhsm.interface.ae31_c2_intrinsic_m4_lepton_action import ACTION_VERSION


CLASSIFICATION = "AE31_CURRENT_C2_QUARK_PROJECTOR_OVERLAP_BRIDGE"


def _square_matrix(values: Iterable[Iterable[complex]], *, name: str) -> np.ndarray:
    matrix = np.asarray(tuple(tuple(row) for row in values), dtype=complex)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError(f"{name} must be a square matrix")
    if not np.all(np.isfinite(matrix)):
        raise ValueError(f"{name} must be finite")
    return matrix


def _orthogonal_projector(values: Iterable[Iterable[complex]], *, name: str) -> np.ndarray:
    projector = _square_matrix(values, name=name)
    if not np.allclose(projector, projector.conj().T, atol=1e-12):
        raise ValueError(f"{name} must be Hermitian")
    if not np.allclose(projector @ projector, projector, atol=1e-12):
        raise ValueError(f"{name} must be idempotent")
    return projector


def projector_overlap_response(
    *,
    active_projector: Iterable[Iterable[complex]],
    scalar_map: Iterable[Iterable[complex]],
    singlet_projector: Iterable[Iterable[complex]],
) -> dict[str, Any]:
    """Evaluate ``Tr(P_A M P_S M^dagger)`` on finite spectral subspaces."""

    p_active = _orthogonal_projector(active_projector, name="active_projector")
    p_singlet = _orthogonal_projector(singlet_projector, name="singlet_projector")
    multiplication = _square_matrix(scalar_map, name="scalar_map")
    if not (p_active.shape == p_singlet.shape == multiplication.shape):
        raise ValueError("projectors and scalar_map must act on one Hilbert space")

    projected_map = p_active @ multiplication @ p_singlet
    response = float(np.real(np.trace(projected_map @ projected_map.conj().T)))
    direct_hs_norm = float(np.linalg.norm(projected_map, ord="fro") ** 2)
    return {
        "functional": "R(P_A,P_S;M_H)=Tr(P_A*M_H*P_S*M_H^dagger)",
        "equivalent_form": "R=||P_A*M_H*P_S||_HS^2",
        "response": response,
        "hilbert_schmidt_residual": abs(response - direct_hs_norm),
        "nonnegative": response >= -1e-12,
        "zero_iff_projected_scalar_map_zero": True,
        "unresolved_basis_vector_required": False,
        "physical_yukawa_residue_promoted": False,
    }


def basis_invariance_witness() -> dict[str, Any]:
    """Show that individual amplitudes move while their projector sum does not."""

    active_basis = np.eye(4, dtype=complex)[:, :2]
    singlet_basis = np.eye(4, dtype=complex)[:, 2:]
    multiplication = np.zeros((4, 4), dtype=complex)
    multiplication[0, 2] = 1.0
    multiplication[1, 3] = 2.0
    theta = 0.37
    rotation = np.asarray(
        ((np.cos(theta), -np.sin(theta)), (np.sin(theta), np.cos(theta))),
        dtype=complex,
    )
    active_rotated = active_basis @ rotation
    singlet_rotated = singlet_basis @ rotation.conj().T

    amplitudes = active_basis.conj().T @ multiplication @ singlet_basis
    rotated_amplitudes = (
        active_rotated.conj().T @ multiplication @ singlet_rotated
    )
    original_sum = float(np.linalg.norm(amplitudes, ord="fro") ** 2)
    rotated_sum = float(np.linalg.norm(rotated_amplitudes, ord="fro") ** 2)
    return {
        "single_matrix_entry_before": float(abs(amplitudes[0, 0]) ** 2),
        "single_matrix_entry_after": float(abs(rotated_amplitudes[0, 0]) ** 2),
        "single_vector_amplitude_basis_dependent": not np.isclose(
            abs(amplitudes[0, 0]) ** 2, abs(rotated_amplitudes[0, 0]) ** 2
        ),
        "projector_sum_before": original_sum,
        "projector_sum_after": rotated_sum,
        "projector_sum_invariance_residual": abs(original_sum - rotated_sum),
        "projectors_unchanged_residual": max(
            float(
                np.linalg.norm(
                    active_basis @ active_basis.conj().T
                    - active_rotated @ active_rotated.conj().T
                )
            ),
            float(
                np.linalg.norm(
                    singlet_basis @ singlet_basis.conj().T
                    - singlet_rotated @ singlet_rotated.conj().T
                )
            ),
        ),
    }


def current_family_projector_contract() -> dict[str, Any]:
    """Attach the invariant construction to the preserved quark mode ledgers."""

    return {
        "raw_mode_relation": "k=q+2*j",
        "up_modes_k_j": [[0, 0], [6, 0], [10, 1]],
        "down_modes_k_j": [[0, 0], [6, 3], [8, 2]],
        "up_modes_q_j": [[0, 0], [6, 0], [8, 1]],
        "down_modes_q_j": [[0, 0], [0, 3], [4, 2]],
        "retained_object": "SPECTRAL_SUBSPACE_PROJECTOR_P_kj_NOT_A_GUESSED_VECTOR_psi_kjm",
        "remaining_m_basis_may_rotate": True,
        "family_and_representation_identity_reused": True,
        "particle_spectrum_rebuilt": False,
    }


def action_trace_bifurcation() -> dict[str, Any]:
    """State exactly when the projector invariant is the action readout."""

    return {
        "full_multiplet_trace": {
            "condition": "PARENT_ACTION_TRACE_RESTRICTS_TO_THE_COMPLETE_RETAINED_kj_SUBSPACES",
            "readout": "R_f=Tr(P_A,f*M_H*P_S,f*M_H^dagger)",
            "m_selection_required": False,
            "basis_invariant": True,
        },
        "selected_vector_or_density": {
            "condition": "PARENT_ACTION_SELECTS_A_PROPER_SUBSPACE_OR_STATE_INSIDE_A_DEGENERATE_kj_SPACE",
            "readout": "R_f(rho_A,rho_S)=Tr(rho_A*M_H*rho_S*M_H^dagger)",
            "m_or_density_selection_required": True,
            "projector_trace_cannot_choose_the_state": True,
        },
        "scientific_decision": (
            "DERIVE_THE_CURRENT_C2_ACTION_TRACE_DOMAIN_BEFORE_REQUESTING_EXPLICIT_m"
        ),
    }


def exact_remaining_owner() -> dict[str, Any]:
    return {
        "basis_ambiguity_removed_from": "FULL_RETAINED_SUBSPACE_OVERLAP_RESPONSE",
        "still_missing_from_parent_action": [
            "normalized_current_C2_internal_scalar_multiplication_operator_M_H",
            "proof_that_the_action_trace_uses_the_complete_retained_kj_subspaces",
            "common_trace_and_field_normalization",
        ],
        "conditional_sector_residue_relation": (
            "|c_f|^2=C_common*Tr(P_A,f*M_H*P_S,f*M_H^dagger)"
        ),
        "conditional_ratio_relation": (
            "|c_u/c_d|^2=R_u/R_d_IF_C_common_AND_FIELD_NORMALIZATION_ARE_SHARED"
        ),
        "historical_boundary_targets_relabelled_as_residues": False,
        "individual_m_guessed_or_fitted": False,
        "independent_yukawa_or_mass_fit_allowed": False,
    }


def claim_boundary() -> dict[str, Any]:
    return {
        "CURRENT_C2_QUARK_PROJECTOR_OVERLAP_FUNCTIONAL_DERIVED": True,
        "CURRENT_C2_QUARK_PROJECTOR_OVERLAP_BASIS_INVARIANT": True,
        "CURRENT_C2_QUARK_FULL_MULTIPLET_TRACE_ROUTE_IDENTIFIED_CONDITIONAL": True,
        "CURRENT_C2_QUARK_ACTION_TRACE_DOMAIN_DERIVED": False,
        "CURRENT_C2_NORMALIZED_INTERNAL_SCALAR_MAP_DERIVED": False,
        "CURRENT_C2_UP_DOWN_YUKAWA_VERTEX_RESIDUES_ACTION_DERIVED": False,
        "CURRENT_C2_PHYSICAL_QUARK_POLES_DERIVED": False,
        "CKM_MATRIX_DERIVED": False,
        "MEASURED_QUARK_MASS_USED": False,
        "particle_spectrum_rebuilt": False,
        "FULL_BHSM_COMPLETE": False,
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "action_trace_bifurcation",
    "basis_invariance_witness",
    "claim_boundary",
    "current_family_projector_contract",
    "exact_remaining_owner",
    "projector_overlap_response",
]
