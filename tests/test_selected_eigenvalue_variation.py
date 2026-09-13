import itertools
import numpy as np
import pytest
from flint import arb, ctx
from bhsm.interface.selected_eigenvalue_variation import eigenvalue_slopes


def third_action(state, legs, maps):
    # S(q,u,v)=q*(u*u-v*v)/2+u*v, so H_reduced=[[q,1],[1,-q]].
    assert len(legs) == 3
    result = np.full(np.broadcast_shapes(*(leg.shape[1:] for leg in legs)), arb(0))
    for coordinate, sign in ((1, 1), (2, -1)):
        for indices in set(itertools.permutations((0, coordinate, coordinate))):
            result += sign*legs[0][indices[0]]*legs[1][indices[1]]*legs[2][indices[2]]
    return result


def test_varying_symmetric_eigenvalue_has_nonzero_slope_despite_zero_auxiliary_border():
    previous = ctx.prec
    ctx.prec = 256
    try:
        # At q=3/4, lambda=5/4 and psi=(2,1)/sqrt(5).
        # Exact lambda(q)=sqrt(1+q*q) gives derivative 3/5.
        psi = np.array([arb(2), arb(1)])/arb(5).sqrt()
        directions = np.array([[1, -2, 0], [0, 0, 1], [0, 0, 0]])
        slopes = eigenvalue_slopes(third_action, [arb(3)/4, 0, 0], psi, directions, None)
        for actual, expected in zip(slopes, (arb(3)/5, -arb(6)/5, arb(0)), strict=True):
            assert actual.contains(expected)
        assert not slopes[0].contains(0)
    finally:
        ctx.prec = previous


def test_missing_raw_state_coordinate_is_rejected():
    with pytest.raises(ValueError):
        eigenvalue_slopes(third_action, [0, 0, 0], [1, 0], [[1], [0]], None)
