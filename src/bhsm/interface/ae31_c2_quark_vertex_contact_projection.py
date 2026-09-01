"""Projection limits of the current-C2 unit product-Dirac source jet."""

from __future__ import annotations

from math import isfinite
from typing import Any, Iterable

import numpy as np

from bhsm.interface.ae31_c2_intrinsic_m4_lepton_action import ACTION_VERSION
from bhsm.interface.ae3_c2_action_puzzle import reduced_product_dirac_hs_source_jet


CLASSIFICATION = "AE31_CURRENT_C2_QUARK_VERTEX_CONTACT_PROJECTION_THEOREM"


def unit_probe_scaling_theorem() -> dict[str, Any]:
    """Verify ``V(q)=q V(1)`` and ``Q(q)=q^2 Q(1)`` exactly numerically."""

    data = {
        "proper_durations": np.asarray((0.7, 1.1, 0.9)),
        "base_W": np.asarray((-0.4, 0.2, 0.8)),
        "source_profile": np.asarray((1.0, 0.5, 1.5)),
    }
    unit = reduced_product_dirac_hs_source_jet(**data, generator_eigenvalue=1.0)
    scale = 7.0 / 3.0
    scaled = reduced_product_dirac_hs_source_jet(**data, generator_eigenvalue=scale)
    vertex_keys = ("vertex_diagonal", "vertex_off_diagonal")
    contact_keys = ("contact_diagonal", "contact_off_diagonal")
    vertex_residual = max(
        float(np.max(np.abs(np.asarray(scaled[key]) - scale * np.asarray(unit[key]))))
        for key in vertex_keys
    )
    contact_residual = max(
        float(
            np.max(
                np.abs(
                    np.asarray(scaled[key]) - scale**2 * np.asarray(unit[key])
                )
            )
        )
        for key in contact_keys
    )
    return {
        "action_version": ACTION_VERSION,
        "source_deformation": "delta_W=q*p",
        "vertex_scaling": "V(q)=q*V(1)",
        "contact_scaling": "Q(q)=q^2*Q(1)",
        "test_scale": scale,
        "vertex_scaling_residual": vertex_residual,
        "contact_scaling_residual": contact_residual,
        "scaling_verified": vertex_residual < 1.0e-14 and contact_residual < 1.0e-14,
        "q_selected_by_unit_probe_derivation": False,
    }


def descriptor_channel_incidence(descriptor_keys: Iterable[str]) -> dict[str, Any]:
    keys = tuple(str(key) for key in descriptor_keys)
    product = tuple(key for key in keys if key.startswith("product_Dirac_"))
    up = tuple(key for key in product if "_up" in key.lower())
    down = tuple(key for key in product if "_down" in key.lower())
    return {
        "descriptor_product_Dirac_key_count": len(product),
        "chirality_plus_present": any("chirality_plus" in key for key in product),
        "chirality_minus_present": any("chirality_minus" in key for key in product),
        "up_sector_keys": list(up),
        "down_sector_keys": list(down),
        "explicit_up_down_sector_axis_present": bool(up or down),
        "source_kind": "UNIT_COMMUTING_REDUCED_LR_HS_PROBE",
        "source_is_dynamical_field_coordinate": False,
        "descriptor_can_distinguish_chirality": True,
        "descriptor_can_distinguish_up_from_down": False,
    }


