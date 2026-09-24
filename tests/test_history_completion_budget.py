from fractions import Fraction
import pytest
from bhsm.interface.history_completion_budget import completion_budget


def test_exact_homogeneous_scaling_and_remaining_allowances():
    result = completion_budget([1, 2], [[.25, .5], [.5, .25]],
                               [8, 4], [.125, .25], [.0625, .125])
    left, right = result['rows']
    # L: linear=4, quadratic=8+4=12; derivative=(4+24)/8.
    assert Fraction(left['known_self_map_part_upper']['exact']) == 17
    assert Fraction(left['known_derivative_row_upper']['exact']) == Fraction(7, 2)
    assert Fraction(left['remaining_self_map_allowance']['exact']) == -9
    assert Fraction(right['known_partial_quadratic_upper']['exact']) == 24


def test_positive_allowance_does_not_certify_missing_remainder():
    result = completion_budget([.1, .1], [[.1, 0], [0, .1]], [1, 1], [0, 0], [0, 0])
    assert all(row['remaining_self_map_allowance']['lower'] > 0 for row in result['rows'])
    assert all(row['certified_full_lhs_upper'] is None for row in result['inequalities'])
    assert all(row['mathematical_status'] == 'UNDECIDED' for row in result['inequalities'])
    assert not result['Gate7_closed']


def test_binary64_brackets_enclose_exact_rational_budget():
    result = completion_budget([.1, .2], [[.02, .03], [.04, .05]],
                               [.8, .3], [.01, .015], [.005, .008])
    for row in result['rows']:
        for value in row.values():
            if isinstance(value, dict):
                exact = Fraction(value['exact'])
                assert Fraction.from_float(value['lower']) <= exact <= Fraction.from_float(value['upper'])


@pytest.mark.parametrize('radius', ([0, 1], [-1, 1], [float('nan'), 1]))
def test_invalid_radius_rejected(radius):
    with pytest.raises(ValueError):
        completion_budget([0, 0], [[0, 0], [0, 0]], radius, [0, 0], [0, 0])
