from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(path: str) -> dict[str, object]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_consolidated_artifacts_exist_and_parse() -> None:
    paths = (
        "artifacts/BHSM_consolidated_status_v0_7.json",
        "artifacts/BHSM_github_cleanup_manifest_v0_7.json",
        "artifacts/BHSM_clean_claims_index_v0_7.json",
        "artifacts/BHSM_cli_command_index_v0_7.json",
        "artifacts/BHSM_artifact_index_v0_7.json",
    )
    assert all(load(path) for path in paths)


def test_status_artifact_preserves_open_and_runtime_gates() -> None:
    payload = load("artifacts/BHSM_consolidated_status_v0_7.json")
    areas = {row["area"]: row for row in payload["areas"]}

    assert areas["cp_o_int"]["status"] == "CANDIDATE"
    assert areas["cp_o_int"]["secondary_status"] == "OPEN"
    assert "callable symbolic field/action candidate exists" in areas["cp_o_int"]["established"]
    assert areas["x_ch"]["status"] == "OPEN"
    assert areas["neutrino_physical_basis_scale"]["status"] == "OPEN"
    assert areas["external_hep_tools"]["status"] == "RUNTIME_GATED"
    assert payload["internet_required"] is False
    assert payload["external_hep_tools_required"] is False


def test_calibration_comparison_and_claim_policies_are_preserved() -> None:
    payload = load("artifacts/BHSM_consolidated_status_v0_7.json")
    boundaries = payload["claim_boundaries"]
    assert boundaries["w_anchor_is_independent_prediction"] is False
    assert boundaries["electron_neutrino_central_measurement_claimed"] is False
    assert boundaries["empirical_validation_claimed"] is False
    assert boundaries["validated_hep_runtime_claimed"] is False

    manifest = load("artifacts/BHSM_github_cleanup_manifest_v0_7.json")
    assert manifest["source_files_changed"] == []
    assert manifest["production_physics_model_logic_changed"] is False
    assert manifest["frozen_predictions_changed"] is False
    assert manifest["empirical_derivation_inputs_used"] is False
    assert manifest["zenodo_work_performed"] is False


def test_major_artifact_index_points_to_existing_sources() -> None:
    payload = load("artifacts/BHSM_artifact_index_v0_7.json")
    paths = [path for group in payload["groups"] for path in group["artifacts"]]
    assert paths
    assert all((ROOT / path).is_file() for path in paths)

