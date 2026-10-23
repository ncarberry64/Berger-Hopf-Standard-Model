import numpy as np
from bhsm.interface.muon_birth_area_endpoint_response import projected_parameter_cotangent


def test_implicit_area_parameter_cotangent_includes_saddle_lift_motion():
    K=np.array([[2.,.4,1.],[.4,1.3,-.2],[1.,-.2,0.]])
    dK=np.array([[.3,-.1,0.],[-.1,.2,0.],[0.,0.,0.]])
    rhs=np.array([[0.],[0.],[1.]])
    theta=np.array([.7,-.6]);dt=np.array([-.2,.4]);X=np.linalg.solve(K,rhs)
    actual=projected_parameter_cotangent(K,X,theta,dt,dK,2,np.ones((1,1)))
    h=1e-5
    value=lambda g:(np.linalg.solve(K+g*dK,rhs)[:2].T@(theta+g*dt))[0]
    np.testing.assert_allclose(actual,(value(h)-value(-h))/(2*h),atol=2e-11,rtol=2e-10)
    assert abs(actual[0]-(X[:2].T@dt)[0])>.01
