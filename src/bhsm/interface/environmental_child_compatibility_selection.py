"""Apply the recovered owner environmental-selection postulate to BHSM resets.

The postulate is pre-existing owner work newly materialized in repository
authority.  It is not a theorem of the thirteen-term action.  This module
constructs the smallest typed environmental descriptor supported by current
BHSM sources, defines a three-valued compatibility relation, and determines
how much of the conditional reset family it removes.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from bhsm.interface.ae4_future_collapse_relative_boundary_domain import (
    future_collapse_domain_contract,
)
from bhsm.interface.aether_parent_child_relative_rotor_v15_36 import (
    relative_rotor_terms,
)
from bhsm.interface.aether_reconstruction_firewall_event_v15_45 import (
    oriented_cut_and_event_data,
    reconstruction_seed,
)
from bhsm.interface.gauge_connection_reset_bundle_lift_adjudication import (
    spatial_correspondence_nonuniqueness_witness,
)
from bhsm.interface.nonfermion_relative_boundary_variation import (
    variational_selection_witness,
)
from bhsm.interface.reset_correspondence_stationarity_adjudication import (
    generator_charge_and_downstream_status,
)


ACTION_VERSION = "BHSM-AE-3.2.8-ENVIRONMENTAL-CHILD-COMPATIBILITY"
CLASSIFICATION = "E5_ENVIRONMENTAL_SUPERSELECTION_WITH_FUNCTIONAL_RESET_RESIDUAL"
STATUS = "RECOVERED_OWNER_POSTULATE_E5_F4_L4_D4_G4_U_OUTCOME_D"
E_CLASS = "E5"
OWNER_STATUS = "PRE_EXISTING_DEEP_OWNER_WORK_NEWLY_MATERIALIZED"
IMPLEMENTATION_DEFICIT = (
    "ONE_UNRECOVERED_ENVIRONMENT_CONDITIONED_RESET_SELECTION_FUNCTOR_OR_"
    "EQUIVALENT_INTERFACE_GENERATING_FUNCTIONAL"
)
EXACT_NEXT_OBJECT = (
    "RECOVER_OR_OWNER_SUPPLY_THE_ENVIRONMENT_CONDITIONED_FULL_FIELD_RESET_"
    "SELECTION_FUNCTOR_E_s_TO_EQUIVALENCE_CLASS_OF_(F_B,L_s)_WITH_"
    "BOUNDARY_CAUCHY_NOETHER_SCALE_AND_STRUCTURE_SUPPORT"
)

SUPPORTED = "SUPPORTED"
EXCLUDED = "EXCLUDED"
UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True)
class EnvironmentalState:
    """Minimal typed state used by the compatibility predicate."""

    regime: str
    event_class: str
    available_structures: frozenset[str]
    produced_structures: frozenset[str]
    invariants: Mapping[str, Any]
    scale_data: Mapping[str, Any]
    energy_support: Mapping[str, Any]
    retarded: bool | None


@dataclass(frozen=True)
class ChildRequirement:
    """Structures and exact domain predicates required by a child sector."""

    child_id: str
    admitted_regimes: frozenset[str]
    admitted_events: frozenset[str]
    required_structures: frozenset[str]
    required_invariants: Mapping[str, Any]
    required_scale_relations: Mapping[str, Any]
    required_energy_support: frozenset[str]
    requires_retarded_support: bool
    unresolved_requirements: frozenset[str] = frozenset()


def owner_environmental_selection_postulate() -> dict[str, Any]:
    """Record Norman P. Carberry's recovered environmental selection rule."""

    return {
        "owner": "Norman P. Carberry",
        "status": OWNER_STATUS,
        "canonical_statement": (
            "THE_SCALE_SCENARIO_AND_LOCAL_ENERGY_SPACETIME_ENVIRONMENT_OF_"
            "THE_ENCAPSULATION_EVENT_SELECT_THE_PHYSICALLY_ADMISSIBLE_CHILD;_"
            "A_CHILD_REQUIRING_STRUCTURE_NOT_SUPPORTED_OR_PRODUCED_BY_THAT_"
            "EVENT_ENVIRONMENT_CANNOT_BE_PRODUCED"
        ),
        "canonical_example": (
            "A_SPACETIME_IN_KNOTS_CHILD_CANNOT_FORM_DIRECTLY_IN_A_NO_"
            "SPACETIME_ENVIRONMENT_AND_A_PREGEOMETRIC_CHILD_CANNOT_FORM_"
            "DIRECTLY_IN_A_REGULAR_SPACETIME_SCENARIO_WITHOUT_AN_OWNED_"
            "TRANSITION;_EMERGENCE_OR_COLLAPSE_SCENARIOS_MUST_BE_TYPED"
        ),
        "pre_existing_owner_work_not_new_physics": True,
        "newly_materialized_in_this_sprint": True,
        "derived_from_thirteen_term_action": False,
        "recovered_repository_antecedents": [
            "theory/bhsm_spacetime_edge_ontology_repair.md",
            "theory/norman_owner_ontology_recovered.md",
            "src/bhsm/interface/envelopment/canonical_crystallization_v11_0.py",
            "src/bhsm/interface/aether_scale_child_ownership_audit_v16_78.py",
            "src/bhsm/interface/current_semantic_normalization.py",
        ],
        "existing_channel_semantics": (
            "(I_event,I_environment,B_SM)->"
            "(admissible_child_sector,R_rec,z_return)"
        ),
        "cross_sector_branch_selection_arbitrary": False,
    }


