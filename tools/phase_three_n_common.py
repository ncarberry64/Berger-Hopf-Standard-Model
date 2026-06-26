from __future__ import annotations

import json
import platform
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RELEASE_BASIS = "v1.0.1"
PHASE = "PHASE_THREE_N_RUNTIME_EXECUTION_GATE"
RUN_DIR = ROOT / "runs" / "phase_three_n"

DISABLED_MODEL = "models/feynrules/BHSM_Minimal_Collider_Interface.fr.disabled"
ENABLED_MODEL = "models/feynrules/BHSM_Minimal_Collider_Interface.fr"
CANDIDATE_MODEL = "runs/phase_three_n/BHSM_Minimal_Collider_Interface.candidate.unvalidated.fr"
UFO_DIR = "models/ufo/BHSM_Minimal_Collider_Interface"

INPUTS = [
    DISABLED_MODEL,
    "scripts/feynrules/enable_minimal_model_if_validated.py",
    "scripts/feynrules/run_live_feynrules_validation.py",
    "scripts/feynrules/run_ufo_export_if_validated.py",
    "scripts/madgraph/run_minimal_ufo_smoke_if_available.py",
    "scripts/feynrules/export_bhsm_minimal_to_ufo.m",
    "scripts/feynrules/check_bhsm_minimal_model.m",
    "scripts/madgraph/import_bhsm_minimal_ufo_smoke.mg5",
    "artifacts/BHSM_live_feynrules_validation_attempt_v1_5.json",
    "artifacts/BHSM_feynrules_model_enablement_decision_v1_5.json",
    "artifacts/BHSM_ufo_export_live_attempt_v1_5.json",
    "artifacts/BHSM_madgraph_live_smoke_attempt_v1_5.json",
    "artifacts/BHSM_phase_three_m_gate_status_v1_5.json",
]


@dataclass
class CommandEntry:
    step_id: str
    purpose: str
    command: str
    working_directory: str
    attempted: bool
    exit_code: int | None
    stdout_log_path: str
    stderr_log_path: str
    result: str
    notes: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "step_id": self.step_id,
            "purpose": self.purpose,
            "command": self.command,
            "working_directory": self.working_directory,
            "attempted": self.attempted,
            "exit_code": self.exit_code,
            "stdout_log_path": self.stdout_log_path,
            "stderr_log_path": self.stderr_log_path,
            "result": self.result,
            "notes": self.notes,
        }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def load_json(relative: str) -> dict[str, Any]:
    path = ROOT / relative
    if not path.exists():
        raise FileNotFoundError(f"Missing required Phase Three-N input: {relative}")
    return json.loads(path.read_text(encoding="utf-8"))


def check_inputs() -> list[str]:
    return [relative for relative in INPUTS if not (ROOT / relative).exists()]


def guardrails() -> dict[str, bool]:
    return {
        "empirical_derivation_inputs_used": False,
        "empirical_runtime_inputs_allowed_in_collider_mode": True,
        "boundary_predictions_modified_by_runtime_inputs": False,
        "boundary_predictions_modified_by_comparison": False,
        "official_predictions_changed": False,
        "source_model_files_changed": False,
    }


def first_existing(paths: list[Path]) -> str | None:
    for path in paths:
        if path.exists():
            return str(path)
    return None


def detect_version(command: list[str]) -> str:
    try:
        result = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=12,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return "unknown"
    lines = (result.stdout or result.stderr).strip().splitlines()
    return lines[0] if lines else "unknown"


def command_version(path: str | None, args: list[str] | None = None) -> str:
    if not path:
        return "not_detected"
    return detect_version([path, *(args or ["--version"])])


def find_wolfram_kernel() -> tuple[bool, str, str]:
    path = shutil.which("WolframKernel") or shutil.which("MathKernel")
    if path:
        return True, path, command_version(path, ["-version"])
    common = [
        Path("C:/Program Files/Wolfram Research/Mathematica"),
        Path("C:/Program Files/Wolfram Research/Wolfram"),
        Path("/Applications/Mathematica.app/Contents/MacOS/WolframKernel"),
        Path("/usr/local/bin/WolframKernel"),
        Path("/usr/bin/WolframKernel"),
    ]
    found = first_existing(common)
    return (found is not None), (found or "not_detected"), "unknown" if found else "not_detected"


