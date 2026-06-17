import sys
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_m_multiplet_harmonic_features as mm  # noqa: E402


def test_all_four_generation_ledgers_have_multiplets():
    ledgers = mm.multiplet_ledgers()
    assert set(ledgers) == {"reference_charged", "reference_neutral", "cyclic_upper", "cyclic_lower"}
    assert all(len(labels) == 3 for labels in ledgers.values())


def test_each_multiplet_has_two_ell_plus_one_weights():
    for labels in mm.multiplet_ledgers().values():
        for label in labels:
            assert len(label.m_values) == int(2 * label.ell) + 1


def test_n_and_m_values_are_admissible():
    assert mm.all_multiplets_admissible() is True
    for labels in mm.multiplet_ledgers().values():
        for label in labels:
            assert mm.n_admissible(label) is True
            assert all(mm.m_admissible(label, m) for m in label.m_values)


def test_known_cyclic_upper_light_label():
    label = mm.multiplet_ledgers()["cyclic_upper"][2]
    assert label.k == 10
    assert label.ell == Fraction(5, 1)
    assert label.n == Fraction(4, 1)
    assert label.m_values[0] == Fraction(-5, 1)
    assert label.m_values[-1] == Fraction(5, 1)
