"""Retained-action no-go for the missing physical outer Calderon operator.

This theorem combines the exact AE2/AE3.1 boundary configuration-space
inventory with the already-derived fermion-state and gauge-residue no-gos.
It determines what the retained action cannot select and leaves open only
genuinely new global-domain or microscopic boundary/collar input.
"""

from __future__ import annotations

from typing import Any

from bhsm.interface.action_extension_global_spin_reset_ae2 import (
    action_definition,
)
from bhsm.interface.ae31_c2_fixed_history_state_nonuniqueness import (
    finite_rank_hadamard_nonuniqueness_theorem,
    pure_self_dual_covariance,
)
from bhsm.interface.ae31_c2_calderon_principal_symbol import (
    local_boundary_symbol_theorem,
)
from bhsm.interface.ae3_c2_gauge_mismatch_resolution import (
    selection_certificate,
)
from bhsm.interface.ae3_c2_maxwell_common_shift_no_go import (
    exact_common_shift_no_go,
    required_noncommon_correction,
)
from bhsm.interface.ae3_c2_two_sided_calderon import (
    two_sided_residue_certificate,
)


ACTION_VERSION = "BHSM-AE-3.1.0"
CLASSIFICATION = "CURRENT_C2_RETAINED_ACTION_OUTER_CALDERON_COMPLETION_NO_GO"


def fermion_selector_configuration_space() -> dict[str, Any]:
    """Prove that the retained action has no state-selecting coordinate."""

    action = action_definition()
    nonuniqueness = finite_rank_hadamard_nonuniqueness_theorem()
    witness = pure_self_dual_covariance(0.371)
    symbol = local_boundary_symbol_theorem()
    return {
        "bulk_configuration_variable": "Psi_ON_THE_AE2_RESET_GLUED_DOMAIN",
        "internal_transmission_variable": "Gamma0_child-U_R*Gamma0_event=0",
        "independent_fermion_surface_action": action[
            "independent_normal_matter_boundary_action"
        ],
        "pregeometric_core_spinor_content": action[
            "pregeometric_core_field_content"
        ],
        "Cauchy_covariance_C_is_action_configuration_variable": False,
        "smooth_bisolution_K_is_action_configuration_variable": False,
        "Euler_Lagrange_equation_for_C_or_K_present": False,
        "nontrivial_covariance_distance_witness": witness[
            "distance_from_zero_covariance"
        ],
        "witness_is_pure_self_dual": (
            witness["purity_residual"] < 1.0e-12
            and witness["self_dual_CAR_residual"] < 1.0e-12
        ),
        "witness_is_smoothing_and_Hadamard_preserving": nonuniqueness[
            "P_theta_minus_P_is_finite_rank_smoothing"
        ],
        "continuum_preserves_reset_and_family_data": (
            nonuniqueness["reset_transport_preserves_the_continuum"]
            and nonuniqueness["family_projectors_unchanged"]
        ),
        "continuum_shares_fixed_local_symbol": symbol[
            "all_admissible_Hadamard_completions_share_spinor_symbol"
        ],
        "retained_classical_action_selects_smooth_covariance": False,
        "reason": (
            "C_AND_ITS_SMOOTHING_PART_ARE_QUANTUM_STATE_DATA_NOT_COORDINATES_"
            "OF_THE_RETAINED_CLASSICAL_ACTION;_THE_INTERNAL_RESET_HAS_ZERO_"
            "INDEPENDENT_FERMION_SURFACE_ACTION"
        ),
    }


def gauge_outer_response_exhaustion() -> dict[str, Any]:
    """Close the coefficient-free retained gauge completion routes."""

    selection = selection_certificate()
    reflected = two_sided_residue_certificate()
    common = exact_common_shift_no_go()
    required = required_noncommon_correction()
    return {
        "coefficient_free_route_selected_before_evaluation": selection[
            "selected_route"
        ],
        "coefficient_free_admissible_route_count": selection["admissible_count"],
        "selected_two_sided_route_evaluated": True,
        "two_sided_Zt_over_Zs": reflected["Zt_over_Zs_two_sided"],
        "two_sided_route_repairs_mismatch": reflected[
            "one_positive_Lorentzian_residue"
        ],
        "common_local_F_squared_shift_repairs_mismatch": common[
            "finite_local_covariant_F_squared_shift_repairs_mismatch"
        ],
        "required_noncommon_equation": required["required_equation"],
        "required_delta_Zt_minus_delta_Zs": required[
            "required_delta_Zt_minus_delta_Zs"
        ],
        "retained_action_selects_one_noncommon_correction": required[
            "one_candidate_selected_by_current_action"
        ],
        "zero_contact_action_may_be_replaced_by_fitted_surface_term": False,
        "retained_coefficient_free_local_and_reflected_routes_exhausted": True,
        "all_possible_global_or_microscopic_extensions_excluded": False,
    }


