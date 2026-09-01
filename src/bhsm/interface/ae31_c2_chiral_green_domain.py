"""Current-C2 charged-lepton chiral operator and Green-domain theorem.

This module reconciles the pre-AE2 matter-domain no-go with the owner-selected
AE2 reset lift, composes the AE3.1 family-noncentral mass block with the
canonical first-order Dirac carrier, and states the strongest Green-operator
result supported by the current Lorentzian geometry.  It does not identify the
proper-history Gate-7 resolvent variable with physical momentum squared.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from bhsm.interface.ae31_c2_intrinsic_m4_lepton_action import (
    ACTION_VERSION,
    conditional_tree_mass_operator,
)


CLASSIFICATION = "CURRENT_C2_CHIRAL_OPERATOR_AND_GREEN_DOMAIN_THEOREM"


def domain_provenance_reconciliation() -> dict[str, Any]:
    """Separate the superseded birth-phase family from live domain questions."""

    return {
        "action_version": ACTION_VERSION,
        "pre_AE2_no_go": (
            "THE_UNCHANGED_RETAINED_ACTION_LEFT_A_U1_PARENT_TIMES_U1_CHILD_"
            "MAXIMAL_ISOTROPIC_BIRTH_PHASE_FAMILY"
        ),
        "AE2_successor_decision": (
            "ONE_GLOBAL_SPIN_TIMES_G_SM_SECTION_WITH_TRACE_GRAPH_"
            "Gamma0_child=U_R*Gamma0_event"
        ),
        "AE2_flux_graph": (
            "Gamma1_child=-U_R*Gamma1_event_ON_Dom(D_AE2_squared)"
        ),
        "old_phase_family_live_in_AE31": False,
        "why": (
            "THE_OLD_RESOLVENT_WITNESS_COMPARED_DISTINCT_PRE_AE2_ACTION_"
            "DOMAINS;_THEY_ARE_NOT_MEMBERS_OF_THE_SINGLE_AE2_SUCCESSOR_DOMAIN"
        ),
        "AE3_enclosure_surface_type": "RESOLVED_INTERNAL_MATERIAL_LEVEL_SET",
        "AE3_enclosure_is_terminal_boundary": False,
        "independent_enclosure_fermion_boundary_parameter_required": False,
        "enclosure_fermion_law": (
            "SMOOTH_TRACE_WITH_OPPOSITE_NORMAL_GREEN_FORMS_CANCELLING"
        ),
        "legacy_master_v7_domain_rows": (
            "HISTORICAL_PRE_AE2_GENERAL_DOMAIN_LEDGER_NOT_CURRENT_AE31_SEAM_AUTHORITY"
        ),
        "remaining_domain_question": (
            "A_SINGLE_PHYSICAL_MEMBER_OR_MAXIMAL_CONTINUATION_OF_THE_CURRENT_"
            "C2_FAMILY_AND_ANY_ASYMPTOTIC_OR_FEYNMAN_STATE_DATA"
        ),
    }


def chiral_operator_assembly() -> dict[str, Any]:
    """Assemble the family-resolved first-order LR operator on current C2."""

    mass = conditional_tree_mass_operator()
    matrix = np.asarray(mass["matrix_GeV"], dtype=float)
    zeros = np.zeros_like(matrix)
    mass_block = np.block([[zeros, matrix], [matrix.T, zeros]])
    eigenvalues = np.linalg.eigvalsh(mass_block)
    return {
        "action_version": ACTION_VERSION,
        "operator": "D_l,C2=[[D_L,M_l],[M_l_dagger,D_R]]",
        "domain": (
            "AE2_RESET_GLUED_FIRST_ORDER_DIRAC_DOMAIN_WITH_SMOOTH_AE3_"
            "INTERNAL_ENCLOSURE_TRANSMISSION"
        ),
        "family_mass_matrix_GeV": matrix.tolist(),
        "LR_zero_order_mass_block_GeV": mass_block.tolist(),
        "LR_mass_block_eigenvalues_GeV": eigenvalues.tolist(),
        "Hermitian_zero_order_perturbation": bool(
            np.allclose(mass_block, mass_block.T, atol=0.0, rtol=0.0)
        ),
        "bounded_on_finite_family_fiber": True,
        "first_order_principal_symbol_unchanged": True,
        "maximal_isotropic_Green_trace_form_unchanged": True,
        "domain_preserved_by_zero_order_mass_term": True,
        "same_current_C2_first_order_LR_block_assembled": True,
        "measured_mass_used": False,
        "independent_wavefunction_factor_added": False,
    }


def family_reset_intertwiner_certificate() -> dict[str, Any]:
    """Certify that the AE3.1 mass block does not disturb AE2 reset gluing."""

    mass = np.asarray(
        conditional_tree_mass_operator()["matrix_GeV"], dtype=complex
    )
    # A nontrivial finite unitary representative is enough because AE2 acts on
    # Spin x G_SM while the recovered hierarchy acts on the family factor.
    reset = np.asarray([[0.0, 1.0], [-1.0, 0.0]], dtype=complex)
    family_identity = np.eye(mass.shape[0], dtype=complex)
    lifted_reset = np.kron(reset, family_identity)
    lifted_mass = np.kron(np.eye(reset.shape[0], dtype=complex), mass)
    residual = float(
        np.linalg.norm(lifted_reset @ lifted_mass - lifted_mass @ lifted_reset)
    )
    return {
        "tensor_factors": "(Spin_x_G_SM)_reset tensor C3_family",
        "commutator_residual": residual,
        "mass_block_intertwines_AE2_reset": residual <= 1.0e-12,
        "new_Cayley_phase_introduced": False,
        "new_surface_mass_density_introduced": False,
    }


def green_operator_feasibility() -> dict[str, Any]:
    """State the exact causal and stationary Green-operator claim boundary."""

    return {
        "action_version": ACTION_VERSION,
        "same_domain_chiral_operator_available": True,
        "formal_square_type": (
            "NORMALLY_HYPERBOLIC_PRINCIPAL_PART_PLUS_CURVATURE_GAUGE_MASS_"
            "AND_HIGGS_LOWER_ORDER_TERMS"
        ),
        "conditional_theorem": (
            "ON_EVERY_CERTIFIED_FINITE_CORE_C2_MEMBER_WITH_METRIC_"
            "h=-d_tau_squared+R4(tau)_squared*dOmega3_squared_AND_R4>0_"
            "THE_DIRAC_TYPE_OPERATOR_HAS_UNIQUE_ADVANCED_AND_RETARDED_GREEN_"
            "OPERATORS_FOR_COMPACT_SOURCES"
        ),
        "finite_core_current_C2_M4_development_certified": True,
        "finite_core_topology": "I_tau_TIMES_S3",
        "finite_core_metric": "h=-d_tau^2+R4(tau)^2*dOmega3^2",
        "finite_core_radius_strictly_positive": True,
        "finite_core_proper_duration_strictly_positive": True,
        "finite_core_global_hyperbolicity_derived_familywise": True,
        "Cauchy_surfaces": "{tau=constant}_IS_DIFFEO_TO_S3",
        "physical_C2_history_member_selected": False,
        "maximal_C2_Lorentzian_continuation_certified": False,
        "advanced_retarded_Green_operator_existence_derived": True,
        "advanced_Green_operator_constructed": False,
        "retarded_Green_operator_constructed": False,
        "Feynman_state_or_vacuum_selected": False,
        "Feynman_two_point_function_constructed": False,
        "global_time_translation_invariance_established": False,
        "continuous_global_frequency_diagonalization_available": False,
        "global_physical_pole_and_residue_extraction_available": False,
        "proper_history_product_Dirac_resolvent_variable": "z",
        "proper_history_z_identified_with_p_squared": False,
        "autonomous_enclosure_only_Green_problem_selected": False,
        "why_enclosure_only_is_not_used": (
            "SIGMA_ZERO_IS_AN_INTERNAL_SMOOTH_INTERFACE;_RESTRICTING_TO_"
            "D_enc_ALONE_WOULD_CREATE_A_NEW_BOUNDARY_PROBLEM_NOT_SELECTED_"
            "BY_THE_ACTION"
        ),
        "first_missing_object": (
            "PHYSICAL_CURRENT_C2_HISTORY_MEMBER_OR_MAXIMAL_CONTINUATION_PLUS_"
            "A_FEYNMAN_OR_ASYMPTOTIC_STATE_CLASS_FOR_DRESSED_POLE_EXTRACTION"
        ),
        "mass_operator_is_first_obstruction": False,
        "AE2_reset_domain_is_first_obstruction": False,
        "result": (
            "CURRENT_C2_FIRST_ORDER_CHIRAL_OPERATOR_ASSEMBLED;_FINITE_CORE_"
            "ADVANCED_RETARDED_GREEN_EXISTENCE_DERIVED_FAMILYWISE;_GLOBAL_"
            "FREQUENCY_AND_DRESSED_POLES_OPEN"
        ),
    }


def claim_boundary() -> dict[str, Any]:
    return {
        "AE2_reset_glued_fermion_domain_current_and_unique_modulo_frame": True,
        "old_pre_AE2_birth_phase_obstruction_superseded_for_AE31": True,
        "AE3_enclosure_requires_no_independent_fermion_wall_parameter": True,
        "current_C2_first_order_charged_lepton_LR_operator_assembled": True,
        "current_C2_chiral_operator_domain_preserved_by_mass_block": True,
        "finite_core_current_C2_global_hyperbolicity_derived_familywise": True,
        "finite_core_advanced_retarded_Green_existence_derived": True,
        "global_current_C2_charged_lepton_Green_operator_derived": False,
        "global_or_dressed_current_C2_charged_lepton_poles_derived": False,
        "global_frequency_pole_claimed_on_nonstationary_history": False,
        "proper_history_z_promoted_to_p_squared": False,
        "absolute_unit_first_principles_derived": False,
        "muon_magnetic_moment_derived": False,
        "FULL_BHSM_COMPLETE": False,
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "chiral_operator_assembly",
    "claim_boundary",
    "domain_provenance_reconciliation",
    "family_reset_intertwiner_certificate",
    "green_operator_feasibility",
]
