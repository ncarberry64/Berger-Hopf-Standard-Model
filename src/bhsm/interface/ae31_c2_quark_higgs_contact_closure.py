"""Close the quark--Higgs contact jet in terms of the first vertices."""

from __future__ import annotations

from math import isfinite
from typing import Any, Iterable

import numpy as np

from bhsm.interface.ae31_c2_intrinsic_m4_lepton_action import ACTION_VERSION
from bhsm.interface.ae31_c2_quark_higgs_incidence_transport import (
    quark_higgs_support_pencil,
)


CLASSIFICATION = "AE31_CURRENT_C2_QUARK_HIGGS_CONTACT_CLOSURE"


def affine_first_order_contact_theorem() -> dict[str, Any]:
    """Differentiate the transported renormalizable first-order incidence."""

    return {
        "scalar_source_scope": "REAL_NEUTRAL_UP_AND_DOWN_CHANNEL_COORDINATES",
        "first_order_operator": "D(h_u,h_d)=D_0+h_u*V_u+h_d*V_d",
        "first_variations": {"up": "V_u", "down": "V_d"},
        "second_variations": {
            "Q_uu": "0",
            "Q_ud": "0",
            "Q_du": "0",
            "Q_dd": "0",
        },
        "reason": "RENORMALIZABLE_QUARK_HIGGS_DIRAC_INCIDENCE_IS_AFFINE_LINEAR_IN_THE_SCALAR_FIELDS",
        "first_order_contact_jet_zero": True,
        "higher_dimension_scalar_fermion_contact_inserted": False,
    }


def squared_pencil_contact_closure(
    *,
    up_shape: Iterable[float],
    down_shape: Iterable[float],
    c_up: float = 1.0,
    c_down: float = 1.0,
) -> dict[str, Any]:
    """Evaluate ``d_f d_g(D^dagger D)`` on the transported supports."""

    up_values = np.asarray(tuple(up_shape), dtype=float)
    down_values = np.asarray(tuple(down_shape), dtype=float)
    if up_values.shape != (3,) or down_values.shape != (3,):
        raise ValueError("three-slot up and down family shapes required")
    if not np.all(np.isfinite(up_values)) or not np.all(np.isfinite(down_values)):
        raise ValueError("finite family shapes required")
    if not isfinite(c_up) or not isfinite(c_down):
        raise ValueError("finite sector residues required")

    support = quark_higgs_support_pencil()
    i_up = np.asarray(support["I_up"], dtype=float)
    i_down = np.asarray(support["I_down"], dtype=float)
    v_up = float(c_up) * np.kron(i_up, np.diag(up_values))
    v_down = float(c_down) * np.kron(i_down, np.diag(down_values))
    vertices = {"up": v_up, "down": v_down}
    contacts = {
        f"Q_{left}_{right}": vertices[left].T @ vertices[right]
        + vertices[right].T @ vertices[left]
        for left in ("up", "down")
        for right in ("up", "down")
    }
    q_up_expected = 2.0 * v_up.T @ v_up
    q_down_expected = 2.0 * v_down.T @ v_down
    return {
        "scalar_source_scope": "REAL_NEUTRAL_UP_AND_DOWN_CHANNEL_COORDINATES",
        "family_shape_dimension": 3,
        "lifted_vertex_dimension": int(v_up.shape[0]),
        "squared_operator": "P(h)=D(h)^dagger*D(h)",
        "general_contact_identity": (
            "d_f*d_g*P=V_f^dagger*V_g+V_g^dagger*V_f"
        ),
        "diagonal_contact_identity": "Q_ff=2*V_f^dagger*V_f",
        "Q_up_up_residual": float(
            np.linalg.norm(contacts["Q_up_up"] - q_up_expected)
        ),
        "Q_down_down_residual": float(
            np.linalg.norm(contacts["Q_down_down"] - q_down_expected)
        ),
        "Q_up_down_norm": float(np.linalg.norm(contacts["Q_up_down"])),
        "Q_down_up_norm": float(np.linalg.norm(contacts["Q_down_up"])),
        "mixed_contact_zero_by_disjoint_support": bool(
            np.linalg.norm(contacts["Q_up_down"]) == 0.0
            and np.linalg.norm(contacts["Q_down_up"]) == 0.0
        ),
        "diagonal_contacts_positive_semidefinite": bool(
            np.min(np.linalg.eigvalsh(contacts["Q_up_up"])) >= 0.0
            and np.min(np.linalg.eigvalsh(contacts["Q_down_down"])) >= 0.0
        ),
        "contact_jet_fixed_once_vertices_are_fixed": True,
        "independent_contact_coefficient_count": 0,
        "sector_residues_action_derived": False,
    }


def determinant_hessian_reduction() -> dict[str, Any]:
    """State the first-order and squared-pencil determinant identities."""

    return {
        "first_order_effective_action": "Gamma=-Tr(log(D))",
        "first_order_H_fg": "Tr(G*V_g*G*V_f)",
        "first_order_Q_fg_term": "ABSENT_BECAUSE_d_f*d_g*D=0",
        "squared_pencil_effective_action": "Gamma_even=-(1/2)*Tr(log(D^dagger*D))",
        "squared_pencil_contact": (
            "Q_fg=V_f^dagger*V_g+V_g^dagger*V_f"
        ),
        "squared_pencil_contact_is_independent_input": False,
        "state_covariance_or_Feynman_inverse_still_required": True,
        "up_down_vertex_residues_still_required": True,
    }


def exact_remaining_owner() -> dict[str, Any]:
    return {
        "missing_action_object": (
            "Gamma_qH_current_C2_WITH_ACTION_NORMALIZED_FIRST_VERTICES_V_u_V_d"
        ),
        "independent_missing_vertex_residues": ["c_u", "c_d"],
        "independent_missing_contact_coefficients": [],
        "squared_pencil_contact_reconstruction": (
            "Q_fg=V_f^dagger*V_g+V_g^dagger*V_f"
        ),
        "mixed_contact_on_transported_support": "Q_ud=Q_du=0",
        "must_remain_common": [
            "current_C2_action",
            "trace_and_field_normalization",
            "boundary_domain",
            "family_shapes_T_u_T_d",
        ],
        "independent_yukawa_contact_or_mass_fit_allowed": False,
    }


def claim_boundary() -> dict[str, Any]:
    return {
        "CURRENT_C2_QUARK_FIRST_ORDER_HIGGS_CONTACT_JET_ZERO_DERIVED_CONDITIONAL": True,
        "CURRENT_C2_QUARK_SQUARED_PENCIL_CONTACT_CLOSED_BY_FIRST_VERTICES": True,
        "CURRENT_C2_QUARK_MIXED_UP_DOWN_CONTACT_ZERO_ON_TRANSPORTED_SUPPORT": True,
        "CURRENT_C2_INDEPENDENT_QUARK_CONTACT_COEFFICIENT_REQUIRED": False,
        "CURRENT_C2_UP_DOWN_YUKAWA_VERTEX_RESIDUES_ACTION_DERIVED": False,
        "CURRENT_C2_QUARK_QUANTUM_HESSIAN_DERIVED": False,
        "CURRENT_C2_PHYSICAL_QUARK_POLES_DERIVED": False,
        "CKM_MATRIX_DERIVED": False,
        "MEASURED_QUARK_MASS_USED": False,
        "particle_spectrum_rebuilt": False,
        "FULL_BHSM_COMPLETE": False,
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "affine_first_order_contact_theorem",
    "claim_boundary",
    "determinant_hessian_reduction",
    "exact_remaining_owner",
    "squared_pencil_contact_closure",
]
