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


def test_no_numerical_or_mixing_claims():
    mod = load_mod()
    data = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    assert mod.numerical_yukawa_values_derived() is False
    assert mod.ckm_values_derived() is False
    assert mod.pmns_values_derived() is False
    assert mod.replacement_claim_ready() is False
    assert data["numerical_yukawa_values_derived"] is False
    assert data["ckm_values_derived"] is False
    assert data["pmns_values_derived"] is False


def test_no_empirical_prediction_imports():
    source = MOD_PATH.read_text(encoding="utf-8")
    forbidden_imports = (
        "prediction_ledger",
        "residual_audit",
        "ckm.py",
        "pmns.py",
        "mass_scheme",
        "common_scale_quark",
    )
    for name in forbidden_imports:
        assert name not in source
