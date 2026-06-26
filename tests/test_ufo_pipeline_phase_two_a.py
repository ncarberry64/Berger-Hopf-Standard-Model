import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PHASE_TWO_A_STATUS = (
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


def test_readme_preserves_phase_two_a_boundaries() -> None:
    text = read("README.md")
    assert PHASE_TWO_A_STATUS in " ".join(text.split())
    assert "Phase Two-A analytical export layer" in text
    assert "This is not yet a production UFO model" in text
    assert "No LHE or HepMC events are generated in this release." in text


def test_required_phase_two_a_docs_exist() -> None:
    for relative in [
        "docs/analytical_export_ledger.md",
        "docs/bhsm_to_ufo_mapping.md",
        "docs/field_content_export_status.md",
        "docs/parameter_card_export_status.md",
        "docs/vertex_source_export_status.md",
        "docs/feynrules_export_blockers.md",
        "docs/ufo_candidate_builder_status.md",
    ]:
        assert (ROOT / relative).exists(), relative

    assert "not a production UFO" in read("docs/analytical_export_ledger.md")
    assert "loadable_ufo_model = false" in read("docs/ufo_candidate_builder_status.md")
    assert "complete_4d_lagrangian_missing" in read("docs/feynrules_export_blockers.md")


def test_required_phase_two_a_artifacts_exist_and_parse() -> None:
    artifacts = [
        "artifacts/BHSM_analytical_export_ledger_v0_2.json",
        "artifacts/BHSM_field_content_export_v0_2.json",
        "artifacts/BHSM_parameter_card_export_v0_2.json",
        "artifacts/BHSM_vertex_source_ledger_v0_2.json",
        "artifacts/BHSM_feynrules_export_blockers_v0_2.json",
        "artifacts/BHSM_ufo_candidate_build_manifest_v0_2.json",
    ]
    for relative in artifacts:
        payload = load(relative)
        assert isinstance(payload, dict), relative
        assert payload["empirical_derivation_inputs_used"] is False
        assert payload["boundary_predictions_modified_by_comparison"] is False
        assert payload["official_predictions_changed"] is False

    ledger = load("artifacts/BHSM_analytical_export_ledger_v0_2.json")
    source_names = {entry["source_artifact"] for entry in ledger["entries"]}
    for expected in [
        "artifacts/profile_scale_closure_values_v1.json",
        "artifacts/tau_sigma_boundary_values_v1.json",
        "artifacts/charged_boundary_bridge_values_v1.json",
        "artifacts/charged_outputs_at_boundary_tau_A_local_v1.json",
        "artifacts/charged_outputs_at_boundary_tau_A_background_identity_v1.json",
        "artifacts/neutral_operator_no_fit_output_v1.json",
        "artifacts/PMNS_no_fit_operator_output_v1.json",
        "artifacts/CKM_no_fit_operator_output_v1.json",
        "artifacts/CP_no_fit_holonomy_output_v1.json",
        "artifacts/common_scale_boundary_transport_v1.json",
        "artifacts/BHSM_boundary_no_fit_prediction_package_v1.json",
        "artifacts/BHSM_COMPLETE_V1_RELEASE_CANDIDATE.json",
    ]:
        assert expected in source_names


def test_field_parameter_and_vertex_exports_are_ledgers_not_ufo_ready() -> None:
    fields = load("artifacts/BHSM_field_content_export_v0_2.json")
    parameters = load("artifacts/BHSM_parameter_card_export_v0_2.json")
    vertices = load("artifacts/BHSM_vertex_source_ledger_v0_2.json")

    assert fields["field_content_complete_for_ufo"] is False
    assert parameters["parameter_card_complete_for_ufo"] is False
    assert vertices["feynman_rules_exported"] is False

    field_ids = {entry["field_entry_id"] for entry in fields["entries"]}
    assert {
        "charged_lepton_sector",
        "up_quark_sector",
        "down_quark_sector",
        "neutral_sector",
        "weak_mixing_sector",
        "ckm_sector",
        "pmns_sector",
        "cp_holonomy_sector",
    }.issubset(field_ids)
    assert all(entry["ufo_ready"] is False for entry in fields["entries"])
    assert all(entry["ufo_ready"] is False for entry in parameters["entries"])
    assert all(entry["ufo_ready"] is False for entry in vertices["entries"])
    assert all(entry["is_fitted_to_empirical_data"] is False for entry in parameters["entries"])
    field_physics_columns = [
        "candidate_field_name",
        "spin",
        "mass_parameter",
        "width_parameter",
        "charge",
        "color_representation",
        "weak_representation",
        "generation",
        "pdg_id",
    ]
    assert any(
        entry[column] is None
        for entry in fields["entries"]
        for column in field_physics_columns
    )
    assert any(
        "complete collider-ready 4D Lagrangian" in " ".join(entry["missing_for_ufo"])
        for entry in fields["entries"]
    )
    assert any(
        "Lorentz structure" in " ".join(entry["missing_for_feynman_rule"])
        or "gauge-fixed interaction term" in " ".join(entry["missing_for_feynman_rule"])
        for entry in vertices["entries"]
    )
    assert any(
        "Feynman rule" in " ".join(entry["missing_for_ufo"])
        for entry in vertices["entries"]
    )


def test_feynrules_blockers_and_ufo_manifest_block_production_export() -> None:
    blockers = load("artifacts/BHSM_feynrules_export_blockers_v0_2.json")
    manifest = load("artifacts/BHSM_ufo_candidate_build_manifest_v0_2.json")

    for key in [
        "complete_4d_lagrangian_missing",
        "gauge_fixed_lagrangian_missing",
        "field_normalization_missing",
        "lorentz_structures_missing",
        "complete_vertex_table_missing",
        "mass_width_scheme_missing",
        "renormalization_scheme_missing",
        "ufo_directory_missing",
        "madgraph_validation_missing",
        "pdg_target_table_missing",
    ]:
        assert blockers["blockers"][key] is True
        assert key in manifest["blockers"]

    assert blockers["feynrules_export_ready"] is False
    assert blockers["ufo_export_ready"] is False
    assert manifest["ufo_candidate_built"] is False
    assert manifest["loadable_ufo_model"] is False
    assert manifest["madgraph_ready"] is False
    assert manifest["lhe_generation_ready"] is False
    assert manifest["hepmc_generation_ready"] is False
    assert manifest["blocked_candidate_directory_created"] is False


def test_phase_two_a_tools_export_consistent_temporary_artifacts(tmp_path: Path) -> None:
    outputs = {
        "field": tmp_path / "field.json",
        "parameters": tmp_path / "parameters.json",
        "vertices": tmp_path / "vertices.json",
        "manifest": tmp_path / "manifest.json",
    }
    commands = [
        ("tools/export_bhsm_field_content.py", "--output", str(outputs["field"])),
        ("tools/export_bhsm_parameter_card.py", "--output", str(outputs["parameters"])),
        ("tools/export_bhsm_vertex_source_ledger.py", "--output", str(outputs["vertices"])),
        ("tools/build_bhsm_ufo_candidate.py", "--output", str(outputs["manifest"])),
    ]
    for command in commands:
        result = run_tool(*command)
        assert result.returncode == 0, result.stderr

    assert json.loads(outputs["field"].read_text(encoding="utf-8"))["field_content_complete_for_ufo"] is False
    assert json.loads(outputs["parameters"].read_text(encoding="utf-8"))["parameter_card_complete_for_ufo"] is False
    assert json.loads(outputs["vertices"].read_text(encoding="utf-8"))["feynman_rules_exported"] is False
    assert json.loads(outputs["manifest"].read_text(encoding="utf-8"))["loadable_ufo_model"] is False

    readiness = run_tool("tools/check_bhsm_ufo_candidate_readiness.py")
    assert readiness.returncode == 0
    readiness_payload = json.loads(readiness.stdout)
    assert readiness_payload["complete_4d_lagrangian_exported"] is False
    assert readiness_payload["feynman_rules_exported"] is False
    assert readiness_payload["ufo_candidate_built"] is False
    assert readiness_payload["loadable_ufo_model"] is False
    assert readiness_payload["madgraph_ready"] is False
    assert readiness_payload["lhe_generation_ready"] is False
    assert readiness_payload["hepmc_generation_ready"] is False
    assert readiness_payload["athena_ready"] is False
    assert readiness_payload["cmssw_ready"] is False


def test_blocked_tarball_packager_is_explicitly_not_for_analysis(tmp_path: Path) -> None:
    output = tmp_path / "BHSM_UFO_CANDIDATE_BLOCKED_NOT_FOR_ANALYSIS_v0_2.tar.gz"
    try:
        result = run_tool("tools/package_bhsm_ufo_candidate_tarball.py", "--output", str(output))
        assert result.returncode == 0, result.stderr
        payload = json.loads(result.stdout)
        assert output.exists()
        assert "BLOCKED_NOT_FOR_ANALYSIS" in output.name
        assert payload["production_ufo_tarball"] is False
        assert payload["not_for_analysis"] is True
        assert payload["loadable_ufo_model"] is False
        assert payload["madgraph_ready"] is False
    finally:
        shutil.rmtree(ROOT / "ufo_candidate_BLOCKED_NOT_FOR_ANALYSIS", ignore_errors=True)


def test_no_production_ufo_or_fake_event_outputs_exist() -> None:
    blocked_dir = ROOT / "ufo_candidate_BLOCKED_NOT_FOR_ANALYSIS"
    assert not blocked_dir.exists()

    forbidden_suffixes = {".lhe", ".hepmc", ".hepmc3"}
    generated_events = [
        path
        for path in ROOT.rglob("*")
        if path.is_file() and path.suffix.lower() in forbidden_suffixes
    ]
    assert generated_events == []

    tarballs = [
        path
        for path in ROOT.rglob("*.tar.gz")
        if "UFO" in path.name.upper() and "BLOCKED_NOT_FOR_ANALYSIS" not in path.name
    ]
    assert tarballs == []


def test_no_positive_readiness_or_validation_claims_in_phase_two_a_surface() -> None:
    combined = "\n".join(
        read(relative)
        for relative in [
            "README.md",
            "docs/analytical_export_ledger.md",
            "docs/bhsm_to_ufo_mapping.md",
            "docs/field_content_export_status.md",
            "docs/parameter_card_export_status.md",
            "docs/vertex_source_export_status.md",
            "docs/feynrules_export_blockers.md",
            "docs/ufo_candidate_builder_status.md",
            "docs/ufo_pipeline.md",
            "docs/feynman_rules_status.md",
            "docs/madgraph_event_generation_path.md",
            "docs/lhe_hepmc_generation_status.md",
        ]
    )
    forbidden_positive_claims = [
        "ufo_candidate_built = true",
        "loadable_ufo_model = true",
        "madgraph_ready = true",
        "lhe_generation_ready = true",
        "hepmc_generation_ready = true",
        "athena_ready = true",
        "cmssw_ready = true",
        "official CERN integration",
        "BHSM is empirically validated",
        "BHSM is empirically proven",
        "production UFO model exported",
        "complete 4D collider-ready Lagrangian exported",
    ]
    lowered = combined.lower()
    for phrase in forbidden_positive_claims:
        assert phrase.lower() not in lowered


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
