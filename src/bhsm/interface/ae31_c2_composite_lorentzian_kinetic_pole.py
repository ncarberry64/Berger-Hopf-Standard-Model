"""Universal Lorentzian derivative pole of the current-C2 gauge HS fields.

The gauge current kernel already supplies unit left-right Hubbard--Stratonovich
vertices in the up, down, and charged-lepton channels.  This module takes the
external-momentum second variation of the same fermion determinant.  It keeps
the universal Hadamard/UV principal part separate from the finite, state- and
subtraction-dependent kinetic coefficient.
"""

from __future__ import annotations

from fractions import Fraction
from math import isfinite, pi
from typing import Any

import numpy as np

from bhsm.interface.ae31_c2_intrinsic_m4_lepton_action import ACTION_VERSION


CLASSIFICATION = "AE31_CURRENT_C2_COMPOSITE_LORENTZIAN_KINETIC_POLE"


def clifford_trace_witness(q: np.ndarray, p: np.ndarray) -> dict[str, Any]:
    """Verify the chiral numerator with an explicit Euclidean Clifford basis."""

    momentum = np.asarray(q, dtype=float)
    external = np.asarray(p, dtype=float)
    if momentum.shape != (4,) or external.shape != (4,):
        raise ValueError("four-dimensional Euclidean covectors required")
    if not np.all(np.isfinite(momentum)) or not np.all(np.isfinite(external)):
        raise ValueError("finite Euclidean covectors required")

    sigma = (
        np.asarray(((0.0, 1.0), (1.0, 0.0)), dtype=complex),
        np.asarray(((0.0, -1.0j), (1.0j, 0.0)), dtype=complex),
        np.asarray(((1.0, 0.0), (0.0, -1.0)), dtype=complex),
    )
    zero = np.zeros((2, 2), dtype=complex)
    identity2 = np.eye(2, dtype=complex)
    gamma = [
        np.block([[zero, -1.0j * matrix], [1.0j * matrix, zero]])
        for matrix in sigma
    ]
    gamma.append(np.block([[zero, identity2], [identity2, zero]]))
    gamma5 = gamma[0] @ gamma[1] @ gamma[2] @ gamma[3]
    projector_left = (np.eye(4) - gamma5) / 2.0
    projector_right = (np.eye(4) + gamma5) / 2.0
    slash_q = sum(momentum[index] * gamma[index] for index in range(4))
    slash_q_plus_p = sum(
        (momentum[index] + external[index]) * gamma[index]
        for index in range(4)
    )
    trace = np.trace(
        projector_left @ slash_q @ projector_right @ slash_q_plus_p
    )
    expected = 2.0 * float(momentum @ (momentum + external))
    return {
        "trace_real": float(trace.real),
        "trace_imaginary": float(trace.imag),
        "expected_2q_dot_q_plus_p": expected,
        "residual": abs(complex(trace) - expected),
        "Euclidean_Clifford_residual": max(
            float(
                np.linalg.norm(
                    gamma[mu] @ gamma[nu]
                    + gamma[nu] @ gamma[mu]
                    - 2.0 * float(mu == nu) * np.eye(4)
                )
            )
            for mu in range(4)
            for nu in range(4)
        ),
    }


def chiral_bubble_principal_part() -> dict[str, Any]:
    """Return the one-pair momentum-space pole before channel traces.

    For a unit complex LR vertex the two orderings cancel the factor one-half
    in the second log-determinant variation.  Clifford trace gives
    ``2 q.(q+p)``.  Dimensional regularization then removes the two scaleless
    tadpoles in

    ``2 q.(q+p) = q^2 + (q+p)^2 - p^2``.

    The remaining logarithmic integral is the local, regulator-independent
    pole coefficient; no finite subtraction is selected here.
    """

    return {
        "effective_action": "Gamma_fermion=-Tr_log(D_C2+H*P_R+Hdagger*P_L)",
        "quadratic_variation": (
            "Gamma_HdaggerH^(2)(p)=-integral_q_"
            "2*q_dot_(q+p)/[q^2*(q+p)^2]"
        ),
        "Clifford_trace": "tr[P_L*slash(q)*P_R*slash(q+p)]=2*q_dot_(q+p)",
        "numerator_identity": (
            "2*q_dot_(q+p)=q^2+(q+p)^2-p^2"
        ),
        "scaleless_tadpoles_in_dimensional_regularization": 2,
        "one_pair_Euclidean_derivative_pole": (
            "+p_E^2/[16*pi^2*epsilon_UV]"
        ),
        "one_pair_pole_coefficient_without_epsilon": 1.0 / (16.0 * pi**2),
        "finite_part_selected": False,
        "mass_quadratic_part_selected": False,
    }


