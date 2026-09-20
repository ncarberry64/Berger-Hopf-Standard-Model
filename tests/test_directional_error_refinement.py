import pytest
from flint import arb, arb_mat, ctx
from bhsm.interface.directional_error_refinement import intersect_majorant


def test_every_finite_iteration_contains_the_implicit_solution():
    # (1+x/8) eta=x/100, |x|<=1: |eta|<=1/100+|eta|/8.
    with ctx.workprec(256):
        bound = intersect_majorant([arb(1)], [arb(1)/100], arb_mat([[arb(1)/8]]))[0]
        exact_worst = arb(2)/175
        assert bound >= exact_worst
        assert bound < arb('0.01143')


def test_no_contraction_needed_and_initial_inclusion_is_never_enlarged():
    result = intersect_majorant([arb(1), arb(3)], [arb(1), arb(0)],
        arb_mat([[2, 0], [arb(1)/4, 0]]))
    assert result == [arb(1), arb(1)/4]


def test_rounding_uncertainty_is_outward_and_negative_majorants_are_rejected():
    result = intersect_majorant([arb(1)], [arb('0.1', '0.01')], arb_mat([[arb('0.2', '0.01')]]))
    assert result[0] >= arb('0.11')/(1-arb('0.21'))
    with pytest.raises(ValueError, match='nonnegative'):
        intersect_majorant([arb(1)], [arb(-1)], arb_mat([[0]]))
