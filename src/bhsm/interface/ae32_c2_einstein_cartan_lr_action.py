"""Current-C2 first-order Einstein--Cartan left/right action completion.

The completion changes the Einstein--Dirac representative from second order
to its coefficient-free first-order form.  Eliminating the algebraic
contorsion then adds the already-derived scalar LR Schur complement.  The
result is an action-owned local four-fermion kernel, not yet a propagating
Higgs/Yukawa sector.
"""

from __future__ import annotations

from typing import Any

import numpy as np


ACTION_VERSION = "BHSM-AE-3.2.0"
PREDECESSOR_ACTION_VERSION = "BHSM-AE-3.1.0"
CLASSIFICATION = "CURRENT_C2_FIRST_ORDER_EINSTEIN_CARTAN_LR_ACTION"
CLIFFORD_FIERZ_COEFFICIENT = 3.0 / 4.0


def action_completion_contract() -> dict[str, Any]:
    """State the owner-selected first-order lift without double counting."""

    return {
        "action_version": ACTION_VERSION,
        "predecessor_action_version": PREDECESSOR_ACTION_VERSION,
        "owner_decision": (
            "SELECT_THE_HISTORICAL_COEFFICIENT_FREE_FIRST_ORDER_"
            "EINSTEIN_DIRAC_COMPLETION_ON_CURRENT_C2"
        ),
        "composition": "S_AE3_2=FirstOrderLift_spin_connection[S_AE3_1]",
        "reduced_composition": "S_AE3_2_reduced=S_AE3_1+Gamma_EC",
        "replacement_not_addition": True,
        "replaced_representative": (
            "LEVI_CIVITA_EINSTEIN_DIRAC_REPRESENTATIVE"
        ),
        "independent_spin_connection": "omega=omega_LeviCivita+C",
        "contorsion_is_algebraic": True,
        "new_continuous_coefficient": False,
        "new_elementary_field": False,
        "same_reset_generated_C2_background": True,
        "Gamma_EC_on_symmetric_zero_fermion_background": 0.0,
        "background_geometry_first_variation_changed_at_zero_fermion": False,
        "same_AE2_spin_x_gauge_reset_domain": True,
        "intrinsic_M4_Higgs_term_removed": False,
        "intrinsic_Higgs_identified_with_HS_auxiliary": False,
        "particle_spectrum_rebuilt": False,
    }


def contorsion_schur_complement() -> dict[str, Any]:
    """Return the exact Clifford/Fierz reduction inherited from v15.76."""

    return {
        "spin_current": (
            "J_S^ABC=(1/4)*bar(Psi)*Gamma^[A*Gamma^B*Gamma^C]*Psi"
        ),
        "contorsion_quadratic_form": (
            "S_C=(1/2)<C,K_G5*Lambda(sigma)*M_Clifford*C>+<C,J_S>"
        ),
        "stationary_contorsion": (
            "C_star=-(K_G5*Lambda*M_Clifford)^(-1)*J_S"
        ),
        "induced_current_action": (
            "Gamma_EC=-1/2<J_S,(K_G5*Lambda*M_Clifford)^(-1)*J_S>"
        ),
        "eliminated_three_form_term": (
            "-(bar(Psi)*Gamma_ABC*Psi)^2/(32*K_G5*Lambda)"
        ),
        "four_dimensional_axial_magnitude": "3/(16*K_G5*Lambda)",
        "scalar_LR_Fierz_coefficient": "c_EC=3/4",
        "c_EC": CLIFFORD_FIERZ_COEFFICIENT,
        "scalar_LR_sign": "ATTRACTIVE",
        "coefficient_inserted_by_hand": False,
        "same_parent_Einstein_Dirac_Hessian": True,
    }


def local_current_c2_lr_kernel(sigma: object) -> dict[str, Any]:
    """Evaluate ``K_G5 G_EC=3/[4 Lambda(sigma)]`` in the C2 interior."""

    material = np.asarray(sigma, dtype=float)
    if (
        material.size == 0
        or not np.all(np.isfinite(material))
        or np.any(np.abs(material) >= 0.5)
    ):
        raise ValueError("finite current-C2 interior values |sigma|<1/2 required")
    weight = 1.0 - 4.0 * material**2
    kernel = CLIFFORD_FIERZ_COEFFICIENT / weight
    inverse_kernel = weight / CLIFFORD_FIERZ_COEFFICIENT
    return {
        "action_version": ACTION_VERSION,
        "domain": "CURRENT_C2_REGULAR_INTERIOR__ABS_SIGMA_LT_ONE_HALF",
        "localization_weight": weight.tolist(),
        "K_G5_times_G_EC": kernel.tolist(),
        "G_EC_inverse_over_K_G5": inverse_kernel.tolist(),
        "formula": "G_EC=(3/4)/(K_G5*(1-4*sigma^2))",
        "inverse_formula": "G_EC^(-1)/K_G5=(4/3)*(1-4*sigma^2)",
        "positive": bool(np.all(kernel > 0.0)),
        "reflection_even": bool(
            np.array_equal(
                kernel,
                CLIFFORD_FIERZ_COEFFICIENT / (1.0 - 4.0 * (-material) ** 2),
            )
        ),
        "locally_finite": True,
        "endpoint_limit": "+infinity_as_abs(sigma)_up_to_1/2",
        "global_zero_mode_weighted_integrability_derived": False,
        "global_reduced_EC_action_domain_derived": False,
    }


