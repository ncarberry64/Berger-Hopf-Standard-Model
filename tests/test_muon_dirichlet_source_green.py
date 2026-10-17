import numpy as np
from bhsm.interface.muon_dirichlet_source_green import dirichlet_source_current


def test_original_action_derivative_source_green_and_complex_pairing():
    rng=np.random.default_rng(214);d=3;e=2;a=4;T=.7;N=1.2
    right=rng.normal(size=(d,e,a))+1j*rng.normal(size=(d,e,a))
    left=rng.normal(size=(e,d,a))+1j*rng.normal(size=(e,d,a))
    def point(t):return dict(N=N,B=np.zeros((d,d)),S=t*right,L=left)
    r=dirichlet_source_current(point,length=T,steps_per_half=2)
    expected=N*N*T**3/12*np.einsum('ida,dja->ij',left,right)
    np.testing.assert_allclose(r['signed_source_current'],expected,rtol=3e-15,atol=3e-15)
    np.testing.assert_allclose(r['selected_scaled_initial_g'],-T*T/2*right,rtol=3e-15,atol=3e-15)
    assert r['endpoint_relative_residual']<1e-15
    assert np.linalg.norm(r['signed_source_current']-r['signed_source_current'].conj().T)>.1


def test_variable_nonnormal_action_refines_with_both_faces_and_midpoint_contact():
    B=np.array([[.2,.8j],[.1,-.3]],complex);S=np.array([[[1.,2.j]],[[3.j,-1.]]])
    L=np.array([[[1.,-2.],[-1.j,2.j]]]);T=.6
    def point(t):return dict(N=1+.2*t,B=B*(1+t),S=(.2+abs(t-T/2))*S,L=(1+t)*L)
    results=[dirichlet_source_current(point,length=T,steps_per_half=n)for n in(4,8,16)]
    coarse=np.linalg.norm(results[0]['signed_source_current']-results[1]['signed_source_current'])
    fine=np.linalg.norm(results[1]['signed_source_current']-results[2]['signed_source_current'])
    assert coarse>0 and fine<coarse/10
    assert max(r['endpoint_relative_residual']for r in results)<1e-14
    assert all(r['temporal_midpoint_contact_retained']for r in results)
