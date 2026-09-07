"""Adjudicate the BHSM boundary-improved event/envelopment charge map.

The current registered object is a stratified action complex, not a single
closed parent action on one event--child moving-boundary domain.  This module
therefore records the maximal sectorwise presymplectic data and stops at the
first charge-theoretic obstruction: no common action-owned generator is a
tangent vector of the active full-field reset domain.  It does not import a
generic GR charge, select a reference, or manufacture an energy ratio.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable

from bhsm.interface.action_extension_global_spin_reset_ae2 import action_definition
from bhsm.interface.ae3_reciprocal_join_localization import interface_variation_ledger
from bhsm.interface.ae4_future_collapse_relative_boundary_domain import (
    future_collapse_domain_contract,
)
from bhsm.interface.completion.boundary_variational_domain_v11_2 import (
    boundary_payload as support_boundary_payload,
)
from bhsm.interface.completion.support_covariant_phase_space_v11_2 import (
    phase_space_payload,
)
from bhsm.interface.master_action.terms import term_rows
from bhsm.interface.nonfermion_relative_boundary_variation import (
    canonical_boundary_variables,
)
from bhsm.interface.relative_diffeomorphism_generator_charge_adjudication import (
    EXACT_NEXT_OBJECT as MOVING_GRAPH_BLOCKER,
    candidate_relative_generator,
    differentiability_and_charge_verdict,
    presymplectic_potential_inventory,
)


ACTION_VERSION = "BHSM-AE-3.2.13-BOUNDARY-IMPROVED-CHARGE-MAP-ADJUDICATION"
CLASSIFICATION = "BOUNDARY_IMPROVED_EVENT_MODE_AND_ENVELOPMENT_CHARGE_MAP_OBSTRUCTION"
XI_CLASS = "XI5"
CHG_CLASS = "CHG4"
REF_CLASS = "REF5"
MODEE_CLASS = "MODEE5"
ENVH_CLASS = "ENVH5"
DOMH_CLASS = "DOMH4"
AE4R_CLASS = "AE4R5"
EXACT_NEXT_OBJECT = MOVING_GRAPH_BLOCKER


@dataclass(frozen=True)
class ThetaSectorRow:
    """One levelwise contribution to the formal boundary potential."""

    sector: str
    action_source: str
    theta_contribution: str
    boundary_term: str
    corner_term: str
    owned: str
    common_event_child_domain: bool
    charge_assembler_available: bool


def registered_action_status() -> dict[str, Any]:
    """Return the charge-relevant status of the registered action complex."""

    terms = term_rows()
    return {
        "registered_object": (
            "S8 -> S5|4(caps+GHY+B1+matcher) -> S4eff stratified action complex"
        ),
        "registered_term_count": len(terms),
        "registered_term_ids": [row["term_id"] for row in terms],
        "single_closed_parent_action": False,
        "reduction_maps_R8_to_5_and_R5_to_4_owned": False,
        "single_full_field_moving_event_child_domain": False,
        "consequence": (
            "levelwise variations may be inventoried, but they cannot be summed "
            "as one covariant presymplectic potential on the requested charge domain"
        ),
    }


def sector_contribution_ledger() -> list[dict[str, Any]]:
    """Return the maximal coefficient-matched sectorwise Theta ledger."""

    canonical = canonical_boundary_variables()
    phase = phase_space_payload()
    ae2 = action_definition()
    ae3 = interface_variation_ledger()
    ae4 = future_collapse_domain_contract()
    rows: Iterable[ThetaSectorRow] = (
        ThetaSectorRow(
            "geometry_EH_GHY",
            "T8_EH and T5_caps plus coefficient-locked T5_GHY (kappa1)",
            (
                "levelwise Einstein-Hilbert potential completed on each declared "
                "regular Dirichlet cap by the Brown-York/GHY canonical metric pair"
            ),
            "GHY cancels normal derivatives of delta g and leaves canonical metric momentum",
            "Hayward area/relative-angle pair only on the separately declared moving geometric interface",
            "OWNED_LEVELWISE_ON_DECLARED_REGULAR_CAPS",
            False,
            False,
        ),
        ThetaSectorRow(
            "carrier_and_scalar_topographic",
            "T8_carrier, T8_scalar, T5_caps scalar, T4_scalar, and regular q_D support action",
            (
                "Theta_chi^A=-sqrt(-G) Zchi(1+g sigma^2) nabla^A chi delta chi; "
                "Theta_sigma^A=-sqrt(-G) Zsigma nabla^A sigma delta sigma; "
                + phase["known_symplectic_potential"]
            ),
            "normal scalar Legendre/Green terms; Dirichlet or Neumann requires a selected ensemble",
            "none action-owned for the full reset",
            "OWNED_SECTORWISE;_SUPPORT_ACTION_AND_COMPLETE_ENSEMBLE_OPEN",
            False,
            False,
        ),
        ThetaSectorRow(
            "Maxwell_and_gauge",
            "T4_gauge with coefficients 1/g_i^2",
            canonical["gauge"]["green_form"],
            canonical["gauge"]["canonical_momentum"],
            "none",
            "OWNED_EFT_GREEN_FORM;_ABSOLUTE_OR_RELATIVE_DOMAIN_IS_INPUT",
            False,
            False,
        ),
        ThetaSectorRow(
            "fermion",
            "symmetrized T4_fermion extended by BHSM-AE-2.0.0",
            "first-order Dirac Green potential/pairing on the AE2 maximal-isotropic trace graph",
            ae2["independent_normal_matter_boundary_action"],
            "none",
            "OWNED_AE2_SPIN_GAUGE_TRACE_DOMAIN_ONLY",
            False,
            False,
        ),
        ThetaSectorRow(
            "ghost_BRST",
            "conditional AE3/AE4 gauge-fixed Hessian and FP symbol",
            canonical["ghost"]["green_form"],
            canonical["ghost"]["canonical_momenta"],
            "none",
            "OWNED_AS_SECTORWISE_GREEN_FORM_NOT_AS_COMPLETE_PARENT_ACTION_TERM",
            False,
            False,
        ),
        ThetaSectorRow(
            "higher_spin_HS",
            "bare algebraic Einstein-Cartan/Hubbard-Stratonovich block",
            canonical["HS"]["green_form"],
            canonical["HS"]["canonical_momentum"],
            "none",
            "OWNED_RANK_ZERO_NORMAL_LEGENDRE_MAP;_TRACE_INCIDENCE_OPEN",
            False,
            False,
        ),
        ThetaSectorRow(
            "finite_N12_canonical",
            "constraint-reduced N12 Galerkin action",
            "Theta_N12=p_I delta q^I on its fixed finite history chart",
            "canonical endpoint pair only",
            "none",
            "OWNED_REDUCED_CHART_BUT_NOT_A_COVARIANT_FULL_FIELD_BOUNDARY_CHARGE",
            False,
            False,
        ),
        ThetaSectorRow(
            "AE3_local_sigma_zero_interface",
            "coefficient-free reciprocal-join localization extension",
            "opposite-normal same-action sector potentials cancel across the smooth internal material level set",
            ae3["brown_york"],
            "none",
            "OWNED_LOCAL_MATERIAL_INTERFACE_NOT_TERMINAL_EVENT_CHILD_BOUNDARY",
            False,
            False,
        ),
        ThetaSectorRow(
            "AE4_future_retarded_domain",
            "future child retarded Schur-complement domain",
            "no new covariant Theta; retarded boundary value constrains the child response domain",
            "no new boundary counterterm",
            "none",
            (
                "OWNED_CAUSAL_DOMAIN_CLASS;_CURRENT_C2_CHILD_BLOCK_AND_COMPLETE_"
                "BRST_CALDERON_PROJECTOR_UNEVALUATED"
            ),
            False,
            False,
        ),
    )
    assert ae4["complete_closed_system_variation_retained"]
    return [asdict(row) for row in rows]


def complete_presymplectic_potential_status() -> dict[str, Any]:
    """Give the maximal formal sum and explain why it is not a Theta."""

    inventory = presymplectic_potential_inventory()
    return {
        "formal_only_expression": (
            "Theta_formal=Theta_EH+GHY + Theta_chi,sigma,qD,H + Theta_YM + "
            "Theta_Dirac + Theta_FP + Theta_N12 + Theta_HS"
        ),
        "complete_Theta_event": inventory["complete_Theta_event"],
        "complete_Theta_child": inventory["complete_Theta_child"],
        "complete_relative_Theta": inventory["complete_relative_Theta"],
        "complete_boundary_presymplectic_potential_derived": False,
        "why_formal_sum_is_not_promoted": [
            "terms live at different strata and on different declared domains",
            "the reduction maps joining S8, S5|4, and S4eff are not owned",
            "the full-field F_B-dependent moving trace graph and its first variation are absent",
            "the complete reset polarization/ensemble is absent",
        ],
        "first_obstruction": EXACT_NEXT_OBJECT,
    }


def generator_adjudication() -> dict[str, Any]:
    """Classify the common physical generator as XI5."""

    relative = candidate_relative_generator()
    return {
        "classification": XI_CLASS,
        "common_action_owned_generator": None,
        "candidate_event_evolution_vector": "WITHIN_SIDE_FLOW_ONLY_NOT_A_COMMON_BOUNDARY_GENERATOR",
        "candidate_retarded_time_flow": "CAUSAL_BOUNDARY_VALUE_PRESCRIPTION_NOT_A_HAMILTONIAN_SYMMETRY",
        "candidate_boundary_time_translation": "NO_SELECTED_BOUNDARY_TIME_TRANSLATION",
        "candidate_Killing_field": "NO_COMMON_KILLING_FIELD_ASSUMED_OR_DERIVED",
        "candidate_event_mode_generator": "ORDERED_EVENT_EIGENLINE_IS_NOT_A_SPACETIME_VECTOR_FIELD",
        "candidate_Hopf_generator": "BULK_SPATIAL_ROTOR_NOT_IDENTIFIED_WITH_ATTACHMENT_TIME_FLOW",
        "formal_two_sided_vector": "delta_F=xi_child o F-F_*xi_event",
        "tangent_to_active_domain": relative[
            "delta_xi_rel_is_a_vector_field_on_current_reset_domain"
        ],
        "reason": (
            "no F_B-dependent full-field trace graph exists on which event and "
            "child vectors could define one tangent symmetry generator"
        ),
        "stop_charge_comparison_here": True,
    }


def differentiability_integrability_status() -> dict[str, Any]:
    """Map the existing G4 theorem to the requested CHG classification."""

    old = differentiability_and_charge_verdict()
    return {
        "classification": CHG_CLASS,
        "prior_classification": old["differentiability_class"],
        "formal_variation": (
            "delta H_xi=sum_s[C_s[xi_s]+integral(delta Q_xi_s-i_xi_s Theta_s)]"
            "-delta B_xi"
        ),
        "functional_differential_exists_on_current_domain": False,
        "integrability_test_reached": False,
        "required_improvement_B_xi": None,
        "B_xi_is_zero": None,
        "why": old["G4_reason"],
        "later_CHG3_possible_after_domain_completion": True,
        "no_numerical_charge_may_be_assigned": True,
    }


def reference_status() -> dict[str, Any]:
    """Classify the common event/child zero point as REF5."""

    support = support_boundary_payload()
    return {
        "classification": REF_CLASS,
        "usable_common_reference": None,
        "Brown_York_reference": None,
        "cap_reference_geometry": None,
        "vacuum_subtraction": None,
        "seam_reference": None,
        "environment_reference": None,
        "normalization_inherited_from_action": (
            "EH/GHY coefficients and orientations only; they do not select a zero point"
        ),
        "selected_boundary_ensemble": support["selected_scalar_ensemble"],
        "complete_boundary_counterterm": support["complete_boundary_counterterm"],
        "reference_ambiguity_not_reached_as_a_charge_ambiguity": True,
        "reason": (
            "no differentiable common charge exists to which a subtraction could "
            "be applied, and BHSM owns no matched event/child reference prescription"
        ),
    }


def event_and_mode_charge_status() -> dict[str, Any]:
    """Adjudicate the event total, projector, and initiating-mode charge."""

    return {
        "total_event_charge_H_xi_event": None,
        "finite": None,
        "integrable": False,
        "gauge_reduced": False,
        "constraint_compatible": None,
        "reference_consistent": False,
        "initiating_mode_projector_P_mode": None,
        "mode_classification": MODEE_CLASS,
        "initiating_mode_charge_H_xi_mode": None,
        "quadratic_mode_energy_separable": None,
        "interaction_cross_terms": "UNALLOCATABLE_WITHOUT_A_PHYSICAL_PROJECTOR_AND_NONLINEAR_CHARGE",
        "frozen_family_projectors_are_P_mode": False,
        "N12_ordered_event_eigenline_is_P_mode": False,
    }


def retained_outgoing_other_ledger() -> list[dict[str, str]]:
    """Record required accounting slots without asserting a subtraction law."""

    return [
        {"slot": "retained_parent_environment", "charge": "UNDEFINED", "status": "NO_COMMON_H_xi"},
        {"slot": "persistent_modes", "charge": "UNDEFINED", "status": "MODE_PROJECTOR_OPEN"},
        {"slot": "outgoing_flux", "charge": "SECTORWISE_FLUX_FORMS_ONLY", "status": "NO_COMPLETE_ORIENTED_CHARGE"},
        {"slot": "other_constraints", "charge": "HAMILTONIAN_MOMENTUM_GAUSS_CONSTRAINTS_SECTORWISE", "status": "NOT_AN_AVAILABLE_ENERGY_SUBTRACTION"},
        {"slot": "independent_children", "charge": "UNDEFINED", "status": "NO_ACTION_OWNED_BRANCHING_INCIDENCE"},
    ]


def available_charge_status() -> dict[str, Any]:
    return {
        "symbol": "H_xi,mode^avail",
        "value": None,
        "definition_earned": False,
        "candidate_subtraction_formula_adopted": False,
        "blocked_by": [XI_CLASS, CHG_CLASS, REF_CLASS, MODEE_CLASS],
        "owner_conservation_firewall_retained": True,
    }


def child_seam_and_increment_status() -> dict[str, Any]:
    return {
        "H_xi_child_plus_seam": None,
        "geometric_contribution": None,
        "GHY_corner_contribution": None,
        "matter_contribution": None,
        "gauge_contribution": None,
        "scalar_topographic_contribution": None,
        "seam_environment_contribution": None,
        "constraint_contribution": None,
        "reference_subtraction": None,
        "Delta_H_xi_child_plus_seam": None,
        "classification": ENVH_CLASS,
        "path_independence": None,
        "carrier_dependence": "UNEVALUABLE",
        "ensemble_dependence": "UNEVALUABLE",
        "reference_dependence": "UNEVALUABLE",
        "topology_dependence": "UNEVALUABLE",
    }


def common_domain_status() -> dict[str, Any]:
    return {
        "classification": DOMH_CLASS,
        "D_H": None,
        "carrier_compatible": False,
        "common_generator": False,
        "common_ensemble": False,
        "common_reference": False,
        "orientation_and_corner_conventions": "OWNED_ONLY_SECTORWISE",
        "full_gauge_reduction": False,
        "regularity": "LOCAL_REGULAR_DOMAINS_ONLY",
        "causal_orientation": "ONE_FORWARD_AND_AE4_RETARDED_CLASS_OWNED_BUT_INSUFFICIENT",
        "sectorwise_domains_exist": True,
        "why_not_DOMH2": (
            "sectorwise domains do not host the two requested comparable full charges"
        ),
    }


def ae4_impedance_and_crossing_status() -> dict[str, Any]:
    return {
        "classification": AE4R_CLASS,
        "historical_E_mode_identified_with_H_xi_mode_avail": False,
        "historical_E_impedance_identified_with_Delta_H_xi_child_plus_seam": False,
        "rho_hold_modern_value": None,
        "rho_hold_status": "UNEVALUABLE_NOT_A_RATIO_OF_CURRENT_CHARGES",
        "first_future_crossing_function": None,
        "crossing_domain": None,
        "existence": None,
        "uniqueness": None,
        "equality_is_saturation": False,
        "root_search_performed": False,
        "historical_rule_status": "ARCHITECTURAL_HYPOTHESIS_ONLY",
    }


def conservation_and_branching_status() -> dict[str, Any]:
    return {
        "no_ex_nihilo_rule": "VALIDATED_AS_A_FIREWALL_NOT_EVALUATED_AS_A_LEDGER",
        "proposed_child_charge_tests_completed": 0,
        "charge_supported_child_found": None,
        "charge_inadmissible_child_found": None,
        "numerical_nonconvergence_relabelled_physical_inadmissibility": False,
        "excess_charge_enlarges_primary_child_automatically": False,
        "multiple_children_forced_by_charge_analysis": False,
        "generic_1_to_n_machinery_used_to_invent_channels": False,
    }


def n12_rank_status() -> dict[str, Any]:
    return {
        "charge_equations_actually_derived": 0,
        "actual_new_independent_rank": 0,
        "residual_before_time_quotient": 67,
        "residual_after_time_quotient": 66,
    }


def claim_boundary() -> dict[str, bool]:
    return {
        "COMPLETE_BOUNDARY_PRESYMPLECTIC_POTENTIAL_DERIVED": False,
        "SECTORWISE_BOUNDARY_VARIATION_LEDGER_COMPLETED": True,
        "COMMON_ACTION_OWNED_XI_DERIVED": False,
        "DIFFERENTIABLE_OR_INTEGRABLE_H_XI_DERIVED": False,
        "BOUNDARY_IMPROVEMENT_B_XI_SELECTED": False,
        "COMMON_REFERENCE_SELECTED": False,
        "TOTAL_EVENT_CHARGE_DERIVED": False,
        "PHYSICAL_INITIATING_MODE_PROJECTOR_DERIVED": False,
        "H_XI_MODE_AVAILABLE_DERIVED": False,
        "H_XI_CHILD_PLUS_SEAM_DERIVED": False,
        "DELTA_H_XI_CHILD_PLUS_SEAM_DERIVED": False,
        "COMMON_CHARGE_DOMAIN_DERIVED": False,
        "RHO_HOLD_MODERNIZED_AND_EVALUABLE": False,
        "FIRST_FUTURE_CROSSING_EQUATION_DERIVED": False,
        "MULTIPLE_CHILDREN_FORCED": False,
        "N12_RANK_CHANGED": False,
        "RESPONSE_FUNCTION_SELECTED": False,
        "FROZEN_PREDICTIONS_CHANGED": False,
        "GATE7_PROMOTED": False,
        "FULL_BHSM_COMPLETE": False,
    }


def exact_next_object() -> dict[str, Any]:
    return {
        "object": EXACT_NEXT_OBJECT,
        "charge_theoretic_role": (
            "make a common event/child vector tangent to one full-field moving "
            "trace domain before Theta, Q_xi, B_xi, and reference tests"
        ),
        "must_supply": [
            "F_B as an action configuration argument",
            "sectorwise spatial pullbacks for every participating trace",
            "first moving-domain variation D_F Graph(R_F)[delta F]",
            "one common boundary polarization candidate",
        ],
        "not_authorized": "choosing an arbitrary reset graph or reference by convenience",
    }


def adjudication_payload() -> dict[str, Any]:
    return {
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "registered_action": registered_action_status(),
        "complete_presymplectic_potential": complete_presymplectic_potential_status(),
        "sector_contribution_ledger": sector_contribution_ledger(),
        "generator": generator_adjudication(),
        "charge_differentiability_integrability": differentiability_integrability_status(),
        "reference": reference_status(),
        "event_and_mode_charge": event_and_mode_charge_status(),
        "retained_outgoing_other_charge_ledger": retained_outgoing_other_ledger(),
        "available_charge": available_charge_status(),
        "child_seam_and_increment": child_seam_and_increment_status(),
        "common_domain": common_domain_status(),
        "AE4_impedance_and_crossing": ae4_impedance_and_crossing_status(),
        "conservation_and_branching": conservation_and_branching_status(),
        "N12_rank": n12_rank_status(),
        "claim_boundary": claim_boundary(),
        "exact_next_object": exact_next_object(),
    }


__all__ = [
    "ACTION_VERSION",
    "AE4R_CLASS",
    "CHG_CLASS",
    "CLASSIFICATION",
    "DOMH_CLASS",
    "ENVH_CLASS",
    "EXACT_NEXT_OBJECT",
    "MODEE_CLASS",
    "REF_CLASS",
    "XI_CLASS",
    "adjudication_payload",
    "ae4_impedance_and_crossing_status",
    "available_charge_status",
    "child_seam_and_increment_status",
    "claim_boundary",
    "common_domain_status",
    "complete_presymplectic_potential_status",
    "conservation_and_branching_status",
    "differentiability_integrability_status",
    "event_and_mode_charge_status",
    "exact_next_object",
    "generator_adjudication",
    "n12_rank_status",
    "reference_status",
    "registered_action_status",
    "retained_outgoing_other_ledger",
    "sector_contribution_ledger",
]
