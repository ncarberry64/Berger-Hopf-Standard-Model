"""Select the AE4 stratified Dirac--zeta induced-action owner.

The owner decision removes the v14.63 generic cutoff-profile fork.  The
microscopic functional is the proper-time integral of the canonical heat
semigroup, completed by the relative zeta/eta prescription at logarithmic
order.  Existing M8/M5/M4 local actions are consequently expansions of one
functional, not independently normalized Wilson sectors.

This module derives the positive-order heat moments of the retained
``-E1(ell^2 P)/2`` regulator.  It does not pretend that the still-missing
global self-adjoint stratified operator/domain has been constructed.
"""

from __future__ import annotations

import math
from typing import Any


ACTION_VERSION = "BHSM-AE-4.0.0"
PREDECESSOR_ACTION_VERSION = "BHSM-AE-3.1.0"
CLASSIFICATION = "AE4_STRATIFIED_DIRAC_ZETA_INDUCED_ACTION_OWNER_SELECTED"
RELEVANT_MOMENT_ORDERS = (8, 6, 5, 4, 3, 2)


def _positive_finite(value: float, name: str) -> float:
    result = float(value)
    if not math.isfinite(result) or result <= 0.0:
        raise ValueError(f"{name} must be positive and finite")
    return result


def proper_time_moment(order: int, spectral_length: float = 1.0) -> float:
    """Return the normalized positive-order moment of ``-E1(ell^2 u)/2``.

    For ``p>0`` and ``a=p/2``, Tonelli/Fubini on the positive ``E1`` kernel
    gives

    ``int_0^inf E1(ell^2 u) u^(a-1) du = Gamma(a)/(a ell^(2a))``.

    Hence the normalized spectral-action moment is
    ``F_p=-ell^(-p)/p``.  The ``p=0`` term is logarithmic and belongs to the
    relative zeta/eta completion rather than this positive-order formula.
    """

    p = int(order)
    ell = _positive_finite(spectral_length, "spectral_length")
    if p <= 0:
        raise ValueError("positive order required; order zero is zeta/logarithmic")
    return -(ell ** (-p)) / p


def proper_time_moment_ratio(
    numerator_order: int,
    denominator_order: int,
    spectral_length: float = 1.0,
) -> float:
    """Return the exact one-scale ratio ``F_p/F_q``."""

    p = int(numerator_order)
    q = int(denominator_order)
    ell = _positive_finite(spectral_length, "spectral_length")
    if p <= 0 or q <= 0:
        raise ValueError("positive orders required")
    return (q / p) * ell ** (q - p)


def native_spectral_length_contract() -> dict[str, Any]:
    """Bind the sole spectral length to the BHSM collapse surface.

    The rule is an owner selection, not a numerical evaluation.  In natural
    units the length is the inverse of the action-derived impedance energy at
    the first future surface where exterior spacetime support reaches the core
    threshold.  No astrophysical or particle datum is used to set it.
    """

    return {
        "surface_rule": (
            "Sigma_star=FIRST_FUTURE_SURFACE_WHERE_"
            "E_impedance[Phi;Sigma]=E_core[Phi;Sigma]_AND_OUTWARD_"
            "SPACETIME_SUPPORT_CEASES"
        ),
        "spectral_length_rule_natural_units": (
            "ell_star=1/E_impedance[Phi_star;Sigma_star]"
        ),
        "ell_star_is_BHSM_native_geometry_functional": True,
        "ell_star_is_free_universal_cutoff": False,
        "first_crossing_not_singular_endpoint_evaluation": True,
        "black_hole_magnetar_neutron_and_atomic_data_set_ell_star": False,
        "those_systems_are_downstream_tests_of_one_surface_rule": True,
        "numerical_ell_star_evaluated_on_current_C2": False,
    }


def forward_time_domain_contract() -> dict[str, Any]:
    """Separate forward physical evolution from heat proper time."""

    return {
        "physical_time_orientation": "FUTURE_DIRECTED_ONLY",
        "parent_child_rule": (
            "THE_PARENT_ENDPOINT_DEFINES_THE_CHILD_INITIAL_SURFACE;_NO_"
            "ADVANCED_CHILD_TO_PARENT_PHYSICAL_EVOLUTION"
        ),
        "physical_propagator_domain": "t_child>=t_parent",
        "retarded_domain_required": True,
        "periodic_cycle_surrogate_for_physical_frequency_allowed": False,
        "heat_parameter_role": "SPECTRAL_PROPER_TIME_REGULATOR_NOT_PHYSICAL_TIME",
        "heat_semigroup_conflicts_with_forward_physical_time": False,
    }


