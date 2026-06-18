import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MOD_PATH = ROOT / "theory" / "candidate_theorem_discharge_generic_finite_width_feature_rank.py"
RESULTS_PATH = ROOT / "theory" / "theorem_discharge_generic_finite_width_feature_rank_results.json"

def load_mod():
    spec = importlib.util.spec_from_file_location("generic_rank", MOD_PATH)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod

def load_results():
    return json.loads(RESULTS_PATH.read_text(encoding="utf-8"))

def test_feature_labels_exist_for_all_modes():
    mod = load_mod()
    labels = mod.all_feature_labels()
    assert len(labels) == 12
    assert all(len(v) > 0 for v in labels.values())
