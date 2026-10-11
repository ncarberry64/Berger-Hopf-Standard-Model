import numpy as np
from scipy.linalg import expm
from bhsm.interface.muon_magnetic_full_cutoff_contact import (
    analytic_magnetic_cutoff_partial,cutoff_lag_partial,enclosed_source_return_cutoff_partial)


def test_coincident_lag_has_signed_boundary_value():
    p=np.array([2.]);c=.37
    actual=cutoff_lag_partial(p,p,c)
    np.testing.assert_allclose(actual[0,0],-c*np.exp(-c*p[0])/2,rtol=2e-15)


def test_contact_and_orders_match_independent_whole_matrix_heat_derivative():
    # A 2+2-dimensional genuine noncommuting source image. For E1(P),
    # partial_c E1(cP)=-exp(-cP)/c. Differentiate its represented outer trace
    # independently; do not invoke the production source-Hessian routine.
    A=np.array([[2.,.2],[.2,3.]])
    B=np.array([[4.,.1],[.1,5.]])
    F=np.array([[[.3,.7],[-.2,.5]]]);C=np.array([[[[.6,.1],[.1,.8]]]])
    z2=np.zeros((2,2));zf=np.zeros_like(F);zc=np.zeros_like(C)
    poly=dict(n0_pencil=(A,z2,z2),contact=(C,zc,zc),shells={'image':dict(pencil=(B,z2,z2),first_source=(F,zf,zf))})
    c=.29;result=analytic_magnetic_cutoff_partial(poly,0,c,lag_order=96)
    def independent(x):
        full=np.block([[A+x*x*C[0,0]/2,x*F[0].T],[x*F[0],B]])
        return -np.trace(expm(-c*full)[:2,:2])/c
    # Richardson cancellation controls the independent finite difference.
    def second(h):return (independent(h)+independent(-h)-2*independent(0))/h**2
    estimate=(4*second(.004)-second(.008))/3
    np.testing.assert_allclose(result['available_source_pair'][0,0].real,estimate,rtol=2e-8,atol=2e-9)
    assert result['source_square_contact'][0,0].real>0
    assert result['ordered_two_insertion'][0,0].real<0
    np.testing.assert_array_equal(result['opposite_order_two_insertion'],result['ordered_two_insertion'].T)


def test_differentiated_signed_inverse_keeps_negative_bare_direction():
    B=np.array([[-2.,.1,0],[.1,3.,.2],[0,.2,4.]])
    R=np.diag([.03,.04,.05]);D=np.array([[.4,.02,0],[.02,-.3,.01],[0,.01,.2]])
    a=enclosed_source_return_cutoff_partial(B,R,R,np.zeros((3,3)),D,D,np.zeros((3,3)))
    h=1e-4
    independent=(np.linalg.inv(B+R+h*D)-np.linalg.inv(B+R-h*D))/(2*h)
    np.testing.assert_allclose(a['source_return_cutoff_partial'],independent,rtol=3e-9,atol=1e-12)
    assert a['differentiated_source_equation_residual_upper']<1e-50