def outer_calderon_no_go_theorem() -> dict[str, Any]:
    """State the exact current-action theorem and the two live exit classes."""

    return {
        "hypotheses": [
            "RETAIN_BHSM_AE3_1_BULK_ACTION_AND_AE2_INTERNAL_RESET_DOMAIN",
            "RETAIN_ZERO_INDEPENDENT_FERMION_AND_GAUGE_CONTACT_ACTION",
            "DO_NOT_INSERT_A_STATE_PARAMETER_COUPLING_RESIDUE_OR_CONE_RETUNING",
            "USE_THE_RECIPROCAL_REFLECTED_CURRENT_C2_EXTERIOR_WHEN_NO_NEW_"
            "GLOBAL_DOMAIN_IS_DERIVED",
        ],
        "fermion_conclusion": (
            "NO_UNIQUE_SMOOTH_SELF_DUAL_CAR_COVARIANCE_IS_SELECTED"
        ),
        "gauge_conclusion": (
            "NO_SINGLE_POSITIVE_LORENTZIAN_MAXWELL_RESIDUE_IS_PRODUCED"
        ),
        "scalar_consequence": (
            "FINITE_STATE_DEPENDENT_SCALAR_HESSIAN_DATA_REMAIN_UNSELECTED"
        ),
        "combined_conclusion": (
            "THE_RETAINED_AE3_1_ACTION_AND_CURRENT_RECIPROCAL_DOMAIN_CANNOT_"
            "SUPPLY_THE_COMPLETE_PHYSICAL_OUTER_GAUGE_SPINOR_GHOST_"
            "CALDERON_OPERATOR"
        ),
        "live_exit_classes": [
            {
                "class": "GLOBAL_DOMAIN_COMPLETION",
                "required_object": (
                    "ACTION_SELECTED_NONREFLECTION_MAXIMAL_EXTERIOR_OR_"
                    "REALIZED_ASYMPTOTIC_OR_EUCLIDEAN_STATE_CONDITION"
                ),
                "action_version_change_logically_required": False,
            },
            {
                "class": "MICROSCOPIC_ACTION_EXTENSION",
                "required_object": (
                    "FIXED_BOUNDARY_OR_COLLAR_FUNCTIONAL_WITH_GAUGE_BRST_"
                    "AND_SELF_DUAL_CAR_VARIATION"
                ),
                "action_version_change_logically_required": True,
            },
        ],
        "one_exit_class_selected_here": False,
        "no_go_scope": "RETAINED_AE3_1_ACTION_PLUS_CURRENT_RECIPROCAL_DOMAIN_ONLY",
        "BHSM_as_a_whole_refuted": False,
    }


def claim_boundary() -> dict[str, Any]:
    return {
        "CURRENT_AE31_RETAINED_ACTION_OUTER_CALDERON_COMPLETION_NO_GO_DERIVED": True,
        "CURRENT_AE31_FERMION_SMOOTH_STATE_SELECTOR_ABSENT_DERIVED": True,
        "CURRENT_AE3_COEFFICIENT_FREE_GAUGE_COMPLETION_ROUTES_EXHAUSTED": True,
        "CURRENT_C2_PHYSICAL_GAUGE_SPINOR_GHOST_CALDERON_PROJECTOR_DERIVED": False,
        "CURRENT_C2_ACTION_SELECTED_HADAMARD_STATE_DERIVED": False,
        "CURRENT_C2_LORENTZIAN_MAXWELL_RESIDUE_DERIVED": False,
        "CURRENT_C2_FINITE_SCALAR_HESSIAN_DERIVED": False,
        "CURRENT_C2_NORMALIZED_PHOTON_PROPAGATOR_DERIVED": False,
        "MUON_MAGNETIC_MOMENT_DERIVED": False,
        "new_boundary_coefficient_inserted": False,
        "BHSM_ROUTE_FAILURE_NOT_GLOBAL_REFUTATION": True,
        "FULL_BHSM_COMPLETE": False,
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "claim_boundary",
    "fermion_selector_configuration_space",
    "gauge_outer_response_exhaustion",
    "outer_calderon_no_go_theorem",
]