def current_c2_lorentzian_principal_symbol(
    *, omega: float, spatial_eigenvalue: float, epsilon_uv: float = 1.0
) -> dict[str, Any]:
    """Evaluate the three-channel local pole on a frozen current-C2 slice.

    ``epsilon_uv`` is an audit coordinate for the Laurent pole, not a physical
    cutoff.  The function is useful at ``epsilon_uv=1`` to expose the exact
    residue coefficients without assigning a finite renormalized value.
    """

    frequency = float(omega)
    laplacian = float(spatial_eigenvalue)
    epsilon = float(epsilon_uv)
    if not all(isfinite(value) for value in (frequency, laplacian, epsilon)):
        raise ValueError("finite frequency, spatial eigenvalue, and pole coordinate required")
    if laplacian < 0.0 or epsilon <= 0.0:
        raise ValueError("nonnegative spatial eigenvalue and positive pole coordinate required")

    multiplicities = np.asarray((9.0, 9.0, 3.0))
    residue = multiplicities / (16.0 * pi**2 * epsilon)
    lorentzian_covector_square = -frequency**2 + laplacian
    hessian = residue * lorentzian_covector_square
    return {
        "action_version": ACTION_VERSION,
        "metric": "h=-d_tau^2+R4(tau)^2*dOmega3^2",
        "channel_basis": ["up", "down", "charged_lepton"],
        "pairing_multiplicities": multiplicities.astype(int).tolist(),
        "multiplicity_source": "REUSED_V16_02_RANK16_PAIRING_TRACE",
        "external_frequency": frequency,
        "frequency_domain": "CONTINUOUS_REAL_OMEGA__NOT_PERIODIC_CYCLE_MODE",
        "spatial_scalar_Laplacian_eigenvalue": laplacian,
        "pole_coordinate_epsilon_uv": epsilon,
        "pole_residue_matrix": np.diag(residue).tolist(),
        "Lorentzian_covector_square": lorentzian_covector_square,
        "Hessian_principal_pole": np.diag(hessian).tolist(),
        "formula": (
            "H_HS,sing=(1/[16*pi^2*epsilon_UV])*diag(9,9,3)*"
            "(-omega^2+lambda_scalar)"
        ),
        "same_temporal_and_spatial_residue_per_channel": True,
        "current_C2_local_Lorentzian_cone_inherited_from_Dirac_action": True,
        "finite_current_C2_covariance_selected": False,
    }


def combined_composite_hessian_structure() -> dict[str, Any]:
    """Combine the pole with the already-owned three-channel bare curvature."""

    inverse = (Fraction(5, 14), Fraction(5, 13), Fraction(5, 3))
    multiplicities = (9, 9, 3)
    normalized = tuple(Fraction(value, multiplicities[0]) for value in multiplicities)
    return {
        "channel_basis": ["up", "down", "charged_lepton"],
        "bare_inverse_curvature_over_G_C2": [str(value) for value in inverse],
        "universal_derivative_pole_multiplicities": list(multiplicities),
        "derivative_pole_relative_to_up": [str(value) for value in normalized],
        "low_momentum_Hessian": (
            "H_HS=G_C2^(-1)*diag(5/14,5/13,5/3)-Pi_0,ren[C]+"
            "diag(9,9,3)*(-omega^2+lambda)/[16*pi^2*epsilon_UV]+..."
        ),
        "up_down_derivative_pole_degenerate": True,
        "up_down_bare_curvature_degenerate": False,
        "pole_alone_selects_up_down_direction": False,
        "finite_masslike_Hessian_selected": False,
        "physical_broken_eigenvector_selected": False,
    }


