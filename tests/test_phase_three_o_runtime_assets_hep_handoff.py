import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATUS = (
    "BHSM v1.0.1 status-reconciled release: internal boundary no-fit package "
    "complete/exported; external empirical comparison layer separate/open"
)
FROZEN_HASHES = {
    ROOT / "docs" / "frozen_predictions.md": "9EA147C56537520C86D3C4F9B864C6BA98BAC9E64931EDAE96449F3B335A36C4",
    ROOT / "docs" / "frozen_predictions.json": "F38210E0689871A25A9D5B0A1A4239883B7240CD7D0E25CDCF4C8CAB72A2CBE7",
}


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def load(relative: str) -> dict:
    return json.loads(read(relative))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def run_tool(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, *args], cwd=ROOT, text=True, capture_output=True, check=False)


def assert_guardrails(payload: dict) -> None:
    assert payload["empirical_derivation_inputs_used"] is False
    assert payload["empirical_runtime_inputs_allowed_in_collider_mode"] is True
    assert payload["boundary_predictions_modified_by_runtime_inputs"] is False
    assert payload["boundary_predictions_modified_by_comparison"] is False
    assert payload["official_predictions_changed"] is False
    assert payload["source_model_files_changed"] is False


def test_phase_three_o_artifacts_exist_and_parse() -> None:
    for relative in [
        "artifacts/BHSM_runtime_asset_manifest_v1_7.json",
        "artifacts/BHSM_runtime_download_attempts_v1_7.json",
        "artifacts/BHSM_wolfram_runtime_mapping_status_v1_7.json",
        "artifacts/BHSM_feynrules_installation_status_v1_7.json",
        "artifacts/BHSM_madgraph_installation_status_v1_7.json",
        "artifacts/BHSM_institutional_hep_handoff_manifest_v1_7.json",
        "artifacts/BHSM_institutional_validation_protocol_v1_7.json",
        "artifacts/BHSM_collider_interface_model_card_v1_7.json",
        "artifacts/BHSM_phase_three_o_gate_status_v1_7.json",
    ]:
        payload = load(relative)
        assert isinstance(payload, dict), relative
        assert_guardrails(payload)


def test_phase_three_o_docs_scripts_and_readme() -> None:
    for relative in [
        "docs/phase_three_o_runtime_assets_hep_handoff.md",
        "docs/runtime_asset_manifest.md",
        "docs/wolfram_runtime_mapping_guide.md",
        "docs/feynrules_installation_guide.md",
        "docs/madgraph_installation_guide.md",
        "docs/institutional_hep_quickstart.md",
        "docs/institutional_validation_protocol.md",
        "docs/bhsm_model_scope_for_hep_review.md",
        "docs/bhsm_collider_interface_model_card.md",
        "docs/phase_three_o_gate_status.md",
        "scripts/setup/bootstrap_bhsm_hep_environment.py",
        "scripts/setup/check_bhsm_hep_environment.py",
        "scripts/setup/download_allowed_assets.py",
        "scripts/setup/map_wolfram_runtime.py",
        "scripts/setup/install_or_map_feynrules.py",
        "scripts/setup/install_or_map_madgraph.py",
        "scripts/setup/run_full_bhsm_hep_validation_chain.py",
        "Makefile",
        "environment.yml",
        "requirements-hep.txt",
        ".devcontainer/devcontainer.json",
        ".devcontainer/README.md",
    ]:
        assert (ROOT / relative).exists(), relative

    readme = " ".join(read("README.md").split())
    assert STATUS in readme
    assert "Phase Three-O runtime assets and institutional HEP handoff" in read("README.md")
    assert "CERN-like institutional HEP handoff package" in readme
    assert "complete BHSM 4D Lagrangian" in read("README.md")
    assert "experiment-approved integration" in read("README.md")


