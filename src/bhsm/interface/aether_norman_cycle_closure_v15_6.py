"""BHSM v15.6 Norman formation--persistence--de-envelopment audit.

The module types the physical cycle without promoting theorem-class arrows to
action-derived dynamics.  In particular, de-envelopment is a forward
reconciliation map to an updated parent state; it is neither formation's
inverse nor its dagger.  Spectral evaluation is fail-closed until a physical
operator representation of the complete cycle exists.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from bhsm.interface.aether_master_closure_v15_5 import (
    PHYSICAL_MASTER_SOLUTION_COUNT,
    GAUGE_QUOTIENTED_MASTER_SOLUTION_COUNT,
    state_dynamics_fixed_point_payload,
)


VERSION = "v15.6"
OUTCOME = "OUTCOME_C_NORMAN_CYCLE_TYPED_BUT_PHYSICAL_ARROWS_NOT_ACTION_CLOSED"
SECONDARY_OUTCOME = "OUTCOME_G_MASTER_MAP_REMAINS_NONCONSTRUCTIBLE"
EXACT_NEXT_OBJECT = (
    "ACTION_DERIVED_NONLINEAR_NORMAN_CYCLE_BOUNDARY_VALUE_PROBLEM_WITH_"
    "FORMATION_CONTINUATION_RELATIVE_PERIODIC_PERSISTENCE_DE_ENVELOPMENT_"
    "RECEIVING_DOMAIN_COMPLETE_NOETHER_LEDGER_AND_PHYSICAL_TANGENT_MONODROMY"
)
PRIMARY_VERDICT = (
    "BHSM_V15_6_THE_NORMAN_FORMATION_PERSISTENCE_DE_ENVELOPMENT_ONTOLOGY_IS_"
    "COMPATIBLE_WITH_THE_RETAINED_BHSM_ARCHITECTURE_AND_TYPES_A_CONDITIONAL_"
    "PARENT_TO_UPDATED_PARENT_CYCLE;_DE_ENVELOPMENT_IS_PROVED_DISTINCT_FROM_"
    "FORMATION_INVERSE_AND_DAGGER;_HOWEVER_THE_ACTION_OWNED_SIGMA_ZERO_"
    "HESSIAN_THRESHOLD_DOES_NOT_BY_ITSELF_DERIVE_A_NONLINEAR_FORMATION_MAP,_"
    "THE_RELATIVE_PERIODIC_FLOQUET_THEOREM_CLASS_DOES_NOT_SELECT_A_PHYSICAL_"
    "PERSISTENT_ORBIT,_AND_NO_ACTION_DERIVED_DE_ENVELOPMENT_RECEIVING_DOMAIN_"
    "OR_COMPLETE_NOETHER_LEDGER_EXISTS;_THEREFORE_THE_COMPOSITE_IS_NOT_YET_A_"
    "PHYSICAL_OPERATOR,_ITS_LOOP_SPECTRUM_AND_FLOQUET_RECONSTRUCTION_ARE_"
    "UNDEFINED,_THE_V15_5_STATE_DYNAMICS_NO_SELECTION_THEOREM_SURVIVES,_AND_"
    "FULL_BHSM_COMPLETION_REMAINS_FALSE"
)

DERIVED = "DERIVED"
CONDITIONAL = "CONDITIONAL"
BLOCKED = "BLOCKED"
UNDEFINED = "UNDEFINED_MISSING_UPSTREAM_STRUCTURE"

PARENT = "parent_core_state_C_n"
ENCLOSURE = "enveloped_state_K_n"
PERSISTED_ENCLOSURE = "persisted_enveloped_state_K_prime_n"
UPDATED_PARENT = "updated_parent_core_state_C_n_plus_1"

FAILURE_CLASSES = (
    "FORMATION_MAP_NOT_ACTION_DERIVED",
    "PERSISTENT_ORBIT_NOT_ACTION_SELECTED",
    "DE_ENVELOPMENT_RULE_NOT_ACTION_DERIVED",
    "DE_ENVELOPMENT_DOMAIN_FAILURE",
    "INVARIANT_LEDGER_INCOMPLETE",
    "CORE_SURFACE_FLUX_NOT_OWNED",
    "PRIMITIVE_LOOP_OPERATOR_NOT_DEFINED",
    "LOOP_SPECTRUM_NOT_DEFINED",
    "FLOQUET_RECONSTRUCTION_FAILURE",
    "DAGGER_REMAINS_UNOWNED",
    "STATE_REMAINS_NONUNIQUE",
    "GNS_REMAINS_NONUNIQUE",
    "GENERATOR_REMAINS_NONUNIQUE",
    "REFERENCE_CLOCK_UNOWNED",
    "ABSOLUTE_SCALE_UNOWNED",
    "SELF_RECONSTRUCTION_MAP_MISSING",
    "NO_MASTER_FIXED_POINT",
    "REGULAR_ACTION_COEFFICIENT_UNOWNED",
    "ENCAPSULATION_COMPLETION_NOT_DERIVED",
)


@dataclass(frozen=True)
class CycleMorphism:
    """One typed arrow in the Norman cycle."""

    symbol: str
    source: str
    target: str
    physical_role: str
    theorem_class_owned: bool
    action_derived_map: bool
    first_failure: str | None


def cycle_morphisms() -> tuple[CycleMorphism, ...]:
    """Return formation, persistence, and release with honest provenance."""

    return (
        CycleMorphism(
            "F",
            PARENT,
            ENCLOSURE,
            "nonlinear continuation through the sigma=0 Hessian instability",
            True,
            False,
            "FORMATION_MAP_NOT_ACTION_DERIVED",
        ),
        CycleMorphism(
            "P",
            ENCLOSURE,
            PERSISTED_ENCLOSURE,
            "relative-periodic evolution Phi(tau+T)=h Phi(tau)",
            True,
            False,
            "PERSISTENT_ORBIT_NOT_ACTION_SELECTED",
        ),
        CycleMorphism(
            "D",
            PERSISTED_ENCLOSURE,
            UPDATED_PARENT,
            "forward invariant reconciliation and release to the updated parent",
            False,
            False,
            "DE_ENVELOPMENT_RULE_NOT_ACTION_DERIVED",
        ),
    )


def compose_cycle(arrows: Sequence[CycleMorphism] | None = None) -> dict[str, Any]:
    """Type-check ``D o P o F`` without inventing an operator action."""

    chain = tuple(cycle_morphisms() if arrows is None else arrows)
    if len(chain) != 3:
        raise ValueError("the Norman cycle requires exactly F, P, D")
    for left, right in zip(chain, chain[1:]):
        if left.target != right.source:
            raise ValueError(f"domain mismatch: {left.symbol} then {right.symbol}")
    return {
        "symbol": "H_A=D o P o F",
        "source": chain[0].source,
        "target": chain[-1].target,
        "parent_to_updated_parent": True,
        "same_parent_state_assumed": False,
        "typed_composition_exists": True,
        "physical_operator_exists": all(arrow.action_derived_map for arrow in chain),
    }


def legitimate_cycle_spectrum(
    representation: np.ndarray | None,
    *,
    action_owned: bool,
    domain_proved: bool,
) -> list[dict[str, float]]:
    """Compute spectral data only for a legitimate finite representation."""

    if not action_owned:
        raise ValueError("PRIMITIVE_LOOP_OPERATOR_NOT_DEFINED")
    if not domain_proved:
        raise ValueError("DE_ENVELOPMENT_DOMAIN_FAILURE")
    if representation is None:
        raise ValueError("LOOP_SPECTRUM_NOT_DEFINED")
    matrix = np.asarray(representation, dtype=complex)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("cycle representation must be square")
    values = np.linalg.eigvals(matrix)
    return [
        {"real": float(np.real(value)), "imag": float(np.imag(value))}
        for value in values
    ]


def ontology_payload() -> dict[str, Any]:
    dependencies = [
        ("particle bubble or foam", "nonlinear enclosure candidate", "CONDITIONAL"),
        ("surface tension", "sigma collective branch and sigma=0 Hessian", "DERIVED_STABILITY_GATE"),
        ("cavitation", "lambda_min(H_sigma^(0)[Phi])=0", "DERIVED_THRESHOLD_MAP_NOT_DERIVED"),
        ("compressed skin", "boundary attachment and enclosure stress", "CONDITIONAL"),
        ("differential equalization", "forward invariant reconciliation", "NOT_ACTION_DERIVED"),
        ("black-hole de-envelopment", "quasilocal Noether-flux receiving BVP", "OPEN_V14_94"),
        ("released spacetime", "updated reconstructed parent state", "NOT_DERIVED"),
        ("one common core", "common parent/core correspondence", "ARCHITECTURE_ONLY"),
        ("relational time", "relative-periodic process depth and recurrence", "CLOCK_NOT_SELECTED"),
    ]
    return {
        "artifact": "BHSM_norman_cycle_ontology_v15_6",
        "version": VERSION,
        "cycle": "C_n --F--> K_n --P--> K_prime_n --D--> C_n_plus_1",
        "morphisms": [asdict(row) for row in cycle_morphisms()],
        "composition": compose_cycle(),
        "historical_dependency_map": [
            {"Norman_language": left, "BHSM_mathematics": right, "status": status}
            for left, right, status in dependencies
        ],
        "ontology_consistent": True,
        "cycle_action_closed": False,
        "external_frame_used": False,
    }


def formation_gate_payload() -> dict[str, Any]:
    return {
        "artifact": "BHSM_norman_formation_gate_v15_6",
        "version": VERSION,
        "threshold": "lambda_min(H_sigma^(0)[Phi])=0",
        "threshold_action_owned": True,
        "threshold_is_formation_map": False,
        "nonlinear_continuation_branch_derived": False,
        "constraint_solved_nonhomogeneous_solution_derived": False,
        "formation_map_F_action_derived": False,
        "first_failure": "FORMATION_MAP_NOT_ACTION_DERIVED",
        "reason": "a linear stability crossing neither proves existence nor selects the nonlinear enclosure branch",
    }


def de_envelopment_gate_payload() -> dict[str, Any]:
    return {
        "artifact": "BHSM_norman_de_envelopment_gate_v15_6",
        "version": VERSION,
        "D_type": f"{PERSISTED_ENCLOSURE}->{UPDATED_PARENT}",
        "formation_inverse_type": f"{ENCLOSURE}->{PARENT}",
        "formation_dagger_type": f"{ENCLOSURE}->{PARENT}",
        "D_equals_F_inverse": False,
        "D_equals_F_dagger": False,
        "difference_is_only_notational": False,
        "updated_parent_may_differ_from_initial_parent": True,
        "receiving_parent_domain_action_owned": False,
        "release_boundary_condition_action_owned": False,
        "quasilocal_Noether_flux_candidate_exists": True,
        "quasilocal_Noether_flux_closes_D": False,
        "status": BLOCKED,
        "failure_classes": [
            "DE_ENVELOPMENT_RULE_NOT_ACTION_DERIVED",
            "DE_ENVELOPMENT_DOMAIN_FAILURE",
            "CORE_SURFACE_FLUX_NOT_OWNED",
        ],
    }


def parent_invariant_ledger_payload() -> dict[str, Any]:
    return {
        "artifact": "BHSM_parent_invariant_ledger_v15_6",
        "version": VERSION,
        "owned_entries": {
            "local_diffeomorphism_Noether_identity": "ON_SHELL_REGULAR_DOMAIN",
            "eta_degree": "CONSERVED_UNDER_SMOOTH_FIXED_DOMAIN_EVOLUTION",
            "closed_cosmos_boundary_flux": "ZERO_WHEN_DOMAIN_REMAINS_CLOSED",
        },
        "open_entries": {
            "enclosure_to_parent_receiving_channel": "NOT_ACTION_OWNED",
            "quasilocal_release_flux": "CANDIDATE_NOT_EVALUATED_ON_PHYSICAL_BVP",
            "domain_topology_change": "NOT_CONTROLLED",
            "released_geometric_capacity": "NOT_RECONSTRUCTED",
            "orphaned_enclosure_degrees_of_freedom": "NOT_EXCLUDED",
        },
        "new_parent_content_field_introduced": False,
        "primitive_metric_area_used_in_core": False,
        "foundational_interface_capacity_allowed": True,
        "ledger_complete": False,
        "first_failure": "INVARIANT_LEDGER_INCOMPLETE",
    }


def primitive_loop_payload() -> dict[str, Any]:
    composition = compose_cycle()
    return {
        "artifact": "BHSM_primitive_loop_monodromy_v15_6",
        "version": VERSION,
        "formal_composite": composition["symbol"],
        "typed_parent_to_updated_parent": composition["typed_composition_exists"],
        "parent_endomorphism_class": "CONDITIONAL_AFTER_CANONICAL_IDENTIFICATION_OF_UPDATED_PARENT_DOMAIN",
        "physical_operator_representation": None,
        "operator_domain_proved": False,
        "loop_spectrum": None,
        "spectrum_evaluation_allowed": False,
        "failure_classes": ["PRIMITIVE_LOOP_OPERATOR_NOT_DEFINED", "LOOP_SPECTRUM_NOT_DEFINED"],
    }


def floquet_reconstruction_payload() -> dict[str, Any]:
    return {
        "artifact": "BHSM_primitive_to_floquet_reconstruction_v15_6",
        "version": VERSION,
        "BHSM_relative_periodic_condition": "Phi(tau+T)=h Phi(tau)",
        "BHSM_tangent_monodromy": "deltaPhi(tau+T)=M_BHSM deltaPhi(tau)",
        "physical_persistent_orbit_action_selected": False,
        "physical_M_BHSM_computed": False,
        "primitive_H_A_operator_computed": False,
        "projection_intertwiner_action_owned": False,
        "dimension_domain_compatibility": UNDEFINED,
        "intertwining_identity_proved": False,
        "reconstruction_status": BLOCKED,
        "first_failure": "FLOQUET_RECONSTRUCTION_FAILURE",
    }


def z2_z3_killscreen_payload() -> dict[str, Any]:
    rows = []
    for order in (2, 3):
        rows.append(
            {
                "candidate": f"Z{order}",
                "physical_option": False,
                "formation_map": BLOCKED,
                "persistent_map": BLOCKED,
                "de_envelopment_map": BLOCKED,
                "invariant_ledger": BLOCKED,
                "loop_monodromy": BLOCKED,
                "self_reconstruction": BLOCKED,
                "first_failure": "FAILS_FORMATION_CLOSURE",
                "additional_failures": [
                    "FAILS_DE_ENVELOPMENT_CLOSURE",
                    "FAILS_INVARIANT_LEDGER",
                    "FAILS_LOOP_MONODROMY_RECONSTRUCTION",
                    "FAILS_SELF_RECONSTRUCTION",
                    "FAILS_CLOCK_SCALE_CLOSURE",
                ],
                "disposition": "SURROGATE_INCOMPLETENESS_WITNESS_NOT_ACTION_ELIMINATED_OR_SELECTED",
            }
        )
    return {
        "artifact": "BHSM_z2_z3_full_cycle_killscreen_v15_6",
        "version": VERSION,
        "candidates": rows,
        "selected_by_generation_count": False,
        "selected_by_minimal_dimension": False,
        "both_pass_full_cycle": False,
        "either_action_eliminated_relative_to_other": False,
    }


def state_gns_cycle_selection_payload() -> dict[str, Any]:
    previous = state_dynamics_fixed_point_payload()
    return {
        "artifact": "BHSM_state_gns_cycle_selection_v15_6",
        "version": VERSION,
        "v15_5_reset_semigroup_theorem_preserved": True,
        "fixed_pair_cardinality": previous["state_dynamics_fixed_pair_cardinality"],
        "physical_cycle_operator_exists": False,
        "cycle_invariant_state_selected": False,
        "dagger_selected_from_cycle": False,
        "canonical_GNS_class_selected": False,
        "Dirichlet_form_action_owned": False,
        "relational_generator_action_owned": False,
        "clock_recurrence_action_owned": False,
        "failure_classes": [
            "DAGGER_REMAINS_UNOWNED",
            "STATE_REMAINS_NONUNIQUE",
            "GNS_REMAINS_NONUNIQUE",
            "GENERATOR_REMAINS_NONUNIQUE",
            "REFERENCE_CLOCK_UNOWNED",
        ],
    }


def master_self_reconstruction_payload() -> dict[str, Any]:
    return {
        "artifact": "BHSM_master_self_reconstruction_v15_6",
        "version": VERSION,
        "primitive_cycle_action_owned": False,
        "foundation_to_regular_reconstruction": "CONDITIONAL_IDENTITY_LIMIT_ONLY",
        "regular_to_foundation_return_map": BLOCKED,
        "surface_capacity_reconstruction": BLOCKED,
        "master_self_reconstruction_map_exists": False,
        "physical_master_solution_count": PHYSICAL_MASTER_SOLUTION_COUNT,
        "gauge_quotiented_master_solution_count": GAUGE_QUOTIENTED_MASTER_SOLUTION_COUNT,
        "fixed_point_exists": UNDEFINED,
        "fixed_point_stability": "NOT_EVALUABLE_NO_MASTER_MAP_OR_FIXED_POINT",
        "absolute_scale_owned": False,
        "failure_classes": [
            "SELF_RECONSTRUCTION_MAP_MISSING",
            "NO_MASTER_FIXED_POINT",
            "ABSOLUTE_SCALE_UNOWNED",
        ],
    }


def theorem_package() -> dict[str, dict[str, Any]]:
    return {
        "N1": {"status": DERIVED, "result": "NORMAN_AND_BHSM_ONTOLOGIES_COMPATIBLE"},
        "N2": {"status": "PARTIAL", "result": "THRESHOLD_DERIVED_FORMATION_MAP_BLOCKED", "failure": "FORMATION_MAP_NOT_ACTION_DERIVED"},
        "N3": {"status": "PARTIAL", "result": "RELATIVE_PERIODIC_CLASS_DERIVED_ORBIT_UNSELECTED", "failure": "PERSISTENT_ORBIT_NOT_ACTION_SELECTED"},
        "N4": {"status": DERIVED, "result": "DE_ENVELOPMENT_NOT_AUTOMATIC_DAGGER_OR_INVERSE"},
        "N5": {"status": BLOCKED, "failure": "DE_ENVELOPMENT_RULE_NOT_ACTION_DERIVED"},
        "N6": {"status": BLOCKED, "failure": "INVARIANT_LEDGER_INCOMPLETE"},
        "N7": {"status": CONDITIONAL, "failure": "PRIMITIVE_LOOP_OPERATOR_NOT_DEFINED"},
        "N8": {"status": BLOCKED, "failure": "LOOP_SPECTRUM_NOT_DEFINED"},
        "N9": {"status": BLOCKED, "failure": "FLOQUET_RECONSTRUCTION_FAILURE"},
        "N10": {"status": BLOCKED, "failure": "DAGGER_REMAINS_UNOWNED"},
        "N11": {"status": BLOCKED, "failure": "STATE_REMAINS_NONUNIQUE"},
        "N12": {"status": BLOCKED, "failure": "GNS_REMAINS_NONUNIQUE"},
        "N13": {"status": BLOCKED, "failure": "GENERATOR_REMAINS_NONUNIQUE"},
        "N14": {"status": BLOCKED, "failure": "REFERENCE_CLOCK_UNOWNED"},
        "N15": {"status": BLOCKED, "failure": "CORE_SURFACE_FLUX_NOT_OWNED"},
        "N16": {"status": DERIVED, "result": "Z2_Z3_FAIL_FULL_CYCLE_AS_SURROGATE_WITNESSES"},
        "N17": {"status": BLOCKED, "failure": "SELF_RECONSTRUCTION_MAP_MISSING"},
        "N18": {"status": BLOCKED, "failure": "NO_MASTER_FIXED_POINT"},
        "N19": {"status": BLOCKED, "failure": "ABSOLUTE_SCALE_UNOWNED"},
        "N20": {"status": BLOCKED, "failure": "REGULAR_ACTION_COEFFICIENT_UNOWNED"},
        "N21": {"status": BLOCKED, "failure": "ENCAPSULATION_COMPLETION_NOT_DERIVED"},
        "N22": {"status": BLOCKED, "result": "FULL_BHSM_COMPLETE_FALSE"},
    }


def completion_conditions() -> dict[str, bool]:
    return {
        "action_derived_primitive_event_composition": False,
        "action_derived_reciprocity_or_unique_physical_class": False,
        "action_derived_formation_map": False,
        "action_derived_persistent_evolution": False,
        "action_derived_de_envelopment_map": False,
        "exact_parent_invariant_bookkeeping": False,
        "derived_primitive_loop_monodromy": False,
        "exact_BHSM_Floquet_reconstruction": False,
        "distinguished_physical_state": False,
        "canonical_GNS_module_representation": False,
        "action_owned_quadratic_Dirichlet_form": False,
        "action_derived_relational_generator": False,
        "action_owned_core_geometry_attachment": False,
        "variational_boundary_relation": False,
        "self_reconstruction_map": False,
        "exactly_one_physical_master_solution_modulo_gauge": False,
        "master_fixed_point_stability": False,
        "stable_internal_reference_clock": False,
        "absolute_dimensionful_scale_ownership": False,
        "regular_action_coefficient_ownership": False,
        "gauge_normalization_ownership": False,
        "scalar_topographic_source_ownership": False,
        "mass_bridge_ownership": False,
        "mixing_provenance": False,
        "neutrino_scale_and_provenance": False,
        "no_empirical_tuning": True,
        "no_arbitrary_unowned_continuous_parameter": True,
        "no_preferred_frame": True,
        "frozen_prediction_integrity": True,
        "full_committed_state_repository_suite_green": True,
    }


def full_completion_payload() -> dict[str, Any]:
    conditions = completion_conditions()
    return {
        "artifact": "BHSM_full_completion_gate_v15_6",
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "outcome": OUTCOME,
        "secondary_outcome": SECONDARY_OUTCOME,
        "FULL_BHSM_COMPLETE": all(conditions.values()),
        "completion_conditions": conditions,
        "condition_count": len(conditions),
        "theorem_package": theorem_package(),
        "physical_master_solution_count": PHYSICAL_MASTER_SOLUTION_COUNT,
        "gauge_quotiented_master_solution_count": GAUGE_QUOTIENTED_MASTER_SOLUTION_COUNT,
        "mathematical_completion_is_empirical_confirmation": False,
        "regular_BHSM": {
            "identity_limit_recovery": "EXACT_UNCHANGED",
            "gauge_normalization": BLOCKED,
            "scalar_topographic_source": BLOCKED,
            "mass_bridge": BLOCKED,
            "CKM_PMNS_provenance": BLOCKED,
            "neutrino_scale": BLOCKED,
            "encapsulation": "BLOCKED_V14_94_NONHOMOGENEOUS_LORENTZIAN_CONTROL",
        },
        "exact_next_object": EXACT_NEXT_OBJECT,
        "Hindsight_20_20": {
            "VALIDATED": [
                "Norman formation persistence and release are compatible with BHSM dynamic envelopment",
                "the sigma=0 Hessian crossing is the action-owned formation threshold",
                "relative-periodic evolution and tangent monodromy are the correct persistence language",
                "release returns content to an updated parent and is not automatically a dagger or inverse",
                "quasilocal Noether flux is the correct route to a release ledger",
                "the v15.5 reset-semigroup no-selection theorem remains valid",
            ],
            "INVALIDATED": [
                "a Hessian zero mode by itself constructs the nonlinear formation map",
                "a theorem-class Floquet problem supplies an action-selected persistent orbit",
                "de-envelopment may be declared equal to formation inverse or dagger",
                "a typed composite may be assigned a physical spectrum before its domain and representation exist",
                "Z2 or Z3 may be selected by generation count or minimality",
            ],
            "RECLASSIFIED": [
                "the primitive loop is a conditional parent-to-updated-parent composite rather than a derived operator",
                "surface capacity is an allowed foundational interface invariant but not primitive metric area",
                "Z2 and Z3 are surrogate incompleteness witnesses that fail the same physical cycle gates",
                "black-hole release is a downstream instance of the unresolved universal release BVP",
            ],
            "OPEN": [EXACT_NEXT_OBJECT],
        },
        "new_empirical_inputs": False,
        "new_fitted_parameters": False,
        "new_arbitrary_continuous_parameters": False,
        "new_primitive_fields": False,
        "primitive_core_metric_area": False,
        "primitive_ordinary_time": False,
        "primitive_ordinary_energy_units": False,
        "preferred_frame": False,
        "frozen_predictions_changed": False,
        "official_prediction_logic_changed": False,
        "USB_touched_during_campaign": False,
    }


def artifact_payloads() -> dict[str, dict[str, Any]]:
    return {
        "BHSM_norman_cycle_ontology_v15_6.json": ontology_payload(),
        "BHSM_norman_formation_gate_v15_6.json": formation_gate_payload(),
        "BHSM_norman_de_envelopment_gate_v15_6.json": de_envelopment_gate_payload(),
        "BHSM_parent_invariant_ledger_v15_6.json": parent_invariant_ledger_payload(),
        "BHSM_primitive_loop_monodromy_v15_6.json": primitive_loop_payload(),
        "BHSM_primitive_to_floquet_reconstruction_v15_6.json": floquet_reconstruction_payload(),
        "BHSM_z2_z3_full_cycle_killscreen_v15_6.json": z2_z3_killscreen_payload(),
        "BHSM_state_gns_cycle_selection_v15_6.json": state_gns_cycle_selection_payload(),
        "BHSM_master_self_reconstruction_v15_6.json": master_self_reconstruction_payload(),
        "BHSM_full_completion_gate_v15_6.json": full_completion_payload(),
    }


def deterministic_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n"


def materialize(directory: str | Path) -> list[Path]:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for name, payload in artifact_payloads().items():
        path = target / name
        path.write_text(deterministic_json(payload), encoding="utf-8")
        paths.append(path)
    return paths
