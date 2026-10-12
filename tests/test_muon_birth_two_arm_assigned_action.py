import numpy as np
import pytest

from bhsm.interface.muon_birth_two_arm_assigned_action import (
    two_arm_time_jet,same_action_attachment_momentum,two_arm_assigned_rows,
)
from bhsm.interface.aether_full_reset_action_jacobian import _attachment_jacobian_at_order
from bhsm.interface.muon_parent_gauge_geometry_correction import ROOT,STATE_SOURCE,correction_representation


def test_oriented_arm_rates_and_common_birth_are_exact():
    length=.003
    for side,t in [('incoming',np.array([-.0025,-.0017,-.0004])),('outgoing',np.array([.0005,.0013,.0026]))]:
        v,d=two_arm_time_jet(t,length,3,side);step=1e-8
        plus,_=two_arm_time_jet(t+step,length,3,side);minus,_=two_arm_time_jet(t-step,length,3,side)
        np.testing.assert_allclose(d,(plus-minus)/(2*step),rtol=2e-9,atol=2e-7)
        ends=np.array([-length,0.]) if side=='incoming' else np.array([0.,length])
        v,d=two_arm_time_jet(ends,length,3,side)
        np.testing.assert_array_equal(v,0);np.testing.assert_array_equal(d,0)
    with pytest.raises(ValueError,match='outside'):
        two_arm_time_jet(np.array([-.001]),length,1,'outgoing')


def _lift_fixture(singular=False):
    q=np.zeros(37);A=np.diag(np.linspace(.9,1.8,37));C=np.zeros((24,37));C[:,13:37]=np.eye(24)
    if singular:A[0,0]=0
    h=np.zeros((100,100));h[37:74,37:74]=A;h[74:98,37:74]=C;h[37:74,74:98]=C.T
    g=np.zeros(100);g[37:74]=np.sin(np.arange(37))
    return q,dict(hessian=h,gradient=g),A,C


def test_saddle_lift_agrees_with_retained_compliance_when_regular():
    q,action,A,C=_lift_fixture();B=_attachment_jacobian_at_order(12,q);G=np.vstack((B,C))
    target=np.zeros((26,2));target[:2]=np.eye(2)
    inverse=np.linalg.solve(A,G.T);lift=inverse@np.linalg.solve(G@inverse,target)
    out=same_action_attachment_momentum(q,action)
    np.testing.assert_allclose(out['lift'],lift,rtol=1e-13,atol=2e-15)
    np.testing.assert_allclose(out['momentum'],lift.T@action['gradient'][37:74],rtol=1e-13,atol=2e-15)
    np.testing.assert_allclose(out['constraint_annihilation'],0,atol=1e-14)
    assert out['regularizing_shift']==0


def test_singular_velocity_form_can_have_regular_constrained_lift():
    q,action,A,C=_lift_fixture(True)
    assert np.linalg.matrix_rank(A)==36
    out=same_action_attachment_momentum(q,action)
    np.testing.assert_allclose(out['boundary_lift_residual'],0,atol=2e-14)
    np.testing.assert_allclose(out['constraint_annihilation'],0,atol=2e-14)
    np.testing.assert_allclose(out['saddle_residual'],0,atol=2e-14)
    assert out['stationarity_not_positive_minimization']


def test_actual_two_arm_rows_keep_ordered_mode_diagnostic_separate():
    rep=correction_representation(radial_points=12,radial_order=1,cap_points=12)
    with np.load(ROOT/STATE_SOURCE,allow_pickle=False) as f:
        x=f['state'];weights=f['state_weights'];reference=f['branch_reference']
    states=np.array([x[98:],x[:98]])
    fields=dict(gauge=np.zeros((12,1,5,4)),gauge_tau=np.zeros((12,1,5,4)),gauge_rho=np.zeros((12,1,5,4)),gauge_angular=np.zeros((12,1,3,5,4)))
    args=dict(rho=rep['rho'],radial_quadrature=rep['radial_quadrature'],fields=fields,H_real=np.array([0.,.8,0.,0.]),H_rate=np.zeros(4),
        wall_gauge=np.zeros((5,4)),lambda_H=rep['scalar_matching']['lambda_H'],nu_squared_action=4.,cap_points=12)
    out=two_arm_assigned_rows(states,[args,args],weights,reference,states[1,:37])
    assert out['residual'].shape==(56,)
    np.testing.assert_allclose(out['raw_trace_attachment'],0,atol=1e-14)
    assert not out['physical_birth_solution']
    assert all(not x['formation_criterion'] for x in out['ordered_velocity_diagnostic'])
    for arm in out['arms']:
        np.testing.assert_allclose(arm['canonical']['constraint_annihilation'],0,atol=2e-7)
