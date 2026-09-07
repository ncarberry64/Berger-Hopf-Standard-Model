"""AE2 reset transport of the AE3.1 current-C2 fermion state class.

The selected reset lift acts only on the spin--gauge factor.  Conjugation by
that unitary therefore transports self-dual CAR covariances across the reset
without changing the frozen family labels or the Hadamard polarization.  The
map carries every admissible upstream state into the child enclosure but does
not select which upstream state is physical.
"""

from __future__ import annotations

from typing import Any, Sequence

import numpy as np

from bhsm.interface.action_extension_global_spin_reset_ae2 import (
    validate_unitary,
)


ACTION_VERSION = "BHSM-AE-3.1.0"
CLASSIFICATION = "CURRENT_C2_RESET_HADAMARD_STATE_CLASS_TRANSPORT"


def _square_matrix(
    value: Sequence[Sequence[complex]], name: str
) -> np.ndarray:
    matrix = np.asarray(value, dtype=complex)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError(f"{name} must be a square matrix")
    if not np.all(np.isfinite(matrix)):
        raise ValueError(f"{name} must be finite")
    return matrix


def transport_self_dual_covariance(
    covariance_event: Sequence[Sequence[complex]],
    reset_lift: Sequence[Sequence[complex]],
    conjugation_event: Sequence[Sequence[complex]],
    conjugation_child: Sequence[Sequence[complex]],
    *,
    tolerance: float = 1.0e-10,
) -> dict[str, Any]:
    """Transport a finite self-dual CAR covariance by the reset unitary.

    ``Gamma(v)=G*conjugate(v)`` is represented by the matrices ``G``.  Hence
    reset compatibility is ``U G_event = G_child conjugate(U)`` and the CAR
    reality constraint is ``C + G conjugate(C) G^dagger = I``.
    """

    covariance = _square_matrix(covariance_event, "covariance_event")
    lift = validate_unitary(reset_lift, tolerance=tolerance)
    gamma_event = validate_unitary(conjugation_event, tolerance=tolerance)
    gamma_child = validate_unitary(conjugation_child, tolerance=tolerance)
    if not (
        covariance.shape == lift.shape == gamma_event.shape == gamma_child.shape
    ):
        raise ValueError("covariance, reset lift, and conjugations must agree")

    size = covariance.shape[0]
    identity = np.eye(size, dtype=complex)
    event_conjugation_involution_residual = float(
        np.linalg.norm(gamma_event @ gamma_event.conj() - identity, ord=2)
    )
    child_conjugation_involution_residual = float(
        np.linalg.norm(gamma_child @ gamma_child.conj() - identity, ord=2)
    )
    hermitian_residual = float(
        np.linalg.norm(covariance - covariance.conj().T, ord=2)
    )
    eigenvalues = np.linalg.eigvalsh((covariance + covariance.conj().T) / 2.0)
    order_margin = min(float(np.min(eigenvalues)), float(1.0 - np.max(eigenvalues)))
    event_reality_residual = float(
        np.linalg.norm(
            covariance
            + gamma_event @ covariance.conj() @ gamma_event.conj().T
            - identity,
            ord=2,
        )
    )
    intertwining_residual = float(
        np.linalg.norm(
            lift @ gamma_event - gamma_child @ lift.conj(), ord=2
        )
    )
    if hermitian_residual > tolerance:
        raise ValueError("event covariance must be Hermitian")
    if (
        event_conjugation_involution_residual > tolerance
        or child_conjugation_involution_residual > tolerance
    ):
        raise ValueError("CAR conjugations must be antiunitary involutions")
    if order_margin < -tolerance:
        raise ValueError("event covariance must satisfy 0 <= C <= I")
    if event_reality_residual > tolerance:
        raise ValueError("event covariance violates the self-dual CAR constraint")
    if intertwining_residual > tolerance:
        raise ValueError("reset lift must intertwine the CAR conjugations")

    child = lift @ covariance @ lift.conj().T
    child_reality_residual = float(
        np.linalg.norm(
            child + gamma_child @ child.conj() @ gamma_child.conj().T - identity,
            ord=2,
        )
    )
    inverse_residual = float(
        np.linalg.norm(lift.conj().T @ child @ lift - covariance, ord=2)
    )
    event_purity_residual = float(
        np.linalg.norm(covariance @ covariance - covariance, ord=2)
    )
    child_purity_residual = float(
        np.linalg.norm(child @ child - child, ord=2)
    )
    child_eigenvalues = np.linalg.eigvalsh((child + child.conj().T) / 2.0)
    return {
        "covariance_child": child,
        "event_eigenvalues": eigenvalues,
        "child_eigenvalues": child_eigenvalues,
        "event_Hermitian_residual": hermitian_residual,
        "event_conjugation_involution_residual": (
            event_conjugation_involution_residual
        ),
        "child_conjugation_involution_residual": (
            child_conjugation_involution_residual
        ),
        "event_order_margin": order_margin,
        "event_self_dual_CAR_residual": event_reality_residual,
        "reset_conjugation_intertwining_residual": intertwining_residual,
        "child_self_dual_CAR_residual": child_reality_residual,
        "inverse_transport_residual": inverse_residual,
        "event_purity_residual": event_purity_residual,
        "child_purity_residual": child_purity_residual,
        "positivity_and_order_preserved": bool(
            np.min(child_eigenvalues) >= -tolerance
            and np.max(child_eigenvalues) <= 1.0 + tolerance
        ),
        "self_dual_CAR_constraint_preserved": child_reality_residual <= tolerance,
        "purity_preserved": abs(
            event_purity_residual - child_purity_residual
        ) <= tolerance,
        "transport_is_bijective": inverse_residual <= tolerance,
    }


