import sys
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_higgs_scalar as hs  # noqa: E402


def test_conjugate_scalar_charges_exact():
    rows = {c.name: c for c in hs.conjugate_scalar_doublet_components()}
    assert rows["H_tilde_zero"].T3 == Fraction(1, 2)
    assert rows["H_tilde_zero"].Y == Fraction(-1)
    assert rows["H_tilde_zero"].Q == Fraction(0)
    assert rows["H_tilde_minus"].T3 == Fraction(-1, 2)
    assert rows["H_tilde_minus"].Y == Fraction(-1)
    assert rows["H_tilde_minus"].Q == Fraction(-1)


def test_conjugate_scalar_documentation():
    hs.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_scalar_conjugate_doublet.md").read_text()
    assert "H_tilde = i sigma_2 H*" in text
    assert "| H_tilde_zero | +1 | 1/2 | -1 | 0 |" in text
    assert "| H_tilde_minus | -1 | -1/2 | -1 | -1 |" in text
    assert "SCALAR_CONJUGATE_DOUBLET_DERIVED_CONDITIONAL" in text
