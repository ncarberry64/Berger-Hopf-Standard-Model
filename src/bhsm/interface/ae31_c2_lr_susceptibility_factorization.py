"""Factor the current-C2 left-right susceptibility by singularity class.

The current C2 fermion action determines a Hadamard singularity class but not
one Feynman covariance.  This module transports the exact round-S3 Weyl sum
to every certified Cauchy slice, separates its universal local pole from the
finite state-dependent remainder, and combines that separation with the
already-derived up/down gauge-exchange ray.  No finite subtraction, vacuum,
Yukawa residue, or physical gap is selected here.
"""

from __future__ import annotations

from fractions import Fraction
from math import isfinite, pi
from typing import Any

import numpy as np

from bhsm.interface.ae31_c2_intrinsic_m4_lepton_action import ACTION_VERSION
from bhsm.interface.ae31_c2_quark_channel_selector_domain import (
    hadamard_susceptibility_witness,
)
from bhsm.interface.ae31_c2_quark_higgs_incidence_transport import (
    quark_higgs_support_pencil,
)
from bhsm.interface.aether_lr_susceptibility_zeta_v15_67 import (
    cutoff_dimensionless_sum_closed,
)


CLASSIFICATION = "AE31_CURRENT_C2_LR_SUSCEPTIBILITY_HADAMARD_FACTORIZATION"


def current_c2_slice_susceptibility(max_level: int, radius: float) -> dict[str, Any]:
    """Evaluate the transported spatial Weyl sum on one round C2 slice."""

    level = int(max_level)
    r4 = float(radius)
    if level < 0:
        raise ValueError("nonnegative cutoff level required")
    if not isfinite(r4) or r4 <= 0.0:
        raise ValueError("finite positive C2 slice radius required")
    dimensionless = float(cutoff_dimensionless_sum_closed(level))
    physical = dimensionless / (2.0 * pi**2 * r4**2)
    return {
        "current_C2_metric": "h=-d_tau^2+R4(tau)^2*dOmega3^2",
        "slice": "tau=tau0_WITH_R4(tau0)>0",
        "one_particle_spatial_eigenvalues": "E_n=(n+3/2)/R4(tau0)",
        "multiplicities": "d_n=(n+1)(n+2)",
        "max_level": level,
        "dimensionless_sum": dimensionless,
        "susceptibility": physical,
        "susceptibility_formula": (
            "chi_N(tau0)=S_N/[2*pi^2*R4(tau0)^2]"
        ),
        "positive": physical > 0.0,
        "global_frequency_diagonalization_used": False,
        "slice_sum_promoted_to_Feynman_loop": False,
    }


def hadamard_pole_factorization() -> dict[str, Any]:
    """Derive the common channel pole in unit-incidence HS coordinates."""

    supports = quark_higgs_support_pencil()
    up = np.asarray(supports["I_up"], dtype=float)
    down = np.asarray(supports["I_down"], dtype=float)
    gram = np.asarray(
        (
            (np.trace(up.T @ up), np.trace(up.T @ down)),
            (np.trace(down.T @ up), np.trace(down.T @ down)),
        ),
        dtype=float,
    )
    common_norm = float(gram[0, 0])
    normalized = gram / common_norm
    return {
        "historical_Laurent_series_per_LR_pair": (
            "S(s;q)=-1/(8s)+1/24-gamma_E/4-log(2)/2-log(q)/4+O(s)"
        ),
        "current_C2_physical_pole_per_LR_pair": (
            "-1/[16*pi^2*R4(tau0)^2*s]"
        ),
        "pole_is_local": True,
        "pole_is_state_independent_within_Hadamard_class": True,
        "incidence_Gram_matrix": gram.tolist(),
        "normalized_channel_pole_matrix": normalized.tolist(),
        "normalized_channel_pole_is_identity": bool(
            np.allclose(normalized, np.eye(2), atol=0.0, rtol=0.0)
        ),
        "coordinate_scope": "UNIT_VERTEX_AUXILIARY_HS_CHANNELS",
        "historical_pairing_multiplicity": "diag(9,9)_ON_UP_DOWN",
        "equal_up_down_multiplicity_reused": True,
        "physical_intrinsic_Higgs_residues_inserted": False,
        "finite_local_HdaggerH_subtraction_selected": False,
    }


