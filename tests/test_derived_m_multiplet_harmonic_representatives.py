import sys
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_m_multiplet_harmonic_features as mm  # noqa: E402


def test_harmonic_representatives_exist_for_every_m_weight():
    for labels in mm.multiplet_ledgers().values():
        for label in labels:
            reps = mm.multiplet_representatives(label)
            assert len(reps) == len(label.m_values)
            assert all(rep.startswith("D^(") for rep in reps)


def test_harmonic_representative_formats_fractional_weights():
    label = mm.multiplet_ledgers()["reference_charged"][1]
    assert label.ell == Fraction(5, 2)
    assert label.n == Fraction(1, 2)
    assert "D^(5/2)_(-5/2,1/2)" in mm.multiplet_representatives(label)
