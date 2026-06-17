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


def test_finite_width_moment_condition_not_derived():
    mod = load_mod()
    data = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    assert mod.finite_width_moment_non_degeneracy_condition_defined() is True
    assert mod.finite_width_moment_non_degeneracy_derived() is False
    assert data["finite_width_moment_non_degeneracy_condition_defined"] is True
    assert data["finite_width_moment_non_degeneracy_derived"] is False