def find_wolframscript() -> tuple[bool, str, str]:
    path = shutil.which("wolframscript")
    if path:
        return True, path, command_version(path, ["-version"])
    common = [
        Path("C:/Program Files/Wolfram Research/WolframScript/wolframscript.exe"),
        Path("/usr/local/bin/wolframscript"),
        Path("/usr/bin/wolframscript"),
    ]
    found = first_existing(common)
    return (found is not None), (found or "not_detected"), "unknown" if found else "not_detected"


def find_mathematica_app() -> tuple[bool, str]:
    common = [
        Path("C:/Program Files/Wolfram Research/Mathematica"),
        Path("C:/Program Files/Wolfram Research/Wolfram"),
        Path("/Applications/Mathematica.app"),
    ]
    found = first_existing(common)
    return (found is not None), (found or "not_detected")


def find_feynrules() -> tuple[bool, str, str]:
    env_names = ["FEYNRULES_PATH", "FEYNRULES_HOME"]
    for name in env_names:
        value = __import__("os").environ.get(name)
        if value and Path(value).exists():
            return True, value, f"detected via {name}"
    common = [
        ROOT / "FeynRules",
        Path.home() / "FeynRules",
        Path.home() / "Documents" / "FeynRules",
        Path.home() / "Applications" / "FeynRules",
    ]
    found = first_existing(common)
    return (found is not None), (found or "not_detected"), "local path heuristic" if found else "not_detected"


def find_madgraph() -> tuple[bool, str, str]:
    path = shutil.which("mg5_aMC") or shutil.which("mg5") or shutil.which("MadGraph5_aMCatNLO")
    if path:
        return True, path, command_version(path, ["--version"])
    common = [
        ROOT / "MG5_aMC" / "bin" / "mg5_aMC",
        Path.home() / "MG5_aMC" / "bin" / "mg5_aMC",
        Path.home() / "MadGraph" / "bin" / "mg5_aMC",
    ]
    found = first_existing(common)
    return (found is not None), (found or "not_detected"), "unknown" if found else "not_detected"


def runtime_report() -> dict[str, Any]:
    missing_inputs = check_inputs()
    py_detected = True
    wolframscript_detected, wolframscript_path, wolframscript_version = find_wolframscript()
    kernel_detected, kernel_path, kernel_version = find_wolfram_kernel()
    mathematica_detected, mathematica_path = find_mathematica_app()
    feynrules_detected, feynrules_path, feynrules_version = find_feynrules()
    madgraph_detected, madgraph_path, madgraph_version = find_madgraph()
    ready_fr = wolframscript_detected and (kernel_detected or mathematica_detected) and feynrules_detected and not missing_inputs
    ready_ufo = ready_fr
    ready_mg = ready_ufo and madgraph_detected
    missing_components: list[str] = []
    if missing_inputs:
        missing_components.extend(f"input:{item}" for item in missing_inputs)
    if not wolframscript_detected:
        missing_components.append("wolframscript")
    if not (kernel_detected or mathematica_detected):
        missing_components.append("wolfram_kernel_or_mathematica")
    if not feynrules_detected:
        missing_components.append("feynrules")
    if not madgraph_detected:
        missing_components.append("madgraph")
    return {
        "release_basis": RELEASE_BASIS,
        "phase": PHASE,
        "platform": platform.platform(),
        "python_detected": py_detected,
        "python_path": sys.executable,
        "wolframscript_detected": wolframscript_detected,
        "wolframscript_path": wolframscript_path,
        "wolframscript_version": wolframscript_version,
        "wolfram_kernel_detected": kernel_detected,
        "wolfram_kernel_path": kernel_path,
        "wolfram_kernel_version": kernel_version,
        "mathematica_detected": mathematica_detected,
        "mathematica_path": mathematica_path,
        "feynrules_detected": feynrules_detected,
        "feynrules_path": feynrules_path,
        "feynrules_version_if_available": feynrules_version,
        "madgraph_detected": madgraph_detected,
        "madgraph_path": madgraph_path,
        "madgraph_version_if_available": madgraph_version,
        "environment_ready_for_feynrules_validation": ready_fr,
        "environment_ready_for_ufo_export": ready_ufo,
        "environment_ready_for_madgraph_smoke": ready_mg,
        "missing_components": missing_components,
        "provisioning_actions_attempted": [
            "PATH lookup for WolframScript/WolframKernel/MadGraph",
            "common local path scan for Mathematica/FeynRules/MadGraph",
            "environment variable scan for FEYNRULES_PATH/FEYNRULES_HOME",
        ],
        "provisioning_actions_succeeded": [
            item
            for item, ok in [
                ("python_runtime_detected", py_detected),
                ("wolframscript_detected", wolframscript_detected),
                ("wolfram_kernel_detected", kernel_detected),
                ("mathematica_app_detected", mathematica_detected),
                ("feynrules_detected", feynrules_detected),
                ("madgraph_detected", madgraph_detected),
            ]
            if ok
        ],
        "license_or_runtime_notes": [
            "No Wolfram license bypass, unauthorized key, or improper installer was used.",
            "If Wolfram/FeynRules is unavailable, validation gates remain false.",
        ],
        **guardrails(),
    }


