"""Verify exact derivative against the independent alternating-basis dual rule."""
from fractions import Fraction
from pathlib import Path
import sys

import numpy as np
from flint import arb

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from materialize_n12_current_stop_endpoint_defects import native_value_derivative, _norm_packet


def _dense_dual(left, coefficients, x):
    value, derivative = Fraction(0), Fraction(0)
    for index, coefficient in enumerate(reversed(coefficients)):
        value += Fraction.from_float(float(coefficient))
        factor, slope = (x, Fraction(1)) if index % 2 == 0 else (1-x, Fraction(-1))
        derivative = derivative * factor + value * slope
        value *= factor
    return value + Fraction.from_float(float(left)), derivative


def test_all_degree_seven_basis_derivatives_and_width_are_exact():
    coefficients = np.eye(7)
    left = np.arange(7, dtype=float) / 8
    width = Fraction(3, 8)
    for x in (Fraction(0), Fraction(1, 7), Fraction(1, 2), Fraction(1)):
        values, derivative = native_value_derivative(left, coefficients, x, width)
        for coordinate in range(7):
            direct_value, direct_derivative = _dense_dual(left[coordinate], coefficients[:, coordinate], x)
            assert values[coordinate] == direct_value
            assert derivative[coordinate] == direct_derivative / width


def test_norm_lower_does_not_square_negative_absolute_endpoint():
    result = _norm_packet([arb(0, "1e-30"), arb(0, "1e-40")])
    assert result["lower"] == 0
    assert result["upper"] >= 1e-30
