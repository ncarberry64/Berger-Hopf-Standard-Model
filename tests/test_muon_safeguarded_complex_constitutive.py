import numpy as np
from bhsm.interface.muon_safeguarded_complex_constitutive import safeguarded_complex_constitutive


def test_all_complex_rows_and_fixed_momentum_survive_trust_region():
    n=2; k=5
    D=np.diag([2.+.2j,3.-.1j,4.+.5j,0,0])
    H=np.zeros((n+k,n+k),complex);H[n:,n:]=D
    source=np.array([0,0,1+2j,0,0])
    def evaluate(e):
        g=H@e;g[n:]+=source
        return dict(gradient=g,hessian=H)
    C=np.zeros((2,k));C[0,-2]=1;C[1,-1]=1
    p=np.array([.7+.1j,-.4j]);eta=np.r_[.2j,.4,.1,.2,.3,.4,.5]
    a=safeguarded_complex_constitutive(eta,p,evaluate,
        dict(named_frame_covectors=C,literal_generators=C.T),max_evaluations=15)
    assert a['status']=='ORIGINAL_COMPLEX_CONSTITUTIVE_TOLERANCE'
    np.testing.assert_allclose(a['fixed_position_defect'],0.,atol=0.)
    np.testing.assert_allclose(a['original_constitutive_rows'],0.,atol=2e-15)
    np.testing.assert_allclose(a['coefficients'][n:n+2],p/np.diag(D)[:2],atol=1e-15)
    assert a['exact_rows_or_numerical_singular_directions_deleted'] is False


def test_optimizer_termination_does_not_promote_unresolved_action_source():
    n=2;k=5;H=np.zeros((n+k,n+k),complex)
    H[n:n+2,n:n+2]=np.eye(2)
    def evaluate(e):
        g=H@e;g[n+2]=1.
        return dict(gradient=g,hessian=H)
    C=np.zeros((2,k));C[0,-2]=1;C[1,-1]=1
    a=safeguarded_complex_constitutive(np.zeros(n+k),np.zeros(n),evaluate,
        dict(named_frame_covectors=C,literal_generators=C.T),max_evaluations=3)
    assert a['status']=='NUMERICAL_OPTIMIZER_TERMINATED_WITH_ORIGINAL_RESIDUAL'
    assert a['original_constitutive_rows'][2]==1.
