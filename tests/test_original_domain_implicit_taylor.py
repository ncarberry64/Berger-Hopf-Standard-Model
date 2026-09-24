"""Analytic checks of implicit residual transport on an unchanged domain."""
import numpy as np
import pytest
from flint import arb, ctx
from bhsm.interface.componentwise_weighted_response import enclose_response_rows
from bhsm.interface.shared_action_taylor import TaylorDomain


@pytest.fixture(autouse=True)
def precision():
    old=ctx.prec
    ctx.prec=160
    yield
    ctx.prec=old


def test_nonlinear_mean_value_inverse_encloses_original_domain():
    # G(y,t)=y^2-(1+t/5). On t in [-1,1], both the positive
    # root and yhat=1+t/10 lie in the ORIGINAL interval [.89,1.11].
    # R=1/2 and sup|1-R*G_y|=.11 throughout their connecting segment.
    domain=TaylorDomain([(0,1,'interval')],1)
    predictor=domain.affine(1,[arb(1)/10])
    original_box=arb(1,arb(11)/100)
    assert original_box.contains(predictor.enclosure())
    residual=(predictor*predictor-domain.affine(1,[arb(1)/5]))/2
    array=lambda values:np.array([arb(v) for v in values],dtype=object)
    _,proof=enclose_response_rows(array([0]),array([residual.support()]),
                                  array([1]),array([arb(11)/100]))
    error=arb(proof['component_radii_upper_rational'][0])
    assert error<arb('0.00562')
    for t in range(-100,101):
        theta=arb(t)/100
        root=(1+theta/5).sqrt()
        assert original_box.contains(root)
        assert abs(root-(1+theta/10))<error


def test_nonlinear_mean_value_bound_cannot_use_a_point_only_defect():
    # The anchor inverse has zero defect at t=0, but this misses the
    # negative endpoint's true error. The full-domain .11 defect is needed.
    anchor_only_bound=arb(1)/200
    actual_error=abs(arb('0.8').sqrt()-arb('0.9'))
    assert actual_error>anchor_only_bound


def test_shared_endpoint_midpoint_chain_retains_cross_term():
    domain=TaylorDomain([(0,1,'interval')],1)
    a=domain.affine(2,[arb(1)/10])
    m=domain.affine(4,[arb(1)/5])
    h=arb(1)/4
    w=domain.affine(1)/2-h*a/8
    composed=h*a/6+2*h*m*w/3
    # Exact quadratic coefficient from -(h^2/12) M(theta) A(theta).
    cross=-h*h*arb('0.1')*arb('0.2')/12
    assert composed.r>=abs(cross)
    for sign in [-1,0,1]:
        aa=2+arb('0.1')*sign
        mm=4+arb('0.2')*sign
        exact=h*aa/6+2*h*mm*(arb(1)/2-h*aa/8)/3
        assert (composed.c+composed.a[0,0]*sign+arb(0,composed.r)).contains(exact)
