"""Quark Yukawa normalization non-identifiability in the current AE3.1 action.

The frozen up/down response operators and their allowed gauge contractions are
already present.  The current action does not contain the sector source
variations that would fix their two scalar normalizations.  This module makes
that missing ownership exact without fitting quark masses or repurposing the
historical family-bridge coefficients.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from bhsm.interface.ae31_c2_intrinsic_m4_lepton_action import ACTION_VERSION
from bhsm.interface.ae3_c2_hopf_semigroup_transport import (
    frozen_internal_semigroup_attachment,
)


CLASSIFICATION = "AE31_CURRENT_C2_QUARK_YUKAWA_NORMALIZATION_NONIDENTIFIABILITY"


def candidate_quark_yukawa_pair(
    *, up_normalization: float, down_normalization: float
) -> dict[str, Any]:
    """Evaluate the two-parameter operator family without promoting a member."""

    c_up = float(up_normalization)
    c_down = float(down_normalization)
    if not np.isfinite(c_up) or not np.isfinite(c_down):
        raise ValueError("finite quark normalizations required")
    if c_up <= 0.0 or c_down <= 0.0:
        raise ValueError("positive quark normalizations required")
    attachment = frozen_internal_semigroup_attachment()
    up_shape = np.asarray(
        attachment["sectors"]["up"]["family_operator"], dtype=float
    )
    down_shape = np.asarray(
        attachment["sectors"]["down"]["family_operator"], dtype=float
    )
    up = c_up * up_shape
    down = c_down * down_shape
    up_values = np.diag(up)
    down_values = np.diag(down)
    return {
        "action_version": ACTION_VERSION,
        "candidate_only": True,
        "formula_up": "Y_u(c_u)=c_u*T_u",
        "formula_down": "Y_d(c_d)=c_d*T_d",
        "up_normalization": c_up,
        "down_normalization": c_down,
        "up_operator": up.tolist(),
        "down_operator": down.tolist(),
        "up_eigenvalues_heavy_middle_light": up_values.tolist(),
        "down_eigenvalues_heavy_middle_light": down_values.tolist(),
        "up_ratios_to_heavy": (up_values / up_values[0]).tolist(),
        "down_ratios_to_heavy": (down_values / down_values[0]).tolist(),
        "heavy_up_over_down": float(up_values[0] / down_values[0]),
        "normalizations_action_selected": False,
        "measured_quark_mass_used": False,
    }


def normalization_nonidentifiability_theorem() -> dict[str, Any]:
    """State the exact kernel of normalized response observables."""

    return {
        "action_version": ACTION_VERSION,
        "candidate_operator_family": (
            "Y_u(c_u)=c_u*J_u^dagger*T_u*R_u;_"
            "Y_d(c_d)=c_d*J_d^dagger*T_d*R_d"
        ),
        "parameter_domain": "(c_u,c_d)_in_positive_real_numbers_squared",
        "within_sector_observables": (
            "rho_u,i=y_u,i/y_u,heavy;_rho_d,i=y_d,i/y_d,heavy"
        ),
        "normalized_shape_Jacobian_with_respect_to_log_c_u_log_c_d": [
            [0.0, 0.0],
            [0.0, 0.0],
            [0.0, 0.0],
            [0.0, 0.0],
        ],
        "normalized_shape_Jacobian_rank": 0,
        "normalization_nullity": 2,
        "all_current_within_sector_response_data_select_c_u_or_c_d": False,
        "heavy_cross_sector_ratio": "y_u,heavy/y_d,heavy=c_u/c_d",
        "relative_normalization_fixed_by_current_response_shapes": False,
        "absolute_normalizations_fixed_by_current_response_shapes": False,
        "exact_missing_variations": {
            "up": (
                "c_u proportional_to P_u[delta^3 S_parent/(delta bar(Q_L) "
                "delta H_tilde delta u_R)]P_u_with_trace_and_domain_fixed"
            ),
            "down": (
                "c_d proportional_to P_d[delta^3 S_parent/(delta bar(Q_L) "
                "delta H delta d_R)]P_d_with_trace_and_domain_fixed"
            ),
        },
        "one_common_lepton_prefactor_can_be_copied_by_gauge_analogy": False,
        "measured_quark_mass_can_select_the_normalizations": False,
    }


def normalization_kernel_witness() -> dict[str, Any]:
    """Exhibit distinct candidate pairs with identical normalized shapes."""

    first = candidate_quark_yukawa_pair(
        up_normalization=1.0, down_normalization=1.0
    )
    second = candidate_quark_yukawa_pair(
        up_normalization=7.0, down_normalization=0.125
    )
    return {
        "first_normalizations": [1.0, 1.0],
        "second_normalizations": [7.0, 0.125],
        "up_shape_residual": float(
            np.max(
                np.abs(
                    np.asarray(first["up_ratios_to_heavy"])
                    - np.asarray(second["up_ratios_to_heavy"])
                )
            )
        ),
        "down_shape_residual": float(
            np.max(
                np.abs(
                    np.asarray(first["down_ratios_to_heavy"])
                    - np.asarray(second["down_ratios_to_heavy"])
                )
            )
        ),
        "first_heavy_up_over_down": first["heavy_up_over_down"],
        "second_heavy_up_over_down": second["heavy_up_over_down"],
        "cross_sector_ratio_changes": (
            first["heavy_up_over_down"] != second["heavy_up_over_down"]
        ),
        "continuum_of_indistinguishable_normalizations": True,
    }


def provenance_and_exclusion_ledger() -> dict[str, Any]:
    """Separate the missing source variation from nearby historical objects."""

    return {
        "charged_lepton_normalization_owner": (
            "sqrt(2)*kappa_H*tau^2*(beta_l*tau/Tr(P_l))"
        ),
        "charged_lepton_owner_may_be_reused_as_quark_number": False,
        "up_down_gauge_invariant_operator_classes_available": True,
        "up_down_frozen_family_response_operators_available": True,
        "up_down_intrinsic_M4_source_variations_available": False,
        "historical_beta_kappa_objects": (
            "CONDITIONAL_FAMILY_BRIDGE_AND_BOUNDARY_SOURCE_CANDIDATES"
        ),
        "historical_beta_kappa_functional_variation": (
            "FAMILY_SLOT_BRIDGE_OR_BOUNDARY_MATRIX_VARIATION"
        ),
        "required_c_u_c_d_functional_variation": (
            "INTRINSIC_M4_LR_HIGGS_THIRD_VARIATION"
        ),
        "beta_kappa_can_be_relabelled_as_c_u_c_d": False,
        "middle_up_virtual_dressing_promoted": False,
        "EC_auxiliary_unit_vertex_supplies_global_quark_normalization": False,
        "why_EC_excluded": (
            "RETAINED_ZERO_MODE_NOT_IN_GLOBAL_EC_STATIONARY_ACTION_DOMAIN"
        ),
        "independent_quark_normalization_inserted": False,
        "quark_mass_fit_used": False,
    }


def claim_boundary() -> dict[str, Any]:
    return {
        "CURRENT_AE31_QUARK_YUKAWA_NORMALIZATION_NONIDENTIFIABILITY_DERIVED": True,
        "CURRENT_AE31_QUARK_NORMALIZATION_NULLITY": 2,
        "CURRENT_C2_QUARK_RESPONSE_SHAPES_REUSED": True,
        "HISTORICAL_BETA_KAPPA_RELABELLED_AS_QUARK_YUKAWA": False,
        "CURRENT_C2_UP_DOWN_YUKAWA_OPERATORS_ACTION_OWNED": False,
        "CURRENT_C2_UP_DOWN_ABSOLUTE_YUKAWA_PREFACTORS_DERIVED": False,
        "CURRENT_C2_PHYSICAL_QUARK_MASS_RATIOS_DERIVED": False,
        "CURRENT_C2_PHYSICAL_QUARK_POLES_DERIVED": False,
        "CKM_MATRIX_DERIVED": False,
        "MEASURED_QUARK_MASS_USED": False,
        "particle_spectrum_rebuilt": False,
        "exact_next_operator": (
            "COMPLETE_PARENT_INTRINSIC_M4_MIXED_THIRD_VARIATIONS_"
            "P_U_DELTA3S_BARQL_HTILDE_UR_P_U_AND_"
            "P_D_DELTA3S_BARQL_H_DR_P_D_WITH_THEIR_TRACE_NORMALIZATIONS"
        ),
        "FULL_BHSM_COMPLETE": False,
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "candidate_quark_yukawa_pair",
    "claim_boundary",
    "normalization_kernel_witness",
    "normalization_nonidentifiability_theorem",
    "provenance_and_exclusion_ledger",
]
