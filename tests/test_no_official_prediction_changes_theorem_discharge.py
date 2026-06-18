import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_theorem_discharge_reports_no_official_prediction_changes():
    payload = json.loads(
        (ROOT / "theory" / "theorem_discharge_phase_orientation_cyclic_results.json").read_text()
    )
    assert payload["official_predictions_changed"] is False
    assert payload["frozen_predictions_changed"] is False
    assert "OFFICIAL_PREDICTIONS_UNCHANGED" in payload["verdict_labels"]
    assert "FROZEN_PREDICTIONS_UNCHANGED" in payload["verdict_labels"]