def enclosure_holding_threshold_hypothesis() -> dict[str, Any]:
    """Record the native cross-scale stability hypothesis fail-closed."""

    return {
        "dimensionless_control_candidate": (
            "rho_hold=E_mode/E_impedance[Phi;Sigma_enclosure]"
        ),
        "stable_side_candidate": "rho_hold<1",
        "first_loss_surface_candidate": "rho_hold=1",
        "atomic_decay_is_surface_holding_failure": "HYPOTHESIS_TO_DERIVE",
        "macroscopic_scale_increases_instability": "HYPOTHESIS_TO_DERIVE",
        "required_derivation": (
            "COMPUTE_THE_ACTION_HESSIAN_OR_RESONANCE_WIDTH_ACROSS_HADRONIC_"
            "NUCLEAR_ATOMIC_COMPACT_OBJECT_AND_HORIZON_ENCLOSURE_SCALES"
        ),
        "empirical_lifetime_or_compact_object_data_inserted": False,
        "physical_decay_law_derived": False,
    }


def induced_local_weight_ledger(spectral_length: float = 1.0) -> dict[str, Any]:
    """Expose the M8/M5/M4 relevant weights derived from one functional."""

    ell = _positive_finite(spectral_length, "spectral_length")
    moments = {
        f"F{order}": proper_time_moment(order, ell)
        for order in RELEVANT_MOMENT_ORDERS
    }
    return {
        "spectral_length": ell,
        "regulator": "f_ell(u)=-(1/2)E1(ell^2*u)",
        "proper_time_form": (
            "Gamma_ind=-(1/2)STr_integral_[ell^2,infinity] "
            "ds/s exp(-s*P_strat)"
        ),
        "derived_positive_order_moments": moments,
        "normalized_ell_equals_one_exact_values": {
            "F8": "-1/8",
            "F6": "-1/6",
            "F5": "-1/5",
            "F4": "-1/4",
            "F3": "-1/3",
            "F2": "-1/2",
        },
        "M8_local_terms": {
            "a0_volume": "F8*a0",
            "a2_Einstein_two_derivative": "F6*a2",
            "a4": "F4*a4",
            "a6": "F2*a6",
            "a8": "relative_zeta_log_order",
        },
        "M5_local_terms": {
            "a0_volume": "F5*a0",
            "a2_Einstein_two_derivative": "F3*a2",
            "boundary_terms": "same_proper_time_moments_on_action_domain",
            "a5": "relative_zeta_log_order",
        },
        "M4_local_terms": {
            "a0_volume": "F4*a0",
            "a2_Einstein_two_derivative": "F2*a2",
            "a4_gauge_curvature_squared": "relative_zeta_log_order",
        },
        "independent_profile_moments_remaining": 0,
        "one_common_spectral_length_remaining": True,
        "ell_equals_one_is_only_a_dimensionless_witness": ell == 1.0,
    }


def microscopic_owner_contract() -> dict[str, Any]:
    """State the selected owner without overclaiming its physical realization."""

    return {
        "action_version": ACTION_VERSION,
        "predecessor_action_version": PREDECESSOR_ACTION_VERSION,
        "owner_status": "SELECTED__GLOBAL_OPERATOR_DOMAIN_STILL_REQUIRED",
        "stratified_Hilbert_architecture": (
            "H8 direct_sum H5_plus direct_sum H5_minus direct_sum H4"
        ),
        "trace_rule": (
            "canonical_geometric_L2_direct_sum_supertrace_with_statistics_"
            "grading_and_BRST_ghost_multiplicities"
        ),
        "positive_operator": (
            "P_strat=D_strat^dagger*D_strat_on_the_zero_mode_and_BRST_quotient"
        ),
        "microscopic_functional": (
            "-(1/2)STr E1(ell_star^2*P_strat),_with_relative_zeta/eta_"
            "completion_for_logarithmic_order_and_determinant_phase"
        ),
        "zeta_completion_is_second_independent_determinant": False,
        "local_M8_M5_M4_actions_are": (
            "ASYMPTOTIC_AND_BOUNDARY_EXPANSIONS_OF_ONE_MICROSCOPIC_FUNCTIONAL"
        ),
        "independent_M8_M5_M4_Wilson_owners_retained": False,
        "independent_ZA_g_gprime_alpha_metric_cone_or_particle_fit_allowed": False,
        "measured_particle_data_used_to_select_owner": False,
        "native_spectral_length": native_spectral_length_contract(),
        "forward_time_domain": forward_time_domain_contract(),
    }


