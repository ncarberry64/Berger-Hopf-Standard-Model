"""Select the future-collapse relative-boundary domain for AE4.

The complete parent+child action remains a closed variational system.  After
the future child is eliminated, the parent sees the retarded Schur complement
of the child block.  This is not the reciprocal reflected cap rejected in
AE3.1 and it is not the reset graph by itself.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from bhsm.interface.ae31_c2_outer_calderon_action_no_go import (
    claim_boundary as ae31_outer_claims,
)
from bhsm.interface.ae4_stratified_dirac_zeta_induced_owner import (
    ACTION_VERSION,
    forward_time_domain_contract,
    native_spectral_length_contract,
)
from bhsm.interface.action_extension_ae2_nonfermion_threshold import (
    seam_wronskian_lower,
)


CLASSIFICATION = "AE4_FUTURE_COLLAPSE_RELATIVE_BOUNDARY_DOMAIN"
CERTIFIED_CHILD_CORE_IMPEDANCE_LOWER = 6.37052204298831e-8


def _square(value: np.ndarray, name: str) -> np.ndarray:
    matrix = np.asarray(value, dtype=complex)
    if (
        matrix.ndim != 2
        or matrix.shape[0] != matrix.shape[1]
        or not np.all(np.isfinite(matrix))
    ):
        raise ValueError(f"{name} must be a finite square matrix")
    return matrix


def retarded_child_schur_complement(
    parent_block: np.ndarray,
    parent_child_coupling: np.ndarray,
    child_retarded_block: np.ndarray,
) -> dict[str, Any]:
    """Eliminate the future child with its retarded inverse.

    ``H_eff^R=H_pp-H_pc (H_cc^R)^(-1) H_cp`` with
    ``H_cp=H_pc^dagger``.  If ``Im H_cc^R`` is positive semidefinite, then
    ``Im H_eff^R`` is positive semidefinite.  The returned identity is the
    finite-dimensional retained-mode form of causal/passive reduction.
    """

    parent = _square(parent_block, "parent_block")
    child = _square(child_retarded_block, "child_retarded_block")
    coupling = np.asarray(parent_child_coupling, dtype=complex)
    if (
        coupling.shape != (parent.shape[0], child.shape[0])
        or not np.all(np.isfinite(coupling))
    ):
        raise ValueError("coupling must map child boundary data to parent data")
    if not np.allclose(parent, parent.conj().T, rtol=0.0, atol=1.0e-11):
        raise ValueError("parent block must be Hermitian")
    inverse = np.linalg.inv(child)
    effective = parent - coupling @ inverse @ coupling.conj().T
    child_imaginary = (child - child.conj().T) / (2.0j)
    effective_imaginary = (effective - effective.conj().T) / (2.0j)
    expected_imaginary = (
        coupling
        @ inverse.conj().T
        @ child_imaginary
        @ inverse
        @ coupling.conj().T
    )
    identity_residual = float(np.linalg.norm(effective_imaginary - expected_imaginary))
    child_minimum = float(np.min(np.linalg.eigvalsh(child_imaginary)))
    effective_minimum = float(np.min(np.linalg.eigvalsh(effective_imaginary)))
    return {
        "effective_retarded_parent_block": effective,
        "child_imaginary_part": child_imaginary,
        "effective_imaginary_part": effective_imaginary,
        "causal_dissipation_identity_residual": identity_residual,
        "child_retarded_imaginary_part_positive_semidefinite": child_minimum >= -1.0e-11,
        "effective_retarded_imaginary_part_positive_semidefinite": effective_minimum >= -1.0e-11,
        "full_parent_child_action_block_replaced_by_fitted_boundary_term": False,
        "explicit_child_inverse_formed_for_theorem_witness": True,
        "physical_continuum_evaluation_requires_resolvent_not_explicit_inverse": True,
    }


def future_collapse_domain_contract() -> dict[str, Any]:
    """Select the causal domain class implied by the owner decision."""

    outer = ae31_outer_claims()
    time = forward_time_domain_contract()
    scale = native_spectral_length_contract()
    return {
        "action_version": ACTION_VERSION,
        "trace_space": (
            "T_parent_direct_sum_T_child_FOR_coexact_gauge_constraint_ghost_"
            "spinor_family_HS_scalar_and_metric_blocks"
        ),
        "collapse_surface": scale["surface_rule"],
        "physical_frequency_boundary_value": "omega_to_omega+i0_FROM_Im_omega>0",
        "child_condition": "FUTURE_RETARDED_REGULARITY_OR_OUTGOING_SUPPORT_ONLY",
        "parent_effective_operator": "H_pp-H_pc*(H_cc^R)^(-1)*H_cp",
        "complete_closed_system_variation_retained": True,
        "reduced_parent_response_may_be_dissipative": True,
        "advanced_child_to_parent_physical_propagation_allowed": False,
        "reciprocal_reflected_cap_selected": False,
        "static_reset_graph_used_as_outer_state_selector": False,
        "reset_graph_role": "TRACE_AND_VARIATION_IDENTIFICATION_AT_PARENT_CHILD_BIRTH",
        "same_retarded_boundary_value_for_BRST_partner_and_ghost": True,
        "AE31_outer_no_go_reused": outer[
            "CURRENT_AE31_RETAINED_ACTION_OUTER_CALDERON_COMPLETION_NO_GO_DERIVED"
        ],
        "future_time_rule_reused": time["retarded_domain_required"],
        "new_boundary_coefficient_inserted": False,
    }


def recovered_child_correspondence_assets() -> dict[str, Any]:
    """Attach the full later child chain instead of restarting at v17.84."""

    zero_threshold = seam_wronskian_lower(
        0.0, CERTIFIED_CHILD_CORE_IMPEDANCE_LOWER, 0.0
    )
    return {
        "v17_84_boundary_relation": (
            "F_child=P_coker(D_Phi(E_child,B_child))*"
            "(Gamma1_event+Gamma1_child+W_phys*Gamma0_event)"
        ),
        "v17_84_first_variation_and_F_child_formula_reused": True,
        "v17_86_metric_lapse_finite_chart_slice_evaluated": True,
        "v17_86_metric_lapse_F_child_norm": 127.161505414014,
        "v17_86_static_spatial_child_BVP_closed": False,
        "v17_86_interpretation": (
            "FINITE_CHART_DTN_MISMATCH_RECLASSIFIES_STATIC_SLICE;_IT_DOES_"
            "NOT_REFUTE_THE_LORENTZIAN_NONEQUILIBRIUM_CHILD"
        ),
        "v17_87_particle_definition": (
            "COMPLETE_RECONSTRUCTED_ENCAPSULATED_PERSISTENT_NONEQUILIBRIUM_CHILD"
        ),
        "v17_87_decay_definition": (
            "tau_decay=inf{tau>0:z_child(tau)_notin_B_child}"
        ),
        "v17_88_to_v17_98_retained_boundary_map_closed": True,
        "v17_98_closed_retained_blocks": [
            "LORENTZIAN_DYNAMIC_WENTZELL_CAUCHY_LAW",
            "ATTACHMENT_INCIDENCE_MOMENTUM_FORCE_AND_TWO_SIDED_FLUX",
            "GRAVITY_ETA_SCALAR_BOUNDARY_SOLUTION",
            "ZERO_BACKGROUND_GAUGE_SPINOR_GHOST_HS_MATCH",
            "DISCRETE_FIREWALL_CORE_OWNERSHIP",
        ],
        "v17_99_positive_duration_complete_child_persistence_validated": True,
        "v21_35_exact_attachment_complete_persistent_orders": [3, 4, 5, 6],
        "v21_35_fixed_background_linear_Calderon_graph_convergence_derived": True,
        "v21_35_weak_bulk_constraint_tail_decay_validated": True,
        "v21_35_N_minus_2_product_bulk_shell_bound_derived": True,
        "v21_35_asymptotic_high_shell_inverse_derived": True,
        "N12_complete_persistent_child_derived": True,
        "N12_continuum_event_child_certified": True,
        "N12_local_singular_hitting_reset_relation_certified": True,
        "N12_physical_time_orientation": "ONE_FORWARD",
        "N12_global_forward_terminal_chart_reachability_derived": False,
        "AE2_nonfermion_child_core_impedance_lower": zero_threshold,
        "AE2_zero_threshold_nonfermion_resonance_excluded": zero_threshold > 0.0,
        "actual_remaining_domain_puzzle_objects": [
            (
                "NONZERO_AE4_STRATIFIED_GAUGE_SPINOR_GHOST_HS_"
                "FLUCTUATION_CALDERON_BLOCKS_ON_THE_RESET_GLUED_MAXIMAL_"
                "HISTORY_DOMAIN"
            ),
            (
                "ACTION_OWNED_COMPACT_FORWARD_TRAPPING_OR_COMPONENT_"
                "RESTRICTED_INTEGRATED_EVENT_TRANSPORT_ESTIMATE_OR_FIRST_"
                "EXISTING_PHYSICAL_DOMAIN_EXIT"
            ),
        ],
        "global_forward_reachability_is_required_to_reopen_local_enclosure": False,
        "global_forward_reachability_role": (
            "PARALLEL_Q_XI_PARENT_RELATIVE_ENERGY_AND_GLOBAL_READOUT_DOMAIN"
        ),
        "five_v17_84_era_missing_block_list_is_current": False,
        "complete_child_calculation_restarted": False,
    }


def reflection_no_go_resolution() -> dict[str, Any]:
    return {
        "AE31_assumption": (
            "N_child=U_reset*N_parent*U_reset_dagger_ON_A_RECIPROCAL_REFLECTED_CAP"
        ),
        "AE4_replacement": (
            "N_child^R_IS_THE_RETURNED_FUTURE_CHILD_IMPEDANCE_DERIVED_FROM_"
            "THE_SAME_STRATIFIED_ACTION"
        ),
        "reflection_identity_retained_as_AE4_domain_identity": False,
        "AE31_no_go_contradicted": False,
        "AE31_no_go_scope_bypassed_by_new_action_domain": True,
        "noncommon_gauge_response_kinematically_available": True,
        "required_Maxwell_residue_difference_numerically_derived_here": False,
        "why_not_yet": (
            "THE_CURRENT_C2_FUTURE_CHILD_OPERATOR_AND_IMPEDANCE_CROSSING_HAVE_"
            "NOT_YET_BEEN_EVALUATED"
        ),
    }


def claim_boundary() -> dict[str, Any]:
    return {
        "AE4_FUTURE_COLLAPSE_RELATIVE_BOUNDARY_DOMAIN_CLASS_SELECTED": True,
        "AE4_RETARDED_CHILD_SCHUR_COMPLEMENT_DERIVED": True,
        "AE4_RETARDED_PASSIVITY_IDENTITY_DERIVED": True,
        "AE4_RECIPROCAL_REFLECTION_DOMAIN_REJECTED": True,
        "AE4_V17_84_EVENT_CHILD_CANONICAL_RELATION_REUSED": True,
        "AE4_V17_86_METRIC_LAPSE_FINITE_CHART_SLICE_REUSED": True,
        "AE4_V17_87_PERSISTENT_NONEQUILIBRIUM_CHILD_REUSED": True,
        "AE4_V17_98_RETAINED_EVENT_CHILD_BOUNDARY_MAP_REUSED_AS_CLOSED": True,
        "AE4_V17_99_POSITIVE_DURATION_CHILD_REUSED": True,
        "AE4_V21_35_N3_TO_N6_COMPLETE_PERSISTENT_CHILDREN_REUSED": True,
        "AE4_V21_35_ASYMPTOTIC_HIGH_SHELL_INVERSE_REUSED": True,
        "AE4_N12_CONTINUUM_EVENT_CHILD_CERTIFICATE_REUSED": True,
        "AE4_N12_LOCAL_SINGULAR_HITTING_RESET_RELATION_REUSED": True,
        "AE4_N12_ONE_FORWARD_TIME_ORIENTATION_REUSED": True,
        "AE4_NONFERMION_ZERO_THRESHOLD_MARGIN_REUSED": True,
        "AE4_FINITE_N6_TO_M0_NORMAL_SCHUR_BRIDGE_CERTIFIED": True,
        "AE4_GLOBAL_FORWARD_TERMINAL_CHART_REACHABILITY_DERIVED": False,
        "AE4_CURRENT_C2_FUTURE_CHILD_BLOCK_EVALUATED": False,
        "AE4_COMPLETE_BRST_CALDERON_PROJECTOR_EVALUATED": False,
        "CURRENT_C2_LORENTZIAN_MAXWELL_RESIDUE_DERIVED": False,
        "CURRENT_C2_ACTION_SELECTED_HADAMARD_STATE_DERIVED": False,
        "FULL_BHSM_COMPLETE": False,
        "exact_next_calculation": (
            "REALIZE_THE_NONZERO_AE4_STRATIFIED_GAUGE_GHOST_FERMION_HS_"
            "SOURCE_RESPONSE_BLOCKS_ON_THE_RESET_GLUED_MAXIMAL_HISTORY_"
            "DOMAIN_AND_EVALUATE_THE_EVENT_CANONICAL_FLUX_AND_COMPLETE_"
            "NOETHER_HAMILTONIAN_BALANCE;_IN_PARALLEL_DERIVE_FORWARD_"
            "REACHABILITY_FOR_Q_XI_AND_PARENT_RELATIVE_ENERGY"
        ),
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "claim_boundary",
    "future_collapse_domain_contract",
    "reflection_no_go_resolution",
    "recovered_child_correspondence_assets",
    "retarded_child_schur_complement",
]
