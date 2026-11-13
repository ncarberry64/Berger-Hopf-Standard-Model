from functools import lru_cache
import numpy as np

from bhsm.interface.muon_birth_chronological_boundary_action import retained_chronological_boundary_application
from bhsm.interface.muon_birth_chronological_normal_inertia import true_legendre_normal_trial,surface_weak_area_application


@lru_cache(maxsize=1)
def actual_application():
    return retained_chronological_boundary_application(
        'artifacts/muon_parent_gauge_geometry_correction_20261010/attached_phase_incoming_1steps_run_1')


def test_literal_gauge_generator_needs_the_nonzero_Higgs_velocity_lift():
    a=actual_application();b=true_legendre_normal_trial(a['action_hessians'][0],a['raw_chronological_midpoints'][0],a['representation'])
    assert np.max(abs(b['gauge_Ward_image']))<2e-13
    assert np.max(abs(b['gauge_source_pairing']))==0
    Z=b['literal_gauge_generators'].copy();Z[102:106]=0
    assert np.linalg.norm(b['legendre_saddle']@Z)>1e-5
    assert np.max(abs(b['frame_reactions']))<1e-15
    assert np.max(abs(b['solve_residual']))<2e-9


def test_named_temporal_and_radial_frames_give_the_same_true_Lyy_trial():
    a=actual_application();args=(a['action_hessians'][0],a['raw_chronological_midpoints'][0],a['representation'])
    t=true_legendre_normal_trial(*args,frame='temporal');r=true_legendre_normal_trial(*args,frame='radial')
    np.testing.assert_allclose(t['response'],r['response'],rtol=3e-12,atol=1e-10)
    assert t['full_true_Lyy_retained'] and not t['zero_Lyy_projection_used']
    assert t['spectral_directions_removed']==0
    assert np.max(abs(t['full_algebraic_residual']))<1e-10
    np.testing.assert_allclose(t['trial_trace']@t['velocity_lift'],np.eye(3),rtol=0,atol=5e-12)


def test_proper_clock_conversion_does_not_assign_unit_inertia_or_a_mode():
    a=actual_application();b=true_legendre_normal_trial(a['action_hessians'][0],a['raw_chronological_midpoints'][0],a['representation'])
    assert b['normal_proper_clock_inertia']==b['induced_lapse']*b['normal_coordinate_time_inertia']
    assert np.linalg.norm(b['algebraic_lift'][:,2])>1
    assert not b['physical_unit_inertia_normalization'] and not b['physical_mode_selected']
    assert b['normal_trace_kind']=='proper'
    assert np.linalg.norm(b['proper_normal_trace'][:37])>0


def test_unit_wall_normal_projection_retains_the_geometry_motion():
    from bhsm.interface.muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
    from bhsm.interface.muon_birth_trace_enriched_action import generic_coordinate_lift
    a=actual_application();raw=a['raw_chronological_midpoints'][0];rep=a['representation']
    b=true_legendre_normal_trial(a['action_hessians'][0],raw,rep)
    w=intrinsic_m4_weight_jet(12,raw[:37],raw[37:74],raw[74:98],source_value=raw[98],source_rate=raw[99])
    c=generic_coordinate_lift(rep['gauge_labels']); d=c['lift'][:100,:c['x_count']]
    C,N,beta=(w['fields'][name].value for name in ('C','N','beta'))
    U=w['U'].value; z=np.sqrt(1-U*U)
    normal=np.array([U/N,1/C-beta*U/N])/z
    metric=np.array([[N*N-C*C*beta*beta,-C*C*beta],[-C*C*beta,-C*C]])
    np.testing.assert_allclose(normal@metric@normal,-1,rtol=0,atol=4e-16)
    tangent=np.array([1.,w['wall_rate'].value])/w['induced_lapse'].value
    np.testing.assert_allclose(normal@metric@tangent,0,rtol=0,atol=2e-16)
    expected=-(normal@metric[:,1])*(w['wall'].gradient@d)
    np.testing.assert_allclose(b['proper_normal_trace'],expected,rtol=5e-16,atol=1e-16)
    np.testing.assert_allclose(b['trial_trace'][2]@b['velocity_lift'],[0,0,1],rtol=0,atol=3e-12)


def test_the_two_owned_area_strata_keep_densities_dimensions_and_path_contacts():
    a=actual_application();args=(a['raw_chronological_midpoints'][0],a['representation'])
    m8=surface_weak_area_application(*args,stratum='M8');m5=surface_weak_area_application(*args,stratum='M5')
    assert m8['worldvolume_dimension']==7 and m5['worldvolume_dimension']==4
    assert m8['gamma_equation']=='gamma=alpha_FSC*c^(-7/2)'
    assert m5['gamma_equation']=='gamma=alpha_FSC*c^(-4/2)'
    assert m8['area_value_per_gamma']<0 and m5['area_value_per_gamma']<0
    for b in (m8,m5):
        assert np.linalg.norm(b['normal_value_rate_second_per_gamma'])>0
        assert b['raw_area_Hessian_equals_Jacobi_not_claimed']
        assert b['nonminimal_path_and_temporal_contacts_retained']
        assert not b['physical_gamma_or_c_selected']
