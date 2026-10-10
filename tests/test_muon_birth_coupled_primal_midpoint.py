import numpy as np
from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import _variables
from bhsm.interface.muon_birth_coupled_primal_midpoint import nonlinear_midpoint_rows,solve_nonlinear_midpoint


def nonlinear_action(eta):
    x0,x1,v0,v1,y=_variables(np.asarray(eta),0,5)
    L=.5*((1+.2*x0*x0)*v0*v0+(1+.1*x1)*v1*v1)+y*(v0-.3*x1)+.2*y*y-.1*x0**4-.2*x1*x1
    return dict(value=L.value,gradient=L.gradient,hessian=L.hessian,Lxx=L.hessian[:2,:2])


def test_full_nonlinear_midpoint_jacobian_is_same_action_directional_derivative():
    x0=np.array([.3,.2]);p0=np.array([.1,-.07]);z=np.array([.31,.19,.11,-.075,.09,-.06,.03]);v=np.sin(np.arange(7)+.2)
    a=nonlinear_midpoint_rows(z,x0,p0,.07,nonlinear_action);eps=1e-5
    p=nonlinear_midpoint_rows(z+eps*v,x0,p0,.07,nonlinear_action)
    m=nonlinear_midpoint_rows(z-eps*v,x0,p0,.07,nonlinear_action)
    np.testing.assert_allclose(a['jacobian']@v,(p['residual']-m['residual'])/(2*eps),rtol=2e-9,atol=3e-11)
    assert not a['instantaneous_Legendre_inverse_used']


def test_actual_constrained_quadratic_step_matches_independent_phase_cayley_map():
    stiffness=np.diag([.7,1.1]);c=1.2
    def action(eta):
        x,v,y=eta[:2],eta[2:4],eta[4]
        value=.5*v@v-.5*x@stiffness@x+y*v[0]+.5*c*y*y
        G=np.r_[-stiffness@x,v+[y,0],v[0]+c*y]
        H=np.zeros((5,5));H[:2,:2]=-stiffness;H[2:4,2:4]=np.eye(2);H[2,4]=H[4,2]=1;H[4,4]=c
        return dict(value=value,gradient=G,hessian=H,Lxx=H[:2,:2])
    eta0=np.array([.3,.2,.1,-.07,-.1/c]);h=.03;saved=[]
    def checkpoint(i,z,a,scale,history,status,old):saved.append((i,z.copy(),a['residual'].copy(),status,old.copy()))
    result=solve_nonlinear_midpoint(eta0,h,action,checkpoint=checkpoint,tolerance=1e-13)
    effective=np.diag([1-1/c,1]);F=np.block([[np.zeros((2,2)),np.linalg.inv(effective)],[-stiffness,np.zeros((2,2))]])
    z0=np.r_[eta0[:2],action(eta0)['gradient'][2:4]]
    independent=np.linalg.solve(np.eye(4)-h*F/2,(np.eye(4)+h*F/2)@z0)
    np.testing.assert_allclose(result['unknowns'][:4],independent,rtol=3e-15,atol=3e-16)
    np.testing.assert_allclose(result['application']['residual'],0,atol=3e-16)
    assert result['status']=='REPRESENTED_MIDPOINT_TOLERANCE'
    assert saved[-1][3]=='ACCEPTED_STEP'
    np.testing.assert_array_equal(saved[-1][1],result['unknowns'])
    assert result['regularizing_shift']==0


def test_backward_step_solves_the_same_nonlinear_action_in_past_orientation():
    eta0=np.array([.3,.2,.1,-.07,-.04]);forward=solve_nonlinear_midpoint(eta0,.01,nonlinear_action,tolerance=1e-13)
    # Keep the next canonical p as an actual phase datum, solve its
    # nonlinear Legendre equations rather than guessing a velocity.
    app=forward['application'];eta1=np.r_[app['x_new'],app['v_mid'],app['y_mid']]
    def constrained_reverse_evaluator(eta):return nonlinear_action(eta)
    backward=solve_nonlinear_midpoint(eta1,-.01,constrained_reverse_evaluator,tolerance=1e-13)
    assert backward['status']=='REPRESENTED_MIDPOINT_TOLERANCE'
    assert np.linalg.norm(backward['application']['residual'])<1e-12
    # This test establishes the oriented action solve, not exact phase
    # reversal with a newly re-Legendre-transformed endpoint velocity.
