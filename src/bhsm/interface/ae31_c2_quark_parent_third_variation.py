"""Exact quark LR--Higgs third variations in the current AE3.1 action.

The current action, the maximal four-dimensional EFT registry, and the
reduced current-C2 HS vertex are distinct variational objects.  This module
evaluates all three without identifying an absent intrinsic-Higgs term with a
formal independent EFT input or with a family-central auxiliary vertex.
"""

from __future__ import annotations

from typing import Any

from bhsm.interface.ae31_c2_intrinsic_m4_lepton_action import (
    ACTION_VERSION,
    action_composition_contract,
)
from bhsm.interface.ae3_c2_hs_mixed_variation import (
    claim_boundary as hs_claim_boundary,
)
from bhsm.interface.master_action.coefficients import rows as coefficient_rows
from bhsm.interface.master_action.terms import term_rows


CLASSIFICATION = "AE31_CURRENT_C2_QUARK_PARENT_THIRD_VARIATION_EVALUATION"


def current_action_incidence_theorem() -> dict[str, Any]:
    """Evaluate the requested derivatives by active-field incidence."""

    composition = action_composition_contract()
    return {
        "action_version": ACTION_VERSION,
        "active_composition": composition["composition"],
        "active_added_intrinsic_M4_term": composition["action_term"],
        "active_added_term_field_channels": ["bar(L_L)", "H", "e_R"],
        "up_channel_derivative": (
            "P_u*D_bar(Q_L)*D_H_tilde*D_u_R*S_AE3_1*P_u=0"
        ),
        "down_channel_derivative": (
            "P_d*D_bar(Q_L)*D_H*D_d_R*S_AE3_1*P_d=0"
        ),
        "up_zero_by_field_incidence": True,
        "down_zero_by_field_incidence": True,
        "reason": (
            "S_AE3_0_HAS_NO_INTRINSIC_QUARK_LR_HIGGS_TRILINEAR_AND_"
            "S_4_lH_BHSM_ADDS_ONLY_THE_CHARGED_LEPTON_CHANNEL"
        ),
        "up_down_Yukawa_terms_added": composition["up_down_Yukawa_terms_added"],
        "zero_is_a_derived_absence_not_a_zero_physical_quark_mass_claim": True,
        "physical_quark_mass_zero_promoted": False,
    }


def maximal_eft_variation_theorem() -> dict[str, Any]:
    """Differentiate the formal maximal S4 EFT term and type its residue."""

    yukawa_term = next(row for row in term_rows() if row["term_id"] == "T4_Yukawa")
    coefficient = next(
        row for row in coefficient_rows() if row["coefficient_id"] == "Yukawa_matrices"
    )
    non_yukawa_terms = [row for row in term_rows() if row["term_id"] != "T4_Yukawa"]
    return {
        "registry_action_level": yukawa_term["level"],
        "registry_term_id": yukawa_term["term_id"],
        "registry_expression": yukawa_term["expression"],
        "formal_up_variation": (
            "P_u*D_bar(Q_L)*D_H_tilde*D_u_R*S4eff*P_u="
            "-sqrt(-h)*P_u*Y_u*P_u_times_delta_and_canonical_index_contractions"
        ),
        "formal_down_variation": (
            "P_d*D_bar(Q_L)*D_H*D_d_R*S4eff*P_d="
            "-sqrt(-h)*P_d*Y_d*P_d_times_delta_and_canonical_index_contractions"
        ),
        "only_T4_Yukawa_contributes": all(
            not ({"Psi", "H"} <= set(row["fields"])) for row in non_yukawa_terms
        ),
        "coefficient_classification": coefficient["classification"],
        "coefficient_action_level": coefficient["action_level"],
        "coefficient_rationale": coefficient["rationale"],
        "variation_recovers_input_matrix": True,
        "variation_derives_input_matrix": False,
        "representation_trace_or_projector_removes_sector_scalar": False,
        "why_projection_does_not_normalize": (
            "P_f*(c_f*T_f)*P_f=c_f*(P_f*T_f*P_f)_FOR_EVERY_POSITIVE_c_f"
        ),
    }


def current_hs_vertex_separation() -> dict[str, Any]:
    """Separate the retained auxiliary third vertex from intrinsic H/Htilde."""

    boundary = hs_claim_boundary()
    return {
        "current_C2_reduced_third_vertex_nonzero": boundary[
            "current_C2_third_LR_HS_vertex_retained"
        ],
        "derivative": "D_HS*D_bar(c)*D_c*S_reduced=V_tensor_I3_family",
        "family_factor": "I3",
        "intrinsic_H_or_H_tilde_derivative": False,
        "current_C2_dynamical_HS_kernel_derived": boundary[
            "current_C2_dynamical_HS_kernel_derived"
        ],
        "physical_broken_LR_direction_selected": boundary[
            "current_C2_broken_LR_saddle_derived"
        ],
        "can_canonically_normalize_Y_u_or_Y_d": False,
        "can_generate_attached_family_noncentral_T_u_or_T_d": False,
        "identification_required_before_reuse": (
            "ACTION_DERIVED_MAP_HS_TO_(H,H_tilde)_PLUS_A_DYNAMICAL_HS_"
            "KINETIC_RESIDUE_AND_SECTOR_FAMILY_PUSHFORWARD"
        ),
    }