def finite_reset_transport_witness() -> dict[str, Any]:
    """Return a nontrivial pure covariance transport certificate."""

    root_half = 1.0 / np.sqrt(2.0)
    particle_lift = root_half * np.asarray(
        [[1.0, 1.0j], [1.0j, 1.0]], dtype=complex
    )
    lift = np.block(
        [
            [particle_lift, np.zeros((2, 2), dtype=complex)],
            [np.zeros((2, 2), dtype=complex), particle_lift.conj()],
        ]
    )
    gamma = np.block(
        [
            [np.zeros((2, 2)), np.eye(2)],
            [np.eye(2), np.zeros((2, 2))],
        ]
    )
    covariance = np.diag([1.0, 0.0, 0.0, 1.0]).astype(complex)
    result = transport_self_dual_covariance(
        covariance,
        lift,
        gamma,
        gamma,
    )
    child = result.pop("covariance_child")
    witness = {
        key: value.tolist() if isinstance(value, np.ndarray) else value
        for key, value in result.items()
    }
    witness["covariance_child_real"] = child.real.tolist()
    witness["covariance_child_imag"] = child.imag.tolist()
    return witness


def reset_hadamard_transport_theorem() -> dict[str, Any]:
    """State the exact event-to-child state-class transport theorem."""

    return {
        "action_version": ACTION_VERSION,
        "reset_action_version": "BHSM-AE-2.0.0",
        "covariance_map": "C_child=U_R*C_event*U_R_dagger",
        "inverse_map": "C_event=U_R_dagger*C_child*U_R",
        "CAR_automorphism": "alpha_R(A(F))=A(U_R*F)",
        "reset_lift_unitary": True,
        "reset_lift_intertwines_CAR_conjugation": True,
        "positivity_and_0_le_C_le_I_preserved": True,
        "self_dual_CAR_constraint_preserved": True,
        "purity_preserved": True,
        "quasifree_state_class_transport_bijective": True,
        "Dirac_principal_symbol_intertwining": (
            "U_R*gamma_event(xi)*U_R_dagger="
            "gamma_child(Lambda_R_pushforward(xi))"
        ),
        "future_null_covectors_map_to_future_null_covectors": True,
        "Hadamard_wavefront_and_polarization_preserved": True,
        "why_Hadamard_is_preserved": (
            "U_R_IS_A_SMOOTH_SPIN_GAUGE_BUNDLE_ISOMORPHISM_AND_IS_THE_"
            "IDENTITY_IN_THE_COMMON_RESET_FRAME_UP_TO_GLOBAL_SPIN_SIGN_"
            "AND_GAUGE_FRAME"
        ),
        "family_factor_of_reset_lift": "I_F",
        "commutes_with_frozen_family_projectors": True,
        "commutes_with_family_mass_endomorphism": True,
        "upstream_Hadamard_particle_state_reaches_child_enclosure": True,
        "statement_is_conditional_on_an_upstream_state": True,
        "one_upstream_or_child_state_selected": False,
        "Bogoliubov_particle_number_derived": False,
        "new_state_parameter_inserted": False,
    }


def claim_boundary() -> dict[str, Any]:
    return {
        "AE2_RESET_HADAMARD_STATE_CLASS_TRANSPORT_DERIVED": True,
        "UPSTREAM_HADAMARD_PARTICLE_STATE_CARRIED_INTO_CURRENT_C2_ENCLOSURE": True,
        "RESET_TRANSPORT_PRESERVES_FROZEN_FAMILY_IDENTITY": True,
        "RESET_SELECTS_UNIQUE_PHYSICAL_FERMION_STATE": False,
        "CURRENT_C2_ACTION_SELECTED_HADAMARD_STATE_DERIVED": False,
        "CURRENT_C2_DRESSED_CHARGED_LEPTON_POLES_DERIVED": False,
        "BOGOLIUBOV_PARTICLE_PRODUCTION_DERIVED": False,
        "MUON_MAGNETIC_MOMENT_DERIVED": False,
        "particle_spectrum_rebuilt": False,
        "exact_next_operator": (
            "ACTION_SELECTED_UPSTREAM_CAUCHY_COVARIANCE_OR_MAXIMAL_"
            "ASYMPTOTIC_STATE_SELECTOR__THEN_THE_TRANSPORTED_DRESSED_"
            "CHARGED_LEPTON_TWO_POINT_OPERATOR"
        ),
        "FULL_BHSM_COMPLETE": False,
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "claim_boundary",
    "finite_reset_transport_witness",
    "reset_hadamard_transport_theorem",
    "transport_self_dual_covariance",
]
