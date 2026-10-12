import numpy as np
from bhsm.interface.muon_chronological_current_matching import (
    current_transfer_chunk,current_test_forms,continued_base_dual_images)


def test_full_saddle_transfer_matches_independent_literal_adjoint():
    rng=np.random.default_rng(147)
    H=rng.normal(size=(12,12))+1j*rng.normal(size=(12,12))+8*np.eye(12)
    # Constrained pairing, with independent directed source columns.
    C=np.array([[1,0,0,1,0,0,0,0,0,0,0,0]],complex)
    K=np.block([[H,C.T],[C,np.zeros((1,1))]])
    R=rng.normal(size=(13,4))+1j*rng.normal(size=(13,4))
    L=rng.normal(size=(13,4))+1j*rng.normal(size=(13,4))
    u=np.linalg.solve(K,R);p=np.linalg.solve(K.T,L)
    pairs=[]
    for ix in (slice(0,5),slice(5,13)):
        pairs.append(current_transfer_chunk(*(x[ix][None] for x in (L,R,u,p))))
    t=sum(q['source_transfer'] for q in pairs)
    z=sum(q['transpose_transfer'] for q in pairs)
    np.testing.assert_allclose(t,L.T@np.linalg.solve(K,R),rtol=2e-13,atol=2e-13)
    np.testing.assert_allclose(t,z,rtol=2e-13,atol=2e-13)
    assert np.linalg.norm(t-L.conj().T@u)>1


def test_independent_complex_continuation_keeps_both_grams_and_base_duals():
    b=np.array([[1,1j],[2,-1j],[1-.2j,.3+.7j]])
    m=np.array([1+.2j,.7-.4j,.2+.1j]);mu=np.array([1,.7,.2])
    H=np.array([np.diag([1+.3j,2]),np.diag([3,4-.2j]),np.diag([2,5])])
    f=current_test_forms(b,m,mu,H)
    t=np.array([.4+.3j,-.7j]);v=np.array([1+.2j,.3-.8j])
    tests=np.kron(t,v)
    np.testing.assert_allclose(tests.conj()@f['Hilbert_test_Gram']@tests,
                              np.sum(mu*abs(b@t)**2)*np.vdot(v,v))
    expected=sum(m[q]*(b[q]@t)**2*(v@H[q]@v) for q in range(3))
    np.testing.assert_allclose(tests@f['analytic_body_form']@tests,expected)
    assert np.linalg.eigvalsh(f['Hilbert_test_Gram']).min()>0
    assert np.linalg.norm(f['Hilbert_test_Gram']-f['analytic_test_Gram'])>.1
    X=np.array([[[1,2j],[3,4]],[[0,1],[2j,0]]],complex)
    a=continued_base_dual_images(H[0],H[0].conj().T,v,X,X.conj().transpose(0,2,1))
    np.testing.assert_allclose(a['reflected_minus_Hilbert_dagger'],0,atol=2e-15)
    assert np.linalg.norm(a['literal_minus_Hilbert_dagger'])>.1
