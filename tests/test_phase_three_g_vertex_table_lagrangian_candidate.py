import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PHASE_THREE_G_STATUS = (
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


def test_phase_three_g_artifacts_exist_and_parse() -> None:
    for relative in [
        "artifacts/BHSM_production_vertex_table_candidate_v0_9.json",
        "artifacts/BHSM_symbolic_4d_lagrangian_assembly_ledger_v0_9.json",
        "artifacts/BHSM_vertex_readiness_matrix_v0_9.json",
        "artifacts/BHSM_feynrules_export_blocker_table_v0_9.json",
        "artifacts/BHSM_runtime_parameter_dependency_table_v0_9.json",
        "artifacts/BHSM_phase_three_g_gate_status_v0_9.json",
    ]:
        payload = load(relative)
        assert isinstance(payload, dict), relative
        assert_guardrails(payload)


def test_phase_three_g_docs_and_readme_preserve_status() -> None:
    for relative in [
        "docs/phase_three_g_vertex_table_lagrangian_candidate.md",
        "docs/production_vertex_table_candidate.md",
        "docs/symbolic_4d_lagrangian_assembly_ledger.md",
        "docs/vertex_readiness_matrix.md",
        "docs/feynrules_export_blocker_table.md",
        "docs/runtime_parameter_dependency_table.md",
        "docs/phase_three_g_gate_status.md",
    ]:
        assert (ROOT / relative).exists(), relative

    readme = " ".join(read("README.md").split())
    assert PHASE_THREE_G_STATUS in readme
    assert "Phase Three-G production-vertex and Lagrangian-candidate status" in read("README.md")
    assert "not a production FeynRules model" in read("README.md")


def test_candidate_vertex_table_contains_required_families_and_blocks_readiness() -> None:
    payload = load("artifacts/BHSM_production_vertex_table_candidate_v0_9.json")
    assert payload["production_vertex_table_candidate_exported"] is True
    assert payload["production_vertex_table_complete"] is False
    entries = {entry["vertex_id"]: entry for entry in payload["entries"]}
    for vertex_id in [
        "q_charged_current_CKM_BH",
        "lepton_charged_current_PMNS_BH",
        "charged_boundary_response_matrix",
        "neutral_operator_kernel_BH",
        "cp_holonomy_phase_attachment",
    ]:
        assert vertex_id in entries
        assert entries[vertex_id]["canonical_basis_status"] == "CANONICAL_PRODUCTION_BASIS_DEFINED"
        assert entries[vertex_id]["pure_no_fit_ready"] is False
        assert entries[vertex_id]["feynrules_ready"] is False
        assert entries[vertex_id]["ufo_ready"] is False
        assert entries[vertex_id]["madgraph_ready"] is False


def test_ckm_pmns_targets_use_bhsm_sources_but_are_not_ready() -> None:
    entries = {
        entry["vertex_id"]: entry
        for entry in load("artifacts/BHSM_production_vertex_table_candidate_v0_9.json")["entries"]
    }
    ckm = entries["q_charged_current_CKM_BH"]
    assert "V_CKM_BH" in ckm["candidate_expression"]
    assert ckm["lorentz_structure_status"] == "STANDARD_HEP_TARGET_CONVENTION"
    assert ckm["gauge_structure_status"] == "TARGET_CONVENTION_PARTIAL"
    assert ckm["mixing_status"] == "DERIVED_FROM_REPO_ARTIFACT"
    assert "CKM_no_fit_operator_output_v1" in ckm["mixing_source"]
    assert ckm["coupling_status"] == "SCHEME_CONDITIONAL"
    assert ckm["mass_width_status"] == "OPEN"
    assert ckm["renormalization_status"] == "OPEN"
    assert ckm["feynrules_ready"] is False

    pmns = entries["lepton_charged_current_PMNS_BH"]
    assert "U_PMNS_BH" in pmns["candidate_expression"]
    assert pmns["lorentz_structure_status"] == "STANDARD_HEP_TARGET_CONVENTION"
    assert pmns["gauge_structure_status"] == "TARGET_CONVENTION_PARTIAL"
    assert pmns["mixing_status"] == "DERIVED_FROM_REPO_ARTIFACT"
    assert "PMNS_no_fit_operator_output_v1" in pmns["mixing_source"]
    assert "neutrino convention" in pmns["missing_for_feynrules"]
    assert pmns["feynrules_ready"] is False


def test_boundary_neutral_and_cp_vertices_preserve_sources_and_blockers() -> None:
    entries = {
        entry["vertex_id"]: entry
        for entry in load("artifacts/BHSM_production_vertex_table_candidate_v0_9.json")["entries"]
    }
    charged = entries["charged_boundary_response_matrix"]
    assert charged["coupling_status"] == "BOUNDARY_SOURCE_MATRIX_ONLY"
    assert charged["lorentz_structure_status"] == "BLOCKED_BY_MISSING_X_CH_OPERATOR"
    assert "C_ch_boundary_exact" in charged["raw_coefficient_or_matrix"]
    assert "X_ch is missing" in charged["notes"]

    neutral = entries["neutral_operator_kernel_BH"]
    assert neutral["coupling_status"] == "BOUNDARY_SOURCE_MATRIX_ONLY"
    assert neutral["lorentz_structure_status"] == "BLOCKED_BY_NEUTRINO_BASIS_SCALE_CONVENTION"
    assert "K_nu" in neutral["raw_coefficient_or_matrix"]
    assert "neutrino basis and scale are missing" in neutral["notes"]

    cp = entries["cp_holonomy_phase_attachment"]
    assert cp["coupling_status"] == "PHASE_SOURCE_ONLY"
    assert cp["holonomy_status"] == "DERIVED_FROM_REPO_ARTIFACT"
    assert cp["raw_coefficient_or_matrix"]["delta_BH"] == "pi/3"
    assert cp["lorentz_structure_status"] == "BLOCKED_BY_MISSING_INTERACTION_ATTACHMENT"
    assert "interaction attachment is missing" in cp["notes"]


def test_symbolic_lagrangian_ledger_is_not_complete_or_ready() -> None:
    payload = load("artifacts/BHSM_symbolic_4d_lagrangian_assembly_ledger_v0_9.json")
    assert payload["symbolic_4d_lagrangian_assembly_ledger_exported"] is True
    assert payload["complete_4d_lagrangian_exported"] is False
    assert "not a complete production 4D Lagrangian" in payload["ledger_statement"]
    terms = {term["term_id"]: term for term in payload["terms"]}
    for term_id in [
        "L_kin_canonical_basis",
        "L_CKM_charged_current_candidate",
        "L_PMNS_charged_current_candidate",
        "L_charged_boundary_response_candidate",
        "L_neutral_operator_candidate",
        "L_CP_holonomy_candidate",
        "L_mass_width_runtime_policy",
        "L_renormalization_placeholder",
    ]:
        assert term_id in terms
        assert terms[term_id]["is_complete_4d_term"] is False
        assert terms[term_id]["is_production_feynrules_ready"] is False
        assert terms[term_id]["is_ufo_ready"] is False
    assert terms["L_charged_boundary_response_candidate"]["status"] == "BLOCKED_BY_MISSING_X_CH_OPERATOR"
    assert terms["L_neutral_operator_candidate"]["status"] == "BLOCKED_BY_NEUTRINO_BASIS_SCALE_CONVENTION"
    assert terms["L_CP_holonomy_candidate"]["status"] == "BLOCKED_BY_MISSING_INTERACTION_ATTACHMENT"


def test_readiness_blockers_and_runtime_dependencies_are_explicit() -> None:
    readiness = load("artifacts/BHSM_vertex_readiness_matrix_v0_9.json")
    rows = {row["vertex_family"]: row for row in readiness["rows"]}
    assert rows["q_charged_current_CKM_BH"]["canonical_basis_ready"] is True
    assert rows["q_charged_current_CKM_BH"]["coupling_ready"] is False
    assert rows["q_charged_current_CKM_BH"]["mass_width_ready"] is False
    assert rows["charged_boundary_response_matrix"]["lorentz_structure_ready"] is False
    assert rows["neutral_operator_kernel_BH"]["gauge_structure_ready"] is False
    assert rows["cp_holonomy_phase_attachment"]["feynrules_ready"] is False

    blockers = {
        row["blocker_id"]: row
        for row in load("artifacts/BHSM_feynrules_export_blocker_table_v0_9.json")["blockers"]
    }
    for blocker_id in [
        "complete_particle_table",
        "complete_parameter_card",
        "mass_width_scheme",
        "renormalization_scheme",
        "gauge_fixing_scheme",
        "production_coupling_scheme",
        "complete_vertex_table",
        "neutrino_basis_and_scale",
        "X_ch_interaction_operator",
        "CP_interaction_attachment",
        "FeynRules_syntax_export",
        "UFO_loadability_test",
        "MadGraph_smoke_test",
    ]:
        assert blockers[blocker_id]["blocks_feynrules"] is True
        assert blockers[blocker_id]["blocks_ufo"] is True
        assert blockers[blocker_id]["blocks_madgraph"] is True

    runtime = load("artifacts/BHSM_runtime_parameter_dependency_table_v0_9.json")
    assert "BHSM_PURE_NOFIT uses no empirical runtime inputs" in runtime["policy_statement"]
    assert "not derivation inputs" in runtime["policy_statement"]
    for entry in runtime["entries"]:
        assert entry["empirical_derivation_inputs_used"] is False
        assert entry["boundary_predictions_modified_by_runtime_inputs"] is False


def test_phase_three_g_gate_status_keeps_production_readiness_false() -> None:
    payload = load("artifacts/BHSM_phase_three_g_gate_status_v0_9.json")
    assert payload["production_vertex_table_candidate_exported"] is True
    assert payload["symbolic_4d_lagrangian_assembly_ledger_exported"] is True
    assert payload["vertex_readiness_matrix_exported"] is True
    assert payload["feynrules_export_blocker_table_exported"] is True
    assert payload["runtime_parameter_dependency_table_exported"] is True
    assert payload["canonical_production_basis_preserved"] is True
    assert payload["interface_normalization_gate_cleared"] is True
    assert payload["runtime_mass_width_policy_defined"] is True
    assert payload["empirical_runtime_inputs_allowed_in_collider_mode"] is True
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
    assert "This is not production FeynRules/UFO readiness" in payload["recommended_status_language"]


def test_phase_three_g_tools_export_to_temporary_outputs(tmp_path: Path) -> None:
    commands = [
        ("tools/export_production_vertex_table_candidate_v0_9.py", "--output", str(tmp_path / "vertices.json")),
        ("tools/export_symbolic_4d_lagrangian_assembly_ledger_v0_9.py", "--output", str(tmp_path / "lagrangian.json")),
        ("tools/export_vertex_readiness_matrix_v0_9.py", "--output", str(tmp_path / "readiness.json")),
        ("tools/export_feynrules_export_blocker_table_v0_9.py", "--output", str(tmp_path / "blockers.json")),
        ("tools/export_runtime_parameter_dependency_table_v0_9.py", "--output", str(tmp_path / "runtime.json")),
        ("tools/check_phase_three_g_gate_status.py", "--output", str(tmp_path / "status.json")),
    ]
    for command in commands:
        result = run_tool(*command)
        assert result.returncode == 0, result.stderr

    assert json.loads((tmp_path / "vertices.json").read_text(encoding="utf-8"))["production_vertex_table_complete"] is False
    assert json.loads((tmp_path / "lagrangian.json").read_text(encoding="utf-8"))["complete_4d_lagrangian_exported"] is False
    assert json.loads((tmp_path / "readiness.json").read_text(encoding="utf-8"))["rows"][0]["feynrules_ready"] is False
    assert json.loads((tmp_path / "blockers.json").read_text(encoding="utf-8"))["blockers"][0]["blocks_feynrules"] is True
    assert json.loads((tmp_path / "runtime.json").read_text(encoding="utf-8"))["entries"][0]["boundary_predictions_modified_by_runtime_inputs"] is False
    assert json.loads((tmp_path / "status.json").read_text(encoding="utf-8"))["ufo_ready"] is False


def test_no_fake_event_files_or_forbidden_phase_three_g_claims() -> None:
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
            "docs/phase_three_g_vertex_table_lagrangian_candidate.md",
            "docs/production_vertex_table_candidate.md",
            "docs/symbolic_4d_lagrangian_assembly_ledger.md",
            "docs/vertex_readiness_matrix.md",
            "docs/feynrules_export_blocker_table.md",
            "docs/runtime_parameter_dependency_table.md",
            "docs/phase_three_g_gate_status.md",
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

