"""Transport the coefficient-free gauge-exchange LR channel ray to current C2."""

from __future__ import annotations

from fractions import Fraction
from typing import Any

import numpy as np

from bhsm.interface.ae31_c2_intrinsic_m4_lepton_action import ACTION_VERSION


CLASSIFICATION = "AE31_CURRENT_C2_QUARK_GAUGE_LR_CHANNEL_RAY"


def exact_group_factor_ray() -> dict[str, Any]:
    """Derive the LR attraction weights from the single-carrier trace ray."""

    color = Fraction(4, 3)
    hypercharge_inverse_ray = Fraction(3, 5)
    products = {
        "up": Fraction(1, 6) * Fraction(2, 3),
        "down": Fraction(1, 6) * Fraction(-1, 3),
    }
    weights = {
        sector: color + hypercharge_inverse_ray * product
        for sector, product in products.items()
    }
    return {
        "single_carrier_inverse_kernel_ray": "G_Y:G_2:G_3=3/5:1:1",
        "color_singlet_C_F": str(color),
        "hypercharge_products": {key: str(value) for key, value in products.items()},
        "pre_Fierz_weights": {key: str(value) for key, value in weights.items()},
        "post_Fierz_weights": {key: str(2 * value) for key, value in weights.items()},
        "C_up_minus_C_down": str(weights["up"] - weights["down"]),
        "C_up_over_C_down": str(weights["up"] / weights["down"]),
        "ordering": "C_up>C_down>0",
        "measured_quark_mass_used": False,
    }


def current_c2_transport_contract() -> dict[str, Any]:
    return {
        "transported_data": [
            "rank16_single_carrier_trace_normalization_ray",
            "current_quark_hypercharges",
            "color_singlet_C_F",
            "transported_I_up_I_down_supports",
        ],
        "common_current_C2_geometry_factor": "G_C2_STATIC_NONLOCAL_DtN",
        "kernel_ray": "K_LR=2*G_C2*diag(7/5,13/10)_on_(up,down)",
        "absolute_G_C2_evaluated_here": False,
        "local_Lorentzian_Maxwell_residue_required_for_relative_ray": False,
        "reason": "THE_COMMON_GEOMETRIC_FACTOR_CANCELS_FROM_THE_CHANNEL_RATIO",
        "Lorentzian_Maxwell_mismatch_overridden": False,
        "nonlocal_static_kernel_relabelled_as_local_photon_exchange": False,
        "current_C2_radial_domain_or_birth_trace_changed": False,
    }


def channel_direction_effect() -> dict[str, Any]:
    """Show what the unequal diagonal ray does and does not select."""

    c_up = 7.0 / 5.0
    c_down = 13.0 / 10.0
    hessian = np.diag((2.0 * c_up, 2.0 * c_down))
    eigenvalues, eigenvectors = np.linalg.eigh(hessian)
    return {
        "normalized_common_factor_Hessian": hessian.tolist(),
        "eigenvalues_ascending": eigenvalues.tolist(),
        "eigenvectors_columns": eigenvectors.tolist(),
        "eigenvalue_splitting": float(eigenvalues[1] - eigenvalues[0]),
        "isolated_O2_quark_plane_degeneracy_broken": True,
        "largest_attraction_axis": "up",
        "mixed_up_down_eigendirection_selected": False,
        "reason_no_mixed_direction": "THE_TRANSPORTED_GAUGE_RAY_IS_DIAGONAL_IN_UP_DOWN_CHANNEL_SPACE",
        "c_up_over_c_down_Yukawa_residue_derived": False,
    }


def family_and_higgs_boundary() -> dict[str, Any]:
    return {
        "family_action": "diag(C_up*I3,C_down*I3)",
        "family_hierarchy_generated": False,
        "CKM_generated": False,
        "single_intrinsic_Higgs_direction_selected": False,
        "required_missing_block": (
            "CURRENT_C2_FULL_LR_SUSCEPTIBILITY_PLUS_INTRINSIC_HIGGS_MIXING_"
            "HESSIAN_WITH_ACTION_DERIVED_OFF_DIAGONAL_CHANNEL_TERMS"
        ),
        "if_off_diagonal_block_is_zero": (
            "FIRST_GAUGE_DRIVEN_INSTABILITY_IS_PURE_UP_NOT_A_SHARED_SM_HIGGS_DIRECTION"
        ),
        "historical_group_weights_relabelled_as_Yukawa_residues": False,
    }


def exact_remaining_owner() -> dict[str, Any]:
    return {
        "derive_together": [
            "current_C2_regulated_LR_fermion_susceptibility",
            "odd_scalar_endomorphism_or_composite_HS_two_point_kernel",
            "intrinsic_Higgs_to_composite_channel_mixing",
            "complete_up_down_off_diagonal_Hessian",
        ],
        "reusable_diagonal_ray": "diag(7/5,13/10)",
        "independent_up_down_gauge_normalizations_allowed": False,
        "group_factor_ratio_may_be_called_Yukawa_ratio": False,
        "quark_mass_fit_allowed": False,
    }


def claim_boundary() -> dict[str, Any]:
    return {
        "CURRENT_C2_QUARK_GAUGE_LR_RELATIVE_CHANNEL_RAY_DERIVED": True,
        "CURRENT_C2_ISOLATED_QUARK_CHANNEL_O2_DEGENERACY_BROKEN_BY_GAUGE_RAY": True,
        "CURRENT_C2_MIXED_SINGLE_HIGGS_DIRECTION_SELECTED": False,
        "CURRENT_C2_UP_DOWN_RELATIVE_YUKAWA_RESIDUE_DERIVED": False,
        "CURRENT_C2_UP_DOWN_ABSOLUTE_YUKAWA_PREFACTORS_DERIVED": False,
        "CURRENT_C2_PHYSICAL_QUARK_POLES_DERIVED": False,
        "CKM_MATRIX_DERIVED": False,
        "MEASURED_QUARK_MASS_USED": False,
        "particle_spectrum_rebuilt": False,
        "FULL_BHSM_COMPLETE": False,
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "channel_direction_effect",
    "claim_boundary",
    "current_c2_transport_contract",
    "exact_group_factor_ray",
    "exact_remaining_owner",
    "family_and_higgs_boundary",
]