def scalar_lr_channel_ledger() -> dict[str, Any]:
    """Attach the Fierz scalar to every retained SM left/right channel."""

    multiplicities = {
        "up": 9,
        "down": 9,
        "charged_lepton": 3,
        "neutrino_effective_extension": 3,
    }
    rows = {
        "up": "(bar(Q_L)*u_R)*(bar(u_R)*Q_L)",
        "down": "(bar(Q_L)*d_R)*(bar(d_R)*Q_L)",
        "charged_lepton": "(bar(L_L)*e_R)*(bar(e_R)*L_L)",
        "neutrino_effective_extension": (
            "(bar(L_L)*nu_R)*(bar(nu_R)*L_L)"
        ),
    }
    return {
        "channels": rows,
        "pairing_multiplicities_three_families": multiplicities,
        "total_pairing_multiplicity": sum(multiplicities.values()),
        "family_action": "I3",
        "color_action": "I3_color_IN_QUARK_CHANNELS",
        "all_channels_gauge_singlets_after_LR_product": True,
        "same_scalar_kernel_per_normalized_pair": True,
        "family_noncentral_direction_selected": False,
        "neutrino_is_effective_extension_not_minimal_SM": True,
    }


def algebraic_hubbard_stratonovich_block() -> dict[str, Any]:
    """Record the exact auxiliary-field representation of the LR kernel."""

    return {
        "identity": (
            "exp[+G_EC*integral(O_f_dagger*O_f)] proportional_to "
            "integral DH_f exp[-integral(H_f_dagger*G_EC^(-1)*H_f-"
            "H_f*O_f_dagger-H_f_dagger*O_f)]"
        ),
        "O_f": "bar(Psi_L)*Psi_R",
        "unnormalized_LR_HS_vertex": 1.0,
        "HS_quadratic_coefficient": "G_EC^(-1)",
        "HS_quadratic_coefficient_positive_in_C2_interior": True,
        "HS_derivative_kinetic_term_present": False,
        "auxiliary_field_is_propagating": False,
        "canonical_Yukawa_residue_derived": False,
        "physical_single_Higgs_direction_selected": False,
        "intrinsic_M4_Higgs_mixing_derived": False,
    }


def charged_bridge_separation_theorem() -> dict[str, Any]:
    """Separate historical family bridges from a canonical Yukawa residue."""

    return {
        "historical_beta_kappa_object": (
            "CONDITIONAL_TRIDIAGONAL_FAMILY_BRIDGE_ENTRIES"
        ),
        "current_EC_object": "ACTION_OWNED_LOCAL_SCALAR_LR_FOUR_FERMION_KERNEL",
        "objects_are_the_same_variation": False,
        "reason": (
            "BETA_AND_KAPPA_ACT_INSIDE_THE_FROZEN_THREE_SLOT_FAMILY_MODULE;_"
            "G_EC_MULTIPLIES_THE_GAUGE_SINGLET_LR_CHANNEL_AND_IS_FAMILY_I3"
        ),
        "auxiliary_rescaling": (
            "H_f_prime=a*H_f_changes_the_coordinate_vertex_and_quadratic_"
            "coefficient_but_leaves_the_eliminated_four_fermion_kernel_FIXED"
        ),
        "consequence": (
            "A_PROPAGATING_HS_TWO_POINT_RESIDUE_AND_A_PHYSICAL_HIGGS_"
            "DIRECTION_OR_MIXING_MAP_ARE_REQUIRED_BEFORE_Y_f_IS_CANONICAL"
        ),
        "beta_u_or_beta_d_promoted_to_Yukawa_prefactor": False,
        "kappa_u_or_kappa_d_promoted_to_Yukawa_prefactor": False,
        "independent_c_u_or_c_d_inserted": False,
    }


def claim_boundary() -> dict[str, Any]:
    return {
        "BHSM_AE32_FIRST_ORDER_EINSTEIN_CARTAN_COMPLETION_SELECTED": True,
        "CURRENT_C2_LOCAL_ALGEBRAIC_LR_KERNEL_DERIVED": True,
        "CURRENT_C2_EXACT_CLIFFORD_FIERZ_COEFFICIENT_DERIVED": True,
        "CURRENT_C2_ALL_SM_LR_CHANNELS_ATTACHED": True,
        "CURRENT_C2_GLOBAL_REDUCED_EC_ACTION_DOMAIN_DERIVED": False,
        "CURRENT_C2_PROPAGATING_HS_KINETIC_KERNEL_DERIVED": False,
        "CURRENT_C2_PHYSICAL_HIGGS_DIRECTION_DERIVED": False,
        "UP_DOWN_ACTION_YUKAWA_PREFACTORS_DERIVED": False,
        "QUARK_MASS_OPERATORS_DERIVED": False,
        "PHYSICAL_CKM_MATRIX_DERIVED": False,
        "HISTORICAL_CHARGED_BRIDGE_VALUES_PROMOTED": False,
        "new_continuous_coefficient_inserted": False,
        "particle_spectrum_rebuilt": False,
        "exact_next_operator": (
            "SAME_AE32_CURRENT_C2_HS_TWO_POINT_KINETIC_MATRIX_AND_"
            "INTRINSIC_HIGGS_MIXING_MAP_ON_AN_ACTION_SELECTED_QUANTUM_STATE"
        ),
        "FULL_BHSM_COMPLETE": False,
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "CLIFFORD_FIERZ_COEFFICIENT",
    "PREDECESSOR_ACTION_VERSION",
    "action_completion_contract",
    "algebraic_hubbard_stratonovich_block",
    "charged_bridge_separation_theorem",
    "claim_boundary",
    "contorsion_schur_complement",
    "local_current_c2_lr_kernel",
    "scalar_lr_channel_ledger",
]
