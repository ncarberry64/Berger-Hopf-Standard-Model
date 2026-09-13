from itertools import product
import pytest
from flint import arb, arb_mat, ctx
from bhsm.interface.directional_variation_split import split_directions, enclose_split_action


def test_split_contains_all_linear_corner_actions():
    ctx.prec = 256
    directions = arb_mat([[arb(3, 1)], [arb(-2, 2)]])
    center, tail = split_directions(directions)
    derivative = arb_mat([[arb(1, 1), -3], [4, arb(2, 1)]])
    enclosed, correction = enclose_split_action(derivative*center, derivative, tail)
    assert all(x.mid().is_zero() for x in tail.entries())
    assert any(not x.rad().is_zero() for x in correction.entries())
    for a, b, x, y in product((0, 2), (1, 3), (2, 4), (-4, 0)):
        exact = arb_mat([[a, -3], [4, b]])*arb_mat([[x], [y]])
        assert all(u.contains(v) for u, v in zip(enclosed.entries(), exact.entries()))


def test_exact_direction_preserves_signed_center_cancellation():
    ctx.prec = 256
    center, tail = split_directions([[1], [1]])
    derivative = arb_mat([[arb('1e20', 1), arb('-1e20', 1)]])
    certified_center_action = arb_mat([[arb(0, '0.001')]])
    enclosed, correction = enclose_split_action(certified_center_action, derivative, tail)
    assert correction[0, 0].is_zero()
    assert enclosed[0, 0].contains(certified_center_action[0, 0])
    assert enclosed[0, 0].rad() < (derivative*center)[0, 0].rad()


def test_rejects_incompatible_tail():
    with pytest.raises(ValueError):
        enclose_split_action([[1]], [[1, 2]], [[1]])
