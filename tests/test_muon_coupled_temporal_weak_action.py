"""Weak temporal identities and common scalar/geometry derivatives.

Polynomial histories/fields are controls, not an interacting BHSM base.
Retained coefficients test the real consumer slots without assigning H.
"""
from pathlib import Path

import numpy as np
import pytest

from bhsm.interface.muon_coupled_temporal_weak_action import (
    temporal_geometry_weak_application, fixed_covariant_scalar_geometry_action_jet,
    scalar_geometry_higgs_cross, combine_local_action_applications,
    coupled_scalar_geometry_application, inherited_scalar_event_matching,
    real_scalar_weak_coefficient_map,
    mechanical_scalar_action_coefficients, mechanical_scalar_geometry_action_jet,
)
from bhsm.interface.muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
from bhsm.interface.muon_moving_geometric_action import retained_state, moving_cap_action_jet
from bhsm.interface.muon_intrinsic_higgs_weak_action import (
    higgs_action, higgs_weak_residual, diagonal_kinetic_density,
)

ROOT=Path(__file__).resolve().parents[1]


def polynomial_block(t):
    # L=.5*qdot^2+2*q, q=t^2: Lq-Dt Lqdot=0.
    z=np.zeros((1,1)); one=np.ones((1,1))
    return dict(S_q=np.array([2.]),canonical_momentum=np.array([2*t]),
        multiplier_constraint_residual=np.array([0.]),
        B_q_direct=np.array([3.]),B_q_rate_direct=np.array([7.]),
        B_q_momentum_contact=np.array([5.]),B_q_rate_momentum_contact=np.array([11.]),
        B_m=np.array([13.]),B_m_rate=np.array([17.]),
        H_qq=z,H_qv=z,H_vq=z,H_vv=one,H_qm=z,H_vm=z,H_mm=z)


def polynomial_tests(t):
    return np.array([[1.,t,t*t]]),np.array([[0.,1.,2*t]]),np.zeros((1,3))


def evaluate_control():
    x,w=np.polynomial.legendre.leggauss(5); x=(x+1)/2; w=w/2
    tests=np.array([polynomial_tests(t)[0] for t in x])
    rates=np.array([polynomial_tests(t)[1] for t in x]); mt=np.zeros((5,1,3))
    endpoints=[]
    for t,sign in ((0.,-1),(1.,1)):
        q,v,m=polynomial_tests(t)
        endpoints.append(dict(orientation=sign,block=polynomial_block(t),q_tests=q,
            q_test_rates=v,m_tests=m,normal=t*t,normal_rate=2*t))
    return temporal_geometry_weak_application([polynomial_block(t) for t in x],w,
        tests,rates,mt,x*x,2*x,endpoints=endpoints)


def test_stationary_history_with_nonzero_endpoint_momentum():
    app=evaluate_control()
    np.testing.assert_allclose(app['euler_volume_pairing'],0,atol=1e-14)
    np.testing.assert_allclose(app['endpoint_momentum_pairing'],[2,2,2],atol=1e-14)
    assert not app['full_stationarity_claim']
    assert not app['retarded_reduced_Hermitian_claim']


def test_partial_normal_source_keeps_direct_rate_and_momentum_contacts():
    app=evaluate_control()
    # v=t^2: bq=3t^2+14t-Dt(5t^2+22t)=3t^2+4t-22.
    expected=[1+2-22,3/4+4/3-11,3/5+1-22/3]
    np.testing.assert_allclose(app['euler_source_pairing'],expected,atol=1e-14)
    np.testing.assert_allclose(app['endpoint_source_pairing'],[27,27,27],atol=1e-14)


def test_temporal_hessian_is_derivative_form_operator():
    app=evaluate_control()
    expected=np.array([[0,0,0],[0,1,1],[0,1,4/3]])
    np.testing.assert_allclose(app['action_hessian'],expected,atol=1e-14)
    # IBP kernel includes Dt^2; it is not a local (q,qdot,m) inversion.
    np.testing.assert_allclose(app['euler_hessian_pairing'][:,2],[-2,-1,-2/3],atol=1e-14)


def test_endpoint_test_transport_is_explicit():
    q,v,m=polynomial_tests(1)
    base=dict(orientation=1,block=polynomial_block(1),q_tests=q,q_test_rates=v,
              m_tests=m,normal=0,normal_rate=0,q_test_shape=np.ones((1,3)))
    app=temporal_geometry_weak_application([polynomial_block(1)],[1],q[None],v[None],
        m[None],[0],[0],endpoints=[base],q_test_shape=np.ones((1,1,3)),
        q_test_rate_shape=np.zeros((1,1,3)),m_test_shape=np.zeros((1,1,3)))
    np.testing.assert_allclose(app['endpoint_source_pairing'],[2,2,2])
    np.testing.assert_allclose(app['euler_source_pairing'],[0,0,0])


