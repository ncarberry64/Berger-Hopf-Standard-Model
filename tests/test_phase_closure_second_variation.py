from fractions import Fraction
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_boundary_second_variation import (  # noqa: E402
    phase_exact_value_near_closure,
    phase_hessian_coefficient,
    phase_quadratic_coefficient,
)


def test_phase_hessian_coefficients():
    assert phase_hessian_coefficient(1) == Fraction(2, 1)
    assert phase_hessian_coefficient(2) == Fraction(8, 1)
    assert phase_hessian_coefficient(3) == Fraction(18, 1)
    assert phase_quadratic_coefficient(3) == Fraction(9, 1)


def test_phase_exact_value_agrees_with_leading_quadratic_term():
    epsilon = 1e-5
    for d in [1, 2, 3]:
        exact = phase_exact_value_near_closure(d, epsilon)
        leading = float(phase_quadratic_coefficient(d)) * epsilon * epsilon
        assert exact == pytest.approx(leading, rel=1e-8)


def test_phase_hessian_rejects_invalid_dimension():
    with pytest.raises(ValueError):
        phase_hessian_coefficient(0)