def minimal_environmental_state_descriptor() -> dict[str, Any]:
    """Return the five irreducible components of the event environment."""

    components = [
        {
            "symbol": "alpha_s",
            "name": "structure_availability_stratum",
            "definition": "alpha_s records which geometric or pregeometric objects exist",
            "source": "completion/aether_parent_stratification_v15_0.py",
            "interpretation": "regular geometry, transition face, core, or reconstructed geometry",
            "transformation": "diffeomorphism-invariant type label",
            "units": "dimensionless discrete label",
            "domain": "all event states; upsilon itself exists only on G_A",
        },
        {
            "symbol": "tau_s",
            "name": "typed_event_scenario",
            "definition": "tau_s is one stage in the owned formation-to-reconstruction order",
            "source": "aether_reconstruction_firewall_event_v15_45.py",
            "interpretation": "states which transition is allowed to create or remove structures",
            "transformation": "invariant event-class label with an oriented order",
            "units": "dimensionless discrete label",
            "domain": "formation, separation, firewall, cut, reconstruction, return, collapse",
        },
        {
            "symbol": "I_s",
            "name": "transported_superselection_signature",
            "definition": (
                "I_s=(degree,orientation,FR_parity,response_endpoint_order,"
                "incidence,Spin_x_GSM_bundle_class,family_projectors)"
            ),
            "source": "aether_scale_child_ownership_audit_v16_78.py",
            "interpretation": "metric-free data that a candidate child must inherit",
            "transformation": "gauge/bundle isomorphism class and oriented topological invariants",
            "units": "dimensionless discrete and representation-valued data",
            "domain": "survives the oriented cut and reconstruction firewall",
        },
        {
            "symbol": "Lambda_s",
            "name": "scale_signature",
            "definition": (
                "Lambda_s=(ell_kappa,R_reset/ell_kappa,x_s);_"
                "ell_kappa=kappa1^(-1/6),_x_s=log(B/A)|_(sigma=0)"
            ),
            "source": "aether_scale_child_ownership_audit_v16_78.py",
            "interpretation": "physical length anchor and dimensionless child shape/scale data",
            "transformation": "ell_kappa is a scalar length; ratios and x_s are scalars",
            "units": "ell_kappa has L; R/ell_kappa and x_s are dimensionless",
            "domain": "regular or reconstructed geometry only; event-specific R_rec is open",
        },
        {
            "symbol": "B_s",
            "name": "constraint_cauchy_noether_energy_support",
            "definition": (
                "B_s is the gauge-covariant constraint-compatible boundary Cauchy and "
                "Noether-flux data of the physical event layer, including retarded sign"
            ),
            "source": (
                "local_environment_finite_time_encapsulation_gate_v14_94.py;_"
                "ae4_future_collapse_relative_boundary_domain.py"
            ),
            "interpretation": "available local energy/stress/flux and causal support, not minimization",
            "transformation": "boundary tensor/covector densities modulo diagonal gauge covariance",
            "units": "sector-dependent action-density or canonical units; normalized Galerkin values dimensionless",
            "domain": "regular event layer; conventional energy is undefined on C_A",
        },
    ]
    return {
        "formula": "E_s=(alpha_s,tau_s,I_s,Lambda_s,B_s)",
        "components": components,
        "minimality": {
            "without_alpha_s": "cannot distinguish regular spacetime from pregeometry",
            "without_tau_s": "cannot distinguish direct production from an allowed transition",
            "without_I_s": "cannot reject topology spin bundle or incidence mismatch",
            "without_Lambda_s": "cannot apply the owner scale selector",
            "without_B_s": "cannot apply energy constraint flux or causal compatibility",
        },
        "not_included": [
            "every_bulk_field_value",
            "proper_time_or_metric_carried_through_the_firewall",
            "arbitrary_fitted_thresholds",
            "minimum_energy_rule",
        ],
    }


