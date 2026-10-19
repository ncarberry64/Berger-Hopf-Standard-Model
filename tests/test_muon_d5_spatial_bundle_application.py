"""Full spatial connection equations, ordered lifts and retained freedom."""
from pathlib import Path
import numpy as np
import pytest
from scipy.linalg import expm

from bhsm.interface.muon_d5_spatial_bundle_application import (
    cross_matrix,spatial_connection_row,spatial_rotation_jacobian,
    rotation_su2,known_spin_gauge_factor,spatial_bundle_application,
)
from bhsm.interface.muon_d5_event_bundle_incidence import original_event_coefficients
from bhsm.interface.muon_d5_event_formation_constraints import corrected_original_event_source_directions
from bhsm.interface.muon_d5_independent_residuals import recovered_export_history


def test_full_spatial_graph_and_rotation_contacts_without_identity_selection():
    O=expm(cross_matrix([.2,-.1,.3]));R=expm(cross_matrix([-.1,.3,.2]))
    p=np.c_[np.diag([-1.2,-1.1,-.9]),[.01,-.03,.02]]
    c=np.c_[O.T@p[:,:3]@R.T,O.T@p[:,3]]
    np.testing.assert_allclose(spatial_connection_row(p,c,O,R),0,atol=2e-16)
    J=spatial_rotation_jacobian(c)
    h=2e-6
    for i in range(6):
        def shifted(sign):
            v=np.eye(3)[i%3]*sign*h
            ot=O@expm(cross_matrix(v)) if i<3 else O
            rt=expm(cross_matrix(v))@R if i>=3 else R
            return spatial_connection_row(p,c,ot,rt)
        np.testing.assert_allclose((shifted(1)-shifted(-1))/(2*h),J[:,i],atol=8e-11)


def test_spin_pullback_is_inverse_base_rotation_and_all_six_contacts_match():
    O=expm(cross_matrix([.2,-.1,.3]));R=expm(cross_matrix([-.1,.3,.2]))
    a=known_spin_gauge_factor(O,R)
    assert np.max(abs(a['original_Clifford_pullback_rows']))<7e-16
    h=2e-6
    for i in range(6):
        def shifted(sign):
            v=np.eye(3)[i%3]*sign*h
            ot=O@expm(cross_matrix(v)) if i<3 else O
            rt=expm(cross_matrix(v))@R if i>=3 else R
            return known_spin_gauge_factor(ot,rt)['known_middle128']
        np.testing.assert_allclose((shifted(1)-shifted(-1))/(2*h),
            a['known_middle_free_rotation_first128'][i],atol=2e-10)


@pytest.fixture(scope='module')
def actual_application():
    import json
    root=Path(__file__).resolve().parents[1]
    folder=root/'artifacts/muon_retained_response_20261018/inputs'
    md=json.loads((folder/'history_metadata.json').read_bytes());hist=[]
    for side in ('incoming','outgoing'):
        rows=md['sides'][side]
        with np.load(folder/(side+'_history.npz'),allow_pickle=False) as z:
            t=np.array([r['time'] for r in rows]);x=np.array([z[r['label']+'_raw_fields'] for r in rows]);dx=np.array([z[r['label']+'_raw_coordinate_time_derivative'] for r in rows])
        hist.append(recovered_export_history(root,side,t,x,dx)[0])
    with np.load(root/'artifacts/muon_d5_event_matching_20261019/formation_core/application.npz',allow_pickle=False) as z:
        delta=z['provisional_raw_normal_source_correction']
    coeff=[original_event_coefficients(h,0.,[np.pi/2],side=side,
        directions=corrected_original_event_source_directions(h,d,side=side))
        for h,d,side in zip(hist,delta,('parent','child'))]
    return spatial_bundle_application(*coeff,hist[1])


def test_actual_full_connection_source_rows_solve_with_field_response_not_trace_fit(actual_application):
    a,r=actual_application
    assert r['candidate_count']==4
    assert np.min(a['parent_weak_curvature_singular_values'])>1
    assert np.min(a['child_weak_curvature_singular_values'])>1
    value=np.max(abs(a['value_component_rows']),axis=1)
    assert np.count_nonzero(value>1e-4)==2
    assert np.count_nonzero(value<3e-11)==2
    np.testing.assert_array_equal(a['child_spatial_wall_field_raw_indices'],np.arange(168,180))
    for i in range(4):
        assert r['candidates'][i]['joint_row_rank']==12
        assert np.max(abs(a['source_component_rows_after'][i]))<2e-20
        assert r['candidates'][i]['candidate_selected_as_physical_map'] is False
    assert np.max(abs(a['source_component_rows_before'][2:]))>4e-6
    assert r['free_rotation_source_coordinates']==6
    assert r['initial_right_translation_parameters']==3
    assert r['physical_admission'] is False
    assert r['outer_Maxwell_field_stationarity_solved'] is False


def test_every_free_rotation_keeps_its_induced_child_field_column(actual_application):
    a,_=actual_application;B=a['child_spatial_wall_trace_pivot']
    for i,(O,R) in enumerate(zip(a['base_rotations'],a['gauge_rotations'])):
        p,c=a['parent_spatial_connection'],a['child_spatial_connection']
        target=c-spatial_connection_row(p,c,O,R).reshape(3,4)
        J=spatial_rotation_jacobian(target)
        raw=a['child_raw_field_free_rotation_coefficients'][i]
        np.testing.assert_allclose(J+B@raw[a['child_spatial_wall_field_raw_indices']],0,atol=1e-20)
        assert np.linalg.matrix_rank(np.c_[B,J])==12
