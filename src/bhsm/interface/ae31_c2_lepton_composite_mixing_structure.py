"""Current-C2 intrinsic-lepton/composite-HS mixing structure."""

from __future__ import annotations

from fractions import Fraction
from typing import Any

import numpy as np

from bhsm.interface.ae31_c2_intrinsic_m4_lepton_action import (
    ACTION_VERSION,
    charged_lepton_yukawa_operator,
)


CLASSIFICATION = "AE31_CURRENT_C2_LEPTON_COMPOSITE_MIXING_STRUCTURE"


def nonzero_gauge_hs_channel_extension() -> dict[str, Any]:
    """Extend the gauge HS block to every nonzero minimal-SM LR channel."""

    weights = {
        "up": Fraction(7, 5),
        "down": Fraction(13, 10),
        "charged_lepton": Fraction(3, 10),
        "neutrino": Fraction(0, 1),
    }
    inverse = {
        name: str(Fraction(1, 2) / value)
        for name, value in weights.items()
        if value > 0
    }
    return {
        "channel_order": list(weights),
        "pre_Fierz_weights": {name: str(value) for name, value in weights.items()},
        "invertible_HS_channels": ["up", "down", "charged_lepton"],
        "bare_inverse_coefficients_over_G_C2": inverse,
        "three_channel_bare_Hessian": (
            "G_C2^(-1)*diag(5/14,5/13,5/3)"
        ),
        "neutrino_zero_kernel_HS_inverse_defined": False,
        "neutrino_auxiliary_inserted_by_regulator": False,
        "same_gauge_current_kernel_reused": True,
        "new_continuous_coefficient": False,
    }


def shared_charged_lepton_vertex_jet() -> dict[str, Any]:
    """Build the intrinsic and auxiliary vertices on the same lepton LR block."""

    yukawa = np.asarray(charged_lepton_yukawa_operator()["family_operator"], dtype=float)
    identity = np.eye(3)
    lr_flip = np.asarray(((0.0, 1.0), (1.0, 0.0)))
    chirality = np.diag((-1.0, 1.0))
    intrinsic = np.kron(lr_flip, yukawa)
    auxiliary = np.kron(lr_flip, identity)
    cross_contact = intrinsic.T @ auxiliary + auxiliary.T @ intrinsic
    expected = 2.0 * np.kron(np.eye(2), yukawa)
    return {
        "combined_first_order_pencil": (
            "D_e(h,h_HS)=D_e0+h*V_intrinsic+h_HS*V_HS"
        ),
        "V_intrinsic": "sigma1_LR_tensor_Y_l",
        "V_HS": "sigma1_LR_tensor_I3",
        "intrinsic_vertex_matrix": intrinsic.tolist(),
        "auxiliary_vertex_matrix": auxiliary.tolist(),
        "intrinsic_grading_residual": float(
            np.linalg.norm(np.kron(chirality, identity) @ intrinsic + intrinsic @ np.kron(chirality, identity))
        ),
        "auxiliary_grading_residual": float(
            np.linalg.norm(np.kron(chirality, identity) @ auxiliary + auxiliary @ np.kron(chirality, identity))
        ),
        "first_order_mixed_contact": 0.0,
        "squared_pencil_mixed_contact": cross_contact.tolist(),
        "squared_pencil_cross_contact_formula": "Q_intrinsic,HS=2*I_LR*Y_l",
        "squared_pencil_cross_contact_residual": float(
            np.linalg.norm(cross_contact - expected)
        ),
        "shared_fermion_bilinear": "bar(L_L)*e_R+h.c.",
        "measured_lepton_mass_used": False,
    }


def one_loop_mixing_factorization() -> dict[str, Any]:
    """Factor the formal mixed determinant Hessian by family projector."""

    eigenvalues = charged_lepton_yukawa_operator()["eigenvalues_heavy_middle_light"]
    return {
        "effective_action": "Gamma_e=-Tr_log(D_e)",
        "mixed_second_variation": (
            "M_eHS[C]=Tr[G_e[C]*V_HS*G_e[C]*V_intrinsic]"
        ),
        "family_projector_form": (
            "M_eHS[C]=sum_f y_f*chi_f[C]*P_f_WHEN_G_e_COMMUTES_WITH_Y_l"
        ),
        "intrinsic_Y_l_eigenvalues": eigenvalues,
        "Y_l_family_noncentral": len(set(eigenvalues)) == 3,
        "current_C2_chiral_operator_commutes_with_Y_l_family_projectors": True,
        "universal_Hadamard_pole": (
            "M_eHS,sing=chi_Had,sing*Y_l"
        ),
        "universal_pole_family_direction_action_derived": True,
        "finite_mixing": "sum_f y_f*chi_f,fin[C]*P_f",
        "finite_chi_f_selected": False,
        "full_numeric_mixing_matrix_derived": False,
        "arbitrary_family_equal_state_assumed": False,
    }


