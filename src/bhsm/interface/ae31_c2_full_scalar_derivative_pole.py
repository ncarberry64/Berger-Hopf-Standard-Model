"""Full intrinsic/composite scalar derivative pole on current C2.

The intrinsic charged-lepton Higgs vertex and the charged-lepton gauge-HS
vertex act on the same family block.  Their external-momentum bubble is the
Gram matrix of ``Y_l`` and ``I_3``.  The up and down gauge-HS vertices occupy
orthogonal species blocks.  This yields the complete universal four-field
derivative pole without selecting a finite covariance or subtraction.
"""

from __future__ import annotations

from math import isfinite, pi
from typing import Any

import numpy as np

from bhsm.interface.ae31_c2_intrinsic_m4_lepton_action import (
    ACTION_VERSION,
    charged_lepton_yukawa_operator,
)


CLASSIFICATION = "AE31_CURRENT_C2_FULL_SCALAR_DERIVATIVE_POLE"
FIELD_BASIS = ("H_intrinsic", "H_HS_e", "H_HS_up", "H_HS_down")


def scalar_vertex_gram_matrix() -> dict[str, Any]:
    """Build the exact family/species trace Gram matrix of scalar vertices."""

    yukawa = np.asarray(
        charged_lepton_yukawa_operator()["family_operator"], dtype=float
    )
    identity = np.eye(3)
    trace_y = float(np.trace(yukawa))
    trace_y2 = float(np.trace(yukawa @ yukawa))
    gram = np.asarray(
        (
            (trace_y2, trace_y, 0.0, 0.0),
            (trace_y, 3.0, 0.0, 0.0),
            (0.0, 0.0, 9.0, 0.0),
            (0.0, 0.0, 0.0, 9.0),
        )
    )
    lepton = gram[:2, :2]
    eigenvalues, eigenvectors = np.linalg.eigh(gram)
    family_values = np.diag(yukawa)
    pairwise_square_sum = sum(
        float((family_values[left] - family_values[right]) ** 2)
        for left in range(3)
        for right in range(left + 1, 3)
    )
    variance_identity = 3.0 * trace_y2 - trace_y**2
    return {
        "field_basis": list(FIELD_BASIS),
        "vertex_vectors": {
            "H_intrinsic": "Y_l_ON_charged_lepton_family_space",
            "H_HS_e": "I3_ON_charged_lepton_family_space",
            "H_HS_up": "I9_ON_up_color_family_pairings",
            "H_HS_down": "I9_ON_down_color_family_pairings",
        },
        "Gram_matrix": gram.tolist(),
        "trace_Y_l": trace_y,
        "trace_Y_l_squared": trace_y2,
        "charged_lepton_block_determinant": float(np.linalg.det(lepton)),
        "variance_identity": variance_identity,
        "pairwise_family_difference_square_sum": pairwise_square_sum,
        "variance_identity_residual": abs(variance_identity - pairwise_square_sum),
        "Y_l_family_noncentral": len(set(family_values.tolist())) == 3,
        "Gram_eigenvalues": eigenvalues.tolist(),
        "Gram_eigenvectors_columns": eigenvectors.tolist(),
        "Gram_rank": int(np.linalg.matrix_rank(gram, tol=1.0e-14)),
        "positive_definite": bool(np.all(eigenvalues > 0.0)),
        "species_off_diagonal_blocks_zero": True,
        "measured_lepton_mass_used": False,
    }


def full_lorentzian_derivative_symbol(
    *, omega: float, spatial_eigenvalue: float, epsilon_uv: float = 1.0
) -> dict[str, Any]:
    """Evaluate the universal four-field Laurent pole and tree derivative."""

    frequency = float(omega)
    laplacian = float(spatial_eigenvalue)
    epsilon = float(epsilon_uv)
    if not all(isfinite(value) for value in (frequency, laplacian, epsilon)):
        raise ValueError("finite symbol data required")
    if laplacian < 0.0 or epsilon <= 0.0:
        raise ValueError("nonnegative spatial eigenvalue and positive pole coordinate required")

    gram = np.asarray(scalar_vertex_gram_matrix()["Gram_matrix"], dtype=float)
    pole = gram / (16.0 * pi**2 * epsilon)
    tree = np.diag((1.0, 0.0, 0.0, 0.0))
    covector_square = -frequency**2 + laplacian
    return {
        "field_basis": list(FIELD_BASIS),
        "metric": "h=-d_tau^2+R4(tau)^2*dOmega3^2",
        "frequency_domain": "CONTINUOUS_REAL_OMEGA__NOT_PERIODIC_CYCLE_MODE",
        "Lorentzian_covector_square": covector_square,
        "tree_derivative_matrix": tree.tolist(),
        "universal_loop_pole_matrix": pole.tolist(),
        "full_derivative_Laurent_matrix_at_epsilon_coordinate": (
            tree + pole
        ).tolist(),
        "Hessian_principal_symbol": ((tree + pole) * covector_square).tolist(),
        "formula": (
            "H_derivative=[diag(1,0,0,0)+Gram(V)/(16*pi^2*epsilon_UV)]*"
            "(-omega^2+lambda_scalar)"
        ),
        "same_temporal_spatial_matrix": True,
        "tree_intrinsic_H_kinetic_term_reused": True,
        "finite_loop_derivative_matrix_selected": False,
    }


