import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PHASE_THREE_N_STATUS = (
    "BHSM v1.0.1 status-reconciled release: internal boundary no-fit package "
    "complete/exported; external empirical comparison layer separate/open"
)
FROZEN_HASHES = {
    ROOT / "docs" / "frozen_predictions.md": (
        "9EA147C56537520C86D3C4F9B864C6BA98BAC9E64931EDAE96449F3B335A36C4"
    ),
    ROOT / "docs" / "frozen_predictions.json": (
        "F38210E0689871A25A9D5B0A1A4239883B7240CD7D0E25CDCF4C8CAB72A2CBE7"
    ),
}


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def load(relative: str) -> dict:
    return json.loads(read(relative))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def run_tool(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def assert_guardrails(payload: dict) -> None:
    assert payload["empirical_derivation_inputs_used"] is False
    assert payload["empirical_runtime_inputs_allowed_in_collider_mode"] is True
    assert payload["boundary_predictions_modified_by_runtime_inputs"] is False
    assert payload["boundary_predictions_modified_by_comparison"] is False
    assert payload["official_predictions_changed"] is False
    assert payload["source_model_files_changed"] is False


def test_phase_three_n_artifacts_exist_and_parse() -> None:
    for relative in [
        "artifacts/BHSM_runtime_provisioning_report_v1_6.json",
        "artifacts/BHSM_live_validation_command_log_v1_6.json",
        "artifacts/BHSM_feynrules_validation_outcome_v1_6.json",
        "artifacts/BHSM_feynrules_enablement_outcome_v1_6.json",
        "artifacts/BHSM_ufo_export_outcome_v1_6.json",
        "artifacts/BHSM_madgraph_smoke_outcome_v1_6.json",
        "artifacts/BHSM_phase_three_n_gate_status_v1_6.json",
    ]:
        payload = load(relative)
        assert isinstance(payload, dict), relative
        assert_guardrails(payload)


def test_phase_three_n_docs_scripts_and_readme_preserve_status() -> None:
    for relative in [
        "docs/phase_three_n_runtime_execution_gate.md",
        "docs/wolfram_feynrules_runtime_provisioning.md",
        "docs/live_validation_command_log.md",
        "docs/feynrules_validation_outcome.md",
        "docs/ufo_export_outcome.md",
        "docs/madgraph_smoke_outcome.md",
        "docs/phase_three_n_gate_status.md",
        "scripts/runtime/README.md",
        "scripts/runtime/find_wolfram_runtime.py",
        "scripts/runtime/find_feynrules.py",
        "scripts/runtime/find_madgraph.py",
        "scripts/runtime/run_phase_three_n_gate.py",
    ]:
        assert (ROOT / relative).exists(), relative

    readme = " ".join(read("README.md").split())
    assert PHASE_THREE_N_STATUS in readme
    assert "Phase Three-N runtime execution gate" in read("README.md")
    assert "complete BHSM 4D Lagrangian" in read("README.md")
    if not load("artifacts/BHSM_phase_three_n_gate_status_v1_6.json")["feynrules_syntax_validated"]:
        assert "minimal model remains disabled" in read("README.md")


def test_runtime_provisioning_report_has_required_detection_fields() -> None:
    payload = load("artifacts/BHSM_runtime_provisioning_report_v1_6.json")
    for key in [
        "platform",
        "python_detected",
        "wolframscript_detected",
        "wolframscript_path",
        "wolframscript_version",
        "wolfram_kernel_detected",
        "wolfram_kernel_path",
        "wolfram_kernel_version",
        "mathematica_detected",
        "mathematica_path",
        "feynrules_detected",
        "feynrules_path",
        "feynrules_version_if_available",
        "madgraph_detected",
        "madgraph_path",
        "madgraph_version_if_available",
        "environment_ready_for_feynrules_validation",
        "environment_ready_for_ufo_export",
        "environment_ready_for_madgraph_smoke",
        "missing_components",
        "provisioning_actions_attempted",
        "provisioning_actions_succeeded",
        "license_or_runtime_notes",
    ]:
        assert key in payload
    assert payload["python_detected"] is True
    assert "No Wolfram license bypass" in " ".join(payload["license_or_runtime_notes"])
    if not payload["environment_ready_for_feynrules_validation"]:
        assert payload["wolframscript_detected"] is False or payload["feynrules_detected"] is False or (
            payload["mathematica_detected"] is False and payload["wolfram_kernel_detected"] is False
        )


def test_command_log_distinguishes_attempted_and_skipped_steps() -> None:
    payload = load("artifacts/BHSM_live_validation_command_log_v1_6.json")
    commands = {entry["step_id"]: entry for entry in payload["commands"]}
    assert set(commands) == {
        "N1_RUNTIME_PROVISIONING",
        "N2_FEYNRULES_VALIDATION",
        "N3_FEYNRULES_ENABLEMENT",
        "N4_UFO_EXPORT",
        "N5_MADGRAPH_SMOKE",
    }
    assert commands["N1_RUNTIME_PROVISIONING"]["attempted"] is True
    if not load("artifacts/BHSM_runtime_provisioning_report_v1_6.json")["environment_ready_for_feynrules_validation"]:
        assert commands["N2_FEYNRULES_VALIDATION"]["attempted"] is False
        assert commands["N2_FEYNRULES_VALIDATION"]["result"] == "skipped"
        assert commands["N3_FEYNRULES_ENABLEMENT"]["attempted"] is False
        assert commands["N4_UFO_EXPORT"]["attempted"] is False
        assert commands["N5_MADGRAPH_SMOKE"]["attempted"] is False


def test_feynrules_validation_and_enablement_are_evidence_gated() -> None:
    validation = load("artifacts/BHSM_feynrules_validation_outcome_v1_6.json")
    enablement = load("artifacts/BHSM_feynrules_enablement_outcome_v1_6.json")
    assert validation["input_disabled_model"] == "models/feynrules/BHSM_Minimal_Collider_Interface.fr.disabled"
    assert validation["is_complete_bhsm_model"] is False
    assert enablement["is_complete_bhsm_model"] is False
    assert enablement["disabled_model_preserved"] is True
    if not validation["validation_attempted"]:
        assert validation["feynrules_syntax_validated"] is False
        assert validation["feynrules_model_load_validated"] is False
        assert validation["production_feynrules_file_exported"] is False
        assert validation["minimal_model_enabled"] is False
        assert enablement["enablement_allowed"] is False
        assert enablement["enablement_performed"] is False
        assert enablement["enabled_model_created"] is False
        assert not (ROOT / "models" / "feynrules" / "BHSM_Minimal_Collider_Interface.fr").exists()


def test_ufo_and_madgraph_outcomes_are_downstream_gated() -> None:
    validation = load("artifacts/BHSM_feynrules_validation_outcome_v1_6.json")
    ufo = load("artifacts/BHSM_ufo_export_outcome_v1_6.json")
    madgraph = load("artifacts/BHSM_madgraph_smoke_outcome_v1_6.json")
    if not validation["feynrules_syntax_validated"]:
        assert ufo["ufo_export_attempted"] is False
        assert ufo["ufo_export_passed"] is False
        assert ufo["ufo_directory_created"] is False
        assert ufo["ufo_loadability_tested"] is False
        assert ufo["ufo_loadability_passed"] is False
    if not (ufo["ufo_export_passed"] and ufo["ufo_loadability_passed"]):
        assert madgraph["madgraph_smoke_test_attempted"] is False
        assert madgraph["madgraph_import_passed"] is False
        assert madgraph["madgraph_process_generation_passed"] is False
        assert madgraph["lhe_generated"] is False
        assert madgraph["hepmc_generated"] is False


def test_phase_three_n_gate_status_is_consistent() -> None:
    payload = load("artifacts/BHSM_phase_three_n_gate_status_v1_6.json")
    for key in [
        "runtime_provisioning_report_exported",
        "live_validation_command_log_exported",
        "feynrules_validation_outcome_exported",
        "feynrules_enablement_outcome_exported",
        "ufo_export_outcome_exported",
        "madgraph_smoke_outcome_exported",
    ]:
        assert payload[key] is True
    assert payload["minimal_model_is_complete_bhsm"] is False
    if not payload["environment_ready_for_feynrules_validation"]:
        assert payload["feynrules_validation_attempted"] is False
        assert payload["feynrules_syntax_validated"] is False
        assert payload["feynrules_model_load_validated"] is False
        assert payload["minimal_feynrules_model_enabled"] is False
        assert payload["production_feynrules_file_exported"] is False
        assert payload["ufo_export_attempted"] is False
        assert payload["madgraph_smoke_test_attempted"] is False
        assert "minimal model remains disabled" in payload["recommended_status_language"]
    assert payload["athena_ready"] is False
    assert payload["cmssw_ready"] is False


def test_minimal_model_exclusions_and_no_fake_event_files() -> None:
    path = ROOT / "models" / "feynrules" / "BHSM_Minimal_Collider_Interface.fr.disabled"
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert "BHSM_MINIMAL_COLLIDER_INTERFACE" in text
    assert "This is not the complete BHSM 4D Lagrangian" in text
    assert "This excludes charged boundary response, neutral kernel, and standalone CP holonomy vertices" in text
    assert "C_ch_boundary" not in text
    assert "K_nu neutral" not in text
    assert "O_int" not in text
    for fake_number in ["172.76", "80.379", "91.1876", "0.118", "125.10"]:
        assert fake_number not in text
    bad_suffixes = {".lhe", ".hepmc", ".hepmc3"}
    bad_files = [path for path in ROOT.rglob("*") if path.is_file() and path.suffix.lower() in bad_suffixes]
    assert bad_files == []


def test_phase_three_n_tools_export_to_temporary_outputs(tmp_path: Path) -> None:
    result = run_tool("tools/run_phase_three_n_execution_gate_v1_6.py", "--output-dir", str(tmp_path))
    assert result.returncode == 0, result.stderr
    for name in [
        "BHSM_runtime_provisioning_report_v1_6.json",
        "BHSM_live_validation_command_log_v1_6.json",
        "BHSM_feynrules_validation_outcome_v1_6.json",
        "BHSM_feynrules_enablement_outcome_v1_6.json",
        "BHSM_ufo_export_outcome_v1_6.json",
        "BHSM_madgraph_smoke_outcome_v1_6.json",
        "BHSM_phase_three_n_gate_status_v1_6.json",
    ]:
        assert (tmp_path / name).exists(), name

    result = run_tool("tools/check_runtime_provisioning_v1_6.py", "--output", str(tmp_path / "runtime.json"))
    assert result.returncode == 0, result.stderr
    result = run_tool("tools/export_live_validation_command_log_v1_6.py", "--output", str(tmp_path / "commands.json"))
    assert result.returncode == 0, result.stderr
    result = run_tool("tools/export_phase_three_n_gate_status.py", "--output", str(tmp_path / "status.json"))
    assert result.returncode == 0, result.stderr
    assert json.loads((tmp_path / "status.json").read_text(encoding="utf-8"))["minimal_model_is_complete_bhsm"] is False


def test_no_forbidden_phase_three_n_claims() -> None:
    combined = "\n".join(
        read(relative)
        for relative in [
            "README.md",
            "docs/phase_three_n_runtime_execution_gate.md",
            "docs/wolfram_feynrules_runtime_provisioning.md",
            "docs/live_validation_command_log.md",
            "docs/feynrules_validation_outcome.md",
            "docs/ufo_export_outcome.md",
            "docs/madgraph_smoke_outcome.md",
            "docs/phase_three_n_gate_status.md",
        ]
    ).lower()
    for phrase in [
        "complete bhsm 4d lagrangian exported = true",
        "production feynrules file exported = true",
        "feynrules syntax validated = true",
        "feynrules validation passed",
        "ufo_export_passed = true",
        "ufo_loadability_passed = true",
        "madgraph_smoke_test_passed = true",
        "lhe_generation_ready = true",
        "hepmc_generation_ready = true",
        "athena_ready = true",
        "cmssw_ready = true",
        "official cern integration",
        "bhsm is empirically validated",
        "bhsm is empirically proven",
        "production ufo model is ready",
        "zenodo doi assigned",
    ]:
        assert phrase not in combined


def test_frozen_predictions_and_physics_source_remain_unchanged() -> None:
    for path, expected in FROZEN_HASHES.items():
        assert sha256(path) == expected

    tracked_src = subprocess.run(
        ["git", "diff", "--name-only", "HEAD", "--", "src"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert tracked_src.returncode == 0
    assert tracked_src.stdout.strip() == ""

    untracked_src = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard", "src"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert untracked_src.returncode == 0
    assert untracked_src.stdout.strip() == ""

