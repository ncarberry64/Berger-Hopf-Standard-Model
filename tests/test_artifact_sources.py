import json
from pathlib import Path

from bhsm.interface.artifact_sources import discover_bhsm_artifacts

ROOT = Path(__file__).resolve().parents[1]


def test_artifact_source_index_builds_offline_and_is_deterministic():
    first = discover_bhsm_artifacts(ROOT).to_dict()
    second = discover_bhsm_artifacts(ROOT).to_dict()
    assert first == second
    assert first["offline"] is True
    assert first["internet_required"] is False
    assert first["artifact_count"] > 0
    assert first["missing_expected_artifacts"] == []
    assert all(row["source_status"] in {"DISCOVERED", "MISSING", "PARSE_FAILED", "UNSUPPORTED_FORMAT", "CLAIM_BOUNDARY_ONLY", "REFERENCE_ONLY"} for row in first["sources"])


def test_generated_source_index_exists_and_parses():
    payload = json.loads((ROOT / "artifacts/BHSM_artifact_source_index_v0_3.json").read_text(encoding="utf-8"))
    assert payload["index_name"] == "BHSM Artifact Source Index"
    assert payload["version"] == "0.3"
    assert payload["artifact_count"] > 0
