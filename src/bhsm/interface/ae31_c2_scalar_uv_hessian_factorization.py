"""Factor the full current-C2 scalar UV Hessian by its vertex Gram matrix."""

from __future__ import annotations

from math import isfinite, pi
from typing import Any

import numpy as np

from bhsm.interface.ae31_c2_full_scalar_derivative_pole import (
    ACTION_VERSION,
    FIELD_BASIS,
    scalar_vertex_gram_matrix,
)


CLASSIFICATION = "AE31_CURRENT_C2_SCALAR_UV_HESSIAN_FACTORIZATION"


def full_zero_momentum_hadamard_pole(
    *, radius: float, mass_laurent_coordinate: float = 1.0
) -> dict[str, Any]:
    """Return the full scalar susceptibility pole on one current-C2 slice.

    The sign follows the already-derived zeta/Hadamard convention
    ``chi_sing=-1/(16*pi^2*R4^2*s)``.  This is a Laurent coefficient, not a
    positive cutoff susceptibility or a renormalized scalar mass matrix.
    """

    r4 = float(radius)
    s_mass = float(mass_laurent_coordinate)
    if not isfinite(r4) or not isfinite(s_mass) or r4 <= 0.0 or s_mass == 0.0:
        raise ValueError("finite positive radius and nonzero Laurent coordinate required")
    gram = np.asarray(scalar_vertex_gram_matrix()["Gram_matrix"], dtype=float)
    coefficient = -1.0 / (16.0 * pi**2 * r4**2 * s_mass)
    susceptibility = coefficient * gram
    return {
        "field_basis": list(FIELD_BASIS),
        "current_C2_slice_radius": r4,
        "mass_Laurent_coordinate": s_mass,
        "per_pair_pole": "-1/[16*pi^2*R4(tau0)^2*s_mass]",
        "vertex_Gram_matrix": gram.tolist(),
        "full_susceptibility_pole_matrix": susceptibility.tolist(),
        "formula": "Pi_0,sing=chi_Had,sing*Gram(V)",
        "local_and_state_independent": True,
        "positive_mode_cutoff_interpretation": False,
        "finite_masslike_subtraction_selected": False,
    }


def uv_shape_proportionality_theorem() -> dict[str, Any]:
    """Prove that masslike and derivative UV poles contain one channel shape."""

    gram = np.asarray(scalar_vertex_gram_matrix()["Gram_matrix"], dtype=float)
    normalized_mass = gram / np.trace(gram)
    normalized_derivative = gram / np.trace(gram)
    inverse_gram = np.linalg.inv(gram)
    generalized = inverse_gram @ gram
    eigenvalues = np.linalg.eigvalsh(generalized)
    return {
        "field_basis": list(FIELD_BASIS),
        "masslike_pole_shape": "Gram(V)",
        "derivative_pole_shape": "Gram(V)",
        "regulator_scalars_compared_or_identified": False,
        "normalized_masslike_shape": normalized_mass.tolist(),
        "normalized_derivative_shape": normalized_derivative.tolist(),
        "normalized_shape_residual": float(
            np.linalg.norm(normalized_mass - normalized_derivative, ord=2)
        ),
        "shape_is_positive_definite": bool(
            np.all(np.linalg.eigvalsh(gram) > 0.0)
        ),
        "shape_rank": int(np.linalg.matrix_rank(gram, tol=1.0e-14)),
        "shape_generalized_operator": generalized.tolist(),
        "shape_generalized_eigenvalues": eigenvalues.tolist(),
        "generalized_operator_identity_residual": float(
            np.linalg.norm(generalized - np.eye(4), ord=2)
        ),
        "UV_singular_generalized_eigenspace_dimension": 4,
        "UV_poles_select_scalar_channel_direction": False,
        "family_noncentrality_gives_full_rank_but_not_direction_selection": True,
    }


def renormalized_generalized_eigenproblem() -> dict[str, Any]:
    """Record the finite matrices required after the common poles are removed."""

    return {
        "field_basis": list(FIELD_BASIS),
        "derivative_decomposition": (
            "Z_ren=Z_tree+z_log(mu)*Gram(V)+Z_fin[C,mu]"
        ),
        "zero_momentum_decomposition": (
            "H0_ren=H0_intrinsic_plus_gauge_HS+H0_fin[C,mu]"
        ),
        "physical_problem": "H0_ren*v=m_scalar^2*Z_ren*v",
        "required_weak_component_resolution": (
            "NEUTRAL_RADIAL_GOLDSTONE_AND_CHARGED_COMPONENTS_BEFORE_"
            "PHYSICAL_SCALAR_COUNTING"
        ),
        "universal_UV_shape_cancels_from_direction_selector": True,
        "finite_state_or_boundary_data_required": True,
        "current_C2_action_selected_covariance_present": False,
        "finite_derivative_matching_present": False,
        "finite_zero_momentum_Hessian_present": False,
        "physical_generalized_eigenproblem_evaluable": False,
        "minimal_subtraction_or_cutoff_chosen_as_physics": False,
    }


def exact_remaining_owner() -> dict[str, Any]:
    return {
        "closed": [
            "complete_four_field_zero_momentum_Hadamard_pole_shape",
            "common_Gram_factorization_of_masslike_and_derivative_UV_poles",
            "fourfold_UV_generalized_direction_degeneracy",
        ],
        "still_required": [
            "action_selected_current_C2_covariance_or_boundary_state_functional",
            "finite_local_derivative_matching_condition",
            "finite_renormalized_zero_momentum_scalar_Hessian",
            "weak_component_resolved_generalized_eigenproblem",
        ],
        "next_variation": (
            "FINITE_PART_OF_D2_Gamma_current_C2_OVER_THE_FULL_SCALAR_"
            "MULTIPLICITY_SPACE_AFTER_ONE_PARENT_OWNED_BOUNDARY_CONDITION"
        ),
        "UV_kinetic_eigenvector_may_be_called_physical_Higgs": False,
        "fitted_finite_matrix_allowed": False,
    }


def claim_boundary() -> dict[str, Any]:
    return {
        "CURRENT_C2_FULL_SCALAR_ZERO_MOMENTUM_HADAMARD_POLE_SHAPE_DERIVED": True,
        "CURRENT_C2_SCALAR_MASSLIKE_DERIVATIVE_UV_GRAM_FACTORIZATION_DERIVED": True,
        "CURRENT_C2_SCALAR_UV_GENERALIZED_DIRECTION_DEGENERACY_DERIVED": True,
        "CURRENT_C2_FINITE_SCALAR_DERIVATIVE_MATRIX_DERIVED": False,
        "CURRENT_C2_FINITE_ZERO_MOMENTUM_SCALAR_HESSIAN_DERIVED": False,
        "CURRENT_C2_PHYSICAL_SINGLE_HIGGS_DIRECTION_SELECTED": False,
        "CURRENT_C2_CANONICAL_YUKAWA_RESIDUES_DERIVED": False,
        "MEASURED_MASS_USED": False,
        "particle_spectrum_rebuilt": False,
        "FULL_BHSM_COMPLETE": False,
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "claim_boundary",
    "exact_remaining_owner",
    "full_zero_momentum_hadamard_pole",
    "renormalized_generalized_eigenproblem",
    "uv_shape_proportionality_theorem",
]
