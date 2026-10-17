"""Literal-action checks for reached source motion before Gauss reduction."""
import json
import numpy as np
import pytest

from bhsm.interface.muon_reached_trace_action import (
    moving_trace_time_forms,coupled_reached_sample,moving_trace_gauge_rows,
)
from bhsm.interface.muon_parent_maxwell_corrected_retarded import (
    _integrated_time_forms,_gauge_rows,full_constant_angular_hessian,
)
from bhsm.interface.muon_parent_maxwell_full_q_application import retained_full_q_angular_space
from bhsm.interface.muon_parent_gauge_geometry_correction import ROOT,correction_representation
from bhsm.interface.muon_parent_maxwell_geometry_weak import geometric_connection_coefficient_jets
from bhsm.interface.muon_parent_maxwell_full_weak import M,full_maxwell_hessian_pairing
from bhsm.interface.muon_parent_retarded_hypercharge import WALL,regular_radial_basis


@pytest.fixture(scope='module')
def problem():
    with np.load(ROOT/'artifacts/muon_pointwise_full_field_action_20261010/run_2/application.npz',allow_pickle=False) as f:
        raw=f['raw_endpoint_coefficients'][0]
    rep=correction_representation(radial_points=12,cap_points=24,radial_order=2,include_wall_lift=True,include_scalar_mean=True)
    angular=retained_full_q_angular_space(ROOT)
    geo=geometric_connection_coefficient_jets(12,raw[:37],raw[37:74],raw[74:98],rep['rho'],source_value=raw[98],source_rate=raw[99])
    A=np.einsum('rj...,j->r...',rep['gauge_basis'],raw[100:160])[:,0]
    At=np.einsum('rj...,j->r...',rep['gauge_basis'],raw[160:220])[:,0]
    Ar=np.einsum('rj...,j->r...',rep['gauge_radial_basis'],raw[100:160])[:,0]
    local=[]
    for j,row in enumerate(geo['rows']):
        A[j,2:]+=M*(row['connection_lambda'].value-1)
        At[j,2:]+=M*row['lambda_tau'].value;Ar[j,2:]+=M*row['lambda_rho'].value
        local.append(full_constant_angular_hessian(A[j],At[j],Ar[j],[row[k].value for k in ('electric','radial','angular','electric_radial','shift')]))
    E=np.concatenate((np.eye(20)[None],angular['derivative_matrices']))
    products=np.array([[a.T@b for b in E] for a in E]);H,Hr=regular_radial_basis(rep['rho'],1)
    return raw,rep,angular,geo,local,A,H,Hr,E,products


def test_fixed_source_reduces_to_retained_action_and_gauge_rows(problem):
    raw,rep,a,geo,local,A,H,Hr,E,products=problem;Q=a['source_coefficients']
    tensors=np.array([z['tensor'] for z in local]);w=rep['radial_quadrature']
    actual=moving_trace_time_forms(tensors,w,H,Hr,Q,np.zeros_like(Q),products)
    retained=_integrated_time_forms(tensors,w,H,Hr,Q,products)
    for x,y in zip(actual,retained):np.testing.assert_allclose(x,y,rtol=3e-14,atol=5e-8)
    np.testing.assert_array_equal(moving_trace_gauge_rows(local,A,w,H,Hr,Q,np.zeros_like(Q),E),_gauge_rows(local,A,w,H,Hr,Q,E))


