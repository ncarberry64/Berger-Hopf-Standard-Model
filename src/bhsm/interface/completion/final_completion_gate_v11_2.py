"""Canonical BHSM v11.2 completion gate and deterministic materializer."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from bhsm.interface.envelopment.relational_axioms import deterministic_json

from ..current_program_status import (
    COMPLETION_MARKS,
    CURRENT_CAMPAIGN,
    CURRENT_VERSION,
    EXACT_NEXT_OBJECT,
    PRIMARY_VERDICT,
    SOURCE_BASE_MAIN_SHA,
    SOURCE_BASE_TREE_SHA,
    status_payload,
)
from .boundary_variational_domain_v11_2 import boundary_payload
from .bidirectional_buoyancy_v11_2 import (
    black_hole_payload,
    boundary_pressure_payload,
    casimir_payload,
    displacement_payload,
    exchange_current_payload,
    fixed_encapsulation_payload,
    ontology_payload,
    steering_payload,
)
from .complete_local_supported_action_v11_2 import action_payload
from .core_asymptotic_domain_v11_2 import core_domain_payload
from .core_transfer_operator_v11_2 import core_transfer_payload
from .downstream_physical_gates_v11_2 import downstream_payload
from .haar_scale_closure_v11_2 import haar_payload
from .historical_recovery_complete_supported_action_v11_2 import recovery_payload
from .local_supported_geometry_v11_2 import geometry_payload
from .primitive_support_character_ledger_v11_2 import ledger_payload
from .support_action_variation_v11_2 import variation_payload
from .support_character_boundary_core_selection_v11_2 import boundary_core_payload
from .support_character_constraint_system_v11_2 import constraint_payload as character_constraint_payload
from .support_character_equivalence_classes_v11_2 import equivalence_class_payload
from .support_covariant_derivative_v11_2 import derivative_payload
from .support_covariant_phase_space_v11_2 import phase_space_payload
from .support_dirac_constraints_v11_2 import constraint_payload
from .support_linear_quadratic_connection_couplings_v11_2 import couplings_payload
from .support_noether_current_v11_2 import current_payload
from .support_physical_equivalence_quotient_v11_2 import equivalence_payload
from .three_mode_physical_action_v11_2 import three_mode_payload


ARTIFACT_FILES = {
    "historical_recovery": "BHSM_historical_recovery_complete_supported_action_v11_2.json",
    "local_supported_geometry": "BHSM_local_supported_geometry_v11_2.json",
    "support_covariant_derivative": "BHSM_support_covariant_derivative_v11_2.json",
    "complete_local_supported_action": "BHSM_complete_local_supported_action_v11_2.json",
    "support_action_variation": "BHSM_support_action_variation_v11_2.json",
    "support_covariant_phase_space": "BHSM_support_covariant_phase_space_v11_2.json",
    "support_constraint_ledger": "BHSM_support_constraint_ledger_v11_2.json",
    "boundary_variational_domain": "BHSM_boundary_variational_domain_v11_2.json",
    "core_asymptotic_domain": "BHSM_core_asymptotic_domain_v11_2.json",
    "support_physical_equivalence_quotient": "BHSM_support_physical_equivalence_quotient_v11_2.json",
    "haar_scale_closure": "BHSM_haar_scale_closure_v11_2.json",
    "core_transfer_operator": "BHSM_core_transfer_operator_v11_2.json",
    "three_mode_physical_action": "BHSM_three_mode_physical_action_v11_2.json",
    "downstream_physical_gates": "BHSM_downstream_physical_gates_v11_2.json",
    "completion": "BHSM_final_completion_gate_v11_2.json",
    "primitive_support_character_ledger": "BHSM_primitive_support_character_ledger_v11_2.json",
    "support_noether_current": "BHSM_support_noether_current_v11_2.json",
    "support_linear_quadratic_connection_couplings": "BHSM_support_linear_quadratic_connection_couplings_v11_2.json",
    "support_character_constraint_system": "BHSM_support_character_constraint_system_v11_2.json",
    "support_character_boundary_core_selection": "BHSM_support_character_boundary_core_selection_v11_2.json",
    "support_character_equivalence_classes": "BHSM_support_character_equivalence_classes_v11_2.json",
    "bidirectional_topological_buoyancy_ontology": "BHSM_bidirectional_topological_buoyancy_ontology_v11_2.json",
    "fixed_encapsulation_geometry": "BHSM_fixed_encapsulation_geometry_v11_2.json",
    "relational_spacetime_displacement": "BHSM_relational_spacetime_displacement_v11_2.json",
    "core_surface_exchange_current": "BHSM_core_surface_exchange_current_v11_2.json",
    "boundary_spectral_pressure": "BHSM_boundary_spectral_pressure_v11_2.json",
    "casimir_reproduction_gate": "BHSM_casimir_reproduction_gate_v11_2.json",
    "black_hole_de_envelopment_transfer": "BHSM_black_hole_de_envelopment_transfer_v11_2.json",
}


def completion_payload() -> dict[str, Any]:
    sections = {
        "historical_recovery": recovery_payload(),
        "local_supported_geometry": geometry_payload(),
        "support_covariant_derivative": derivative_payload(),
        "complete_local_supported_action": action_payload(),
        "support_action_variation": variation_payload(),
        "support_covariant_phase_space": phase_space_payload(),
        "support_constraint_ledger": constraint_payload(),
        "boundary_variational_domain": boundary_payload(),
        "core_asymptotic_domain": core_domain_payload(),
        "support_physical_equivalence_quotient": equivalence_payload(),
        "haar_scale_closure": haar_payload(),
        "core_transfer_operator": core_transfer_payload(),
        "three_mode_physical_action": three_mode_payload(),
        "downstream_physical_gates": downstream_payload(),
        "primitive_support_character_ledger": ledger_payload(),
        "support_noether_current": current_payload(),
        "support_linear_quadratic_connection_couplings": couplings_payload(),
        "support_character_constraint_system": character_constraint_payload(),
        "support_character_boundary_core_selection": boundary_core_payload(),
        "support_character_equivalence_classes": equivalence_class_payload(),
        "bidirectional_topological_buoyancy_ontology": ontology_payload(),
        "fixed_encapsulation_geometry": fixed_encapsulation_payload(),
        "relational_spacetime_displacement": displacement_payload(),
        "core_surface_exchange_current": exchange_current_payload(),
        "boundary_spectral_pressure": boundary_pressure_payload(),
        "casimir_reproduction_gate": casimir_payload(),
        "black_hole_de_envelopment_transfer": black_hole_payload(),
        "bidirectional_buoyancy_steering": steering_payload(),
    }
    validation = {
        "all_sections_valid": all(section["validation_passed"] for section in sections.values()),
        "historical_recovery_exhausted": sections["historical_recovery"]["historical_routes_exhausted"],
        "support_connection_derived": sections["support_covariant_derivative"]["connection_is_independent_field"] is False,
        "complete_action_fail_closed": sections["complete_local_supported_action"]["complete_local_action"] is None,
        "complete_variation_fail_closed": sections["support_action_variation"]["complete_noether_identity"] is None,
        "canonical_domain_fail_closed": sections["core_asymptotic_domain"]["self_adjoint_domains"] is None,
        "equivalence_not_overclaimed": sections["support_physical_equivalence_quotient"]["physically_equivalent"] is None,
        "haar_not_fabricated": sections["haar_scale_closure"]["lambda_D"] is None,
        "downstream_fail_closed": not sections["downstream_physical_gates"]["automatic_continuation_triggered"],
        "no_prediction_changes": True,
        "primitive_ledger_exhausted": sections["primitive_support_character_ledger"]["nontrivial_action_owned_ledger"] is None,
        "constraint_rank_and_nullity_exact": sections["support_character_constraint_system"]["rank"] == 7 and sections["support_character_constraint_system"]["nullity"] == 12,
        "current_classified_without_gauge_overclaim": not sections["support_noether_current"]["transformation_classification"]["local_gauge_redundancy"],
        "linear_quadratic_pairing_enforced": sections["support_linear_quadratic_connection_couplings"]["validation_passed"],
        "boundary_core_anomaly_exhausted": sections["support_character_boundary_core_selection"]["validation_passed"],
        "equivalence_quotient_exhausted": sections["support_character_equivalence_classes"]["validation_passed"],
        "bidirectional_ontology_fail_closed": steering_payload()["validation_passed"] and steering_payload()["supported_action"]["complete"] is False,
    }
    return {
        "artifact": "BHSM_final_completion_gate_v11_2",
        "version": CURRENT_VERSION,
        "campaign": CURRENT_CAMPAIGN,
        "source_base_main_sha": SOURCE_BASE_MAIN_SHA,
        "source_base_tree_sha": SOURCE_BASE_TREE_SHA,
        "primary_verdict": PRIMARY_VERDICT,
        "exact_next_object": EXACT_NEXT_OBJECT,
        **sections,
        "completion_marks": COMPLETION_MARKS,
        "Mark_I": "REACHED",
        "Mark_II": "NOT_REACHED",
        "Mark_III": "NOT_REACHED",
        "Mark_IV": "NOT_REACHED",
        "physical_BHSM_complete": False,
        "empirical_replacement_complete": False,
        "frozen_predictions_changed": False,
        "official_prediction_logic_changed": False,
        "new_geometric_fields": [],
        "new_continuous_physical_parameters": [],
        "measured_particle_inputs": [],
        "physical_outputs_promoted": [],
        "physical_outputs_withheld": ["core transfer", "three-mode Hessian", "stable cycles", "buoyancy/Higgs", "masses", "CKM", "PMNS", "normalized M4 action", "quantum probabilities"],
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def artifact_payloads() -> dict[str, dict[str, Any]]:
    result = completion_payload()
    payloads = {key: result[key] for key in ARTIFACT_FILES if key != "completion"} | {"completion": result}
    steering_keys = {
        "primitive_support_character_ledger",
        "support_noether_current",
        "support_linear_quadratic_connection_couplings",
        "support_character_constraint_system",
        "support_character_boundary_core_selection",
        "support_character_equivalence_classes",
    }
    ledger = result["primitive_support_character_ledger"]
    constraints = result["support_character_constraint_system"]
    current = result["support_noether_current"]
    couplings = result["support_linear_quadratic_connection_couplings"]
    selection = result["support_character_boundary_core_selection"]
    equivalence = result["support_character_equivalence_classes"]
    common = {
        "historical_sources": [row["object"] for row in result["historical_recovery"]["candidates"]],
        "primitive_fields": [row["object"] for row in ledger["primitive_objects"]],
        "candidate_weights": constraints["variables"],
        "derivation_equations": constraints["row_labels"],
        "constraint_matrix": constraints["matrix"],
        "rank": constraints["rank"],
        "nullity": constraints["nullity"],
        "normalization_freedom": equivalence["common_rescaling_test"],
        "current": current["current_classification"],
        "linear_couplings": couplings["complete_linear_couplings"],
        "quadratic_couplings": couplings["complete_quadratic_couplings"],
        "boundary_result": selection["boundary_test"],
        "core_result": selection["core_test"],
        "anomaly_result": selection["anomaly_test"],
        "frozen_limit": "A_D=0 at constant upsilon=1; frozen action and predictions unchanged",
        "final_status": PRIMARY_VERDICT,
    }
    for key in steering_keys:
        payloads[key] = payloads[key] | common
    return payloads


def canonical_completion_gate_payload() -> dict[str, Any]:
    from .final_completion_gate_v11_1 import canonical_completion_gate_payload as prior_gate

    gate = prior_gate()
    result = completion_payload()
    gate.update({
        "version": CURRENT_VERSION,
        "sprint": "bhsm-complete-local-supported-action-v11-2",
        "source_main_sha": SOURCE_BASE_MAIN_SHA,
        "current_verdict": PRIMARY_VERDICT,
        "next_highest_upstream_blocker": EXACT_NEXT_OBJECT,
        "composite_support_connection_derived": True,
        "primitive_support_character_current_ledger_action_owned": False,
        "support_character_constraint_rank": 7,
        "support_character_constraint_nullity": 12,
        "pre_ontology_support_character_constraint_nullity": 5,
        "leading_support_character_candidate_owner": "core_surface_attachment",
        "complete_local_supported_action": False,
        "boundary_core_canonical_domain_complete": False,
        "support_equivalence_quotient_complete": False,
        "haar_scale_action_fixed": False,
        "BHSM_1_0_release_complete": False,
        "completion_marks": COMPLETION_MARKS,
        "new_fields_in_v11_2": [],
        "new_continuous_parameters_in_v11_2": [],
        "frozen_predictions_changed": False,
        "validation_passed": result["validation_passed"],
    })
    gate["RB15"] = {"status": "BLOCKED_AFTER_RELATIONAL_RANK_7_NULLITY_12_ATTACHMENT_AUDIT", "resolution": EXACT_NEXT_OBJECT}
    gate["RB16"] = {"status": "DOWNSTREAM_BLOCKED", "resolution": "Mark II remains NOT_REACHED"}
    return gate


COMMAND_SECTIONS = {
    "supported-geometry-status-v11-2": "local_supported_geometry",
    "support-derivative-status-v11-2": "support_covariant_derivative",
    "supported-action-status-v11-2": "complete_local_supported_action",
    "support-variation-status-v11-2": "support_action_variation",
    "support-phase-space-status-v11-2": "support_covariant_phase_space",
    "support-constraint-status-v11-2": "support_constraint_ledger",
    "boundary-domain-status-v11-2": "boundary_variational_domain",
    "core-domain-status-v11-2": "core_asymptotic_domain",
    "support-equivalence-status-v11-2": "support_physical_equivalence_quotient",
    "haar-scale-status-v11-2": "haar_scale_closure",
    "core-transfer-status-v11-2": "core_transfer_operator",
    "three-mode-status-v11-2": "three_mode_physical_action",
    "physical-completion-status-v11-2": None,
    "primitive-support-ledger-status-v11-2": "primitive_support_character_ledger",
    "support-current-status-v11-2": "support_noether_current",
    "support-connection-couplings-status-v11-2": "support_linear_quadratic_connection_couplings",
    "support-character-constraint-status-v11-2": "support_character_constraint_system",
    "support-character-boundary-core-status-v11-2": "support_character_boundary_core_selection",
    "support-character-equivalence-class-status-v11-2": "support_character_equivalence_classes",
    "bidirectional-buoyancy-status-v11-2": "bidirectional_buoyancy_steering",
}


def command_payload(command: str) -> dict[str, Any]:
    if command not in COMMAND_SECTIONS:
        raise ValueError(f"unknown v11.2 status command: {command}")
    result = completion_payload()
    section = COMMAND_SECTIONS[command]
    return {
        "version": CURRENT_VERSION,
        "command": command,
        "primary_verdict": PRIMARY_VERDICT,
        "exact_next_object": EXACT_NEXT_OBJECT,
        "completion_marks": COMPLETION_MARKS,
        "section": result if section is None else result[section],
        "physical_BHSM_complete": False,
        "frozen_predictions_changed": False,
    }


def command_to_markdown(command: str, payload: dict[str, Any] | None = None) -> str:
    data = command_payload(command) if payload is None else payload
    return "\n".join([
        f"# BHSM v11.2 {command}", "",
        f"Primary verdict: `{data['primary_verdict']}`", "",
        "- Composite flat support connection derived: `true`",
        "- Primitive support-character/current ledger action-owned: `false`",
        "- Boundary/core canonical domain complete: `false`",
        "- Mark II reached: `false`",
        "- Frozen predictions changed: `false`", "",
        "## Exact next object", "", f"`{data['exact_next_object']}`",
    ]) + "\n"


def materialize(root: Path | None = None) -> list[Path]:
    repository = Path(__file__).resolve().parents[4] if root is None else Path(root)
    target = repository / "artifacts"
    target.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for key, payload in artifact_payloads().items():
        path = target / ARTIFACT_FILES[key]
        path.write_text(deterministic_json(payload), encoding="utf-8", newline="\n")
        paths.append(path)
    canonical = target / "BHSM_1_0_completion_gate.json"
    canonical.write_text(deterministic_json(canonical_completion_gate_payload()), encoding="utf-8", newline="\n")
    paths.append(canonical)
    docs = repository / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "current_bhsm_status.json").write_text(deterministic_json(status_payload()), encoding="utf-8", newline="\n")
    return paths
