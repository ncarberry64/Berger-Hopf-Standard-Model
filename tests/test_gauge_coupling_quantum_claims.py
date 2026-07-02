import json
from pathlib import Path

from bhsm.interface.gauge_coupling_quantum import build_gauge_coupling_quantum_report


ROOT = Path(__file__).resolve().parents[1]


def test_claim_boundaries_and_rejections_are_preserved():
    report = build_gauge_coupling_quantum_report()
    assert len(report["required_statements"]) == 7
    assert "REJECTED_BRIDGE_ARITHMETIC_AS_GAUGE_COUPLING" in report["retired_or_rejected_claims"]
    assert report["empirical_inputs_used"] is False
    assert report["ckm"]["ckm_exponent_status"] == "not_derived"


def test_v31_artifacts_are_guarded_and_parseable():
    artifacts = tuple((ROOT / "artifacts").glob("BHSM_*_v3_1.json"))
    assert len(artifacts) >= 10
    for path in artifacts:
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["empirical_inputs_used"] is False
        assert payload["frozen_predictions_modified"] is False
        assert payload["official_prediction_logic_modified"] is False
