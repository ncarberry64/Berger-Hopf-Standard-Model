import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_finite_boundary_gate_reports_no_official_prediction_changes():
    payload = json.loads((ROOT / "theory" / "finite_boundary_algebra_results.json").read_text())
    assert payload["official_predictions_changed"] is False
    assert payload["frozen_predictions_changed"] is False
    assert "OFFICIAL_PREDICTIONS_UNCHANGED" in payload["verdict_labels"]
    assert "FROZEN_PREDICTIONS_UNCHANGED" in payload["verdict_labels"]
