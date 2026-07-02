import json
from pathlib import Path

from bhsm.interface.weak_gauge_action_source import build_weak_gauge_action_source_report


ROOT = Path(__file__).resolve().parents[1]


def test_required_claim_boundary_and_input_guards():
    report = build_weak_gauge_action_source_report()
    assert len(report["required_statements"]) == 7
    assert report["ckm_blocker"]["ckm_exponent_status"] == "not_derived"
    assert report["empirical_inputs_used"] is False


def test_v3_artifacts_have_no_forbidden_inputs():
    artifacts = tuple((ROOT / "artifacts").glob("BHSM_*_v3_0.json"))
    assert len(artifacts) >= 9
    for path in artifacts:
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["empirical_inputs_used"] is False
        assert payload["frozen_predictions_modified"] is False
        assert payload["official_prediction_logic_modified"] is False
