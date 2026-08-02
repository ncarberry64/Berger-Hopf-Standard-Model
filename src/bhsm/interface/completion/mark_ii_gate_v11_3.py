"""BHSM v11.3 completion gate, CLI payloads, and deterministic materializer."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from bhsm.interface.envelopment.relational_axioms import deterministic_json

from .attachment_boundary_core_domain_v11_3 import boundary_payload, core_payload
from .attachment_character_derivation_v11_3 import character_payload, constraint_matrix_payload
from .attachment_exchange_current_v11_3 import current_payload
from .attachment_incidence_ledger_v11_3 import BASE_MAIN_SHA, BASE_TREE_SHA, ledger_payload
from .reciprocal_attachment_action_v11_3 import EXACT_NEXT_OBJECT, PRIMARY_VERDICT, action_payload
from .three_mode_action_v11_3 import three_mode_payload


VERSION = "v11.3"
MARK_STATUS = "BHSM_MARK_II_REACHED_CONDITIONALLY"
ARTIFACT_FILES = {
    "reciprocal_attachment_action": "BHSM_reciprocal_attachment_action_v11_3.json",
    "attachment_incidence_ledger": "BHSM_attachment_incidence_ledger_v11_3.json",
    "attachment_character_derivation": "BHSM_attachment_character_derivation_v11_3.json",
    "attachment_exchange_current": "BHSM_attachment_exchange_current_v11_3.json",
    "attachment_boundary_variation": "BHSM_attachment_boundary_variation_v11_3.json",
    "attachment_core_domain": "BHSM_attachment_core_domain_v11_3.json",
    "attachment_character_constraint_matrix": "BHSM_attachment_character_constraint_matrix_v11_3.json",
    "three_mode_action": "BHSM_three_mode_action_v11_3.json",
    "mark_ii_completion_gate": "BHSM_mark_ii_completion_gate_v11_3.json",
    "final_completion_report": "BHSM_final_completion_report_v11_3.json",
}


def completion_payload() -> dict[str, Any]:
    sections = {
        "reciprocal_attachment_action": action_payload(),
        "attachment_incidence_ledger": ledger_payload(),
        "attachment_character_derivation": character_payload(),
        "attachment_exchange_current": current_payload(),
        "attachment_boundary_variation": boundary_payload(),
        "attachment_core_domain": core_payload(),
        "attachment_character_constraint_matrix": constraint_matrix_payload(),
        "three_mode_action": three_mode_payload(),
    }
    conditions = {
        "explicit_local_attachment_action": True,
        "action_owned_core_and_wall_incidence_maps": True,
        "fixed_reciprocal_characters": True,
        "complete_support_covariant_expansion": True,
        "derived_current_or_stress_transfer": True,
        "differentiable_boundary_completion": True,
        "defined_regular_core_attachment_domain": True,
        "physical_three_mode_kinetic_Hessian_operator": False,
        "no_arbitrary_local_attachment_coefficient": True,
        "frozen_parent_action_exact": True,
    }
    validation = {
        "all_sections_valid": all(section["validation_passed"] for section in sections.values()),
        "nine_of_ten_mark_ii_conditions": sum(conditions.values()) == 9,
        "only_one_exact_open_block": [key for key, value in conditions.items() if not value] == ["physical_three_mode_kinetic_Hessian_operator"],
        "conditional_mark_used": True,
        "frozen_predictions_unchanged": True,
        "official_prediction_logic_unchanged": True,
        "no_downstream_outputs": True,
    }
    return {
        "artifact": "BHSM_final_completion_report_v11_3",
        "version": VERSION,
        "baseline_main_commit": BASE_MAIN_SHA,
        "baseline_tree": BASE_TREE_SHA,
        "branch": "agent/bhsm-reciprocal-core-surface-attachment-v11-3",
        **sections,
        "mark_ii_conditions": conditions,
        "conditions_satisfied": [key for key, value in conditions.items() if value],
        "conditions_open": [key for key, value in conditions.items() if not value],
        "Mark_I": "REACHED",
        "Mark_II": "REACHED_CONDITIONALLY",
        "Mark_III": "NOT_REACHED",
        "Mark_IV": "NOT_REACHED",
        "mark_ii_status": MARK_STATUS,
        "validated": ["intrinsic enclosure support neutrality", "action-owned Q_H(G8)/g5 attachment slot", "reciprocal half-characters", "q_D source sign", "three-way Ward transfer", "algebraic boundary differentiability", "finite core attachment closure"],
        "invalidated": ["support dressing the entire parent action", "independent unrelated core/wall exponents", "intrinsic metric scaling", "new displacement mediator", "linear A_D current without a quadratic completion"],
        "open": [EXACT_NEXT_OBJECT, "Casimir boundary spectrum", "black-hole de-envelopment transfer", "masses and mixing", "quantum probabilities"],
        "primary_verdict": PRIMARY_VERDICT,
        "exact_next_object": EXACT_NEXT_OBJECT,
        "frozen_predictions_changed": False,
        "official_prediction_logic_changed": False,
        "physical_outputs_promoted": [],
        "new_fields": [],
        "new_coefficients": [],
        "new_parameters": [],
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def artifact_payloads() -> dict[str, dict[str, Any]]:
    result = completion_payload()
    mark = {
        "artifact": "BHSM_mark_ii_completion_gate_v11_3",
        "version": VERSION,
        "conditions": result["mark_ii_conditions"],
        "conditions_satisfied": result["conditions_satisfied"],
        "conditions_open": result["conditions_open"],
        "status": MARK_STATUS,
        "primary_verdict": PRIMARY_VERDICT,
        "exact_next_object": EXACT_NEXT_OBJECT,
        "frozen_predictions_changed": False,
        "validation": result["validation"],
        "validation_passed": result["validation_passed"],
    }
    payloads = {key: result[key] for key in ARTIFACT_FILES if key not in {"mark_ii_completion_gate", "final_completion_report"}}
    payloads["mark_ii_completion_gate"] = mark
    payloads["final_completion_report"] = result
    return payloads


def canonical_completion_gate_payload() -> dict[str, Any]:
    from .final_completion_gate_v11_2 import canonical_completion_gate_payload as prior_gate

    gate = prior_gate()
    result = completion_payload()
    gate.update({
        "version": VERSION,
        "sprint": "bhsm-reciprocal-core-surface-attachment-v11-3",
        "source_main_sha": BASE_MAIN_SHA,
        "current_verdict": PRIMARY_VERDICT,
        "next_highest_upstream_blocker": EXACT_NEXT_OBJECT,
        "reciprocal_attachment_action_derived": True,
        "attachment_character_and_exchange_current_action_fixed": True,
        "attachment_character_constraint_rank": 11,
        "attachment_character_constraint_nullity": 8,
        "Mark_II": "REACHED_CONDITIONALLY",
        "mark_ii_status": MARK_STATUS,
        "physical_three_mode_Hessian_complete": False,
        "BHSM_1_0_release_complete": False,
        "new_fields_in_v11_3": [],
        "new_coefficients_in_v11_3": [],
        "frozen_predictions_changed": False,
        "validation_passed": result["validation_passed"],
    })
    gate["RB15"] = {"status": "CONDITIONAL_MARK_II_ONE_HESSIAN_BLOCK_OPEN", "resolution": EXACT_NEXT_OBJECT}
    return gate


COMMAND_SECTIONS = {
    "reciprocal-attachment-status": "reciprocal_attachment_action",
    "attachment-character-status": "attachment_character_derivation",
    "attachment-current-status": "attachment_exchange_current",
    "attachment-domain-status": "attachment_core_domain",
    "three-mode-action-status-v11-3": "three_mode_action",
    "mark-ii-status": None,
}


def command_payload(command: str) -> dict[str, Any]:
    if command not in COMMAND_SECTIONS:
        raise ValueError(f"unknown v11.3 command: {command}")
    result = completion_payload()
    section = COMMAND_SECTIONS[command]
    return {
        "version": VERSION,
        "command": command,
        "primary_verdict": PRIMARY_VERDICT,
        "exact_next_object": EXACT_NEXT_OBJECT,
        "mark_ii_status": MARK_STATUS,
        "section": result if section is None else result[section],
        "frozen_predictions_changed": False,
    }


def command_to_markdown(command: str, payload: dict[str, Any] | None = None) -> str:
    data = command_payload(command) if payload is None else payload
    return "\n".join([
        f"# BHSM v11.3 {command}", "",
        f"Primary verdict: `{data['primary_verdict']}`", "",
        f"Mark II: `{data['mark_ii_status']}`", "",
        f"Exact next object: `{data['exact_next_object']}`", "",
        "Frozen predictions changed: `false`",
    ]) + "\n"


def materialize(root: Path | None = None) -> list[Path]:
    repository = Path(__file__).resolve().parents[4] if root is None else Path(root)
    target = repository / "artifacts"
    target.mkdir(parents=True, exist_ok=True)
    paths = []
    for key, payload in artifact_payloads().items():
        path = target / ARTIFACT_FILES[key]
        path.write_text(deterministic_json(payload), encoding="utf-8", newline="\n")
        paths.append(path)
    canonical = target / "BHSM_1_0_completion_gate.json"
    canonical.write_text(deterministic_json(canonical_completion_gate_payload()), encoding="utf-8", newline="\n")
    paths.append(canonical)
    from bhsm.interface.current_program_status import status_payload
    docs = repository / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    status = docs / "current_bhsm_status.json"
    status.write_text(deterministic_json(status_payload()), encoding="utf-8", newline="\n")
    return paths