def composite_hessian_decomposition() -> dict[str, Any]:
    """Decompose the unit-vertex HS Hessian into trace and traceless parts."""

    c_up = Fraction(7, 5)
    c_down = Fraction(13, 10)
    inverse_up = Fraction(1, 2) / c_up
    inverse_down = Fraction(1, 2) / c_down
    trace_coefficient = (inverse_up + inverse_down) / 2
    traceless_coefficient = (inverse_up - inverse_down) / 2
    difference = inverse_up - inverse_down
    return {
        "unit_vertex_HS_Hessian": (
            "H_C=K_LR^(-1)-Pi_Had,sing*I2-Pi_fin[C]"
        ),
        "inverse_kernel": (
            "K_LR^(-1)=G_C2^(-1)*diag(5/14,5/13)"
        ),
        "inverse_kernel_trace_coefficient": f"{trace_coefficient}/G_C2",
        "inverse_kernel_traceless_coefficient": (
            f"{traceless_coefficient}/G_C2"
        ),
        "inverse_kernel_up_minus_down": f"{difference}/G_C2",
        "sigma3_convention": "sigma3=diag(1,-1)",
        "exact_decomposition": (
            "K_LR^(-1)=135/(364*G_C2)*I2-5/(364*G_C2)*sigma3"
        ),
        "universal_Hadamard_pole_traceless_projection": [[0.0, 0.0], [0.0, 0.0]],
        "universal_pole_changes_relative_channel_direction": False,
        "gauge_inverse_curvature_orders_up_below_down_for_positive_G_C2": True,
        "absolute_G_C2_evaluated": False,
        "finite_state_remainder_removed": False,
    }


def finite_state_remainder_witness() -> dict[str, Any]:
    """Show that the smooth Hadamard remainder can still rotate the channels."""

    reference = hadamard_susceptibility_witness(0.0)
    rotated = hadamard_susceptibility_witness(np.pi / 6.0)
    first = np.asarray(reference["susceptibility_matrix"], dtype=float)
    second = np.asarray(rotated["susceptibility_matrix"], dtype=float)
    delta = second - first
    traceless = delta - np.trace(delta) * np.eye(2) / 2.0
    return {
        "same_action_domain_and_Hadamard_singularity": True,
        "finite_response_difference": delta.tolist(),
        "finite_response_difference_norm": float(np.linalg.norm(delta)),
        "traceless_finite_difference": traceless.tolist(),
        "traceless_finite_difference_norm": float(np.linalg.norm(traceless)),
        "finite_remainder_can_change_channel_eigenvectors": bool(
            abs(traceless[0, 1]) > 1.0e-12
        ),
        "witness_is_BHSM_physical_covariance": False,
        "purpose": "PROVE_THE_FINITE_REMAINDER_CANNOT_BE_DROPPED",
        "universal_pole_factorization_selects_physical_direction": False,
    }


def exact_remaining_owner() -> dict[str, Any]:
    return {
        "derived_now": [
            "current_C2_round_slice_spatial_LR_spectral_sum",
            "state_independent_local_Hadamard_pole_factor",
            "unit_vertex_HS_trace_traceless_Hessian_decomposition",
            "cancellation_of_the_common_pole_from_the_traceless_channel",
        ],
        "still_required": [
            "action_selected_current_C2_covariance_or_equivalent_boundary_state_functional",
            "renormalized_finite_local_composite_quadratic_form",
            "finite_Pi_fin_C_in_the_up_down_channels",
            "intrinsic_Higgs_to_unit_vertex_HS_mixing_map",
        ],
        "next_operator": (
            "H_mix=[[H_intrinsic,M_HS],[M_HS^dagger,"
            "K_LR^(-1)-Pi_Had,sing*I2-Pi_fin[C]]]"
        ),
        "cutoff_or_fitted_subtraction_allowed": False,
        "arbitrary_Hadamard_state_allowed": False,
    }


def claim_boundary() -> dict[str, Any]:
    return {
        "CURRENT_C2_LR_ROUND_SLICE_SPECTRAL_SUM_TRANSPORTED": True,
        "CURRENT_C2_LR_HADAMARD_UV_POLE_FACTOR_DERIVED": True,
        "CURRENT_C2_LR_COMMON_POLE_TRACeless_CANCELLATION_DERIVED": True,
        "CURRENT_C2_LR_FINITE_STATE_REMAINDER_NUMERICALLY_DERIVED": False,
        "CURRENT_C2_FULL_RENORMALIZED_LR_HESSIAN_DERIVED": False,
        "CURRENT_C2_MIXED_SINGLE_HIGGS_DIRECTION_SELECTED": False,
        "CURRENT_C2_COMPOSITE_GAP_DERIVED": False,
        "CURRENT_C2_UP_DOWN_YUKAWA_RESIDUES_DERIVED": False,
        "CURRENT_C2_PHYSICAL_QUARK_POLES_DERIVED": False,
        "MEASURED_QUARK_MASS_USED": False,
        "particle_spectrum_rebuilt": False,
        "FULL_BHSM_COMPLETE": False,
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "claim_boundary",
    "composite_hessian_decomposition",
    "current_c2_slice_susceptibility",
    "exact_remaining_owner",
    "finite_state_remainder_witness",
    "hadamard_pole_factorization",
]
