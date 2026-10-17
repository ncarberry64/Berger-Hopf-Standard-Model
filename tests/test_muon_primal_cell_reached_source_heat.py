"""Actual reached wall restriction and source-paired positive-factor checks."""
from pathlib import Path
import numpy as np
import pytest
from bhsm.interface.muon_current_source_motion_mean_load import load_enriched_reached_mean_inputs,enriched_reached_first_fields
from bhsm.interface.muon_parent_maxwell_full_q_application import retained_full_q_angular_space
from bhsm.interface.muon_primal_cell_reached_source_heat import actual_reached_cell_vertices,actual_midpoint_reached_source_heat
ROOT=Path(__file__).resolve().parents[1]


@pytest.fixture(scope='module')
def actual():
    inputs=load_enriched_reached_mean_inputs('artifacts/muon_trace_enriched_reached_action_20261010/incoming_run_1',repository=ROOT)
    fields=enriched_reached_first_fields(inputs,inputs['times'][len(inputs['times'])//2])
    return fields,inputs['representation'],retained_full_q_angular_space(ROOT)


def test_actual_midpoint_dirichlet_wall_zero_and_nonzero_H_image(actual):
    fields,rep,_=actual;v=actual_reached_cell_vertices(fields,rep)
    np.testing.assert_array_equal(v['gauge_spatial_vertex'],0);np.testing.assert_array_equal(v['gauge_temporal_vertex'],0)
    assert np.linalg.norm(v['fixed_Y_H_response_vertex'])>0
    np.testing.assert_allclose(v['vertex_n0_to_angular'],v['adjoint_vertex_n0_to_angular'],rtol=0,atol=0)
    grading=np.diag([1]*12+[-1]*6)
    np.testing.assert_array_equal(grading@v['vertex_n0_to_angular']@grading,-v['vertex_n0_to_angular'])


def test_complete_shell_contact_is_literal_Haar_square_and_both_orders(actual):
    fields,rep,angular=actual;out=actual_midpoint_reached_source_heat(fields,rep,angular,length=1e-5,cutoff=1e-11)
    core=out['zero_Y_source_core'];assert core['intermediate_shells']['1']['intermediate_mode_count']==24
    assert core['intermediate_shells']['3']['intermediate_mode_count']==96
    X=np.concatenate([a['source_vertex'] for a in core['intermediate_shells'].values()],axis=1)
    gram=np.einsum('Aki,Bki->AB',X.conj(),X);expected=gram+gram.T
    # The off-diagonal entries cancel to16orders below the diagonal scale.
    # Check the independent whole matrix identity at its own norm scale.
    error=np.linalg.norm(core['mixed_contact_n0_spectral_diagonal'].sum(axis=-1)-expected)
    assert error<=2e-15*np.linalg.norm(expected)
    r=out['unit_Y2_source_pair'];np.testing.assert_array_equal(r['opposite_order_two_insertion'],r['ordered_two_insertion'].T)
    np.testing.assert_allclose(r['available_source_pair'],r['source_square_contact']+r['ordered_two_insertion']+r['opposite_order_two_insertion'],rtol=0,atol=0)
    assert np.linalg.norm(r['available_source_pair'])>0
    assert r['lag_rule32_64_pair_difference_norm']>=0
    assert not r['lag_rule_difference_is_rigorous_enclosure'];assert not r['proper_time_upper_tail_truncated']
    assert not out['induced_mean_second_operator_contact_included']


def test_temporal_vertex_keeps_antihermitian_adjoint_distinct(actual):
    fields,rep,_=actual;control=dict(fields);a=fields['first_wall_gauge'].copy();a[:,0,3]=.01
    control['first_wall_gauge']=a;v=actual_reached_cell_vertices(control,rep)
    np.testing.assert_array_equal(v['gauge_temporal_vertex'].conj().transpose(0,1,3,2),-v['gauge_temporal_vertex'])
    assert np.linalg.norm(v['vertex_n0_to_angular']-v['adjoint_vertex_n0_to_angular'])>0


def test_Y2_reduction_rejects_nonzero_wall_source(actual):
    fields,rep,angular=actual;bad=dict(fields);a=fields['first_wall_gauge'].copy();a[0,2,0,0]=1
    bad['first_wall_gauge']=a
    with pytest.raises(ValueError,match='zero Dirichlet'):
        actual_midpoint_reached_source_heat(bad,rep,angular,length=1e-5,cutoff=1e-11)
