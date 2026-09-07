"""Fixed-history nonuniqueness of the current-C2 fermion state.

The retained quadratic fermion action fixes the Dirac operator, causal
propagator, CAR pairing, and Hadamard singularity class.  It contains no
boundary state functional.  A finite-rank Bogoliubov rotation inside any
one frozen family sector therefore produces a continuum of distinct pure
Hadamard covariances with exactly the same retained action data.
"""

from __future__ import annotations

from typing import Any

import numpy as np


ACTION_VERSION = "BHSM-AE-3.1.0"
CLASSIFICATION = "CURRENT_C2_FIXED_HISTORY_PURE_STATE_NONUNIQUENESS"


def pure_self_dual_covariance(theta: float) -> dict[str, Any]:
    """Construct the four-mode finite-rank Bogoliubov witness.

    In the ordered basis ``(e1,e2,Gamma e1,Gamma e2)``, take ``e1,e2`` in
    opposite charge sectors of one family.  ``P0`` projects on
    ``span(e1,e2)`` and ``P_theta`` projects on

    ``span(cos(theta)e1+sin(theta)Gamma e2,
           cos(theta)e2-sin(theta)Gamma e1)``.

    Both are pure self-dual CAR covariances.  On the full Cauchy-data space
    the replacement is finite rank, hence smoothing and Hadamard preserving.
    """

    if not np.isfinite(theta):
        raise ValueError("theta must be finite")
    cosine = float(np.cos(theta))
    sine = float(np.sin(theta))
    gamma = np.block(
        [
            [np.zeros((2, 2)), np.eye(2)],
            [np.eye(2), np.zeros((2, 2))],
        ]
    ).astype(complex)
    covariance_zero = np.diag([1.0, 1.0, 0.0, 0.0]).astype(complex)
    charge = np.diag([1.0, -1.0, -1.0, 1.0]).astype(complex)
    positive_frame = np.asarray(
        [
            [cosine, 0.0],
            [0.0, cosine],
            [0.0, -sine],
            [sine, 0.0],
        ],
        dtype=complex,
    )
    covariance_theta = positive_frame @ positive_frame.conj().T
    identity = np.eye(4, dtype=complex)
    eigenvalues = np.linalg.eigvalsh(covariance_theta)
    return {
        "theta": theta,
        "covariance_zero": covariance_zero,
        "covariance_theta": covariance_theta,
        "conjugation_matrix": gamma,
        "charge_grading_matrix": charge,
        "frame_orthonormality_residual": float(
            np.linalg.norm(
                positive_frame.conj().T @ positive_frame - np.eye(2), ord=2
            )
        ),
        "Hermitian_residual": float(
            np.linalg.norm(
                covariance_theta - covariance_theta.conj().T, ord=2
            )
        ),
        "purity_residual": float(
            np.linalg.norm(
                covariance_theta @ covariance_theta - covariance_theta,
                ord=2,
            )
        ),
        "self_dual_CAR_residual": float(
            np.linalg.norm(
                covariance_theta
                + gamma @ covariance_theta.conj() @ gamma.conj().T
                - identity,
                ord=2,
            )
        ),
        "charge_commutator_residual": float(
            np.linalg.norm(
                covariance_theta @ charge - charge @ covariance_theta,
                ord=2,
            )
        ),
        "minimum_eigenvalue": float(np.min(eigenvalues)),
        "maximum_eigenvalue": float(np.max(eigenvalues)),
        "distance_from_zero_covariance": float(
            np.linalg.norm(covariance_theta - covariance_zero, ord=2)
        ),
        "finite_rank_difference_upper_bound": 4,
    }


