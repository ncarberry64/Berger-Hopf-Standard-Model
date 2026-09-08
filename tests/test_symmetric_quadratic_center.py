from fractions import Fraction as F
import numpy as np
import pytest
import sympy as sp
from flint import ctx

from bhsm.interface.symmetric_quadratic_center import certify_representation, symmetric_center


def test_exact_polarization_and_common_pullback_remove_only_skew():
    a,b,c,d,x,y,u,v = sp.symbols('a b c d x y u v', real=True)
    q=sp.Matrix([[a,b],[c,d]])
    s=(q+q.T)/2
    z=sp.Matrix([x,y]); w=sp.Matrix([u,v])
    assert sp.expand((z.T*(q-s)*z)[0]) == 0
    polarization=((z+w).T*q*(z+w)-z.T*q*z-w.T*q*w)[0]/2
    assert sp.expand(polarization-(z.T*s*w)[0]) == 0
    m=sp.Matrix([[1,2,-1],[3,0,4]])
    assert sp.simplify((m.T*q*m+(m.T*q*m).T)/2-m.T*s*m) == sp.zeros(3)
    # General ordered bilinear data must not be silently replaced by its
    # symmetric part: unlike a quadratic form, it sees the skew component.
    assert sp.expand((z.T*(q-s)*w)[0]) != 0


@pytest.mark.parametrize('seed',range(5))
def test_actual_rounding_bound_contains_exact_rational_error(seed):
    rng=np.random.default_rng(seed)
    q=rng.normal(size=(3,7,7))
    previous=ctx.prec
    s,report=certify_representation(q)
    exact_squared=sum((F(float(s[o,i,j]))-(F(float(q[o,i,j]))+F(float(q[o,j,i])))/2)**2
                      for o in range(3) for i in range(7) for j in range(7))
    assert exact_squared <= F(report['projection_rounding_Frobenius_upper'])**2
    assert np.array_equal(s,s.transpose(0,2,1))
    assert report['physical_Hessian_error_enclosed'] is False
    assert ctx.prec==previous


def test_tiny_stored_skew_is_not_confused_with_projection_rounding():
    q=np.array([[[1.,1.+2**-39],[1.,2.]]])
    s,report=certify_representation(q)
    assert np.linalg.norm(q-q.transpose(0,2,1))/np.linalg.norm(q)>5e-13
    assert report['projection_rounding_Frobenius_upper']==0.
    assert s[0,0,1]==1.+2**-40


def test_maximum_finite_values_do_not_overflow_and_diagonal_is_unchanged():
    big=np.finfo(float).max
    q=np.array([[[big,big],[np.nextafter(big,0.),-big]]])
    s,report=certify_representation(q)
    assert np.all(np.isfinite(s))
    assert s[0,0,0]==big and s[0,1,1]==-big
    assert np.isfinite(report['projection_rounding_Frobenius_upper'])


def test_subnormal_rounding_is_enclosed_not_silently_zeroed():
    tiny=np.nextafter(0.,1.)
    q=np.array([[[tiny,3*tiny],[tiny,-tiny]]])
    s,report=certify_representation(q)
    assert s[0,0,0]==tiny and s[0,1,1]==-tiny
    squared=2*(F(float(s[0,0,1]))-2*F(float(tiny)))**2
    assert squared<=F(report['projection_rounding_Frobenius_upper'])**2


def test_huge_exponent_separation_remains_enclosed():
    q=np.array([[[0.,1e200],[1e-200,0.]]])
    s,report=certify_representation(q)
    squared=2*(F(float(s[0,0,1]))-(F(1e200)+F(1e-200))/2)**2
    assert squared<=F(report['projection_rounding_Frobenius_upper'])**2


@pytest.mark.parametrize('q',[np.ones((2,2)),np.ones((1,2,3)),np.zeros((0,2,2)),
                              np.ones((1,2,2),complex),np.full((1,2,2),np.nan)])
def test_invalid_inputs_fail_closed(q):
    previous=ctx.prec
    with pytest.raises(ValueError): certify_representation(q)
    assert ctx.prec==previous
