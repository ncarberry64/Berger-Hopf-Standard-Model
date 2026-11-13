import numpy as np
from bhsm.interface.muon_holomorphic_magnetic_birth_matching import signed_field_face_reconstruction


def test_reconstruct_face_preserves_original_Gauss_and_canonical_targets_with_known_source():
    rng=np.random.default_rng(816);draw=lambda s:rng.normal(size=s)+.2j*rng.normal(size=s)
    na,nd,ns=2,4,3;n=na+nd;K=draw((n,n));K[:na,:na]+=4*np.eye(na)
    M=np.zeros((n,n),complex);M[na:,na:]=draw((nd,nd))+5*np.eye(nd)
    BF=draw((n,n));BF[:,:na]=0;BR=draw((n,n));BR[:na]=0
    forms=dict(K=K,M=M,B_forward=BF,B_reverse=BR);state=draw((2*nd,ns));L=draw((n,2));wall=[draw((2,ns))for _ in range(3)]
    a=signed_field_face_reconstruction(forms,np.eye(n),L,wall,state,na)
    f,ft=a['total_field'],a['total_coordinate_rate']
    np.testing.assert_allclose((K@f+BF@ft)[:na],0,atol=8e-15)
    np.testing.assert_allclose((M@ft+BR@f)[na:],state[nd:],rtol=3e-14,atol=8e-15)
    np.testing.assert_allclose(a['original_unbordered_Euler_rows'],0,atol=3e-14)
    # Independent simultaneous Gauss/momentum solve at the SAME full value
    # verifies both analytic cross blocks and the affine source count.
    phase=np.block([[M[na:,na:],BR[na:,:na]],[BF[:na,na:],K[:na,:na]]])
    rhs=np.r_[state[nd:]-BR[na:,na:]@f[na:],-K[:na,na:]@f[na:]]
    exact=np.linalg.solve(phase,rhs)
    np.testing.assert_allclose(ft[na:],exact[:nd],rtol=3e-14,atol=9e-15)
    np.testing.assert_allclose(f[:na],exact[nd:],rtol=3e-14,atol=9e-15)
