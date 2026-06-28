import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PHASE_THREE_D_STATUS = (
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


def test_phase_three_d_artifacts_exist_and_parse() -> None:
    for relative in [
        "artifacts/BHSM_canonical_field_target_conventions_v0_6.json",
        "artifacts/BHSM_vector_fermion_normalization_status_v0_6.json",
        "artifacts/BHSM_chiral_current_attachment_map_v0_6.json",
        "artifacts/BHSM_mass_width_renormalization_open_gates_v0_6.json",
        "artifacts/BHSM_phase_three_d_gate_status_v0_6.json",
    ]:
        payload = load(relative)
        assert isinstance(payload, dict), relative
        assert payload["empirical_derivation_inputs_used"] is False
        assert payload["boundary_predictions_modified_by_comparison"] is False
        assert payload["official_predictions_changed"] is False
        assert payload["source_model_files_changed"] is False


def test_phase_three_d_docs_and_readme_preserve_boundaries() -> None:
    for relative in [
        "docs/phase_three_d_canonical_current_attachment.md",
        "docs/canonical_field_target_conventions.md",
        "docs/chiral_current_attachment_map.md",
        "docs/vector_fermion_normalization_status.md",
        "docs/mass_width_renormalization_open_gates.md",
        "docs/phase_three_d_gate_status.md",
    ]:
        assert (ROOT / relative).exists(), relative

    readme = " ".join(read("docs/archive/README_status_history_pre_v0_7.md").split())
    assert PHASE_THREE_D_STATUS in readme
    assert "Phase Three-D canonical current interface status" in read("docs/archive/README_status_history_pre_v0_7.md")
    assert "This does not constitute production FeynRules, UFO, MadGraph" in read("docs/archive/README_status_history_pre_v0_7.md")


def test_canonical_field_target_conventions_preserve_zh_and_label_targets() -> None:
    payload = load("artifacts/BHSM_canonical_field_target_conventions_v0_6.json")
    assert payload["canonical_field_target_convention_exported"] is True
    assert payload["BHSM_Z_H_preserved"] is True
    entries = {entry["convention_id"]: entry for entry in payload["entries"]}

    scalar = entries["scalar_field"]
    assert scalar["candidate_Z_symbol"] == "Z_H"
    assert scalar["candidate_Z_value"] == 1
    assert scalar["classification"] in {"BHSM_DERIVED_VALUE", "DERIVED_CONDITIONAL_FROM_AUTHOR_AXIOM"}
    assert scalar["is_BHSM_derived"] is True
    assert scalar["ufo_ready"] is False

    vector = entries["vector_gauge_field"]
    assert vector["candidate_Z_symbol"] == "Z_A_target"
    assert vector["candidate_Z_value"] == 1
    assert vector["classification"] == "STANDARD_HEP_TARGET_CONVENTION"
    assert vector["is_BHSM_derived"] is False
    assert vector["is_standard_target_convention"] is True
    assert "not a BHSM empirical fit" in vector["notes"]

    fermion = entries["fermion_field"]
    assert fermion["candidate_Z_symbol"] == "Z_psi_target"
    assert fermion["candidate_Z_value"] == 1
    assert fermion["classification"] == "STANDARD_HEP_TARGET_CONVENTION"
    assert fermion["is_BHSM_derived"] is False
    assert fermion["is_standard_target_convention"] is True
    assert "not a BHSM empirical fit" in fermion["notes"]


def test_vector_fermion_normalization_status_is_not_bhsm_derived_for_za_zpsi() -> None:
    payload = load("artifacts/BHSM_vector_fermion_normalization_status_v0_6.json")
    assert payload["Z_A_status"] == "STANDARD_TARGET_CONVENTION_OR_BLOCKED_NOT_BHSM_DERIVED"
    assert payload["Z_psi_status"] == "STANDARD_TARGET_CONVENTION_OR_BLOCKED_NOT_BHSM_DERIVED"
    entries = {entry["field_or_sector_id"]: entry for entry in payload["entries"]}
    for expected in [
        "profile_scalar_H",
        "gauge_gluon_target",
        "gauge_weak_target",
        "gauge_hypercharge_target",
        "lepton_left_doublet",
        "charged_lepton_right",
        "quark_left_doublet",
        "up_quark_right",
        "down_quark_right",
        "neutral_sector",
    ]:
        assert expected in entries
        assert entries[expected]["ufo_ready"] is False

    assert entries["profile_scalar_H"]["candidate_Z_symbol"] == "Z_H"
    assert entries["profile_scalar_H"]["candidate_Z_value"] == 1
    assert entries["profile_scalar_H"]["is_BHSM_derived"] is True

    for key in ["gauge_gluon_target", "gauge_weak_target", "gauge_hypercharge_target"]:
        assert entries[key]["candidate_Z_symbol"] == "Z_A_target"
        assert entries[key]["candidate_Z_value"] == 1
        assert entries[key]["is_BHSM_derived"] is False
        assert entries[key]["is_standard_target_convention"] is True

    for key in [
        "lepton_left_doublet",
        "charged_lepton_right",
        "quark_left_doublet",
        "up_quark_right",
        "down_quark_right",
        "neutral_sector",
    ]:
        assert entries[key]["candidate_Z_symbol"] == "Z_psi_target"
        assert entries[key]["candidate_Z_value"] == 1
        assert entries[key]["is_BHSM_derived"] is False
        assert entries[key]["is_standard_target_convention"] is True


def test_chiral_current_attachment_map_is_sourced_but_not_ready() -> None:
    payload = load("artifacts/BHSM_chiral_current_attachment_map_v0_6.json")
    assert payload["CKM_current_target_identified"] is True
    assert payload["PMNS_current_target_identified"] is True
    assert payload["charged_boundary_source_preserved"] is True
    assert payload["neutral_boundary_source_preserved"] is True
    entries = {entry["current_family_id"]: entry for entry in payload["entries"]}

    ckm = entries["q_charged_current_CKM_BH"]
    assert "V_CKM_BH" in ckm["target_expression"]
    assert ckm["lorentz_structure_status"] == "STANDARD_HEP_TARGET_CONVENTION"
    assert ckm["mixing_matrix_status"] == "DERIVED_FROM_REPO_ARTIFACT"
    assert "CKM_no_fit_operator_output_v1" in ckm["mixing_matrix_source"]
    assert ckm["coupling_source"] == "g2_BH_candidate"
    assert ckm["coupling_status"] == "SCHEME_CONDITIONAL"
    assert ckm["feynrules_ready"] is False
    assert ckm["ufo_ready"] is False

    pmns = entries["lepton_charged_current_PMNS_BH"]
    assert "U_PMNS_BH" in pmns["target_expression"]
    assert pmns["lorentz_structure_status"] == "STANDARD_HEP_TARGET_CONVENTION"
    assert pmns["mixing_matrix_status"] == "DERIVED_FROM_REPO_ARTIFACT"
    assert "PMNS_no_fit_operator_output_v1" in pmns["mixing_matrix_source"]
    assert pmns["coupling_status"] == "SCHEME_CONDITIONAL"
    assert pmns["feynrules_ready"] is False
    assert pmns["ufo_ready"] is False

    charged = entries["charged_boundary_response_matrix"]
    assert charged["coupling_status"] == "BOUNDARY_SOURCE_MATRIX_ONLY"
    assert charged["feynrules_ready"] is False
    assert charged["ufo_ready"] is False
    assert "interaction operator X_ch" in charged["missing_for_feynrules"]

    neutral = entries["neutral_operator_kernel_BH"]
    assert neutral["coupling_status"] == "BOUNDARY_SOURCE_MATRIX_ONLY"
    assert neutral["feynrules_ready"] is False
    assert neutral["ufo_ready"] is False
    assert "Dirac/Majorana convention" in neutral["missing_for_feynrules"]


def test_mass_width_and_renormalization_open_gates_are_explicit() -> None:
    payload = load("artifacts/BHSM_mass_width_renormalization_open_gates_v0_6.json")
    assert payload["mass_width_scheme_complete"] is False
    assert payload["renormalization_scheme_complete"] is False
    gates = {entry["gate_id"]: entry for entry in payload["entries"]}
    for gate in [
        "pole_mass_scheme",
        "running_mass_scheme",
        "decay_width_scheme",
        "gauge_boson_width_scheme",
        "fermion_width_scheme",
        "higgs_width_scheme",
        "neutrino_mass_scheme",
        "reference_scale",
        "gauge_coupling_scheme",
        "yukawa_scheme",
        "threshold_scheme",
        "counterterm_scheme",
        "running_scheme",
        "PDG_target_table",
        "MadGraph_validation",
    ]:
        assert gates[gate]["status"] == "OPEN"
        assert gates[gate]["blocks_feynrules"] is True
        assert gates[gate]["blocks_ufo"] is True
        assert gates[gate]["blocks_madgraph"] is True
        assert "No fake masses" in gates[gate]["notes"]


def test_phase_three_d_gate_status_keeps_readiness_false() -> None:
    payload = load("artifacts/BHSM_phase_three_d_gate_status_v0_6.json")
    assert payload["canonical_field_target_convention_exported"] is True
    assert payload["BHSM_Z_H_preserved"] is True
    assert payload["Z_A_status"] == "STANDARD_TARGET_CONVENTION_OR_BLOCKED_NOT_BHSM_DERIVED"
    assert payload["Z_psi_status"] == "STANDARD_TARGET_CONVENTION_OR_BLOCKED_NOT_BHSM_DERIVED"
    assert payload["chiral_current_attachment_map_exported"] is True
    assert payload["CKM_current_target_identified"] is True
    assert payload["PMNS_current_target_identified"] is True
    assert payload["charged_boundary_source_preserved"] is True
    assert payload["neutral_boundary_source_preserved"] is True
    for key in [
        "mass_width_scheme_complete",
        "renormalization_scheme_complete",
        "complete_4d_lagrangian_exported",
        "feynrules_ready",
        "ufo_ready",
        "madgraph_ready",
        "lhe_generation_ready",
        "hepmc_generation_ready",
        "athena_ready",
        "cmssw_ready",
    ]:
        assert payload[key] is False


def test_phase_three_d_tools_export_to_temporary_outputs(tmp_path: Path) -> None:
    commands = [
        ("tools/export_canonical_field_target_conventions_v0_6.py", "--output", str(tmp_path / "canonical.json")),
        ("tools/export_vector_fermion_normalization_status_v0_6.py", "--output", str(tmp_path / "norms.json")),
        ("tools/export_chiral_current_attachment_map_v0_6.py", "--output", str(tmp_path / "currents.json")),
        ("tools/export_mass_width_renormalization_open_gates_v0_6.py", "--output", str(tmp_path / "gates.json")),
        ("tools/check_phase_three_d_gate_status.py", "--output", str(tmp_path / "status.json")),
    ]
    for command in commands:
        result = run_tool(*command)
        assert result.returncode == 0, result.stderr

    assert json.loads((tmp_path / "canonical.json").read_text(encoding="utf-8"))["BHSM_Z_H_preserved"] is True
    assert json.loads((tmp_path / "norms.json").read_text(encoding="utf-8"))["Z_A_status"] == "STANDARD_TARGET_CONVENTION_OR_BLOCKED_NOT_BHSM_DERIVED"
    assert json.loads((tmp_path / "currents.json").read_text(encoding="utf-8"))["CKM_current_target_identified"] is True
    assert json.loads((tmp_path / "gates.json").read_text(encoding="utf-8"))["mass_width_scheme_complete"] is False
    assert json.loads((tmp_path / "status.json").read_text(encoding="utf-8"))["feynrules_ready"] is False


def test_no_fake_event_files_or_forbidden_claims() -> None:
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
            "docs/archive/README_status_history_pre_v0_7.md",
            "docs/phase_three_d_canonical_current_attachment.md",
            "docs/canonical_field_target_conventions.md",
            "docs/chiral_current_attachment_map.md",
            "docs/vector_fermion_normalization_status.md",
            "docs/mass_width_renormalization_open_gates.md",
            "docs/phase_three_d_gate_status.md",
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
