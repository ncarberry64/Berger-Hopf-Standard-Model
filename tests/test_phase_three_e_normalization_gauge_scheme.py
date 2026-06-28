import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PHASE_THREE_E_STATUS = (
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
    assert payload["boundary_predictions_modified_by_comparison"] is False
    assert payload["official_predictions_changed"] is False
    assert payload["source_model_files_changed"] is False


def test_phase_three_e_artifacts_exist_and_parse() -> None:
    for relative in [
        "artifacts/BHSM_vector_normalization_theorem_v0_7.json",
        "artifacts/BHSM_fermion_normalization_theorem_v0_7.json",
        "artifacts/BHSM_gauge_fixing_production_coupling_scheme_v0_7.json",
        "artifacts/BHSM_mass_width_scheme_candidate_v0_7.json",
        "artifacts/BHSM_renormalization_scheme_candidate_v0_7.json",
        "artifacts/BHSM_phase_three_e_gate_status_v0_7.json",
    ]:
        payload = load(relative)
        assert isinstance(payload, dict), relative
        assert_guardrails(payload)


def test_phase_three_e_docs_and_readme_preserve_status() -> None:
    for relative in [
        "docs/phase_three_e_normalization_gauge_scheme.md",
        "docs/vector_normalization_theorem.md",
        "docs/fermion_normalization_theorem.md",
        "docs/gauge_fixing_and_production_coupling_scheme.md",
        "docs/mass_width_scheme_candidate.md",
        "docs/renormalization_scheme_candidate.md",
        "docs/phase_three_e_gate_status.md",
    ]:
        assert (ROOT / relative).exists(), relative

    readme = " ".join(read("docs/archive/README_status_history_pre_v0_7.md").split())
    assert PHASE_THREE_E_STATUS in readme
    assert "Phase Three-E normalization and scheme status" in read("docs/archive/README_status_history_pre_v0_7.md")
    assert "This does not constitute production FeynRules, UFO, MadGraph" in read("docs/archive/README_status_history_pre_v0_7.md")


def test_vector_normalization_is_target_convention_not_bhsm_prediction() -> None:
    payload = load("artifacts/BHSM_vector_normalization_theorem_v0_7.json")
    assert payload["field_family"] == "vector_gauge_fields"
    assert payload["candidate_Z_A_symbol"] == "Z_A_target"
    assert payload["candidate_Z_A_value"] == 1
    assert payload["Z_A_status"] == "STANDARD_HEP_TARGET_CONVENTION"
    assert payload["is_BHSM_derived"] is False
    assert payload["is_standard_target_convention"] is True
    assert payload["feynrules_ready"] is False
    assert payload["ufo_ready"] is False
    assert "BHSM vector field-strength normalization theorem" in payload["missing_for_BHSM_derivation"]
    assert "not a BHSM-derived vector field-strength prediction" in payload["notes"]


def test_fermion_normalization_is_target_convention_for_all_required_families() -> None:
    payload = load("artifacts/BHSM_fermion_normalization_theorem_v0_7.json")
    assert payload["Z_psi_status"] == "STANDARD_HEP_TARGET_CONVENTION"
    entries = {entry["field_family"]: entry for entry in payload["entries"]}
    for family in [
        "lepton_left_doublet",
        "charged_lepton_right",
        "quark_left_doublet",
        "up_quark_right",
        "down_quark_right",
        "neutral_sector",
    ]:
        entry = entries[family]
        assert entry["candidate_Z_psi_symbol"] == "Z_psi_target"
        assert entry["candidate_Z_psi_value"] == 1
        assert entry["Z_psi_status"] == "STANDARD_HEP_TARGET_CONVENTION"
        assert entry["is_BHSM_derived"] is False
        assert entry["is_standard_target_convention"] is True
        assert entry["feynrules_ready"] is False
        assert entry["ufo_ready"] is False
        assert "not a BHSM-derived fermion field-strength prediction" in entry["notes"]


def test_gauge_couplings_are_scheme_conditional_not_production_ready() -> None:
    payload = load("artifacts/BHSM_gauge_fixing_production_coupling_scheme_v0_7.json")
    assert payload["target_gauge_group"] == "SU(3)c x SU(2)L x U(1)Y"
    assert payload["canonical_vector_kinetic_terms"] is True
    assert payload["gauge_fixing_status"] == "OPEN_OR_TARGET_CONVENTION_ONLY"
    assert payload["production_coupling_status"] == "SCHEME_CONDITIONAL"
    couplings = {entry["parameter"]: entry for entry in payload["candidate_couplings"]}
    for parameter in ["g1_BH_candidate", "g2_BH_candidate", "g3_BH_candidate"]:
        assert parameter in couplings
        assert couplings[parameter]["status"] == "SCHEME_CONDITIONAL"
        assert couplings[parameter]["production_ready"] is False
        assert "reference scale" in couplings[parameter]["requires"]
        assert "renormalization scheme" in couplings[parameter]["requires"]
    assert payload["feynrules_ready"] is False
    assert payload["ufo_ready"] is False


def test_mass_width_scheme_has_no_fake_pdg_masses_or_widths() -> None:
    payload = load("artifacts/BHSM_mass_width_scheme_candidate_v0_7.json")
    assert payload["mass_scheme_status"] == "STRUCTURAL_CANDIDATE"
    assert payload["width_scheme_status"] == "BLOCKED_BY_MISSING_THEOREM"
    assert payload["scalar_profile_mass_status"]["value_exact"] == "64*pi^5"
    assert "not automatically a collider Higgs mass" in payload["scalar_profile_mass_status"]["notes"]
    assert payload["contains_pdg_masses"] is False
    assert payload["contains_fake_widths"] is False
    assert payload["feynrules_ready"] is False
    assert payload["ufo_ready"] is False
    serialized = json.dumps(payload).lower()
    for phrase in ["pdg mass value", "decay width value", "higgs width value"]:
        assert phrase not in serialized


def test_renormalization_scheme_does_not_invent_beta_functions_or_thresholds() -> None:
    payload = load("artifacts/BHSM_renormalization_scheme_candidate_v0_7.json")
    assert payload["reference_scale_status"] == "OPEN"
    assert payload["gauge_coupling_running_status"] == "SCHEME_CONDITIONAL"
    assert payload["yukawa_running_status"] == "OPEN"
    assert payload["threshold_scheme_status"] == "OPEN"
    assert payload["counterterm_scheme_status"] == "OPEN"
    assert payload["beta_functions_implemented"] is False
    assert payload["invented_thresholds"] is False
    assert "production renormalization scheme remains open" in payload["common_scale_transport_status"]
    assert payload["feynrules_ready"] is False
    assert payload["ufo_ready"] is False


def test_phase_three_e_gate_status_keeps_all_production_readiness_false() -> None:
    payload = load("artifacts/BHSM_phase_three_e_gate_status_v0_7.json")
    assert payload["vector_normalization_exported"] is True
    assert payload["fermion_normalization_exported"] is True
    assert payload["Z_A_status"] == "STANDARD_HEP_TARGET_CONVENTION_NOT_BHSM_DERIVED"
    assert payload["Z_psi_status"] == "STANDARD_HEP_TARGET_CONVENTION_NOT_BHSM_DERIVED"
    assert payload["gauge_fixing_scheme_exported"] is True
    assert payload["production_coupling_scheme_exported"] is True
    assert payload["mass_width_scheme_candidate_exported"] is True
    assert payload["renormalization_scheme_candidate_exported"] is True
    for key in [
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
    assert "complete 4D Lagrangian" in payload["remaining_blockers"]
    assert "production vertex table remain open" in payload["recommended_status_language"]


def test_phase_three_e_tools_export_to_temporary_outputs(tmp_path: Path) -> None:
    commands = [
        ("tools/export_vector_normalization_theorem_v0_7.py", "--output", str(tmp_path / "vector.json")),
        ("tools/export_fermion_normalization_theorem_v0_7.py", "--output", str(tmp_path / "fermion.json")),
        ("tools/export_gauge_fixing_production_coupling_scheme_v0_7.py", "--output", str(tmp_path / "gauge.json")),
        ("tools/export_mass_width_scheme_candidate_v0_7.py", "--output", str(tmp_path / "mass.json")),
        ("tools/export_renormalization_scheme_candidate_v0_7.py", "--output", str(tmp_path / "renorm.json")),
        ("tools/check_phase_three_e_gate_status.py", "--output", str(tmp_path / "status.json")),
    ]
    for command in commands:
        result = run_tool(*command)
        assert result.returncode == 0, result.stderr

    assert json.loads((tmp_path / "vector.json").read_text(encoding="utf-8"))["is_BHSM_derived"] is False
    assert json.loads((tmp_path / "fermion.json").read_text(encoding="utf-8"))["Z_psi_status"] == "STANDARD_HEP_TARGET_CONVENTION"
    assert json.loads((tmp_path / "gauge.json").read_text(encoding="utf-8"))["production_coupling_status"] == "SCHEME_CONDITIONAL"
    assert json.loads((tmp_path / "mass.json").read_text(encoding="utf-8"))["contains_fake_widths"] is False
    assert json.loads((tmp_path / "renorm.json").read_text(encoding="utf-8"))["beta_functions_implemented"] is False
    assert json.loads((tmp_path / "status.json").read_text(encoding="utf-8"))["ufo_ready"] is False


def test_no_fake_event_files_or_forbidden_phase_three_e_claims() -> None:
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
            "docs/phase_three_e_normalization_gauge_scheme.md",
            "docs/vector_normalization_theorem.md",
            "docs/fermion_normalization_theorem.md",
            "docs/gauge_fixing_and_production_coupling_scheme.md",
            "docs/mass_width_scheme_candidate.md",
            "docs/renormalization_scheme_candidate.md",
            "docs/phase_three_e_gate_status.md",
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

