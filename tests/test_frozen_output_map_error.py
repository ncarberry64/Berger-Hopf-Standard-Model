from fractions import Fraction as F
import numpy as np
import pytest
from flint import ctx
from bhsm.interface.frozen_output_map_error import bound_output_map_errors, bound_output_error_pullback


def _multiply(a,b):
    return [[sum(x*y for x,y in zip(row,col)) for col in zip(*b)] for row in a]


def _exact(a):
    return [[F(float(x)) for x in row] for row in a]


def test_all_three_maps_enclose_exact_rational_formulas():
    r = np.diag([3.,7.])
    t = np.array([[1.,-.25,.5],[.125,1.,-.5]])
    a = np.array([[.5,-.25,.125],[0.,1.,.25],[.5,-.125,-.25]])
    h = .1
    b = -np.linalg.solve(r,t)
    j = b@a
    approximate = np.array([h*b/6+h*h*j/12,h*b/6-h*h*j/12,2*h*b/3])
    result = bound_output_map_errors(r,t,a,h,approximate)
    be = _multiply([[F(-1,3),F(0)],[F(0),F(-1,7)]],_exact(t))
    je = _multiply(be,_exact(a))
    he = F(h)
    targets = [[[he*be[i][k]/6+sign*he*he*je[i][k]/12 for k in range(3)] for i in range(2)]
               for sign in (1,-1)]
    targets.append([[2*he*x/3 for x in row] for row in be])
    for label,target,stored in zip(('left','right','midpoint'),targets,approximate):
        error = [[x-y for x,y in zip(row,s)] for row,s in zip(target,_exact(stored))]
        bound = result['maps'][label]
        assert sum(x*x for row in error for x in row) <= F(bound['frobenius_error_upper'])**2
        assert sum(row[-1]**2 for row in error) <= F(bound['scalar_column_error_upper'])**2
        for vector in ((1,0,0),(0,1,0),(0,0,1),(1,-2,3)):
            image = [sum(x*y for x,y in zip(row,vector)) for row in error]
            assert sum(x*x for x in image) <= F(bound['operator_error_upper'])**2*sum(x*x for x in vector)
    assert result['physical_operand_errors_enclosed'] is False


def test_pullback_includes_all_storage_and_coordinate_cross_terms():
    # Positive scalar case saturates the formula and would expose a missing
    # output*storage, output*coordinate, or three-way cross term.
    e,u,c = F(1,8),F(5,4),F(3,8)
    uu,cu,cc,p,s = F(1,2),F(1,4),F(1,8),F(1,16),F(1,32)
    target = e*(u*u*(uu+p+s)+2*u*c*cu+c*c*cc)
    result = bound_output_error_pullback(float(e),float(e),float(u),float(c),
        [float(uu),float(cu),float(cc)],float(p),float(s))
    assert F(result) >= target
    assert result < float(target)*1.000000000001


def test_scalar_storage_error_uses_its_column_bound():
    result = bound_output_error_pullback(100.,.125,2.,0.,[0.,0.,0.],0.,.25)
    assert .125 <= result < .126


def test_zero_and_subnormal_errors_preserve_precision():
    previous = ctx.prec
    assert bound_output_error_pullback(0.,0.,1.,1.,[1.,1.,1.],1.,1.) == 0
    tiny = np.nextafter(0.,1.)
    assert bound_output_error_pullback(tiny,0.,1.,0.,[1.,0.,0.],0.,0.) >= tiny
    assert ctx.prec == previous


@pytest.mark.parametrize('step',[0.,-1.,np.nan,np.inf,[1.]])
def test_invalid_steps_rejected(step):
    with pytest.raises(ValueError):
        bound_output_map_errors([[1.]],[[1.]],[[1.]],step,np.ones((3,1,1)))


def test_singular_inverse_rejected_and_precision_restored():
    previous = ctx.prec
    with pytest.raises((ValueError,RuntimeError,ZeroDivisionError)):
        bound_output_map_errors([[0.]],[[1.]],[[1.]],1.,np.ones((3,1,1)))
    assert ctx.prec == previous


@pytest.mark.parametrize('q',[[-1.,0.,0.],[np.inf,0.,0.],[np.nan,0.,0.],[1.,2.]])
def test_invalid_tensor_bounds_rejected(q):
    with pytest.raises(ValueError):
        bound_output_error_pullback(1.,1.,1.,1.,q,0.,0.)
