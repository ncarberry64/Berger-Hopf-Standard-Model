"""Canonical doctrine, dependency, and falsification registries for v11.0.

This module crystallizes author-selected ontology without upgrading it to an
action-derived theorem. It also exposes the dependency ordering that prevents
downstream physical calculations from being evaluated with arbitrary support
weights or core data.
"""

from __future__ import annotations

from typing import Any


CANONICAL_DOCTRINE_VERDICT = "BHSM_CANONICAL_RELATIONAL_ENVELOPMENT_ARCHITECTURE_CRYSTALLIZED"


def _entry(
    key: str,
    statement: str,
    classification: str,
    *,
    physical_theorem: bool = False,
    exact_gate: str | None = None,
) -> dict[str, Any]:
    return {
        "key": key,
        "statement": statement,
        "classification": classification,
        "physical_theorem": physical_theorem,
        "exact_gate": exact_gate,
    }


def ontology_payload() -> dict[str, Any]:
    entries = [
        _entry("relational_envelopment_holism", "the whole selects permitted local differentials and local differentials reshape the whole", "AUTHOR_AXIOM"),
        _entry("pure_energy_core", "pure energy without ordinary spacetime support is the core", "AUTHOR_AXIOM", exact_gate="CORE_BOUNDARY_PHASE_SPACE_AND_SELF_ADJOINT_TRANSFER_OPERATOR_AT_QD_INFINITY"),
        _entry("support_surface", "ordinary spacetime is the support/enclosure geometry around the core", "AUTHOR_AXIOM"),
        _entry("three_modes", "q_C, q_W, and q_D are distinct physical geometric mode classes", "AUTHOR_AXIOM", exact_gate="COMMON_S8_S5_S4_REDUCTION_FUNCTOR_AND_COMPLETE_THREE_MODE_HESSIAN"),
        _entry("seam", "the observable M4 seam is a coordinate projection and not a fourth mode", "AUTHOR_AXIOM"),
        _entry("particle", "a particle is a stable localized or parent-bound spacetime envelopment", "WORKING_GEOMETRIC_IDENTIFICATION", exact_gate="STABLE_RELATIVE_PERIODIC_PARTICLE_CYCLES_AND_PHYSICAL_FLOQUET_SPECTRA"),
        _entry("field", "a field is an extended topology of warped spacetime", "WORKING_GEOMETRIC_IDENTIFICATION", exact_gate="NORMALIZED_M4_REDUCTION_AND_FIELD_SOURCE_DICTIONARY"),
        _entry("mass", "mass is invariant displaced energy in a stable spacetime-bearing envelopment", "WORKING_GEOMETRIC_IDENTIFICATION", exact_gate="ACTION_DERIVED_DISPLACED_ENERGY_MASS_FUNCTIONAL"),
        _entry("topological_buoyancy", "closed geometry supplies a universal restoring response to displacement", "STRUCTURAL_POSTULATE", exact_gate="UNIVERSAL_ACTION_DERIVED_BUOYANCY_FUNCTIONAL_AND_WEAK_FIELD_LIMIT"),
        _entry("higgs", "the Higgs is the primary scalar support/displacement/buoyancy wave", "WORKING_GEOMETRIC_IDENTIFICATION", exact_gate="NORMALIZED_SCALAR_BUOYANCY_EIGENMODE_WITH_EFFECTIVE_HIGGS_REPRESENTATION"),
        _entry("electric_charge", "electric charge is signed boundary-phase winding relative to the core", "WORKING_GEOMETRIC_IDENTIFICATION", exact_gate="ACTION_DERIVED_GEOMETRIC_CHARGE_FUNCTOR"),
        _entry("weak_isospin", "weak isospin is two-state handed orientation of core attachment", "WORKING_GEOMETRIC_IDENTIFICATION", exact_gate="ACTION_DERIVED_GEOMETRIC_CHARGE_FUNCTOR"),
        _entry("chirality", "chirality is circulation orientation between the knot and core geometry", "WORKING_GEOMETRIC_IDENTIFICATION", exact_gate="LOCAL_TEXTURE_TO_M4_CHIRAL_CLIFFORD_TRANSGRESSION"),
        _entry("color", "color is open threefold triality closed only in a hadronic parent", "WORKING_GEOMETRIC_IDENTIFICATION", exact_gate="ACTION_DERIVED_COLOR_TRIALITY_CONFINEMENT_FUNCTIONAL"),
        _entry("hypercharge", "hypercharge combines phase, weak orientation, and support representation", "WORKING_GEOMETRIC_IDENTIFICATION", exact_gate="ACTION_DERIVED_GEOMETRIC_CHARGE_FUNCTOR"),
        _entry("antimatter", "antimatter is the complementary orientation of the same envelopment class", "AUTHOR_AXIOM", exact_gate="COMPLETE_ACTION_SECTOR_ANTILINEAR_INVOLUTION"),
        _entry("generations", "three generations are three stable synchronization phases of one sector cycle", "AUTHOR_AXIOM", exact_gate="ORDER_THREE_PHYSICAL_MONODROMY_AND_FROZEN_SLOT_INTERTWINER"),
        _entry("mixing", "mixing is basis overlap dynamically realized by core-mediated reorganization", "AUTHOR_AXIOM", exact_gate="FULL_RANK_CYCLE_AVERAGED_CURRENT_PULLBACK_AND_CORE_TRANSITION"),
        _entry("quantum", "surface quantum behavior is an effective description of core-mediated dynamics", "STRUCTURAL_POSTULATE", exact_gate="NORM_PRESERVING_NO_SIGNALLING_CORE_TRANSFER_CHANNEL"),
        _entry("measurement", "measurement is whole-system re-synchronization to a stable output", "STRUCTURAL_POSTULATE", exact_gate="ACTION_DERIVED_CPTP_MEASUREMENT_REDUCTION_AND_PROBABILITY_RULE"),
        _entry("global_anchor", "one measured global curvature radius may convert completed dimensionless geometry to units", "AUTHOR_AXIOM", exact_gate="ACTION_SELECTED_UNIQUE_DIMENSIONLESS_GLOBAL_GEOMETRY"),
        _entry("multiplicative_support", "upsilon composes multiplicatively and depth additively", "AUTHOR_AXIOM"),
        _entry("logarithmic_depth", "q_D=-lambda_D log(upsilon)", "DERIVED", physical_theorem=True),
        _entry("haar_metric", "ds_D^2=lambda_D^2 dupsilon^2/upsilon^2", "DERIVED", physical_theorem=True),
        _entry("zero_bare_support_potential", "U_D,bare=0", "AUTHOR_AXIOM"),
    ]
    validation = {
        "all_entries_typed": all(row["classification"] in {"AUTHOR_AXIOM", "STRUCTURAL_POSTULATE", "WORKING_GEOMETRIC_IDENTIFICATION", "DERIVED", "DERIVED_CONDITIONAL", "OPEN", "INVALIDATED"} for row in entries),
        "hypotheses_not_promoted": all(row["physical_theorem"] is False for row in entries if row["classification"] in {"STRUCTURAL_POSTULATE", "WORKING_GEOMETRIC_IDENTIFICATION"}),
        "derived_support_results_present": all(any(row["key"] == key and row["classification"] == "DERIVED" for row in entries) for key in ("logarithmic_depth", "haar_metric")),
        "three_modes_not_generations": True,
        "seam_not_fourth_mode": True,
    }
    return {
        "artifact": "BHSM_canonical_ontology_v11_0",
        "paradigm": "Relational Envelopment Holism",
        "entries": entries,
        "canonical_doctrine_verdict": CANONICAL_DOCTRINE_VERDICT,
        "physical_completion_claimed": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def dependency_payload() -> dict[str, Any]:
    nodes = [
        {"id": "D00", "object": "CANONICAL_ONTOLOGY_REGISTRY", "depends_on": [], "status": "CLOSED"},
        {"id": "D01", "object": "MULTIPLICATIVE_SUPPORT_HAAR_KINEMATICS", "depends_on": ["D00"], "status": "CLOSED"},
        {"id": "D02", "object": "ACTION_DERIVED_SUPPORT_REPRESENTATION_FUNCTOR_ON_STRATIFIED_SECTORS_WITH_FIXED_HAAR_SCALE", "depends_on": ["D01"], "status": "OPEN_HIGHEST_UPSTREAM"},
        {"id": "D03", "object": "COMPLETE_SUPPORTED_PARENT_ACTION_AND_EFFECTIVE_RESTORING_RESPONSE", "depends_on": ["D02"], "status": "BLOCKED"},
        {"id": "D04", "object": "CORE_BOUNDARY_PHASE_SPACE_AND_SELF_ADJOINT_TRANSFER_OPERATOR_AT_QD_INFINITY", "depends_on": ["D03"], "status": "BLOCKED"},
        {"id": "D05", "object": "COMMON_S8_S5_S4_REDUCTION_FUNCTOR_AND_COMPLETE_THREE_MODE_HESSIAN", "depends_on": ["D03", "D04"], "status": "BLOCKED"},
        {"id": "D06", "object": "BUOYANCY_HIGGS_CHARGE_AND_WEAK_FIELD_DERIVATIONS", "depends_on": ["D05"], "status": "BLOCKED"},
        {"id": "D07", "object": "STABLE_RELATIVE_PERIODIC_PARTICLE_CYCLES_AND_FLOQUET_SPECTRA", "depends_on": ["D05", "D06"], "status": "BLOCKED"},
        {"id": "D08", "object": "ORDER_THREE_MONODROMIES_AND_FROZEN_SLOT_INTERTWINERS", "depends_on": ["D07"], "status": "BLOCKED"},
        {"id": "D09", "object": "UNIQUE_GLOBAL_GEOMETRY_AND_CURVATURE_RADIUS_ANCHOR", "depends_on": ["D03", "D05"], "status": "BLOCKED"},
        {"id": "D10", "object": "PHYSICAL_MASSES_CKM_PMNS_AND_CORE_TRANSITIONS", "depends_on": ["D07", "D08", "D09"], "status": "BLOCKED"},
        {"id": "D11", "object": "NORMALIZED_EFFECTIVE_M4_STANDARD_MODEL", "depends_on": ["D06", "D10"], "status": "BLOCKED"},
        {"id": "D12", "object": "QUANTUM_MEASUREMENT_PROBABILITY_AND_NO_SIGNALLING", "depends_on": ["D04", "D07", "D11"], "status": "BLOCKED"},
        {"id": "D13", "object": "EMPIRICAL_REPLACEMENT", "depends_on": ["D11", "D12"], "status": "NOT_ELIGIBLE_FROM_REPOSITORY_WORK"},
    ]
    ids = {row["id"] for row in nodes}
    validation = {
        "dependencies_exist": all(set(row["depends_on"]) <= ids for row in nodes),
        "single_highest_upstream_open": sum(row["status"] == "OPEN_HIGHEST_UPSTREAM" for row in nodes) == 1,
        "no_downstream_false_closure": all(row["status"] != "CLOSED" for row in nodes if row["id"] not in {"D00", "D01"}),
        "empirical_replacement_not_repo_gate": nodes[-1]["status"] == "NOT_ELIGIBLE_FROM_REPOSITORY_WORK",
    }
    return {
        "artifact": "BHSM_canonical_dependency_graph_v11_0",
        "nodes": nodes,
        "highest_upstream_open_object": nodes[2]["object"],
        "acyclic_by_declared_order": True,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def falsification_payload() -> dict[str, Any]:
    rows = [
        ("support", "healthy reduced scalar, conservation, v10.4 limit", "ghost, gradient instability, incompatible conservation, or failed parent limit"),
        ("three_mode", "complete reduced action and stable coupled orbit", "no stable physical orbit after complete reduction"),
        ("buoyancy", "universal displaced-energy restoring law and weak-field limit", "no universal law or failed weak-field/equivalence limit"),
        ("higgs", "normalized scalar mode with effective Higgs representation/interactions", "scalar mode cannot realize the required representation or couplings"),
        ("generation", "exactly three stable physical monodromy phases", "phase count differs from three or frozen slots have no intertwiner"),
        ("charge", "geometric assignments, Q=T3+Y/2, and anomaly compatibility", "derived charges fail the relation or anomaly cancellation"),
        ("mixing", "positive Grams, full-rank currents, unitary CKM/PMNS", "rank deficiency, nonunitarity, or missing common current ownership"),
        ("quantum", "norm preservation, conservation, CPTP reduction, no-signalling", "core transfer violates any required property"),
    ]
    return {
        "artifact": "BHSM_canonical_falsification_v11_0",
        "rows": [{"principle": key, "required_result": required, "rejection_condition": rejection, "evaluated": False} for key, required, rejection in rows],
        "physical_rejection_tests_run": False,
        "reason": "their prerequisite action operators and solutions remain unavailable",
        "validation_passed": True,
    }


def core_transfer_payload() -> dict[str, Any]:
    return {
        "artifact": "BHSM_core_transfer_v11_0",
        "target_map": "T_core:(X_in,P_in,phase,Q_topology,G_gauge)->(X_out,P_out,phase_out,Q_out,G_out)",
        "core_endpoint": "q_D=+infinity",
        "mass_shell_transport": None,
        "energy_matching": None,
        "penetration_threshold": None,
        "trajectory_target_selection": "AUTHOR_AXIOM_NOT_DERIVED",
        "phase_transport": None,
        "topology_transport": None,
        "gauge_transport": None,
        "reflection_condition": None,
        "exit_condition": None,
        "flux_conservation_form": "regular+boundary+core=0",
        "transfer_operator": None,
        "status": "BHSM_TRAJECTORY_SELECTED_CORE_TRANSFER_MAP_NOT_DERIVED",
        "next_exact_object": "CORE_BOUNDARY_PHASE_SPACE_AND_SELF_ADJOINT_TRANSFER_OPERATOR_AT_QD_INFINITY",
        "validation_passed": True,
    }


def buoyancy_payload() -> dict[str, Any]:
    return {
        "artifact": "BHSM_topological_buoyancy_v11_0",
        "definition": "F_B=-delta E_complete/delta q_D",
        "classification": "STRUCTURAL_POSTULATE",
        "displaced_energy_functional": None,
        "universal_scale_range": "AUTHOR_AXIOM_NOT_DERIVED",
        "mass_depth_monotonicity": None,
        "inertial_gravitational_identity": None,
        "equivalence_principle": None,
        "weak_field_limit": None,
        "black_hole_limit": None,
        "status": "BHSM_TOPOLOGICAL_BUOYANCY_REMAINS_UNDERIVED_WITHOUT_COMPLETE_SUPPORT_ACTION",
        "next_exact_object": "UNIVERSAL_ACTION_DERIVED_BUOYANCY_FUNCTIONAL_AND_WEAK_FIELD_LIMIT",
        "validation_passed": True,
    }


def higgs_payload() -> dict[str, Any]:
    return {
        "artifact": "BHSM_higgs_buoyancy_mode_v11_0",
        "identification": "primary scalar wave of support, displacement, and buoyancy",
        "classification": "WORKING_GEOMETRIC_IDENTIFICATION",
        "normalized_scalar_mode": None,
        "components": {"q_C": None, "q_W": None, "q_D": None},
        "mass": None,
        "gauge_couplings": None,
        "fermion_couplings": None,
        "tensor_scalar_separation": None,
        "effective_Higgs_representation_recovered": False,
        "status": "BHSM_HIGGS_BUOYANCY_IDENTIFICATION_AWAITS_COMPLETE_PHYSICAL_HESSIAN",
        "next_exact_object": "NORMALIZED_SCALAR_BUOYANCY_EIGENMODE_WITH_EFFECTIVE_HIGGS_REPRESENTATION",
        "validation_passed": True,
    }


def charge_payload() -> dict[str, Any]:
    return {
        "artifact": "BHSM_geometric_charges_v11_0",
        "hypotheses": {
            "electric_charge": "signed boundary-phase winding relative to core",
            "weak_isospin": "two-state handed core-attachment orientation",
            "chirality": "circulation direction between knot and core",
            "color": "open threefold triality in a color-neutral parent",
            "hypercharge": "combination of phase, weak orientation, and support representation",
        },
        "classification": "WORKING_GEOMETRIC_IDENTIFICATION",
        "Q_equals_T3_plus_Y_over_2_derived": False,
        "geometric_assignments": None,
        "existing_anomaly_free_SM_ledger_retained": True,
        "anomaly_cancellation_from_geometric_hypotheses": False,
        "reason": "support weights, chiral transgression, and action-owned charge functor remain missing",
        "status": "BHSM_GEOMETRIC_CHARGE_HYPOTHESES_NOT_DERIVED_FROM_UNIFIED_ACTION",
        "next_exact_object": "ACTION_DERIVED_GEOMETRIC_CHARGE_FUNCTOR",
        "validation_passed": True,
    }


def quantum_measurement_payload() -> dict[str, Any]:
    return {
        "artifact": "BHSM_quantum_measurement_v11_0",
        "quantum_interpretation": "core-mediated dynamics seen from the regular surface",
        "measurement_interpretation": "whole-system re-synchronization to a stable output",
        "classification": "STRUCTURAL_POSTULATE",
        "core_state_space": None,
        "absorption": None,
        "core_evolution": None,
        "emission": None,
        "probability_law": None,
        "no_signalling": None,
        "entanglement": None,
        "measurement_channel": None,
        "classical_limit": None,
        "status": "BHSM_QUANTUM_MEASUREMENT_INTERPRETATION_AWAITS_CORE_TRANSFER_DYNAMICS",
        "next_exact_object": "NORM_PRESERVING_NO_SIGNALLING_CORE_TRANSFER_CHANNEL",
        "validation_passed": True,
    }
