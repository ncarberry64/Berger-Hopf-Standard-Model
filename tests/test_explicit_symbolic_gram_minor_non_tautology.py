import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MOD_PATH = ROOT / "theory" / "candidate_theorem_discharge_explicit_symbolic_gram_minor.py"


def load_mod():
    spec = importlib.util.spec_from_file_location("explicit_minor", MOD_PATH)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_non_tautology_guardrails():
    mod = load_mod()
    guardrails = mod.non_tautology_guardrails()
    assert any("Wigner/Hopf" in item for item in guardrails)
    assert any("not asserted" in item for item in guardrails)
    assert any("CKM" in item for item in guardrails)

