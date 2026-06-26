from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


PHASE_THREE_K_INPUTS = {
    "minimal_bounded_lagrangian_subset": "artifacts/BHSM_minimal_bounded_lagrangian_subset_v1_2.json",
    "included_excluded_vertex_families": "artifacts/BHSM_included_excluded_vertex_families_v1_2.json",
    "bounded_feynrules_prep_lagrangian": "artifacts/BHSM_bounded_feynrules_prep_lagrangian_v1_2.json",
    "minimal_runtime_parameter_requirements": "artifacts/BHSM_minimal_runtime_parameter_requirements_v1_2.json",
    "phase_three_j_gate_status": "artifacts/BHSM_phase_three_j_gate_status_v1_2.json",
}


def load_required(relative: str) -> dict[str, Any]:
    path = ROOT / relative
    if not path.exists():
        raise FileNotFoundError(f"Missing required Phase Three-J artifact: {relative}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_phase_three_k_inputs() -> dict[str, dict[str, Any]]:
    return {name: load_required(relative) for name, relative in PHASE_THREE_K_INPUTS.items()}


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
    return list(PHASE_THREE_K_INPUTS.values())


def disabled_model_path() -> str:
    return "models/feynrules/BHSM_Minimal_Collider_Interface.fr.disabled"


def enabled_model_path() -> str:
    return "models/feynrules/BHSM_Minimal_Collider_Interface.fr"

