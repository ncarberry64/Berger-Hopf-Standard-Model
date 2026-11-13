from functools import lru_cache
import numpy as np

from bhsm.interface.muon_birth_chronological_boundary_action import retained_chronological_boundary_application
from bhsm.interface.muon_birth_chronological_normal_inertia import true_legendre_normal_trial
from bhsm.interface.muon_birth_chronological_normal_boundary_response import full_birth_trace_response,spatial_slice_normal_jacobi,mixed_canonical_far_response
from bhsm.interface.muon_birth_attached_phase import load_attached_endpoint


@lru_cache(maxsize=1)
def actual():
    a=retained_chronological_boundary_application('artifacts/muon_parent_gauge_geometry_correction_20261010/attached_phase_incoming_1steps_run_1')
    raw=load_attached_endpoint(a['receipt']['consumed_paired_endpoint_path'],side='incoming')['raw']
    b=true_legendre_normal_trial(a['action_hessians'][0],raw,a['representation'])
    return a,raw,b


def test_complete_internal_solve_keeps_all_original_equations_and_field_image():
    a,raw,b=actual();r=full_birth_trace_response(a['cell_hessians'][0],106,1,b['trial_trace'],b['literal_gauge_generators'][:106])
    assert r['original_action_block'].shape==(146,146)
    assert r['true_Lyy_and_all_Gauss_rows_retained'] and r['spectral_directions_removed']==0
    assert np.linalg.norm(r['birth_trace_lift'][38:102,2])>1
    assert np.linalg.norm(r['algebraic_lift'][:,2])>1
    np.testing.assert_allclose(r['trial_trace']@r['birth_trace_lift'],np.eye(3),rtol=0,atol=1e-10)
    assert np.max(abs(r['scaled_solve_residual']))<2e-8
    assert np.max(abs(r['frame_reactions']))<1e-12


def test_named_gauge_frames_do_not_select_a_different_normal_response():
    a,raw,b=actual();args=(a['cell_hessians'][0],106,1,b['trial_trace'],b['literal_gauge_generators'][:106])
    r=full_birth_trace_response(*args,frame='radial');c=full_birth_trace_response(*args,frame='complete')
    np.testing.assert_allclose(r['response'],c['response'],rtol=1e-11,atol=1e-6)
    assert np.max(abs(r['central_source_pairing']))==0
    assert not r['physical_far_face_selected']


def test_spatial_jacobi_cancels_the_first_log_squares_without_removing_time_contacts():
    a,raw,b=actual()
    m8=spatial_slice_normal_jacobi(raw,stratum='M8');m5=spatial_slice_normal_jacobi(raw,stratum='M5')
    for d in (m8,m5):
        assert d['constant_normal_J']==-(d['second_fundamental_squared']+d['spatial_Ric_normal_normal'])
        assert not d['full_formation_J_or_gamma_selected']
    assert m8['spatial_mean_curvature']==0
    assert m8['spatial_dimension']==6 and m5['spatial_dimension']==3
    # M5 is nonminimal: a signed area Hessian includes K^2 and temporal
    # contacts, so its substitution for this spatial Jacobi is prohibited.
    assert m5['spatial_mean_curvature']!=0


def test_mixed_canonical_reduction_removes_static_radial_gauge_by_literal_identity():
    a,raw,b=actual();r=mixed_canonical_far_response(a['action_hessians'][0],a['signed_step'],1,b,a['representation'])
    assert np.max(abs(r['solve_residual']))<1e-12
    assert np.max(abs(r['literal_gauge_Ward_image']))<2e-14
    assert np.max(abs(r['central_source_pairing']))==0
    assert np.max(abs(r['frame_reactions']))<1e-15
    assert np.max(abs(r['original_action_hessian'][:,r['static_central_radial_coordinate_indices']]))==0
    np.testing.assert_allclose(b['trial_trace']@r['final_face_lift'],np.eye(3),rtol=0,atol=5e-13)
    assert r['response'][2,2]<0  # evaluated sign; no positivity presumed
    assert r['spectral_directions_removed']==0 and not r['actual_E0_boundary_graph_selected']