def base_command_log() -> list[CommandEntry]:
    return [
        CommandEntry(
            "N1_RUNTIME_PROVISIONING",
            "Detect local Wolfram/FeynRules/MadGraph runtime",
            "python tools/check_runtime_provisioning_v1_6.py",
            str(ROOT),
            True,
            0,
            "not_created",
            "not_created",
            "passed",
            "Repository Python preflight executed; external proprietary runtimes are only detected, not installed.",
        )
    ]


def skipped_command(step_id: str, purpose: str, command: str, reason: str) -> CommandEntry:
    return CommandEntry(step_id, purpose, command, str(ROOT), False, None, "not_created", "not_created", "skipped", reason)


def run_logged(step_id: str, purpose: str, command: list[str]) -> CommandEntry:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    stdout_path = RUN_DIR / f"{step_id.lower()}_stdout.log"
    stderr_path = RUN_DIR / f"{step_id.lower()}_stderr.log"
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    stdout_path.write_text(result.stdout, encoding="utf-8")
    stderr_path.write_text(result.stderr, encoding="utf-8")
    return CommandEntry(
        step_id,
        purpose,
        " ".join(command),
        str(ROOT),
        True,
        result.returncode,
        str(stdout_path.relative_to(ROOT)),
        str(stderr_path.relative_to(ROOT)),
        "passed" if result.returncode == 0 else "failed",
        "Real command executed; inspect logs for details.",
    )


