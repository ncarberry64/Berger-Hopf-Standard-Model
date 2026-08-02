"""Canonical BHSM v11.1 obstruction and downstream completion gate."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from bhsm.interface.envelopment.relational_axioms import deterministic_json
from bhsm.interface.recovery.historical_equivalence_audit import recovery_payload

from ..current_program_status import status_payload
from .downstream_physical_gates_v11_1 import (
    buoyancy_payload,
    core_transfer_payload,
    cycle_payload,
    generation_payload,
    global_payload,
    higgs_payload,
    m4_payload,
    mass_mixing_payload,
    quantum_payload,
    three_mode_payload,
)
from .haar_scale_normalization_v11_1 import haar_scale_payload
from .support_functor_equivalence_quotient_v11_1 import equivalence_payload
from .support_representation_category_v11_1 import category_payload, functor_payload
from .supported_parent_action_v11_1 import supported_action_payload


# Historical CLI/artifact identity must not drift when the canonical current
# status advances. These are the values merged by the v11.1 campaign.
CURRENT_CAMPAIGN = "v11.1 Support representation functor and physical completion campaign"
CURRENT_VERSION = "v11.1"
PRIMARY_VERDICT = "BHSM_SUPPORT_FUNCTOR_PHYSICAL_EQUIVALENCE_QUOTIENT_BLOCKED_BY_ABSENT_COMPLETE_LOCAL_BOUNDARY_AND_CORE_ACTION_DATA"
EXACT_NEXT_OBJECT = "COMPLETE_LOCAL_SUPPORTED_ACTION_WITH_SUPPORT_DERIVATIVE_COUPLINGS_AND_BOUNDARY_CORE_CANONICAL_DOMAIN"
SOURCE_BASE_MAIN_SHA = "76ca770729d73805e79e2e6528fc735dcdd559ec"
SOURCE_BASE_TREE_SHA = "3f09b0a891b1e11ffbf8943d380df81dfb169209"
COMPLETION_MARKS = {
    "Mark_I_Canonical_ontology": "REACHED",
    "Mark_II_Complete_conditional_architecture": "NOT_REACHED",
    "Mark_III_Physical_derivation": "NOT_REACHED",
    "Mark_IV_Empirical_replacement": "NOT_REACHED",
}


ARTIFACT_FILES = {
    "support_representation_category": "BHSM_support_representation_category_v11_1.json",
    "support_representation_functor": "BHSM_support_representation_functor_v11_1.json",
    "support_functor_equivalence_quotient": "BHSM_support_functor_equivalence_quotient_v11_1.json",
    "historical_recovery": "BHSM_historical_recovery_audit_support_representation_v11_1.json",
    "haar_scale_normalization": "BHSM_haar_scale_normalization_v11_1.json",
    "supported_parent_action": "BHSM_supported_parent_action_v11_1.json",
    "core_asymptotic_transfer": "BHSM_core_asymptotic_transfer_v11_1.json",
    "three_mode_physical_action": "BHSM_three_mode_physical_action_v11_1.json",
    "nonlinear_envelopment_cycles": "BHSM_nonlinear_envelopment_cycles_v11_1.json",
    "topological_buoyancy": "BHSM_topological_buoyancy_v11_1.json",
    "higgs_buoyancy_mode": "BHSM_higgs_buoyancy_mode_v11_1.json",
    "global_geometry_scale": "BHSM_global_geometry_scale_v11_1.json",
    "generation_monodromy": "BHSM_generation_monodromy_v11_1.json",
    "physical_mass_mixing": "BHSM_physical_mass_mixing_v11_1.json",
    "effective_m4_reduction": "BHSM_effective_m4_reduction_v11_1.json",
    "quantum_core_measurement": "BHSM_quantum_core_measurement_v11_1.json",
    "current_program_status": "BHSM_current_program_status_v11_1.json",
    "completion": "BHSM_final_completion_gate_v11_1.json",
}


def completion_payload() -> dict[str, Any]:
    category = category_payload()
    functor = functor_payload()
    equivalence = equivalence_payload()
    recovery = recovery_payload()
    haar = haar_scale_payload()
    action = supported_action_payload()
    core = core_transfer_payload()
    three_mode = three_mode_payload()
    cycles = cycle_payload()
    buoyancy = buoyancy_payload()
    higgs = higgs_payload()
    global_result = global_payload()
    generations = generation_payload()
    mass_mixing = mass_mixing_payload()
    m4 = m4_payload()
    quantum = quantum_payload()
    current = status_payload()
    validation = {
        "category_presented": category["validation_passed"],
        "provisional_lifts_materialized": functor["validation_passed"] and functor["unique_fixed_character_representative"] is False,
        "physical_inequivalence_not_overclaimed": equivalence["validation_passed"] and not equivalence["physically_inequivalent_theories_proven"],
        "historical_recovery_complete_before_blocker": recovery["validation_passed"] and recovery["historical_routes_exhausted"],
        "all_haar_routes_exhausted": haar["validation_passed"] and haar["lambda_D"] is None,
        "supported_action_fail_closed": action["validation_passed"] and action["unique_complete_formula"] is None,
        "core_transfer_withheld": core["transfer_operator"] is None,
        "three_mode_withheld": three_mode["physical_hessian"] is None,
        "cycles_withheld": cycles["stable_physical_cycles"] == 0,
        "buoyancy_withheld": buoyancy["mass_functional"] is None,
        "higgs_withheld": higgs["physical_scalar"] is None,
        "global_scale_withheld": global_result["global_curvature_radius"] is None,
        "frozen_ledgers_unchanged": generations["frozen_ledgers_changed"] is False,
        "mass_mixing_withheld": mass_mixing["physical_masses"] is None and mass_mixing["CKM"] is None and mass_mixing["PMNS"] is None,
        "m4_withheld": m4["normalized_reduction"] is None,
        "quantum_withheld": quantum["probability_rule"] is None,
        "no_particle_inputs": not current["measured_particle_inputs"],
        "no_new_fields_or_parameters": not current["new_geometric_fields"] and not current["new_continuous_physical_parameters"],
    }
    return {
        "artifact": "BHSM_final_completion_gate_v11_1",
        "version": CURRENT_VERSION,
        "campaign": CURRENT_CAMPAIGN,
        "source_base_main_sha": SOURCE_BASE_MAIN_SHA,
        "source_base_tree_sha": SOURCE_BASE_TREE_SHA,
        "primary_verdict": PRIMARY_VERDICT,
        "exact_next_object": EXACT_NEXT_OBJECT,
        "support_representation_category": category,
        "support_representation_functor": functor,
        "support_functor_equivalence_quotient": equivalence,
        "historical_recovery": recovery,
        "haar_scale_normalization": haar,
        "supported_parent_action": action,
        "core_asymptotic_transfer": core,
        "three_mode_physical_action": three_mode,
        "nonlinear_envelopment_cycles": cycles,
        "topological_buoyancy": buoyancy,
        "higgs_buoyancy_mode": higgs,
        "global_geometry_scale": global_result,
        "generation_monodromy": generations,
        "physical_mass_mixing": mass_mixing,
        "effective_m4_reduction": m4,
        "quantum_core_measurement": quantum,
        "current_program_status": current,
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
        "physical_outputs_withheld": ["masses", "CKM", "PMNS", "core amplitudes", "quantum probabilities", "normalized M4 vertices"],
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def artifact_payloads() -> dict[str, dict[str, Any]]:
    completion = completion_payload()
    return {
        key: completion[key]
        for key in ARTIFACT_FILES
        if key != "completion"
    } | {"completion": completion}


def canonical_completion_gate_payload() -> dict[str, Any]:
    from bhsm.interface.envelopment.final_physical_gate_v11_0 import canonical_completion_gate_payload as prior_gate

    gate = prior_gate()
    result = completion_payload()
    gate.update(
        {
            "version": CURRENT_VERSION,
            "sprint": "bhsm-support-representation-physical-completion-v11-1",
            "source_main_sha": SOURCE_BASE_MAIN_SHA,
            "current_verdict": PRIMARY_VERDICT,
            "next_highest_upstream_blocker": EXACT_NEXT_OBJECT,
            "support_representation_functor_action_owned": False,
            "support_functor_equivalence_quotient_complete": False,
            "haar_scale_action_fixed": False,
            "three_mode_action_complete": False,
            "physical_particle_cycles_complete": False,
            "physical_mass_mixing_complete": False,
            "BHSM_1_0_release_complete": False,
            "completion_marks": COMPLETION_MARKS,
            "new_fields_in_v11_1": [],
            "new_continuous_parameters_in_v11_1": [],
            "frozen_predictions_changed": False,
            "validation_passed": result["validation_passed"],
        }
    )
    gate["RB15"] = {"status": "BLOCKED_BY_NONUNIQUE_SUPPORT_FUNCTOR", "resolution": EXACT_NEXT_OBJECT}
    gate["RB16"] = {"status": "DOWNSTREAM_BLOCKED", "resolution": "no physical output is licensed"}
    return gate


COMMAND_SECTIONS = {
    "support-category-status-v11-1": "support_representation_category",
    "support-functor-status-v11-1": "support_representation_functor",
    "support-equivalence-status-v11-1": "support_functor_equivalence_quotient",
    "haar-scale-status-v11-1": "haar_scale_normalization",
    "supported-action-status-v11-1": "supported_parent_action",
    "core-transfer-status-v11-1": "core_asymptotic_transfer",
    "three-mode-status-v11-1": "three_mode_physical_action",
    "buoyancy-higgs-status-v11-1": "topological_buoyancy",
    "global-scale-status-v11-1": "global_geometry_scale",
    "generation-status-v11-1": "generation_monodromy",
    "mass-mixing-status-v11-1": "physical_mass_mixing",
    "effective-m4-status-v11-1": "effective_m4_reduction",
    "quantum-measurement-status-v11-1": "quantum_core_measurement",
    "physical-completion-status-v11-1": None,
}


def command_payload(command: str) -> dict[str, Any]:
    if command not in COMMAND_SECTIONS:
        raise ValueError(f"unknown v11.1 status command: {command}")
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
    return "\n".join(
        [
            f"# BHSM v11.1 {command}",
            "",
            f"Primary verdict: `{data['primary_verdict']}`",
            "",
            "- Stratified category presented: `true`",
            "- Unique action-derived support functor: `false`",
            "- Haar scale action-fixed: `false`",
            "- Physical derivation complete: `false`",
            "- Frozen predictions changed: `false`",
            "",
            "## Exact next object",
            "",
            f"`{data['exact_next_object']}`",
        ]
    ) + "\n"


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
    docs = repository / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    current = status_payload()
    (docs / "current_bhsm_status.json").write_text(
        deterministic_json(current), encoding="utf-8", newline="\n"
    )
    # Markdown status pages intentionally preserve theorem-era chronology used
    # by compatibility tests and reviewers. Materialization updates only typed
    # JSON; the concise v11.1 block is maintained in those append-only pages.
    return paths
