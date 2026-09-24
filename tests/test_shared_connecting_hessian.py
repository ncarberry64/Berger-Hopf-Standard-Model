"""Connecting-domain identities independent of BHSM physical promotion."""
import pytest
from flint import arb, ctx

from bhsm.interface.shared_action_taylor import TaylorDomain
from bhsm.interface.shared_connecting_hessian import (
    connecting_operands, enclose_difference, integrate_unit_parameter,
)


@pytest.fixture(autouse=True)
def precision():
    old = ctx.prec
    ctx.prec = 256
    yield
    ctx.prec = old


def scalar_operands(*, variation=False):
    return connecting_operands([0], [1], [[arb(1)/4]], [(0, 1, 'interval')],
                               [[1, 0], [3, 1]], [1, 2], [1], 0,
                               variation=variation)


def at(value, parameters):
    return (value.c + sum((a*x for a, x in zip(value.a.entries(), parameters,
                                             strict=True)), arb(0)) + arb(0, value.r))


def test_integrates_only_path_coordinate_and_retains_uniform_tail():
    d = TaylorDomain([(0, 1, 'interval'), (1, 2, 'interval')], 2)
    original = d.affine(2, [4, 3], arb(1)/8)
    result = integrate_unit_parameter(original, 1)
    assert result.c == 2
    assert result.a.entries() == [arb(4), arb(0)]
    assert result.r == arb(1)/8
    assert original.a.entries() == [arb(4), arb(3)]
    with pytest.raises(ValueError):
        integrate_unit_parameter(original, 2)


def test_exact_quartic_difference_is_enclosed_over_entire_star():
    ops = scalar_operands()
    # S(x)=x^4/12 => S''(x)=x^2, S'''(x)=2*x.
    def evaluate(state, legs):
        return 2*state[0]*legs[0][0]*legs[1][0]*legs[2][0], arb(1)
    result = enclose_difference(evaluate, ops)['model']
    for target_coordinate in (-1, 0, 1):
        for reach in (arb(0), arb(1)/2, arb(1)):
            for output, factor in ((0, arb(1)), (1, arb(3)/2)):
                parameters = [arb(0)]*ops['domain'].dimension
                parameters[0] = arb(target_coordinate)
                parameters[ops['reach_parameter']] = 2*reach-1
                parameters[3+output] = arb(1)
                exact = factor*(reach*(1+arb(target_coordinate)/4))**2
                assert at(result, parameters).contains(exact)


def test_preconditioner_cancellation_precedes_absolute_support():
    ops = connecting_operands([0, 0], [1, 2], [[1], [1]],
        [(0, 1, 'interval')], [[1, -1, 0], [2, -2, 0], [0, 0, 1]],
        [1, 1, 1], [1, 1], 0, variation=True)
    # S=(x+y)^3/6 has all third tensor entries equal to 1.
    def evaluate(state, legs):
        value = state[0].domain.affine(1)
        for leg in legs:
            value = value*(leg[0]+leg[1])
        return value, arb(1)
    assert enclose_difference(evaluate, ops)['weighted_output_norm_upper'].is_zero()


def test_all_output_rows_and_weighted_input_box_are_present():
    ops = scalar_operands(variation=True)
    # S=x^3/6 => Hessian difference = x. Last output row scales by 3/2.
    def evaluate(state, legs):
        return legs[0][0]*legs[1][0]*legs[2][0], arb(1)
    result = enclose_difference(evaluate, ops)['model']
    parameters = [arb(0)]*ops['domain'].dimension
    parameters[0] = 1
    parameters[ops['reach_parameter']] = 1
    parameters[4] = 1  # last bordered output coordinate
    parameters[5] = -1  # full weighted physical input
    assert at(result, parameters).contains(-arb(15)/8)
    assert result.support() >= arb(15)/8
    assert ops['input_kind'] == 'WEIGHTED_REDUCED_BOX'


def test_constant_hessian_has_zero_connecting_difference():
    ops = scalar_operands()
    result = enclose_difference(lambda state, legs: (state[0].domain.affine(0), arb(1)), ops)
    assert result['weighted_output_norm_upper'].is_zero()


def test_invalid_or_changed_domains_fail_closed():
    with pytest.raises(ValueError):
        connecting_operands([0], [1], [[1]], [(0, 1, 'interval')],
                            [[1, 0], [0, 1]], [1, 0], [1], 0, variation=True)
    ops = scalar_operands()
    other = TaylorDomain(ops['domain'].groups, ops['domain'].dimension)
    with pytest.raises(ValueError):
        enclose_difference(lambda state, legs: (other.affine(0), arb(1)), ops)


def test_shared_path_is_not_an_endpoint_only_domain():
    ops = scalar_operands()
    assert ops['reach_parameter'] != ops['integration_parameter']
    assert (ops['reach_parameter'], ops['reach_parameter']+1, 'interval') in ops['domain'].groups
    parameters = [arb(0)]*ops['domain'].dimension
    parameters[0] = -1
    parameters[ops['reach_parameter']] = 0  # s=1/2
    parameters[ops['integration_parameter']] = 1  # t=1
    assert at(ops['state'][0], parameters).contains(arb(3)/8)
