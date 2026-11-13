import numpy as np
from bhsm.interface.muon_joined_chronological_heat_mean import canonical_initial_mean_rows


def test_initial_canonical_load_matches_independent_original_residual():
    # A constrained quadratic action with all mixed velocity/algebraic terms.
    rng=np.random.default_rng(21);A=rng.normal(size=(5,5));H=A+A.T
    n=2;h=-.3;x0=np.array([.2,-.4]);p0=np.array([.1,.8]);end=rng.normal(size=7)
    dx=rng.normal(size=(2,3));dp=rng.normal(size=(2,3))
    def residual(x,p):
        xn,pn,v,y=end[:2],end[2:4],end[4:6],end[6:]
        gradient=H@np.r_[(x+xn)/2,v,y]
        return np.r_[xn-x-h*v,pn-p-h*gradient[:2],gradient[2:4]-(p+pn)/2,gradient[4:]]
    J=np.zeros((7,7));J[:2,:2]=np.eye(2);J[:2,4:6]=-h*np.eye(2)
    J[2:4,:2]=-h*H[:2,:2]/2;J[2:4,2:4]=np.eye(2);J[2:4,4:]=-h*H[:2,2:]
    J[4:6,:2]=H[2:4,:2]/2;J[4:6,2:4]=-np.eye(2)/2;J[4:6,4:]=H[2:4,2:]
    J[6:,:2]=H[4:,:2]/2;J[6:,4:]=H[4:,2:]
    exact=canonical_initial_mean_rows(J,n,dx,dp)
    step=1e-5
    for j in range(3):
        fd=(residual(x0+step*dx[:,j],p0+step*dp[:,j])-residual(x0-step*dx[:,j],p0-step*dp[:,j]))/(2*step)
        np.testing.assert_allclose(exact[:,j],fd,rtol=2e-10,atol=2e-10)