def test_temporal_shapes_and_orientation_fail_closed():
    q,v,m=polynomial_tests(1)
    e=dict(orientation=0,block=polynomial_block(1),q_tests=q,q_test_rates=v,
           m_tests=m,normal=0,normal_rate=0)
    with pytest.raises(ValueError,match='orientation'):
        temporal_geometry_weak_application([polynomial_block(1)],[1],q[None],v[None],
                                            m[None],[0],[0],endpoints=[e])


@pytest.fixture(scope='module')
def scalar_control():
    state=retained_state(ROOT)
    weights=intrinsic_m4_weight_jet(12,*state)
    rng=np.random.default_rng(117)
    H=rng.normal(size=(3,2))+1j*rng.normal(size=(3,2))
    DH=rng.normal(size=(3,4,2))+1j*rng.normal(size=(3,4,2))
    J=rng.normal(size=(3,2))+1j*rng.normal(size=(3,2))
    h=rng.normal(size=(3,2,4))+1j*rng.normal(size=(3,2,4))
    dh=rng.normal(size=(3,4,2,4))+1j*rng.normal(size=(3,4,2,4))
    return state,weights,H,DH,J,h,dh,np.array([.2,.3,.5])


def scalar_kwargs(weights,H,DH,J,quad):
    a=dict(time=weights['wT'].value,spatial=weights['wS'].value)
    return dict(quadrature=quad,kinetic_density=diagonal_kinetic_density(a),
                volume_density=weights['wV'].value,H=H,DH=DH,J=J,
                lambda_H=.7,nu_squared=.4)


def test_scalar_insertion_equals_literal_owned_action(scalar_control):
    _,w,H,DH,J,_,_,quad=scalar_control
    a=fixed_covariant_scalar_geometry_action_jet(w,H,DH,J,.7,.4,quad)
    assert a['total'].value==pytest.approx(higgs_action(**scalar_kwargs(w,H,DH,J,quad)),abs=3e-14)
    assert np.linalg.norm(a['total'].gradient[74:86])>1
    assert not a['complete_connection_frame_derivative']


def test_metric_higgs_cross_is_scalar_residual_geometry_derivative(scalar_control):
    state,w,H,DH,J,h,dh,quad=scalar_control
    mixed=scalar_geometry_higgs_cross(w,H,DH,J,h,dh,.7,.4,quad)
    q,v,m=state; eps=1e-6; p=q.copy(); n=q.copy(); p[25]+=eps; n[25]-=eps
    wp=intrinsic_m4_weight_jet(12,p,v,m); wn=intrinsic_m4_weight_jet(12,n,v,m)
    for j in range(4):
        plus=higgs_weak_residual(**scalar_kwargs(wp,H,DH,J,quad),phi=h[:,:,j],Dphi=dh[:,:,:,j])
        minus=higgs_weak_residual(**scalar_kwargs(wn,H,DH,J,quad),phi=h[:,:,j],Dphi=dh[:,:,:,j])
        assert (plus-minus)/(2*eps)==pytest.approx(mixed[25,j],rel=3e-8,abs=3e-8)


def test_common_scalar_partial_source_and_hessian(scalar_control):
    state,w,H,DH,J,_,_,quad=scalar_control
    scalar=fixed_covariant_scalar_geometry_action_jet(w,H,DH,J,.7,.4,quad)['total']
    eps=2e-5
    wp=intrinsic_m4_weight_jet(12,*state,source_value=eps)
    wn=intrinsic_m4_weight_jet(12,*state,source_value=-eps)
    plus=higgs_action(**scalar_kwargs(wp,H,DH,J,quad)); minus=higgs_action(**scalar_kwargs(wn,H,DH,J,quad))
    assert (plus-minus)/(2*eps)==pytest.approx(scalar.gradient[98],abs=3e-8)
    assert (plus-2*scalar.value+minus)/eps**2==pytest.approx(scalar.hessian[98,98],abs=2e-5)


