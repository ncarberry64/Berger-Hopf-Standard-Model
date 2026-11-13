from pathlib import Path
import numpy as np
import pytest

from bhsm.interface.muon_attached_source_mean_load import load_attached_reached_mean_inputs
from bhsm.interface.muon_current_source_motion_mean_load import enriched_reached_first_fields
from bhsm.interface.muon_current_source_motion_cubic import current_face_source_jets,current_source_cubic_application
from bhsm.interface.muon_electromagnetic_source_mean_load import (
    source_jet_motion_contact,load_electromagnetic_reached_mean_inputs,
    electromagnetic_source_jet_at_node,
)
from bhsm.interface.muon_primal_electromagnetic_source import higgs_aligned_source_first_jets
from bhsm.interface.muon_parent_maxwell_full_q_application import retained_full_q_angular_space


ROOT=Path(__file__).resolve().parents[1]


@pytest.fixture(scope='module')
def actual_fields():
    inputs=load_attached_reached_mean_inputs(
        'artifacts/muon_attached_reached_action_20261011/incoming_run_1',repository=ROOT)
    fields=enriched_reached_first_fields(inputs,inputs['times'][len(inputs['times'])//2])
    angular=retained_full_q_angular_space(ROOT)
    arguments={key:fields[key] for key in ('first_gauge','first_gauge_rate','first_gauge_radial',
        'first_wall_gauge','first_H','first_H_rate')}
    arguments['nu_squared_action']=inputs['receipt']['action_parameters']['nu_squared_action']
    return inputs,fields,angular,arguments


def test_general_source_contact_recovers_owned_Tb_only_limit(actual_fields):
    inputs,fields,angular,arguments=actual_fields
    raw=fields['raw_fields'];b=inputs['source']['b_source_coefficients']
    face=current_face_source_jets(raw[:100]);T,Td=face['T_b'],face['T_b_dot']
    dQ=np.zeros((268,400,8));dQt=dQ.copy()
    dQ[:100]=T.gradient[:,None,None]*b;dQt[:100]=Td.gradient[:,None,None]*b
    jet=dict(Q=T.value*b,Qdot=Td.value*b,Q_first_jet=dQ,Qdot_first_jet=dQt)
    # A finite nonzero pulse is an algebra check of the source pullback,
    # not a new physical pulse or a replacement of the saved response.
    p,pt=.37,-.21
    general=source_jet_motion_contact(raw,inputs['representation'],angular,jet,p,pt,**arguments)
    old=current_source_cubic_application(raw,inputs['representation'],angular,b,p,pt,**arguments)
    expected=old['moving_source_geometry_cubic']
    assert np.linalg.norm(general['source_motion_cotangent'][:100]-expected)<=3e-14*np.linalg.norm(expected)
    assert np.count_nonzero(general['source_motion_cotangent'][100:])==0


def test_H_selected_source_has_scalar_motion_and_future_rate_jets(actual_fields):
    _,fields,angular,_=actual_fields
    raw=fields['raw_fields'].copy()
    # Check all nonzero actual scalar directions without choosing an H axis.
    source=higgs_aligned_source_first_jets(raw,angular)
    assert np.linalg.norm(source['Q_first_jet'][-8:-4])>0
    assert np.linalg.norm(source['Qdot_first_jet'][-4:])>0
    direction=np.array([.2,-.1,.3,-.4]);eps=2e-6
    delta=np.zeros(268);delta[-8:-4]=direction
    plus=higgs_aligned_source_first_jets(raw+eps*delta,angular)
    minus=higgs_aligned_source_first_jets(raw-eps*delta,angular)
    for name,jet in (('connection_source','Q_first_jet'),('connection_source_rate','Qdot_first_jet')):
        measured=(plus[name]-minus[name])/(2*eps)
        analytic=np.einsum('r,rab->ab',delta,source[jet])
        assert np.linalg.norm(measured-analytic)<2e-9*np.linalg.norm(analytic)


def test_derived_zero_support_keeps_actual_nonzero_H_response(actual_fields):
    inputs,fields,angular,arguments=actual_fields
    actual=higgs_aligned_source_first_jets(fields['raw_fields'],angular)
    jet=dict(Q=actual['connection_source'],Qdot=actual['connection_source_rate'],
        Q_first_jet=actual['Q_first_jet'],Qdot_first_jet=actual['Qdot_first_jet'])
    assert fields['profile']==fields['profile_rate']==0
    assert np.linalg.norm(fields['first_H'])>0
    result=source_jet_motion_contact(fields['raw_fields'],inputs['representation'],angular,jet,
        fields['profile'],fields['profile_rate'],**arguments)
    assert np.count_nonzero(result['source_motion_cotangent'])==0
    assert result['source_motion_zero_reason'] is not None


def test_required_source_rate_jet_not_filled_zero(actual_fields):
    inputs,fields,angular,arguments=actual_fields
    jet=dict(Q=np.zeros((400,8)),Qdot=np.zeros((400,8)),Q_first_jet=np.zeros((268,400,8)))
    with pytest.raises(ValueError,match='source-rate first jet'):
        source_jet_motion_contact(fields['raw_fields'],inputs['representation'],angular,jet,0.,0.,**arguments)


def test_actual_EM_binding_retains_new_image_H_and_chronological_J():
    inputs=load_electromagnetic_reached_mean_inputs(
        'artifacts/muon_primal_electromagnetic_source_20261011/incoming_run_1',repository=ROOT)
    assert inputs['actual_H_selected_EM_source']
    assert inputs['source']['b_source_coefficients'].ndim==3
    t=inputs['times'][len(inputs['times'])//2]
    jet=electromagnetic_source_jet_at_node(inputs,t)
    assert np.linalg.norm(jet['Q_first_jet'][-8:-4])>0
    fields=enriched_reached_first_fields(inputs,t)
    assert np.linalg.norm(fields['first_H'])>0
    assert fields['coordinate_time']==-t
    assert fields['profile']==fields['profile_rate']==0
    assert not np.any(fields['first_wall_gauge'])


def test_old_Q8_response_cannot_be_relabelled_electromagnetic():
    with pytest.raises(ValueError,match='H-selected EM response'):
        load_electromagnetic_reached_mean_inputs(
            'artifacts/muon_attached_reached_action_20261011/incoming_run_1',repository=ROOT)
