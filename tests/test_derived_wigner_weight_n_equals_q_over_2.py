import sys
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_harmonic_highest_weight as hw  # noqa: E402


def test_n_from_q_is_q_over_two():
    assert hw.n_from_q(0) == Fraction(0, 1)
    assert hw.n_from_q(1) == Fraction(1, 2)
    assert hw.n_from_q(3) == Fraction(3, 2)
    assert hw.n_from_q(8) == Fraction(4, 1)


def test_canonical_ledgers_have_expected_n_values():
    ledgers = hw.highest_weight_ledgers()
    assert ledgers["reference_charged"][1].n == Fraction(1, 2)
    assert ledgers["reference_charged"][2].n == Fraction(3, 2)
    assert ledgers["reference_neutral"][1].n == Fraction(3, 2)
    assert ledgers["cyclic_upper"][1].n == Fraction(3, 1)
    assert ledgers["cyclic_upper"][2].n == Fraction(4, 1)
    assert ledgers["cyclic_lower"][1].n == Fraction(0, 1)


def test_wigner_weight_doc_records_conditional_derivation():
    hw.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_wigner_weight_n_equals_q_over_2.md").read_text()
    assert "`n=q/2`" in text
    assert "Q_OVER_2_AS_WIGNER_WEIGHT_DERIVED_CONDITIONAL" in text
