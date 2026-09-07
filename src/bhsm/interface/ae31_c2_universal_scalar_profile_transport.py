"""Transport the recovered universal scalar profile to the current-C2 domain.

This is an operator/domain theorem.  The historical profile and its canonical
normalization remain conditional inputs until the AE3.1 parent action derives
their attachment to the intrinsic four-dimensional Higgs coordinate.
"""

from __future__ import annotations

from math import isfinite
from typing import Any, Iterable

import numpy as np

from bhsm.interface.ae31_c2_intrinsic_m4_lepton_action import ACTION_VERSION


CLASSIFICATION = "AE31_CURRENT_C2_UNIVERSAL_SCALAR_PROFILE_TRANSPORT"


def universal_profile_operator(
    *, distances: Iterable[float], sigma: float, phi0: float
) -> dict[str, Any]:
    """Evaluate the universal Gaussian profile as a multiplication operator."""

    radius = np.asarray(tuple(distances), dtype=float)
    if radius.ndim != 1 or radius.size == 0:
        raise ValueError("a nonempty one-dimensional distance sample is required")
    if not np.all(np.isfinite(radius)) or np.any(radius < 0.0):
        raise ValueError("distances must be finite and nonnegative")
    if not isfinite(sigma) or sigma < 0.0:
        raise ValueError("sigma must be finite and nonnegative")
    if not isfinite(phi0):
        raise ValueError("phi0 must be finite")

    profile = float(phi0) * np.exp(-float(sigma) * radius**2)
    multiplication = np.diag(profile)
    operator_norm = float(np.linalg.norm(multiplication, ord=2))
    return {
        "profile": "Phi(y)=Phi0*exp[-sigma*d_I(y,y0)^2]",
        "values": profile.tolist(),
        "multiplication_operator": multiplication.tolist(),
        "operator_norm": operator_norm,
        "supremum_bound": abs(float(phi0)),
        "bound_residual": max(0.0, operator_norm - abs(float(phi0))),
        "bounded_for_every_finite_phi0_and_sigma_nonnegative": True,
        "flavor_dependent_width_inserted": False,
    }


def canonical_discrete_normalization(
    *, distances: Iterable[float], measure_weights: Iterable[float], sigma: float
) -> dict[str, Any]:
    """Give the exact quadrature analogue of the canonical L2 normalization."""

    radius = np.asarray(tuple(distances), dtype=float)
    weights = np.asarray(tuple(measure_weights), dtype=float)
    if radius.ndim != 1 or radius.size == 0 or weights.shape != radius.shape:
        raise ValueError("distances and measure_weights must have one matching shape")
    if not np.all(np.isfinite(radius)) or np.any(radius < 0.0):
        raise ValueError("distances must be finite and nonnegative")
    if not np.all(np.isfinite(weights)) or np.any(weights <= 0.0):
        raise ValueError("measure_weights must be finite and positive")
    if not isfinite(sigma) or sigma < 0.0:
        raise ValueError("sigma must be finite and nonnegative")

    normalization_integral = float(np.sum(weights * np.exp(-2.0 * sigma * radius**2)))
    phi0 = normalization_integral ** -0.5
    profile = phi0 * np.exp(-sigma * radius**2)
    norm_squared = float(np.sum(weights * profile**2))
    return {
        "continuum_formula": (
            "Phi0=[integral_B exp(-2*sigma*d_I(y,y0)^2)*dmu_Berger]^-1/2"
        ),
        "normalization_integral": normalization_integral,
        "phi0": phi0,
        "weighted_norm_squared": norm_squared,
        "unit_norm_residual": abs(norm_squared - 1.0),
        "independent_amplitude_after_canonical_normalization": False,
        "BHSM_profile_measure_numerically_evaluated": False,
    }


def current_c2_tensor_domain_transport(*, profile_values: Iterable[float]) -> dict[str, Any]:
    """Verify that a bounded internal multiplier preserves the radial domain."""

    profile = np.asarray(tuple(profile_values), dtype=float)
    if profile.ndim != 1 or profile.size == 0 or not np.all(np.isfinite(profile)):
        raise ValueError("a finite nonempty profile is required")
    radial = np.asarray(((2.0, -1.0, 0.0), (-1.0, 2.0, -1.0), (0.0, -1.0, 2.0)))
    radial_lift = np.kron(radial, np.eye(profile.size))
    profile_lift = np.kron(np.eye(radial.shape[0]), np.diag(profile))
    return {
        "tensor_operator": "I_C2 tensor M_Phi",
        "domain_identity": (
            "(D_C2 tensor I)(I tensor M_Phi)=(I tensor M_Phi)(D_C2 tensor I)"
        ),
        "sample_commutator_residual": float(
            np.linalg.norm(radial_lift @ profile_lift - profile_lift @ radial_lift)
        ),
        "bounded_internal_multiplier_preserves_Domain_D_C2_tensor_I": True,
        "reset_generated_C2_radial_operator_unchanged": True,
        "retained_birth_trace_unchanged": True,
        "endpoint_boundary_condition_reselected": False,
    }