def test_sectors_combined_before_reduction(scalar_control):
    state,w,H,DH,J,_,_,quad=scalar_control
    geo=moving_cap_action_jet(12,*state,points=32)
    scalar=fixed_covariant_scalar_geometry_action_jet(w,H,DH,J,.7,.4,quad)
    combined=combine_local_action_applications(geo,scalar)
    np.testing.assert_allclose(combined['multiplier_constraint_residual'],
        geo['total'].gradient[74:98]+scalar['total'].gradient[74:98],atol=1e-14)
    np.testing.assert_allclose(combined['B_q_momentum_contact'],
        geo['total'].hessian[37:74,98]+scalar['total'].hessian[37:74,98],atol=1e-13)
    assert not combined['stationarity_claim']
    invalid=dict(scalar,source_indices=(1,2))
    with pytest.raises(ValueError,match='domain'):
        combine_local_action_applications(geo,invalid)


@pytest.mark.parametrize('mechanical_patch',[None,'parent','child'])
def test_coupled_jacobian_is_same_action_real_variation(scalar_control,mechanical_patch):
    state,w,H,DH,J,h,dh,quad=scalar_control
    maps=np.zeros((3,100,2)); maps[:,25,0]=1.; maps[:,74,1]=1.
    tests=np.transpose(h,(2,0,1)); Dt=np.transpose(dh,(3,0,1,2))
    kwargs=dict(weight_nodes=[w]*3,quadrature=quad,metric_maps=maps,H=H,DH=DH,J=J,
        test_values=tests,test_derivatives=Dt,lambda_H=.7,nu_squared=.4,
        normal=np.ones(3),normal_rates=np.zeros(3))
    if mechanical_patch is not None:
        kwargs.update(mechanical_patch=mechanical_patch,mechanical_rotation=np.eye(3))
    base=coupled_scalar_geometry_application(**kwargs)
    eps=2e-6; p=H+eps*h[:,:,2]; n=H-eps*h[:,:,2]
    plus=coupled_scalar_geometry_application(**dict(kwargs,H=p,DH=DH+eps*dh[:,:,:,2]))
    minus=coupled_scalar_geometry_application(**dict(kwargs,H=n,DH=DH-eps*dh[:,:,:,2]))
    np.testing.assert_allclose((plus['scalar_action_residual']-minus['scalar_action_residual'])/(2*eps),
        base['scalar_action_jacobian'][:,4],rtol=2e-8,atol=2e-8)
    np.testing.assert_allclose(base['scalar_action_jacobian'],base['scalar_action_jacobian'].T,atol=2e-13)
    q,v,m=state; qp=q.copy(); qn=q.copy(); qp[25]+=eps; qn[25]-=eps
    wp=intrinsic_m4_weight_jet(12,qp,v,m); wn=intrinsic_m4_weight_jet(12,qn,v,m)
    plus=coupled_scalar_geometry_application(**dict(kwargs,weight_nodes=[wp]*3))
    minus=coupled_scalar_geometry_application(**dict(kwargs,weight_nodes=[wn]*3))
    np.testing.assert_allclose((plus['scalar_action_residual']-minus['scalar_action_residual'])/(2*eps),
        base['scalar_action_jacobian'][:,0],rtol=3e-8,atol=3e-8)
    wp=intrinsic_m4_weight_jet(12,*state,source_value=eps)
    wn=intrinsic_m4_weight_jet(12,*state,source_value=-eps)
    plus=coupled_scalar_geometry_application(**dict(kwargs,weight_nodes=[wp]*3))
    minus=coupled_scalar_geometry_application(**dict(kwargs,weight_nodes=[wn]*3))
    np.testing.assert_allclose((plus['scalar_action_residual']-minus['scalar_action_residual'])/(2*eps),
        base['scalar_partial_metric_normal_source'],rtol=3e-8,atol=3e-8)
    assert base['partial_fixed_connection_application']
    assert not base['full_stationarity_claim']


def matching_control():
    return dict(parent_trace=np.array([.3+.2j,-.4j]),child_trace=np.array([.7-.1j]),
        trace_transport=np.array([[1.+.2j,.3j]]),parent_flux=np.array([.5j,.8]),child_flux=np.array([-.2j]),
        parent_pairing=np.array([[2.,.2j],[-.2j,3.]]),child_pairing=np.array([[5.]]),
        parent_orientation=-1,child_orientation=1,boundary_source_covector=np.array([.1,.2j]),
        response_H_covector=np.array([.3j,-.1]),trace_transport_shape=np.array([[.3j,.4]]),
        parent_pairing_shape=np.array([[.2,.1j],[-.1j,-.3]]),child_pairing_shape=np.array([[.7]]),
        parent_flux_shape=np.array([.1j,.2]),child_flux_shape=np.array([.3j]),
        boundary_source_shape=np.array([-.1,.4j]),response_H_shape=np.array([.5j,.2]))


