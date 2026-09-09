from fractions import Fraction as F
import numpy as np
import pytest
from flint import ctx

from bhsm.interface.frozen_causal_map_error import (
    bound_frozen_map_error, transport_map_perturbations,
)


def _fraction_matrix(a):
    return [[F(float(x)) for x in row] for row in a]


def _product(a,b):
    return [[sum(x*y for x,y in zip(row,col)) for col in zip(*b)] for row in a]


def test_map_error_encloses_independent_rational_inverse_and_products():
    right = np.array([[3.,.5],[-.25,2.]])
    test = np.array([[1.,.25,0.],[0.,1.,-.5]])
    left = np.array([[.5,1.],[-.25,.75],[.125,-.5]])
    trial = np.array([[1.,.5],[-.25,1.]])
    approximate = -np.linalg.solve(right,test@left@trial)
    result = bound_frozen_map_error(right,test,left,trial,approximate)
    a,b = _fraction_matrix(right)[0]
    c,d = _fraction_matrix(right)[1]
    determinant = a*d-b*c
    negative_inverse = [[-d/determinant,b/determinant],[c/determinant,-a/determinant]]
    exact = _product(negative_inverse,_product(_product(_fraction_matrix(test),
                           _fraction_matrix(left)),_fraction_matrix(trial)))
    error = [[x-y for x,y in zip(row,stored)]
             for row,stored in zip(exact,_fraction_matrix(approximate))]
    assert sum(x*x for row in error for x in row) <= F(result['map_frobenius_error_upper'])**2
    for vector in ((1,0),(0,1),(1,1),(1,-1),(3,-2)):
        image = [sum(x*y for x,y in zip(row,vector)) for row in error]
        assert sum(x*x for x in image) <= F(result['map_operator_error_upper'])**2*sum(x*x for x in vector)
    assert 0 < result['map_operator_error_upper'] < 1e-14
    assert result['physical_operand_errors_enclosed'] is False


@pytest.mark.parametrize('block',[1,2,10])
def test_relative_and_source_cross_error_bound_against_exact_recurrence(block):
    p = np.array([1.,-.25,.5,1.25,-.125])
    delta = [F(1,128),F(-1,64),F(1,256),F(1,128),F(-1,64)]
    source = [F(1,4),F(-1,8),F(3,16),F(1,2),F(-1,8)]
    ds = [F(1,1024),F(-1,512),F(1,512),F(0),F(-1,256)]
    result = transport_map_perturbations(p[:,None,None],
                                        [float(abs(x)) for x in delta],block)
    z,zstar,gsource = F(0),F(0),F(0)
    stored,error,source_response = [],[],[]
    for pi,dp,f,df in zip(p,delta,source,ds):
        z = F(float(pi))*z+f
        zstar = (F(float(pi))+dp)*zstar+f+df
        gsource = F(float(pi))*gsource+df
        stored.append(abs(z)); error.append(abs(zstar-z)); source_response.append(abs(gsource))
    rhs = (F(result['relative_stored_response_error_multiplier_upper'])*max(stored)
           +F(result['source_error_multiplier_upper'])*max(source_response))
    assert max(error) <= rhs
    assert result['perturbation_gain_upper'] < .1
    assert result['status'] == 'PERTURBATION_GAIN_BELOW_ONE'


def test_zero_initial_state_removes_first_map_error_only():
    p = np.ones((2,1,1))
    result = transport_map_perturbations(p,[1e100,.125])
    assert .125 <= result['perturbation_gain_upper'] < .126
    singleton = transport_map_perturbations(p[:1],[1e100])
    assert singleton['perturbation_gain_upper'] == 0
    assert singleton['source_error_multiplier_upper'] == 1
    assert singleton['relative_stored_response_error_multiplier_upper'] == 0


def test_inconclusive_gain_does_not_claim_instability():
    result = transport_map_perturbations(np.ones((3,1,1)),[0.,1.,1.])
    assert result['status'] == 'GAIN_BOUND_INCONCLUSIVE'
    assert result['source_error_multiplier_upper'] is None
    assert result['Gate7_closed'] is False
    assert result['FULL_BHSM_COMPLETE'] is False


def test_subnormal_map_error_and_precision_restoration():
    previous = ctx.prec
    tiny = np.nextafter(0.,1.)
    result = bound_frozen_map_error([[1.]],[[1.]],[[tiny]],[[1.]],[[0.]])
    assert result['map_operator_error_upper'] >= tiny
    assert ctx.prec == previous
    result = transport_map_perturbations(np.ones((2,1,1)),[0.,tiny])
    assert result['relative_stored_response_error_multiplier_upper'] >= tiny
    assert result['source_error_multiplier_upper'] > 1.
    assert ctx.prec == previous


@pytest.mark.parametrize('right', [[[0.]],[[np.nan]],[[np.inf]],[[1.,2.]]])
def test_invalid_or_singular_map_operands_rejected_and_precision_restored(right):
    previous = ctx.prec
    with pytest.raises((ValueError,RuntimeError,ZeroDivisionError)):
        bound_frozen_map_error(right,[[1.]],[[1.]],[[1.]],[[1.]])
    assert ctx.prec == previous


@pytest.mark.parametrize('bounds', [[-1.,0.],[np.inf,0.],[np.nan,0.],[1.]])
def test_invalid_bounds_are_not_hidden_by_zero_initial_state(bounds):
    with pytest.raises(ValueError):
        transport_map_perturbations(np.ones((2,1,1)),bounds)
