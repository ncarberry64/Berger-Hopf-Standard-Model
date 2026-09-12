"""Exact polynomial fixtures for correlated-domain mean-value enclosures."""
import numpy as np
import pytest
from flint import arb, ctx
from bhsm.interface.affine_longitudinal_hessian import endpoint_tube, enclose_hessian
from bhsm.interface.uniform_eigenpair_proposal import propose
from bhsm.interface.arb_eigenpair_inclusion import verify_eigenpair_box


@pytest.fixture(autouse=True)
def precision():
    previous = ctx.prec
    ctx.prec = 256
    yield
    ctx.prec = previous


def test_split_preserves_nonunit_axis_signed_cancellation_and_descriptor():
    tube = endpoint_tube([4, 6, 7], [[1, -1], [2, 1], [0, 3]], [2, 2],
                         .2, .01, [2, 3])
    assert tube['raw_longitudinal_direction'][0].is_zero()
    assert tube['raw_longitudinal_direction'][1].contains(2)
    assert tube['raw_longitudinal_direction'][2].contains(6)
    # A specific admissible t=(.006,.008), l=.1 has ||t||2=.01.
    t = [arb('.006'), arb('.008')]
    for i, (z, row, weight) in enumerate(zip([4, 6, 7], [[1, -1], [2, 1], [0, 3]], [2, 3, 1])):
        actual = (arb(z)+sum((arb(a)*(arb(2)*arb('.1')+v) for a,v in zip(row,t)),arb(0)))/weight
        assert tube['raw_segment_hull'][i].contains(actual)


def test_large_correlated_translation_does_not_destroy_eigenpair_inclusion():
    # S(x,y)=x^2/2+3*y^2/2+(x-y)^3/6. Along u=(1,1),
    # D3S[.,.,u]=0 exactly. Independent raw x/y boxes lose this cancellation.
    tube = endpoint_tube([0, 0, 0], [[1,0],[0,1],[0,0]], [1,1],
                         100, .001, [1,1])
    x,y = tube['raw_transverse_box'][:2]
    d=x-y
    base=np.array([[1+d,-d],[-d,3+d]],dtype=object)
    u=tube['raw_longitudinal_direction'][:2]
    signed=u[0]-u[1]
    third=np.array([[signed,-signed],[-signed,signed]],dtype=object)
    h=enclose_hessian(base,third,tube['radius_longitudinal'])
    assert max(float(v.rad()) for v in h.flat) < .00201
    p,lam,_,_=propose(h,[1.,0.],selected=0)
    assert verify_eigenpair_box(h,p,lam,precision=256)['validation_passed']
    assert float((tube['raw_segment_hull'][0]-tube['raw_segment_hull'][1]).rad()) > 199


def test_nonzero_third_derivative_covers_both_longitudinal_endpoints():
    # S=x^3/6+3*y^2/2, H=diag(x,3), u=(2,-1).
    base=np.array([[arb(1,'.01'),arb(0)],[arb(0),arb(3)]])
    h=enclose_hessian(base,[[2,0],[0,0]],.2)
    assert h[0,0].contains(arb('.59')) and h[0,0].contains(arb('1.41'))
    assert h[1,1].contains(3)


def test_fixed_endpoint_retains_center_uncertainty_without_displacement():
    tube=endpoint_tube([arb(1,'.001'),2],[[2],[3]],[4],1,2,[1],fixed=True)
    assert tube['radius_longitudinal'].is_zero() and tube['radius_transverse'].is_zero()
    assert tube['raw_segment_hull'][0].contains(arb(1,'.001'))
    assert float(tube['raw_segment_hull'][0].rad()) < .00101


def test_invalid_weights_dimensions_and_nonfinite_derivatives_fail_closed():
    with pytest.raises(ValueError,match='positive'):
        endpoint_tube([0,0],[[1],[1]],[1],1,1,[0])
    with pytest.raises(ValueError,match='matching'):
        enclose_hessian(np.eye(2),np.eye(3),1)
    with pytest.raises(ValueError,match='finite'):
        enclose_hessian([[1]],[[float('inf')]],1)
