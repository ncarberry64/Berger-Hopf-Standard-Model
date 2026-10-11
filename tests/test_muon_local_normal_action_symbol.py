import numpy as np
from bhsm.interface.muon_local_normal_action_symbol import chronological_frequency_polynomial,frozen_normal_frequency_jet


def test_frequency_polynomial_equals_literal_complex_quadratic_action():
    rng=np.random.default_rng(61011);H=rng.normal(size=(7,7));H=(H+H.T)/2
    x=rng.normal(size=2)+1j*rng.normal(size=2);y=rng.normal(size=3)+1j*rng.normal(size=3);w=.37
    p=chronological_frequency_polynomial(H,2);u=np.r_[x,y];full=np.r_[x,1j*w*x,y]
    np.testing.assert_allclose(u.conj()@(p['constant']+1j*w*p['imaginary_linear']+w*w*p['quadratic'])@u,
                               full.conj()@H@full,rtol=2e-15,atol=3e-15)


def test_low_frequency_inertia_uses_static_internal_response_not_kinetic_schur():
    # L=.5*v^T M v-.5*x^T K x+.5*y^2, x=(internal,normal).
    M=np.array([[3.,.7],[.7,2.]]);K=np.array([[4.,1.2],[1.2,5.]])
    H=np.zeros((5,5));H[:2,:2]=-K;H[2:4,2:4]=M;H[4,4]=1
    a=frozen_normal_frequency_jet(H,np.array([0.,1.]),np.zeros((0,3)),lapse=.8)
    phi=np.array([-K[0,1]/K[0,0],1.])
    np.testing.assert_allclose(a['coordinate_restoring_density'],phi@K@phi,rtol=1e-15)
    np.testing.assert_allclose(a['coordinate_low_frequency_inertia'],phi@M@phi,rtol=1e-15)
    assert abs(a['coordinate_low_frequency_inertia']-(M[1,1]-M[0,1]**2/M[0,0]))>.01
    np.testing.assert_allclose(a['proper_low_frequency_inertia'],.8*(phi@M@phi),rtol=1e-15)
    np.testing.assert_allclose(a['proper_restoring_density'],(phi@K@phi)/.8,rtol=1e-15)
    for w in (1e-3,5e-4):
        exact=w*w*M-K;phi_w=np.array([-exact[0,1]/exact[0,0],1.]);value=phi_w@exact@phi_w
        approx=(a['response_taylor_coefficients']*np.array([1,w,w*w])).sum().real
        assert abs(exact[0]@phi_w)<1e-15
        assert abs(value-approx)<w**4


def test_named_frame_reaction_is_not_dropped_from_original_action_rows():
    H=np.zeros((5,5));H[:2,:2]=[[2.,.3],[.3,1.]];H[2:4,2:4]=np.eye(2);H[4,4]=1
    a=frozen_normal_frequency_jet(H,np.array([0.,1.]),np.array([[1.,0.,0.]]),lapse=1.)
    assert abs(a['frame_reaction_coefficients'][0,0])>.2
    np.testing.assert_allclose(a['original_action_row_residual'][0,0],.3,rtol=1e-15)
    assert np.max(abs(a['bordered_row_residual']))<1e-15