def family_noncentral_rank_theorem() -> dict[str, Any]:
    """State why the intrinsic/HS lepton kinetic block has rank two."""

    gram = scalar_vertex_gram_matrix()
    determinant = float(gram["charged_lepton_block_determinant"])
    return {
        "charged_lepton_derivative_pole_block": (
            "[[Tr(Y_l^2),Tr(Y_l)],[Tr(Y_l),3]]/[16*pi^2*epsilon_UV]"
        ),
        "determinant_numerator": "3*Tr(Y_l^2)-Tr(Y_l)^2",
        "determinant_identity": "sum_(i<j)(y_i-y_j)^2",
        "determinant_value": determinant,
        "strictly_positive": determinant > 0.0,
        "reason": "THREE_DISTINCT_ACTION_OWNED_CHARGED_LEPTON_FAMILY_EIGENVALUES",
        "family_central_limit_would_have_rank_one": True,
        "current_family_noncentral_block_rank": 2,
        "full_four_field_pole_rank": gram["Gram_rank"],
        "intrinsic_and_charged_lepton_HS_directions_redundant": False,
        "family_hierarchy_rebuilt": False,
    }


def derivative_eigenmode_boundary() -> dict[str, Any]:
    """Separate UV kinetic eigenmodes from physical scalar mass eigenmodes."""

    gram = scalar_vertex_gram_matrix()
    return {
        "universal_pole_kinetic_eigenvalues": gram["Gram_eigenvalues"],
        "universal_pole_kinetic_eigenvectors_columns": gram[
            "Gram_eigenvectors_columns"
        ],
        "UV_derivative_eigendirections_action_derived": True,
        "finite_canonical_fields_derived": False,
        "zero_momentum_masslike_Hessian_derived": False,
        "kinetic_and_masslike_matrices_simultaneously_diagonalized": False,
        "physical_lightest_or_broken_scalar_selected": False,
        "why": (
            "A_PHYSICAL_GENERALIZED_EIGENPROBLEM_REQUIRES_THE_FINITE_"
            "RENORMALIZED_DERIVATIVE_MATRIX_AND_ZERO_MOMENTUM_HESSIAN"
        ),
    }


def exact_remaining_owner() -> dict[str, Any]:
    return {
        "closed": [
            "complete_four_field_universal_derivative_pole_matrix",
            "intrinsic_charged_lepton_HS_cross_derivative_pole",
            "family_noncentral_rank_two_lepton_block",
            "full_rank_four_field_UV_kinetic_form",
        ],
        "still_required": [
            "finite_current_C2_derivative_matching_condition",
            "renormalized_zero_momentum_four_field_Hessian",
            "physical_generalized_scalar_eigenproblem",
            "nonzero_broken_mode_and_canonical_Yukawa_pushforward",
        ],
        "next_operator": (
            "H0_ren*v=m_squared*Z_ren*v_ON_"
            "(H_intrinsic,H_HS_e,H_HS_up,H_HS_down)"
        ),
        "old_EC_residue_or_fitted_scalar_normalization_allowed": False,
    }


def claim_boundary() -> dict[str, Any]:
    return {
        "CURRENT_C2_FULL_FOUR_FIELD_DERIVATIVE_PRINCIPAL_POLE_DERIVED": True,
        "CURRENT_C2_INTRINSIC_LEPTON_HS_CROSS_DERIVATIVE_POLE_DERIVED": True,
        "CURRENT_C2_FAMILY_NONCENTRAL_LEPTON_KINETIC_RANK_TWO_DERIVED": True,
        "CURRENT_C2_FULL_SCALAR_UV_KINETIC_FORM_POSITIVE_DEFINITE": True,
        "CURRENT_C2_FINITE_FULL_SCALAR_KINETIC_MATRIX_DERIVED": False,
        "CURRENT_C2_RENORMALIZED_ZERO_MOMENTUM_SCALAR_HESSIAN_DERIVED": False,
        "CURRENT_C2_PHYSICAL_SINGLE_HIGGS_DIRECTION_SELECTED": False,
        "CURRENT_C2_CANONICAL_YUKAWA_RESIDUES_DERIVED": False,
        "MEASURED_MASS_USED": False,
        "particle_spectrum_rebuilt": False,
        "FULL_BHSM_COMPLETE": False,
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "FIELD_BASIS",
    "claim_boundary",
    "derivative_eigenmode_boundary",
    "exact_remaining_owner",
    "family_noncentral_rank_theorem",
    "full_lorentzian_derivative_symbol",
    "scalar_vertex_gram_matrix",
]
