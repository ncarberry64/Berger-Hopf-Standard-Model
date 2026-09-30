"""Check native second derivatives by independent alternating-basis jet rules."""
from fractions import Fraction
from pathlib import Path
import sys

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from certify_n12_current_stop_curve_derivative_pilot import native_curve_jet


def native_second_dual(left, coefficients, x):
    value, first, second = Fraction(0), Fraction(0), Fraction(0)
    for index, coefficient in enumerate(reversed(coefficients)):
        value += Fraction.from_float(float(coefficient))
        factor, slope = (x, Fraction(1)) if index % 2 == 0 else (1 - x, Fraction(-1))
        second = second * factor + 2 * first * slope
        first = first * factor + value * slope
        value *= factor
    return value + Fraction.from_float(float(left)), first, second


def test_exact_second_jet_all_native_basis_terms_and_width_squared():
    left = np.arange(7, dtype=float) / 16
    coefficients = np.eye(7)
    width = Fraction(3, 8)
    for x in (Fraction(0), Fraction(1, 7), Fraction(1, 2), Fraction(1)):
        actual = native_curve_jet(left, coefficients, x, width)
        for coordinate in range(7):
            expected = native_second_dual(left[coordinate], coefficients[:, coordinate], x)
            for order in range(3):
                assert actual[order][coordinate] == expected[order] / width ** order


def test_zero_second_derivative_remains_zero_for_native_linear_curve():
    coefficients = np.zeros((7, 2))
    coefficients[0] = [2, -3]
    values, first, second = native_curve_jet([1, 4], coefficients, Fraction(3, 5), Fraction(1, 4))
    assert values == [Fraction(11, 5), Fraction(11, 5)]
    assert first == [Fraction(8), Fraction(-12)]
    assert second == [Fraction(0), Fraction(0)]
    with pytest.raises(ValueError, match="positive"):
        native_curve_jet([1, 4], coefficients, Fraction(0), Fraction(0))
