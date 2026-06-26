import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PHASE_THREE_F_STATUS = (
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


def test_phase_three_f_artifacts_exist_and_parse() -> None:
    for relative in [
        "artifacts/BHSM_canonical_production_basis_theorem_v0_8.json",
        "artifacts/BHSM_runtime_parameter_modes_v0_8.json",
        "artifacts/BHSM_production_coupling_map_v0_8.json",
        "artifacts/BHSM_mass_width_runtime_policy_v0_8.json",
        "artifacts/BHSM_phase_three_f_gate_status_v0_8.json",
    ]:
        payload = load(relative)
        assert isinstance(payload, dict), relative
        assert_guardrails(payload)


def test_phase_three_f_docs_and_readme_preserve_status() -> None:
    for relative in [
        "docs/phase_three_f_production_basis_runtime_params.md",
        "docs/canonical_production_basis_theorem.md",
        "docs/runtime_parameter_modes.md",
        "docs/production_coupling_map.md",
        "docs/mass_width_runtime_policy.md",
        "docs/phase_three_f_gate_status.md",
    ]:
        assert (ROOT / relative).exists(), relative

    readme = " ".join(read("README.md").split())
    assert PHASE_THREE_F_STATUS in readme
    assert "Phase Three-F production-basis and runtime-parameter status" in read("README.md")
    assert "This does not constitute production FeynRules, UFO, MadGraph" in read("README.md")


def test_canonical_production_basis_clears_interface_normalization_only() -> None:
    basis = load("artifacts/BHSM_canonical_production_basis_theorem_v0_8.json")
    gate = load("artifacts/BHSM_phase_three_f_gate_status_v0_8.json")
    assert basis["production_basis_defined"] is True
    assert basis["Z_A_prod"] == 1
    assert basis["Z_psi_prod"] == 1
    assert basis["Z_A_prod_status"] == "CANONICAL_PRODUCTION_BASIS_DEFINED"
    assert basis["Z_psi_prod_status"] == "CANONICAL_PRODUCTION_BASIS_DEFINED"
    assert basis["is_Z_A_prod_BHSM_dynamical_prediction"] is False
    assert basis["is_Z_psi_prod_BHSM_dynamical_prediction"] is False
    assert "not empirical fits" in basis["notes"]
    assert gate["interface_normalization_gate_cleared"] is True
    assert gate["complete_4d_lagrangian_exported"] is False
    assert gate["feynrules_ready"] is False
    assert gate["ufo_ready"] is False


def test_runtime_parameter_modes_separate_derivation_from_comparison() -> None:
    payload = load("artifacts/BHSM_runtime_parameter_modes_v0_8.json")
    modes = {entry["mode_name"]: entry for entry in payload["modes"]}
    pure = modes["BHSM_PURE_NOFIT"]
    collider = modes["BHSM_COLLIDER_INTERFACE"]

    assert pure["empirical_runtime_inputs_allowed"] is False
    assert pure["empirical_derivation_inputs_used"] is False
    assert pure["can_generate_physical_events"] is False
    assert pure["can_be_used_for_derivation"] is True
    assert pure["boundary_predictions_modified_by_runtime_inputs"] is False

    assert collider["empirical_runtime_inputs_allowed"] is True
    assert collider["empirical_derivation_inputs_used"] is False
    assert collider["can_be_used_for_derivation"] is False
    assert "true_only_when_runtime_parameter_card" in collider["can_be_used_for_detector_comparison"]
    assert collider["boundary_predictions_modified_by_runtime_inputs"] is False
    assert "must never be used to derive or retune" in payload["policy_statement"]


def test_production_coupling_map_preserves_blocked_vertices() -> None:
    payload = load("artifacts/BHSM_production_coupling_map_v0_8.json")
    assert payload["universal_canonical_basis_rule"] == "G_prod = G_raw / product_a sqrt(Z_a)"
    assert payload["canonical_production_basis_reduction"] == "Z_a = 1 for production fields; therefore G_prod = G_raw"
    entries = {entry["coupling_family_id"]: entry for entry in payload["entries"]}
    for family in [
        "q_charged_current_CKM_BH",
        "lepton_charged_current_PMNS_BH",
        "charged_boundary_response_matrix",
        "neutral_operator_kernel_BH",
        "cp_holonomy_phase_attachment",
    ]:
        assert family in entries
        assert entries[family]["feynrules_ready"] is False
        assert entries[family]["ufo_ready"] is False

    assert entries["q_charged_current_CKM_BH"]["canonical_basis_rule"] == "APPLICABLE"
    assert entries["q_charged_current_CKM_BH"]["lorentz_attachment_status"] == "STANDARD_HEP_TARGET_CONVENTION"
    assert entries["q_charged_current_CKM_BH"]["scheme_status"] == "SCHEME_CONDITIONAL"
    assert entries["q_charged_current_CKM_BH"]["mass_width_status"] == "OPEN"
    assert entries["q_charged_current_CKM_BH"]["renormalization_status"] == "OPEN"

    assert entries["charged_boundary_response_matrix"]["canonical_basis_rule"] == "FORMALLY_APPLICABLE"
    assert "X_ch is missing" in entries["charged_boundary_response_matrix"]["notes"]
    assert entries["neutral_operator_kernel_BH"]["canonical_basis_rule"] == "FORMALLY_APPLICABLE"
    assert "neutrino basis" in entries["neutral_operator_kernel_BH"]["notes"]
    assert entries["cp_holonomy_phase_attachment"]["canonical_basis_rule"] == "FORMALLY_APPLICABLE"
    assert "interaction attachment is missing" in entries["cp_holonomy_phase_attachment"]["notes"]


def test_mass_width_runtime_policy_contains_no_fake_numbers() -> None:
    payload = load("artifacts/BHSM_mass_width_runtime_policy_v0_8.json")
    assert "kappa_H = 64*pi^5" in payload["kappa_H_policy"]
    assert "not automatically a collider Higgs mass" in payload["kappa_H_policy"]
    assert payload["pure_no_fit_mass_width_status"] == "OPEN_NO_EXTERNAL_RUNTIME_INPUTS"
    assert payload["collider_interface_mass_width_status"] == "RUNTIME_INPUTS_ALLOWED_FOR_COMPARISON_ONLY"
    assert payload["contains_fake_masses"] is False
    assert payload["contains_fake_widths"] is False
    assert "No PDG values are inserted" in payload["pdg_target_policy"]
    assert "not derivation inputs" in payload["event_generation_policy"]
    serialized = json.dumps(payload).lower()
    for phrase in ["pdg mass value", "decay width value", "higgs width value"]:
        assert phrase not in serialized


def test_phase_three_f_gate_status_keeps_production_stack_blocked() -> None:
    payload = load("artifacts/BHSM_phase_three_f_gate_status_v0_8.json")
    assert payload["canonical_production_basis_defined"] is True
    assert payload["Z_A_prod_status"] == "CANONICAL_PRODUCTION_BASIS_DEFINED"
    assert payload["Z_psi_prod_status"] == "CANONICAL_PRODUCTION_BASIS_DEFINED"
    assert payload["Z_A_prod_is_BHSM_dynamical_prediction"] is False
    assert payload["Z_psi_prod_is_BHSM_dynamical_prediction"] is False
    assert payload["runtime_parameter_modes_exported"] is True
    assert payload["production_coupling_map_exported"] is True
    assert payload["mass_width_runtime_policy_exported"] is True
    assert payload["interface_normalization_gate_cleared"] is True
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
    assert "mass-width closure for BHSM_PURE_NOFIT" in payload["remaining_blockers"]


def test_phase_three_f_tools_export_to_temporary_outputs(tmp_path: Path) -> None:
    commands = [
        ("tools/export_canonical_production_basis_theorem_v0_8.py", "--output", str(tmp_path / "basis.json")),
        ("tools/export_runtime_parameter_modes_v0_8.py", "--output", str(tmp_path / "modes.json")),
        ("tools/export_production_coupling_map_v0_8.py", "--output", str(tmp_path / "couplings.json")),
        ("tools/export_mass_width_runtime_policy_v0_8.py", "--output", str(tmp_path / "policy.json")),
        ("tools/check_phase_three_f_gate_status.py", "--output", str(tmp_path / "status.json")),
    ]
    for command in commands:
        result = run_tool(*command)
        assert result.returncode == 0, result.stderr

    assert json.loads((tmp_path / "basis.json").read_text(encoding="utf-8"))["Z_A_prod"] == 1
    assert len(json.loads((tmp_path / "modes.json").read_text(encoding="utf-8"))["modes"]) == 2
    assert json.loads((tmp_path / "couplings.json").read_text(encoding="utf-8"))["entries"][0]["feynrules_ready"] is False
    assert json.loads((tmp_path / "policy.json").read_text(encoding="utf-8"))["contains_fake_masses"] is False
    assert json.loads((tmp_path / "status.json").read_text(encoding="utf-8"))["interface_normalization_gate_cleared"] is True


def test_no_fake_event_files_or_forbidden_phase_three_f_claims() -> None:
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
            "docs/phase_three_f_production_basis_runtime_params.md",
            "docs/canonical_production_basis_theorem.md",
            "docs/runtime_parameter_modes.md",
            "docs/production_coupling_map.md",
            "docs/mass_width_runtime_policy.md",
            "docs/phase_three_f_gate_status.md",
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

