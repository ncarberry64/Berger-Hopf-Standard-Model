from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


PHASE_THREE_L_INPUTS = {
    "bounded_feynrules_prep_lagrangian": "artifacts/BHSM_bounded_feynrules_prep_lagrangian_v1_2.json",
    "minimal_runtime_parameter_requirements": "artifacts/BHSM_minimal_runtime_parameter_requirements_v1_2.json",
    "phase_three_j_gate_status": "artifacts/BHSM_phase_three_j_gate_status_v1_2.json",
    "minimal_feynrules_model_export_attempt": "artifacts/BHSM_minimal_feynrules_model_export_attempt_v1_3.json",
    "feynrules_to_ufo_export_contract": "artifacts/BHSM_feynrules_to_ufo_export_contract_v1_3.json",
    "madgraph_smoke_test_plan": "artifacts/BHSM_madgraph_smoke_test_plan_v1_3.json",
    "software_track_readiness_gates": "artifacts/BHSM_software_track_readiness_gates_v1_3.json",
    "phase_three_k_gate_status": "artifacts/BHSM_phase_three_k_gate_status_v1_3.json",
}


def load_required(relative: str) -> dict[str, Any]:
    path = ROOT / relative
    if not path.exists():
        raise FileNotFoundError(f"Missing required Phase Three-J/K artifact: {relative}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_phase_three_l_inputs() -> dict[str, dict[str, Any]]:
    return {name: load_required(relative) for name, relative in PHASE_THREE_L_INPUTS.items()}


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
    return list(PHASE_THREE_L_INPUTS.values())


def disabled_model_path() -> str:
    return "models/feynrules/BHSM_Minimal_Collider_Interface.fr.disabled"


def model_text() -> str:
    return (ROOT / disabled_model_path()).read_text(encoding="utf-8")


def which(name: str) -> str | None:
    return shutil.which(name)


def detect_version(command: list[str]) -> str:
    try:
        result = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return "unknown"
    output = (result.stdout or result.stderr).strip().splitlines()
    return output[0] if output else "unknown"


def component(component: str, executable: str | None, required_for: list[str], blocks: bool, notes: str) -> dict[str, object]:
    detected = executable is not None and which(executable) is not None
    version = detect_version([executable, "--version"]) if detected and executable else "not_detected"
    return {
        "component": component,
        "detected": detected,
        "version": version,
        "detection_method": f"PATH lookup for {executable}" if executable else "manual/artifact lookup",
        "required_for": required_for,
        "blocks_if_missing": blocks,
        "notes": notes,
    }

