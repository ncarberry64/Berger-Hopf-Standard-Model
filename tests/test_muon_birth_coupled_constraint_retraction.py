import numpy as np
import pytest

from bhsm.interface.muon_birth_coupled_constraint_retraction import (
    pointwise_assigned_action, retract_multiplier_constraints,
)
from bhsm.interface.muon_parent_gauge_geometry_correction import (
    ROOT, retained_state, correction_representation, intrinsic_m4_weight_jet,
)


@pytest.fixture(scope='module')
def application():
    rep=correction_representation(time_points=2,radial_points=12,radial_order=1,cap_points=12)
    q,v,m=retained_state(ROOT)
    fields=dict(gauge=np.zeros((12,1,5,4)),gauge_tau=np.zeros((12,1,5,4)),
        gauge_rho=np.zeros((12,1,5,4)),gauge_angular=np.zeros((12,1,3,5,4)))
    args=dict(rho=rep['rho'],radial_quadrature=rep['radial_quadrature'],fields=fields,
        H_real=np.array([.1,.8,-.2,.05]),H_rate=np.array([.03,-.04,.02,.01]),
        wall_gauge=np.zeros((5,4)),lambda_H=rep['scalar_matching']['lambda_H'],
        nu_squared_action=4.,cap_points=12)
    return q,v,m,args,pointwise_assigned_action(q,v,m,**args)


def test_constraint_jacobian_differentiates_actual_assigned_action(application):
    q,v,m,args,base=application
    d=np.sin(np.arange(61));d/=np.linalg.norm(d);eps=1e-6
    plus=pointwise_assigned_action(q,v+eps*d[:37],m+eps*d[37:],**args)
    minus=pointwise_assigned_action(q,v-eps*d[:37],m-eps*d[37:],**args)
    np.testing.assert_allclose(base['constraint_jacobian'][:,37:98]@d,
        (plus['multiplier_constraints']-minus['multiplier_constraints'])/(2*eps),
        rtol=2e-7,atol=2e-7)


def test_canonical_scalar_dual_contains_factor_two_and_density_once(application):
    q,v,m,args,base=application
    wt=intrinsic_m4_weight_jet(12,q,v,m)['wT'].value
    np.testing.assert_allclose(base['scalar_real_canonical_dual'],
        2*wt*args['H_rate']/(2*np.pi**2),rtol=1e-14)
    np.testing.assert_allclose(base['gradient'],sum((s['gradient'] for s in base['sectors'].values()),np.zeros(100)),rtol=0,atol=0)
    assert not base['physical_Pauli_contraction']
    assert not base['stationary_E1_claim']


def test_retraction_is_actual_weighted_rank_revealing_newton(application):
    q,v,m,args,base=application
    weights=np.linspace(.7,1.8,61)
    result=retract_multiplier_constraints(q,v,m,weights,action_arguments=args,max_iterations=6)
    assert result['status']=='ASSIGNED_MULTIPLIER_CONSTRAINT_TOLERANCE'
    assert np.linalg.norm(result['final']['multiplier_constraints'])<result['target']
    assert result['history'][0]['rank']==24
    for record in result['steps']:
        J=record['jacobian'];step=record['step']
        np.testing.assert_allclose(J@step+record['residual'],record['linearized_residual'],atol=1e-14)
        # The weighted step is orthogonal to the numerical nullspace: this
        # tests minimum-norm algebra, not a physical branch-selection rule.
        _,s,V=np.linalg.svd(J/weights[None,:],full_matrices=True)
        rank=np.sum(s>1e-12*s.max())
        np.testing.assert_allclose(V[rank:]@(weights*step),0,atol=2e-12)
    np.testing.assert_array_equal(result['q'],q)


def test_invalid_action_weights_are_rejected(application):
    q,v,m,args,_=application
    with pytest.raises(ValueError,match='positive inherited'):
        retract_multiplier_constraints(q,v,m,np.zeros(61),action_arguments=args)
