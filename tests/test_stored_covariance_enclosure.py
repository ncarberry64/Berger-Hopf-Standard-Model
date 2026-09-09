from fractions import Fraction as F
import numpy as np
import pytest
from flint import arb,arb_mat,ctx
from bhsm.interface.stored_covariance_enclosure import (
    product_radius_about_stored,interval_matrix,projected_covariance_upper,
)
from bhsm.interface.current_green_midpoint_coordinate_error import _float_upper


def test_product_encloses_exact_rational_oracle_about_different_midpoint():
    a=np.array([[.1,-.3,2.],[.125,1.,-.25]])
    b=np.array([[.7,.25],[.25,-.125],[.125,1.]])
    stored=a@b
    stored[0,0]=np.nextafter(stored[0,0],np.inf)
    radius=product_radius_about_stored(a,b,stored)
    for i in range(2):
        for j in range(2):
            exact=sum(F(float(a[i,k]))*F(float(b[k,j])) for k in range(3))
            assert abs(exact-F(float(stored[i,j])))<=F(float(radius[i,j]))


def test_underflow_product_is_not_lost():
    tiny=np.nextafter(0.,1.)
    radius=product_radius_about_stored([[tiny]],[[.5]],[[0.]])
    assert F(float(radius[0,0]))>=F(tiny)/2


def test_nonunit_axis_projection_uses_exact_projector_formula():
    previous=ctx.prec
    ctx.prec=512
    try:
        # A deliberately nonunit axis makes trace-l2 invalid for T=I-ee.T.
        factors=arb_mat([[1,2],[3,4]])
        g=arb_mat([[1,arb(1)/4],[arb(-1)/2,1]])
        e=arb_mat([[arb(3)/2],[arb(1)/4]])
        c=factors*factors.transpose()
        axis_squared=(e.transpose()*e)[0,0]
        l,t=projected_covariance_upper(c,g.transpose()*g,g.transpose()*e,axis_squared)
        mapped=g*factors
        projected=(arb_mat([[1,0],[0,1]])-e*e.transpose())*mapped
        actual_l=e.transpose()*mapped
        l2=sum(actual_l[0,j]**2 for j in range(2))
        t2=sum(projected[i,j]**2 for i in range(2) for j in range(2))
        assert F(_float_upper(l))**2>=F(float(l2))
        assert F(_float_upper(t))**2>=F(float(t2))
    finally:
        ctx.prec=previous


@pytest.mark.parametrize('radius',[[[-1.]],[[np.nan]],[[np.inf]],[[1.,2.]]])
def test_invalid_balls_rejected(radius):
    with pytest.raises(ValueError):interval_matrix([[1.]],radius)


def test_precision_restored_after_product_error():
    previous=ctx.prec
    with pytest.raises(ValueError):product_radius_about_stored([[1.,2.]],[[1.]],[[1.]])
    product_radius_about_stored([[1.]],[[1.]],[[1.]])
    assert ctx.prec==previous