def test_moving_full_trace_matches_independent_literal_weak_action(problem):
    raw,rep,a,geo,local,A,H,Hr,E,products=problem
    rng=np.random.default_rng(31);Q=a['source_coefficients'].copy();Qt=np.zeros_like(Q)
    # An off-original-span component tests actual map motion. These are
    # representation test vectors, not physical current/mode selections.
    Q[180,0]+=.07;Qt[217,0]=.13;Qt[344,4]=-.21
    mass,mixed,K=moving_trace_time_forms(np.array([z['tensor'] for z in local]),rep['radial_quadrature'],H,Hr,Q,Qt,products)
    z=rng.normal(size=408);zd=rng.normal(size=408);b=rng.normal(size=408);bd=rng.normal(size=408)
    contracted=zd@mass@bd+z@mixed@bd+zd@mixed.T@b+z@K@b
    def profiles(x,xd):
        value=H[:,0,None]*x[:400]+H[:,1,None]*(Q@x[400:])
        time=H[:,0,None]*xd[:400]+H[:,1,None]*(Q@xd[400:]+Qt@x[400:])
        radial=Hr[:,0,None]*x[:400]+Hr[:,1,None]*(Q@x[400:])
        def val(f):return np.einsum('pn,rfn->rpf',a['basis_values'],f.reshape(-1,20,20)).reshape(len(H),-1,5,4)
        angular=np.einsum('pin,rfn->rpif',a['basis_derivative_values'],value.reshape(-1,20,20)).reshape(len(H),-1,3,5,4)
        return val(value),val(time),val(radial),angular
    left=profiles(z,zd);right=profiles(b,bd)
    fields={k:np.broadcast_to(np.einsum('rj...,j->r...',rep['gauge_basis'] if k!='gauge_rho' else rep['gauge_radial_basis'],raw[160:220] if k=='gauge_tau' else raw[100:160]),(len(H),len(a['Haar_weights']),5,4)) for k in ('gauge','gauge_tau','gauge_rho')}
    fields['gauge_angular']=np.zeros((len(H),len(a['Haar_weights']),3,5,4))
    literal=full_maxwell_hessian_pairing(geo,rep['radial_quadrature'],a['Haar_weights'],**fields,
        left=left[0],left_tau=left[1],left_rho=left[2],left_angular=left[3],
        right=right[0],right_tau=right[1],right_rho=right[2],right_angular=right[3],geometric_derivatives=False)
    assert contracted==pytest.approx(literal['value'],rel=8e-13,abs=3e-5)
    frozen=moving_trace_time_forms(np.array([z['tensor'] for z in local]),rep['radial_quadrature'],H,Hr,Q,np.zeros_like(Q),products)
    assert np.linalg.norm(mixed-frozen[1])>1e-4
    assert np.linalg.norm(K-frozen[2])>1e-4


def test_full_coupled_reached_action_keeps_gauss_higgs_and_source_motion(problem):
    raw,rep,a,*_=problem;Q=a['source_coefficients'];Qt=-.5*.088*Q
    result=coupled_reached_sample(raw,rep,a,Q,Qt,nu_squared_action=4.)
    assert result['all_moving_trace_contacts_retained']
    assert result['raw_forms'][0].shape==(488,488)
    assert result['gauge_weak_rows'].shape==(4,80,488)
    assert np.linalg.norm(result['raw_forms'][2][400:480,480:])>0
    f=result['reduced'];rng=np.random.default_rng(42);z=rng.normal(size=408);zd=rng.normal(size=408)
    At=f['At_value_map']@z+f['At_velocity_map']@zd
    r=f['Gauss_matrix']@At+f['Gauss_value_row']@z+f['Gauss_velocity_row']@zd
    assert np.linalg.norm(r)/(1+np.linalg.norm(f['Gauss_matrix']@At))<3e-14
    assert result['physical_free_wall_inverse'] is False
    with pytest.raises(ValueError):coupled_reached_sample(raw,rep,a,Q,None,nu_squared_action=4.)


def test_executed_reached_response_preserves_motion_and_actual_checks():
    folder=ROOT/'artifacts/muon_reached_trace_action_20261010/run_2'
    receipt=json.loads((folder/'result.json').read_text(encoding='utf8'))
    assert receipt['actual_new_reached_source_response']
    assert not receipt['old_source_span_response_substituted']
    assert receipt['source_motion_count']==1
    assert receipt['Gauss_relative_maximum']<4e-14
    assert receipt['adjoint_pairing_maximum_defect']<1e-14
    assert receipt['action_boundary_relative_defect']<1e-9
    assert receipt['original_Q8_outside_relative_norm']>1e-3
    assert receipt['intrinsic_H_response_norm']>1e-11
    assert receipt['gauge_Euler_reaction_norm']>1e-4
    with np.load(folder/'source.npz',allow_pickle=False) as f:
        q,qt=f['full400_source_Q'],f['full400_source_Qdot'];times=f['response_times']
        tb,tbd=f['T_b'],f['T_b_dot'];b=f['cut_b_source_coefficients']
        np.testing.assert_allclose(q,tb[:,None,None]*b[None],rtol=0,atol=0)
        np.testing.assert_allclose(qt,tbd[:,None,None]*b[None],rtol=0,atol=0)
    with np.load(folder/'contact.npz',allow_pickle=False) as f:
        np.testing.assert_allclose(f['adjoint_output'],f['adjoint_source_pairing'],rtol=0,atol=1e-14)
        assert np.linalg.norm(f['intrinsic_scalar_wall_current_pairing'])>0
    assert not receipt['physical_native_heat_closed']
    assert not receipt['physical_Pauli_value']