def historical_reconciliation() -> dict[str, Any]:
    """Reconcile v14.63/v14.64 with the already-retained v15.99-v16 action."""

    return {
        "v14_63_generic_profile_independence_theorem_retained": True,
        "v14_63_open_foundational_choice_now_made": True,
        "v14_64_canonical_exponential_heat_semigroup_branch_adopted": True,
        "v14_64_geometric_unweighted_direct_sum_trace_adopted": True,
        "v15_99_v16_regulator_reused": "-(1/2)E1(ell_kappa^2*P)",
        "raw_heat_trace_confused_with_integrated_determinant": False,
        "new_moment_result": (
            "THE_INTEGRATED_HEAT_OWNER_HAS_F_p=-ell_star^(-p)/p_FOR_p>0;_"
            "IT_DOES_NOT_HAVE_THE_RAW_HEAT_TRACE_MOMENTS_F_p=ell_star^(-p)"
        ),
        "v16_00_no_double_counting_rule_retained": (
            "the_old_attached_zeta_seed_is_replaced_not_added_to_the_sourced_"
            "proper_time_superdeterminant"
        ),
        "frozen_particle_family_representation_projector_current_assets_changed": False,
    }


def claim_boundary() -> dict[str, Any]:
    return {
        "AE4_STRATIFIED_DIRAC_ZETA_MICROSCOPIC_OWNER_SELECTED": True,
        "AE4_POSITIVE_ORDER_M8_M5_M4_MOMENT_RATIOS_DERIVED": True,
        "AE4_INDEPENDENT_CROSS_STRATUM_WILSON_ONTOLOGY_RETIRED": True,
        "AE4_ELL_STAR_NATIVE_COLLAPSE_SURFACE_OWNER_RULE_SELECTED": True,
        "AE4_FUTURE_DIRECTED_PARENT_CHILD_DOMAIN_SELECTED": True,
        "AE4_COMMON_SPECTRAL_LENGTH_PHYSICAL_ORIGIN_DERIVED": False,
        "AE4_CURRENT_C2_COLLAPSE_IMPEDANCE_ENERGY_EVALUATED": False,
        "AE4_GLOBAL_SELF_ADJOINT_STRATIFIED_DIRAC_DOMAIN_DERIVED": False,
        "AE4_COMPLETE_OPERATOR_VALUED_CALDERON_WENTZELL_SEAM_DERIVED": False,
        "AE4_LOG_ORDER_RELATIVE_ZETA_ETA_PHASE_EVALUATED": False,
        "AE4_FINITE_FAMILY_DIRAC_OPERATOR_EVALUATED": False,
        "AE4_PHYSICAL_M8_M5_M4_NUMERICAL_COEFFICIENTS_DERIVED": False,
        "FULL_BHSM_COMPLETE": False,
        "exact_next_calculation": (
            "CONSTRUCT_THE_GLOBAL_OPERATOR_VALUED_RELATIVE_BOUNDARY_DIRAC_DOMAIN_"
            "THEN_EVALUATE_THE_FIRST_FUTURE_CURRENT_C2_IMPEDANCE_CROSSING_"
            "TO_OBTAIN_ELL_STAR_AND_THE_STRATIFIED_HEAT_COEFFICIENTS_AND_"
            "RELATIVE_ZETA_ETA_TERMS"
        ),
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "PREDECESSOR_ACTION_VERSION",
    "RELEVANT_MOMENT_ORDERS",
    "claim_boundary",
    "enclosure_holding_threshold_hypothesis",
    "forward_time_domain_contract",
    "historical_reconciliation",
    "induced_local_weight_ledger",
    "microscopic_owner_contract",
    "native_spectral_length_contract",
    "proper_time_moment",
    "proper_time_moment_ratio",
]
