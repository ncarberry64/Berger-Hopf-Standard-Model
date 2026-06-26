import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PHASE_THREE_J_STATUS = (
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


def test_phase_three_j_artifacts_exist_and_parse() -> None:
    for relative in [
        "artifacts/BHSM_minimal_bounded_lagrangian_subset_v1_2.json",
        "artifacts/BHSM_included_excluded_vertex_families_v1_2.json",
        "artifacts/BHSM_bounded_feynrules_prep_lagrangian_v1_2.json",
        "artifacts/BHSM_minimal_runtime_parameter_requirements_v1_2.json",
        "artifacts/BHSM_phase_three_j_gate_status_v1_2.json",
    ]:
        payload = load(relative)
        assert isinstance(payload, dict), relative
        assert_guardrails(payload)


def test_phase_three_j_docs_and_readme_preserve_status() -> None:
    for relative in [
        "docs/phase_three_j_minimal_collider_lagrangian.md",
        "docs/minimal_bounded_lagrangian_subset.md",
        "docs/included_excluded_vertex_families.md",
        "docs/bounded_feynrules_prep_lagrangian.md",
        "docs/minimal_runtime_parameter_requirements.md",
        "docs/phase_three_j_gate_status.md",
    ]:
        assert (ROOT / relative).exists(), relative

    readme = " ".join(read("README.md").split())
    assert PHASE_THREE_J_STATUS in readme
    assert "Phase Three-J minimal collider-interface Lagrangian subset" in read("README.md")
    assert "does not constitute the complete BHSM 4D Lagrangian" in read("README.md")


def test_minimal_subset_includes_only_bounded_ckm_pmns_currents() -> None:
    payload = load("artifacts/BHSM_minimal_bounded_lagrangian_subset_v1_2.json")
    assert payload["subset_statement"] == (
        "This is a minimal bounded collider-interface Lagrangian subset, "
        "not the complete BHSM 4D Lagrangian."
    )
    assert payload["included_terms"] == [
        "L_kin_canonical_basis",
        "L_gauge_target_convention",
        "L_CKM_charged_current_bounded",
        "L_PMNS_charged_current_bounded",
    ]
    assert "L_charged_boundary_response_candidate" in payload["excluded_terms"]
    assert "L_neutral_operator_candidate" in payload["excluded_terms"]
    assert "L_CP_holonomy_standalone_candidate" in payload["excluded_terms"]

    terms = {entry["term_id"]: entry for entry in payload["terms"]}
    assert terms["L_CKM_charged_current_bounded"]["included_in_minimal_subset"] is True
    assert terms["L_PMNS_charged_current_bounded"]["included_in_minimal_subset"] is True
    assert terms["L_CKM_charged_current_bounded"]["runtime_parameter_mode"] == "BHSM_COLLIDER_INTERFACE"
    assert terms["L_PMNS_charged_current_bounded"]["runtime_parameter_mode"] == "BHSM_COLLIDER_INTERFACE"
    assert terms["L_charged_boundary_response_candidate"]["included_in_minimal_subset"] is False
    assert "X_ch theorem missing" in terms["L_charged_boundary_response_candidate"]["exclusion_reason_if_excluded"]
    assert terms["L_neutral_operator_candidate"]["included_in_minimal_subset"] is False
    assert "Dirac-Majorana theorem missing" in terms["L_neutral_operator_candidate"]["exclusion_reason_if_excluded"]
    assert terms["L_CP_holonomy_standalone_candidate"]["included_in_minimal_subset"] is False
    assert "O_int theorem missing" in terms["L_CP_holonomy_standalone_candidate"]["exclusion_reason_if_excluded"]
    for term in payload["terms"]:
        assert term["is_production_feynrules_ready"] is False
        assert term["is_ufo_ready"] is False


def test_included_excluded_vertex_families_match_phase_three_scope() -> None:
    entries = {
        entry["vertex_family"]: entry
        for entry in load("artifacts/BHSM_included_excluded_vertex_families_v1_2.json")["entries"]
    }
    assert entries["q_charged_current_CKM_BH"]["included_in_minimal_subset"] is True
    assert entries["q_charged_current_CKM_BH"]["inclusion_or_exclusion_status"] == "INCLUDED_BOUNDED_COLLIDER_INTERFACE_TARGET"
    assert entries["lepton_charged_current_PMNS_BH"]["included_in_minimal_subset"] is True
    assert entries["lepton_charged_current_PMNS_BH"]["inclusion_or_exclusion_status"] == "INCLUDED_BOUNDED_COLLIDER_INTERFACE_TARGET"
    assert entries["charged_boundary_response_matrix"]["inclusion_or_exclusion_status"] == "EXCLUDED_OPEN_X_CH_THEOREM"
    assert entries["neutral_operator_kernel_BH"]["inclusion_or_exclusion_status"] == (
        "EXCLUDED_OPEN_NEUTRINO_BASIS_SCALE_DIRAC_MAJORANA_THEOREM"
    )
    assert entries["cp_holonomy_phase_attachment"]["inclusion_or_exclusion_status"] == "EXCLUDED_OPEN_O_INT_THEOREM"
    for entry in entries.values():
        assert entry["production_feynrules_ready"] is False
        assert entry["ufo_ready"] is False


def test_bounded_feynrules_prep_is_not_fr_or_ufo() -> None:
    payload = load("artifacts/BHSM_bounded_feynrules_prep_lagrangian_v1_2.json")
    assert payload["model_name"] == "BHSM_MINIMAL_COLLIDER_INTERFACE_PREP"
    assert payload["parameter_mode"] == "BHSM_COLLIDER_INTERFACE"
    assert payload["is_complete_bhsm_model"] is False
    assert payload["is_feynrules_file"] is False
    assert payload["is_ufo_model"] is False
    terms = {entry["term_id"]: entry for entry in payload["terms"]}
    assert "V_CKM_BH[i,j]" in terms["L_CC_q_BHSM_CKM"]["symbolic_expression"]
    assert "U_PMNS_BH[i,j]" in terms["L_CC_l_BHSM_PMNS"]["symbolic_expression"]
    assert "g2_BH_runtime is a runtime/scheme parameter" in payload["required_statements"][0]
    for term in payload["terms"]:
        assert term["translation_status"] == "FEYNRULES_PREP_CANDIDATE_NOT_FR_FILE"
        assert term["empirical_derivation_inputs_used"] is False
        assert term["boundary_predictions_modified_by_runtime_inputs"] is False


def test_runtime_requirements_distinguish_bhsm_sources_from_runtime_inputs() -> None:
    payload = load("artifacts/BHSM_minimal_runtime_parameter_requirements_v1_2.json")
    assert payload["numerical_values_inserted"] is False
    requirements = {entry["parameter_id"]: entry for entry in payload["requirements"]}
    for key in [
        "g2_BH_runtime",
        "W_mass_runtime",
        "W_width_runtime",
        "fermion_masses_runtime",
        "fermion_widths_runtime",
        "neutrino_runtime_convention_for_PMNS_labels",
        "renormalization_scale_runtime",
    ]:
        assert requirements[key]["is_runtime_input"] is True
        assert requirements[key]["is_BHSM_derived"] is False
        assert requirements[key]["allowed_in_BHSM_PURE_NOFIT"] is False
        assert requirements[key]["allowed_in_BHSM_COLLIDER_INTERFACE"] is True
        assert requirements[key]["empirical_derivation_inputs_used"] is False
        assert requirements[key]["boundary_predictions_modified_by_runtime_input"] is False

    assert requirements["CKM_BH_source_matrix"]["is_BHSM_derived"] is True
    assert requirements["CKM_BH_source_matrix"]["is_runtime_input"] is False
    assert requirements["PMNS_BH_source_matrix"]["is_BHSM_derived"] is True
    assert requirements["PMNS_BH_source_matrix"]["is_runtime_input"] is False
    serialized = json.dumps(requirements).lower()
    assert "numerical_value" not in serialized
    assert "pdg" not in serialized


def test_phase_three_j_gate_status_sets_prep_true_and_production_false() -> None:
    payload = load("artifacts/BHSM_phase_three_j_gate_status_v1_2.json")
    assert payload["minimal_bounded_lagrangian_subset_exported"] is True
    assert payload["included_excluded_vertex_families_exported"] is True
    assert payload["bounded_feynrules_prep_lagrangian_exported"] is True
    assert payload["minimal_runtime_parameter_requirements_exported"] is True
    assert payload["canonical_production_basis_preserved"] is True
    assert payload["interface_normalization_gate_cleared"] is True
    assert payload["ckm_minimal_current_included"] is True
    assert payload["pmns_minimal_current_included"] is True
    assert payload["charged_boundary_response_excluded"] is True
    assert payload["neutral_kernel_excluded"] is True
    assert payload["standalone_cp_holonomy_excluded"] is True
    assert payload["complete_bhsm_4d_lagrangian_exported"] is False
    assert payload["minimal_collider_interface_lagrangian_exported"] is True
    assert payload["feynrules_prep_ready"] is True
    assert payload["production_feynrules_file_exported"] is False
    for key in [
        "ufo_ready",
        "madgraph_ready",
        "lhe_generation_ready",
        "hepmc_generation_ready",
        "athena_ready",
        "cmssw_ready",
    ]:
        assert payload[key] is False
    assert payload["empirical_runtime_inputs_allowed_in_collider_mode"] is True
    assert "FeynRules-prep only" in payload["recommended_status_language"]


def test_phase_three_j_tools_export_to_temporary_outputs(tmp_path: Path) -> None:
    commands = [
        ("tools/export_minimal_bounded_lagrangian_subset_v1_2.py", "--output", str(tmp_path / "subset.json")),
        ("tools/export_included_excluded_vertex_families_v1_2.py", "--output", str(tmp_path / "vertices.json")),
        ("tools/export_bounded_feynrules_prep_lagrangian_v1_2.py", "--output", str(tmp_path / "prep.json")),
        ("tools/export_minimal_runtime_parameter_requirements_v1_2.py", "--output", str(tmp_path / "runtime.json")),
    ]
    for command in commands:
        result = run_tool(*command)
        assert result.returncode == 0, result.stderr
    result = run_tool("tools/check_phase_three_j_gate_status.py", "--output", str(tmp_path / "status.json"))
    assert result.returncode == 0, result.stderr

    assert json.loads((tmp_path / "subset.json").read_text(encoding="utf-8"))["included_terms"][2] == "L_CKM_charged_current_bounded"
    assert json.loads((tmp_path / "vertices.json").read_text(encoding="utf-8"))["entries"][0]["included_in_minimal_subset"] is True
    assert json.loads((tmp_path / "prep.json").read_text(encoding="utf-8"))["is_feynrules_file"] is False
    assert json.loads((tmp_path / "runtime.json").read_text(encoding="utf-8"))["numerical_values_inserted"] is False
    assert json.loads((tmp_path / "status.json").read_text(encoding="utf-8"))["feynrules_prep_ready"] is True


def test_no_fake_files_values_or_forbidden_phase_three_j_claims() -> None:
    forbidden_suffixes = {".lhe", ".hepmc", ".hepmc3", ".fr"}
    bad_files = [
        path
        for path in ROOT.rglob("*")
        if path.is_file() and path.suffix.lower() in forbidden_suffixes
    ]
    assert bad_files == []

    combined = "\n".join(
        read(relative)
        for relative in [
            "README.md",
            "docs/phase_three_j_minimal_collider_lagrangian.md",
            "docs/minimal_bounded_lagrangian_subset.md",
            "docs/included_excluded_vertex_families.md",
            "docs/bounded_feynrules_prep_lagrangian.md",
            "docs/minimal_runtime_parameter_requirements.md",
            "docs/phase_three_j_gate_status.md",
        ]
    ).lower()
    for phrase in [
        "production feynrules readiness is complete",
        "production feynrules file exported = true",
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
        "fake mass inserted",
        "fake width inserted",
        "fake feynman rule inserted",
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
