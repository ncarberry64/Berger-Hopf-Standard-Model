from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PHASE = "PHASE_THREE_M_LIVE_FEYNRULES_VALIDATION"
RELEASE_BASIS = "v1.0.1"

PHASE_THREE_M_INPUTS = {
    "disabled_model": "models/feynrules/BHSM_Minimal_Collider_Interface.fr.disabled",
    "l_syntax_contract": "artifacts/BHSM_feynrules_syntax_contract_v1_4.json",
    "l_runner_package": "artifacts/BHSM_feynrules_export_runner_package_v1_4.json",
    "l_preflight": "artifacts/BHSM_software_environment_preflight_v1_4.json",
    "l_ufo_runner_contract": "artifacts/BHSM_ufo_export_runner_contract_v1_4.json",
    "l_madgraph_runner_contract": "artifacts/BHSM_madgraph_smoke_runner_contract_v1_4.json",
    "l_gate_status": "artifacts/BHSM_phase_three_l_gate_status_v1_4.json",
    "feynrules_check_script": "scripts/feynrules/check_bhsm_minimal_model.m",
    "feynrules_export_script": "scripts/feynrules/export_bhsm_minimal_to_ufo.m",
    "madgraph_smoke_script": "scripts/madgraph/import_bhsm_minimal_ufo_smoke.mg5",
}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def load_required(relative: str) -> dict[str, Any]:
    path = ROOT / relative
    if not path.exists():
        raise FileNotFoundError(f"Missing required Phase Three-L input: {relative}")
    return json.loads(path.read_text(encoding="utf-8"))


def ensure_file(relative: str) -> Path:
    path = ROOT / relative
    if not path.exists():
        raise FileNotFoundError(f"Missing required Phase Three-M input file: {relative}")
    return path


def load_phase_three_l_artifacts() -> dict[str, dict[str, Any]]:
    return {
        name: load_required(relative)
        for name, relative in PHASE_THREE_M_INPUTS.items()
        if relative.endswith(".json")
    }


def guardrails() -> dict[str, bool]:
    return {
        "empirical_derivation_inputs_used": False,
        "empirical_runtime_inputs_allowed_in_collider_mode": True,
        "boundary_predictions_modified_by_runtime_inputs": False,
        "boundary_predictions_modified_by_comparison": False,
        "official_predictions_changed": False,
        "source_model_files_changed": False,
    }


def disabled_model_path() -> str:
    return PHASE_THREE_M_INPUTS["disabled_model"]


def enabled_model_path() -> str:
    return "models/feynrules/BHSM_Minimal_Collider_Interface.fr"


def candidate_enabled_model_path() -> str:
    return "runs/feynrules_validation/BHSM_Minimal_Collider_Interface.candidate.unvalidated.fr"


def ufo_output_directory() -> str:
    return "models/ufo/BHSM_Minimal_Collider_Interface"


def model_text() -> str:
    return ensure_file(disabled_model_path()).read_text(encoding="utf-8")


def which_any(names: list[str]) -> tuple[str | None, str | None]:
    for name in names:
        path = shutil.which(name)
        if path:
            return name, path
    return None, None


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
    lines = (result.stdout or result.stderr).strip().splitlines()
    return lines[0] if lines else "unknown"


def component(
    name: str,
    executables: list[str],
    required_for: list[str],
    blocks: bool,
    notes: str,
    *,
    version_args: list[str] | None = None,
    manual_detected: bool | None = None,
    manual_path: str | None = None,
    manual_method: str | None = None,
) -> dict[str, Any]:
    executable, path = which_any(executables)
    detected = path is not None
    if manual_detected is not None:
        detected = manual_detected
        path = manual_path
        executable = manual_path or None
    if detected and executable and path and manual_detected is None:
        args = version_args if version_args is not None else ["--version"]
        version = detect_version([executable, *args])
    else:
        version = "not_detected"
    return {
        "component": name,
        "detected": detected,
        "version_if_available": version,
        "path_if_available": path or "not_detected",
        "detection_method": manual_method or f"PATH lookup for {', '.join(executables)}",
        "required_for": required_for,
        "blocks_if_missing": blocks,
        "notes": notes,
    }


