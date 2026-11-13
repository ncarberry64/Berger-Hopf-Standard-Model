from pathlib import Path
import numpy as np
import pytest
from bhsm.interface.muon_magnetic_source_mean_load import (
    load_magnetic_reached_mean_inputs,magnetic_reached_first_fields,magnetic_source_jet_at_node)
from bhsm.interface.muon_parent_maxwell_full_q_application import retained_full_q_angular_space
from bhsm.interface.muon_magnetic_cell_source_heat import (
    magnetic_source_heat_polynomial,magnetic_source_even_y2_coefficient,
    magnetic_source_analytic_error_estimates)
ROOT=Path(__file__).resolve().parents[1]

@pytest.fixture(scope='module')
def actual():
    inputs=load_magnetic_reached_mean_inputs(
        'artifacts/muon_electromagnetic_soft_magnetic_source_20261011/incoming_run_1',repository=ROOT)
    fields=magnetic_reached_first_fields(inputs,inputs['times'][len(inputs['times'])//2])
    angular=retained_full_q_angular_space(ROOT)
    poly=magnetic_source_heat_polynomial(fields,inputs['representation'],angular,length=inputs['times'][-1])
    return inputs,fields,poly

def test_active_plateau_keeps_actual_gauge_and_solved_H(actual):
    inputs,fields,poly=actual
    assert fields['profile']==1 and fields['profile_rate']==0
    assert np.linalg.norm(fields['first_wall_gauge'])>0
    assert np.linalg.norm(fields['first_H'])>0
    assert not np.any(fields['first_wall_gauge'][3:])
    assert not np.any(fields['first_H'][3:])
    jet=magnetic_source_jet_at_node(inputs,fields['response_time'])
    assert np.array_equal(fields['first_wall_gauge'].reshape(8,400).T,jet['Q'])
    assert np.linalg.norm(poly['vertices']['gauge_spatial_vertex'])>0
    assert poly['exact_LR_even_sign_parity']

def test_incoming_active_ramp_keeps_future_rate(actual):
    inputs,_,_=actual
    fields=magnetic_reached_first_fields(inputs,inputs['source']['times'][1])
    assert fields['profile']==1 and fields['profile_rate']==0
    assert fields['coordinate_time']==fields['response_time']-inputs['times'][-1]
    # The shared callback returns the retained fields, not a reversed time derivative.
    assert np.linalg.norm(fields['first_H_rate'])>0

def test_all_intermediate_images_and_contact_orders_retained(actual):
    _,_,poly=actual
    assert poly['shells']['1']['intermediate_mode_count']==24
    assert poly['shells']['3']['intermediate_mode_count']==96
    for coefficient in poly['contact']:
        assert np.array_equal(coefficient,coefficient.swapaxes(0,1))
        assert not np.any(coefficient[3:]) and not np.any(coefficient[:,3:])
    assert np.linalg.norm(poly['contact'][0])>0
    assert np.linalg.norm(poly['contact'][2])>0

def test_contour_refinement_retains_direct_and_both_insertions(actual):
    _,_,poly=actual
    coarse=magnetic_source_even_y2_coefficient(poly,1.0329133712274834e-11,
        contour_radius=16384,contour_order=32,lag_order=32)
    fine=magnetic_source_even_y2_coefficient(poly,1.0329133712274834e-11,
        contour_radius=32768,contour_order=32,lag_order=64)
    a=coarse['paired_middle_minus_light_Y2_source_pair'];b=fine['paired_middle_minus_light_Y2_source_pair']
    assert np.linalg.norm(a['available_source_pair']-b['available_source_pair'])<2e-12*np.linalg.norm(b['available_source_pair'])
    assert np.array_equal(b['ordered_two_insertion'].T,b['opposite_order_two_insertion'])
    assert np.allclose(b['available_source_pair'],b['source_square_contact']+b['ordered_two_insertion']+b['opposite_order_two_insertion'],rtol=2e-15,atol=0)
    assert not np.any(b['available_source_pair'][3:])

def test_analytic_bound_scope_and_invalid_circle(actual):
    _,_,poly=actual
    result=magnetic_source_analytic_error_estimates(poly,1.0329133712274834e-11)
    assert result['bounding_circle_accretivity_margin']>0
    assert np.max(result['paired_even_Y4_remainder_majorant_estimate'])>0
    assert not result['norm_and_majorant_arithmetic_outward_certified']
    with pytest.raises(ValueError,match='accretive'):
        magnetic_source_even_y2_coefficient(poly,1e-11,contour_radius=1e8)

def test_old_compact_source_cannot_be_relabelled_magnetic():
    with pytest.raises(ValueError,match='local magnetic'):
        load_magnetic_reached_mean_inputs(
            'artifacts/muon_primal_electromagnetic_source_20261011/incoming_run_1',repository=ROOT)


def test_outgoing_fields_continue_actual_canonical_birth_not_new_ramp():
    incoming=load_magnetic_reached_mean_inputs(
        'artifacts/muon_electromagnetic_soft_magnetic_source_20261011/incoming_run_1',repository=ROOT)
    outgoing=load_magnetic_reached_mean_inputs(
        'artifacts/muon_electromagnetic_soft_magnetic_source_20261011/outgoing_run_1',repository=ROOT)
    assert np.array_equal(outgoing['phase']['state'][0],incoming['phase']['state'][-1])
    fields=magnetic_reached_first_fields(outgoing,outgoing['times'][0])
    assert fields['profile']==1 and fields['profile_rate']==0
    assert np.linalg.norm(fields['first_H'])>0
    assert not np.array_equal(outgoing['velocity']['velocity'][0],incoming['velocity']['velocity'][-1])
