"""Exact current-C2 gauge-kernel Hubbard--Stratonovich action rewrite."""

from __future__ import annotations

from fractions import Fraction
from math import isfinite
from typing import Any

import numpy as np

from bhsm.interface.ae31_c2_intrinsic_m4_lepton_action import ACTION_VERSION
from bhsm.interface.ae31_c2_quark_higgs_incidence_transport import (
    quark_higgs_support_pencil,
)


CLASSIFICATION = "AE31_CURRENT_C2_GAUGE_COMPOSITE_HS_ACTION"


def exact_hs_completion_witness(common_kernel: float = 1.0) -> dict[str, Any]:
    """Verify the two-channel completion of the square at its HS saddle."""

    common = float(common_kernel)
    if not isfinite(common) or common <= 0.0:
        raise ValueError("finite positive common current-C2 kernel required")
    weights = np.asarray((7.0 / 5.0, 13.0 / 10.0))
    kernel = 2.0 * common * np.diag(weights)
    inverse = np.linalg.inv(kernel)
    bilinear = np.asarray((2.0 / 3.0, -3.0 / 5.0))
    saddle = kernel @ bilinear
    four_fermion = float(bilinear @ kernel @ bilinear)
    hs_at_saddle = float(
        -saddle @ inverse @ saddle + 2.0 * saddle @ bilinear
    )
    stationary_residual = float(
        np.linalg.norm(-2.0 * inverse @ saddle + 2.0 * bilinear)
    )
    return {
        "channel_basis": ["up", "down"],
        "common_kernel": common,
        "K_LR": kernel.tolist(),
        "K_LR_inverse": inverse.tolist(),
        "bilinear_witness": bilinear.tolist(),
        "HS_saddle": saddle.tolist(),
        "four_fermion_exponent": four_fermion,
        "HS_exponent_at_saddle": hs_at_saddle,
        "completion_residual": abs(four_fermion - hs_at_saddle),
        "stationary_residual": stationary_residual,
        "Gaussian_normalization_field_independent": True,
    }


def action_owned_gauge_hs_contract() -> dict[str, Any]:
    """State the exact auxiliary rewrite of the derived gauge LR kernel."""

    return {
        "source_action_object": "CURRENT_C2_STATIC_NONLOCAL_GAUGE_CURRENT_KERNEL",
        "source_kernel": "K_LR=2*G_C2*diag(7/5,13/10)",
        "domain": "POSITIVE_COEXACT_CURRENT_C2_DtN_MODES_WITH_G_C2>0",
        "bilinear_column": "O=(bar(Q_L)*u_R,bar(Q_L)*d_R)^T",
        "four_fermion_factor": "exp[+O^dagger*K_LR*O]",
        "auxiliary_identity": (
            "exp[+O^dagger*K_LR*O]_proportional_to_integral_DH_"
            "exp[-H^dagger*K_LR^(-1)*H+H^dagger*O+O^dagger*H]"
        ),
        "bare_auxiliary_Hessian": (
            "K_LR^(-1)=G_C2^(-1)*diag(5/14,5/13)"
        ),
        "bare_LR_vertices": {"up": 1.0, "down": 1.0},
        "unit_vertex_is_coefficient_placement_not_fitted_Yukawa": True,
        "new_continuous_coefficient": False,
        "new_elementary_scalar": False,
        "gauge_kernel_changed": False,
        "local_Maxwell_residue_required": False,
        "static_nonlocal_kernel_relabelled_local": False,
    }


def odd_composite_endomorphism_attachment() -> dict[str, Any]:
    """Attach the exact HS vertices to the transported odd incidences."""

    support = quark_higgs_support_pencil()
    up = np.asarray(support["I_up"], dtype=float)
    down = np.asarray(support["I_down"], dtype=float)
    chirality = np.diag((-1.0, -1.0, 1.0, 1.0))
    residuals = {
        "up": float(np.linalg.norm(chirality @ up + up @ chirality)),
        "down": float(np.linalg.norm(chirality @ down + down @ chirality)),
    }
    return {
        "composite_odd_endomorphism": "E_HS=H_u*I_up+H_d*I_down",
        "grading": "{Gamma_chi,E_HS}=0",
        "grading_residuals": residuals,
        "supports_disjoint": float(np.trace(up.T @ down)) == 0.0,
        "support_ranks": {
            "up": int(np.linalg.matrix_rank(up)),
            "down": int(np.linalg.matrix_rank(down)),
        },
        "composite_HS_odd_endomorphism_action_owned_by_rewrite": all(
            value == 0.0 for value in residuals.values()
        ),
        "intrinsic_Higgs_odd_endomorphism_action_owned": False,
        "existing_representation_projectors_reused": True,
        "particle_spectrum_rebuilt": False,
    }


