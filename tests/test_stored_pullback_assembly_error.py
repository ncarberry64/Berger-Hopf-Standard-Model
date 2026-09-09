from fractions import Fraction as F
import numpy as np
import pytest
from flint import ctx
from bhsm.interface.stored_pullback_assembly_error import (
    fast_frobenius_upper, difference_frobenius_upper, addition_rounding_frobenius_upper,
    assemble_pullback_with_error,
)


@pytest.mark.parametrize('values',[
    [0.,0.],[.1,-.3,.7],[1e308,1e308],[1e-300,-2e-300],
    [np.nextafter(0.,1.),np.nextafter(0.,1.)],[1.,np.nextafter(0.,1.)]])
def test_scaled_norm_encloses_exact_rational_squares(values):
    bound = fast_frobenius_upper(values)
    assert F(bound)**2 >= sum(F(v)**2 for v in values)
    if max(abs(v) for v in values)>1e-290:
        expected = np.hypot.reduce(values)
        assert bound <= expected*1.000000000001


@pytest.mark.parametrize('symmetrize',[False,True])
def test_pullback_error_encloses_full_independent_rational_contraction(symmetrize):
    rng = np.random.default_rng(73148)
    l = rng.normal(size=(2,2))
    q = rng.normal(size=(2,3,2))
    x = rng.normal(size=(3,2))
    y = rng.normal(size=(2,2))
    actual,record = assemble_pullback_with_error(l,q,x,y,symmetrize=symmetrize)
    exact = np.empty((2,2,2),dtype=object)
    for c in range(2):
        for i in range(2):
            for j in range(2):
                exact[c,i,j] = sum(F(float(l[c,o]))*F(float(q[o,a,b]))
                    *F(float(x[a,i]))*F(float(y[b,j]))
                    for o in range(2) for a in range(3) for b in range(2))
    if symmetrize:
        exact = (exact+exact.transpose(0,2,1))/2
    difference = [e-F(float(a)) for e,a in zip(exact.flat,actual.flat)]
    assert sum(v*v for v in difference) <= F(record['assembly_error_frobenius_upper'])**2
    assert record['assembly_error_frobenius_upper'] < 1e-10
    assert record['physical_Hessian_error_enclosed'] is False


def test_underflow_in_a_dot_product_is_enclosed():
    tiny = np.nextafter(0.,1.)
    actual,record = assemble_pullback_with_error([[1.]],np.array([[[tiny]]]),[[.5]],[[1.]])
    exact = F(tiny)/2
    assert abs(F(float(actual[0,0,0]))-exact) <= F(record['assembly_error_frobenius_upper'])


def test_difference_and_addition_against_rational_oracles():
    a = np.array([.1,1e100,np.nextafter(0.,1.)])
    b = np.array([.3,-1e100,np.nextafter(0.,1.)])
    difference = [F(float(x))-F(float(y)) for x,y in zip(a,b)]
    assert sum(x*x for x in difference) <= F(difference_frobenius_upper(a,b))**2
    actual = a+b
    error = [F(float(x))+F(float(y))-F(float(z)) for x,y,z in zip(a,b,actual)]
    assert sum(x*x for x in error) <= F(addition_rounding_frobenius_upper(a,b))**2
    assert difference_frobenius_upper(a,a) == 0.


@pytest.mark.parametrize('values',[[],[np.nan],[np.inf],[1+2j]])
def test_invalid_norm_operands_rejected(values):
    with pytest.raises(ValueError):
        fast_frobenius_upper(values)


def test_invalid_shape_and_precision_restoration():
    previous = ctx.prec
    with pytest.raises(ValueError):
        assemble_pullback_with_error([[1.]],np.ones((1,2,2)),[[1.]],[[1.]])
    fast_frobenius_upper([1.,2.])
    assert ctx.prec == previous
