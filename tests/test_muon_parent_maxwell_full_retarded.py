"""Same-action elimination and finite retarded checks; no physical source chosen."""
import numpy as np
import pytest

from bhsm.interface.muon_parent_maxwell_full_retarded import (
    constrained_gauss_schur,full_reference_retarded_form,retarded_full_q_application)
from bhsm.interface.muon_parent_maxwell_geometry_weak import geometric_connection_coefficient_jets
from bhsm.interface.muon_moving_geometric_action import retained_state
from bhsm.interface.muon_birth_candidate_geometry_action import ROOT
from bhsm.interface.muon_parent_maxwell_full_weak import full_maxwell_hessian_pairing
from bhsm.interface.muon_parent_retarded_hypercharge import WALL,ALPHA


def test_gauss_elimination_is_stationary_literal_action_not_unforced_zero():
    # CONTROL_ONLY independent real finite action with nonzero At and
    # velocity/current coupling.  Compare scalar values and momentum.
    M=np.diag([0.,3.,4.]);B=np.array([[0.,.5,-.4],[0.,.2,.3],[0.,-.1,.4]])
    K=np.array([[2.,1.,-.5],[1.,-3.,.2],[-.5,.2,-4.]])
    r=constrained_gauss_schur(M,B,K,1)
    z=np.array([.7,-.3]);v=np.array([-.2,.6])
    y=r['At_value_map']@z+r['At_velocity_map']@v
    assert abs(y[0])>.1
    q=np.r_[y,z];dq=np.r_[0.,v]
    original=.5*dq@M@dq+q@B@dq+.5*q@K@q
    reduced=.5*v@r['M']@v+z@r['B']@v+.5*z@r['K']@z
    assert original==pytest.approx(reduced,abs=2e-15)
    np.testing.assert_allclose((K@q+B@dq)[:1],0,atol=1e-15)
    np.testing.assert_allclose((M@dq+B.T@q)[1:],r['M']@v+r['B'].T@z,atol=1e-15)


@pytest.mark.parametrize('which',[0,1,2])
def test_no_silent_complex_projection_in_action(which):
    args=[np.diag([0.,1.]),np.zeros((2,2)),np.eye(2)]
    args[which]=args[which].astype(complex);args[which][1,1]+=1j
    with pytest.raises(ValueError,match='no complex projection'):
        constrained_gauss_schur(*args,1)


def test_omitted_temporal_gauss_momentum_is_rejected():
    with pytest.raises(ValueError,match='At must be algebraic'):
        constrained_gauss_schur(np.eye(2),np.zeros((2,2)),np.eye(2),1)


def test_same_affine_vector_supplies_connection_and_its_coordinate_time_derivative():
    q,v,m=retained_state(ROOT);rho=np.array([.2,.7,1.3]);t=.001;h=2e-6
    def at(tt):return geometric_connection_coefficient_jets(12,q+tt*v,v,m,rho,clock='coordinate_time')
    now,plus,minus=at(t),at(t+h),at(t-h)
    fd=np.array([(a['connection_lambda'].value-b['connection_lambda'].value)/(2*h) for a,b in zip(plus['rows'],minus['rows'])])
    actual=np.array([x['lambda_tau'].value for x in now['rows']])
    np.testing.assert_allclose(actual,fd,rtol=2e-8,atol=2e-10)
    assert np.linalg.norm(actual)>0


@pytest.fixture(scope='module')
def evaluated():
    # CONTROL_ONLY interval and finite orders.  Actual E1 initial metric,
    # affine firstjet and all8 full-Q angular directions are consumed.
    form=full_reference_retarded_form(time_nodes=5,radial_points=12)
    response=retarded_full_q_application(form,time_steps=16)
    return form,response


def test_retarded_full5_has_real_gauss_elimination_and_actual_gradient_completion(evaluated):
    f,r=evaluated
    assert f['actual_gauge_gradient_columns']==80
    assert f['gauge_gradient_mass_identity_max']<5e-9
    assert f['minimum_interior_mass_eigenvalue']>0
    assert r['A_tau'].shape[1:]==(80,8)
    assert np.linalg.norm(r['A_tau'])>0
    assert r['Gauss_residual_maximum_relative']<3e-14
    np.testing.assert_array_equal(r['state'][0],np.zeros((640,8)))
    assert r['state'].shape[1:]==(640,8)


