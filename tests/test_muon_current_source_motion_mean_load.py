"""Independent mean-row derivative checks on actual interacting fields."""
import json
from pathlib import Path
import numpy as np
import pytest
from bhsm.interface.muon_current_source_motion_mean_load import prescribed_source_complete_mean_load
from bhsm.interface.muon_current_source_motion_cubic import current_face_source_jets,maxwell_cross_hessian,higgs_cross_hessian
from bhsm.interface.muon_parent_gauge_geometry_correction import correction_representation
from bhsm.interface.muon_parent_maxwell_full_q_application import retained_full_q_angular_space
from bhsm.interface.muon_parent_maxwell_geometry_weak import geometric_connection_coefficient_jets
from bhsm.interface.muon_parent_maxwell_full_weak import M,FIELD_ORDER
from bhsm.interface.muon_parent_mean_causal_action import MAXWELL_TO_CAP,VOLUME
ROOT=Path(__file__).resolve().parents[1]


@pytest.fixture(scope='module')
def actual():
    folder=ROOT/'artifacts/muon_parent_gauge_geometry_correction_20261010/enriched_phase_incoming_1steps_run_1';md=json.loads((folder/'result.json').read_text())
    rep=correction_representation(radial_points=48,cap_points=48,radial_order=2,include_wall_lift=True,include_scalar_mean=True)
    with np.load(folder/'application.npz',allow_pickle=False) as a:
        raw=a['stage_midpoint_raw'][0].copy()
        for name in ('rho','radial_quadrature','radial_value_map','radial_derivative_map','wall_trace_map'):rep[name]=a[name].copy()
    rep['gauge_labels']=md['gauge_labels'];N=80;R=len(rep['rho']);gb=np.zeros((R,N,1,5,4));gr=gb.copy()
    for j,label in enumerate(rep['gauge_labels']):
        f=FIELD_ORDER.index(label['field']);c=label['internal'];k=label['radial'];gb[:,j,0,f,c]=rep['radial_value_map'][:,k];gr[:,j,0,f,c]=rep['radial_derivative_map'][:,k]
    rep['gauge_basis']=gb;rep['gauge_radial_basis']=gr
    angular=retained_full_q_angular_space(ROOT);b=angular['source_coefficients'][:,:2]
    return raw,rep,angular,b


def _paired(raw,rep,angular,b):
    chart=current_face_source_jets(raw[:100]);T,Td=chart['T_b'].value,chart['T_b_dot'].value;w=chart['intrinsic_weights'];B=b.T.reshape(2,5,4,20);E=angular['derivative_matrices']
    geo=geometric_connection_coefficient_jets(12,raw[:37],raw[37:74],raw[74:98],rep['rho'],source_value=raw[98],source_rate=raw[99])
    gb,gr=rep['gauge_basis'],rep['gauge_radial_basis'];A=np.einsum('rj...,j->r...',gb,raw[100:180])[:,0];At=np.einsum('rj...,j->r...',gb,raw[180:260])[:,0];Ar=np.einsum('rj...,j->r...',gr,raw[100:180])[:,0]
    p=.7;pt=.2;out=np.zeros((2,2))
    for j,row in enumerate(geo['rows']):
        A[j,2:]+=M*(row['connection_lambda'].value-1);At[j,2:]+=M*row['lambda_tau'].value;Ar[j,2:]+=M*row['lambda_rho'].value
        lift=rep['radial_value_map'][j,-1];lr=rep['radial_derivative_map'][j,-1]
        u=(lift*T*p*B,lift*(Td*p+T*pt)*B,lr*T*p*B);d=np.array([row[k].value for k in ('electric','radial','angular','electric_radial','shift')])
        out+=MAXWELL_TO_CAP*rep['radial_quadrature'][j]*maxwell_cross_hessian(A[j],At[j],Ar[j],*u,*u,E,d)
    wall=np.einsum('fcj,j->fc',rep['wall_trace_map'],raw[100:180]);wall[2:]+=M*(w['mechanical_connection_lambda'].value-1);z=np.zeros((2,4,20));a=T*p*B
    out+=higgs_cross_hessian(raw[260:264],raw[264:],wall,z,z,a,z,z,a,E,np.array([w[k].value for k in ('wT','wS','wV')]),lambda_H=rep['scalar_matching']['lambda_H'],nu_squared_action=4.)/VOLUME**2
    return out


def test_complete_mean_load_retains_all_rows_and_independent_field_derivatives(actual):
    raw,rep,angular,b=actual;out=prescribed_source_complete_mean_load(raw,rep,angular,b,.7,.2,nu_squared_action=4.)
    assert out['raw_mean_cotangent'].shape==(268,2,2)
    assert out['all_represented_mean_rows_retained'];assert out['At_Gauss_rows_removed'] is False
    for index in (100,160,180,240,261,263):
        step=1e-5;d=np.eye(268)[index];fd=(_paired(raw+step*d,rep,angular,b)-_paired(raw-step*d,rep,angular,b))/(2*step)
        np.testing.assert_allclose(fd,out['raw_mean_cotangent'][index],rtol=3e-7,atol=3e-9)
    assert np.linalg.norm(out['scalar_value_cotangent'])>0
    assert np.linalg.norm(out['Maxwell_gauge_value_cotangent'])>0
    # This explicit spatial-only source has no mixed electric curvature; its rate row is action-zero in this restriction.
    np.testing.assert_array_equal(out['Maxwell_gauge_rate_cotangent'],0)
    # The action has no independent At-time derivative, even with nonzero Gauss value rows.
    At=np.array([i for i,l in enumerate(rep['gauge_labels']) if l['field']==FIELD_ORDER[0]])
    np.testing.assert_array_equal(out['Maxwell_gauge_rate_cotangent'][At],0)


