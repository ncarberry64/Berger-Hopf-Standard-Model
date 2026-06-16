from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_boundary_anomaly_results_report_official_unchanged() -> None:
    payload = json.loads(
        (
            ROOT / "theory" / "boundary_integer_anomaly_closure_results.json"
        ).read_text(encoding="utf-8")
    )
    assert payload["official_predictions_changed"] is False
    assert "OFFICIAL_PREDICTIONS_UNCHANGED" in payload["verdict_labels"]


def test_boundary_anomaly_gate_does_not_touch_official_prediction_files() -> None:
    touched = {
        "theory/candidate_boundary_integer_anomaly.py",
        "theory/boundary_integer_anomaly_closure_gate.md",
        "theory/boundary_integer_anomaly_closure_results.json",
    }
    assert "docs/frozen_predictions.md" not in touched
    assert "docs/frozen_predictions.json" not in touched
    assert "BHSM_BARE_V1" not in touched
    assert "BHSM_DRESSED_V1_CANDIDATE" not in touched
