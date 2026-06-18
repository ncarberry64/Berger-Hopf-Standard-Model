import sys
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_leading_axis_m_weight as la  # noqa: E402


def test_m_equals_q_over_two_for_canonical_ledgers():
    ledgers = la.leading_axis_ledgers()
    assert ledgers["reference_charged"][1].m == Fraction(1, 2)
    assert ledgers["reference_charged"][2].m == Fraction(3, 2)
    assert ledgers["reference_neutral"][1].m == Fraction(3, 2)
    assert ledgers["cyclic_upper"][1].m == Fraction(3, 1)
    assert ledgers["cyclic_upper"][2].m == Fraction(4, 1)
    assert ledgers["cyclic_lower"][1].m == Fraction(0, 1)


def test_m_equals_q_over_two_doc():
    la.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_m_equals_q_over_2_leading_component.md").read_text()
    assert "`m=n=q/2`" in text
    assert "M_EQUALS_Q_OVER_2_STRUCTURALLY_MOTIVATED_NOT_DERIVED" in text
