import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MOD_PATH = ROOT / "theory" / "candidate_theorem_discharge_y0_coordinate_constraint.py"
RESULTS_PATH = ROOT / "theory" / "theorem_discharge_y0_coordinate_constraint_results.json"

def load_mod():
    spec = importlib.util.spec_from_file_location("y0coord", MOD_PATH)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod

def load_results():
    return json.loads(RESULTS_PATH.read_text(encoding="utf-8"))

def test_frozen_predictions_unchanged_flag():
    data = load_results()
    assert data["frozen_predictions_changed"] is False
    assert "FROZEN_PREDICTIONS_UNCHANGED" in data["verdict_labels"]