def spacetime_regime_classification() -> dict[str, Any]:
    """Stratify object availability without identifying chart loss with an edge."""

    common_geometry = [
        "smooth_manifold", "nondegenerate_metric", "inverse_metric",
        "orientation", "connection", "curvature", "canonical_phase_space",
    ]
    rows = [
        {
            "regime": "G_A_LORENTZIAN_REGULAR",
            "condition": "alpha_s=G_A;_0<upsilon<=1;_det(g)!=0;_signature_Lorentzian",
            "objects": common_geometry + ["causal_cones", "proper_time"],
            "energy": "stress_energy_canonical_energy_and_boundary_flux_defined",
            "status": "REPOSITORY_OWNED_REGULAR_DOMAIN",
        },
        {
            "regime": "G_A_EUCLIDEAN_REGULAR",
            "condition": "alpha_s=G_A;_0<upsilon<=1;_det(g)!=0;_signature_Euclidean",
            "objects": common_geometry,
            "missing": ["Lorentzian_causal_cones", "proper_time"],
            "energy": "Euclidean_action_not_Lorentzian_Hamiltonian_energy",
            "status": "ACTION_ACCEPTS_BRANCH_BUT_SIGNATURE_NOT_SELECTED",
        },
        {
            "regime": "G_A_DEPLETED_REGULAR",
            "condition": "alpha_s=G_A;_0<upsilon<1;_det(g)!=0",
            "objects": common_geometry,
            "status": "REGULAR_SUBREGIME_NOT_THE_CORE",
        },
        {
            "regime": "LEGENDRE_FIREWALL_TRANSITION_FACE",
            "condition": "minimum(kappa1+X_eta^3)=0_on_the_next_stage",
            "objects": ["last_regular_trace", "degree", "orientation", "FR_parity", "incidence"],
            "not_carried": [
                "metric", "proper_distance", "proper_time", "velocity",
                "curvature", "local_energy_density", "canonical_metric_momentum",
            ],
            "status": "CHART_OR_RECONSTRUCTION_FIREWALL_NOT_PROVED_SPACETIME_EDGE",
        },
        {
            "regime": "C_A_PREGEOMETRIC_CORE",
            "condition": "alpha_s=C_A_separate_from_G_A_and_not_upsilon_equals_zero",
            "objects": ["abstract_invariant_signature"],
            "missing": [
                "spacetime_coordinates", "metric", "inverse_metric", "causal_cones",
                "conventional_time", "conventional_energy", "curvature", "metric_size",
            ],
            "status": "OWNER_ONTOLOGY;_CORE_ADJACENCY_AND_TRANSFER_LAW_OPEN",
        },
        {
            "regime": "G_A_LORENTZIAN_RECONSTRUCTED",
            "condition": "post_cut_constraint_solved_BVP_with_positive_eta_Legendre_form",
            "objects": common_geometry + ["causal_cones", "retarded_child_support"],
            "status": "CONDITIONAL_ON_THE_RECONSTRUCTION_BVP_AND_EVENT_DATA_MAP",
        },
        {
            "regime": "EMERGENCE_OR_COLLAPSE_TRANSITION",
            "condition": "an_owned_transition_map_produces_or_removes_required_structures",
            "objects": [],
            "status": "NOT_YET_DERIVED_AS_A_GENERAL_CORE_GEOMETRY_TRANSFER",
        },
    ]
    return {
        "space": "E=DISJOINT_UNION_OF_TYPED_REGIME_STRATA_AND_TRANSITION_FACES",
        "rows": rows,
        "spacetime_edge": (
            "OWNER_AUTHORIZED_LIMIT_WHERE_GEOMETRIC_VARIABLES_CEASE_AND_PURE_"
            "ENERGY_AETHER_IS_OPERATIVE;_NO_CURRENT_ACTION_LEVEL_LOCATION_EQUATION"
        ),
        "forbidden_identifications": [
            "form_core_truncation_equals_spacetime_edge",
            "core_boundary_equals_spacetime_edge_without_theorem",
            "canonical_stop_equals_spacetime_edge_without_theorem",
            "Legendre_firewall_equals_spacetime_edge_without_theorem",
        ],
    }


def scenario_event_classification() -> dict[str, Any]:
    event = oriented_cut_and_event_data()["surviving_data"]
    ae4 = future_collapse_domain_contract()
    return {
        "typed_order": event["event_order"],
        "extended_classes": [
            "FORMATION", "CONSTRAINT_SOLVED_SHEAR", "SURFACE_SEPARATION",
            "LEGENDRE_FIREWALL", "ORIENTED_CUT", "CHILD_RECONSTRUCTION",
            "PERSISTENCE_OR_RETURN", "AE4_FUTURE_COLLAPSE",
        ],
        "creation_semantics": (
            "A_REQUIRED_STRUCTURE_MAY_BE_ABSENT_BEFORE_tau_s_ONLY_IF_AN_"
            "ACTION_OWNED_OR_OWNER_AUTHORIZED_MATHEMATICAL_TRANSITION_AT_tau_s_"
            "PRODUCES_IT"
        ),
        "AE4_collapse_surface": ae4["collapse_surface"],
        "AE4_child_condition": ae4["child_condition"],
        "homogeneous_local_encapsulation_threshold_derived": False,
        "canonical_stop_identifies_spacetime_edge": False,
    }