def test_event_matching_dual_preserves_nontrivial_pairing():
    kw=matching_control(); app=inherited_scalar_event_matching(**kw)
    rng=np.random.default_rng(33); p=rng.normal(size=2)+1j*rng.normal(size=2)
    c=rng.normal(size=1)+1j*rng.normal(size=1)
    lhs=np.vdot(kw['trace_transport']@p,kw['child_pairing']@c)
    rhs=np.vdot(p,kw['parent_pairing']@app['dual_trace_return']@c)
    assert lhs==pytest.approx(rhs,abs=2e-14)
    assert not np.allclose(app['dual_trace_return'],kw['trace_transport'].conj().T)
    assert not app['retarded_reduced_Hermitian_claim']


def test_event_matching_partial_shape_keeps_measure_frame_and_boundary_sources():
    kw=matching_control(); app=inherited_scalar_event_matching(**kw); eps=2e-6
    names=dict(trace_transport='trace_transport_shape',parent_pairing='parent_pairing_shape',
        child_pairing='child_pairing_shape',parent_flux='parent_flux_shape',child_flux='child_flux_shape',
        boundary_source_covector='boundary_source_shape',response_H_covector='response_H_shape')
    plus=dict(kw); minus=dict(kw)
    for name,delta in names.items():
        plus[name]=kw[name]+eps*kw[delta]; minus[name]=kw[name]-eps*kw[delta]
    p=inherited_scalar_event_matching(**plus); n=inherited_scalar_event_matching(**minus)
    np.testing.assert_allclose((p['flux_covector_residual']-n['flux_covector_residual'])/(2*eps),
                               app['partial_flux_shape'],rtol=1e-9,atol=1e-10)
    np.testing.assert_allclose((p['trace_residual']-n['trace_residual'])/(2*eps),
                               app['partial_trace_shape'],rtol=1e-9,atol=1e-10)


def test_evaluated_real_weak_polynomial_without_selecting_physical_field(scalar_control):
    _,w,H,_,J,_,_,_=scalar_control
    coefficients=real_scalar_weak_coefficient_map(w)
    x=np.concatenate((H.real,H.imag),axis=1); y=np.concatenate((J.real,J.imag),axis=1)
    for v,j in zip(x,y):
        actual=.7*np.einsum('ijkl,j,k,l->i',coefficients['cubic_tensor_times_lambda_H'],v,v,v)
        actual+=.7*.4*coefficients['linear_tensor_times_lambda_H_nu_squared']@v
        actual+=coefficients['source_pairing']@j
        expected=-2*w['wV'].value*(2*.7*(v@v-.4)*v+j)
        np.testing.assert_allclose(actual,expected,atol=1e-14)
    assert not coefficients['primal_H_evaluated']


@pytest.mark.parametrize('patch',['parent','child'])
def test_mechanical_connection_action_jet_includes_field_and_normal_cross(scalar_control,patch):
    state,w,H,DH,J,_,_,quad=scalar_control
    c=mechanical_scalar_action_coefficients(w,patch=patch,rotation=np.eye(3))
    application=mechanical_scalar_geometry_action_jet(w,H,DH,J,.7,.4,quad,
        patch=patch,rotation=np.eye(3))['total']
    def literal(weights):
        coeff=mechanical_scalar_action_coefficients(weights,patch=patch,rotation=np.eye(3))
        covariant=DH.copy()
        covariant[:,1:]+=coeff['kappa'].value*np.einsum('iab,pb->pia',coeff['unit_connection_generators'],H)
        return higgs_action(**scalar_kwargs(weights,H,covariant,J,quad))
    assert application.value==pytest.approx(literal(w),abs=3e-14)
    assert c['H_norm_coefficient'].value<0
    eps=2e-5
    wp=intrinsic_m4_weight_jet(12,*state,source_value=eps)
    wn=intrinsic_m4_weight_jet(12,*state,source_value=-eps)
    wpp=intrinsic_m4_weight_jet(12,*state,source_value=2*eps)
    wnn=intrinsic_m4_weight_jet(12,*state,source_value=-2*eps)
    first=(-literal(wpp)+8*literal(wp)-8*literal(wn)+literal(wnn))/(12*eps)
    assert first==pytest.approx(application.gradient[98],abs=2e-9)
    assert (literal(wp)-2*literal(w)+literal(wn))/eps**2==pytest.approx(application.hessian[98,98],abs=3e-5)
    q,v,m=state; qp=q.copy(); qn=q.copy(); qp[25]+=eps; qn[25]-=eps
    wp=intrinsic_m4_weight_jet(12,qp,v,m); wn=intrinsic_m4_weight_jet(12,qn,v,m)
    assert (literal(wp)-literal(wn))/(2*eps)==pytest.approx(application.gradient[25],abs=2e-8)
