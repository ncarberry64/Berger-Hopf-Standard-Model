import numpy as np
from scipy.linalg import expm
from bhsm.interface.muon_owned_native_product_connection import (
    owned_native_product_blocks,native_product_green_boundary,native_real_action_vertices)
from bhsm.interface.muon_chronological_clifford_graph import chronological_dense_blocks


def test_true_covariant_product_transforms_while_naive_hamiltonian_factor_does_not():
    rng=np.random.default_rng(2514);C=rng.normal(size=(6,6))+1j*rng.normal(size=(6,6))
    Om=(C-C.conj().T)*.08;W=(C+C.conj().T)*.3
    F=rng.normal(size=(6,6))+1j*rng.normal(size=(6,6));F=(F-F.conj().T)*.13
    U=expm(.27*F);Ud=F@U
    u=rng.normal(size=6)+1j*rng.normal(size=6);du=rng.normal(size=6)+1j*rng.normal(size=6)
    Op=U@Om@U.conj().T-Ud@U.conj().T;Wp=U@W@U.conj().T
    Ap=native_product_green_boundary(Wp,Op,value=U@u,proper_derivative=Ud@u+U@du)
    np.testing.assert_allclose(Ap,U@native_product_green_boundary(W,Om,value=u,proper_derivative=du),atol=2e-15)
    naive=Ud@u+U@du+(Wp-1j*Op)@U@u-U@(du+(W-1j*Om)@u)
    np.testing.assert_allclose(naive,(1+1j)*Ud@u,atol=2e-15)
    assert np.linalg.norm(naive)>.1


def test_real_geometric_l2_square_matches_unsquared_map_with_variable_lapse_and_connection():
    rng=np.random.default_rng(642);q=[];expected=np.zeros((18,18),complex)
    for edge in range(3):
        for x in(.211324865405187,.788675134594813):
            C=rng.normal(size=(6,6))+1j*rng.normal(size=(6,6))
            W=(C+C.conj().T)*.11;O=(C-C.conj().T)*.08;N=.7+edge*.1+x*.06
            q.append(dict(H=W+O,Hsharp=W-O,R=1.,Rsharp=1.,rows=((edge,1-x,-1.),(edge+1,x,1.)),
                right_clock=N,reflected_clock=N,measure=N*.5))
            A=np.zeros((6,18),complex)
            for j,p,d in q[-1]['rows']:
                if j:A[:,(j-1)*6:j*6]=d*np.eye(6)/N+p*(W+O)
            expected+=N*.5*A.conj().T@A
    b=owned_native_product_blocks(dict(quadrature=q,temporal_nodes=4),np.zeros((3,1,1)),alpha=np.zeros((3,6,6)))
    K=chronological_dense_blocks(b);M=chronological_dense_blocks(b,prefix='M')
    np.testing.assert_allclose(K,expected,rtol=5e-15,atol=5e-15)
    assert np.linalg.eigvalsh(K)[0]>0 and np.linalg.eigvalsh(M)[0]>0
    assert b['original_quadratic_Hermitian_defect']<2e-15


def test_green_identity_retains_both_oriented_endpoint_conormals():
    # Constant scalar commuting restriction of the complete product identity.
    x,w=np.polynomial.legendre.leggauss(8);t=(x+1)/2;weights=w/2
    W=np.diag(np.arange(1,7)*.1);O=1j*np.diag(np.arange(6)*.03)
    rng=np.random.default_rng(772);a,b,c,d=rng.normal(size=(4,6))+1j*rng.normal(size=(4,6))
    u=a+t[:,None]*b;v=c+t[:,None]*d
    Au=b[:,None]+(W+O)@u.T;Av=d[:,None]+(W+O)@v.T
    # The covariant second derivative keeps the -2 Omega v' term.
    strong=-2*O@d[:,None]+(W-O)@(W+O)@v.T
    lhs=np.einsum('p,ip,ip->',weights,Au.conj(),Av)
    bulk=np.einsum('p,pi,ip->',weights,u.conj(),strong)
    contact=np.vdot(a+b,native_product_green_boundary(W,O,value=c+d,proper_derivative=d))-np.vdot(a,native_product_green_boundary(W,O,value=c,proper_derivative=d))
    np.testing.assert_allclose(lhs,bulk+contact,atol=3e-14)


def test_native_temporal_source_is_the_covariant_connection_not_lorentz_hamiltonian():
    from bhsm.interface.muon_magnetic_open_lepton_vertex import canonical_open_field_vertices
    c=canonical_open_field_vertices(.91,.67);v=native_real_action_vertices(.91,.67)
    np.testing.assert_allclose(v['vertices'][:4],1j*c['gauge'][0])
    np.testing.assert_allclose(v['vertices'][8:20],c['gauge'][2:].reshape(12,18,18))
    np.testing.assert_allclose(v['vertices'][20:],c['scalar'])
    np.testing.assert_allclose(v['vertices_sharp'][:4],-v['vertices'][:4])
    np.testing.assert_allclose(v['vertices_sharp'][8:],v['vertices'][8:],atol=1e-16)
