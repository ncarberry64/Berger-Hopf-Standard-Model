from fractions import Fraction
import importlib.util
from pathlib import Path

import numpy as np
import pytest
from flint import ctx

PATH = Path(__file__).resolve().parents[1] / "scripts/certify_n12_gate7_current_green_midpoint_coordinate_solve.py"
spec = importlib.util.spec_from_file_location("midpoint_coordinate_solve", PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_bound_contains_exact_rational_error_for_multiple_columns():
    basis = np.array([[3., 0.], [0., 7.]])
    target = np.array([[1., 2.], [3., 4.]])
    approximate = np.linalg.solve(basis, target)
    previous = ctx.prec
    result = module.certify_solve(basis, target, approximate)
    exact_error = max(sum(abs(Fraction(int(target[i, j]), int(basis[i, i]))
                              - Fraction(float(approximate[i, j])))
                          for j in range(2)) for i in range(2))
    assert 0 < exact_error <= Fraction(result["coordinate_error_infinity_upper"])
    assert result["coordinate_error_infinity_upper"] < 1e-14
    assert ctx.prec == previous


def test_large_inexact_approximation_is_bounded_without_tolerance_rejection():
    result = module.certify_solve(np.diag([1., 2.**-100]), np.ones((2, 1)), np.zeros((2, 1)))
    assert result["coordinate_error_infinity_upper"] >= 2.**100


@pytest.mark.parametrize("basis,target,approximate", [
    (np.ones((2, 2)), np.ones((2, 1)), np.zeros((2, 1))),
    (np.eye(2), np.ones((2, 1)), np.zeros((1, 1))),
    (np.eye(2), np.full((2, 1), np.nan), np.zeros((2, 1))),
    (np.eye(2), np.zeros((2, 0)), np.zeros((2, 0))),
])
def test_invalid_or_singular_solve_is_rejected(basis, target, approximate):
    previous = ctx.prec
    with pytest.raises((ValueError, RuntimeError, ZeroDivisionError)):
        module.certify_solve(basis, target, approximate)
    assert ctx.prec == previous
