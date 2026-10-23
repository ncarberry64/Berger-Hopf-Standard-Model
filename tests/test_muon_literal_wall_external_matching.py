from pathlib import Path
import numpy as np
from bhsm.interface.muon_literal_wall_external_matching import physical_y_wall_current,paired_physical_y_wall_current,full_c6_positive_pole_jet,normalized_pole_spin_covectors
ROOT=Path(__file__).resolve().parents[1]


def inputs():
    with np.load(ROOT/'artifacts/muon_literal_euclidean_wall_y_response_20261011/run_1/incoming_coefficients.npz',allow_pickle=False)as a:c={k:a[k].copy()for k in a.files}
    with np.load(ROOT/'artifacts/muon_literal_euclidean_wall_action_20261011/run_2/incoming_cells_2_field_original_action_Green.npz',allow_pickle=False)as a:g=a['original_action_Green'].copy()
    with np.load(ROOT/'artifacts/muon_literal_euclidean_wall_action_20261011/run_2/incoming_family_1_cells_2_current.npz',allow_pickle=False)as a:direct=a['open_Gaussian_current'].copy()
    with np.load(ROOT/'artifacts/muon_coupled_lambda_local_matching_20261011/run_2/application.npz',allow_pickle=False)as a:h=a['original_incoming_raw_fields'][260:264].copy()
    return c,g,direct,h[:2]+1j*h[2:]


def test_exact_physical_Y_reconstructs_original_whole_current():
    c,g,direct,h=inputs();a=physical_y_wall_current(c,g,y=c['family_Y'][0])
    assert np.linalg.norm(a['self_energy_zero']-direct)<1e-18
    assert a['original_fermion_source_residual_max']<1e-10


def test_actual_shared_difference_retains_all_literal_polynomial_contacts():
    c,g,direct,h=inputs();a=paired_physical_y_wall_current(c,g,y_middle=c['family_Y'][0],y_light=c['family_Y'][1])
    assert np.linalg.norm(a['paired_self_energy_zero']-c['paired_current_coefficients_through_order'])<2e-22
    assert np.linalg.norm(a['paired_self_energy_first']-c['paired_energy_coefficients_through_order'])<2e-26
    assert np.linalg.norm(a['telescoping_vs_raw_current_difference'])<1e-19


def test_full_positive_pole_return_and_residue_match_original_C6_pencil():
    c,g,direct,h=inputs();s=physical_y_wall_current(c,g,y=c['family_Y'][0]);m=.002145068448715311
    app=lambda E:full_c6_positive_pole_jet(h,s['self_energy_zero'],s['self_energy_first'],family=1,matched_mass_action=E)
    a=app(m);eps=1e-7
    fd=(app(m+eps)['matched_positive_inverse']-app(m-eps)['matched_positive_inverse'])/(2*eps)
    assert np.linalg.norm(fd-a['matched_positive_energy_derivative'])<1e-8
    assert np.linalg.norm(a['full_C6_to_positive_inverse_residual'])<1e-8
    assert np.linalg.norm(a['derivative_dual_identity_residual'])<1e-14
    assert np.linalg.norm(a['full_complement_return'])>0
    z=.003+.001j;G=a['full_C6_energy_derivative'];B=a['fixed_Y_operator']+s['self_energy_zero']
    reconstructed=sum(r/(z-e)for r,e in zip(a['local_affine_pencil_residue_matrices'],a['local_affine_pencil_poles']))
    assert np.linalg.norm(reconstructed-np.linalg.inv(z*G-B))<1e-8


def test_mass_matching_preserves_the_noncentral_complex_remnant():
    c,g,direct,h=inputs();s=physical_y_wall_current(c,g,y=c['family_Y'][0]);a=full_c6_positive_pole_jet(h,s['self_energy_zero'],s['self_energy_first'],family=1,matched_mass_action=.002145068448715311)
    assert np.array_equal(a['isotropic_mass_matching_load']*np.eye(2)+a['remaining_complex_spin_pole_matrix'],a['matched_positive_inverse'])
    assert np.linalg.norm(a['remaining_complex_spin_pole_matrix'])>0
    assert not a['Yukawa_replaced_or_mass_counterterm_applied']


def test_full_return_normalized_spin_dual_agrees_with_uncompressed_action():
    c,g,direct,h=inputs();s=physical_y_wall_current(c,g,y=c['family_Y'][0]);a=full_c6_positive_pole_jet(h,s['self_energy_zero'],s['self_energy_first'],family=1,matched_mass_action=.002145068448715311)
    v=normalized_pole_spin_covectors(a,electric_charge=.3028221207369548)
    from bhsm.interface.muon_magnetic_open_lepton_vertex import PAULI
    # Use the actual full six-component field/current as the test direction.
    actual=s['self_energy_zero'];left=v['normalized_literal_left_pole_test'];right=v['normalized_right_pole_test']
    literal=np.array([a['matched_mass_action']/.3028221207369548*np.trace(p@left@actual@right)for p in PAULI])
    dual=np.einsum('kij,ij->k',v['full_C6_magnetic_spin_tensor_weight'],actual)
    assert np.linalg.norm(literal-dual)<1e-20
    assert np.linalg.norm(v['pole_current_normalization_residual'])<2e-14
    assert np.linalg.norm(v['normalized_pole_matching_remainder'])>0


def test_actual_Hcan_lower_order_body_is_retained_before_pole_reduction():
    from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase,profile_preserving_lepton_sample
    c,g,direct,h=inputs();phase=load_profile_preserving_phase('artifacts/muon_finite_normal_phase_20261011/incoming_run_1')
    operator=profile_preserving_lepton_sample(phase,0.)['operator'];ids=np.array([2,3,8,9,14,15]);body=operator['H_can'][np.ix_(ids,ids)]
    s=physical_y_wall_current(c,g,y=c['family_Y'][0]);m=.0021449028310434885
    a=full_c6_positive_pole_jet(operator['H'],s['self_energy_zero'],s['self_energy_first'],family=1,matched_mass_action=m,tree_body=body)
    expected=m*(np.eye(6)-s['self_energy_first'])-body-s['self_energy_zero']
    assert np.array_equal(a['full_C6_inverse_symbol'],expected)
    assert np.linalg.norm(body-a['fixed_Y_operator'])>1
    assert a['same_background_constant_angular_tree_body_retained']
    assert not a['constant_angular_kernel_to_normal_Wilson_symbol_identified']
