import numpy as np
from bhsm.interface.muon_complex_canonical_compatibility import complex_constitutive_compatibility


def test_original_analytic_rows_and_named_reactions_preserve_supplied_momentum():
    # A nonsymmetric complex source compatibility application with two
    # literal algebraic frame identities and one genuine constrained row.
    n=2;m=3;D=np.diag([2.,3.,4.,0.,0.]).astype(complex)
    H=np.zeros((2*n+m,)*2,complex);H[n:,n:]=D
    q=np.array([.2j,.4]);p=np.array([.7+.1j,-.4j]);source=np.array([0,0,1+2j,0,0])
    def evaluate(eta):
        g=H@eta;g[n:]+=source
        return dict(gradient=g,hessian=H)
    C=np.zeros((2,n+m));C[0,-2]=1;C[1,-1]=1;Z=C.T
    eta=np.r_[q,np.array([.1,.2]),np.array([.3,.4,.5])]
    a=complex_constitutive_compatibility(eta,p,evaluate,dict(named_frame_covectors=C,literal_generators=Z))
    assert a['status']=='FRAMED_CONSTITUTIVE_TOLERANCE'
    np.testing.assert_allclose(a['fixed_position_defect'],0.,atol=0.)
    np.testing.assert_allclose(a['original_constitutive_rows'],0.,atol=3e-16)
    np.testing.assert_allclose(a['coefficients'][n:2*n],p/np.array([2.,3.]),atol=2e-16)
    assert np.linalg.norm(p-evaluate(eta)['gradient'][n:2*n])>.1
