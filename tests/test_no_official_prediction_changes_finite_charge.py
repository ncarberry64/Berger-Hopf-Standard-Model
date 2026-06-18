import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_finite_algebra_charge as discharge  # noqa: E402


def test_result_payload_and_export_report_no_official_prediction_change():
    payload = discharge.export_outputs(ROOT)
    parsed = json.loads((ROOT / "theory" / "theorem_discharge_finite_algebra_charge_results.json").read_text())

    assert payload["official_predictions_changed"] is False
    assert payload["frozen_predictions_changed"] is False
    assert parsed["official_predictions_changed"] is False
    assert parsed["frozen_predictions_changed"] is False
    assert "FROZEN_PREDICTIONS_UNCHANGED" in parsed["verdict_labels"]
    assert "OFFICIAL_PREDICTIONS_UNCHANGED" in parsed["verdict_labels"]
