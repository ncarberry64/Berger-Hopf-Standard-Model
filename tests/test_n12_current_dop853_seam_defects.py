"""Detect polynomial seam sources that ordinary endpoint rounding hides."""
from fractions import Fraction
from pathlib import Path
import sys

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from materialize_n12_current_dop853_seam_defects import endpoint_jumps, norm_upper


def test_sub_ulp_endpoint_jump_is_not_erased():
    values = np.ones((3, 2))
    coefficients = np.zeros((2, 7, 2))
    coefficients[0, 0, 0] = 2.0**-55
    coefficients[0, 1:, :] = 100.0  # The other dense controls vanish at x=1.
    jump = endpoint_jumps(values, coefficients, 1)
    assert values[0, 0]+coefficients[0, 0, 0] == values[1, 0]
    assert jump == [[-Fraction(1, 2**55), Fraction(0)]]


def test_only_seams_before_the_terminal_native_interval_are_sources():
    values = np.array([[0.0], [2.0], [4.0], [6.0]])
    coefficients = np.zeros((3, 7, 1))
    coefficients[:, 0, 0] = 2.0
    assert endpoint_jumps(values, coefficients, 2) == [[Fraction(0)], [Fraction(0)]]


def test_exact_norm_is_outward_and_zero_stays_zero():
    assert norm_upper([Fraction(3), Fraction(4)]) >= 5.0
    assert norm_upper([Fraction(0)]) == 0.0


def test_malformed_dense_order_is_rejected():
    with pytest.raises(ValueError):
        endpoint_jumps(np.ones((2, 1)), np.zeros((1, 6, 1)), 0)
