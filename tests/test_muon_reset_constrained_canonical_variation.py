import numpy as np
from bhsm.interface.muon_reset_constrained_canonical_variation import canonical_variation_embedding,signed_reset_constrained_trial,canonical_variation_evolution


def test_full_Lyy_canonical_elimination_matches_literal_constrained_action():
    rng=np.random.default_rng(510);n=2;m=1;A=rng.normal(size=(5,5))+.2j*rng.normal(size=(5,5));H=A.T@A+np.eye(5)*3
    x=np.arange(n);v=n+x;y=np.arange(2*n,2*n+m);Gs=np.array([.4+.2j,.1,.3j,-.2,.5])
    B=np.array([[1,0,0,0,0]],complex);N=np.array([0,1,0,0,0],complex);F=np.zeros((0,3));C=np.zeros((0,5))
    a=canonical_variation_embedding(H,x,v,y,F,source_gradient=Gs)
    t=signed_reset_constrained_trial(H,a,B,N,C)
    # Independent original variable KKT. Ly enters once as its algebraic
    # compatibility constraint, never as a natural force forced to zero.
    E=np.vstack((B,H[y],N));rhs=np.r_[0,-Gs[y],1]
    K=np.block([[H,E.T],[E,np.zeros((3,3))]]);z=np.linalg.solve(K,np.r_[-Gs,rhs])
    np.testing.assert_allclose(t['original_master_direction'],z[:5],atol=2e-14,rtol=2e-14)
    assert np.max(abs(H[y]@t['original_master_direction']+Gs[y]))<2e-14
    assert abs(t['natural_normal_KKT_reaction'])>.1
    assert np.max(abs(a['original_source_rows']))<1e-14
    assert np.max(abs(t['original_rows']))<2e-14
    # Active Lyy and an algebraic source cannot be replaced by zero.
    assert abs(H[y[0],y[0]])>1
    assert np.linalg.norm(a['source_embedding'])>.01


def test_whole_canonical_embedding_time_jet_and_source_evolution():
    rng=np.random.default_rng(512);A=rng.normal(size=(7,7))+.1j*rng.normal(size=(7,7));H=A.T@A+np.eye(7)*4
    Hd=np.full((7,7),.03+.01j);Gs=np.arange(7)*(.03+.01j);Gst=np.arange(7)*(-.02+.04j)
    x=np.arange(3);v=3+x;y=np.array([6]);F=np.zeros((0,4))
    a=canonical_variation_embedding(H,x,v,y,F,source_gradient=Gs,hessian_time_first=Hd,source_gradient_time_first=Gst)
    h=1e-5;p=canonical_variation_embedding(H+h*Hd,x,v,y,F,source_gradient=Gs+h*Gst)
    m=canonical_variation_embedding(H-h*Hd,x,v,y,F,source_gradient=Gs-h*Gst)
    np.testing.assert_allclose(a['embedding_time_first'],(p['embedding']-m['embedding'])/(2*h),atol=3e-11,rtol=2e-7)
    np.testing.assert_allclose(a['source_embedding_time_first'],(p['source_embedding']-m['source_embedding'])/(2*h),atol=3e-11,rtol=2e-7)
    B=np.zeros((1,7));B[0,0]=1;N=np.zeros(7);N[1]=1;C=np.zeros((0,7))
    t=signed_reset_constrained_trial(H,a,B,N,C);e=canonical_variation_evolution(H,a,t)
    assert np.max(abs(e['original_position_rate_identity']))<2e-14
    assert np.max(abs(e['original_momentum_rate_identity']))<2e-14
    assert np.max(abs(e['original_algebraic_time_first']))<2e-14
