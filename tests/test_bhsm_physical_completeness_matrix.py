from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/materialize_bhsm_physical_completeness_matrix.py"
ARTIFACT = ROOT / "artifacts/BHSM_PHYSICAL_COMPLETENESS_MATRIX.json"


def _module():
    spec = importlib.util.spec_from_file_location("bhsm_physical_matrix", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_matrix_tracks_all_required_physical_sectors_without_promotion() -> None:
    module = _module()
    payload = module.build_payload()
    assert payload["validation_passed"] is True
    assert payload["FULL_BHSM_COMPLETE"] is False
    assert payload["Gate7_authority"]["status"] == "ACTIVE_NOT_CLOSED"
    assert tuple(record["id"] for record in payload["records"]) == module.REQUIRED_RECORD_IDS
    assert all(record["prediction_classification"] == "OPEN_INTERNAL_BLOCKER" for record in payload["records"])
    assert not any(record["physical_prediction_materialized"] for record in payload["records"])
    assert payload["current_status"] == (
        "GATE7_INTERVAL_PROMOTION_OPEN__"
        "UNIVERSAL_ACTION_TO_OBSERVABLE_INFRASTRUCTURE_IMPLEMENTED_GATED"
    )


def test_local_kernel_and_universal_apis_are_not_history_predictions() -> None:
    payload = _module().build_payload()
    records = {record["id"]: record for record in payload["records"]}
    expansion = records["UNIVERSAL_ACTION_EXPANSION"]
    assert expansion["implementation_status"] == "IMPLEMENTED_GATED"
    assert expansion["implementation_detail"] == "VALIDATED_LOCAL_KERNEL_GATED"
    assert "history and seam action assembly" in expansion["dependencies_open"]
    magnetic = records["LEPTON_MAGNETIC_MOMENTS"]
    assert magnetic["implementation_status"] == "IMPLEMENTED_GATED"
    assert magnetic["prediction_classification"] == "OPEN_INTERNAL_BLOCKER"
    assert "complete renormalized electromagnetic vertex" in magnetic["dependencies_open"]
    assert "q-squared to zero enclosure" in magnetic["dependencies_open"]
    scale = records["UNIVERSAL_GF_SCALE_MAP"]
    assert scale["physical_prediction_materialized"] is False
    assert "action-derived frozen c_F" in scale["dependencies_open"]


def test_every_row_has_explicit_evidence_and_promotion_fields() -> None:
    payload = _module().build_payload()
    required = {
        "evidence", "dependencies_open", "promotion_gate", "action_owned",
        "empirical_input_used", "last_verified_commit",
    }
    for record in payload["records"]:
        assert required <= record.keys()
        assert record["evidence"]
        assert all(item["sha256"] for item in record["evidence"])
        assert record["last_verified_commit"] == _module().ENGINE_VERIFIED_COMMIT
        assert record["empirical_input_used"] is False


def test_materialized_artifact_matches_deterministic_builder_and_hashes() -> None:
    module = _module()
    expected = module.build_payload()
    stored = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert stored == expected
    for relative, digest in stored["source_sha256"].items():
        assert module._sha256(ROOT / relative) == digest