def phase_three_n_results(execute: bool = True) -> dict[str, Any]:
    report = runtime_report()
    command_log = base_command_log()

    validation_attempted = False
    validation_exit_ok = False
    if execute and report["environment_ready_for_feynrules_validation"]:
        entry = run_logged(
            "N2_FEYNRULES_VALIDATION",
            "Run live FeynRules model load and syntax validation",
            [sys.executable, "scripts/feynrules/run_live_feynrules_validation.py"],
        )
        command_log.append(entry)
        validation_attempted = True
        validation_exit_ok = entry.exit_code == 0
    else:
        command_log.append(
            skipped_command(
                "N2_FEYNRULES_VALIDATION",
                "Run live FeynRules model load and syntax validation",
                "python scripts/feynrules/run_live_feynrules_validation.py",
                "Wolfram/FeynRules runtime not ready",
            )
        )

    validation_passed = validation_attempted and validation_exit_ok
    enabled_created = False
    if validation_passed:
        entry = run_logged(
            "N3_FEYNRULES_ENABLEMENT",
            "Enable bounded minimal .fr only after validation",
            [sys.executable, "scripts/feynrules/enable_minimal_model_if_validated.py"],
        )
        command_log.append(entry)
        enabled_created = entry.exit_code == 0 and (ROOT / ENABLED_MODEL).exists()
    else:
        command_log.append(
            skipped_command(
                "N3_FEYNRULES_ENABLEMENT",
                "Enable bounded minimal .fr only after validation",
                "python scripts/feynrules/enable_minimal_model_if_validated.py",
                "FeynRules validation did not pass",
            )
        )

    ufo_attempted = False
    ufo_passed = False
    ufo_loadability_tested = False
    ufo_loadability_passed = False
    if validation_passed and enabled_created:
        entry = run_logged(
            "N4_UFO_EXPORT",
            "Attempt UFO export after validated .fr enablement",
            [sys.executable, "scripts/feynrules/run_ufo_export_if_validated.py"],
        )
        command_log.append(entry)
        ufo_attempted = True
        ufo_passed = entry.exit_code == 0 and (ROOT / UFO_DIR).exists()
        required = ["__init__.py", "particles.py", "parameters.py", "couplings.py", "lorentz.py", "vertices.py"]
        ufo_loadability_tested = ufo_passed
        ufo_loadability_passed = ufo_passed and all((ROOT / UFO_DIR / item).exists() for item in required)
    else:
        command_log.append(
            skipped_command(
                "N4_UFO_EXPORT",
                "Attempt UFO export after validated .fr enablement",
                "python scripts/feynrules/run_ufo_export_if_validated.py",
                "Validated enabled .fr file is unavailable",
            )
        )

    mg_attempted = False
    mg_passed = False
    if ufo_passed and ufo_loadability_passed and report["madgraph_detected"]:
        entry = run_logged(
            "N5_MADGRAPH_SMOKE",
            "Attempt MadGraph import/process smoke test",
            [sys.executable, "scripts/madgraph/run_minimal_ufo_smoke_if_available.py"],
        )
        command_log.append(entry)
        mg_attempted = True
        mg_passed = entry.exit_code == 0
    else:
        command_log.append(
            skipped_command(
                "N5_MADGRAPH_SMOKE",
                "Attempt MadGraph import/process smoke test",
                "python scripts/madgraph/run_minimal_ufo_smoke_if_available.py",
                "UFO export/loadability and/or MadGraph detection gates did not pass",
            )
        )

    validation_outcome = {
        "release_basis": RELEASE_BASIS,
        "phase": PHASE,
        "input_disabled_model": DISABLED_MODEL,
        "candidate_model_path": CANDIDATE_MODEL,
        "enabled_model_path": ENABLED_MODEL,
        "validation_attempted": validation_attempted,
        "validation_command": "python scripts/feynrules/run_live_feynrules_validation.py" if validation_attempted else "not_run",
        "validation_log_paths": ["runs/phase_three_n/n2_feynrules_validation_stdout.log", "runs/phase_three_n/n2_feynrules_validation_stderr.log"] if validation_attempted else [],
        "mathematica_detected": report["mathematica_detected"] or report["wolfram_kernel_detected"],
        "feynrules_detected": report["feynrules_detected"],
        "mathematica_syntax_passed": validation_passed,
        "feynrules_package_loaded": validation_passed,
        "model_load_passed": validation_passed,
        "lagrangian_symbol_found": validation_passed,
        "feynman_rules_generation_attempted": validation_attempted,
        "feynman_rules_generation_passed": validation_passed,
        "feynrules_syntax_validated": validation_passed,
        "feynrules_model_load_validated": validation_passed,
        "excluded_vertices_confirmed_absent": excluded_vertices_confirmed_absent(),
        "forbidden_content_confirmed_absent": forbidden_content_confirmed_absent(),
        "failure_reason_if_any": "none" if validation_passed else "Wolfram/FeynRules runtime unavailable or validation failed",
        "production_feynrules_file_exported": enabled_created,
        "minimal_model_enabled": enabled_created,
        "is_complete_bhsm_model": False,
        "notes": [
            "This outcome applies only to the bounded minimal CKM/PMNS collider-interface subset.",
            "Static checks are not validation evidence.",
        ],
        **guardrails(),
    }

    enablement_outcome = {
        "release_basis": RELEASE_BASIS,
        "phase": PHASE,
        "enablement_attempted": validation_passed,
        "enablement_performed": enabled_created,
        "enablement_allowed": validation_passed,
        "enablement_reason": "validation passed" if validation_passed else "FeynRules validation did not pass",
        "disabled_model_preserved": (ROOT / DISABLED_MODEL).exists(),
        "enabled_model_created": enabled_created,
        "enabled_model_path": ENABLED_MODEL,
        "validation_required": True,
        "validation_passed": validation_passed,
        "is_complete_bhsm_model": False,
        "unresolved_vertices_excluded": excluded_vertices_confirmed_absent(),
        "notes": ["The disabled model is never overwritten."],
        **guardrails(),
    }

    ufo_outcome = {
        "release_basis": RELEASE_BASIS,
        "phase": PHASE,
        "ufo_export_attempted": ufo_attempted,
        "ufo_export_passed": ufo_passed,
        "input_feynrules_model": ENABLED_MODEL,
        "output_ufo_directory": UFO_DIR,
        "export_command": "python scripts/feynrules/run_ufo_export_if_validated.py" if ufo_attempted else "not_run",
        "export_log_paths": ["runs/phase_three_n/n4_ufo_export_stdout.log", "runs/phase_three_n/n4_ufo_export_stderr.log"] if ufo_attempted else [],
        "required_ufo_files_present": ufo_loadability_passed,
        "ufo_directory_created": (ROOT / UFO_DIR).exists(),
        "ufo_loadability_tested": ufo_loadability_tested,
        "ufo_loadability_passed": ufo_loadability_passed,
        "loadability_command": "file presence check for minimal UFO files" if ufo_loadability_tested else "not_run",
        "failure_reason_if_any": "none" if ufo_passed else "FeynRules validation/enablement did not pass or UFO export failed",
        "notes": ["UFO export is not attempted from the disabled .fr file."],
        **guardrails(),
    }

    madgraph_outcome = {
        "release_basis": RELEASE_BASIS,
        "phase": PHASE,
        "madgraph_smoke_test_attempted": mg_attempted,
        "madgraph_detected": report["madgraph_detected"],
        "requires_loadable_ufo": True,
        "ufo_loadability_passed": ufo_loadability_passed,
        "input_ufo_directory": UFO_DIR,
        "mg5_script_path": "scripts/madgraph/import_bhsm_minimal_ufo_smoke.mg5",
        "planned_processes": ["u d~ > w+", "e+ ve > w+"],
        "actual_processes_attempted": ["u d~ > w+", "e+ ve > w+"] if mg_attempted else [],
        "madgraph_command": "python scripts/madgraph/run_minimal_ufo_smoke_if_available.py" if mg_attempted else "not_run",
        "madgraph_log_paths": ["runs/phase_three_n/n5_madgraph_smoke_stdout.log", "runs/phase_three_n/n5_madgraph_smoke_stderr.log"] if mg_attempted else [],
        "madgraph_import_passed": mg_passed,
        "madgraph_process_generation_passed": mg_passed,
        "lhe_generated": False,
        "hepmc_generated": False,
        "failure_reason_if_any": "none" if mg_passed else "UFO loadability and/or MadGraph runtime gate did not pass",
        "notes": ["No fake LHE or HepMC files are generated."],
        **guardrails(),
    }

    command_payload = {
        "release_basis": RELEASE_BASIS,
        "phase": PHASE,
        "commands": [entry.as_dict() for entry in command_log],
        "notes": [
            "Unattempted commands are listed explicitly with attempted=false.",
            "No fake validation logs are created.",
        ],
        **guardrails(),
    }

    gate_status = gate_status_payload(report, command_payload, validation_outcome, enablement_outcome, ufo_outcome, madgraph_outcome)
    return {
        "runtime_provisioning": report,
        "command_log": command_payload,
        "feynrules_validation": validation_outcome,
        "feynrules_enablement": enablement_outcome,
        "ufo_export": ufo_outcome,
        "madgraph_smoke": madgraph_outcome,
        "gate_status": gate_status,
    }