def current_c2_domain_and_trace_transport() -> dict[str, Any]:
    return {
        "radial_operator": "D_C2_tensor_I_internal",
        "auxiliary_incidence": "I_radial_tensor_(I_up_direct_sum_I_down)",
        "radial_incidence_commutator": 0.0,
        "reset_generated_C2_domain_preserved": True,
        "retained_birth_trace_preserved": True,
        "family_action": "I3",
        "historical_up_down_pairing_multiplicities": [9, 9],
        "family_hierarchy_generated": False,
        "CKM_generated": False,
        "endpoint_cutoff_inserted": False,
        "Einstein_Cartan_global_kernel_used": False,
        "why_EC_not_used": (
            "THE_GAUGE_KERNEL_IS_REGULAR_ON_ITS_COEXACT_CURRENT_C2_DOMAIN_"
            "AND_DOES_NOT_IMPORT_THE_FAILED_GLOBAL_EC_ZERO_MODE_ELIMINATION"
        ),
    }


def intrinsic_higgs_mixing_boundary() -> dict[str, Any]:
    return {
        "auxiliary_composite_fields": ["H_HS_up", "H_HS_down"],
        "auxiliary_derivative_kinetic_term_at_bare_level": False,
        "fermion_determinant_two_point_block_required": True,
        "intrinsic_AE31_Higgs_field": "H_intrinsic_charged_lepton_block",
        "intrinsic_to_composite_mixing_block": "M_HS",
        "M_HS_action_derived": False,
        "auxiliary_field_is_physical_Higgs": False,
        "unit_bare_vertex_is_canonical_Yukawa_residue": False,
        "physical_single_Higgs_direction_selected": False,
        "exact_next_operator": (
            "H_mix=[[H_intrinsic,M_HS],[M_HS^dagger,"
            "K_LR^(-1)-Pi_Had,sing*I2-Pi_fin[C]]]"
        ),
        "next_variation": (
            "DELTA_Hintrinsic_DELTA_HHS_DELTA_PsiBarL_DELTA_PsiR_"
            "Gamma_current_C2"
        ),
    }


def exact_inverse_coefficients() -> dict[str, str]:
    up = Fraction(1, 2) / Fraction(7, 5)
    down = Fraction(1, 2) / Fraction(13, 10)
    return {
        "up": str(up),
        "down": str(down),
        "up_minus_down": str(up - down),
        "mean": str((up + down) / 2),
        "sigma3": str((up - down) / 2),
    }


def claim_boundary() -> dict[str, Any]:
    return {
        "CURRENT_C2_GAUGE_COMPOSITE_HS_REWRITE_DERIVED": True,
        "CURRENT_C2_GAUGE_COMPOSITE_BARE_HESSIAN_DERIVED": True,
        "CURRENT_C2_GAUGE_COMPOSITE_UNIT_LR_VERTICES_DERIVED": True,
        "CURRENT_C2_COMPOSITE_ODD_ENDOMORPHISM_ACTION_OWNED": True,
        "CURRENT_C2_INTRINSIC_HIGGS_ODD_ENDOMORPHISM_ACTION_OWNED": False,
        "CURRENT_C2_COMPOSITE_DERIVATIVE_KINETIC_TERM_DERIVED": False,
        "CURRENT_C2_INTRINSIC_COMPOSITE_MIXING_DERIVED": False,
        "CURRENT_C2_PHYSICAL_SINGLE_HIGGS_DIRECTION_SELECTED": False,
        "CURRENT_C2_CANONICAL_QUARK_YUKAWA_RESIDUES_DERIVED": False,
        "CURRENT_C2_COMPOSITE_GAP_DERIVED": False,
        "MEASURED_QUARK_MASS_USED": False,
        "particle_spectrum_rebuilt": False,
        "FULL_BHSM_COMPLETE": False,
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "action_owned_gauge_hs_contract",
    "claim_boundary",
    "current_c2_domain_and_trace_transport",
    "exact_hs_completion_witness",
    "exact_inverse_coefficients",
    "intrinsic_higgs_mixing_boundary",
    "odd_composite_endomorphism_attachment",
]
