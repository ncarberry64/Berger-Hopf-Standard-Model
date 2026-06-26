import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PHASE_THREE_H_STATUS = (
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


def test_phase_three_h_artifacts_exist_and_parse() -> None:
    for relative in [
        "artifacts/BHSM_x_ch_interaction_operator_resolution_attempt_v1_0.json",
        "artifacts/BHSM_neutrino_basis_scale_resolution_attempt_v1_0.json",
        "artifacts/BHSM_cp_holonomy_attachment_resolution_attempt_v1_0.json",
        "artifacts/BHSM_bounded_vertex_promotion_audit_v1_0.json",
        "artifacts/BHSM_phase_three_h_gate_status_v1_0.json",
    ]:
        payload = load(relative)
        assert isinstance(payload, dict), relative
        assert_guardrails(payload)


def test_phase_three_h_docs_and_readme_preserve_status() -> None:
    for relative in [
        "docs/phase_three_h_bounded_blocker_resolution.md",
        "docs/x_ch_interaction_operator_resolution_attempt.md",
        "docs/neutrino_basis_scale_resolution_attempt.md",
        "docs/cp_holonomy_attachment_resolution_attempt.md",
        "docs/bounded_vertex_promotion_audit.md",
        "docs/phase_three_h_gate_status.md",
    ]:
        assert (ROOT / relative).exists(), relative

    readme = " ".join(read("README.md").split())
    assert PHASE_THREE_H_STATUS in readme
    assert "Phase Three-H bounded blocker resolution status" in read("README.md")
    assert "does not constitute complete 4D Lagrangian export" in read("README.md")


def test_x_ch_partial_resolution_does_not_promote_boundary_response() -> None:
    payload = load("artifacts/BHSM_x_ch_interaction_operator_resolution_attempt_v1_0.json")
    assert payload["resolution_status"] == "PARTIALLY_RESOLVED_FOR_SPECIFIC_VERTEX_FAMILY"
    assert payload["standard_target_convention_used"] is True
    assert payload["derived_from_repo_artifact"] is False
    assert "q_charged_current_CKM_BH" in payload["promoted_vertex_families"]
    assert "lepton_charged_current_PMNS_BH" in payload["promoted_vertex_families"]
    assert payload["still_blocked_vertex_families"] == ["charged_boundary_response_matrix"]
    assert "not collapsed into W exchange" in payload["notes"]
    assert payload["feynrules_ready"] is False
    assert payload["ufo_ready"] is False


def test_neutrino_kernel_not_promoted_to_physical_mass_matrix() -> None:
    payload = load("artifacts/BHSM_neutrino_basis_scale_resolution_attempt_v1_0.json")
    assert payload["basis_resolution_status"] == "PARTIALLY_RESOLVED_FOR_PMNS_CHARGED_CURRENT_TARGET"
    assert payload["scale_resolution_status"] == "OPEN"
    assert payload["dirac_majorana_status"] == "OPEN"
    assert payload["promoted_vertex_families"] == ["lepton_charged_current_PMNS_BH"]
    assert payload["still_blocked_vertex_families"] == ["neutral_operator_kernel_BH"]
    assert "not yet a collider neutrino mass matrix" in payload["notes"]
    assert payload["feynrules_ready"] is False
    assert payload["ufo_ready"] is False


def test_cp_holonomy_partial_resolution_keeps_standalone_vertex_blocked() -> None:
    payload = load("artifacts/BHSM_cp_holonomy_attachment_resolution_attempt_v1_0.json")
    assert payload["delta_BH"] == "pi/3"
    assert payload["holonomy_source"] == "CP_no_fit_holonomy_output_v1"
    assert payload["attachment_resolution_status"] == "PARTIALLY_RESOLVED_FOR_CKM_PMNS_MIXING_VERTICES"
    assert "q_charged_current_CKM_BH" in payload["promoted_vertex_families"]
    assert "lepton_charged_current_PMNS_BH" in payload["promoted_vertex_families"]
    assert payload["still_blocked_vertex_families"] == ["cp_holonomy_phase_attachment"]
    assert "missing O_int" in payload["notes"]
    assert payload["feynrules_ready"] is False
    assert payload["ufo_ready"] is False


def test_bounded_vertex_promotion_audit_promotes_only_ckm_pmns() -> None:
    entries = {
        entry["vertex_family"]: entry
        for entry in load("artifacts/BHSM_bounded_vertex_promotion_audit_v1_0.json")["entries"]
    }
    assert entries["q_charged_current_CKM_BH"]["promotion_result"] == "PARTIALLY_PROMOTED_TO_BOUNDED_COLLIDER_INTERFACE_TARGET"
    assert entries["lepton_charged_current_PMNS_BH"]["promotion_result"] == "PARTIALLY_PROMOTED_TO_BOUNDED_COLLIDER_INTERFACE_TARGET"
    assert entries["charged_boundary_response_matrix"]["promotion_result"] == "NOT_PROMOTED"
    assert entries["neutral_operator_kernel_BH"]["promotion_result"] == "NOT_PROMOTED"
    assert entries["cp_holonomy_phase_attachment"]["promotion_result"] == "NOT_PROMOTED_AS_STANDALONE_VERTEX"
    for entry in entries.values():
        assert entry["pure_no_fit_ready"] is False
        assert entry["feynrules_ready"] is False
        assert entry["ufo_ready"] is False
        assert entry["madgraph_ready"] is False
        assert "not production readiness" in entry["notes"]


def test_phase_three_h_gate_status_keeps_production_readiness_false() -> None:
    payload = load("artifacts/BHSM_phase_three_h_gate_status_v1_0.json")
    assert payload["x_ch_resolution_attempt_exported"] is True
    assert payload["neutrino_basis_scale_resolution_attempt_exported"] is True
    assert payload["cp_holonomy_attachment_resolution_attempt_exported"] is True
    assert payload["bounded_vertex_promotion_audit_exported"] is True
    assert payload["x_ch_status"] == "PARTIALLY_RESOLVED_FOR_STANDARD_CHARGED_CURRENT_TARGETS_OR_OPEN_FOR_BOUNDARY_RESPONSE"
    assert payload["neutrino_basis_status"] == "PARTIALLY_RESOLVED_FOR_PMNS_TARGET_OR_OPEN_FOR_NEUTRAL_KERNEL"
    assert payload["neutrino_scale_status"] == "OPEN"
    assert payload["cp_holonomy_attachment_status"] == "PARTIALLY_RESOLVED_FOR_CKM_PMNS_MIXING_VERTICES_OR_OPEN_FOR_STANDALONE_CP_VERTEX"
    assert payload["ckm_vertex_bounded_promotion"] is True
    assert payload["pmns_vertex_bounded_promotion"] is True
    assert payload["charged_boundary_response_promoted"] is False
    assert payload["neutral_kernel_promoted"] is False
    assert payload["standalone_cp_holonomy_vertex_promoted"] is False
    for key in [
        "complete_4d_lagrangian_exported",
        "production_vertex_table_complete",
        "mass_width_scheme_complete_for_pure_no_fit",
        "renormalization_scheme_complete",
        "feynrules_ready",
        "ufo_ready",
        "madgraph_ready",
        "lhe_generation_ready",
        "hepmc_generation_ready",
        "athena_ready",
        "cmssw_ready",
    ]:
        assert payload[key] is False
    assert payload["empirical_runtime_inputs_allowed_in_collider_mode"] is True
    assert "This is not production FeynRules/UFO readiness" in payload["recommended_status_language"]


def test_phase_three_h_tools_export_to_temporary_outputs(tmp_path: Path) -> None:
    commands = [
        ("tools/export_x_ch_interaction_operator_resolution_attempt_v1_0.py", "--output", str(tmp_path / "xch.json")),
        ("tools/export_neutrino_basis_scale_resolution_attempt_v1_0.py", "--output", str(tmp_path / "nu.json")),
        ("tools/export_cp_holonomy_attachment_resolution_attempt_v1_0.py", "--output", str(tmp_path / "cp.json")),
        ("tools/export_bounded_vertex_promotion_audit_v1_0.py", "--output", str(tmp_path / "promotion.json")),
        ("tools/check_phase_three_h_gate_status.py", "--output", str(tmp_path / "status.json")),
    ]
    for command in commands:
        result = run_tool(*command)
        assert result.returncode == 0, result.stderr

    assert json.loads((tmp_path / "xch.json").read_text(encoding="utf-8"))["feynrules_ready"] is False
    assert json.loads((tmp_path / "nu.json").read_text(encoding="utf-8"))["scale_resolution_status"] == "OPEN"
    assert json.loads((tmp_path / "cp.json").read_text(encoding="utf-8"))["delta_BH"] == "pi/3"
    assert json.loads((tmp_path / "promotion.json").read_text(encoding="utf-8"))["entries"][0]["feynrules_ready"] is False
    assert json.loads((tmp_path / "status.json").read_text(encoding="utf-8"))["ufo_ready"] is False


def test_no_fake_event_files_or_forbidden_phase_three_h_claims() -> None:
    suffixes = {".lhe", ".hepmc", ".hepmc3"}
    event_files = [
        path
        for path in ROOT.rglob("*")
        if path.is_file() and path.suffix.lower() in suffixes
    ]
    assert event_files == []

    combined = "\n".join(
        read(relative)
        for relative in [
            "README.md",
            "docs/phase_three_h_bounded_blocker_resolution.md",
            "docs/x_ch_interaction_operator_resolution_attempt.md",
            "docs/neutrino_basis_scale_resolution_attempt.md",
            "docs/cp_holonomy_attachment_resolution_attempt.md",
            "docs/bounded_vertex_promotion_audit.md",
            "docs/phase_three_h_gate_status.md",
        ]
    ).lower()
    for phrase in [
        "feynrules_ready = true",
        "ufo_ready = true",
        "madgraph_ready = true",
        "lhe_generation_ready = true",
        "hepmc_generation_ready = true",
        "athena_ready = true",
        "cmssw_ready = true",
        "official cern integration",
        "bhsm is empirically validated",
        "bhsm is empirically proven",
        "zenodo doi assigned",
        "production feynrules model is ready",
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