def historical_mass_derivative_adjudication() -> dict[str, Any]:
    """Separate the old static mass derivative from a kinetic residue."""

    return {
        "historical_object": "v15.77_Z_H=-partial_chi_LR/partial_(m^2)",
        "historical_variation": "STATIC_SUSCEPTIBILITY_MASS_PARAMETER_DERIVATIVE",
        "current_object": (
            "partial_(external_p^2)_Gamma_HdaggerH^(2)(p)_at_p=0"
        ),
        "current_variation": "LORENTZIAN_EXTERNAL_MOMENTUM_TWO_POINT_DERIVATIVE",
        "same_functional_derivative": False,
        "historical_numeric_Z_H_promoted_to_current_C2_kinetic_residue": False,
        "historical_gap_branch_revived": False,
        "global_EC_eliminated_action_used": False,
        "valid_historical_pairing_multiplicities_reused": True,
        "scientific_conclusion": (
            "THE_OLD_MINUS_D_CHI_D_M2_NUMBER_IS_NOT_A_WAVEFUNCTION_"
            "NORMALIZATION;_THE_CURRENT_C2_EXTERNAL_MOMENTUM_POLE_IS_DERIVED_"
            "INSTEAD"
        ),
    }


def exact_remaining_owner() -> dict[str, Any]:
    return {
        "closed": [
            "unit_vertex_three_channel_external_momentum_bubble",
            "continuous_frequency_current_C2_Lorentzian_principal_symbol",
            "universal_positive_Euclidean_derivative_pole",
            "same_temporal_spatial_residue_at_the_local_pole",
            "historical_mass_derivative_not_equal_to_kinetic_derivative",
        ],
        "still_required": [
            "action_selected_finite_current_C2_covariance",
            "parent_owned_finite_derivative_subtraction_or_boundary_matching_rule",
            "renormalized_zero_momentum_composite_Hessian",
            "nonzero_gap_and_physical_broken_channel_eigenvector",
        ],
        "next_operator": (
            "RENORMALIZED_FULL_THREE_CHANNEL_LORENTZIAN_HS_HESSIAN_WITH_"
            "FINITE_PI_0_AND_PI_P2_FROM_ONE_CURRENT_C2_ACTION_DOMAIN"
        ),
        "cutoff_fitted_residue_or_old_EC_number_allowed": False,
    }


def claim_boundary() -> dict[str, Any]:
    return {
        "CURRENT_C2_COMPOSITE_LORENTZIAN_PRINCIPAL_POLE_DERIVED": True,
        "CURRENT_C2_COMPOSITE_TEMPORAL_SPATIAL_POLE_RESIDUE_MATCH_DERIVED": True,
        "CURRENT_C2_COMPOSITE_DERIVATIVE_TERM_LOCALLY_INDUCED": True,
        "CURRENT_C2_FINITE_COMPOSITE_KINETIC_RESIDUE_DERIVED": False,
        "CURRENT_C2_RENORMALIZED_COMPOSITE_HESSIAN_DERIVED": False,
        "CURRENT_C2_COMPOSITE_GAP_DERIVED": False,
        "CURRENT_C2_PHYSICAL_SINGLE_HIGGS_DIRECTION_SELECTED": False,
        "CURRENT_C2_CANONICAL_YUKAWA_RESIDUES_DERIVED": False,
        "HISTORICAL_MINUS_DCHI_DM2_USED_AS_KINETIC_RESIDUE": False,
        "MEASURED_MASS_USED": False,
        "particle_spectrum_rebuilt": False,
        "FULL_BHSM_COMPLETE": False,
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "chiral_bubble_principal_part",
    "clifford_trace_witness",
    "claim_boundary",
    "combined_composite_hessian_structure",
    "current_c2_lorentzian_principal_symbol",
    "exact_remaining_owner",
    "historical_mass_derivative_adjudication",
]
