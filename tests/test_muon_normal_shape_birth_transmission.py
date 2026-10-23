import numpy as np
from bhsm.interface.muon_normal_shape_birth_transmission import canonical_source_transmission


def test_source_offset_and_named_rows_match_independent_complete_complex_system():
    rng=np.random.default_rng(9007);n,m=3,2;d=n+m;nu=2*n
    H=rng.normal(size=(2*n+m,)*2)+.2j*rng.normal(size=(2*n+m,)*2)
    H[n:,n:]+=6*np.eye(d);F=np.zeros((1,d),complex);F[0,-1]=1
    E=np.eye(2*n);Jp=rng.normal(size=(9,len(H)))+.1j*rng.normal(size=(9,len(H)))
    Jc=rng.normal(size=Jp.shape)+.1j*rng.normal(size=Jp.shape)
    p=rng.normal(size=(len(H),1));g=.3*rng.normal(size=p.shape);b=.2*rng.normal(size=p.shape);extra=.1*rng.normal(size=(9,1))
    ids=np.array([0,2,4,6]);C=np.eye(nu)[[1,4]];target=np.array([[.12+.03j],[-.22+.01j]])
    a=canonical_source_transmission(H,F,E,Jp,Jc,p,np.zeros_like(p),g,np.zeros_like(g),b,np.zeros_like(b),extra,ids,C,target)
    K=np.block([[H[n:,n:],F.T],[F,np.zeros((1,1))]])
    maprhs=np.vstack((-H[n:,:n]@E[:n]+np.vstack((E[n:],np.zeros((m,nu)))),np.zeros((1,nu))))
    R=np.vstack((E[:n],np.linalg.solve(K,maprhs)[:d]))
    s=np.r_[np.zeros((n,1)),np.linalg.solve(K,np.r_[-g[n:],np.zeros((1,1))])[:d]]
    A=np.r_[(Jc@R)[ids],C];rhs=np.r_[-(Jp@p+Jc@(b+s)+extra)[ids],target]
    u=np.linalg.solve(A,rhs);aa=a['arrays'];got=aa['total_phase_high']+aa['total_phase_low']
    np.testing.assert_allclose(got,b+R@u+s,rtol=2e-13,atol=2e-13)
    assert a['selected_rows_upper']<1e-25 and a['held_rows_upper']<1e-25
    assert a['original_plus_reaction_upper']<1e-25 and a['literal_pairing_upper']<1e-25
    # All unselected action rows remain; a square solve does not set them0.
    assert np.max(abs(aa['all_original_state_and_known_source_rows_high']))>.1
