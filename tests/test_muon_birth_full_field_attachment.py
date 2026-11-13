import numpy as np
from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import _variables
from bhsm.interface.muon_birth_full_field_attachment import constrained_attachment_lift,attachment_momentum_variation,attachment_momentum_cotangent


def action(eta):
    x0,x1,x2,v0,v1,v2,y=_variables(np.asarray(eta),0,7)
    s=(1+x0)*v0*v0/2+.8*v1*v1+.7*v2*v2+.15*v0*v1*v2+y*(v2+.3*v0*v1+.2*x1)+.1*y*y+.2*x0*v0
    return dict(value=s.value,gradient=s.gradient,hessian=s.hessian)


def boundary(eta):
    B=np.array([[1+.1*eta[0],0,0],[0,1+.1*eta[2],0]])
    db=np.zeros((7,2,3));db[0,0,0]=.1;db[2,1,1]=.1
    return B,db


def test_full_saddle_retains_multiplier_reaction_without_inverse_A():
    eta=np.array([.2,-.1,.3,.4,.2,-.3,.15]);B,db=boundary(eta)
    a=constrained_attachment_lift(action(eta),B,dynamic_count=3,algebraic_count=1)
    np.testing.assert_allclose(a['boundary_lift_residual'],0,atol=1e-15)
    np.testing.assert_allclose(a['constraint_annihilation'],0,atol=1e-15)
    np.testing.assert_allclose(a['saddle_residual'],0,atol=2e-15)
    assert np.linalg.norm(a['reaction'])>0
    singular=dict(gradient=np.zeros(7),hessian=np.zeros((7,7)))
    singular['hessian'][6,5]=singular['hessian'][5,6]=1
    r=constrained_attachment_lift(singular,B,dynamic_count=3,algebraic_count=1)
    np.testing.assert_allclose(r['boundary_lift_residual'],0,atol=1e-15)


def test_implicit_and_adjoint_variations_agree_with_independent_momentum_difference():
    eta=np.array([.2,-.1,.3,.4,.2,-.3,.15]);d=np.linspace(-.2,.4,7);B,db=boundary(eta);a=action(eta)
    base=constrained_attachment_lift(a,B,dynamic_count=3,algebraic_count=1);eps=1e-5
    plus=action(eta+eps*d);minus=action(eta-eps*d)
    v=attachment_momentum_variation(base,(plus['gradient']-minus['gradient'])/(2*eps),
        (plus['hessian']-minus['hessian'])/(2*eps),delta_boundary=np.einsum('k,kij->ij',d,db))
    p=constrained_attachment_lift(plus,boundary(eta+eps*d)[0],dynamic_count=3,algebraic_count=1)
    m=constrained_attachment_lift(minus,boundary(eta-eps*d)[0],dynamic_count=3,algebraic_count=1)
    np.testing.assert_allclose(v['momentum_variation'],(p['momentum']-m['momentum'])/(2*eps),rtol=5e-10,atol=5e-11)
    np.testing.assert_allclose(v['direct_adjoint_difference'],0,atol=1e-15)


def test_four_hessian_applications_supply_the_whole_cotangent_with_B_contact():
    eta=np.array([.2,-.1,.3,.4,.2,-.3,.15]);B,db=boundary(eta)
    result=attachment_momentum_cotangent(eta,action,B,db,dynamic_count=3,algebraic_count=1,difference_step=2e-5)
    independent=np.zeros((2,7));eps=1e-5
    for k in range(7):
        e=np.eye(7)[k]*eps
        p=constrained_attachment_lift(action(eta+e),boundary(eta+e)[0],dynamic_count=3,algebraic_count=1)
        m=constrained_attachment_lift(action(eta-e),boundary(eta-e)[0],dynamic_count=3,algebraic_count=1)
        independent[:,k]=(p['momentum']-m['momentum'])/(2*eps)
    np.testing.assert_allclose(result['cotangent'],independent,rtol=2e-9,atol=3e-10)
    assert len(result['directional_hessian_applications'])==2
    assert np.linalg.norm(result['boundary_contact'])>0