def scale_and_energy_variables() -> dict[str, Any]:
    return {
        "scale": {
            "ell_kappa": {"formula": "kappa1^(-1/6)", "units": "L", "owned": True},
            "canonical_reset_radius": {
                "formula": "R_star=2.0232708255441265*ell_kappa",
                "units": "L",
                "owned": True,
            },
            "reset_shape_scale": {
                "formula": "x_s=log(B/A)|_(sigma=0)",
                "units": "dimensionless",
                "owned": True,
            },
            "return_scale": {
                "formula": "R_rec[I_event,I_environment]",
                "units": "L",
                "owned": False,
                "status": "OPEN_BROKEN_RECONSTRUCTION_BVP_OUTPUT",
            },
            "arbitrary_cutoffs_added": False,
        },
        "energy": {
            "Hamiltonian_momentum_constraints": "defined_on_Lorentzian_canonical_strata",
            "stress_energy_invariants": "defined_where_metric_and_inverse_metric_exist",
            "canonical_Galerkin_energy": "dimensionless_in_repository_normalization",
            "Brown_York_boundary_response": "defined_after_a_geometric_boundary_ensemble_is_chosen",
            "Noether_and_Gauss_flux": "gauge_covariant_boundary_density",
            "Hopf_relative_rotor_energy": "positive_adversarial_energy_not_a_minimum_rule",
            "core_conventional_energy": None,
            "minimum_energy_selection_used": False,
            "unknown_thresholds_are": "OPEN_NOT_FITTED",
        },
    }


def actual_knotted_spacetime_child_requirement() -> ChildRequirement:
    event = oriented_cut_and_event_data()["surviving_data"]
    seed = reconstruction_seed()["child_topological_data"]
    return ChildRequirement(
        child_id="BHSM_DEGREE_ONE_LORENTZIAN_FULL_PREIMAGE_CHILD",
        admitted_regimes=frozenset({"G_A_LORENTZIAN_REGULAR", "G_A_LORENTZIAN_RECONSTRUCTED"}),
        admitted_events=frozenset({"CHILD_RECONSTRUCTION", "PERSISTENCE_OR_RETURN"}),
        required_structures=frozenset({
            "smooth_manifold", "nondegenerate_metric", "inverse_metric", "causal_cones",
            "orientation", "spin_structure", "Spin_x_GSM_bundle", "connection",
            "curvature", "canonical_phase_space", "Hopf_full_preimage",
            "constraint_solved_boundary_data", "retarded_child_support",
        }),
        required_invariants={
            "degree": event["global_event_degree"],
            "orientation": seed["orientation"],
            "FR_parity": event["FR_parity"],
            "response_endpoint_order": tuple(event["response_endpoint_order"]),
            "incidence": tuple(event["incidence"]),
            "seam": "S3_times_S3",
            "post_cut_topology": "B4_times_S3",
            "bundle_class": "RETURNED_SAME_Spin_x_GSM_ISOMORPHISM_CLASS",
        },
        required_scale_relations={
            "reset_radius_relation": "R_reset=2.0232708255441265*ell_kappa",
            "return_scale": "OPEN_EVENT_ENVIRONMENT_BVP_OUTPUT",
        },
        required_energy_support=frozenset({
            "Hamiltonian_constraint", "momentum_constraint", "positive_eta_Legendre_form",
            "Gauss_Noether_flux_compatibility",
        }),
        requires_retarded_support=True,
        unresolved_requirements=frozenset({
            "event_layer_to_reconstruction_boundary_data_map",
            "environment_conditioned_return_scale",
        }),
    )


def pregeometric_child_requirement() -> ChildRequirement:
    return ChildRequirement(
        child_id="PREGEOMETRIC_AETHER_CORE_CHILD",
        admitted_regimes=frozenset({"C_A_PREGEOMETRIC_CORE"}),
        admitted_events=frozenset({"EMERGENCE_OR_COLLAPSE_TRANSITION"}),
        required_structures=frozenset({"abstract_invariant_signature", "core_adjacency"}),
        required_invariants={},
        required_scale_relations={},
        required_energy_support=frozenset(),
        requires_retarded_support=False,
        unresolved_requirements=frozenset({
            "positive_core_state_sector", "core_adjacency", "core_transfer_operator",
        }),
    )


def child_requirement_signature() -> dict[str, Any]:
    knotted = actual_knotted_spacetime_child_requirement()
    core = pregeometric_child_requirement()
    return {
        "schema": (
            "R_child=(required_regime,event_classes,structures,invariants,"
            "scale_relations,energy_constraint_support,causal_support)"
        ),
        "knotted_spacetime_child": _requirement_payload(knotted),
        "pregeometric_child": _requirement_payload(core),
        "threshold_policy": "ONLY_REPOSITORY_OWNED_EQUALITIES_INEQUALITIES_AND_DOMAINS;_UNKNOWN_IS_OPEN",
    }


