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


def test_quadratic_engine_credits_explicit_brst_quotient_without_promotion() -> None:
    payload = _module().build_payload()
    records = {record["id"]: record for record in payload["records"]}
    quadratic = records["UNIVERSAL_QUADRATIC_SPECTRUM_AND_PROPAGATORS"]
    evidence_paths = {item["path"] for item in quadratic["evidence"]}
    assert "src/bhsm/interface/universal_brst_quotient.py" in evidence_paths
    assert "tests/test_universal_brst_quotient.py" in evidence_paths
    assert "explicit constraint/gauge nullspace quotient" in quadratic["satisfied_dependencies"]
    assert "src/bhsm/interface/universal_momentum_map.py" in evidence_paths
    assert quadratic["prediction_classification"] == "OPEN_INTERNAL_BLOCKER"
    assert quadratic["physical_prediction_materialized"] is False


def test_rg_and_muon_readout_capabilities_remain_prediction_gated() -> None:
    payload = _module().build_payload()
    records = {record["id"]: record for record in payload["records"]}
    rg = records["RENORMALIZATION_AND_LOOP_COMPLETION"]
    rg_paths = {item["path"] for item in rg["evidence"]}
    assert "src/bhsm/interface/universal_rg_flow.py" in rg_paths
    assert "joint same-action full-parameter RG transport" in rg["satisfied_dependencies"]
    magnetic = records["LEPTON_MAGNETIC_MOMENTS"]
    assert "fail-closed renormalized-vertex plus LSZ muon g-2 composition" in magnetic[
        "satisfied_dependencies"
    ]
    assert magnetic["prediction_classification"] == "OPEN_INTERNAL_BLOCKER"
    assert magnetic["physical_prediction_materialized"] is False
    collision = records["COLLISION_AND_SCATTERING_PREDICTION"]
    assert "complete s/t/u assembly without quartic double counting" in collision[
        "satisfied_dependencies"
    ]


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
