import sys
from fractions import Fraction
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_finite_algebra_charge as discharge  # noqa: E402


def test_boundary_charge_operator_exact_rows():
    assert discharge.boundary_charge(0, 1) == Fraction(0)
    assert discharge.boundary_charge(0, -1) == Fraction(-1)
    assert discharge.boundary_charge(1, 1) == Fraction(2, 3)
    assert discharge.boundary_charge(1, -1) == Fraction(-1, 3)
    assert discharge.q_independent_of_w() is True


def test_boundary_charge_operator_validation():
    with pytest.raises(ValueError):
        discharge.boundary_charge(2, 1)
    with pytest.raises(ValueError):
        discharge.boundary_charge(0, 0)


def test_boundary_charge_operator_documentation():
    discharge.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_boundary_charge_operator.md").read_text(encoding="utf-8")
    assert "Q_boundary = 1/2(S_sigma-I) + 2/3 P_C" in text
    assert "| 1 | -1 | -1/3 |" in text
    assert "BOUNDARY_CHARGE_OPERATOR_DERIVED_CONDITIONAL" in text
