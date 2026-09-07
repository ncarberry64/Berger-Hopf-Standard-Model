"""Stability of the current-C2 Maxwell mismatch under common F-squared shifts."""

from __future__ import annotations

from math import isfinite
from typing import Any

from bhsm.interface.ae3_c2_lorentzian_gauge_ghost_hessian import (
    ACTION_VERSION,
    lowest_transverse_residue_witness,
)


CLASSIFICATION = "CURRENT_C2_MAXWELL_COMMON_COVARIANT_SHIFT_NO_GO"


def common_covariant_shift_witness(delta_z: float) -> dict[str, Any]:
    """Apply one finite local ``F^2`` residue to both gauge coefficients."""

    shift = float(delta_z)
    if not isfinite(shift):
        raise ValueError("finite common residue shift required")
    witness = lowest_transverse_residue_witness()
    z_spatial = 1.0
    z_temporal = float(witness["temporal_to_complete_spatial_mode_residue_ratio"])
    shifted_temporal = z_temporal + shift
    shifted_spatial = z_spatial + shift
    difference_before = z_spatial - z_temporal
    difference_after = shifted_spatial - shifted_temporal
    invariance_residual = abs(difference_after - difference_before)
    positive_shifted_form = shifted_temporal > 0.0 and shifted_spatial > 0.0
    return {
        "normalization": "Z_s_parent=1",
        "Z_t_parent": z_temporal,
        "Z_s_parent": z_spatial,
        "common_delta_Z_F_squared": shift,
        "Z_t_shifted": shifted_temporal,
        "Z_s_shifted": shifted_spatial,
        "difference_before": difference_before,
        "difference_after": difference_after,
        "difference_invariance_residual": invariance_residual,
        "relative_difference_invariance_residual": invariance_residual
        / max(1.0, abs(shift)),
        "shifted_form_positive": positive_shifted_form,
        "one_Maxwell_residue_after_finite_common_shift": (
            shifted_temporal == shifted_spatial
        ),
        "ratio_after_shift": (
            shifted_temporal / shifted_spatial if shifted_spatial != 0.0 else None
        ),
        "finite_common_shift_can_approach_but_not_reach_ratio_one": True,
    }


def exact_common_shift_no_go() -> dict[str, Any]:
    """State the algebraic theorem independently of any shift value."""

    witness = lowest_transverse_residue_witness()
    ratio = float(witness["temporal_to_complete_spatial_mode_residue_ratio"])
    mismatch = 1.0 - ratio
    return {
        "parent_normalized_residues": {"Z_t": ratio, "Z_s": 1.0},
        "parent_difference_Zs_minus_Zt": mismatch,
        "common_shift_equation": "Z_t+delta_Z=Z_s+delta_Z_iff_Z_t=Z_s",
        "parent_equality_holds": ratio == 1.0,
        "finite_local_covariant_F_squared_shift_repairs_mismatch": False,
        "renormalization_scale_choice_repairs_mismatch": False,
        "infinite_common_shift_promoted_as_finite_physical_residue": False,
        "theorem_scope": (
            "CORRECTIONS_PROPORTIONAL_TO_THE_SAME_LOCAL_F_MUNU_F_MUNU_"
            "OPERATOR_IN_THE_ACTION_SELECTED_LORENTZIAN_METRIC"
        ),
        "all_quantum_or_boundary_corrections_excluded": False,
    }


def required_noncommon_correction() -> dict[str, Any]:
    """Derive the exact anisotropic correction equation still required."""

    witness = lowest_transverse_residue_witness()
    ratio = float(witness["temporal_to_complete_spatial_mode_residue_ratio"])
    required = 1.0 - ratio
    return {
        "normalization": "Z_s_parent=1",
        "required_equation": "delta_Z_t-delta_Z_s=Z_s_parent-Z_t_parent",
        "required_delta_Zt_minus_delta_Zs": required,
        "candidate_operator_classes_not_excluded": [
            "action_derived_boundary_or_Wentzell_term",
            "action_derived_collar_or_extrinsic_curvature_term",
            "action_selected_nonreflection_exterior_DtN_domain",
            "curvature_dependent_quantum_form_factor_on_current_C2",
        ],
        "one_candidate_selected_by_current_action": False,
        "coefficient_fitted_to_required_difference": False,
        "independent_ZA_g_gprime_alpha_or_metric_cone_inserted": False,
    }


def muon_chain_boundary() -> dict[str, Any]:
    return {
        "structural_neutral_charge_direction_already_available": True,
        "normalized_photon_propagator_available": False,
        "common_matter_wavefunction_renormalization_can_unlock_photon": False,
        "next_gauge_owner": (
            "ACTION_DERIVED_NONCOMMON_BOUNDARY_CURVATURE_OR_DOMAIN_"
            "CONTRIBUTION_SATISFYING_delta_Zt-delta_Zs=Zs-Zt"
        ),
        "electroweak_neutral_pole_ready": False,
        "muon_vertex_F2_zero_ready": False,
    }


def claim_boundary() -> dict[str, Any]:
    return {
        "CURRENT_C2_COMMON_COVARIANT_F2_SHIFT_NO_GO_DERIVED": True,
        "CURRENT_C2_REQUIRED_NONCOMMON_GAUGE_RESIDUE_DIFFERENCE_DERIVED": True,
        "CURRENT_C2_ALL_QUANTUM_GAUGE_REPAIRS_EXCLUDED": False,
        "CURRENT_C2_LORENTZIAN_MAXWELL_RESIDUE_DERIVED": False,
        "CURRENT_C2_NORMALIZED_PHOTON_PROPAGATOR_DERIVED": False,
        "MUON_MAGNETIC_MOMENT_DERIVED": False,
        "fitted_residue_used": False,
        "metric_cone_adjusted": False,
        "FULL_BHSM_COMPLETE": False,
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "claim_boundary",
    "common_covariant_shift_witness",
    "exact_common_shift_no_go",
    "muon_chain_boundary",
    "required_noncommon_correction",
]
