import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS_PATH = ROOT / "theory" / "theorem_discharge_explicit_symbolic_gram_minor_results.json"
FROZEN_MD = ROOT / "docs" / "frozen_predictions.md"
FROZEN_JSON = ROOT / "docs" / "frozen_predictions.json"


def test_frozen_unchanged_flags_and_files_exist():
    data = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    assert data["frozen_predictions_changed"] is False
    assert "FROZEN_PREDICTIONS_UNCHANGED" in data["verdict_labels"]
    assert FROZEN_MD.exists()
    assert FROZEN_JSON.exists()