def _requirement_payload(requirement: ChildRequirement) -> dict[str, Any]:
    return {
        "child_id": requirement.child_id,
        "admitted_regimes": sorted(requirement.admitted_regimes),
        "admitted_events": sorted(requirement.admitted_events),
        "required_structures": sorted(requirement.required_structures),
        "required_invariants": dict(requirement.required_invariants),
        "required_scale_relations": dict(requirement.required_scale_relations),
        "required_energy_support": sorted(requirement.required_energy_support),
        "requires_retarded_support": requirement.requires_retarded_support,
        "unresolved_requirements": sorted(requirement.unresolved_requirements),
    }


def compatibility_relation(
    environment: EnvironmentalState,
    requirement: ChildRequirement,
) -> dict[str, Any]:
    """Evaluate support, exclusion, or unresolved status without thresholds."""

    failures: list[str] = []
    open_items: list[str] = []
    if environment.regime not in requirement.admitted_regimes:
        failures.append("regime_not_admitted")
    if environment.event_class not in requirement.admitted_events:
        failures.append("event_class_not_admitted")

    available = environment.available_structures | environment.produced_structures
    missing_structures = sorted(requirement.required_structures - available)
    if missing_structures:
        failures.extend(f"missing_structure:{item}" for item in missing_structures)

    for key, expected in requirement.required_invariants.items():
        if key not in environment.invariants:
            open_items.append(f"missing_invariant:{key}")
        elif environment.invariants[key] != expected:
            failures.append(f"invariant_mismatch:{key}")

    for key, expected in requirement.required_scale_relations.items():
        if expected.startswith("OPEN_"):
            open_items.append(f"open_scale_relation:{key}")
        elif key not in environment.scale_data:
            open_items.append(f"missing_scale_relation:{key}")
        elif environment.scale_data[key] != expected:
            failures.append(f"scale_relation_failed:{key}")

    for key in requirement.required_energy_support:
        if key not in environment.energy_support or environment.energy_support[key] is None:
            open_items.append(f"missing_energy_or_constraint_support:{key}")
        elif environment.energy_support[key] is not True:
            failures.append(f"energy_or_constraint_support_failed:{key}")

    if requirement.requires_retarded_support:
        if environment.retarded is None:
            open_items.append("retarded_support_unknown")
        elif environment.retarded is not True:
            failures.append("retarded_support_failed")

    open_items.extend(sorted(requirement.unresolved_requirements))
    status = EXCLUDED if failures else UNRESOLVED if open_items else SUPPORTED
    return {
        "formula": (
            "E_s_models_R_child_IFF_required_structures_subset_of_"
            "Available(E_s)_union_Produced(tau_s)_AND_invariants_scale_energy_"
            "causal_incidence_predicates_hold"
        ),
        "status": status,
        "failures": failures,
        "open_items": sorted(set(open_items)),
        "minimum_energy_used": False,
    }


def _regular_environment(**overrides: Any) -> EnvironmentalState:
    event = oriented_cut_and_event_data()["surviving_data"]
    requirement = actual_knotted_spacetime_child_requirement()
    values: dict[str, Any] = {
        "regime": "G_A_LORENTZIAN_RECONSTRUCTED",
        "event_class": "CHILD_RECONSTRUCTION",
        "available_structures": requirement.required_structures,
        "produced_structures": frozenset(),
        "invariants": dict(requirement.required_invariants),
        "scale_data": {
            "reset_radius_relation": "R_reset=2.0232708255441265*ell_kappa",
        },
        "energy_support": {
            "Hamiltonian_constraint": True,
            "momentum_constraint": True,
            "positive_eta_Legendre_form": True,
            "Gauss_Noether_flux_compatibility": True,
        },
        "retarded": True,
    }
    values.update(overrides)
    assert event["global_event_degree"] == 1
    return EnvironmentalState(**values)