def test_unknown_first_response_cannot_be_zero_filled(actual):
    from bhsm.interface.muon_current_source_motion_mean_load import current_source_complete_mean_load
    raw,rep,angular,b=actual
    with pytest.raises(ValueError,match='explicit real'):
        current_source_complete_mean_load(raw,rep,angular,b,.7,.2,first_gauge=None,first_gauge_rate=None,first_gauge_radial=None,first_wall_gauge=None,first_H=None,first_H_rate=None,nu_squared_action=4.)


def test_general_total_first_response_preserves_nonzero_mean_rate_rows(actual):
    from bhsm.interface.muon_current_source_motion_mean_load import current_source_complete_mean_load
    raw,rep,angular,b=actual;rng=np.random.default_rng(509);chart=current_face_source_jets(raw[:100]);B=b.T.reshape(2,5,4,20)
    c,ct=rng.normal(size=(2,2,5,4,20))*.01;profile=.7;profile_rate=.2
    v=rep['radial_value_map'];dr=rep['radial_derivative_map'];T,Td=chart['T_b'].value,chart['T_b_dot'].value
    u=v[:,0,None,None,None,None]*c+v[:,-1,None,None,None,None]*T*profile*B
    ut=v[:,0,None,None,None,None]*ct+v[:,-1,None,None,None,None]*(Td*profile+T*profile_rate)*B
    ur=dr[:,0,None,None,None,None]*c+dr[:,-1,None,None,None,None]*T*profile*B
    h,ht=rng.normal(size=(2,2,4,20))*.005
    out=current_source_complete_mean_load(raw,rep,angular,b,profile,profile_rate,first_gauge=u,first_gauge_rate=ut,first_gauge_radial=ur,first_wall_gauge=T*profile*B,first_H=h,first_H_rate=ht,nu_squared_action=4.)
    assert np.linalg.norm(out['Maxwell_gauge_rate_cotangent'])>0
    assert np.linalg.norm(out['scalar_rate_cotangent'])==0  # source Atwall=0 in this explicit trial, even when interiorAt is active
    assert out['continuum_angular_gravity_first_rows_filled_zero'] is False


def test_fresh_same_phase_fields_are_complete_and_midpoint_source_is_action_zero():
    from bhsm.interface.muon_current_source_motion_mean_load import load_enriched_reached_mean_inputs,enriched_reached_first_fields
    inputs=load_enriched_reached_mean_inputs('artifacts/muon_trace_enriched_reached_action_20261010/incoming_run_1',repository=ROOT)
    t=inputs['times'][len(inputs['times'])//2];out=enriched_reached_first_fields(inputs,t)
    index=np.flatnonzero(inputs['times']==t)[0]
    np.testing.assert_array_equal(out['first_H'],inputs['phase']['state'][index,320:400].T.reshape(8,4,20))
    np.testing.assert_array_equal(out['first_H_rate'],inputs['velocity']['velocity'][index,320:400].T.reshape(8,4,20))
    assert np.linalg.norm(out['first_H'])>0;assert np.linalg.norm(out['first_gauge'])>0
    assert out['profile']==out['profile_rate']==0
    np.testing.assert_array_equal(out['first_wall_gauge'],0)
    assert out['coordinate_time']==-5e-6
    assert out['all_solved_first_fields_used']


def test_fresh_field_application_rejects_extrapolation_and_unretained_time():
    from bhsm.interface.muon_current_source_motion_mean_load import load_enriched_reached_mean_inputs,enriched_reached_first_fields
    inputs=load_enriched_reached_mean_inputs('artifacts/muon_trace_enriched_reached_action_20261010/incoming_run_1',repository=ROOT)
    for t in (-1.,float('nan'),1e-12):
        with pytest.raises(ValueError):enriched_reached_first_fields(inputs,t)


def test_active_incoming_pulse_rate_has_future_coordinate_sign():
    from scipy.interpolate import CubicSpline
    from bhsm.interface.muon_current_source_motion_mean_load import load_enriched_reached_mean_inputs
    from bhsm.interface.muon_parent_retarded_hypercharge import compact_trace_pulse
    inputs=load_enriched_reached_mean_inputs('artifacts/muon_trace_enriched_reached_action_20261010/incoming_run_1',repository=ROOT)
    s=inputs['source'];L=inputs['times'][-1];D=inputs['receipt']['source_pulse_duration']
    np.testing.assert_array_equal(s['coordinate_times'],s['times']-L)
    index=16;u=inputs['times'][index];p,pt,_=compact_trace_pulse(u,D)
    assert p>0 and pt>0
    Q=CubicSpline(s['times'],s['Q'])(u);Qt=CubicSpline(s['times'],s['Qdot'])(u)
    np.testing.assert_allclose(inputs['contacts']['source_trace_rate'][index],pt*Q+p*Qt,rtol=2e-16,atol=1e-12)
    coordinate=u-L;step=D*1e-6
    fd=(compact_trace_pulse(coordinate+step+L,D)[0]-compact_trace_pulse(coordinate-step+L,D)[0])/(2*step)
    assert fd==pytest.approx(float(pt),rel=1e-9)
