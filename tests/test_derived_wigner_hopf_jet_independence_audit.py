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


def load_results():
    return json.loads(RESULTS_PATH.read_text(encoding="utf-8"))


def test_global_independence_not_local_jet_proof():
    mod = load_mod()
    data = load_results()
    assert mod.global_peter_weyl_independence_supported() is True
    assert mod.local_jet_injectivity_proven() is False
    assert mod.wigner_hopf_jet_independence_derived() is False
    assert data["wigner_hopf_jet_independence_derived"] is False
    assert "WIGNER_HOPF_JET_INDEPENDENCE_REMAINS_OPEN" in data["verdict_labels"]

