import sys
from fractions import Fraction
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_finite_algebra_charge as discharge  # noqa: E402


def test_boundary_t3_and_hypercharge_exact_rows():
    assert discharge.active_orientation_T3(1, 1) == Fraction(1, 2)
    assert discharge.active_orientation_T3(1, -1) == Fraction(-1, 2)
    assert discharge.active_orientation_T3(0, 1) == Fraction(0)
    assert discharge.active_orientation_T3(0, -1) == Fraction(0)

    assert discharge.boundary_hypercharge(0, 1, 1) == Fraction(-1)
    assert discharge.boundary_hypercharge(0, -1, 1) == Fraction(-1)
    assert discharge.boundary_hypercharge(1, 1, 1) == Fraction(1, 3)
    assert discharge.boundary_hypercharge(1, -1, 1) == Fraction(1, 3)
    assert discharge.boundary_hypercharge(0, 1, 0) == Fraction(0)
    assert discharge.boundary_hypercharge(0, -1, 0) == Fraction(-2)
    assert discharge.boundary_hypercharge(1, 1, 0) == Fraction(4, 3)
    assert discharge.boundary_hypercharge(1, -1, 0) == Fraction(-2, 3)


def test_hypercharge_matches_prior_integer_bridge_without_importing_labels():
    for C in (0, 1):
        for sigma in (-1, 1):
            for w in (0, 1):
                assert discharge.hypercharge_equivalent_to_prior_bridge(C, sigma, w)


def test_boundary_hypercharge_validation_and_documentation():
    with pytest.raises(ValueError):
        discharge.boundary_hypercharge(0, 1, 2)
    discharge.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_boundary_hypercharge_operator.md").read_text(encoding="utf-8")
    assert "T3_boundary = 1/2 P_w S_sigma" in text
    assert "Y_boundary = 2(Q_boundary - T3_boundary)" in text
    assert "| 1 | -1 | 0 | -1/3 | 0 | -2/3 |" in text
    assert "PO_BH_10_CHARGE_HYPERCHARGE_OPERATORS_DERIVED_CONDITIONAL" in text
