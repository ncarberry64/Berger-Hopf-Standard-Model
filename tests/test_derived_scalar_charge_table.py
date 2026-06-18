import sys
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_higgs_scalar as hs  # noqa: E402


def test_scalar_charge_table_exact():
    rows = {c.name: c for c in hs.scalar_doublet_components()}
    assert rows["H_plus"].sigma == 1
    assert rows["H_plus"].T3 == Fraction(1, 2)
    assert rows["H_plus"].Y == Fraction(1)
    assert rows["H_plus"].Q == Fraction(1)
    assert rows["H_zero"].sigma == -1
    assert rows["H_zero"].T3 == Fraction(-1, 2)
    assert rows["H_zero"].Y == Fraction(1)
    assert rows["H_zero"].Q == Fraction(0)


def test_scalar_charge_table_documentation():
    hs.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_scalar_charge_table.md").read_text()
    assert "| H_plus | +1 | 1/2 | 1 | 1 |" in text
    assert "| H_zero | -1 | -1/2 | 1 | 0 |" in text
    assert "SCALAR_CHARGE_TABLE_DERIVED_CONDITIONAL" in text
