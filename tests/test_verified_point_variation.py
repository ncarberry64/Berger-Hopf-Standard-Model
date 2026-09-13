import pytest
from flint import arb
from bhsm.interface.verified_point_variation import difference_lower_bounds


def test_disjoint_point_balls_give_necessary_radius():
    # Actual values lie in [1,2] and [5,6], hence differ by at least three.
    difference, lower = difference_lower_bounds([arb('1.5', '.5')], [arb('5.5', '.5')])
    assert difference[0].contains(-5) and difference[0].contains(-3)
    # Outward radius arithmetic may make the certified lower bound smaller.
    assert arb('2.99') < lower[0] <= 3
    assert arb('1.49') < lower[0]/2 <= arb('1.5')


def test_overlapping_balls_do_not_prove_nonzero_variation():
    _, lower = difference_lower_bounds([arb(2, 1)], [arb(3, 1)])
    assert lower[0].is_zero()


def test_point_shapes_must_match():
    with pytest.raises(ValueError):
        difference_lower_bounds([arb(1), arb(2)], [arb(1)])
