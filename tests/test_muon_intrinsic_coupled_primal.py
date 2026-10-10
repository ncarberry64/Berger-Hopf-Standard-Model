"""Meaningful coefficient, canonical, domain and solve-contract checks."""
import numpy as np
import pytest

from bhsm.interface.muon_intrinsic_scalar_discretization import (
    scalar_s3_discretization,polynomial_temporal_discretization,
)
from bhsm.interface.muon_intrinsic_coupled_primal import (
    coupled_coefficient_layout,set_block,block_coefficients,
    branch_fields_from_coefficients,scalar_first_order_rows,
    graph_canonical_time_application,temporal_momentum_contraction,
    causal_collocation_rows,require_physical_solve_binding,
    UnboundPhysicalApplication,residual_driven_newton,
    geometry_euler_from_local_jet,
)
from bhsm.interface.aether_exact_radial_schur_lift_v15_83 import Jet


def fixture():
    a=scalar_s3_discretization(1)
    t={s:polynomial_temporal_discretization(-.1,0.,2) for s in ('parent','child')}
    layout=coupled_coefficient_layout(a,t,geometric_order=1)
    c=np.zeros(layout['size'])
    for side in t:
        m=np.zeros((3,2));m[:,0]=-.3
        set_block(c,layout,f'{side}.m',m)
    return a,t,layout,c


def test_scalar_and_momentum_are_unknowns_with_same_derivative_maps():
    a,t,l,c=fixture();nodes=t['parent']['interpolation_times']
    h=np.zeros((3,5,2),complex);h[:,0,0]=(1+2j)*nodes
    p=np.zeros_like(h);p[:,0,0]=3*nodes**2
    set_block(c,l,'parent.H',h);set_block(c,l,'parent.p_H',p)
    f=branch_fields_from_coefficients(c,l,a,t,'parent',interpolation=True)
    np.testing.assert_allclose(f['DH'][:,:,0,0],np.broadcast_to(1+2j,f['DH'][:,:,0,0].shape),atol=2e-14)
    np.testing.assert_allclose(f['Dtp_H'][:,:,0],np.broadcast_to(6*nodes[:,None],f['Dtp_H'][:,:,0].shape),atol=2e-14)
    assert not np.array_equal(f['H'],f['p_H'])
    assert f['source_provenance']['quantum_effects_deleted'] is False


def test_higgs_weak_time_pairing_has_two_but_momentum_does_not():
    a,t,l,c=fixture();h=np.zeros((3,5,2),complex)
    p=np.zeros_like(h);p[:,0,0]=1.;set_block(c,l,'parent.p_H',p)
    f=branch_fields_from_coefficients(c,l,a,t,'parent')
    test=h.copy();test[:,0,0]=t['parent']['interpolation_times']
    value=temporal_momentum_contraction(f,a,t['parent'],test)
    np.testing.assert_allclose(value,2*.1*(2*np.pi**2),rtol=2e-14)
    rows=scalar_first_order_rows(f,a,lambda_H=.7,nu_squared=.4)
    np.testing.assert_allclose(rows['kinematic'][:,0],-2*np.pi**2,rtol=2e-14)


def test_child_connection_uses_actual_pointwise_ad_g():
    a,t,l,c=fixture();f=branch_fields_from_coefficients(c,l,a,t,'child')
    assert np.max(np.ptp(f['connection'][0,:,1:].real,axis=0))>.01
    assert np.max(abs(f['connection'][:,:,0]))==0 # zero iterate, not a physical equation
    assert f['gauge_zero_is_only_an_iterate']


def test_time_connection_changes_same_unknown_field_application():
    a,t,l,c=fixture();h=np.zeros((3,5,2),complex);h[:,0,0]=1.
    assert not l['blocks']['parent.gauge']['complex']
    set_block(c,l,'parent.H',h)
    g=block_coefficients(c,l,'parent.gauge');g[:,0,0,3]=2.
    set_block(c,l,'parent.gauge',g)
    f=branch_fields_from_coefficients(c,l,a,t,'parent')
    np.testing.assert_allclose(f['DH'][:,:,0,0],-1j,atol=2e-14)


def test_causal_rows_leave_actual_past_unknown_instead_of_zero_selection():
    a,t,l,c=fixture();f=branch_fields_from_coefficients(c,l,a,t,'parent',interpolation=True)
    rows=scalar_first_order_rows(f,a,lambda_H=.7,nu_squared=.4)
    interior=causal_collocation_rows(rows)
    assert len(interior)==2*(3-1)*5*2
    assert len(interior)<2*3*5*2


def test_graph_legendre_uses_offdiagonal_terms_once():
    g=np.zeros((2,4,4));g[:,0,0]=3.;g[:,1:,1:]=-np.eye(3)
    g[:,0,1]=g[:,1,0]=.2
    h=np.zeros((2,2),complex);p=np.ones_like(h)*(1+2j);d=np.ones((2,3,2),complex)
    app=graph_canonical_time_application(G=g,H=h,p_H=p,spatial_covariant_derivatives=d)
    np.testing.assert_allclose(app['DtH'],(p-.2)/3)
    np.testing.assert_allclose(app['momentum_reconstruction'],p)


def test_geometry_uses_temporal_chain_rule_not_local_momentum_minimum():
    n=8;x=np.arange(n,dtype=float)/10
    A=np.diag(np.arange(1.,9.));A[2,0]=A[0,2]=.3
    jet=Jet(float(.5*x@A@x),A@x,A)
    app=geometry_euler_from_local_jet(jet,[.2,.3],[.4,.5],[.6,.7])
    tangent=np.array([.2,.3,.4,.5,.6,.7,0,0])
    np.testing.assert_allclose(app['F_q'],(A@x)[:2]-A[2:4]@tangent)
    np.testing.assert_allclose(app['canonical_geometry_momentum'],(A@x)[2:4])


def test_numeric_solve_fails_on_precise_owned_coefficient():
    with pytest.raises(UnboundPhysicalApplication) as caught:
        require_physical_solve_binding({})
    assert caught.value.operand=='lambda_H'
    assert 'fourth variation' in caught.value.producer
    assert 'lapse' in caught.value.consumer


def test_closed_newton_executes_only_with_all_boundary_bindings_control():
    # CONTROL_ONLY software solve. These named stand-ins are not physical
    # BHSM parameters/domain/load applications and are never production.
    binding=dict(lambda_H=.7,nu_squared_action_units=.4,surface_gamma=.2,
        incoming_scalar_event_load='CONTROL',worldvolume_bundle_conditions='CONTROL',
        complete_gauge_response_boundary_application='CONTROL')
    def action(x):return dict(residual=np.array([x[0]**2-2]),jacobian=np.array([[2*x[0]]]))
    r=residual_driven_newton([1.],action,binding=binding,tolerance=1e-12)
    assert r['converged'];assert r['history'][0]['correction_norm']>0
    assert r['history'][0]['updated_residual']<r['history'][0]['initial_residual']
    np.testing.assert_allclose(r['coefficients'],np.sqrt(2),atol=1e-12)