def test_asset_manifest_marks_wolfram_as_external_licensed_runtime() -> None:
    manifest = load("artifacts/BHSM_runtime_asset_manifest_v1_7.json")
    assets = {entry["asset_id"]: entry for entry in manifest["assets"]}
    assert set(assets) == {
        "python",
        "wolframscript",
        "wolfram_kernel",
        "mathematica",
        "feynrules",
        "feynarts_optional",
        "madgraph",
        "hepmc_optional",
        "root_optional",
        "lhapdf_optional",
    }
    for key in ["wolframscript", "wolfram_kernel", "mathematica"]:
        assert assets[key]["download_allowed"] is False
        assert assets[key]["install_allowed"] is False
        assert "licensed" in assets[key]["legal_source_policy"]
        assert assets[key]["blocks_validation_if_missing"] is True
    assert assets["feynrules"]["download_allowed"] is True
    assert assets["madgraph"]["download_allowed"] is True


def test_download_attempts_do_not_commit_or_fetch_assets_by_default() -> None:
    payload = load("artifacts/BHSM_runtime_download_attempts_v1_7.json")
    assert payload["downloaded_assets_committed_to_repo"] is False
    for entry in payload["attempts"]:
        assert entry["download_attempted"] is False
        assert entry["download_succeeded"] is False
    assert "automatic downloads disabled by default" in json.dumps(payload)


def test_runtime_mapping_install_statuses_remain_evidence_based() -> None:
    wolfram = load("artifacts/BHSM_wolfram_runtime_mapping_status_v1_7.json")
    feynrules = load("artifacts/BHSM_feynrules_installation_status_v1_7.json")
    madgraph = load("artifacts/BHSM_madgraph_installation_status_v1_7.json")
    assert wolfram["mapping_attempted"] is True
    assert "WOLFRAMSCRIPT_PATH" in wolfram["environment_variables_checked"]
    if not wolfram["ready_for_feynrules"]:
        assert wolfram["wolframscript_detected"] is False or wolfram["wolfram_kernel_detected"] is False
    assert feynrules["installation_or_mapping_attempted"] is True
    assert feynrules["download_attempted"] is False
    assert feynrules["load_test_attempted"] is False
    assert feynrules["ready_for_validation"] is False
    assert madgraph["installation_or_mapping_attempted"] is True
    assert madgraph["download_attempted"] is False
    assert madgraph["import_test_attempted"] is False


def test_institutional_handoff_and_model_card_scope() -> None:
    handoff = load("artifacts/BHSM_institutional_hep_handoff_manifest_v1_7.json")
    model = load("artifacts/BHSM_collider_interface_model_card_v1_7.json")
    assert handoff["package_name"] == "BHSM Phase Three-O CERN-like institutional HEP handoff package"
    assert handoff["is_official_cern_integration"] is False
    assert handoff["is_complete_bhsm_4d_lagrangian"] is False
    assert handoff["is_minimal_collider_interface_subset"] is True
    assert "charged_boundary_response_matrix" in handoff["excluded_physics"]
    assert "neutral_operator_kernel_BH" in handoff["excluded_physics"]
    assert "standalone cp_holonomy_phase_attachment" in handoff["excluded_physics"]
    assert model["model_name"] == "BHSM_Minimal_Collider_Interface"
    assert model["included_vertices"] == ["q_charged_current_CKM_BH", "lepton_charged_current_PMNS_BH"]
    assert "claiming official CERN integration" in model["inappropriate_uses"]
    assert "claiming empirical validation" in model["inappropriate_uses"]


def test_validation_protocol_is_stepwise_and_gated() -> None:
    protocol = load("artifacts/BHSM_institutional_validation_protocol_v1_7.json")
    steps = [entry["step_id"] for entry in protocol["steps"]]
    assert steps == [
        "step_0_repo_integrity",
        "step_1_runtime_preflight",
        "step_2_feynrules_load_validation",
        "step_3_feynman_rules_generation",
        "step_4_ufo_export",
        "step_5_ufo_loadability",
        "step_6_madgraph_import",
        "step_7_minimal_smoke_process",
        "step_8_event_output_optional",
        "step_9_detector_software_boundary_review",
    ]
    assert all("Do not promote readiness without live evidence." in entry["notes"] for entry in protocol["steps"])


