import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_boundary_hessian_reports_no_official_prediction_changes():
    payload = json.loads((ROOT / "theory" / "boundary_action_hessian_scaffold_results.json").read_text())
    assert payload["official_predictions_changed"] is False
    assert payload["frozen_predictions_changed"] is False
    assert "OFFICIAL_PREDICTIONS_UNCHANGED" in payload["verdict_labels"]
    assert "FROZEN_PREDICTIONS_UNCHANGED" in payload["verdict_labels"]
