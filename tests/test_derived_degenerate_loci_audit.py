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


def test_degenerate_loci_are_reported():
    mod = load_mod()
    loci = mod.degenerate_loci()
    assert any("beta0" in item for item in loci)
    assert any("moment" in item for item in loci)
    assert any("jet" in item for item in loci)