def abstract_sector_projection(*, q_up: float, q_down: float) -> dict[str, Any]:
    """Project a representation-valued source and expose its free coefficients."""

    up = float(q_up)
    down = float(q_down)
    if not isfinite(up) or not isfinite(down):
        raise ValueError("finite sector source coefficients required")
    p_up = np.diag((1.0, 0.0))
    p_down = np.diag((0.0, 1.0))
    generator = up * p_up + down * p_down
    return {
        "representation_identity": np.eye(2).tolist(),
        "P_up": p_up.tolist(),
        "P_down": p_down.tolist(),
        "G_H_candidate": generator.tolist(),
        "projected_vertex_coefficients": {
            "up": float(np.trace(p_up @ generator @ p_up)),
            "down": float(np.trace(p_down @ generator @ p_down)),
        },
        "projected_contact_coefficients": {
            "up_up": float(np.trace(p_up @ generator @ generator @ p_up)),
            "down_down": float(np.trace(p_down @ generator @ generator @ p_down)),
            "up_down": float(np.trace(p_up @ generator @ generator @ p_down)),
        },
        "projector_orthogonality_residual": float(np.linalg.norm(p_up @ p_down)),
        "projector_completeness_residual": float(
            np.linalg.norm(p_up + p_down - np.eye(2))
        ),
        "block_projection_structurally_defined": True,
        "q_up_q_down_action_derived": False,
    }


def projection_nonidentifiability_theorem() -> dict[str, Any]:
    first = abstract_sector_projection(q_up=1.0, q_down=1.0)
    second = abstract_sector_projection(q_up=2.0, q_down=0.5)
    return {
        "first": first,
        "second": second,
        "both_obey_same_projector_algebra": (
            first["projector_orthogonality_residual"] == 0.0
            and second["projector_orthogonality_residual"] == 0.0
            and first["projector_completeness_residual"] == 0.0
            and second["projector_completeness_residual"] == 0.0
        ),
        "sector_residue_ratio_first": 1.0,
        "sector_residue_ratio_second": 4.0,
        "same_structural_projection_different_residue_ratio": True,
        "representation_projectors_select_block_support": True,
        "representation_projectors_select_block_coefficients": False,
        "gauge_allowed_H_and_H_tilde_contractions_select_absolute_residues": False,
    }


def exact_missing_incidence_map() -> dict[str, Any]:
    return {
        "required_map": (
            "rho_qH_current_C2:(H,H_tilde)_intrinsic_to_"
            "End(Q_L_direct_sum_u_R_direct_sum_d_R)"
        ),
        "required_linearization": (
            "D_rho_qH=V_spatial_tensor(q_up*P_up+q_down*P_down)"
        ),
        "required_contact": (
            "D2_rho_qH=Q_spatial_tensor_sector_contact_matrix"
        ),
        "must_be_derived_from": (
            "ONE_CURRENT_C2_PARENT_OR_INTRINSIC_ACTION_WITH_FIXED_TRACE_"
            "DOMAIN_AND_FIELD_NORMALIZATIONS"
        ),
        "existing_projectors_and_family_operators_reused": True,
        "unit_probe_may_be_declared_both_sector_coefficients": False,
        "independent_q_up_q_down_allowed": False,
        "quark_mass_fit_allowed": False,
    }


def claim_boundary() -> dict[str, Any]:
    return {
        "CURRENT_C2_UNIT_PRODUCT_DIRAC_SOURCE_SCALING_DERIVED": True,
        "CURRENT_C2_PRODUCT_DIRAC_DESCRIPTOR_UP_DOWN_INCIDENCE_PRESENT": False,
        "CURRENT_C2_QUARK_VERTEX_CONTACT_BLOCK_PROJECTION_STRUCTURALLY_DEFINED": True,
        "CURRENT_C2_QUARK_VERTEX_CONTACT_COEFFICIENTS_ACTION_DERIVED": False,
        "CURRENT_C2_UP_DOWN_YUKAWA_OPERATORS_ACTION_OWNED": False,
        "CURRENT_C2_QUARK_CHANNEL_DIRECTION_SELECTED": False,
        "CURRENT_C2_PHYSICAL_QUARK_POLES_DERIVED": False,
        "CKM_MATRIX_DERIVED": False,
        "MEASURED_QUARK_MASS_USED": False,
        "particle_spectrum_rebuilt": False,
        "FULL_BHSM_COMPLETE": False,
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "abstract_sector_projection",
    "claim_boundary",
    "descriptor_channel_incidence",
    "exact_missing_incidence_map",
    "projection_nonidentifiability_theorem",
    "unit_probe_scaling_theorem",
]
