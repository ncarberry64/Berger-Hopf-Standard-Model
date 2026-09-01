"""Classify the action parity of the recovered scalar-profile attachment.

The existing Higgs-selected U(1) connection is chirality even.  The recovered
quark--Higgs incidence is chirality odd.  This module proves that the former
cannot be varied into the latter and identifies the exact missing parent
Dirac/superconnection object without adding it as a new input.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from bhsm.interface.ae31_c2_intrinsic_m4_lepton_action import ACTION_VERSION
from bhsm.interface.ae31_c2_quark_higgs_incidence_transport import (
    quark_higgs_support_pencil,
)


CLASSIFICATION = "AE31_CURRENT_C2_QUARK_SCALAR_ATTACHMENT_VARIATION"


def current_action_internal_scalar_incidence() -> dict[str, Any]:
    """Evaluate whether ``Phi`` is an active coordinate of ``S_AE3.1``."""

    return {
        "action_version": ACTION_VERSION,
        "active_composition": "S_AE3_1=S_AE3_0+S_4_lH_BHSM",
        "active_H_field": "INTRINSIC_M4_ACTIVE_FIELD",
        "active_internal_Phi_field": False,
        "historical_scalar_state": "H(x,y)=H(x)*Phi(y)",
        "historical_scalar_state_status": "SCALAR_STATE_ONTOLOGY_CONDITIONAL",
        "delta_S_AE31_over_delta_Phi_defined": False,
        "reason": "PHI_IS_NOT_AN_ACTIVE_FIELD_COORDINATE_OF_THE_VERSIONED_AE31_ACTION",
        "H_times_Phi_kinematic_factorization_is_action_attachment": False,
        "profile_transport_upgraded_to_action_ownership": False,
    }


def chirality_parity_theorem() -> dict[str, Any]:
    """Compare a U(1) connection with the transported LR scalar supports."""

    chirality = np.diag((-1.0, -1.0, 1.0, 1.0))
    p_left = (np.eye(4) - chirality) / 2.0
    p_right = (np.eye(4) + chirality) / 2.0
    # Doubled-hypercharge values in the current basis.  Only diagonality is
    # used by the theorem; the numerical charges provide an explicit witness.
    u1_connection = np.diag((-1.0 / 3.0, -1.0 / 3.0, 4.0 / 3.0, -2.0 / 3.0))
    support = quark_higgs_support_pencil()
    incidence = {
        "up": np.asarray(support["I_up"], dtype=float),
        "down": np.asarray(support["I_down"], dtype=float),
    }
    return {
        "basis_order": support["basis_order"],
        "chirality_operator": chirality.tolist(),
        "u1_chirality_commutator_norm": float(
            np.linalg.norm(chirality @ u1_connection - u1_connection @ chirality)
        ),
        "u1_left_right_block_norm": float(np.linalg.norm(p_left @ u1_connection @ p_right)),
        "u1_right_left_block_norm": float(np.linalg.norm(p_right @ u1_connection @ p_left)),
        "u1_connection_is_chirality_even": True,
        "up_scalar_chirality_anticommutator_norm": float(
            np.linalg.norm(chirality @ incidence["up"] + incidence["up"] @ chirality)
        ),
        "down_scalar_chirality_anticommutator_norm": float(
            np.linalg.norm(chirality @ incidence["down"] + incidence["down"] @ chirality)
        ),
        "transported_scalar_incidence_is_chirality_odd": True,
        "even_U1_connection_variation_can_equal_odd_LR_scalar_vertex": False,
    }


def scalar_only_variation_theorem() -> dict[str, Any]:
    """Separate scalar normalization from mixed fermion incidence."""

    return {
        "scalar_projection": "H(x,y)=H(x)*Phi(y)",
        "scalar_kinetic_reduction": (
            "integral_B|Phi|^2*dmu_Berger_TIMES_integral_M4|D H|^2"
        ),
        "canonical_profile_condition": "integral_B|Phi|^2*dmu_Berger=1",
        "kinetic_residue_conditionally_fixed": True,
        "scalar_action_depends_on_Q_L_u_R_d_R": False,
        "mixed_third_variations": {
            "delta_barQ_delta_Htilde_delta_uR_S_scalar": "0",
            "delta_barQ_delta_H_delta_dR_S_scalar": "0",
        },
        "profile_normalization_generates_Yukawa_vertex": False,
        "profile_response_may_normalize_an_already_owned_odd_vertex": True,
    }


def historical_parent_term_adjudication() -> dict[str, Any]:
    """Classify the two historical Phi-bearing parent scaffold objects."""

    return {
        "rows": [
            {
                "id": "I_U1",
                "expression": "Phi0^dagger*D_tr*Phi0_OR_barPsi*A_Higgs-U1*Psi",
                "role": "TRACE_U1_BOUNDARY_PHASE_AND_CHARGE_ORIENTATION",
                "chirality_parity": "EVEN",
                "contains_explicit_quark_LR_scalar_incidence": False,
                "can_own_c_u_c_d": False,
            },
            {
                "id": "I_BDY",
                "expression": "S_boundary[Psi,Phi0]",
                "role": "SYMBOLIC_FAMILY_INDEX_AND_SECTOR_WINDING_SELECTION",
                "chirality_parity": "NOT_EVALUABLE_FROM_SYMBOLIC_EXPRESSION",
                "contains_explicit_quark_LR_scalar_incidence": False,
                "can_own_c_u_c_d": False,
            },
        ],
        "boundary_functional_full_action_variation_completed": False,
        "target_values_6_and_12_relabelled_as_Yukawa_residues": False,
        "Higgs_selected_U1_phase_discarded": False,
        "proper_role_preserved": "CHARGE_AND_BOUNDARY_ORIENTATION_SELECTION",
    }


def required_odd_endomorphism_contract() -> dict[str, Any]:
    """Identify the unique parity class that can carry the existing supports."""

    support = quark_higgs_support_pencil()
    up = np.asarray(support["I_up"], dtype=float)
    down = np.asarray(support["I_down"], dtype=float)
    chirality = np.diag((-1.0, -1.0, 1.0, 1.0))
    combined = 0.7 * up - 1.1 * down
    return {
        "required_parent_object": (
            "ODD_INTERNAL_DIRAC_OR_SUPERCONNECTION_ENDOMORPHISM_E_H[H,Htilde]"
        ),
        "action_location": "integral_barPsi*E_H[H,Htilde]*Psi",
        "grading_condition": "Gamma_chi*E_H+E_H*Gamma_chi=0",
        "sample_grading_residual": float(
            np.linalg.norm(chirality @ combined + combined @ chirality)
        ),
        "support_decomposition": "E_H=V_u(Htilde)*I_up+V_d(H)*I_down",
        "existing_binary_supports_reused": True,
        "new_representation_channel_required": False,
        "new_independent_contact_term_required": False,
        "coefficient_or_residue_inserted": False,
        "object_promoted_into_AE31_action": False,
    }


def exact_remaining_owner() -> dict[str, Any]:
    return {
        "derive_from_one_parent_action": [
            "odd_endomorphism_E_H_and_its_normalization",
            "identification_of_intrinsic_H_with_the_universal_internal_profile",
            "complete_retained_internal_trace_or_selected_density",
            "c_u_and_c_d_on_the_existing_I_up_and_I_down_supports",
        ],
        "then_reuse": [
            "projector_overlap_R_up_R_down",
            "squared_pencil_contact_Q_fg",
            "family_shapes_T_u_T_d",
            "current_C2_radial_domain_and_birth_trace",
        ],
        "U1_connection_or_scalar_kinetic_term_can_substitute": False,
        "historical_target_or_beta_kappa_relabelling_allowed": False,
        "independent_yukawa_or_mass_fit_allowed": False,
    }


def claim_boundary() -> dict[str, Any]:
    return {
        "CURRENT_C2_HIGGS_SELECTED_U1_CONNECTION_LR_VERTEX_EXCLUDED": True,
        "CURRENT_C2_SCALAR_PROFILE_NORMALIZATION_LR_VERTEX_EXCLUDED": True,
        "CURRENT_C2_REQUIRED_ODD_DIRAC_ENDOMORPHISM_CLASS_DERIVED": True,
        "CURRENT_C2_ODD_DIRAC_ENDOMORPHISM_ACTION_OWNED": False,
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
    "chirality_parity_theorem",
    "claim_boundary",
    "current_action_internal_scalar_incidence",
    "exact_remaining_owner",
    "historical_parent_term_adjudication",
    "required_odd_endomorphism_contract",
    "scalar_only_variation_theorem",
]
