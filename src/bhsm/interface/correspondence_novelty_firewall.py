"""BHSM v6.0.6 correspondence, ontology, and novelty firewall."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


VERSION = "v6.0.6"
SPRINT = "bhsm-general-energy-geometry-envelopment-v6-0-6"
PRIMARY_RESULT = "BHSM_CORRESPONDENCE_NOVELTY_FIREWALL_DERIVED"
REDUCTION_RESULT = "BHSM_B8_S7_TO_BERGER_S3_REDUCTION_READINESS_IDENTIFIED"
REDUCTION_STATUS = "BHSM_B8_S7_TO_BERGER_S3_REDUCTION_BLOCKED"

CATEGORIES = (
    "ESTABLISHED_PHYSICS_CORRESPONDENCE",
    "BHSM_GEOMETRIC_REINTERPRETATION",
    "BHSM_DERIVED",
    "BHSM_DERIVED_CONDITIONALLY",
    "BHSM_CANDIDATE",
    "BHSM_NOVEL_PREDICTION_FROZEN",
    "INVALIDATED",
    "OPEN",
)

ARTIFACT_FILES = {
    "ontology": "BHSM_physicality_ontology_v6_0_6.json",
    "correspondence": "BHSM_established_physics_correspondence_registry_v6_0_6.json",
    "reinterpretation": "BHSM_geometric_reinterpretation_registry_v6_0_6.json",
    "native": "BHSM_native_derivation_registry_v6_0_6.json",
    "firewall": "BHSM_novelty_prediction_firewall_v6_0_6.json",
    "harmonic": "BHSM_harmonic_role_reclassification_v6_0_6.json",
    "sigma": "BHSM_sigma_role_reclassification_v6_0_6.json",
    "roles": "BHSM_b8_s7_berger_s3_candidate_role_matrix_v6_0_6.json",
    "maps": "BHSM_b8_s7_berger_s3_required_maps_v6_0_6.json",
    "metric": "BHSM_b8_s7_berger_s3_metric_measure_compatibility_v6_0_6.json",
    "action": "BHSM_parent_to_v5_action_sector_map_v6_0_6.json",
    "modes": "BHSM_s7_to_berger_s3_mode_branching_readiness_v6_0_6.json",
    "blockers": "BHSM_b8_s7_berger_s3_reduction_blockers_v6_0_6.json",
    "roadmap": "BHSM_full_bhsm_roadmap_v6_0_6.json",
    "audit": "BHSM_correspondence_hidden_input_claim_audit_v6_0_6.json",
    "report": "BHSM_correspondence_novelty_firewall_report_v6_0_6.json",
}

GUARDS = {
    "new_parent_field_added": False,
    "new_interaction_added": False,
    "measured_mass_coupling_or_scale_used": False,
    "target_fitting_used": False,
    "frozen_predictions_changed": False,
    "official_prediction_logic_changed": False,
    "existing_numerical_predictions_changed": False,
    "absolute_unit_generated": False,
    "particle_objecthood_derived": False,
    "full_bhsm_completion_claimed": False,
}


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _common(artifact: str) -> dict[str, Any]:
    return {
        "artifact": artifact,
        "version": VERSION,
        "sprint": SPRINT,
        "primary_result": PRIMARY_RESULT,
        "reduction_readiness_result": REDUCTION_RESULT,
        "reduction_status": REDUCTION_STATUS,
        "claim_boundary": (
            "v6.0.6 freezes an interpretive ontology and a provenance firewall. "
            "It does not claim established physics as a BHSM derivation, close the "
            "B8/S7-to-Berger-S3 reduction, or change any observable prediction."
        ),
        **GUARDS,
    }


def ontology_payload() -> dict[str, Any]:
    levels = [
        {"term": "physical differential", "definition": "nonzero change in stress, energy, flux, curvature, field value, topology, or boundary response relative to a declared background"},
        {"term": "envelopment", "definition": "localized, bounded, shell-like, level-set, or otherwise distinguishable spacetime differential"},
        {"term": "persistence", "definition": "continued existence under the equations of motion"},
        {"term": "objecthood", "definition": "self-supported persistent localization"},
        {"term": "particle-like object", "definition": "object with appropriate quantization, topology, spectrum, spin/statistics, charges, and interactions"},
    ]
    return {
        **_common("BHSM_physicality_ontology_v6_0_6"),
        "status": "BHSM_PHYSICALITY_ONTOLOGY_FROZEN",
        "category": "BHSM_GEOMETRIC_REINTERPRETATION",
        "definition": "Physicality is the observable differentiation produced when energy modifies, strains, localizes, propagates through, or envelopes spacetime.",
        "scope": "interpretive ontology, not a new dynamical theorem",
        "established_examples": ["compression", "collision", "propagation", "explosion-like shells", "constructive interference", "curvature response", "gauge pressure"],
        "scientific_burden": "derive Berger-Hopf-specific discrete structures, coefficients, spectra, forces, particles, generations, scales, and preregistered predictions",
        "dictionary": levels,
        "universal_sigma_required": False,
        "universal_harmonic_trigger_required": False,
    }


def _entry(
    concept: str,
    category: str,
    statement: str,
    source: str,
    bhsm_specific: bool,
    mathematical_dependencies: list[str],
    physical_dependencies: list[str],
    claim_boundary: str,
    changes_observable_calculation: bool = False,
    independently_testable: bool = False,
) -> dict[str, Any]:
    if category not in CATEGORIES:
        raise ValueError(f"unknown category: {category}")
    return {
        "concept": concept,
        "category": category,
        "precise_statement": statement,
        "source_artifact": source,
        "bhsm_specific": bhsm_specific,
        "mathematical_dependencies": mathematical_dependencies,
        "physical_dependencies": physical_dependencies,
        "claim_boundary": claim_boundary,
        "changes_observable_calculation": changes_observable_calculation,
        "independently_testable": independently_testable,
    }


def concept_registry() -> list[dict[str, Any]]:
    correspondence = "used as a correspondence requirement; not a novel BHSM achievement"
    open_boundary = "not parent-derived and not a BHSM prediction"
    rows = [
        _entry("stress-energy conservation", "ESTABLISHED_PHYSICS_CORRESPONDENCE", "On-shell covariant stress conservation is required where the action has diffeomorphism invariance.", "artifacts/BHSM_minimal_parent_action_equations_stress_v6_0_5.json", False, ["action", "field equations", "Bianchi identity"], ["stress tensor"], correspondence),
        _entry("compression", "ESTABLISHED_PHYSICS_CORRESPONDENCE", "Compression and converging flow can produce stress and density gradients.", "docs/bhsm_correspondence_novelty_firewall_v6_0_6.md", False, ["continuum or field equations"], ["matter or field stress"], correspondence),
        _entry("collisions", "ESTABLISHED_PHYSICS_CORRESPONDENCE", "Collisions can create localized energy-spacetime differentials.", "docs/bhsm_correspondence_novelty_firewall_v6_0_6.md", False, ["interaction dynamics"], ["colliding physical system"], correspondence),
        _entry("outgoing waves and explosion-like shells", "ESTABLISHED_PHYSICS_CORRESPONDENCE", "Ordinary outgoing wavefronts and shells are established propagation phenomena.", "docs/bhsm_correspondence_novelty_firewall_v6_0_6.md", False, ["hyperbolic evolution"], ["initial data", "stress and flux"], "not a shock without nonlinear weak-solution and jump conditions"),
        _entry("constructive and destructive interference", "ESTABLISHED_PHYSICS_CORRESPONDENCE", "Linear waves exhibit phase-dependent local interference.", "artifacts/BHSM_harmonic_linear_no_selection_theorem_v6_0_4.json", False, ["linear superposition"], ["coherent initial data"], "ordinary interference is not a derived BHSM interaction"),
        _entry("curvature sourced by stress-energy", "ESTABLISHED_PHYSICS_CORRESPONDENCE", "Metric theories use stress as a curvature source according to their field equations.", "artifacts/BHSM_minimal_parent_action_equations_stress_v6_0_5.json", False, ["selected metric action"], ["conserved stress"], "BHSM has not solved a new self-gravitating envelope"),
        _entry("gauge connections", "ESTABLISHED_PHYSICS_CORRESPONDENCE", "Connections and curvature are accepted gauge-theory language.", "theory/explicit_hopf_berger_boundary_oneforms.md", False, ["bundle", "connection"], ["gauge representation"], "a BHSM normalization and action source remain required"),
        _entry("topological solitons", "ESTABLISHED_PHYSICS_CORRESPONDENCE", "Topological solitons are an established class of persistent field configurations.", "CLAIMS.md", False, ["nontrivial homotopy", "nonlinear action"], ["finite-energy boundary conditions"], "no BHSM soliton is derived"),
        _entry("compact-space spectra", "BHSM_DERIVED_CONDITIONALLY", "Spectra follow exactly after the compact metric, operator, and domain are fixed.", "artifacts/BHSM_harmonic_exact_mode_representation_spectrum_v6_0_4.json", True, ["metric", "operator", "domain"], [], "the round-S7 scalar diagnostic is exact; the physical parent operator remains unselected"),
        _entry("particle localization", "OPEN", "No parent-derived localized particle sector is established.", "STATUS.md", True, ["reduction", "operator", "localized solution"], ["stability"], open_boundary),
        _entry("stable objecthood", "OPEN", "Self-supported persistent localization has not been derived.", "docs/bhsm_minimal_parent_theory_kill_test_v6_0_5.md", True, ["nonlinear solution", "constrained Hessian"], ["finite energy", "controlled leakage"], open_boundary),
        _entry("charge quantization", "OPEN", "No parent-to-reduced charge quantization theorem is complete.", "STATUS.md", True, ["bundle", "representation", "normalization"], ["gauge action"], open_boundary),
        _entry("three generations", "OPEN", "Existing mode ledgers do not derive three physical generations.", "artifacts/BHSM_harmonic_parent_to_v5_compatibility_v6_0_4.json", True, ["S7-to-S3 branching", "fermion operator"], ["particle identification"], open_boundary),
        _entry("particle masses", "OPEN", "Particle masses are not parent-derived.", "CLAIMS.md", True, ["reduced action", "absolute unit"], ["particle sectors"], open_boundary),
        _entry("gauge couplings", "OPEN", "Gauge normalizations and couplings are not parent-derived.", "artifacts/BHSM_unified_dynamical_action_candidate_v5_4.json", True, ["fiber trace", "action coefficient map"], ["gauge sector"], open_boundary),
        _entry("fine-structure constant", "OPEN", "The fine-structure constant is not derived.", "CLAIMS.md", True, ["gauge normalization", "quantum running"], ["absolute unit convention"], open_boundary),
        _entry("CKM", "OPEN", "CKM completion is not derived from the parent action.", "CLAIMS.md", True, ["charged-current action", "generation basis"], ["quark sectors"], open_boundary),
        _entry("PMNS", "OPEN", "PMNS completion is not derived from the parent action.", "CLAIMS.md", True, ["neutral and charged lepton actions"], ["lepton sectors"], open_boundary),
        _entry("neutrino scale", "OPEN", "The neutrino absolute scale remains unanchored.", "STATUS.md", True, ["neutral operator", "absolute unit"], ["neutrino sector"], open_boundary),
        _entry("black-hole de-envelopment", "BHSM_CANDIDATE", "De-envelopment is an interpretive candidate requiring a causal, dynamical theorem.", "CLAIMS.md", True, ["Lorentzian solution", "horizon/interface dynamics"], ["conservation", "regular continuation"], "no black-hole de-envelopment result is claimed"),
        _entry("shared-core hypothesis", "BHSM_CANDIDATE", "A shared core is an unproved hypothesis.", "CLAIMS.md", True, ["global parent geometry", "causal continuation"], ["black-hole solutions"], "no shared core or singularity resolution is claimed"),
        _entry("primordial release", "OPEN", "No action-derived absolute release threshold is complete.", "artifacts/BHSM_primordial_boundary_tension_action_source_closure_report_v5_12.json", True, ["surface Hessian", "sourced tension", "absolute unit"], ["stable compact state"], open_boundary),
        _entry("absolute unit", "OPEN", "The global scale modulus has not been lifted by an internally sourced anchor.", "artifacts/BHSM_absolute_unit_anchor_generation_report_v5_8.json", True, ["dimensionful parent primitive or anomaly"], [], open_boundary),
        _entry("v5 scalar/topographic vacuum", "BHSM_DERIVED_CONDITIONALLY", "The reduced potential V=-sigma^2+2sigma^4 has A_ST=-2, G_ST=8, and |sigma|=1/2 in its declared normalized model.", "artifacts/BHSM_scalar_topographic_evaluated_vacuum_functional_v5_7.json", True, ["reduced v5 action"], [], "reduced conditional result; parent source and universal meaning are open"),
        _entry("exact S7 octave pair", "BHSM_DERIVED", "For a massless scalar on round S7, l=4 and l=10 obey omega_10=2 omega_4.", "artifacts/BHSM_harmonic_exact_mode_representation_spectrum_v6_0_4.json", True, ["round S7", "scalar Laplacian"], [], "dimensionless diagnostic relation only", False, True),
        _entry("Berger S3 mode ledger", "BHSM_DERIVED_CONDITIONALLY", "Stored Berger-S3 mode calculations retain their stated lower-dimensional domains.", "artifacts/BHSM_s7_berger_s3_reclassification_v6_0_1.json", True, ["Berger metric", "declared operators and domains"], [], "not yet identified with branched S7 parent modes"),
        _entry("physicality as envelopment", "BHSM_GEOMETRIC_REINTERPRETATION", "Known differentials admit a common energy-spacetime envelopment interpretation.", "artifacts/BHSM_physicality_ontology_v6_0_6.json", True, [], ["observable differential"], "ontology, not a dynamical theorem"),
    ]
    return rows


def correspondence_payload() -> dict[str, Any]:
    rows = [row for row in concept_registry() if row["category"] == "ESTABLISHED_PHYSICS_CORRESPONDENCE"]
    return {**_common("BHSM_established_physics_correspondence_registry_v6_0_6"), "status": "BHSM_ESTABLISHED_PHYSICS_CORRESPONDENCE_REGISTRY_DERIVED", "rows": rows, "allowed_uses": ["correspondence requirements", "experimental comparison", "notation", "validated limiting behavior"], "forbidden_uses": ["claim as new BHSM discovery", "supply unexplained foundational coefficients", "target fit BHSM outputs"]}


def reinterpretation_payload() -> dict[str, Any]:
    return {**_common("BHSM_geometric_reinterpretation_registry_v6_0_6"), "status": "BHSM_PHYSICALITY_ONTOLOGY_FROZEN", "rows": [row for row in concept_registry() if row["category"] == "BHSM_GEOMETRIC_REINTERPRETATION"], "status_type": "INTERPRETIVE_ONTOLOGICAL", "dynamical_theorem": False}


def native_payload() -> dict[str, Any]:
    return {**_common("BHSM_native_derivation_registry_v6_0_6"), "status": "BHSM_NATIVE_DERIVATION_REGISTRY_DERIVED", "rows": [row for row in concept_registry() if row["category"] in {"BHSM_DERIVED", "BHSM_DERIVED_CONDITIONALLY"}], "registry_complete_for_full_bhsm": False}


def firewall_payload() -> dict[str, Any]:
    return {**_common("BHSM_novelty_prediction_firewall_v6_0_6"), "status": "BHSM_NOVELTY_CLAIM_FIREWALL_DERIVED", "categories": list(CATEGORIES), "rows": concept_registry(), "prediction_gate": {"required_category": "BHSM_NOVEL_PREDICTION_FROZEN", "requirements": ["BHSM-specific derivation", "defined action and domain", "no target fitting", "numerical or structural preregistration", "frozen output before experimental comparison", "independent testability"]}, "current_v6_0_6_predictions": [], "established_physics_claimed_novel": False}


def harmonic_payload() -> dict[str, Any]:
    return {**_common("BHSM_harmonic_role_reclassification_v6_0_6"), "status": "BHSM_HARMONIC_ROLE_RECLASSIFIED", "exact_result": {"category": "BHSM_DERIVED", "formula": "omega_10=2 omega_4", "domain": "massless scalar Laplacian on round S7", "scale_status": "dimensionless ratio only"}, "ordinary_interference": "ESTABLISHED_PHYSICS_CORRESPONDENCE", "future_mode_selection": "BHSM_CANDIDATE", "frozen_theory_result": "BHSM_HARMONIC_ENVELOPMENT_SELECTION_NOT_DERIVED", "not_implied": ["universal physicality trigger", "particle hierarchy", "generation theorem", "absolute scale", "nonlinear resonance", "physical interaction"]}


def sigma_payload() -> dict[str, Any]:
    return {**_common("BHSM_sigma_role_reclassification_v6_0_6"), "status": "BHSM_SIGMA_ROLE_RECLASSIFIED", "category": "BHSM_CANDIDATE", "candidate_roles": ["scalar/topographic localization", "persistent envelope phase", "boundary response", "vacuum branch", "object-stability mode", "geometric scale response"], "reduced_model": {"potential": "V_red(sigma)=-sigma^2+2 sigma^4", "A_ST": -2, "G_ST": 8, "vacuum_abs_sigma": 0.5, "status": "REDUCED_CONDITIONAL_PARENT_MAP_OPEN"}, "universal_definition_of_physicality": False, "v6_0_5_scope": "frozen free-scalar theory does not generate an autonomous nonlinear coherently selected persistent sigma!=0 phase"}


def candidate_roles() -> list[dict[str, Any]]:
    return [
        {"role": "S3 fiber of S3->S7->S4", "topology": "exact principal Sp(1) Hopf fiber", "map": "i_x:p_H^-1(x)=S3 -> S7 after x in S4 is selected", "dimension": 3, "metric_relation": "round vertical restriction for the standard round submersion; generic Berger squashing requires an unselected compatible S7 metric", "measure_relation": "conditional fiber measure after vertical scale/orientation", "operator_relation": "vertical operator only; not the full S7 Laplacian", "action_relation": "fiber restriction/integration and consistent truncation unproved", "status": "VIABLE_TOPOLOGY_REDUCTION_BLOCKED"},
        {"role": "canonical spatial slice", "topology": "no canonical three-dimensional slice of seven-dimensional S7 selected", "map": None, "dimension": 3, "metric_relation": "absent", "measure_relation": "absent", "operator_relation": "absent", "action_relation": "absent", "status": "REJECTED_AS_CURRENT_CANONICAL_ROLE"},
        {"role": "embedded submanifold of S7", "topology": "a selected Hopf fiber is an embedded S3; other embeddings are nonunique", "map": "i:S3->S7 must be explicit", "dimension": 3, "metric_relation": "i^*g_S7 must be evaluated", "measure_relation": "induced measure", "operator_relation": "ambient and intrinsic Laplacians differ by extrinsic data", "action_relation": "restriction is not automatically a consistent truncation", "status": "VIABLE_CONDITIONALLY"},
        {"role": "quotient or orbit geometry", "topology": "S7/Sp(1)=S4, not S3; another group action would be required", "map": "pi:S7->S7/G", "dimension": 3, "metric_relation": "requires selected four-dimensional orbit and submersion metric", "measure_relation": "orbit volume/Faddeev-Popov data", "operator_relation": "invariant-sector operator", "action_relation": "quotient action absent", "status": "BLOCKED_NO_GROUP_ACTION"},
        {"role": "homogeneous truncation of S7", "topology": "field-sector reduction rather than a topological identification", "map": "P_inv:Fields(S7)->retained S3-labelled sector", "dimension": 3, "metric_relation": "effective metric must follow from the projected kinetic form", "measure_relation": "normalization inherited from S7 inner product", "operator_relation": "retained subspace must be invariant", "action_relation": "discarded-mode equations must vanish", "status": "VIABLE_CONDITIONALLY"},
        {"role": "boundary mode sector", "topology": "S7 is closed, or is the seven-boundary of B8; an S3 sub-boundary is not automatic", "map": "boundary spectral projector required", "dimension": 3, "metric_relation": "induced/effective metric unproved", "measure_relation": "projected boundary measure unproved", "operator_relation": "boundary operator/domain required", "action_relation": "boundary source and conditions absent", "status": "BLOCKED"},
        {"role": "internal compact factor", "topology": "independent S3 is coherent in a product theory but is not itself the S7 reduction", "map": "product projection or selected S7 fiber", "dimension": 3, "metric_relation": "legacy Berger metric applies directly only on an independently postulated S3", "measure_relation": "product/fiber measure", "operator_relation": "Kaluza-Klein reduction required", "action_relation": "dimensionally compatible parent product action absent", "status": "STRONG_CONDITIONAL_NOT_B8_S7_BRIDGE"},
        {"role": "effective reduced configuration space", "topology": "not fixed by topology alone", "map": "quotient or collective-coordinate map required", "dimension": 3, "metric_relation": "kinetic metric must be derived", "measure_relation": "Jacobian required", "operator_relation": "effective operator required", "action_relation": "effective action derivation absent", "status": "CONDITIONAL"},
        {"role": "unrelated proxy geometry", "topology": "legacy S3 retained on its declared domain", "map": None, "dimension": 3, "metric_relation": "no asserted S7 relation", "measure_relation": "legacy measure only", "operator_relation": "legacy operator only", "action_relation": "no parent reduction claim", "status": "CURRENT_CONSERVATIVE_FALLBACK"},
    ]


def roles_payload() -> dict[str, Any]:
    return {**_common("BHSM_b8_s7_berger_s3_candidate_role_matrix_v6_0_6"), "status": REDUCTION_RESULT, "rows": candidate_roles(), "selected_role": None, "strongest_candidate": "selected quaternionic Hopf fiber plus a proved action-consistent invariant-mode truncation", "legacy_language_used_as_selection": False}


def maps_payload() -> dict[str, Any]:
    maps = [
        {"name": "Hopf projection", "symbol": "p_H:S7->S4", "status": "EXACT_TOPOLOGY", "purpose": "defines quaternionic fibers"},
        {"name": "fiber embedding", "symbol": "i_x:S3=p_H^-1(x)->S7", "status": "EXACT_AFTER_BASEPOINT", "purpose": "metric pullback and vertical fields"},
        {"name": "vertical projection", "symbol": "P_V:TS7->ker(dp_H)", "status": "REQUIRES_CONNECTION_METRIC", "purpose": "vertical metric, Hodge, and operators"},
        {"name": "fiber pushforward", "symbol": "(p_H)_*", "status": "CONDITIONAL_ORIENTATION_MEASURE_PAIRING", "purpose": "integrate vertical degrees"},
        {"name": "invariant-mode projection", "symbol": "P_inv", "status": "MISSING", "purpose": "consistent retained field sector"},
        {"name": "representation branching", "symbol": "SO(8) rep -> Hopf subgroup reps -> Berger S3 labels", "status": "MISSING", "purpose": "mode correspondence"},
        {"name": "action reduction", "symbol": "R:S_parent[B8 or R_t x S7]->S_v5[Berger S3]", "status": "MISSING", "purpose": "measure, coefficients, boundary conditions, operators"},
    ]
    return {**_common("BHSM_b8_s7_berger_s3_required_maps_v6_0_6"), "status": "REQUIRED_REDUCTION_MAPS_IDENTIFIED", "maps": maps, "pullback_pushforward_conflated": False, "reduction_complete": False}


def metric_payload() -> dict[str, Any]:
    return {**_common("BHSM_b8_s7_berger_s3_metric_measure_compatibility_v6_0_6"), "status": "ROUND_FIBER_COMPATIBLE_GENERIC_BERGER_MAP_OPEN", "standard_round_case": {"topology": "S3 fiber", "metric": "vertical restriction is round up to the declared Hopf normalization", "volume_check": "Vol(S7)=Vol(S4_radius_half)Vol(S3)=pi^4 L^7/3", "orientation": "must be declared"}, "generic_berger_case": {"metric": "g_Berger=a^2(sigma_1^2+sigma_2^2)+c^2 sigma_3^2", "equals_round_pullback": "only at the round specialization with compatible normalization", "generic_pullback_proved": False, "required_parent_data": ["explicit squashed S7 metric", "vertical/horizontal split", "connection normalization", "stationarity", "orientation"]}, "relations_not_conflated": ["g_Berger=i^*g_S7", "g_Berger=vertical metric", "g_Berger=effective pushforward metric"], "measure_normalization_proved": False, "hodge_relation_proved": False, "curvature_relation_proved": False}


def action_payload() -> dict[str, Any]:
    rows = []
    specs = [
        ("boundary geometry", "Berger-S3/collar boundary Hessian", "P1 boundary completion plus separately sourced physical interface", "induced metric/extrinsic curvature reduction", "BLOCKED"),
        ("gauge", "Berger-S3 conditional gauge action", "nested Hopf connection-curvature sector", "fiber trace and invariant connection-mode reduction", "STRUCTURALLY_COMPATIBLE"),
        ("fermion", "conditional Berger-S3 Dirac pairing", "B8/S7 spinor action", "spin structure and vertical/horizontal Dirac branching", "BLOCKED"),
        ("scalar/topographic", "reduced V_red and profile action", "parent sigma/topographic sector", "normalized fiber profile and quartic overlaps", "STRUCTURALLY_COMPATIBLE"),
        ("charged current", "conditional adjoint-paired current", "parent gauge-spinor coupling", "representation branching and coefficient trace", "BLOCKED"),
        ("neutral response", "conditional response kernel", "parent neutral field/operator", "parent field identification and spectral reduction", "BLOCKED"),
        ("scale/RG", "symbolic collar/scale bridge", "parent modulus/effective action", "dimensionful source, anomaly, and running", "BLOCKED"),
        ("recycling", "interpretive black-hole ledger", "causal parent bulk dynamics", "Lorentzian solutions, interfaces, conservation, continuation", "INCOMPATIBLE_AS_CURRENT_ACTION_TERM"),
    ]
    for sector, current, parent, operation, status in specs:
        rows.append({"sector": sector, "current_domain": current, "proposed_parent_source": parent, "reduction_operation": operation, "missing_metric_data": True, "missing_measure": True, "missing_mode_normalization": True, "missing_coefficient_source": True, "status": status, "v5_values_used_as_parent_input": False})
    return {**_common("BHSM_parent_to_v5_action_sector_map_v6_0_6"), "status": "PARENT_TO_V5_ACTION_REDUCTION_BLOCKED", "rows": rows, "reverse_engineering_used": False, "A_ST_minus_2_used_as_parent_target": False, "G_ST_8_used_as_parent_target": False}


def modes_payload() -> dict[str, Any]:
    return {**_common("BHSM_s7_to_berger_s3_mode_branching_readiness_v6_0_6"), "status": "S7_TO_BERGER_S3_REPRESENTATION_BRANCHING_PROBLEM_IDENTIFIED", "parent": {"operator": "round-S7 scalar Laplacian diagnostic", "symmetry": "SO(8)", "labels": "l plus degeneracy labels", "domain": "smooth fields on closed S7"}, "target": {"operator": "legacy Berger-S3 operators", "labels": ["q", "j", "m", "coframe/charge labels where declared"], "status": "lower-dimensional proxy until mapped"}, "required_chain": ["choose Hopf-preserving subgroup and field representation", "branch SO(8) representation to nested Hopf subgroup representations", "identify vertical Sp(1) and optional U(1) weights", "construct normalized intertwiner", "prove domain and boundary-condition compatibility", "prove operator intertwining or controlled reduction"], "numeric_eigenvalue_matching_sufficient": False, "representation_compatibility_required": True, "measure_normalization_required": True, "operator_compatibility_required": True, "branching_map": None}


def blockers_payload() -> dict[str, Any]:
    blockers = ["parent domain and action selection", "explicit stationary S7 metric and squashing convention", "selected S3 role and map", "vertical/horizontal connection normalization", "orientation and physical measure", "consistent field truncation", "representation branching and normalized intertwiner", "operator and Hodge compatibility", "boundary conditions and variational completion", "parent coefficient sources", "parent-to-v5 scalar/gauge/fermion coefficient map"]
    return {**_common("BHSM_b8_s7_berger_s3_reduction_blockers_v6_0_6"), "status": REDUCTION_STATUS, "blockers": blockers, "topology_alone_sufficient": False, "round_fiber_topology_available": True, "generic_berger_metric_derived": False, "consistent_truncation_derived": False, "action_reduction_derived": False, "exact_next_theorem": "B8/S7 parent geometry -> selected S3 role -> Berger metric -> measure and Hodge structure -> operators and spectra -> reduced action -> v5 coefficient map"}


def roadmap_payload() -> dict[str, Any]:
    steps = ["freeze correspondence and ontology", "derive B8/S7-to-Berger-S3 reduction", "derive lower-dimensional action and coefficient map", "derive Hopf connection and scalar/topographic sectors", "close fermion operator and domains", "derive topological or spectral particle sectors", "derive gauge normalization and geometric aperture", "derive generations, masses, CKM, PMNS, and neutral scales", "close quantum effective action and running", "freeze predictions before comparison", "pass full completion gate"]
    return {**_common("BHSM_full_bhsm_roadmap_v6_0_6"), "status": "FULL_BHSM_ROADMAP_CORRECTED", "steps": [{"index": i + 1, "step": step, "complete": i == 0} for i, step in enumerate(steps)], "next_gate": steps[1], "established_physics_must_be_rediscovered": False, "completion_gate_status": "FULL_BHSM_NOT_COMPLETE"}


def audit_payload() -> dict[str, Any]:
    return {**_common("BHSM_correspondence_hidden_input_claim_audit_v6_0_6"), "status": "NO_NEW_HIDDEN_PHYSICAL_INPUTS", "correspondence_inputs": ["standard conservation language", "standard wave/interference terminology", "standard Hopf bundle mathematics"], "not_used": ["measured masses", "measured gauge couplings", "fine-structure calibration", "CKM/PMNS fitting", "neutrino limits", "cosmological parameters", "absolute length or energy scale"], "unresolved_choices": ["parent action coefficients", "S7 metric/squashing", "S3 role", "map and representation branching", "mode normalization", "physical measure", "coefficient reduction"], "observable_calculation_changed": False, "historical_artifacts_rewritten": False}


def report_payload() -> dict[str, Any]:
    return {**_common("BHSM_correspondence_novelty_firewall_report_v6_0_6"), "status": PRIMARY_RESULT, "ontology_result": "BHSM_PHYSICALITY_ONTOLOGY_FROZEN", "correspondence_result": "BHSM_ESTABLISHED_PHYSICS_CORRESPONDENCE_REGISTRY_DERIVED", "novelty_result": "BHSM_NOVELTY_CLAIM_FIREWALL_DERIVED", "harmonic_result": "BHSM_HARMONIC_ROLE_RECLASSIFIED", "sigma_result": "BHSM_SIGMA_ROLE_RECLASSIFIED", "central_answer": "Physicality-as-envelopment is frozen as a BHSM interpretive ontology, while established compression, propagation, interference, conservation, curvature response, and gauge language are classified as correspondence rather than BHSM discoveries. The exact round-S7 octave remains a BHSM-specific diagnostic result. The strongest next mathematical bridge is a selected quaternionic Hopf-fiber role plus a metric-, measure-, operator-, representation-, and action-consistent truncation to the Berger-S3 engine; that reduction is identified but blocked.", "retained_v6_0_5_results": ["BHSM_MINIMAL_PARENT_THEORY_FAILS_PHYSICALITY_TRIGGER", "BHSM_MINIMAL_FREE_SCALAR_COHERENT_TRIGGER_FAILED", "BHSM_HARMONIC_ENVELOPMENT_SELECTION_NOT_DERIVED", "BHSM_GENERAL_ENERGY_GEOMETRY_ENVELOPMENT_REMAINS_OPEN"], "derived": ["correspondence and novelty taxonomy", "machine-readable provenance registry", "S7-to-Berger-S3 candidate-role and required-map matrix", "exact reduction blocker package", "corrected full-BHSM roadmap"], "reclassified": ["physicality as ontology rather than dynamical theorem", "compression/explosions/waves as established correspondence", "ordinary interference as correspondence and future Hopf selection as candidate", "sigma as a candidate persistent/localization variable"], "invalidated": ["BHSM rediscovered generic compression, explosions, waves, or stress conservation", "generic Berger S3 automatically equals the round S7 Hopf fiber", "numeric eigenvalue matching alone establishes mode correspondence", "v5 coefficients may be reverse-engineered into the parent action"], "still_requiring_new_mathematics": blockers_payload()["blockers"], "completion_gate_status": "V6_0_6_STOP_FIREWALL_DERIVED_REDUCTION_READY_BUT_BLOCKED", "recommended_next_branch": "bhsm-b8-s7-to-berger-s3-reduction-theorem-v6-0-7"}


def build_artifact_payloads(repo_root: Path | None = None) -> dict[str, dict[str, Any]]:
    _ = repo_root
    return {
        "ontology": ontology_payload(),
        "correspondence": correspondence_payload(),
        "reinterpretation": reinterpretation_payload(),
        "native": native_payload(),
        "firewall": firewall_payload(),
        "harmonic": harmonic_payload(),
        "sigma": sigma_payload(),
        "roles": roles_payload(),
        "maps": maps_payload(),
        "metric": metric_payload(),
        "action": action_payload(),
        "modes": modes_payload(),
        "blockers": blockers_payload(),
        "roadmap": roadmap_payload(),
        "audit": audit_payload(),
        "report": report_payload(),
    }


def materialize_artifacts(root: Path) -> list[Path]:
    target = root / "artifacts"
    target.mkdir(parents=True, exist_ok=True)
    payloads = build_artifact_payloads(root)
    written = []
    for key, filename in ARTIFACT_FILES.items():
        path = target / filename
        path.write_text(deterministic_json(payloads[key]), encoding="utf-8")
        written.append(path)
    return written


def correspondence_firewall_status_report(repo_root: Path | None = None) -> dict[str, Any]:
    report = report_payload()
    report["artifacts"] = {key: f"artifacts/{name}" for key, name in ARTIFACT_FILES.items()}
    return report


def correspondence_firewall_status_to_markdown(report: dict[str, Any]) -> str:
    return "\n".join([
        "# BHSM v6.0.6 Correspondence, Ontology, and Novelty Firewall",
        "",
        f"Primary result: `{report['primary_result']}`.",
        f"Reduction readiness: `{report['reduction_readiness_result']}`.",
        f"Reduction status: `{report['reduction_status']}`.",
        "",
        report["central_answer"],
        "",
        f"Completion gate: `{report['completion_gate_status']}`.",
    ]) + "\n"