def test_retarded_source_pairing_keeps_temporal_endpoint_and_advanced_dual(evaluated):
    f,r=evaluated
    assert r['wall_trace_reaction_pairing'].shape==(8,8)
    assert np.max(abs(r['wall_trace_reaction_pairing']))>1e6
    assert np.linalg.norm(r['action_temporal_endpoint'])>0
    assert r['action_boundary_relative_defect']<2e-9
    np.testing.assert_allclose(r['adjoint_output'],r['adjoint_source_pairing'],atol=3e-7)
    assert r['adjoint_pairing_maximum_defect']<3e-7


def test_nonstationary_gauge_euler_reaction_cannot_be_promoted_to_physical_quotient(evaluated):
    f,r=evaluated
    assert np.linalg.norm(r['paired_gauge_Euler_reaction'])>.1
    assert f['physical_gauge_quotient_closed'] is False
    assert r['physical_gauge_quotient_closed'] is False
    assert r['stationary_background'] is False
    assert r['native_heat_evaluated'] is False
    assert r['physical_Pauli_form'] is None
    assert 'CONTROL_ONLY' in r['source_scope']


def test_added_gradient_rows_agree_with_literal_five_component_action(evaluated):
    # CONTROL_ONLY coefficient test.  All radial/temporal gradients and
    # At of D_A eta are reconstructed; the literal action is independent.
    f,_=evaluated;a=f['angular'];o=f['operators'];t=f['time_nodes'][2]
    q,v,m=retained_state(ROOT)
    c=geometric_connection_coefficient_jets(12,q+t*v,v,m,f['rho'],clock='coordinate_time')
    eta=np.eye(80)[:,17];rate=.4
    z=np.zeros(408);z[:400]=.2*a['source_coefficients'][:,2];z[13]=.3;z[80+11]=-.1;z[400]=.7
    dz=.23*z;dz[:80]=0
    left=[];lt=[];lr=[];right=[];rt=[];rr=[]
    for j,row in enumerate(c['rows']):
        p,l=f['H'][j];pr,dr=f['Hr'][j];x=f['rho'][j]/WALL
        norm=p/(x**ALPHA*(1-x));p2=norm/WALL**2*(ALPHA*(ALPHA-1)*x**(ALPHA-2)*(1-x)-2*ALPHA*x**(ALPHA-1))
        D=o['G0']+(row['connection_lambda'].value-1)*o['G1']
        L=np.r_[p*rate*eta,pr*eta,p*(D@eta)]
        Lt=np.r_[np.zeros(80),pr*rate*eta,p*(rate*D+row['lambda_tau'].value*o['G1'])@eta]
        Lr=np.r_[pr*rate*eta,p2*eta,(pr*D+p*row['lambda_rho'].value*o['G1'])@eta]
        Q=a['source_coefficients'];R=p*z[:400]+l*(Q@z[400:]);Rt=p*dz[:400]+l*(Q@dz[400:]);Rr=pr*z[:400]+dr*(Q@z[400:])
        left.append(L);lt.append(Lt);lr.append(Lr);right.append(R);rt.append(Rt);rr.append(Rr)
    def vals(coeff):return np.einsum('pn,rfn->rpf',a['basis_values'],np.asarray(coeff).reshape(-1,20,20)).reshape(len(f['rho']),-1,5,4)
    def ev(coeff):return np.einsum('pin,rfn->rpif',a['basis_derivative_values'],np.asarray(coeff).reshape(-1,20,20)).reshape(len(f['rho']),-1,3,5,4)
    zero=np.zeros_like(vals(left));ez=np.zeros_like(ev(left))
    literal=full_maxwell_hessian_pairing(c,f['quadrature'],a['Haar_weights'],
        gauge=zero,gauge_tau=zero,gauge_rho=zero,gauge_angular=ez,
        left=vals(left),left_tau=vals(lt),left_rho=vals(lr),left_angular=ev(left),
        right=vals(right),right_tau=vals(rt),right_rho=vals(rr),right_angular=ev(right),geometric_derivatives=False)
    G0z,G0v,G1z,G1v=f['gauge_weak_rows'](t)
    expected=eta@(G0z@z+G0v@dz+rate*(G1z@z+G1v@dz))
    assert literal['value']==pytest.approx(expected,rel=3e-12,abs=5e-8)


@pytest.mark.parametrize('kwargs',[{'duration':0.},{'final_time':.0001},{'time_nodes':4},{'radial_points':3}])
def test_explicit_computational_interval_and_representation_are_required(kwargs):
    with pytest.raises(ValueError,match='explicit positive resolved'):
        full_reference_retarded_form(**kwargs)