def owner_example_adjudication() -> dict[str, Any]:
    knotted = actual_knotted_spacetime_child_requirement()
    core = pregeometric_child_requirement()
    core_environment = EnvironmentalState(
        regime="C_A_PREGEOMETRIC_CORE",
        event_class="CHILD_RECONSTRUCTION",
        available_structures=frozenset({"abstract_invariant_signature"}),
        produced_structures=frozenset(),
        invariants={},
        scale_data={},
        energy_support={},
        retarded=None,
    )
    regular_environment = _regular_environment(
        event_class="CHILD_RECONSTRUCTION",
    )
    return {
        "spacetime_in_knots_means": (
            "THE_DEGREE_ONE_ETA_FULL_PREIMAGE_GEOMETRY_WITH_S3_TIMES_S3_"
            "SEAM_HOPF_STRUCTURE_AND_A_REGULAR_LORENTZIAN_CHILD_METRIC"
        ),
        "spacetime_in_knots_identification_status": (
            "STRONGEST_REPOSITORY_SUPPORTED_FORMAL_CORRESPONDENT_NOT_AN_"
            "ACTION_DERIVED_SYNONYM_THEOREM"
        ),
        "exact_owner_phrase_to_mathematical_object_equivalence_derived": False,
        "no_spacetime_means": (
            "C_A_WHERE_SPACETIME_COORDINATES_METRIC_INVERSE_METRIC_CAUSAL_"
            "CONES_CONVENTIONAL_TIME_ENERGY_CURVATURE_AND_METRIC_SIZE_ARE_UNDEFINED"
        ),
        "core_directly_to_knotted": compatibility_relation(core_environment, knotted),
        "regular_directly_to_pregeometric": compatibility_relation(regular_environment, core),
        "vice_versa_qualification": (
            "THE_INCOMPATIBILITY_IS_FOR_DIRECT_PRODUCTION;_A_TYPED_EMERGENCE_"
            "OR_COLLAPSE_EVENT_CAN_MEDIATE_ONLY_AFTER_ITS_STRUCTURE_PRODUCTION_"
            "OR_REMOVAL_MAP_IS_OWNED"
        ),
        "current_general_core_geometry_transition_owned": False,
    }


def adversarial_compatibility_tests() -> dict[str, Any]:
    requirement = actual_knotted_spacetime_child_requirement()
    regular = _regular_environment()
    same_energy_spin_bad = _regular_environment(
        available_structures=requirement.required_structures - {"spin_structure"},
    )
    topology_bad_invariants = dict(regular.invariants)
    topology_bad_invariants["degree"] = 0
    topology_bad = _regular_environment(invariants=topology_bad_invariants)
    advanced = _regular_environment(retarded=False)
    incidence_bad_invariants = dict(regular.invariants)
    incidence_bad_invariants["incidence"] = ("DISCONNECTED_EVENT_CHILD",)
    incidence_bad = _regular_environment(invariants=incidence_bad_invariants)
    holonomy_bad = _regular_environment(
        available_structures=requirement.required_structures - {"connection"},
    )
    disconnected = _regular_environment(
        available_structures=requirement.required_structures - {"constraint_solved_boundary_data"},
    )
    rotor = relative_rotor_terms(0.5, relative_charge=0.5, points=4001)
    return {
        "known_child_status": compatibility_relation(regular, requirement),
        "same_scale_energy_but_spin_incompatible": compatibility_relation(
            same_energy_spin_bad, requirement
        ),
        "topology_change_without_owned_transition": compatibility_relation(topology_bad, requirement),
        "advanced_AE4_candidate": compatibility_relation(advanced, requirement),
        "incompatible_incidence": compatibility_relation(incidence_bad, requirement),
        "nontrivial_holonomy_without_connection": compatibility_relation(holonomy_bad, requirement),
        "disconnected_attachment_without_boundary_solution": compatibility_relation(
            disconnected, requirement
        ),
        "positive_Hopf_rotor": {
            "energy": rotor["relative_rotor_energy"],
            "positive": rotor["relative_rotor_energy"] > 0.0,
            "changes_required_structure_signature": False,
            "selects_orientation_or_attachment": False,
        },
        "Galerkin_restriction": (
            "PROJECTOR_INTERTWINING_IS_REQUIRED_BUT_A_FINITE_GALERKIN_"
            "REPRESENTATIVE_DOES_NOT_SELECT_THE_CONTINUUM_ATTACHMENT"
        ),
    }


