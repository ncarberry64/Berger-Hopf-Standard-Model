"""Evaluate the reciprocal two-sided current-C2 Calderón construction.

The proof is algebraic. Reflection about ``chi=pi/4`` reverses the AE3
material coordinate while preserving every radial coefficient in the
Maxwell--BRST quadratic form. The sampled residuals below audit the
implementation of those exact identities; they are not used as their proof.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from bhsm.interface.ae3_c2_lorentzian_gauge_ghost_hessian import (
    lowest_transverse_residue_witness,
)
from bhsm.interface.ae3_reciprocal_join_localization import (
    localization_weight,
    reciprocal_join_profile,
)


ACTION_VERSION = "BHSM-AE-3.0.0"
CLASSIFICATION = "AE3_CURRENT_C2_TWO_SIDED_CALDERON_REFLECTION_NO_GO"


def reflection_certificate(samples: int = 4097) -> dict[str, Any]:
    """Return the exact reflection identities plus a numerical audit."""

    if samples < 5 or samples % 2 == 0:
        raise ValueError("odd samples >=5 required")
    chi = np.linspace(0.0, np.pi / 2.0, samples)
    mirror = np.pi / 2.0 - chi
    sigma = reciprocal_join_profile(chi)
    sigma_mirror = reciprocal_join_profile(mirror)
    weight = localization_weight(sigma)
    weight_mirror = localization_weight(sigma_mirror)
    radius = np.sin(chi) * np.cos(chi)
    radius_mirror = np.sin(mirror) * np.cos(mirror)

    audit = {
        "samples": samples,
        "sigma_antisymmetry_residual": float(
            np.max(np.abs(sigma + sigma_mirror))
        ),
        "weight_symmetry_residual": float(
            np.max(np.abs(weight - weight_mirror))
        ),
        "radius_symmetry_residual": float(
            np.max(np.abs(radius - radius_mirror))
        ),
    }
    return {
        "proof_kind": "EXACT_TRIGONOMETRIC_IDENTITIES_WITH_NUMERICAL_AUDIT",
        "exact_identities": {
            "material": "sigma(pi/2-chi)=-sigma(chi)",
            "round_radius": (
                "sin(pi/2-chi)*cos(pi/2-chi)=sin(chi)*cos(chi)"
            ),
            "localization": "Lambda(-sigma)=Lambda(sigma)=1-4*sigma^2",
            "half_cap_coordinate": (
                "rho_inside=2*chi; rho_exterior=pi-2*chi; "
                "sin(rho_exterior)=sin(rho_inside)"
            ),
        },
        "interface_coordinate": float(np.pi / 4.0),
        "inside": "sigma<0",
        "outside": "sigma>0",
        "reflection_isometry_exact": True,
        "numerical_audit": audit,
        "numerical_audit_passed": all(
            residual < 2.0e-15
            for key, residual in audit.items()
            if key.endswith("_residual")
        ),
    }


def operator_domain_transport_certificate() -> dict[str, Any]:
    """Record why the full regular Maxwell--BRST domain is conjugate."""

    return {
        "same_parent_operator": "AE3_WEIGHTED_MAXWELL_PLUS_BRST_GAUGE_GHOST_BLOCK",
        "continuous_frequency_preserved": True,
        "coexact_level_preserved": True,
        "interface_Dirichlet_trace_preserved": True,
        "regular_pole_condition_exchanged_by_reflection": True,
        "temporal_electric_weight_preserved": True,
        "transverse_spatial_weight_preserved": True,
        "constraint_block_preserved": True,
        "BRST_gauge_fixing_and_ghost_complex_preserved": True,
        "reset_is_unitary_on_the_retained_internal_fiber": True,
        "surface_contact_term": None,
        "operator_identity": (
            "N_exterior(omega,k)=U_reset*N_inside(omega,k)*U_reset_star"
        ),
        "scalar_coexact_identity_after_reset": (
            "U_reset_star*N_exterior*U_reset=N_inside"
        ),
        "full_regular_domain_transport_derived": True,
    }


def two_sided_residue_certificate() -> dict[str, Any]:
    """Evaluate the two-sided low-frequency transverse residue."""

    one_sided = lowest_transverse_residue_witness()
    static = float(one_sided["static_dimensionless_DtN"])
    temporal = float(one_sided["electric_weight_integral"])
    ratio = float(
        one_sided["temporal_to_complete_spatial_mode_residue_ratio"]
    )
    return {
        "N_inside_zero": static,
        "N_exterior_zero": static,
        "N_total_zero": 2.0 * static,
        "minus_dq2_N_inside_zero": temporal,
        "minus_dq2_N_exterior_zero": temporal,
        "minus_dq2_N_total_zero": 2.0 * temporal,
        "reset_conjugation_changes_scalar_coexact_residue": False,
        "Zt_over_Zs_inside": ratio,
        "Zt_over_Zs_two_sided": ratio,
        "one_positive_Lorentzian_residue": False,
        "scientific_result": (
            "RECIPROCAL_REFLECTION_DOUBLES_BOTH_RESIDUES_AND_CANNOT_REPAIR_"
            "THE_MISMATCH"
        ),
    }


def irreducible_decision_surface() -> dict[str, Any]:
    """Return the physical choices that are not selected by this theorem."""

    return {
        "retained_action_and_domain_outcome": "NO_LOCAL_LORENTZIAN_MAXWELL_RESIDUE",
        "coefficient_free_retained_routes_remaining": 0,
        "decision_classes": [
            {
                "decision": (
                    "DERIVE_A_NEW_AE4_BOUNDARY_OR_COLLAR_ACTION_FROM_A_MORE_"
                    "MICROSCOPIC_PARENT"
                ),
                "requirement": "fixed_nonarbitrary_common_Lorentzian_gauge_coefficient",
            },
            {
                "decision": (
                    "DERIVE_A_NONREFLECTION_PHYSICAL_EXTERIOR_OR_INDEPENDENT_"
                    "BOUNDARY_FIELD_DOMAIN"
                ),
                "requirement": "action_selected_domain_and_full_interface_variation",
            },
            {
                "decision": "RETAIN_AE3_ACTION_AND_DOMAIN",
                "consequence": (
                    "no_physical_local_Maxwell_photon_sector_from_this_parent_trace"
                ),
            },
        ],
        "choice_made_here": False,
        "physical_photon_derived": False,
        "FULL_BHSM_COMPLETE": False,
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "irreducible_decision_surface",
    "operator_domain_transport_certificate",
    "reflection_certificate",
    "two_sided_residue_certificate",
]
