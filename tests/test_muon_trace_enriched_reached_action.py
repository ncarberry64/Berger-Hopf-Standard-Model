import numpy as np
import pytest
from bhsm.interface.muon_parent_gauge_geometry_correction import ROOT,correction_representation
from bhsm.interface.muon_parent_maxwell_full_q_application import retained_full_q_angular_space
from bhsm.interface.muon_birth_trace_enriched_phase import load_enriched_endpoint
from bhsm.interface.muon_reached_trace_action import coupled_reached_sample
from bhsm.interface.muon_trace_enriched_reached_action import enriched_coupled_reached_sample
from bhsm.interface.muon_parent_maxwell_full_weak import FIELD_ORDER


@pytest.fixture(scope='module')
def actual():
    source='artifacts/muon_parent_gauge_geometry_correction_20261010/paired_field_endpoint_enriched_run_1'
    loaded=load_enriched_endpoint(source,side='outgoing')
    angular=retained_full_q_angular_space(ROOT)
    return loaded,angular


def test_full_enriched_background_restricts_to_unchanged_literal_action(actual):
    loaded,angular=actual;rep=loaded['representation']
    original=correction_representation(radial_points=48,cap_points=48,radial_order=2,include_wall_lift=True,include_scalar_mean=True)
    raw=np.zeros(228);raw[:100]=loaded['raw'][:100];raw[-8:]=loaded['raw'][-8:]
    raw[100:160]=.002*np.sin(np.arange(60));raw[160:220]=.003*np.cos(np.arange(60))
    extended=np.zeros(268);extended[:100]=raw[:100];extended[-8:]=raw[-8:]
    for j,label in enumerate(original['gauge_labels']):
        radial=3 if label['wall_lift'] else label['radial']
        k=20*radial+4*FIELD_ORDER.index(label['field'])+label['internal']
        extended[100+k]=raw[100+j];extended[180+k]=raw[160+j]
    Q=.02*angular['source_coefficients'];Qt=.03*angular['source_coefficients']
    a=coupled_reached_sample(raw,original,angular,Q,Qt,nu_squared_action=4.)
    b=enriched_coupled_reached_sample(extended,rep,angular,Q,Qt,nu_squared_action=4.)
    for key in ('raw_forms','scalar_forms','gauge_weak_rows'):
        np.testing.assert_allclose(b[key],a[key],rtol=3e-13,atol=3e-10)


def test_new_radial_image_affects_bulk_weak_action_even_when_wall_trace_vanishes(actual):
    loaded,angular=actual;rep=loaded['representation'];raw=loaded['raw'].copy()
    assert not rep['wall_trace_map'][:,:,40:60].any()
    altered=raw.copy();altered[148]+=.01
    Q=.02*angular['source_coefficients'];Qt=.03*angular['source_coefficients']
    a=enriched_coupled_reached_sample(raw,rep,angular,Q,Qt,nu_squared_action=4.)
    b=enriched_coupled_reached_sample(altered,rep,angular,Q,Qt,nu_squared_action=4.)
    assert np.linalg.norm(a['raw_forms'][2]-b['raw_forms'][2])>1e-4
    np.testing.assert_array_equal(a['scalar_forms'],b['scalar_forms'])


def test_actual_full_action_gauss_reduction_preserves_all_eighty_rows(actual):
    loaded,angular=actual
    a=enriched_coupled_reached_sample(loaded['raw'],loaded['representation'],angular,
        .02*angular['source_coefficients'],.03*angular['source_coefficients'],nu_squared_action=4.)
    red=a['reduced'];z=np.sin(np.arange(408));zd=np.cos(np.arange(408))
    At=red['At_value_map']@z+red['At_velocity_map']@zd
    pieces=(red['Gauss_matrix']@At,red['Gauss_value_row']@z,red['Gauss_velocity_row']@zd)
    assert len(At)==80
    assert np.linalg.norm(sum(pieces))/(1+sum(np.linalg.norm(x) for x in pieces))<2e-14
    assert np.linalg.norm(a['full_background_values'])>0
