from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_text(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def read_json(relative: str) -> dict:
    return json.loads(read_text(relative))


def test_v1_1_0_release_files_exist_and_parse() -> None:
    docs = [
        "docs/hep_review_quickstart.md",
        "docs/institutional_hep_handoff_index.md",
        "docs/bhsm_v1_1_0_release_scope.md",
        "docs/bhsm_v1_1_0_claim_status.md",
        "docs/bhsm_v1_1_0_runtime_validation_status.md",
        "docs/bhsm_v1_1_0_forbidden_claims.md",
        "docs/bhsm_v1_1_0_release_checklist.md",
        "RELEASE_NOTES_v1.1.0.md",
    ]
    artifacts = [
        "artifacts/BHSM_v1_1_0_hep_handoff_release_manifest.json",
        "artifacts/BHSM_v1_1_0_hep_review_quickstart_index.json",
        "artifacts/BHSM_v1_1_0_phase_three_consolidated_gate_status.json",
        "artifacts/BHSM_v1_1_0_runtime_validation_status.json",
        "artifacts/BHSM_v1_1_0_claim_status.json",
        "artifacts/BHSM_v1_1_0_release_checklist.json",
    ]
    for relative in docs:
        assert (ROOT / relative).exists(), relative
        assert read_text(relative).strip()
    for relative in artifacts:
        assert (ROOT / relative).exists(), relative
        assert read_json(relative)["release_version"] == "v1.1.0"


def test_readme_preserves_v1_0_1_and_adds_v1_1_0_status() -> None:
    readme = read_text("docs/archive/README_status_history_pre_v0_7.md")
    assert "BHSM v1.0.1 status-reconciled release:" in readme
    assert "internal boundary no-fit package complete/exported;" in readme
    assert "external empirical comparison layer separate/open." in readme
    assert "## BHSM v1.1.0 HEP handoff status" in readme
    assert "bounded minimal collider-interface handoff layer" in readme
    assert "This is not an officially integrated CERN software package." in readme
    assert "It is not the complete BHSM 4D Lagrangian." in readme
    assert "remain gated until external licensed runtime tools are available" in readme


def test_hep_review_quickstart_has_required_sections_and_status_language() -> None:
    text = read_text("docs/hep_review_quickstart.md")
    required = [
        "Repository Status",
        "What BHSM v1.1.0 Contains",
        "What BHSM v1.1.0 Does Not Contain",
        "Minimal Collider-Interface Subset Scope",
        "Runtime Dependencies",
        "Run Repo Tests",
        "Run Environment Preflight",
        "Map Wolfram/FeynRules",
        "Attempt Live FeynRules Validation",
        "Attempt UFO Export",
        "Attempt MadGraph Smoke Test",
        "What Counts As Success",
        "Claims That Remain Forbidden",
    ]
    for heading in required:
        assert heading in text
    assert (
        "Runtime validation requires external licensed Wolfram/FeynRules tooling"
        in text
    )


def test_claim_status_forbids_runtime_and_institutional_overclaims() -> None:
    claim_status = read_json("artifacts/BHSM_v1_1_0_claim_status.json")
    forbidden = "\n".join(claim_status["forbidden_claims"])
    for phrase in (
        "CERN-ready",
        "Athena-ready",
        "CMSSW-ready",
        "validated UFO model",
        "passed MadGraph validation",
        "validated LHE/HepMC events",
        "complete 4D Lagrangian",
        "empirically validated",
    ):
        assert phrase in forbidden


def test_consolidated_gate_status_preserves_honest_closed_and_open_gates() -> None:
    status = read_json(
        "artifacts/BHSM_v1_1_0_phase_three_consolidated_gate_status.json"
    )
    assert status["internal_boundary_no_fit_package_complete"] is True
    assert status["boundary_no_fit_prediction_package_complete"] is True
    assert status["external_empirical_comparison_layer_status"] == "separate/open"
    assert status["minimal_collider_interface_subset_exported"] is True
    assert status["institutional_hep_handoff_package_ready"] is True
    assert status["official_cern_integration"] is False
    assert status["complete_bhsm_4d_lagrangian"] is False
    assert status["minimal_collider_interface_subset"] is True
    for key in (
        "minimal_feynrules_model_enabled",
        "production_feynrules_file_exported",
        "feynrules_syntax_validated",
        "feynrules_model_load_validated",
        "ufo_export_passed",
        "ufo_loadability_passed",
        "madgraph_smoke_test_passed",
        "lhe_generation_ready",
        "hepmc_generation_ready",
        "athena_ready",
        "cmssw_ready",
    ):
        assert status[key] is False
    assert status["empirical_derivation_inputs_used"] is False
    assert status["boundary_predictions_modified_by_runtime_inputs"] is False
    assert status["boundary_predictions_modified_by_comparison"] is False
    assert status["official_predictions_changed"] is False
    assert status["source_model_files_changed"] is False


def test_runtime_validation_status_keeps_runtime_gates_closed() -> None:
    runtime = read_json("artifacts/BHSM_v1_1_0_runtime_validation_status.json")
    for key in (
        "wolfram_runtime_ready",
        "feynrules_ready",
        "madgraph_ready",
        "live_feynrules_validation_attempted",
        "live_feynrules_validation_passed",
        "minimal_feynrules_model_enabled",
        "ufo_export_attempted",
        "ufo_export_passed",
        "ufo_loadability_passed",
        "madgraph_smoke_attempted",
        "madgraph_smoke_passed",
        "event_generation_ready",
    ):
        assert runtime[key] is False
    assert "Install or map a licensed Wolfram" in runtime["next_required_external_action"]


def test_no_enabled_feynrules_ufo_or_fake_event_outputs() -> None:
    assert not (ROOT / "models/feynrules/BHSM_Minimal_Collider_Interface.fr").exists()
    assert (ROOT / "models/feynrules/BHSM_Minimal_Collider_Interface.fr.disabled").exists()

    ufo_files = [
        path
        for path in (ROOT / "models/ufo").rglob("*")
        if path.is_file() and path.name != ".gitkeep"
    ]
    assert ufo_files == []

    event_files = []
    for suffix in ("*.lhe", "*.hepmc", "*.hepmc3"):
        event_files.extend(ROOT.rglob(suffix))
    assert event_files == []


def test_frozen_prediction_integrity_files_are_unchanged_by_release_artifacts() -> None:
    frozen_md = read_text("docs/frozen_predictions.md")
    frozen_json = read_json("docs/frozen_predictions.json")
    assert "BHSM_BARE_V1" in frozen_md
    assert "BHSM_DRESSED_V1_CANDIDATE" in frozen_md
    assert frozen_json
