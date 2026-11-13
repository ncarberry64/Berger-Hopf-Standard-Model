import numpy as np
from bhsm.interface.muon_dirichlet_source_green_collocation import (
    gauss_collocation_table,dirichlet_source_current_collocation,
)


def test_gauss_table_and_high_degree_original_action_source_current():
    s=8;table=gauss_collocation_table(s);c,b,A=(table[n]for n in('c','b','A'))
    for k in range(s):np.testing.assert_allclose(A@(c**k),c**(k+1)/(k+1),rtol=1e-9,atol=1e-10)
    for k in range(2*s):np.testing.assert_allclose(b@(c**k),1/(k+1),rtol=1e-13,atol=1e-14)
    T=.7;N=1.3;power=6;S0=np.array([[[1+2j,3-1j]]]);L0=np.array([[[2-1j,-1+3j]]])
    def point(t):return dict(N=N,B=np.zeros((1,1)),S=t**power*S0,L=t**power*L0)
    r=dirichlet_source_current_collocation(point,length=T,stages=s)
    # f=N/(k+1)*(t^(k+1)-t*T^k), with both Dirichlet faces.
    scalar=-N*N*T**(2*power+2)/(power+1)*(1/(2*power+2)-1/(power+2))
    expected=scalar*np.einsum('ida,dja->ij',L0,S0)
    np.testing.assert_allclose(r['signed_source_current'],expected,rtol=3e-10,atol=1e-12)
    assert r['endpoint_relative_residual']<1e-14


def test_nonnormal_changing_action_refinement_and_literal_left_pairing():
    B=np.array([[.2,.8j],[.1,-.3]],complex);S=np.array([[[1.,2.j]],[[3.j,-1.]]])
    L=np.array([[[1.,-2.],[-1.j,2.j]]]);T=.6
    def point(t):return dict(N=1+.2*t,B=B*(1+t),S=(.2+abs(t-T/2))*S,L=(1+t)*L)
    a=dirichlet_source_current_collocation(point,length=T,stages=4)
    b=dirichlet_source_current_collocation(point,length=T,stages=6)
    c=dirichlet_source_current_collocation(point,length=T,stages=8)
    coarse=np.linalg.norm(a['signed_source_current']-c['signed_source_current'])
    fine=np.linalg.norm(b['signed_source_current']-c['signed_source_current'])
    assert coarse>1e-13 and fine<coarse/100
    assert max(r['stage_relative_residual']for r in(a,b,c))<1e-14
