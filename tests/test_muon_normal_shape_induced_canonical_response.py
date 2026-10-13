"""Independent complete original-action source and true-face dual controls."""
import numpy as np
from bhsm.interface.muon_normal_shape_induced_canonical_response import forced_original_canonical_jacobi,source_complete_true_face
from bhsm.interface.muon_complex_canonical_midpoint import complex_canonical_midpoint_rows


def test_forced_jacobi_matches_whole_quadratic_action_source_difference():
    rng=np.random.default_rng(815);n,m=2,2;d=2*n+m
    A=rng.normal(size=(d,d))+.1j*rng.normal(size=(d,d));H=A+A.T+8*np.eye(d)
    F=np.zeros((1,n+m),complex);F[0,-1]=1;g=rng.normal(size=d)+.2j*rng.normal(size=d)
    initial_source=rng.normal(size=n)+.1j*rng.normal(size=n);h=.13-.04j
    initial=np.r_[np.zeros(n),initial_source][:,None]
    z=forced_original_canonical_jacobi(H,h,F,initial,np.zeros_like(initial),g)
    def full(epsilon):
        x0=np.zeros(n);p0=epsilon*initial_source;unknown=np.zeros(3*n+m,complex)
        a=complex_canonical_midpoint_rows(unknown,x0,p0,h,lambda eta:dict(gradient=H@eta+epsilon*g,hessian=H))
        C=np.zeros((1,len(unknown)),complex);C[:,2*n:]=F;E=np.zeros((len(unknown),1),complex);E[2*n:]=F.T
        K=np.block([[a['jacobian'],E],[C,np.zeros((1,1))]])
        return np.linalg.solve(K,-np.r_[a['residual'],0])[:-1]
    epsilon=2e-5;fd=(full(epsilon)-full(-epsilon))/(2*epsilon)
    actual=(z['solution_high']+z['solution_low'])[:-1,0]
    assert np.max(abs(fd-actual))<2e-15
    assert z['framed_rows_upper']<1e-28
    assert z['original_plus_reaction_assembly_upper']<1e-28
    assert z['literal_pairing_upper']<1e-28


def test_full_phase_rate_dual_and_source_offset_match_dense_true_face():
    rng=np.random.default_rng(242);n,m=3,2;d=2*n+m
    A=rng.normal(size=(d,d))+.1j*rng.normal(size=(d,d));H=A+A.T+9*np.eye(d)
    F=np.zeros((1,n+m),complex);F[0,-1]=1
    Q=(rng.normal(size=2*n)+.2j*rng.normal(size=2*n))[:,None]
    g=rng.normal(size=d)+.1j*rng.normal(size=d);B=rng.normal(size=d)+.3j*rng.normal(size=d)
    z=source_complete_true_face(H,F,Q,np.zeros_like(Q),g,B)
    K=np.block([[H[n:,n:],F.T],[F,np.zeros((1,1))]])
    rhs=np.r_[Q[n:,0],np.zeros(m)]-H[n:,:n]@Q[:n,0]-g[n:]
    v=np.linalg.solve(K,np.r_[rhs,0]);eta=np.r_[Q[:n,0],v[:-1]]
    assert np.max(abs(z['induced_phase_high'][:,0]+z['induced_phase_low'][:,0]-eta))<4e-15
    assert abs(z['complete_rate_work'][0,0]-B@eta)<3e-15
    assert z['full_rate_work_decomposition_upper']<1e-27
    assert abs(z['rate_source_offset_contact'])>1e-3
    assert abs(B@eta-B[:n]@eta[:n])>.1
