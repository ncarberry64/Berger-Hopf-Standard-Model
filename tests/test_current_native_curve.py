from fractions import Fraction as F

import numpy as np
import pytest

from bhsm.interface.current_native_curve import bernstein_range, native_cell


def test_native_alternating_basis_at_shared_parameter_points():
    left = [F(2), F(-3)]
    coefficients = np.arange(1, 15).reshape(7, 2)
    cell = native_cell(left, coefficients, F(9), F(1, 2), F(1, 4), F(3, 4))
    for theta in (F(-1), F(-2, 3), F(0), F(1, 2), F(1)):
        fraction = F(1, 2) + theta / 4
        expected = []
        for j in range(2):
            value = F(0)
            for k, row in enumerate(reversed(coefficients)):
                value = (value + int(row[j])) * (fraction if k % 2 == 0 else 1-fraction)
            expected.append(value + left[j])
        assert cell.jet_value(theta=theta) == tuple(expected)
    assert cell.arc_midpoint == F(37, 4)
    assert cell.arc_radius == F(1, 8)


def test_arc_jets_of_known_cubic_and_linear_coordinates():
    # Three native coefficients give P=left+c0*x+c1*x*(1-x)+c2*x*x*(1-x).
    cell = native_cell([0, 1], [[2, 3], [5, 0], [7, 0]], 0, F(2), F(1, 4), F(3, 4))
    for theta in (F(-1), F(0), F(1)):
        x = F(1, 2) + theta / 4
        assert cell.jet_value(1, theta) == ((7 + 4*x - 21*x*x)/2, F(3, 2))
        assert cell.jet_value(2, theta) == ((4 - 42*x)/4, F(0))
        assert cell.jet_value(3, theta) == (F(-21, 4), F(0))


def test_bernstein_range_retains_interior_values_and_rejects_invalid_cells():
    # 1-theta^2 has an interior maximum absent from its endpoint values.
    lo, hi = bernstein_range((F(1), F(0), F(-1)))
    assert lo <= 0 and hi >= 1
    with pytest.raises(ValueError):
        native_cell([0], [[1]], 0, 0)
    with pytest.raises(ValueError):
        native_cell([0], [[1]], 0, 1, F(1, 2), F(1, 4))
