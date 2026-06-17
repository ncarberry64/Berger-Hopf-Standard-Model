import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS_PATH = ROOT / "theory" / "theorem_discharge_explicit_symbolic_gram_minor_results.json"


def test_official_unchanged():
    data = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    assert data["official_predictions_changed"] is False
    assert "OFFICIAL_PREDICTIONS_UNCHANGED" in data["verdict_labels"]
