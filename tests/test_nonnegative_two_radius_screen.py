from fractions import Fraction
from types import SimpleNamespace

import numpy as np
import pytest

from bhsm.interface import nonnegative_two_radius_screen as screen


ZERO = [0., 0.]
MATRIX_ZERO = [[0., 0.], [0., 0.]]


def test_exact_witness_retains_factor_two_and_strict_boundary():
    args = ([.125, .125], MATRIX_ZERO, ZERO, [.5, .5], ZERO, 1.)
    assert screen.exact_self_map_witness(*args, [.5, .5])["exact_margin"] == ["1/8", "1/8"]
    assert screen.exact_self_map_witness(*args, [.25, .25])["exact_margin"] == ["1/16", "1/16"]
    assert screen.exact_self_map_witness(*args, [1., 1.]) is None


def test_exact_witness_rejects_zero_margin_and_outside_ceiling():
    args = ([.5, .5], MATRIX_ZERO, ZERO, ZERO, ZERO, 1.)
    for r in ([.5, .5], [1.01, 1.], [0., 1.], [float("nan"), 1.], [1.]):
        assert screen.exact_self_map_witness(*args, r) is None


def test_continuous_search_recovers_feasible_region_missed_by_old_grid():
    # Unequal optima avoid the helper's initial midpoint/cap trial radii.
    centers = np.array([.413, .619])
    y = centers / 2 * (1 - 1e-9)
    curvature = 1 / (2 * centers)
    for i, n in enumerate((360, 520)):
        grid = np.geomspace(y[i], 1., n)
        assert not np.any(grid > y[i] + curvature[i]*grid**2)
    args = (y, MATRIX_ZERO, [curvature[0], 0.], ZERO, [0., curvature[1]], 1.)
    assert screen.exact_self_map_witness(*args, [.5, .5]) is None
    assert screen.exact_self_map_witness(*args, [1., 1.]) is None
    result = screen.continuous_two_radius_screen(*args)
    assert result["status"] == "STORED_POLYNOMIAL_SELF_MAP"
    r = [Fraction.from_float(v) for v in result["witness"]["radius"]]
    assert all(v > Fraction.from_float(float(y[i]))
               + Fraction.from_float(float(curvature[i]))*v*v for i, v in enumerate(r))
    assert not result["claim_boundary"]["GATE7_CLOSED"]


def test_cap_obstruction_is_not_a_physical_nonexistence_claim():
    result = screen.continuous_two_radius_screen(
        [.125, .125], [[1., 0.], [0., 1.]], ZERO, ZERO, ZERO, 1.)
    assert result["status"] == "STORED_POLYNOMIAL_CAP_OBSTRUCTION"
    assert result["obstruction"]["iterations"] == 8
    assert not result["claim_boundary"]["root_nonexistence_proved"]


def test_lower_rounding_cannot_cross_an_existing_strict_supersolution():
    args = ([.01, .02], [[.1, .02], [.04, .15]], [.1, .2], [.02, .03], [.2, .1], 1.)
    assert screen.exact_self_map_witness(*args, [.5, .5]) is not None
    assert screen.monotone_ceiling_obstruction(*args) is None


def test_iteration_limit_and_optimizer_failure_remain_unresolved(monkeypatch):
    monkeypatch.setattr(screen, "minimize", lambda *a, **kw: SimpleNamespace(
        x=np.array([float("nan"), float("nan"), 0.]),
        success=False, message="test iteration limit"))
    # This map is obstructed, but one lower iteration does not establish that.
    result = screen.continuous_two_radius_screen(
        [.01, .01], [[2., 0.], [0., 2.]], ZERO, ZERO, ZERO, 1.,
        obstruction_iterations=1)
    assert result["status"] == "UNRESOLVED"


def test_optimizer_success_alone_does_not_certify(monkeypatch):
    monkeypatch.setattr(screen, "minimize", lambda *a, **kw: SimpleNamespace(
        x=np.array([-1., -1., -10.]), success=True, message="not a witness"))
    result = screen.continuous_two_radius_screen(
        [.01, .01], [[2., 0.], [0., 2.]], ZERO, ZERO, ZERO, 1.,
        obstruction_iterations=1)
    assert result["status"] == "UNRESOLVED"


@pytest.mark.parametrize("bad", [-1., float("nan"), float("inf")])
def test_invalid_coefficients_rejected(bad):
    with pytest.raises(ValueError):
        screen.continuous_two_radius_screen([bad, .1], MATRIX_ZERO, ZERO, ZERO, ZERO, 1.)


@pytest.mark.parametrize("bad", [0., -1., float("nan"), float("inf")])
def test_invalid_ceiling_rejected(bad):
    with pytest.raises(ValueError):
        screen.continuous_two_radius_screen([.1, .1], MATRIX_ZERO, ZERO, ZERO, ZERO, bad)


def test_zero_and_subnormal_coefficients():
    assert screen.continuous_two_radius_screen(
        ZERO, MATRIX_ZERO, ZERO, ZERO, ZERO, 1.)["status"] == "STORED_POLYNOMIAL_SELF_MAP"
    tiny = np.nextafter(0., 1.)
    result = screen.continuous_two_radius_screen(
        [tiny, tiny], MATRIX_ZERO, ZERO, ZERO, ZERO, tiny*4)
    assert result["status"] == "STORED_POLYNOMIAL_SELF_MAP"


def test_equal_cap_is_obstructed_for_strict_self_map():
    result = screen.continuous_two_radius_screen(
        [1., .1], MATRIX_ZERO, ZERO, ZERO, ZERO, 1.)
    assert result["status"] == "STORED_POLYNOMIAL_CAP_OBSTRUCTION"


def test_log_ratio_formula_matches_independent_polynomial_evaluation():
    args = (np.array([.02, .03]), np.array([[.1, .2], [.3, .4]]),
            np.array([.2, .3]), np.array([.1, .4]), np.array([.4, .2]), .7)
    x = np.array([-.8, -.3])
    r = .7 * np.exp(x)
    terms = screen._log_terms(*args)
    for i, row in enumerate(terms):
        ratio = sum(np.exp(logc + exponent @ x) for logc, exponent in row)
        y, z, c, m, t, _ = args
        expected = (y[i] + z[i] @ r + c[i]*r[0]**2
                    + 2*m[i]*r[0]*r[1] + t[i]*r[1]**2) / r[i]
        assert ratio == pytest.approx(expected, rel=1e-14)