def test_phase_three_o_gate_status_keeps_runtime_readiness_false_without_evidence() -> None:
    payload = load("artifacts/BHSM_phase_three_o_gate_status_v1_7.json")
    assert payload["institutional_hep_handoff_package_ready"] is True
    assert payload["is_official_cern_integration"] is False
    assert payload["is_complete_bhsm_4d_lagrangian"] is False
    assert payload["is_minimal_collider_interface_subset"] is True
    assert payload["downloaded_assets_committed_to_repo"] is False
    if not payload["environment_ready_for_feynrules_validation"]:
        for key in [
            "feynrules_validation_attempted",
            "feynrules_syntax_validated",
            "feynrules_model_load_validated",
            "minimal_feynrules_model_enabled",
            "production_feynrules_file_exported",
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


def test_phase_three_o_tools_export_to_temporary_outputs(tmp_path: Path) -> None:
    result = run_tool("tools/export_institutional_hep_handoff_manifest_v1_7.py", "--output-dir", str(tmp_path))
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "BHSM_phase_three_o_gate_status_v1_7.json").exists()
    for tool, name in [
        ("tools/check_runtime_asset_manifest_v1_7.py", "manifest.json"),
        ("tools/download_allowed_runtime_assets_v1_7.py", "downloads.json"),
        ("tools/map_wolfram_runtime_v1_7.py", "wolfram.json"),
        ("tools/install_or_map_feynrules_v1_7.py", "feynrules.json"),
        ("tools/install_or_map_madgraph_v1_7.py", "madgraph.json"),
        ("tools/check_phase_three_o_gate_status.py", "status.json"),
    ]:
        result = run_tool(tool, "--output", str(tmp_path / name))
        assert result.returncode == 0, result.stderr
        assert (tmp_path / name).exists()


def test_no_event_files_or_forbidden_phase_three_o_claims() -> None:
    bad_suffixes = {".lhe", ".hepmc", ".hepmc3"}
    bad_files = [path for path in ROOT.rglob("*") if path.is_file() and path.suffix.lower() in bad_suffixes]
    assert bad_files == []
    combined = "\n".join(
        read(relative)
        for relative in [
            "README.md",
            "docs/phase_three_o_runtime_assets_hep_handoff.md",
            "docs/runtime_asset_manifest.md",
            "docs/wolfram_runtime_mapping_guide.md",
            "docs/feynrules_installation_guide.md",
            "docs/madgraph_installation_guide.md",
            "docs/institutional_hep_quickstart.md",
            "docs/institutional_validation_protocol.md",
            "docs/bhsm_model_scope_for_hep_review.md",
            "docs/bhsm_collider_interface_model_card.md",
            "docs/phase_three_o_gate_status.md",
        ]
    ).lower()
    for phrase in [
        "cern-ready",
        "cern-approved",
        "official cern software integration",
        "athena-ready",
        "cmssw-ready",
        "is madgraph-ready",
        "is ufo-ready",
        "empirically validated",
        "complete bhsm 4d lagrangian exported = true",
        "feynrules syntax validated = true",
        "ufo_export_passed = true",
        "madgraph_smoke_test_passed = true",
    ]:
        assert phrase not in combined


def test_frozen_predictions_and_physics_source_remain_unchanged() -> None:
    for path, expected in FROZEN_HASHES.items():
        assert sha256(path) == expected
    tracked_src = subprocess.run(["git", "diff", "--name-only", "HEAD", "--", "src"], cwd=ROOT, text=True, capture_output=True, check=False)
    assert tracked_src.returncode == 0
    assert tracked_src.stdout.strip() == ""
    untracked_src = subprocess.run(["git", "ls-files", "--others", "--exclude-standard", "src"], cwd=ROOT, text=True, capture_output=True, check=False)
    assert untracked_src.returncode == 0
    assert untracked_src.stdout.strip() == ""
