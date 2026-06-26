import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PHASE_THREE_M_STATUS = (
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


def test_phase_three_m_artifacts_exist_and_parse() -> None:
    for relative in [
        "artifacts/BHSM_live_feynrules_validation_attempt_v1_5.json",
        "artifacts/BHSM_feynrules_model_enablement_decision_v1_5.json",
        "artifacts/BHSM_ufo_export_live_attempt_v1_5.json",
        "artifacts/BHSM_madgraph_live_smoke_attempt_v1_5.json",
        "artifacts/BHSM_phase_three_m_gate_status_v1_5.json",
    ]:
        payload = load(relative)
        assert isinstance(payload, dict), relative
        assert_guardrails(payload)


def test_phase_three_m_docs_and_readme_preserve_status() -> None:
    for relative in [
        "docs/phase_three_m_live_feynrules_validation.md",
        "docs/live_feynrules_validation_report.md",
        "docs/feynrules_enablement_policy.md",
        "docs/ufo_export_live_attempt_report.md",
        "docs/madgraph_live_smoke_attempt_report.md",
        "docs/phase_three_m_gate_status.md",
        "scripts/feynrules/enable_minimal_model_if_validated.py",
        "scripts/feynrules/run_live_feynrules_validation.py",
        "scripts/feynrules/run_ufo_export_if_validated.py",
        "scripts/madgraph/run_minimal_ufo_smoke_if_available.py",
    ]:
        assert (ROOT / relative).exists(), relative

    readme = " ".join(read("README.md").split())
    assert PHASE_THREE_M_STATUS in readme
    assert "Phase Three-M live FeynRules validation status" in read("README.md")
    assert "Static checks do not count as live FeynRules validation" in read("README.md")
    assert "not UFO-ready, not MadGraph-ready, and not event-generation-ready" in readme


def test_live_feynrules_validation_attempt_records_missing_tools_cleanly() -> None:
    payload = load("artifacts/BHSM_live_feynrules_validation_attempt_v1_5.json")
    entries = {entry["component"]: entry for entry in payload["environment_preflight"]}
    assert set(entries) == {
        "python",
        "mathematica_kernel",
        "wolframscript",
        "feynrules",
        "feynarts_optional",
        "madgraph",
        "hepmc_optional",
        "root_optional",
    }
    assert entries["python"]["detected"] is True
    assert payload["model_file_tested"] == "models/feynrules/BHSM_Minimal_Collider_Interface.fr.disabled"
    assert payload["model_scope"] == "BHSM_MINIMAL_COLLIDER_INTERFACE_ONLY"
    assert payload["is_complete_bhsm_model"] is False
    assert payload["excluded_vertices_confirmed"] is True
    assert payload["forbidden_content_confirmed_absent"] is True
    if not (payload["mathematica_detected"] and payload["wolframscript_detected"] and payload["feynrules_detected"]):
        assert payload["live_validation_attempted"] is False
        assert payload["feynrules_syntax_validated"] is False
        assert payload["feynrules_model_load_validated"] is False
        assert payload["feynman_rules_generation_attempted"] is False
        assert payload["feynman_rules_generation_passed"] is False
        assert payload["failure_reason_if_any"] == "Mathematica/FeynRules runtime unavailable"


def test_model_enablement_policy_refuses_static_only_enablement() -> None:
    validation = load("artifacts/BHSM_live_feynrules_validation_attempt_v1_5.json")
    enablement = load("artifacts/BHSM_feynrules_model_enablement_decision_v1_5.json")
    assert enablement["disabled_model_path"] == "models/feynrules/BHSM_Minimal_Collider_Interface.fr.disabled"
    assert enablement["enabled_model_path"] == "models/feynrules/BHSM_Minimal_Collider_Interface.fr"
    assert enablement["model_scope"] == "BHSM_MINIMAL_COLLIDER_INTERFACE_ONLY"
    assert enablement["is_complete_bhsm_model"] is False
    if not (validation["feynrules_syntax_validated"] and validation["feynrules_model_load_validated"]):
        assert enablement["enablement_allowed"] is False
        assert enablement["enablement_performed"] is False
        assert "Live FeynRules validation did not pass" in enablement["enablement_reason"]
        assert not (ROOT / "models" / "feynrules" / "BHSM_Minimal_Collider_Interface.fr").exists()


def test_ufo_and_madgraph_live_attempts_remain_gated() -> None:
    validation = load("artifacts/BHSM_live_feynrules_validation_attempt_v1_5.json")
    ufo = load("artifacts/BHSM_ufo_export_live_attempt_v1_5.json")
    madgraph = load("artifacts/BHSM_madgraph_live_smoke_attempt_v1_5.json")
    if not (validation["feynrules_syntax_validated"] and validation["feynrules_model_load_validated"]):
        assert ufo["ufo_export_attempted"] is False
        assert ufo["ufo_export_passed"] is False
        assert ufo["ufo_directory_created"] is False
        assert ufo["ufo_loadability_tested"] is False
        assert ufo["ufo_loadability_passed"] is False
        assert ufo["failure_reason_if_any"] == "FeynRules validation gates did not pass"

    assert madgraph["requires_loadable_ufo"] is True
    assert madgraph["input_ufo_directory"] == "models/ufo/BHSM_Minimal_Collider_Interface"
    assert madgraph["planned_processes"] == ["u d~ > w+", "e+ ve > w+"]
    if not (ufo["ufo_export_passed"] and ufo["ufo_loadability_passed"] and madgraph["madgraph_detected"]):
        assert madgraph["madgraph_smoke_test_attempted"] is False
        assert madgraph["madgraph_import_passed"] is False
        assert madgraph["madgraph_process_generation_passed"] is False
        assert madgraph["lhe_generated"] is False
        assert madgraph["hepmc_generated"] is False


def test_phase_three_m_gate_status_reflects_live_evidence_only() -> None:
    payload = load("artifacts/BHSM_phase_three_m_gate_status_v1_5.json")
    for key in [
        "live_feynrules_validation_attempt_artifact_exported",
        "feynrules_model_enablement_decision_exported",
        "ufo_export_live_attempt_artifact_exported",
        "madgraph_live_smoke_attempt_artifact_exported",
    ]:
        assert payload[key] is True
    if not payload["feynrules_syntax_validated"]:
        for key in [
            "minimal_feynrules_model_file_enabled",
            "production_feynrules_file_exported",
            "feynrules_live_validation_attempted",
            "feynrules_model_load_validated",
            "feynman_rules_generation_attempted",
            "feynman_rules_generation_passed",
            "ufo_export_attempted",
            "ufo_export_passed",
            "ufo_loadability_tested",
            "ufo_loadability_passed",
            "madgraph_smoke_test_attempted",
            "madgraph_smoke_test_passed",
            "lhe_generation_ready",
            "hepmc_generation_ready",
            "athena_ready",
            "cmssw_ready",
        ]:
            assert payload[key] is False
        assert "no FeynRules/UFO/MadGraph readiness is claimed" in payload["recommended_status_language"]


def test_minimal_model_remains_bounded_and_disabled() -> None:
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
    assert not (ROOT / "models" / "feynrules" / "BHSM_Minimal_Collider_Interface.fr").exists()


def test_phase_three_m_tools_export_to_temporary_outputs(tmp_path: Path) -> None:
    commands = [
        ("tools/run_live_feynrules_validation_attempt_v1_5.py", "--output", str(tmp_path / "validation.json")),
        ("tools/export_feynrules_model_enablement_decision_v1_5.py", "--output", str(tmp_path / "enablement.json")),
        ("tools/export_ufo_live_attempt_v1_5.py", "--output", str(tmp_path / "ufo.json")),
        ("tools/export_madgraph_live_smoke_attempt_v1_5.py", "--output", str(tmp_path / "madgraph.json")),
        ("tools/check_phase_three_m_gate_status.py", "--output", str(tmp_path / "status.json")),
    ]
    for command in commands:
        result = run_tool(*command)
        assert result.returncode == 0, result.stderr

    assert json.loads((tmp_path / "validation.json").read_text(encoding="utf-8"))["is_complete_bhsm_model"] is False
    assert json.loads((tmp_path / "enablement.json").read_text(encoding="utf-8"))["enablement_performed"] is False
    assert json.loads((tmp_path / "ufo.json").read_text(encoding="utf-8"))["ufo_export_passed"] is False
    assert json.loads((tmp_path / "madgraph.json").read_text(encoding="utf-8"))["lhe_generated"] is False
    assert json.loads((tmp_path / "status.json").read_text(encoding="utf-8"))["athena_ready"] is False


def test_no_event_files_or_forbidden_phase_three_m_claims() -> None:
    bad_suffixes = {".lhe", ".hepmc", ".hepmc3"}
    bad_files = [
        path
        for path in ROOT.rglob("*")
        if path.is_file() and path.suffix.lower() in bad_suffixes
    ]
    assert bad_files == []

    combined = "\n".join(
        read(relative)
        for relative in [
            "README.md",
            "docs/phase_three_m_live_feynrules_validation.md",
            "docs/live_feynrules_validation_report.md",
            "docs/feynrules_enablement_policy.md",
            "docs/ufo_export_live_attempt_report.md",
            "docs/madgraph_live_smoke_attempt_report.md",
            "docs/phase_three_m_gate_status.md",
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