def reset_family_after_environmental_selection() -> dict[str, Any]:
    base = spatial_correspondence_nonuniqueness_witness()
    polarization = variational_selection_witness()
    return {
        "prior_family": "A_0={(F_B,L_s):previously_admissible_conditional_full_field_reset}",
        "selected_family": (
            "A(E_s)={(F_B,L_s)_in_A_0:Compatibility(E_s,R_child(F_B,L_s))_"
            "is_not_EXCLUDED}"
        ),
        "confirmed_physical_family_requires_open_inputs_resolved": True,
        "eliminated_classes": [
            "regime_structure_mismatch", "unmediated_geometry_core_transition",
            "degree_orientation_FR_or_incidence_mismatch", "spin_bundle_mismatch",
            "unsupported_connection_or_holonomy", "constraint_or_flux_failure",
            "advanced_AE4_support", "violated_owned_scale_relation",
        ],
        "effect_on_base_routes": {
            "common_embedding": "MUST_PASS_COMPATIBILITY_BUT_NOT_SELECTED",
            "retained_flow": "MUST_PASS_COMPATIBILITY_BUT_NOT_SELECTED",
            "normal_collar": "MUST_PASS_COMPATIBILITY_BUT_NOT_SELECTED",
            "implicit_spatial_construction": "MUST_PASS_COMPATIBILITY_BUT_NOT_SELECTED",
        },
        "base_map_witness": {
            "same_degree": base["same_degree"],
            "same_orientation": base["same_orientation"],
            "same_volume_jacobian": base["same_volume_jacobian"],
            "same_metric": base["both_preserve_product_tangent_metric"],
            "different_tangent_maps": base["tangent_maps_distinct"],
            "both_have_same_environmental_requirement_signature": True,
        },
        "effect_on_nonfermion_polarization": (
            "REJECT_POLARIZATIONS_REQUIRING_UNAVAILABLE_SECTORS_OR_VIOLATING_"
            "CAUSAL_CONSTRAINT_BUNDLE_INCIDENCE_DATA;_NO_WITHIN_SECTOR_GRAPH_SELECTED"
        ),
        "polarization_witness": {
            "both_maximal_isotropic": polarization["both_graphs_maximal_isotropic"],
            "both_cancel_fixed_field_variations": polarization[
                "all_fixed_field_vertical_variations_cancel"
            ],
            "different_jets": polarization["different_first_field_jets"],
            "same_environmental_requirement_signature": True,
        },
        "classification": E_CLASS,
        "E1": False,
        "E2": False,
        "E3": False,
        "E4": False,
        "E5": True,
        "surviving_freedom": (
            "INFINITE_DIMENSIONAL_ENVIRONMENT_COMPATIBLE_BASE_MAP_AND_"
            "NONFERMION_LAGRANGIAN_CORRESPONDENCE_FAMILY"
        ),
        "why_not_reduced_below_E5": (
            "THE_POSTULATE_IS_A_SUPPORT_PREDICATE_ON_CHILD_SECTORS;_CURRENT_"
            "AUTHORITY_HAS_NO_EVENT_BOUNDARY_DATA_MAP_OR_RULE_ASSIGNING_ONE_"
            "POINTWISE_F_B_AND_ONE_L_s_WITHIN_A_SUPPORTED_SECTOR"
        ),
    }


def consequence_and_downstream_status() -> dict[str, Any]:
    prior = generator_charge_and_downstream_status()
    return {
        "physical_principle_deficit_reclassified": (
            "ZERO_NEW_OWNER_PRINCIPLE_AT_THIS_STAGE_BECAUSE_ENVIRONMENTAL_"
            "SELECTION_IS_RECOVERED_PRE_EXISTING_OWNER_WORK"
        ),
        "mathematical_implementation_deficit": IMPLEMENTATION_DEFICIT,
        "arbitrary_interface_functional_domain_reduced": True,
        "functional_dimension_reduced_to_finite": False,
        "selected_reset": None,
        "F_class": "F4",
        "L_class": "L4",
        "D_class": "D4",
        "differentiability_class": prior["differentiability_class"],
        "charge_class": prior["charge_class"],
        "outcome": prior["outcome"],
        "Q_event": prior["Q_event"],
        "Q_child": prior["Q_child"],
        "Q_relative": prior["Q_relative"],
        "gauge_kernel": prior["gauge_kernel"],
        "reduced_reset": prior["reduced_reset"],
        "beta": prior["beta"],
        "S1": prior["S1"],
        "S2": prior["S2"],
        "S3": prior["S3"],
        "S4": prior["S4"],
        "exact_next_object": EXACT_NEXT_OBJECT,
    }


