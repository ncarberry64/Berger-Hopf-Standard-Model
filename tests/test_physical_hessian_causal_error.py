from fractions import Fraction
import numpy as np
import pytest
from bhsm.interface.physical_hessian_causal_error import assemble_local_bounds
from bhsm.interface.current_green_causal_error import transport_local_errors


def test_endpoint_incidence_and_midpoint_factor_on_two_interval_recurrence():
    # Midpoint pair coefficients are already 2 * their tensor norm.
    # z1 = 2+3, z2 = 2*z1 + 4+5+7 = 26 for scalar positive maps.
    value = assemble_local_bounds({0: 2., 1: 4.},
        {1: {(0, 'right'): 3., (1, 'left'): 5.}, 2: {(1, 'right'): 7.}}, intervals=2)
    for actual, exact in zip(value['local_coefficients_upper'], (5, 16), strict=True):
        assert Fraction(actual) >= exact
        assert actual < exact * (1+1e-14)
    result = transport_local_errors(np.array([[[99.]], [[2.]]]),
                                    np.array(value['local_coefficients_upper']), block_size=2)
    assert result['node_error_norm_upper'][0] == 0.
    for actual, exact in zip(result['node_error_norm_upper'][1:], (5, 26), strict=True):
        assert Fraction(actual) >= exact
        assert actual < exact * (1+1e-14)
    assert value['coverage']['complete']


def test_missing_error_is_unknown_and_cannot_make_complete_envelope():
    with pytest.raises(RuntimeError, match='missing errors are unknown'):
        assemble_local_bounds({0: 0.}, {1: {(0, 'right'): 0., (1, 'left'): 0.}}, intervals=2)
    result = assemble_local_bounds({0: 0.}, {}, intervals=2, selected_only=True)
    assert result['coverage']['missing_midpoints'] == [1]
    assert result['coverage']['missing_endpoints'] == [1, 2]
    assert result['missing_errors_assumed_zero'] is False
    assert result['scope'] == 'SELECTED_ADDITIVE_HESSIAN_ERROR_COMPONENT_ONLY'


def test_selected_endpoint_requires_both_incidences():
    with pytest.raises(ValueError, match='both incident slots'):
        assemble_local_bounds({}, {1: {(0, 'right'): 2.}}, intervals=2, selected_only=True)


def test_outward_sum_retains_sub_ulp_term_and_restores_precision():
    from flint import ctx
    previous = ctx.prec
    result = assemble_local_bounds({0: 1.}, {1: {(0, 'right'): 2.**-54}}, intervals=1)
    assert Fraction(result['local_coefficients_upper'][0]) >= 1 + Fraction(1, 2**54)
    assert ctx.prec == previous


@pytest.mark.parametrize('bad', [-1., float('nan'), float('inf'), True])
def test_bad_bounds_rejected(bad):
    with pytest.raises(ValueError, match='finite nonnegative'):
        assemble_local_bounds({0: bad}, {}, intervals=1, selected_only=True)
