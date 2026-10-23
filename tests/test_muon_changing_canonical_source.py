import numpy as np
from bhsm.interface.muon_complex_canonical_midpoint import solve_complex_canonical_midpoint
from bhsm.interface.muon_changing_canonical_source import changing_stage_source, constitutive_source_two_term


def test_changing_nonlinear_stage_derivative_and_independent_analytic_dual():
    # Nonconstant Hessian and explicit moving source. No Hermitian replacement.
    def action(e,t):
        x,v,y=e;g=np.array([2*x+.21*x*x+t,3*v+.12*v*v+.07*y,.07*v+2*y],complex)
        H=np.array([[2+.42*x,0,0],[0,3+.24*v,.07],[0,.07,2]],complex)
        return dict(gradient=g,hessian=H)
    x=np.array([.3+.04j]);v=.2-.03j;y=-.035*v
    eta=np.array([x[0],v,y]);p=np.array([action(eta,0)['gradient'][1]])
    h=.03;frame=dict(named_frame_covectors=np.empty((0,2)))
    b=solve_complex_canonical_midpoint(x,p,eta,h,lambda e:action(e,h/2),frame,tolerance=1e-13)
    dx=np.array([.09+.02j]);dp=np.array([-.04+.07j]);g=np.array([1,0,0],complex)
    a=changing_stage_source(b,dx,dp,g,np.zeros(3),frame['named_frame_covectors'],np.empty(0),np.empty(0),np.array([1j]),delta_x_low=np.zeros(1),delta_p_low=np.zeros(1))
    assert a['original_rows_upper']<1e-14
    assert a['framed_rows_upper']<1e-28
    assert a['pairing_difference_upper']<1e-28
    eps=2e-5
    states=[]
    for sign in (1,-1):
        xx=x+sign*eps*dx;pp=p+sign*eps*dp;ee=eta.copy();ee[0]=xx[0]
        z=solve_complex_canonical_midpoint(xx,pp,ee,h,lambda e:action(e,h/2+sign*eps),frame,tolerance=1e-13)
        states.append(z['unknowns'])
    fd=(states[0]-states[1])/(2*eps)
    np.testing.assert_allclose(a['arrays']['stage_solution_high'],fd,rtol=2e-8,atol=2e-10)
    assert abs(a['normal_pairing']-1j*fd[0])<2e-10


def test_constitutive_two_term_source_preserves_independent_x_and_momentum():
    rng=np.random.default_rng(146)
    n=2;m=2
    A=rng.normal(size=(2*n+m,2*n+m))+.2j*rng.normal(size=(2*n+m,2*n+m))
    H=A+A.T+5*np.eye(2*n+m)
    C=np.array([[0,0,0,1]],complex)
    dx=np.array([.3+.02j,-.2+.07j]);dx_low=np.array([.003j,-.004])
    dp=np.array([.08+.03j,-.06+.01j]);dp_low=np.array([.007,-.002j])
    g=rng.normal(size=2*n+m)+.2j*rng.normal(size=2*n+m)
    gl=np.array([.003,-.008j,.004j,.007,-.005,.006j])
    fv=np.array([.04+.03j]);fl=np.array([.009j])
    a=constitutive_source_two_term(H,dx,dp,g,gl,C,fv,
        dx_low=dx_low,dp_low=dp_low,frame_value_low=fl)
    phase=H[n:,n:]
    K=np.block([[phase,C.T],[C,np.zeros((1,1))]])
    rhs=np.r_[np.r_[dp+dp_low,np.zeros(m)]-H[n:,:n]@(dx+dx_low)-(g+gl)[n:],fv+fl]
    z=np.linalg.solve(K,rhs)
    direction=np.r_[dx+dx_low,z[:n+m]]
    np.testing.assert_allclose(a['direction_high']+a['direction_low'],direction,atol=2e-15)
    np.testing.assert_array_equal(a['canonical_momentum_target_high'],dp)
    np.testing.assert_array_equal(a['canonical_momentum_target_low'],dp_low)
    np.testing.assert_array_equal(a['source_gradient_high'],g)
    np.testing.assert_array_equal(a['source_gradient_low'],gl)
    assert a['framed_rows_upper']<1e-28
    assert a['original_rows_upper']>.01  # Reaction cannot be counted as original admission.
    # A fresh inherited source is a new response with the SAME explicit x/Pi/frame.
    changed=gl.copy();changed[n]+=.03+.01j
    b=constitutive_source_two_term(H,dx,dp,g,changed,C,fv,
        dx_low=dx_low,dp_low=dp_low,frame_value_low=fl)
    np.testing.assert_array_equal(b['canonical_momentum_target_high'],dp)
    np.testing.assert_array_equal(b['direction_high'][:n]+b['direction_low'][:n],a['direction_high'][:n]+a['direction_low'][:n])
    assert np.linalg.norm(b['direction_high'][n:]-a['direction_high'][n:])>1e-3
