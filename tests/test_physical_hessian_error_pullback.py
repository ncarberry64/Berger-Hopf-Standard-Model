from fractions import Fraction as F
import numpy as np
import pytest
from bhsm.interface.physical_hessian_error_pullback import pullback_hessian_error


def exact_pullback(l,q,x):
    l,q,x=[np.array([F(float(v)) for v in a.flat],dtype=object).reshape(a.shape)
           for a in (l,q,x)]
    return sum((l[0,k]*(x.T@q[k]@x) for k in range(q.shape[0])),
               np.zeros((x.shape[1],x.shape[1]),dtype=object))


def test_signed_center_and_radius_contain_exact_perturbed_quadratic_map():
    l=np.array([[3.,-5.]])
    q=np.array([[[2.,-1.],[-1.,4.]],[[1.,2.],[2.,-3.]]])
    r=np.full(q.shape,1/32); x=np.array([[1.,-2.],[3.,1.]])
    delta=1/8
    center,report=pullback_hessian_error(l,q,r,x,delta)
    bound=F(report['correction_enclosure_frobenius_radius_upper'])**2
    rng=np.random.default_rng(511)
    for _ in range(25):
        perturbation=rng.choice([-1.,1.],size=q.shape)*r
        # Symmetrization is an exact contraction for the Frobenius norm.
        perturbation=(perturbation+perturbation.transpose(0,2,1))/2
        dx=rng.choice([-1.,1.],size=x.shape)*(delta/2)
        actual=exact_pullback(l,q+perturbation,x+dx)
        difference=actual-np.array([F(float(v)) for v in center[0].flat],dtype=object).reshape(2,2)
        assert sum(v*v for v in difference.flat)<=bound
    assert report['all_node_physical_hessian_enclosed'] is False


def test_tiny_input_radius_is_not_discarded():
    _,report=pullback_hessian_error(np.array([[1e200]]),np.zeros((1,1,1)),
                                   np.array([[[1e-310]]]),np.ones((1,1)))
    assert F(report['propagated_entrywise_radius_frobenius_upper'])>=F(1e200)*F(1e-310)


@pytest.mark.parametrize('bad',[float('nan'),float('inf'),-1.])
def test_invalid_coordinate_bound_fails(bad):
    with pytest.raises(ValueError):
        pullback_hessian_error(np.ones((1,1)),np.zeros((1,1,1)),
                               np.zeros((1,1,1)),np.ones((1,1)),bad)


def test_negative_radius_fails():
    with pytest.raises(ValueError):
        pullback_hessian_error(np.ones((1,1)),np.zeros((1,1,1)),
                               -np.ones((1,1,1)),np.ones((1,1)))
