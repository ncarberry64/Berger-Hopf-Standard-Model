import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PHASE_THREE_K_STATUS = (
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


def test_phase_three_k_artifacts_exist_and_parse() -> None:
    for relative in [
        "artifacts/BHSM_minimal_feynrules_model_export_attempt_v1_3.json",
        "artifacts/BHSM_feynrules_to_ufo_export_contract_v1_3.json",
        "artifacts/BHSM_madgraph_smoke_test_plan_v1_3.json",
        "artifacts/BHSM_software_track_readiness_gates_v1_3.json",
        "artifacts/BHSM_phase_three_k_gate_status_v1_3.json",
    ]:
        payload = load(relative)
        assert isinstance(payload, dict), relative
        assert_guardrails(payload)


def test_phase_three_k_docs_and_readme_preserve_status() -> None:
    for relative in [
        "docs/phase_three_k_feynrules_export_attempt.md",
        "docs/bhsm_minimal_feynrules_model.md",
        "docs/feynrules_to_ufo_export_contract.md",
        "docs/madgraph_smoke_test_plan.md",
        "docs/software_track_readiness_gates.md",
        "docs/phase_three_k_gate_status.md",
    ]:
        assert (ROOT / relative).exists(), relative

    readme = " ".join(read("README.md").split())
    assert PHASE_THREE_K_STATUS in readme
    assert "Phase Three-K bounded FeynRules export attempt" in read("README.md")
    assert "not the complete BHSM 4D Lagrangian" in read("README.md")


def test_minimal_feynrules_export_attempt_is_disabled_and_bounded() -> None:
    payload = load("artifacts/BHSM_minimal_feynrules_model_export_attempt_v1_3.json")
    assert payload["model_name"] == "BHSM_MINIMAL_COLLIDER_INTERFACE"
    assert payload["model_file_path"] == "models/feynrules/BHSM_Minimal_Collider_Interface.fr.disabled"
    assert payload["model_file_created"] is True
    assert payload["model_file_enabled"] is False
    assert payload["is_complete_bhsm_model"] is False
    assert payload["is_minimal_collider_interface_subset"] is True
    assert payload["production_feynrules_file_exported"] is False
    assert payload["feynrules_syntax_status"] == "SYNTAX_CONTRACT_ONLY_DISABLED_DRAFT"
    assert "charged_boundary_response_matrix" in payload["excluded_terms"]
    assert "neutral_operator_kernel_BH" in payload["excluded_terms"]
    assert "standalone cp_holonomy_phase_attachment" in payload["excluded_terms"]


def test_disabled_model_file_has_guarded_content_only() -> None:
    path = ROOT / "models" / "feynrules" / "BHSM_Minimal_Collider_Interface.fr.disabled"
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert "BHSM_MINIMAL_COLLIDER_INTERFACE" in text
    assert "This is not the complete BHSM 4D Lagrangian" in text
    assert "This excludes charged boundary response, neutral kernel, and standalone CP holonomy vertices" in text
    assert "V_CKM_BH" in text
    assert "U_PMNS_BH" in text
    assert "g2_BH_runtime" in text
    assert "charged_boundary_response_matrix" in text
    assert "neutral_operator_kernel_BH" in text
    assert "standalone cp_holonomy_phase_attachment" in text
    assert "C_ch_boundary" not in text
    assert "K_nu neutral" not in text
    assert "O_int" not in text
    for fake_number in ["172.76", "80.379", "91.1876", "0.118", "125.10"]:
        assert fake_number not in text
    assert not (ROOT / "models" / "feynrules" / "BHSM_Minimal_Collider_Interface.fr").exists()


def test_ufo_contract_keeps_export_unattempted() -> None:
    payload = load("artifacts/BHSM_feynrules_to_ufo_export_contract_v1_3.json")
    assert payload["requires_mathematica"] is True
    assert payload["requires_feynrules"] is True
    assert payload["ufo_export_attempted"] is False
    assert payload["ufo_export_passed"] is False
    assert payload["ufo_loadability_tested"] is False
    assert payload["ufo_loadability_passed"] is False
    assert "Mathematica/FeynRules runtime unavailable" in payload["missing_for_ufo"]


def test_madgraph_smoke_plan_is_not_executed() -> None:
    payload = load("artifacts/BHSM_madgraph_smoke_test_plan_v1_3.json")
    assert payload["requires_loadable_ufo"] is True
    assert payload["requires_madgraph"] is True
    assert payload["minimal_processes"] == ["u d~ > w+", "e+ ve > w+"]
    assert payload["smoke_test_attempted"] is False
    assert payload["smoke_test_passed"] is False
    assert payload["lhe_generated"] is False
    assert payload["hepmc_generated"] is False


def test_software_track_gates_are_explicitly_blocked() -> None:
    gates = {
        entry["gate_id"]: entry
        for entry in load("artifacts/BHSM_software_track_readiness_gates_v1_3.json")["gates"]
    }
    assert set(gates) == {
        "bounded_feynrules_model_file",
        "feynrules_syntax_validation",
        "ufo_export",
        "ufo_loadability",
        "madgraph_import",
        "madgraph_smoke_process",
        "lhe_generation",
        "hepmc_generation",
        "athena_boundary",
        "cmssw_boundary",
    }
    assert gates["bounded_feynrules_model_file"]["status"] == "DISABLED_DRAFT_EXPORTED"
    assert gates["feynrules_syntax_validation"]["status"] == "NOT_VALIDATED"
    assert gates["ufo_export"]["status"] == "NOT_ATTEMPTED"
    assert gates["madgraph_smoke_process"]["status"] == "PLANNED_NOT_ATTEMPTED"
    for gate in gates.values():
        assert gate["blocks_next_step"] is True


def test_phase_three_k_gate_status_keeps_downstream_readiness_false() -> None:
    payload = load("artifacts/BHSM_phase_three_k_gate_status_v1_3.json")
    assert payload["minimal_feynrules_model_export_attempted"] is True
    assert payload["minimal_feynrules_model_file_created"] is True
    assert payload["minimal_feynrules_model_enabled"] is False
    assert payload["minimal_feynrules_model_is_complete_bhsm"] is False
    assert payload["minimal_feynrules_model_excludes_unresolved_vertices"] is True
    assert payload["production_feynrules_file_exported"] is False
    assert payload["feynrules_syntax_validated"] is False
    assert payload["ufo_export_attempted"] is False
    assert payload["ufo_export_passed"] is False
    assert payload["ufo_loadability_tested"] is False
    assert payload["ufo_loadability_passed"] is False
    assert payload["madgraph_smoke_test_planned"] is True
    assert payload["madgraph_smoke_test_attempted"] is False
    assert payload["madgraph_smoke_test_passed"] is False
    assert payload["lhe_generation_ready"] is False
    assert payload["hepmc_generation_ready"] is False
    assert payload["athena_ready"] is False
    assert payload["cmssw_ready"] is False
    assert "UFO/MadGraph/event readiness remains gated" in payload["recommended_status_language"]


def test_phase_three_k_tools_export_to_temporary_outputs(tmp_path: Path) -> None:
    commands = [
        ("tools/export_minimal_feynrules_model_export_attempt_v1_3.py", "--output", str(tmp_path / "model.json")),
        ("tools/export_feynrules_to_ufo_export_contract_v1_3.py", "--output", str(tmp_path / "ufo.json")),
        ("tools/export_madgraph_smoke_test_plan_v1_3.py", "--output", str(tmp_path / "mg.json")),
    ]
    for command in commands:
        result = run_tool(*command)
        assert result.returncode == 0, result.stderr
    result = run_tool("tools/export_software_track_readiness_gates_v1_3.py", "--output", str(tmp_path / "gates.json"))
    assert result.returncode == 0, result.stderr
    result = run_tool("tools/check_phase_three_k_gate_status.py", "--output", str(tmp_path / "status.json"))
    assert result.returncode == 0, result.stderr

    assert json.loads((tmp_path / "model.json").read_text(encoding="utf-8"))["model_file_enabled"] is False
    assert json.loads((tmp_path / "ufo.json").read_text(encoding="utf-8"))["ufo_export_passed"] is False
    assert json.loads((tmp_path / "mg.json").read_text(encoding="utf-8"))["lhe_generated"] is False
    assert json.loads((tmp_path / "gates.json").read_text(encoding="utf-8"))["gates"][0]["blocks_next_step"] is True
    assert json.loads((tmp_path / "status.json").read_text(encoding="utf-8"))["production_feynrules_file_exported"] is False


def test_no_fake_event_files_or_forbidden_phase_three_k_claims() -> None:
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
            "docs/phase_three_k_feynrules_export_attempt.md",
            "docs/bhsm_minimal_feynrules_model.md",
            "docs/feynrules_to_ufo_export_contract.md",
            "docs/madgraph_smoke_test_plan.md",
            "docs/software_track_readiness_gates.md",
            "docs/phase_three_k_gate_status.md",
        ]
    ).lower()
    for phrase in [
        "complete bhsm 4d lagrangian exported = true",
        "production feynrules file exported = true",
        "feynrules syntax validated = true",
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
        "zenodo doi assigned",
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