def species_block_selection_theorem() -> dict[str, Any]:
    """Classify mixing under vector-gauge perturbation at the symmetric point."""

    return {
        "field_order": ["H_intrinsic", "H_HS_e", "H_HS_up", "H_HS_down"],
        "one_fermion_loop_possible_blocks": [
            [True, True, False, False],
            [True, True, False, False],
            [False, False, True, False],
            [False, False, False, True],
        ],
        "intrinsic_to_charged_lepton_composite_shared_species": True,
        "intrinsic_to_quark_composite_shared_species": False,
        "direct_one_fermion_loop_intrinsic_quark_mixing_zero": True,
        "reason": (
            "ORTHOGONAL_SPECIES_PROJECTORS_AND_ONE_UNPAIRED_CHIRALITY_FLIP_"
            "ON_EACH_SEPARATE_FERMION_LOOP"
        ),
        "vector_gauge_vertices_preserve_chirality_and_species": True,
        "all_orders_vector_gauge_mixing_zero_at_chirally_symmetric_quark_background": True,
        "scope": (
            "PERTURBATION_THEORY_IN_THE_RETAINED_VECTOR_GAUGE_VERTICES_WITH_"
            "ZERO_QUARK_ODD_BACKGROUND"
        ),
        "quark_link_requires": (
            "A_COMMON_PARENT_ODD_ENDOMORPHISM_OR_AN_INDEPENDENTLY_DERIVED_"
            "NONZERO_QUARK_CHIRALITY_BREAKING_GAP"
        ),
        "nonperturbative_chirality_violating_topological_vertex_excluded": False,
    }


def exact_remaining_owner() -> dict[str, Any]:
    return {
        "closed": [
            "charged_lepton_gauge_HS_auxiliary_channel",
            "shared_intrinsic_auxiliary_lepton_vertex_jet",
            "universal_Hadamard_mixing_direction_proportional_to_Y_l",
            "one_fermion_loop_species_block_pattern",
        ],
        "next": [
            "finite_current_C2_charged_lepton_composite_mixing_for_selected_covariance",
            "common_parent_odd_intrinsic_to_quark_endomorphism_or_independent_quark_gap",
            "full_derivative_Higgs_composite_residue_matrix",
            "physical_normalized_scalar_eigenvector",
        ],
        "next_operator": (
            "ACTION_DERIVED_COMMON_ODD_ENDOMORPHISM_E_H_ON_THE_EXISTING_"
            "I_up_I_down_SUPPORTS__OR_A_NONZERO_QUARK_GAP_FROM_THE_FULL_"
            "CURRENT_C2_COMPOSITE_HESSIAN"
        ),
        "one_loop_zero_replaced_by_fitted_mixing": False,
    }


def claim_boundary() -> dict[str, Any]:
    return {
        "CURRENT_C2_CHARGED_LEPTON_GAUGE_HS_CHANNEL_DERIVED": True,
        "CURRENT_C2_INTRINSIC_LEPTON_COMPOSITE_VERTEX_JET_DERIVED": True,
        "CURRENT_C2_LEPTON_COMPOSITE_HADAMARD_POLE_DIRECTION_DERIVED": True,
        "CURRENT_C2_DIRECT_ONE_FERMION_LOOP_INTRINSIC_QUARK_MIXING_ZERO_DERIVED": True,
        "CURRENT_C2_FINITE_LEPTON_COMPOSITE_MIXING_DERIVED": False,
        "CURRENT_C2_VECTOR_GAUGE_INTRINSIC_QUARK_MIXING_EXCLUDED_ON_SYMMETRIC_BACKGROUND": True,
        "CURRENT_C2_COMMON_PARENT_ODD_QUARK_ENDOMORPHISM_DERIVED": False,
        "CURRENT_C2_PHYSICAL_SINGLE_HIGGS_DIRECTION_SELECTED": False,
        "CURRENT_C2_CANONICAL_QUARK_YUKAWA_RESIDUES_DERIVED": False,
        "CURRENT_C2_PHYSICAL_QUARK_POLES_DERIVED": False,
        "MEASURED_MASS_USED": False,
        "particle_spectrum_rebuilt": False,
        "FULL_BHSM_COMPLETE": False,
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "claim_boundary",
    "exact_remaining_owner",
    "nonzero_gauge_hs_channel_extension",
    "one_loop_mixing_factorization",
    "shared_charged_lepton_vertex_jet",
    "species_block_selection_theorem",
]