def historical_residue_adjudication() -> dict[str, Any]:
    """Record why nearby residue calculations do not alter the evaluation."""

    return {
        "rows": [
            {
                "object": "V15_73_EVENT_SHELL_GAMMA_BOUNDARY_THIRD_RESIDUE",
                "result": "FORMAL_RESIDUE_DEFINED",
                "current_AE31_intrinsic_quark_owner": False,
                "reason": "ACTUAL_EVENT_SHELL_CROSSING_NOT_ESTABLISHED_IN_V15_73",
            },
            {
                "object": "V15_91_PROPER_CYCLE_CANONICAL_YUKAWA",
                "result": "Y_PROPER_TIMES_I3_EVALUATED",
                "current_AE31_intrinsic_quark_owner": False,
                "reason": (
                    "PERIODIC_PROPER_CYCLE_SURROGATE_IS_FAMILY_CENTRAL_AND_"
                    "ITS_LOCAL_ELECTRIC_MAGNETIC_MAXWELL_COEFFICIENTS_MISMATCH"
                ),
            },
            {
                "object": "V15_96_COMMON_QUANTUM_SUPERDETERMINANT",
                "result": "THIRD_DERIVATIVE_CONTRACT_FORMULATED",
                "current_AE31_intrinsic_quark_owner": False,
                "reason": (
                    "INTERACTING_SOURCE_HESSIAN_AND_COUPLED_QUANTUM_EVENT_"
                    "SADDLE_NOT_SOLVED"
                ),
            },
            {
                "object": "AE32_CURRENT_C2_EINSTEIN_CARTAN_AUXILIARY_VERTEX",
                "result": "LOCAL_UNIT_AUXILIARY_VERTEX_ONLY",
                "current_AE31_intrinsic_quark_owner": False,
                "reason": (
                    "RETAINED_ZERO_MODE_OUTSIDE_GLOBAL_STATIONARY_EC_ACTION_"
                    "DOMAIN_AND_NO_PROPAGATING_HS_KINETIC_RESIDUE"
                ),
            },
        ],
        "attachable_current_AE31_intrinsic_quark_residue_count": 0,
        "historical_result_discarded": False,
        "historical_result_silently_promoted": False,
    }


def exact_next_owner() -> dict[str, Any]:
    return {
        "required_functional": (
            "Gamma_qH_current_C2[barQ_L,u_R,d_R,H]_ON_THE_AE3_1_DOMAIN"
        ),
        "required_derivatives": [
            "P_u*D_bar(Q_L)*D_H_tilde*D_u_R*Gamma_qH*P_u",
            "P_d*D_bar(Q_L)*D_H*D_d_R*Gamma_qH*P_d",
        ],
        "must_include": [
            "current_C2_trace_and_boundary_domain",
            "canonical_Q_L_u_R_d_R_and_H_wavefunction_normalizations",
            "action_derived_identification_of_H_and_H_tilde",
            "pushforward_of_the_reused_T_u_and_T_d_family_operators",
            "sector_residues_c_u_and_c_d_from_the_same_functional",
        ],
        "proved_equivalent_route_allowed": (
            "CURRENT_HS_VERTEX_MAY_BE_USED_ONLY_AFTER_THE_HS_TO_INTRINSIC_"
            "HIGGS_MAP,_DYNAMICAL_RESIDUE,_AND_SECTOR_PUSHFORWARD_ARE_DERIVED"
        ),
        "quark_mass_fit_allowed": False,
        "independent_c_u_or_c_d_allowed": False,
    }


def claim_boundary() -> dict[str, Any]:
    return {
        "CURRENT_AE31_UP_DOWN_INTRINSIC_HIGGS_THIRD_VARIATIONS_EVALUATED": True,
        "CURRENT_AE31_UP_INTRINSIC_HIGGS_THIRD_VARIATION_NONZERO": False,
        "CURRENT_AE31_DOWN_INTRINSIC_HIGGS_THIRD_VARIATION_NONZERO": False,
        "MAXIMAL_S4_EFT_VARIATIONS_RECOVER_INDEPENDENT_Y_U_Y_D": True,
        "MAXIMAL_S4_EFT_VARIATIONS_DERIVE_Y_U_Y_D": False,
        "CURRENT_C2_REDUCED_HS_THIRD_VERTEX_IDENTIFIED_WITH_PHYSICAL_HIGGS": False,
        "CURRENT_C2_UP_DOWN_YUKAWA_OPERATORS_ACTION_OWNED": False,
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
    "claim_boundary",
    "current_action_incidence_theorem",
    "current_hs_vertex_separation",
    "exact_next_owner",
    "historical_residue_adjudication",
    "maximal_eft_variation_theorem",
]
