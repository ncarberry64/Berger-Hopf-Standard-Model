import numpy as np
from bhsm.interface.muon_complex_canonical_midpoint import (
    complex_canonical_midpoint_rows,solve_complex_canonical_midpoint)


def test_complex_canonical_step_matches_cayley_and_discrete_action_cotangents():
    # Independent Hamiltonian Cayley solution for a complex oscillator,
    # with a genuine algebraic saddle and two named null frame variables.
    n=2;m=3;mass=np.diag([2.,3.]);Q=np.array([[1.,.3],[.3,2.]])
    H=np.zeros((2*n+m,)*2,complex);H[:n,:n]=-Q;H[n:2*n,n:2*n]=mass
    H[2*n,2*n]=4.;source=np.zeros(2*n+m,complex);source[2*n]=.7+.2j
    def evaluate(eta):return dict(gradient=H@eta+source,hessian=H,value=eta@H@eta/2+source@eta)
    x=np.array([.2+.1j,-.4j]);p=np.array([.6-.2j,.1j]);h=.07-.02j
    eta=np.r_[x,np.linalg.solve(mass,p),np.array([-.1,.3j,.2])]
    C=np.zeros((2,n+m));C[0,-2]=1;C[1,-1]=1
    result=solve_complex_canonical_midpoint(x,p,eta,h,evaluate,dict(named_frame_covectors=C))
    assert result['status']=='ALL_ORIGINAL_COMPLEX_CANONICAL_ROWS_TOLERANCE'
    a=result['application'];F=np.block([[np.zeros((n,n)),np.linalg.inv(mass)],[-Q,np.zeros((n,n))]])
    expected=np.linalg.solve(np.eye(2*n)-h*F/2,(np.eye(2*n)+h*F/2)@np.r_[x,p])
    np.testing.assert_allclose(np.r_[a['x_new'],a['p_new']],expected,atol=2e-16)
    np.testing.assert_allclose(a['initial_action_cotangent'],-p,atol=2e-16)
    np.testing.assert_allclose(a['final_action_cotangent'],a['p_new'],atol=2e-16)
    np.testing.assert_allclose(a['algebraic_action_cotangent'],0,atol=1e-17)
    assert abs(a['midpoint_coefficients'][2*n]+(.7+.2j)/4)<1e-16
    assert np.max(abs(result['frame_reactions']))<1e-16


def test_nonlinear_nonreal_action_jacobian_matches_independent_direction():
    n=2;m=1;H=np.diag([1.,2.,3.,4.,5.]).astype(complex)
    d=np.array([.3,.7,-.2,.5,.9],complex);coefficient=.04+.03j
    def evaluate(eta):
        q=d@eta
        return dict(value=eta@H@eta/2+coefficient*q**4,
                    gradient=H@eta+4*coefficient*q**3*d,
                    hessian=H+12*coefficient*q*q*np.outer(d,d))
    x=np.array([.2j,.4]);p=np.array([.3,-.1j]);h=.03-.07j
    z=np.array([.1+.2j,.3j,.2,.5j,.7,.1-.2j,-.4],complex)
    direction=np.array([.4j,.2,-.1,.6+.2j,-.7,.3j,.8],complex)
    a=complex_canonical_midpoint_rows(z,x,p,h,evaluate);eps=2e-6
    fd=(complex_canonical_midpoint_rows(z+eps*direction,x,p,h,evaluate)['residual']-
        complex_canonical_midpoint_rows(z-eps*direction,x,p,h,evaluate)['residual'])/(2*eps)
    np.testing.assert_allclose(a['jacobian']@direction,fd,rtol=2e-10,atol=2e-10)
    # This control would fail if any complex source/clock were projected.
    assert np.linalg.norm(a['residual'].imag)>.1


def test_temporal_gauge_velocity_lift_preserves_original_Gauss_compatibility():
    # Literal kinetic identity delta(v)=delta(At), with a moving endpoint.
    # This tests the complete canonical frame, not just an algebraic zero.
    H=np.array([[0.,0.,0.],[0.,1.,-1.],[0.,-1.,1.]],complex)
    def evaluate(e):return dict(gradient=H@e,hessian=H,value=e@H@e/2)
    x=np.array([.3j]);h=.04+.02j;eta=np.array([x[0],.5j,.5j])
    C=np.array([[0.,1.]])
    a=solve_complex_canonical_midpoint(x,np.zeros(1),eta,h,evaluate,dict(named_frame_covectors=C))
    assert a['status']=='ALL_ORIGINAL_COMPLEX_CANONICAL_ROWS_TOLERANCE'
    np.testing.assert_allclose(a['application']['x_new'],x+h*eta[1],atol=0.)
    np.testing.assert_allclose(a['application']['p_new'],0,atol=0.)
    np.testing.assert_allclose(a['application']['residual'],0,atol=3e-17)
    # A frame reaction cannot hide a nonzero canonical charge/Gauss load.
    b=solve_complex_canonical_midpoint(x,np.array([.4]),eta,h,evaluate,dict(named_frame_covectors=C),max_iterations=2)
    assert b['status']!='ALL_ORIGINAL_COMPLEX_CANONICAL_ROWS_TOLERANCE'
    assert np.max(abs(b['application']['residual']))>.1
