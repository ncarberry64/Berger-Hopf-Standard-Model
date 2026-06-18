import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MOD_PATH = ROOT / "theory" / "candidate_theorem_discharge_explicit_symbolic_gram_minor.py"
RESULTS_PATH = ROOT / "theory" / "theorem_discharge_explicit_symbolic_gram_minor_results.json"


def load_mod():
    spec = importlib.util.spec_from_file_location("explicit_minor", MOD_PATH)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_generic_rank_condition_defined_but_not_promoted():
    mod = load_mod()
    data = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    assert mod.generic_rank_three_support_condition_defined() is True
    assert mod.generic_rank_three_support_derived() is False
    assert data["generic_rank_three_support_condition_defined"] is True
    assert data["generic_rank_three_support_derived"] is False
    assert "GENERIC_RANK_THREE_SUPPORT_REMAINS_OPEN" in data["verdict_labels"]