def finite_rank_hadamard_nonuniqueness_theorem() -> dict[str, Any]:
    """State the fixed-history pure-state nonuniqueness theorem."""

    return {
        "action_version": ACTION_VERSION,
        "hypothesis": (
            "FIX_ANY_CERTIFIED_FINITE_CORE_CURRENT_C2_HISTORY_AND_ONE_PURE_"
            "HADAMARD_COVARIANCE_P_WITH_TWO_SMOOTH_ORTHONORMAL_OPPOSITE_"
            "CHARGE_MODES_IN_ONE_FROZEN_FAMILY_SECTOR"
        ),
        "construction": (
            "REPLACE_P_ON_SPAN(e1,e2,Gamma*e1,Gamma*e2)_BY_P_theta_"
            "PROJECTING_ON_(cos(theta)e1+sin(theta)Gamma*e2,_"
            "cos(theta)e2-sin(theta)Gamma*e1)"
        ),
        "parameter_domain": "theta_IN_AN_OPEN_REAL_INTERVAL_ABOUT_ZERO",
        "P_theta_is_Hermitian": True,
        "P_theta_squared_equals_P_theta": True,
        "P_theta_plus_Gamma_P_theta_Gamma_equals_I": True,
        "zero_le_P_theta_le_I": True,
        "P_theta_minus_P_is_finite_rank_smoothing": True,
        "Hadamard_wavefront_and_polarization_unchanged": True,
        "gauge_charge_grading_unchanged": True,
        "family_projectors_unchanged": True,
        "Dirac_operator_and_causal_propagator_unchanged": True,
        "classical_quadratic_action_unchanged": True,
        "distinct_for_generic_nonzero_theta": True,
        "continuum_of_distinct_pure_Hadamard_covariances": True,
        "reset_transport_preserves_the_continuum": True,
        "why_reset_preserves_it": (
            "UNITARY_CONJUGATION_IS_BIJECTIVE_AND_THE_RESET_LIFT_IS_"
            "SPIN_GAUGE_TENSOR_I_F"
        ),
        "history_selection_alone_selects_a_state": False,
        "state_selection_requires_additional_action_owned_input": True,
    }


def retained_selector_status() -> dict[str, Any]:
    """Separate the open history problem from the stronger state problem."""

    return {
        "current_Gate7_continuous_action_constrained_history": "OPEN",
        "stored_quarter_DOP853_center_is_physical_history": False,
        "mathematical_asymptotic_branch_is_owner_realized": False,
        "asymptotic_branch_log_radius_rate_limit": "H4_TO_H0_POSITIVE",
        "asymptotic_stationary_vacuum_condition_derived": False,
        "complete_child_boundary_H_xi_executable": False,
        "selected_child_boundary_ensemble_present": False,
        "classical_constraint_reduced_Legendre_energy": 0.0,
        "Legendre_energy_can_be_relabelled_state_Hamiltonian": False,
        "even_a_future_unique_history_would_remove_covariance_freedom": False,
        "missing_state_selector": (
            "AN_ACTION_OWNED_BOUNDARY_COVARIANCE_OR_EQUIVALENT_"
            "SPECTRAL_EUCLIDEAN_OR_ASYMPTOTIC_CONDITION_THAT_FIXES_THE_"
            "SMOOTH_BISOLUTION_PART"
        ),
    }


def claim_boundary() -> dict[str, Any]:
    return {
        "CURRENT_C2_FIXED_HISTORY_PURE_HADAMARD_STATE_NONUNIQUENESS_DERIVED": True,
        "CURRENT_C2_HISTORY_SELECTION_ALONE_SUFFICIENT_FOR_STATE_SELECTION": False,
        "CURRENT_C2_ACTION_SELECTED_HADAMARD_STATE_DERIVED": False,
        "CURRENT_C2_ACTION_OWNED_FEYNMAN_TWO_POINT_FUNCTION_DERIVED": False,
        "CURRENT_C2_DRESSED_CHARGED_LEPTON_POLES_DERIVED": False,
        "CURRENT_C2_PHYSICAL_MUON_POLE_DERIVED": False,
        "MUON_MAGNETIC_MOMENT_DERIVED": False,
        "new_state_parameter_inserted": False,
        "particle_spectrum_rebuilt": False,
        "exact_next_operator": (
            "COMPLETE_AN_ACTION_OWNED_STATE_SELECTING_BOUNDARY_OR_"
            "ASYMPTOTIC_CONDITION__THEN_TRANSPORT_THE_SELECTED_COVARIANCE_"
            "AND_ASSEMBLE_THE_DRESSED_CHARGED_LEPTON_TWO_POINT_OPERATOR"
        ),
        "FULL_BHSM_COMPLETE": False,
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "claim_boundary",
    "finite_rank_hadamard_nonuniqueness_theorem",
    "pure_self_dual_covariance",
    "retained_selector_status",
]
