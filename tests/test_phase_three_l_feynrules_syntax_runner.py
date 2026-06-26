import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PHASE_THREE_L_STATUS = (
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
    assert payload["boundary_predictions_modified_by_runtime_inputs"] is False
    assert payload["boundary_predictions_modified_by_comparison"] is False
    assert payload["official_predictions_changed"] is False
    assert payload["source_model_files_changed"] is False


def test_phase_three_l_artifacts_exist_and_parse() -> None:
    for relative in [
        "artifacts/BHSM_feynrules_syntax_contract_v1_4.json",
        "artifacts/BHSM_feynrules_export_runner_package_v1_4.json",
        "artifacts/BHSM_software_environment_preflight_v1_4.json",
        "artifacts/BHSM_ufo_export_runner_contract_v1_4.json",
        "artifacts/BHSM_madgraph_smoke_runner_contract_v1_4.json",
        "artifacts/BHSM_phase_three_l_gate_status_v1_4.json",
    ]:
        payload = load(relative)
        assert isinstance(payload, dict), relative
        assert_guardrails(payload)


def test_phase_three_l_docs_scripts_and_readme_preserve_status() -> None:
    for relative in [
        "docs/phase_three_l_feynrules_syntax_runner.md",
        "docs/feynrules_syntax_contract.md",
        "docs/feynrules_local_execution_guide.md",
        "docs/ufo_export_runner_guide.md",
        "docs/madgraph_smoke_runner_guide.md",
        "docs/software_environment_preflight.md",
        "docs/phase_three_l_gate_status.md",
        "scripts/feynrules/README.md",
        "scripts/feynrules/check_bhsm_minimal_model.m",
        "scripts/feynrules/export_bhsm_minimal_to_ufo.m",
        "scripts/madgraph/README.md",
        "scripts/madgraph/import_bhsm_minimal_ufo_smoke.mg5",
    ]:
        assert (ROOT / relative).exists(), relative

    readme = " ".join(read("README.md").split())
    assert PHASE_THREE_L_STATUS in readme
    assert "Phase Three-L FeynRules syntax-runner package" in read("README.md")
    assert "Repository static checks do not equal FeynRules validation" in read("README.md")


def test_feynrules_syntax_contract_is_static_only() -> None:
    payload = load("artifacts/BHSM_feynrules_syntax_contract_v1_4.json")
    assert payload["model_file_checked"] is True
    assert payload["model_file_enabled"] is False
    assert payload["model_scope"] == "BHSM_MINIMAL_COLLIDER_INTERFACE_ONLY"
    assert payload["is_complete_bhsm_model"] is False
    assert payload["allowed_vertex_families"] == [
        "q_charged_current_CKM_BH",
        "lepton_charged_current_PMNS_BH",
    ]
    assert payload["excluded_vertex_families"] == [
        "charged_boundary_response_matrix",
        "neutral_operator_kernel_BH",
        "cp_holonomy_phase_attachment",
    ]
    assert all(entry["passed"] is True for entry in payload["static_contract_checks"])
    assert payload["static_contract_passed"] is True
    assert payload["mathematica_syntax_checked"] is False
    assert payload["feynrules_load_checked"] is False
    assert payload["feynrules_lagrangian_checked"] is False
    assert payload["ufo_export_checked"] is False


def test_export_runner_package_is_created_but_not_executed() -> None:
    payload = load("artifacts/BHSM_feynrules_export_runner_package_v1_4.json")
    assert payload["runner_package_created"] is True
    assert payload["mathematica_script_path"] == "scripts/feynrules/export_bhsm_minimal_to_ufo.m"
    assert payload["model_check_script_path"] == "scripts/feynrules/check_bhsm_minimal_model.m"
    assert payload["input_model_file"] == "models/feynrules/BHSM_Minimal_Collider_Interface.fr.disabled"
    assert payload["expected_enabled_model_file"] == "models/feynrules/BHSM_Minimal_Collider_Interface.fr"
    assert payload["expected_ufo_output_directory"] == "models/ufo/BHSM_Minimal_Collider_Interface"
    assert payload["requires_mathematica"] is True
    assert payload["requires_feynrules"] is True
    assert payload["export_attempted"] is False
    assert payload["export_passed"] is False
    assert payload["feynrules_version_detected"] == "not_detected"
    assert payload["mathematica_version_detected"] == "not_detected"
    assert "Mathematica/FeynRules runtime unavailable" in payload["missing_for_execution"]


def test_software_environment_preflight_reports_missing_external_stack() -> None:
    payload = load("artifacts/BHSM_software_environment_preflight_v1_4.json")
    entries = {entry["component"]: entry for entry in payload["entries"]}
    assert set(entries) == {
        "python",
        "mathematica_kernel",
        "wolframscript",
        "feynrules",
        "feynarts",
        "madgraph",
        "hepmc",
        "root_optional",
    }
    assert entries["python"]["detected"] is True
    for component in [
        "mathematica_kernel",
        "wolframscript",
        "feynrules",
        "madgraph",
        "hepmc",
    ]:
        assert entries[component]["detected"] is False
    assert entries["feynarts"]["blocks_if_missing"] is False
    assert entries["root_optional"]["blocks_if_missing"] is False


def test_ufo_and_madgraph_runner_contracts_are_unattempted() -> None:
    ufo = load("artifacts/BHSM_ufo_export_runner_contract_v1_4.json")
    assert ufo["input_feynrules_model"] == "models/feynrules/BHSM_Minimal_Collider_Interface.fr"
    assert ufo["output_ufo_directory"] == "models/ufo/BHSM_Minimal_Collider_Interface"
    assert ufo["export_command_template"] == "wolframscript -file scripts/feynrules/export_bhsm_minimal_to_ufo.m"
    assert ufo["ufo_export_attempted"] is False
    assert ufo["ufo_export_passed"] is False
    assert ufo["ufo_directory_created"] is False
    assert ufo["ufo_loadability_tested"] is False
    assert ufo["ufo_loadability_passed"] is False

    madgraph = load("artifacts/BHSM_madgraph_smoke_runner_contract_v1_4.json")
    assert madgraph["requires_loadable_ufo"] is True
    assert madgraph["requires_madgraph"] is True
    assert madgraph["mg5_script_path"] == "scripts/madgraph/import_bhsm_minimal_ufo_smoke.mg5"
    assert madgraph["planned_processes"] == ["u d~ > w+", "e+ ve > w+"]
    assert madgraph["smoke_test_attempted"] is False
    assert madgraph["smoke_test_passed"] is False
    assert madgraph["lhe_generated"] is False
    assert madgraph["hepmc_generated"] is False


def test_phase_three_l_gate_status_keeps_readiness_false() -> None:
    payload = load("artifacts/BHSM_phase_three_l_gate_status_v1_4.json")
    for key in [
        "feynrules_syntax_contract_exported",
        "feynrules_export_runner_package_exported",
        "software_environment_preflight_exported",
        "ufo_export_runner_contract_exported",
        "madgraph_smoke_runner_contract_exported",
        "static_contract_checks_passed",
    ]:
        assert payload[key] is True
    for key in [
        "mathematica_detected",
        "feynrules_detected",
        "madgraph_detected",
        "minimal_feynrules_model_file_enabled",
        "production_feynrules_file_exported",
        "feynrules_syntax_validated",
        "feynrules_model_load_validated",
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
    assert "Static repository checks may pass" in payload["recommended_status_language"]


def test_disabled_model_file_stays_disabled_and_bounded() -> None:
    path = ROOT / "models" / "feynrules" / "BHSM_Minimal_Collider_Interface.fr.disabled"
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert "BHSM_MINIMAL_COLLIDER_INTERFACE" in text
    assert "This is not the complete BHSM 4D Lagrangian" in text
    assert "This excludes charged boundary response, neutral kernel, and standalone CP holonomy vertices" in text
    assert "V_CKM_BH" in text
    assert "U_PMNS_BH" in text
    assert "g2_BH_runtime" in text
    assert "C_ch_boundary" not in text
    assert "K_nu neutral" not in text
    assert "O_int" not in text
    for fake_number in ["172.76", "80.379", "91.1876", "0.118", "125.10"]:
        assert fake_number not in text
    assert not (ROOT / "models" / "feynrules" / "BHSM_Minimal_Collider_Interface.fr").exists()


def test_phase_three_l_tools_export_to_temporary_outputs(tmp_path: Path) -> None:
    commands = [
        ("tools/check_feynrules_syntax_contract_v1_4.py", "--output", str(tmp_path / "syntax.json")),
        ("tools/check_software_environment_preflight_v1_4.py", "--output", str(tmp_path / "preflight.json")),
        ("tools/export_feynrules_runner_package_v1_4.py", "--output", str(tmp_path / "runner.json")),
        ("tools/export_ufo_export_runner_contract_v1_4.py", "--output", str(tmp_path / "ufo.json")),
        ("tools/export_madgraph_smoke_runner_contract_v1_4.py", "--output", str(tmp_path / "mg.json")),
        ("tools/check_phase_three_l_gate_status.py", "--output", str(tmp_path / "status.json")),
    ]
    for command in commands:
        result = run_tool(*command)
        assert result.returncode == 0, result.stderr

    assert json.loads((tmp_path / "syntax.json").read_text(encoding="utf-8"))["static_contract_passed"] is True
    assert json.loads((tmp_path / "preflight.json").read_text(encoding="utf-8"))["entries"][0]["component"] == "python"
    assert json.loads((tmp_path / "runner.json").read_text(encoding="utf-8"))["export_passed"] is False
    assert json.loads((tmp_path / "ufo.json").read_text(encoding="utf-8"))["ufo_export_passed"] is False
    assert json.loads((tmp_path / "mg.json").read_text(encoding="utf-8"))["smoke_test_passed"] is False
    assert json.loads((tmp_path / "status.json").read_text(encoding="utf-8"))["feynrules_syntax_validated"] is False


def test_no_event_files_or_forbidden_phase_three_l_claims() -> None:
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
            "docs/phase_three_l_feynrules_syntax_runner.md",
            "docs/feynrules_syntax_contract.md",
            "docs/feynrules_local_execution_guide.md",
            "docs/ufo_export_runner_guide.md",
            "docs/madgraph_smoke_runner_guide.md",
            "docs/software_environment_preflight.md",
            "docs/phase_three_l_gate_status.md",
        ]
    ).lower()
    for phrase in [
        "production feynrules file exported = true",
        "feynrules syntax validated = true",
        "feynrules model load validated = true",
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
        "feynrules validation passed",
        "madgraph readiness passed",
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