def feynrules_detected_from_environment() -> tuple[bool, str | None, str]:
    for key in ["FEYNRULES_PATH", "FEYNRULES_HOME"]:
        value = os.environ.get(key)
        if value and Path(value).exists():
            return True, value, f"environment variable {key}"
    common = [
        ROOT / "FeynRules",
        Path.home() / "FeynRules",
        Path.home() / "Documents" / "FeynRules",
    ]
    for path in common:
        if path.exists():
            return True, str(path), "local directory heuristic"
    return False, None, "manual/path heuristic"


def environment_preflight_entries() -> list[dict[str, Any]]:
    fr_detected, fr_path, fr_method = feynrules_detected_from_environment()
    return [
        component(
            "python",
            ["python", "py"],
            ["repository exporters", "static checks", "runner wrappers"],
            True,
            "Python is available for repository tooling.",
            manual_detected=True,
            manual_path=str(Path(os.__file__).parent),
            manual_method="current Python interpreter",
        ),
        component(
            "mathematica_kernel",
            ["WolframKernel", "MathKernel"],
            ["FeynRules syntax validation", "model loading"],
            True,
            "Required for live FeynRules execution.",
        ),
        component(
            "wolframscript",
            ["wolframscript"],
            ["scripted Mathematica/FeynRules execution"],
            True,
            "Required for the repository runner scripts.",
        ),
        component(
            "feynrules",
            [],
            ["FeynRules package loading", "Feynman rule generation", "UFO export"],
            True,
            "FeynRules is a Mathematica package; PATH detection alone is insufficient.",
            manual_detected=fr_detected,
            manual_path=fr_path,
            manual_method=fr_method,
        ),
        component(
            "feynarts_optional",
            [],
            ["optional diagram/form-factor workflows"],
            False,
            "Optional FeynArts package detection is not required for Phase Three-M.",
            manual_detected=False,
            manual_method="manual/path heuristic",
        ),
        component(
            "madgraph",
            ["mg5_aMC", "mg5", "MadGraph5_aMCatNLO"],
            ["MadGraph UFO import", "MadGraph smoke process"],
            True,
            "Required for actual MadGraph smoke tests.",
        ),
        component(
            "hepmc_optional",
            ["hepmc3-config", "HepMC3-config"],
            ["optional HepMC event-output validation"],
            False,
            "Optional until event generation exists.",
        ),
        component(
            "root_optional",
            ["root-config"],
            ["optional analysis and plotting checks"],
            False,
            "ROOT is optional for this runner package.",
        ),
    ]


def preflight_by_component() -> dict[str, dict[str, Any]]:
    return {entry["component"]: entry for entry in environment_preflight_entries()}


def excluded_vertices_confirmed() -> bool:
    text = model_text()
    return all(
        phrase in text
        for phrase in [
            "This excludes charged boundary response, neutral kernel, and standalone CP holonomy vertices",
            "BHSM_MINIMAL_COLLIDER_INTERFACE",
            "This is not the complete BHSM 4D Lagrangian",
        ]
    ) and all(token not in text for token in ["C_ch_boundary", "K_nu neutral", "O_int"])


def forbidden_content_confirmed_absent() -> bool:
    text = model_text().lower()
    forbidden = [
        "80.379",
        "91.1876",
        "125.10",
        "172.76",
        "fake width",
        "lhe generated",
        "hepmc generated",
        "athena ready",
        "cmssw ready",
        "official cern",
    ]
    return all(token not in text for token in forbidden)


def common_payload() -> dict[str, Any]:
    return {
        "release_basis": RELEASE_BASIS,
        "phase": PHASE,
        **guardrails(),
    }