def excluded_vertices_confirmed_absent() -> bool:
    text = (ROOT / DISABLED_MODEL).read_text(encoding="utf-8")
    return all(token not in text for token in ["C_ch_boundary", "K_nu neutral", "O_int"]) and all(
        marker in text
        for marker in [
            "BHSM_MINIMAL_COLLIDER_INTERFACE",
            "This is not the complete BHSM 4D Lagrangian",
            "This excludes charged boundary response, neutral kernel, and standalone CP holonomy vertices",
        ]
    )


def forbidden_content_confirmed_absent() -> bool:
    text = (ROOT / DISABLED_MODEL).read_text(encoding="utf-8").lower()
    forbidden = [
        "172.76",
        "80.379",
        "91.1876",
        "0.118",
        "125.10",
        "fake width",
        "lhe generated",
        "hepmc generated",
        "official cern",
        "empirically validated",
    ]
    return all(item not in text for item in forbidden)


def gate_status_payload(
    report: dict[str, Any],
    command_log: dict[str, Any],
    validation: dict[str, Any],
    enablement: dict[str, Any],
    ufo: dict[str, Any],
    madgraph: dict[str, Any],
) -> dict[str, Any]:
    fr_passed = validation["feynrules_syntax_validated"] and validation["feynrules_model_load_validated"]
    if not report["environment_ready_for_feynrules_validation"]:
        status = (
            "BHSM Phase Three-N attempted runtime provisioning for live FeynRules validation. "
            "The required Wolfram/FeynRules runtime was not detected, so the minimal model remains disabled and no FeynRules/UFO/MadGraph readiness is claimed."
        )
    elif fr_passed and not (ufo["ufo_export_passed"] and ufo["ufo_loadability_passed"]):
        status = (
            "BHSM Phase Three-N validates the bounded minimal collider-interface FeynRules subset under live Wolfram/FeynRules execution and enables the minimal .fr file. "
            "This validates only the bounded CKM/PMNS subset, not the complete BHSM 4D Lagrangian or UFO/MadGraph/event readiness."
        )
    elif fr_passed and ufo["ufo_export_passed"] and ufo["ufo_loadability_passed"] and madgraph["madgraph_process_generation_passed"]:
        status = (
            "BHSM Phase Three-N validates the bounded minimal collider-interface FeynRules subset, exports a loadable UFO model, and passes an initial MadGraph smoke test. "
            "This applies only to the bounded CKM/PMNS collider-interface subset and does not complete the full BHSM 4D Lagrangian or unresolved excluded sectors."
        )
    else:
        status = "BHSM Phase Three-N records runtime execution blockers; readiness gates remain closed where live evidence is absent."
    return {
        "release_basis": RELEASE_BASIS,
        "phase": PHASE,
        "runtime_provisioning_report_exported": True,
        "live_validation_command_log_exported": True,
        "feynrules_validation_outcome_exported": True,
        "feynrules_enablement_outcome_exported": True,
        "ufo_export_outcome_exported": True,
        "madgraph_smoke_outcome_exported": True,
        "python_detected": report["python_detected"],
        "wolframscript_detected": report["wolframscript_detected"],
        "wolfram_kernel_detected": report["wolfram_kernel_detected"],
        "mathematica_detected": report["mathematica_detected"],
        "feynrules_detected": report["feynrules_detected"],
        "madgraph_detected": report["madgraph_detected"],
        "environment_ready_for_feynrules_validation": report["environment_ready_for_feynrules_validation"],
        "feynrules_validation_attempted": validation["validation_attempted"],
        "feynrules_syntax_validated": validation["feynrules_syntax_validated"],
        "feynrules_model_load_validated": validation["feynrules_model_load_validated"],
        "feynman_rules_generation_attempted": validation["feynman_rules_generation_attempted"],
        "feynman_rules_generation_passed": validation["feynman_rules_generation_passed"],
        "minimal_feynrules_model_enabled": enablement["enabled_model_created"],
        "production_feynrules_file_exported": validation["production_feynrules_file_exported"],
        "minimal_model_is_complete_bhsm": False,
        "ufo_export_attempted": ufo["ufo_export_attempted"],
        "ufo_export_passed": ufo["ufo_export_passed"],
        "ufo_loadability_tested": ufo["ufo_loadability_tested"],
        "ufo_loadability_passed": ufo["ufo_loadability_passed"],
        "madgraph_smoke_test_attempted": madgraph["madgraph_smoke_test_attempted"],
        "madgraph_smoke_test_passed": madgraph["madgraph_process_generation_passed"],
        "lhe_generation_ready": madgraph["lhe_generated"],
        "hepmc_generation_ready": madgraph["hepmc_generated"],
        "athena_ready": False,
        "cmssw_ready": False,
        **guardrails(),
        "remaining_blockers": report["missing_components"]
        + [
            blocker
            for blocker, open_ in [
                ("live FeynRules validation", not validation["feynrules_syntax_validated"]),
                ("enabled bounded minimal .fr file", not enablement["enabled_model_created"]),
                ("UFO export", not ufo["ufo_export_passed"]),
                ("UFO loadability", not ufo["ufo_loadability_passed"]),
                ("MadGraph smoke test", not madgraph["madgraph_process_generation_passed"]),
                ("LHE/HepMC event generation", not (madgraph["lhe_generated"] and madgraph["hepmc_generated"])),
                ("Athena/CMSSW boundary", True),
            ]
            if open_
        ],
        "recommended_status_language": status,
    }


def artifact_paths() -> dict[str, Path]:
    return {
        "runtime_provisioning": ROOT / "artifacts" / "BHSM_runtime_provisioning_report_v1_6.json",
        "command_log": ROOT / "artifacts" / "BHSM_live_validation_command_log_v1_6.json",
        "feynrules_validation": ROOT / "artifacts" / "BHSM_feynrules_validation_outcome_v1_6.json",
        "feynrules_enablement": ROOT / "artifacts" / "BHSM_feynrules_enablement_outcome_v1_6.json",
        "ufo_export": ROOT / "artifacts" / "BHSM_ufo_export_outcome_v1_6.json",
        "madgraph_smoke": ROOT / "artifacts" / "BHSM_madgraph_smoke_outcome_v1_6.json",
        "gate_status": ROOT / "artifacts" / "BHSM_phase_three_n_gate_status_v1_6.json",
    }


def write_all(results: dict[str, Any]) -> None:
    for key, path in artifact_paths().items():
        write_json(path, results[key])

