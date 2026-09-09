from fractions import Fraction as F
import numpy as np
import pytest
from bhsm.interface.physical_hessian_frozen_pullback import pullback_with_frozen_output


def exact(a):return np.array([F(float(v)) for v in a.flat],dtype=object).reshape(a.shape)


def test_output_coordinate_and_physical_ball_cross_terms_contain_exact_target():
    l=np.array([[3.,-5.]])
    q=np.array([[[2.,-1.],[-1.,4.]],[[1.,2.],[2.,-3.]]])
    r=np.full(q.shape,1/32);x=np.array([[1.,-2.],[3.,1.]])
    center,report=pullback_with_frozen_output(l,q,r,x,1/8,1/8)
    rng=np.random.default_rng(119)
    for _ in range(20):
        dq=rng.choice([-1.,1.],size=q.shape)*r
        dq=(dq+dq.transpose(0,2,1))/2
        dx=rng.choice([-1.,1.],size=x.shape)/16
        dl=rng.choice([-1.,1.],size=l.shape)/16
        le,qe,xe=exact(l+dl),exact(q+dq),exact(x+dx)
        target=sum((le[0,k]*(xe.T@qe[k]@xe) for k in range(2)),np.zeros((2,2),dtype=object))
        difference=target-exact(center[0])
        assert sum(v*v for v in difference.flat)<=F(report['correction_enclosure_frobenius_radius_upper'])**2
    assert report['output_physical_coordinate_cross_error_frobenius_upper']>0
    assert report['all_node_physical_hessian_enclosed'] is False


@pytest.mark.parametrize('bad',[-1.,float('inf'),float('nan')])
def test_invalid_output_error_fails(bad):
    with pytest.raises(ValueError):
        pullback_with_frozen_output(np.ones((1,1)),np.zeros((1,1,1)),np.zeros((1,1,1)),np.ones((1,1)),0.,bad)