def finite_projector_response_bound(
    *,
    active_projector: Iterable[Iterable[float]],
    scalar_map: Iterable[Iterable[float]],
    singlet_projector: Iterable[Iterable[float]],
) -> dict[str, Any]:
    """Bound the compressed trace without requiring a global operator trace."""

    p_active = np.asarray(tuple(tuple(row) for row in active_projector), dtype=float)
    p_singlet = np.asarray(tuple(tuple(row) for row in singlet_projector), dtype=float)
    scalar = np.asarray(tuple(tuple(row) for row in scalar_map), dtype=float)
    if (
        p_active.ndim != 2
        or p_active.shape[0] != p_active.shape[1]
        or p_singlet.shape != p_active.shape
        or scalar.shape != p_active.shape
    ):
        raise ValueError("all inputs must be square matrices on one space")
    for projector, name in ((p_active, "active"), (p_singlet, "singlet")):
        if not np.allclose(projector, projector.T, atol=1e-12) or not np.allclose(
            projector @ projector, projector, atol=1e-12
        ):
            raise ValueError(f"{name} input must be an orthogonal projector")
    compressed = p_active @ scalar @ p_singlet
    response = float(np.linalg.norm(compressed, ord="fro") ** 2)
    operator_norm = float(np.linalg.norm(scalar, ord=2))
    rank_bound = min(round(float(np.trace(p_active))), round(float(np.trace(p_singlet))))
    upper_bound = float(rank_bound) * operator_norm**2
    return {
        "response": response,
        "finite_rank_bound": "R<=min(rank(P_A),rank(P_S))*||M_Phi||_op^2",
        "upper_bound": upper_bound,
        "bound_residual": max(0.0, response - upper_bound),
        "compressed_operator_is_hilbert_schmidt": True,
        "global_uncompressed_trace_class_assumed": False,
        "parent_action_full_multiplet_trace_selected": False,
    }


def conjugate_channel_universality() -> dict[str, Any]:
    return {
        "up_scalar": "H_tilde=epsilon*complex_conjugate(H)",
        "down_scalar": "H",
        "internal_maps": "M_Htilde=epsilon*M_Phi^bar,_M_H=M_Phi",
        "one_universal_profile": True,
        "flavor_or_generation_dependent_sigma_allowed": False,
        "equal_operator_norms_for_conjugate_profile": True,
        "equal_up_down_projector_responses_forced": False,
        "reason": "P_A,up/P_S,up_AND_P_A,down/P_S,down_ARE_DIFFERENT_COMPRESSIONS",
    }


def provenance_and_action_gate() -> dict[str, Any]:
    return {
        "historical_profile_status": "UNIVERSAL_HIGGS_TOPOGRAPHIC_PROFILE_DERIVED_CONDITIONAL",
        "canonical_Z_H_status": "DERIVED_CONDITIONAL_FROM_AUTHOR_PROFILE_NORMALIZATION_AXIOM",
        "canonical_Z_H_formula": "integral_B|Phi|^2*dmu_Berger=1",
        "sigma_action_derived_in_current_AE31": False,
        "Phi0_from_current_Berger_measure_evaluated": False,
        "intrinsic_M4_H_to_internal_profile_attachment_action_derived": False,
        "conditional_transport_is_not_action_ownership": True,
        "old_boundary_no_fit_values_used_as_quark_yukawa_inputs": False,
    }


def exact_remaining_owner() -> dict[str, Any]:
    return {
        "next_action_variation": (
            "DELTA_S_AE31/DELTA_H_INTERNAL_AT_FIXED_CURRENT_C2_DOMAIN_TO_DERIVE_"
            "H(x)_MAPS_TO_H(x)*Phi(y)_AND_THE_RETAINED_INTERNAL_TRACE"
        ),
        "then_evaluate": [
            "sigma_and_Phi0_from_the_same_profile_action_and_Berger_measure",
            "R_up_and_R_down_on_the_preserved_family_projectors",
            "common_trace_and_field_normalization",
        ],
        "m_weight_required_if_full_multiplet_trace_selected": False,
        "independent_sector_profile_widths_allowed": False,
        "independent_yukawa_or_mass_fit_allowed": False,
    }


def claim_boundary() -> dict[str, Any]:
    return {
        "CURRENT_C2_UNIVERSAL_SCALAR_PROFILE_BOUNDED_MULTIPLIER_DERIVED_CONDITIONAL": True,
        "CURRENT_C2_UNIVERSAL_SCALAR_PROFILE_PRESERVES_RADIAL_DOMAIN": True,
        "CURRENT_C2_FINITE_PROJECTOR_OVERLAP_TRACE_FINITE": True,
        "CURRENT_C2_INTRINSIC_HIGGS_INTERNAL_PROFILE_ATTACHMENT_ACTION_DERIVED": False,
        "CURRENT_C2_PROFILE_SIGMA_AND_AMPLITUDE_ACTION_DERIVED": False,
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
    "canonical_discrete_normalization",
    "claim_boundary",
    "conjugate_channel_universality",
    "current_c2_tensor_domain_transport",
    "exact_remaining_owner",
    "finite_projector_response_bound",
    "provenance_and_action_gate",
    "universal_profile_operator",
]
