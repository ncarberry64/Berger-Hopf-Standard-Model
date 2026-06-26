from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def load_required(relative: str) -> dict[str, Any]:
    path = ROOT / relative
    if not path.exists():
        raise FileNotFoundError(f"Missing required Phase Three-C artifact: {relative}")
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def guardrails() -> dict[str, bool]:
    return {
        "empirical_derivation_inputs_used": False,
        "boundary_predictions_modified_by_comparison": False,
        "official_predictions_changed": False,
        "source_model_files_changed": False,
    }


def phase_three_c_inputs() -> dict[str, dict[str, Any]]:
    return {
        "fields": load_required("artifacts/BHSM_explicit_4d_field_dictionary_v0_5.json"),
        "gauge": load_required("artifacts/BHSM_gauge_field_target_dictionary_v0_5.json"),
        "parameters": load_required("artifacts/BHSM_candidate_parameter_card_v0_5.json"),
        "matrices": load_required("artifacts/BHSM_boundary_source_matrices_v0_5.json"),
        "vertices": load_required("artifacts/BHSM_vertex_source_target_map_v0_5.json"),
        "gate": load_required("artifacts/BHSM_phase_three_c_gate_status_v0_5.json"),
    }
