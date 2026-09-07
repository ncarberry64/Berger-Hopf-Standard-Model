"""AE3.1 broken neutral connection-coordinate Hessian on current C2."""

from __future__ import annotations

from math import sqrt
from typing import Any

import numpy as np

from bhsm.interface.ae31_c2_intrinsic_m4_lepton_action import (
    conditional_higgs_saddle,
)


ACTION_VERSION = "BHSM-AE-3.1.0"
CLASSIFICATION = "CURRENT_C2_BROKEN_NEUTRAL_CONNECTION_COORDINATE_HESSIAN"


def higgs_neutral_charge_ledger() -> dict[str, Any]:
    """Return the exact charges of the selected neutral Higgs component."""

    return {
        "H_representation": "(1,2,+1/2)",
        "vacuum_component": "H_0=(0,v_BH/sqrt(2))",
        "T3_on_vacuum": -0.5,
        "Y_BH_on_vacuum": 0.5,
        "Q_em_on_vacuum": 0.0,
        "Q_em": "T3+Y_BH",
        "connection_coordinates": {
            "W3_hat": "g2*W3_physical_before_canonical_normalization",
            "B_hat": "g1*B_physical_before_canonical_normalization",
        },
        "independent_g2_or_g1_inserted": False,
    }


def neutral_connection_hessian(v_bh: float | None = None) -> dict[str, Any]:
    """Derive the rank-one Higgs Hessian in ``(W3_hat,B_hat)`` coordinates."""

    saddle = conditional_higgs_saddle()
    value = float(saddle["v_BH_GeV"] if v_bh is None else v_bh)
    if not np.isfinite(value) or value <= 0.0:
        raise ValueError("positive finite Higgs saddle required")
    shape = np.asarray(((1.0, -1.0), (-1.0, 1.0)))
    matrix = value**2 * shape / 4.0
    null = np.asarray((1.0, 1.0)) / sqrt(2.0)
    broken = np.asarray((1.0, -1.0)) / sqrt(2.0)
    eigenvalues = np.linalg.eigvalsh(matrix)
    return {
        "action_version": ACTION_VERSION,
        "basis": ["W3_hat", "B_hat"],
        "formula": "H_neutral=(v_BH^2/4)*[[1,-1],[-1,1]]",
        "matrix_GeV2": matrix.tolist(),
        "eigenvalues_GeV2": eigenvalues.tolist(),
        "rank": int(np.linalg.matrix_rank(matrix, tol=1.0e-10)),
        "nullity": int(2 - np.linalg.matrix_rank(matrix, tol=1.0e-10)),
        "Q_em_null_vector": null.tolist(),
        "Q_em_null_residual_exact": 0.0,
        "Q_em_null_residual_floating": float(np.linalg.norm(matrix @ null)),
        "broken_vector": broken.tolist(),
        "broken_curvature_GeV2": float(broken @ matrix @ broken),
        "broken_curvature_positive": bool(broken @ matrix @ broken > 0.0),
        "unique_neutral_null_direction": bool(
            np.linalg.matrix_rank(matrix, tol=1.0e-10) == 1
        ),
        "v_BH_GeV": value,
        "measured_Higgs_VEV_used": False,
        "absolute_scale_action_derived": False,
        "connection_coordinate_result": True,
        "canonically_normalized_physical_field_result": False,
    }


def neutral_field_current_rotation() -> dict[str, Any]:
    """Rotate fields and currents in the unnormalized connection coordinates."""

    transform = np.asarray(((1.0, 1.0), (1.0, -1.0))) / sqrt(2.0)
    return {
        "input_field_basis": ["W3_hat", "B_hat"],
        "output_field_basis": ["A_Q", "Z_H"],
        "field_rotation": (
            "A_Q=(W3_hat+B_hat)/sqrt(2);_Z_H=(W3_hat-B_hat)/sqrt(2)"
        ),
        "input_current_basis": ["J3", "JY"],
        "output_current_basis": ["J_Q", "J_H"],
        "current_rotation": (
            "J_Q=(J3+JY)/sqrt(2);_J_H=(J3-JY)/sqrt(2)"
        ),
        "interaction_identity": (
            "W3_hat*J3+B_hat*JY=A_Q*J_Q+Z_H*J_H"
        ),
        "Q_em_current": "J_Q proportional_to J3+JY",
        "broken_neutral_current": "J_H proportional_to J3-JY",
        "orthogonal_coordinate_transform": bool(
            np.allclose(transform @ transform.T, np.eye(2), atol=1.0e-15, rtol=0.0)
        ),
        "same_current_C2_source_domain": True,
        "canonical_kinetic_rotation_claimed": False,
        "Weinberg_angle_derived": False,
    }


def lorentzian_photon_promotion_gate() -> dict[str, Any]:
    """Keep the structural null connection distinct from a physical photon."""

    return {
        "neutral_Higgs_curvature_null_direction_derived": True,
        "coexact_JY_J3_source_pair_attached": True,
        "single_Lorentzian_Maxwell_residue_available": False,
        "reason": (
            "THE_CURRENT_AE3_GAUGE_GHOST_HESSIAN_HAS_AN_UNRENORMALIZED_"
            "TEMPORAL_SPATIAL_RESIDUE_MISMATCH"
        ),
        "physical_transverse_A_Q_pole_derived": False,
        "Ward_identity_for_canonical_A_Q_derived": False,
        "physical_photon_promoted": False,
        "independent_ZA_g_gprime_alpha_or_mixing_angle_inserted": False,
    }


def claim_boundary() -> dict[str, Any]:
    return {
        "CURRENT_C2_NEUTRAL_CONNECTION_HESSIAN_DERIVED": True,
        "CURRENT_C2_UNIQUE_QEM_CONNECTION_NULL_DIRECTION_DERIVED": True,
        "CURRENT_C2_STRUCTURAL_JQ_CURRENT_DERIVED": True,
        "CURRENT_C2_FIELDS_AND_CURRENTS_ROTATED_IN_CONNECTION_COORDINATES": True,
        "CURRENT_C2_CANONICAL_WEINBERG_ROTATION_DERIVED": False,
        "CURRENT_C2_PHYSICAL_PHOTON_DERIVED": False,
        "CURRENT_C2_PHOTON_POLE_AND_WARD_IDENTITY_DERIVED": False,
        "MUON_MAGNETIC_MOMENT_DERIVED": False,
        "independent_gauge_or_mixing_parameter_inserted": False,
        "exact_next_operator": (
            "ACTION_OWNED_LORENTZIAN_GAUGE_DOMAIN_WITH_ONE_COMMON_TEMPORAL_"
            "SPATIAL_RESIDUE_FOR_THE_QEM_NULL_CONNECTION_THEN_ITS_WARD_IDENTITY"
        ),
        "FULL_BHSM_COMPLETE": False,
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "claim_boundary",
    "higgs_neutral_charge_ledger",
    "lorentzian_photon_promotion_gate",
    "neutral_connection_hessian",
    "neutral_field_current_rotation",
]