def hindsight_ledger() -> dict[str, Any]:
    return {
        "PREVIOUSLY_DERIVED": [
            "G_A_DISJOINT_UNION_C_A_TYPED_STRATIFICATION",
            "OWNER_SPACETIME_EDGE_ONTOLOGY_WITH_ACTION_LOCATION_OPEN",
            "EVENT_ORDER_AND_SURVIVING_DEGREE_ORIENTATION_FR_INCIDENCE_DATA",
            "ENVIRONMENT_TO_CHILD_CHANNEL_SEMANTICS_AND_SUPERSELECTION_RESTRICTORS",
            "CONDITIONAL_FULL_FIELD_RESET_FAMILY_AND_F4_L4_D4_G4_U_D",
        ],
        "OWNER_AUTHORIZED_RECOVERED_POSTULATE": [
            "SCALE_SCENARIO_AND_ENERGY_SPACETIME_ENVIRONMENT_SELECT_ADMISSIBLE_CHILD",
            "UNSUPPORTED_REQUIRED_STRUCTURE_FORBIDS_DIRECT_CHILD_PRODUCTION",
        ],
        "NOT_YET_DERIVED": [
            "EVENT_LAYER_TO_RECONSTRUCTION_BOUNDARY_DATA_MAP",
            "GENERAL_CORE_GEOMETRY_EMERGENCE_OR_COLLAPSE_TRANSFER",
            "ENVIRONMENT_CONDITIONED_RETURN_SCALE",
            "WITHIN_SECTOR_F_B_AND_L_s_SELECTION_FUNCTOR",
        ],
        "VALIDATED": [
            "ENVIRONMENTAL_COMPATIBILITY_IS_A_TYPED_SUPPORT_RELATION",
            "INCOMPATIBLE_REGIME_TOPOLOGY_SPIN_INCIDENCE_CAUSALITY_AND_SCALE_CLASSES_ARE_EXCLUDED",
            "VICE_VERSA_IS_SCENARIO_RELATIVE_NOT_A_NAIVE_BINARY_FLAG",
            "EXISTING_DEEP_OWNER_SEMANTICS_PRECEDES_THIS_MATERIALIZATION",
        ],
        "INVALIDATED": [
            "OWNER_POSTULATE_IS_NEWLY_INVENTED_PHYSICS",
            "UPSILON_EQUALS_ZERO_IS_AN_INTERIOR_CORE_STATE",
            "LEGENDRE_FIREWALL_OR_CANONICAL_STOP_AUTOMATICALLY_EQUALS_SPACETIME_EDGE",
            "SAME_SCALE_OR_POSITIVE_ENERGY_ALONE_IMPLIES_COMPATIBILITY",
            "ENVIRONMENTAL_SUPPORT_SELECTS_ONE_POINTWISE_ATTACHMENT_OR_POLARIZATION",
        ],
        "REDUNDANT": [
            "REPEAT_THIRTEEN_TERM_ACTION_SELECTOR_SEARCH",
            "REPEAT_MOVING_GRAPH_COVARIANCE_GROUPOID_BRST_OR_R4_AUDITS",
        ],
        "OPEN": [EXACT_NEXT_OBJECT],
        "DECISION_POWER": (
            "THE_RECOVERED_POSTULATE_REMOVES_PHYSICALLY_IMPOSSIBLE_"
            "SUPERSELECTION_SECTORS_BUT_LEAVES_E5_WITHIN_SUPPORTED_SECTORS;_"
            "F4_L4_D4_G4_U_AND_D_REMAIN"
        ),
        "NEW_PHYSICS_DEFICIT": (
            "NOT_CLASSIFIED_AS_NEW_PHYSICS;_CURRENT_DEFICIT_IS_RECOVERY_OR_"
            "MATHEMATICAL_IMPLEMENTATION_OF_DEEP_OWNER_WORK"
        ),
        "OWNER_POSTULATE_CONSEQUENCE": (
            "CROSS_SECTOR_IMPOSSIBILITIES_ARE_ELIMINATED_BEFORE_VARIATION_"
            "BUT_NO_UNIQUE_RESET_IS_EARNED"
        ),
        "ENVIRONMENTAL_CLASSIFICATION": "E_s=(alpha_s,tau_s,I_s,Lambda_s,B_s)",
        "CHILD_REQUIREMENT_CLASSIFICATION": (
            "R_child=(regime,event,structures,invariants,scale,energy,causality)"
        ),
        "SURVIVING_RESET_FREEDOM": E_CLASS,
        "EXACT_NEXT_OBJECT": EXACT_NEXT_OBJECT,
    }


def claim_boundary() -> dict[str, Any]:
    return {
        "status": STATUS,
        "owner_postulate_pre_existing": True,
        "owner_postulate_newly_invented": False,
        "owner_postulate_derived_from_old_action": False,
        "environment_descriptor_derived_from_repository_authority": True,
        "compatibility_relation_materialized": True,
        "unique_reset_selected": False,
        "environmental_class": E_CLASS,
        "F_class": "F4",
        "L_class": "L4",
        "D_class": "D4",
        "differentiability_class": "G4",
        "charge_class": "U",
        "outcome": "D",
        "interface_functional_implemented": False,
        "empirical_thresholds_added": False,
        "minimum_energy_used": False,
        "frozen_predictions_changed": False,
        "FULL_BHSM_COMPLETE": False,
        "exact_next_object": EXACT_NEXT_OBJECT,
    }


__all__ = [
    "ACTION_VERSION", "CLASSIFICATION", "E_CLASS", "EXACT_NEXT_OBJECT",
    "IMPLEMENTATION_DEFICIT", "OWNER_STATUS", "STATUS", "ChildRequirement",
    "EnvironmentalState", "actual_knotted_spacetime_child_requirement",
    "adversarial_compatibility_tests", "child_requirement_signature",
    "claim_boundary", "compatibility_relation", "consequence_and_downstream_status",
    "hindsight_ledger", "minimal_environmental_state_descriptor",
    "owner_environmental_selection_postulate", "owner_example_adjudication",
    "pregeometric_child_requirement", "reset_family_after_environmental_selection",
    "scale_and_energy_variables", "scenario_event_classification",
    "spacetime_regime_classification",
]
