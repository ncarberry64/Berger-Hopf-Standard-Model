import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PHASE_THREE_I_STATUS = (
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


def test_phase_three_i_artifacts_exist_and_parse() -> None:
    for relative in [
        "artifacts/BHSM_x_ch_charged_boundary_response_theorem_v1_1.json",
        "artifacts/BHSM_neutrino_dirac_majorana_basis_scale_theorem_v1_1.json",
        "artifacts/BHSM_cp_holonomy_o_int_attachment_theorem_v1_1.json",
        "artifacts/BHSM_interaction_theorem_closure_audit_v1_1.json",
        "artifacts/BHSM_phase_three_i_gate_status_v1_1.json",
    ]:
        payload = load(relative)
        assert isinstance(payload, dict), relative
        assert_guardrails(payload)


def test_phase_three_i_docs_and_readme_preserve_status() -> None:
    for relative in [
        "docs/phase_three_i_interaction_theorem_closure.md",
        "docs/x_ch_charged_boundary_response_theorem.md",
        "docs/neutrino_dirac_majorana_basis_scale_theorem.md",
        "docs/cp_holonomy_o_int_attachment_theorem.md",
        "docs/interaction_theorem_closure_audit.md",
        "docs/phase_three_i_gate_status.md",
    ]:
        assert (ROOT / relative).exists(), relative

    readme = " ".join(read("README.md").split())
    assert PHASE_THREE_I_STATUS in readme
    assert "Phase Three-I interaction-theorem closure status" in read("README.md")
    assert "does not constitute complete 4D Lagrangian" in read("README.md")


def test_x_ch_theorem_keeps_charged_boundary_response_blocked() -> None:
    payload = load("artifacts/BHSM_x_ch_charged_boundary_response_theorem_v1_1.json")
    assert payload["theorem_status"] == "OPEN_EXACT_MISSING_THEOREM"
    assert payload["candidate_X_ch_symbol"] == "X_ch^mu"
    assert payload["derived_from_repo_artifact"] is False
    assert payload["derived_conditional_from_author_axiom"] is False
    assert payload["standard_target_convention_used"] is True
    assert payload["is_identified_with_W_mu"] is False
    assert payload["is_distinct_boundary_response_operator"] is True
    assert payload["promotes_charged_boundary_response"] is False
    assert payload["promotion_status"] == "FORBIDDEN_TO_PROMOTE_WITHOUT_NEW_THEOREM"
    assert payload["feynrules_ready"] is False
    assert payload["ufo_ready"] is False
    assert "spin" in payload["missing_if_open"]


def test_neutrino_theorem_keeps_k_nu_boundary_source_only() -> None:
    payload = load("artifacts/BHSM_neutrino_dirac_majorana_basis_scale_theorem_v1_1.json")
    assert payload["theorem_status"] == "OPEN_EXACT_MISSING_THEOREM"
    assert payload["K_nu_status"] == "BOUNDARY_OPERATOR_SOURCE_ONLY"
    assert payload["basis_status"] == "PARTIAL_FOR_PMNS_TARGET_LABELS"
    assert payload["scale_status"] == "OPEN"
    assert payload["dirac_majorana_status"] == "OPEN"
    assert payload["promotes_neutral_kernel"] is False
    assert payload["feynrules_ready"] is False
    assert payload["ufo_ready"] is False
    assert "K_nu_as_physical_neutrino_mass_matrix" in payload["forbidden_promotions"]


def test_cp_o_int_theorem_keeps_standalone_cp_vertex_blocked() -> None:
    payload = load("artifacts/BHSM_cp_holonomy_o_int_attachment_theorem_v1_1.json")
    assert payload["theorem_status"] == "OPEN_EXACT_MISSING_THEOREM"
    assert payload["delta_BH"] == "pi/3"
    assert payload["holonomy_source"] == "CP_no_fit_holonomy_output_v1"
    assert payload["attached_to_CKM_PMNS_mixing"] is True
    assert payload["standalone_attachment_defined"] is False
    assert payload["promotes_standalone_cp_vertex"] is False
    assert payload["feynrules_ready"] is False
    assert payload["ufo_ready"] is False
    assert "O_int" in payload["missing_if_open"]


def test_interaction_theorem_closure_audit_summarizes_three_blockers() -> None:
    entries = {
        entry["theorem_id"]: entry
        for entry in load("artifacts/BHSM_interaction_theorem_closure_audit_v1_1.json")["entries"]
    }
    assert set(entries) == {
        "X_ch_charged_boundary_response",
        "neutrino_dirac_majorana_basis_scale",
        "cp_holonomy_O_int_attachment",
    }
    for entry in entries.values():
        assert entry["closure_result"] == "NOT_CLOSED_EXACT_MISSING_THEOREM_LOCALIZED"
        assert entry["promoted_vertices"] == []
        assert entry["feynrules_ready"] is False
        assert entry["ufo_ready"] is False
    assert entries["X_ch_charged_boundary_response"]["still_blocked_vertices"] == ["charged_boundary_response_matrix"]
    assert entries["neutrino_dirac_majorana_basis_scale"]["still_blocked_vertices"] == ["neutral_operator_kernel_BH"]
    assert entries["cp_holonomy_O_int_attachment"]["still_blocked_vertices"] == ["cp_holonomy_phase_attachment"]


def test_phase_three_i_gate_status_keeps_all_production_gates_closed() -> None:
    payload = load("artifacts/BHSM_phase_three_i_gate_status_v1_1.json")
    assert payload["x_ch_theorem_exported"] is True
    assert payload["neutrino_dirac_majorana_theorem_exported"] is True
    assert payload["cp_o_int_theorem_exported"] is True
    assert payload["interaction_theorem_closure_audit_exported"] is True
    assert payload["x_ch_theorem_status"] == "OPEN_EXACT_MISSING_THEOREM_FOR_BOUNDARY_RESPONSE"
    assert payload["neutrino_basis_status"] == "PARTIAL_FOR_PMNS_TARGET_LABELS"
    assert payload["neutrino_scale_status"] == "OPEN"
    assert payload["dirac_majorana_status"] == "OPEN"
    assert payload["cp_o_int_status"] == "OPEN_EXACT_MISSING_THEOREM_FOR_STANDALONE_VERTEX"
    assert payload["ckm_pmns_mediator_status"] == "STANDARD_TARGET_CONVENTION_FOR_CHARGED_CURRENT_ONLY"
    assert payload["ckm_pmns_cp_attachment_status"] == "PARTIALLY_RESOLVED_THROUGH_MIXING_SOURCES"
    assert payload["charged_boundary_response_promoted"] is False
    assert payload["neutral_kernel_promoted"] is False
    assert payload["standalone_cp_holonomy_vertex_promoted"] is False
    assert payload["any_new_vertex_promoted_to_feynrules_ready"] is False
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
    assert "not complete 4D Lagrangian export" in payload["recommended_status_language"]


def test_phase_three_i_tools_export_to_temporary_outputs(tmp_path: Path) -> None:
    commands = [
        ("tools/export_x_ch_charged_boundary_response_theorem_v1_1.py", "--output", str(tmp_path / "xch.json")),
        ("tools/export_neutrino_dirac_majorana_basis_scale_theorem_v1_1.py", "--output", str(tmp_path / "nu.json")),
        ("tools/export_cp_holonomy_o_int_attachment_theorem_v1_1.py", "--output", str(tmp_path / "cp.json")),
    ]
    for command in commands:
        result = run_tool(*command)
        assert result.returncode == 0, result.stderr

    result = run_tool("tools/export_interaction_theorem_closure_audit_v1_1.py", "--output", str(tmp_path / "audit.json"))
    assert result.returncode == 0, result.stderr
    result = run_tool("tools/check_phase_three_i_gate_status.py", "--output", str(tmp_path / "status.json"))
    assert result.returncode == 0, result.stderr

    assert json.loads((tmp_path / "xch.json").read_text(encoding="utf-8"))["promotes_charged_boundary_response"] is False
    assert json.loads((tmp_path / "nu.json").read_text(encoding="utf-8"))["K_nu_status"] == "BOUNDARY_OPERATOR_SOURCE_ONLY"
    assert json.loads((tmp_path / "cp.json").read_text(encoding="utf-8"))["standalone_attachment_defined"] is False
    assert json.loads((tmp_path / "audit.json").read_text(encoding="utf-8"))["entries"][0]["feynrules_ready"] is False
    assert json.loads((tmp_path / "status.json").read_text(encoding="utf-8"))["ufo_ready"] is False


def test_no_fake_event_files_values_or_forbidden_phase_three_i_claims() -> None:
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
            "docs/phase_three_i_interaction_theorem_closure.md",
            "docs/x_ch_charged_boundary_response_theorem.md",
            "docs/neutrino_dirac_majorana_basis_scale_theorem.md",
            "docs/cp_holonomy_o_int_attachment_theorem.md",
            "docs/interaction_theorem_closure_audit.md",
            "docs/phase_three_i_gate_status.md",
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
        "uses pdg values",
        "pdg values inserted as inputs",
        "fake mass",
        "fake width",
        "fake feynman rule",
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
