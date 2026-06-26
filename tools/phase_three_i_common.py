from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


PHASE_THREE_I_INPUTS = {
    "explicit_4d_field_dictionary": "artifacts/BHSM_explicit_4d_field_dictionary_v0_5.json",
    "gauge_field_target_dictionary": "artifacts/BHSM_gauge_field_target_dictionary_v0_5.json",
    "candidate_parameter_card": "artifacts/BHSM_candidate_parameter_card_v0_5.json",
    "boundary_source_matrices": "artifacts/BHSM_boundary_source_matrices_v0_5.json",
    "vertex_source_target_map": "artifacts/BHSM_vertex_source_target_map_v0_5.json",
    "chiral_current_attachment_map": "artifacts/BHSM_chiral_current_attachment_map_v0_6.json",
    "phase_three_d_gate_status": "artifacts/BHSM_phase_three_d_gate_status_v0_6.json",
    "gauge_fixing_production_coupling_scheme": "artifacts/BHSM_gauge_fixing_production_coupling_scheme_v0_7.json",
    "mass_width_scheme_candidate": "artifacts/BHSM_mass_width_scheme_candidate_v0_7.json",
    "renormalization_scheme_candidate": "artifacts/BHSM_renormalization_scheme_candidate_v0_7.json",
    "phase_three_e_gate_status": "artifacts/BHSM_phase_three_e_gate_status_v0_7.json",
    "canonical_production_basis_theorem": "artifacts/BHSM_canonical_production_basis_theorem_v0_8.json",
    "runtime_parameter_modes": "artifacts/BHSM_runtime_parameter_modes_v0_8.json",
    "production_coupling_map": "artifacts/BHSM_production_coupling_map_v0_8.json",
    "mass_width_runtime_policy": "artifacts/BHSM_mass_width_runtime_policy_v0_8.json",
    "phase_three_f_gate_status": "artifacts/BHSM_phase_three_f_gate_status_v0_8.json",
    "production_vertex_table_candidate": "artifacts/BHSM_production_vertex_table_candidate_v0_9.json",
    "symbolic_4d_lagrangian_assembly_ledger": "artifacts/BHSM_symbolic_4d_lagrangian_assembly_ledger_v0_9.json",
    "vertex_readiness_matrix": "artifacts/BHSM_vertex_readiness_matrix_v0_9.json",
    "feynrules_export_blocker_table": "artifacts/BHSM_feynrules_export_blocker_table_v0_9.json",
    "runtime_parameter_dependency_table": "artifacts/BHSM_runtime_parameter_dependency_table_v0_9.json",
    "phase_three_g_gate_status": "artifacts/BHSM_phase_three_g_gate_status_v0_9.json",
    "x_ch_resolution_attempt": "artifacts/BHSM_x_ch_interaction_operator_resolution_attempt_v1_0.json",
    "neutrino_basis_scale_resolution_attempt": "artifacts/BHSM_neutrino_basis_scale_resolution_attempt_v1_0.json",
    "cp_holonomy_attachment_resolution_attempt": "artifacts/BHSM_cp_holonomy_attachment_resolution_attempt_v1_0.json",
    "bounded_vertex_promotion_audit": "artifacts/BHSM_bounded_vertex_promotion_audit_v1_0.json",
    "phase_three_h_gate_status": "artifacts/BHSM_phase_three_h_gate_status_v1_0.json",
}


def load_required(relative: str) -> dict[str, Any]:
    path = ROOT / relative
    if not path.exists():
        raise FileNotFoundError(f"Missing required Phase Three input artifact: {relative}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_phase_three_i_inputs() -> dict[str, dict[str, Any]]:
    return {name: load_required(relative) for name, relative in PHASE_THREE_I_INPUTS.items()}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def guardrails() -> dict[str, bool]:
    return {
        "empirical_derivation_inputs_used": False,
        "boundary_predictions_modified_by_runtime_inputs": False,
        "boundary_predictions_modified_by_comparison": False,
        "official_predictions_changed": False,
        "source_model_files_changed": False,
    }


def source_artifact_list() -> list[str]:
    return list(PHASE_THREE_I_INPUTS.values())


def readiness_false() -> dict[str, bool]:
    return {
        "complete_4d_lagrangian_exported": False,
        "feynrules_ready": False,
        "ufo_ready": False,
        "madgraph_ready": False,
        "lhe_generation_ready": False,
        "hepmc_generation_ready": False,
        "athena_ready": False,
        "cmssw_ready": False,
    }


def runtime_policy_defined(inputs: dict[str, dict[str, Any]]) -> bool:
    status = inputs["phase_three_h_gate_status"]
    return bool(status.get("runtime_mass_width_policy_defined", False))

