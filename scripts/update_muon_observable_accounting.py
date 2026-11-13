"""Maintain the single active muon contribution/error table from frozen inputs.

This working accounting does not promote a finite action application to
a physical native contribution. Completed matching inputs and projected
native results can replace ONLY their affected consumer rows.
"""
from pathlib import Path
from hashlib import sha256
import argparse,json,math
ROOT=Path(__file__).resolve().parents[1]
LOCAL='artifacts/muon_calibrated_finite_projection_ledger_20261010/run_1/finite_projection_ledger.json'


def materialize(output):
    out=ROOT/output;out.mkdir(parents=True,exist_ok=True)
    p=ROOT/LOCAL;local=json.loads(p.read_bytes());refs={LOCAL:sha256(p.read_bytes()).hexdigest()}
    rows=[]
    error_keys=(('metrological_inputs',),('QED_coefficients_and_truncation','metrological_inputs'),
        ('weak_source_uncertainty_and_mass_approximation','weak_decay_estimated_standard_uncertainty','weak_decay_omitted_order_estimate','gamma_Z_correlator_standard_uncertainty','metrological_inputs'),
        ('hadronic','hadronic_metrology_derivative_scope','metrological_inputs'),
        ('hadronic','hadronic_metrology_derivative_scope','metrological_inputs'),('top_current','metrological_inputs'),
        ('bosonic_logarithm','metrological_inputs'),('finite_transverse_W_Hgamma','metrological_inputs'))
    for row,keys in zip(local['contribution_table'],error_keys,strict=True):
        rows.append(dict(component=row['component'],a_mu=row['value'],status='EVALUATED',
            owner=row['owner'],already_in_local_subtotal=True,
            overlap_rule='count once in the matched local ledger; its same-background native counterpart is subtracted from the native result',
            error_objects={key:local['errors'][key]for key in keys},
            shared_error_objects_are_not_independent_per_row_allowances=True,
            uncertainty_contract='joint dependency/uncertainty object in the frozen local ledger; component sensitivities added before correlated propagation'))
    subtotal=math.fsum(row['a_mu']for row in rows)
    if abs(subtotal-.0011659186179552334)>2e-18:raise ValueError('frozen local accounting unexpectedly changed')
    rows.append(dict(component='remaining matched finite bosonic weak and quark Hgamma/HZ sectors',a_mu=None,status='UNEVALUATED',
        owner='same literal action and local matching complement of the evaluated EW rows',
        already_in_local_subtotal=False,overlap_rule='only the omitted complement of the evaluated local weak rows; its same-background native reference is subtracted once',
        error_objects={key:local['errors'][key]for key in ('weak_unexecuted_sectors','full_bosonic_finite_remainder')},
        uncertainty_contract='4.292e-10 is a conditional finite-order allowance estimate under minimal matching; it does not enclose an arbitrary absolute quark-Y completion'))
    rows.append(dict(component='disjoint same-background native Pauli remainder',a_mu=None,status='ACTIVE_ACTION_APPLICATION',
        owner='corrected joined classical/Clifford/field action with its physical external pole and branch-birth cutoff',
        overlap_rule='project the completed corrected native combination minus its same-background matched local reference exactly once; strong pieces remain in this row or in the explicitly matched hadronic rows, never both',
        consumer='signed charge-normalized and LSZ-normalized soft-transfer Pauli derivative',
        uncertainty_contract='numerical, continuum/domain, response, pole/charge/residue matching, physical cutoff/source jets, overlap and soft-limit errors must propagate through the same projected combination'))
    # Evidence of the active combined action, not separate contributions to
    # a_mu and not a second table of invented zero/null component values.
    evidence={}
    for key,path in(
        ('literal_higgs_inverse','artifacts/muon_literal_euclidean_higgs_green_20261011/run_1/result.json'),
        ('same_background_clock_measure_mean','artifacts/muon_transported_chronological_heat_mean_20261011/run_2/result.json'),
        ('same_clifford_contact_both_insertions','artifacts/muon_reduced_joined_euclidean_source_heat_20261011/run_1/result.json'),
        ('actual_connector_spectral_returns','artifacts/muon_euclidean_spectral_corner_gluing_20261011/run_1/result.json'),
        ('joint_natural_wall_common_Y_response','artifacts/muon_literal_euclidean_wall_y_response_20261011/run_1/result.json'),
        ('source_directed_original_wall_current','artifacts/muon_source_directed_wall_current_20261011/run_1/result.json'),
        ('external_pole_and_graph_resolved_matching','artifacts/muon_literal_wall_external_matching_20261011/run_2/result.json'),
        ('full_two_spin_momentum_and_residue_jet','artifacts/muon_literal_wall_matching_state_jet_20261011/run_1/result.json'),
        ('four_placement_magnetic_matching_incoming','artifacts/muon_literal_wall_magnetic_matching_20261011/incoming_run_1/result.json'),
        ('same_current_Wilson_first_germ','artifacts/muon_literal_wall_wilson_germ_20261011/run_1/result.json'),
        ('complete_point_Wilson_E_p_Ep_jets','artifacts/muon_literal_wall_point_wilson_jet_20261011/run_1/result.json'),
        ('same_radial_spatial_Wilson_quadratic','artifacts/muon_point_radial_wilson_quadratic_20261011/run_1/result.json'),
        ('same_current_scalar_matching_and_complete_C_covectors','artifacts/muon_normal_matched_current_covectors_20261011/run_2/result.json'),
        ('complete_incoming_C_projection','artifacts/muon_complete_C_normal_projection_20261011/incoming_run_1/result.json'),
        ('complete_C_photon_adjoint_and_all_closed_leptons','artifacts/muon_normal_matched_photon_current_20261011/run_1/result.json'),
        ('same_observation_owned_decay_tensor','artifacts/muon_owned_observation_lifetime_20261011/run_1/result.json'),
        ('corrected_full_wall_reached_return_heat','artifacts/muon_full_wall_photon_heat_kernel_20261011/run_4/result.json'),
        ('all_closed_lepton_families_for_each_outer_current','artifacts/muon_full_wall_lepton_sector_heat_20261011/run_1/result.json'),
        ('corrected_incoming_magnetic_source_contact','artifacts/muon_literal_wall_angular_contact_repair_20261011/incoming_run_1/result.json'),
        ('corrected_outgoing_magnetic_source_contact','artifacts/muon_literal_wall_angular_contact_repair_20261011/outgoing_run_1/result.json'),
        ('source_specific_original_field_own_mean','artifacts/muon_literal_wall_contracted_mean_20261011/incoming_middle_mass_axis0_run_1/result.json'),
        ('source_specific_all_lepton_field_heat_mean','artifacts/muon_wall_field_heat_mean_20261011/incoming_middle_mass_axis0_run_1/result.json'),
        ('corrected_reflected_connector_action_and_returns','artifacts/muon_reflected_clifford_connector_action_20261011/run_1/result.json'),
        ('reached_zero_source_all_lepton_quantum_field_mean','artifacts/muon_wall_quantum_field_mean_20261011/run_1/result.json'),
        ('reached_zero_source_mean_Higgs_frame_contact','artifacts/muon_quantum_field_higgs_frame_contact_20261011/run_1/result.json'),
        ('reached_zero_source_mean_gauge_invariant_curvature','artifacts/muon_quantum_field_curvature_readout_20261011/run_3/result.json'),
        ('complete_first_Moyal_and_left_gradient','artifacts/muon_literal_wall_left_gradient_20261011/run_1/result.json'),
        ('complete_unsubtracted_C6_local_pole_residue','artifacts/muon_full_c6_affine_normal_poles_20261011/run_1/result.json'),
        ('complete_C6_band_C_covectors','artifacts/muon_affine_band_current_covectors_20261011/run_1/result.json'),
        ('complete_incoming_C_T_band_application','artifacts/muon_affine_complete_C_T_readout_20261011/incoming_run_1/result.json'),
        ('complete_outgoing_C_T_band_application','artifacts/muon_affine_complete_C_T_readout_20261011/outgoing_run_1/result.json'),
        ('complete_C6_band_energy_motion','artifacts/muon_affine_band_energy_motion_20261011/run_1/result.json'),
        ('both_external_energy_leg_contacts','artifacts/muon_affine_band_source_energy_20261011/run_1/result.json'),
        ('incoming_full_ordered_momentum_source','artifacts/muon_literal_wall_wall_image_contraction_20261011/incoming_momentum_run_2/result.json'),
        ('outgoing_full_ordered_momentum_source','artifacts/muon_literal_wall_wall_image_contraction_20261011/outgoing_momentum_run_2/result.json'),
        ('continued_local_weak_strong_composition_and_source_germs','artifacts/muon_continued_local_square_20261011/birth_run_1/result.json'),
        ('restored_birth_window_heat','artifacts/muon_restored_clifford_heat_cotangent_20261011/birth_refinement_2_run_1/result.json'),
        ('whole_chronological_reflected_pencil','artifacts/muon_chronological_clifford_graph_20261011/run_1/result.json'),
        ('whole_chronological_low_spectral_modes','artifacts/muon_chronological_spectral_branch_20261011/low_n0_run_1/result.json'),
        ('whole_chronological_negative_spectral_modes','artifacts/muon_chronological_spectral_branch_20261011/negative_n0_run_1/result.json'),
        ('whole_chronological_partial_low_heat_cotangent','artifacts/muon_chronological_low_heat_cotangent_20261011/tau_n0_run_1/result.json'),
        ('whole_classical_nonlinear_stationarity','artifacts/muon_chronological_n0_nonlinear_newton_20261011/run_1/result.json'),
        ('complete_both_leg_C_T_external_energy_partial','artifacts/muon_affine_complete_C_T_energy_readout_20261011/run_1/result.json'),
        ('owned_common_A_real_native_reference','artifacts/muon_owned_native_product_connection_20261011/run_1/result.json'),
        ('owned_common_A_real_native_reference_heat','artifacts/muon_owned_native_product_heat_20261011/run_1/result.json'),
        ('native_local_current_and_coupled_scalar_overlap_matching','artifacts/muon_native_local_overlap_matching_20261011/run_3/result.json'),
        ('common_global_n1_current_action','artifacts/muon_chronological_n1_field_action_20261011/run_1/result.json'),
        ('common_global_current_body_and_first_germ','artifacts/muon_chronological_current_body_20261011/run_1/result.json'),
        ('common_global_incoming_muon_source_transfer_and_matching_forms','artifacts/muon_chronological_current_matching_20261011/incoming_family_1_run_1/result.json'),
        ('common_global_outgoing_muon_source_transfer_and_matching_forms','artifacts/muon_chronological_current_matching_20261011/outgoing_family_1_run_1/result.json'),
        ('common_global_incoming_electron_source_transfer_and_matching_forms','artifacts/muon_chronological_current_matching_20261011/incoming_family_2_run_1/result.json'),
        ('common_global_outgoing_electron_source_transfer_and_matching_forms','artifacts/muon_chronological_current_matching_20261011/outgoing_family_2_run_1/result.json'),
        ('common_global_actual_birth_current_adjoint_source_images','artifacts/muon_chronological_birth_current_images_20261011/run_1/result.json'),
        ('common_global_actual_both_external_energy_legs','artifacts/muon_chronological_current_energy_20261011/incoming_family_1_run_1/result.json'),
        ('common_global_outgoing_both_external_energy_legs','artifacts/muon_chronological_current_energy_20261011/outgoing_family_1_run_1/result.json'),
        ('common_global_actual_endpoint_and_nonstationary_amputation','artifacts/muon_chronological_current_amputation_20261011/run_1/result.json'),
        ('common_global_coupled_radial_source_and_adjoint','artifacts/muon_common_graph_radial_matching_20261011/run_1/result.json'),
        ('corrected_retarded_scalar_path_and_residues','artifacts/muon_causal_radial_matching_20261011/run_1/result.json'),
        ('same_base_unsquared_native_current_range_match','artifacts/muon_native_unsquared_domain_matching_20261011/run_1/result.json'),
        ('actual_global_coupled_current_adjoint_native_source_match','artifacts/muon_global_current_native_matching_20261011/incoming_family_1_column208_run_1/result.json'),
        ('common_global_actual_native_analytic_source_return','artifacts/muon_native_current_range_return_20261011/run_1/result.json'),
        ('common_global_actual_shifted_boundary_and_forced_form_core_return','artifacts/muon_shifted_boundary_source_20261011/run_1/result.json'),
        ('common_global_incoming_coupled_GG_GH_HG_HH','artifacts/muon_chronological_common_y_current_20261011/incoming_run_1/result.json'),
        ('common_global_outgoing_coupled_GG_GH_HG_HH','artifacts/muon_chronological_common_y_current_20261011/outgoing_run_1/result.json'),
        ('common_global_incoming_actual_transported_288_current','artifacts/muon_chronological_cauchy_trace_current_20261011/incoming_run_1/result.json'),
        ('common_global_outgoing_actual_transported_288_current','artifacts/muon_chronological_cauchy_trace_current_20261011/outgoing_run_1/result.json'),
        ('common_global_charge_transport_and_source_chart_weak_residual','artifacts/muon_common_domain_charge_transport_20261011/run_3/result.json'),
        ('common_global_corrected_source_clock_charge_projection','artifacts/muon_common_domain_charge_source_clock_20261011/run_1/result.json'),
        ('common_global_full_complex_child_action_constraints','artifacts/muon_holomorphic_child_terminal_20261011/run_2/result.json'),
        ('common_global_full_complex_terminal_stress_attribution','artifacts/muon_complex_terminal_action_sectors_20261011/run_1/result.json'),
        ('common_global_full_complex_canonical_compatibility_application','artifacts/muon_complex_canonical_compatibility_20261011/run_1/result.json'),
        ('common_global_safeguarded_full_canonical_constraints','artifacts/muon_safeguarded_complex_constitutive_20261011/resumed_run_1/result.json'),
        ('common_global_exact_field_elimination_and_remaining_geometry','artifacts/muon_reduced_complex_canonical_geometry_20261011/run_1/result.json'),
        ('common_global_exact_material_rate_action_constraints','artifacts/muon_material_rate_canonical_geometry_20261011/run_2/result.json'),
        ('common_global_material_rate_action_continuation','artifacts/muon_material_rate_canonical_geometry_20261011/continued_run_1/result.json'),
        ('common_global_literal_high_precision_constitutive_gradient','artifacts/muon_high_precision_constitutive_gradient_20261012/run_1/result.json'),
        ('common_global_compatible_original_canonical_launch','artifacts/muon_high_precision_canonical_compatibility_20261012/run_1/result.json'),
        ('common_global_original_complex_canonical_exterior_step','artifacts/muon_complex_canonical_exterior_step_20261012/run_1/result.json'),
        ('common_global_true_original_canonical_endpoint','artifacts/muon_complex_canonical_endpoint_20261012/run_1/result.json'),
        ('common_global_precise_original_canonical_exterior_step','artifacts/muon_precise_complex_canonical_exterior_step_20261012/run_1/result.json'),
        ('common_global_second_true_original_canonical_endpoint','artifacts/muon_complex_canonical_endpoint_20261012/continued_run_1/result.json'),
        ('common_global_complex_area_and_clock_work','artifacts/muon_complex_endpoint_area_clock_20261012/run_1/result.json'),
        ('common_global_coupled_reference_source_control','artifacts/muon_canonical_descriptor_frame_application_20261012/run_1/result.json'),
        ('common_global_reference_control_on_solved_path','artifacts/muon_canonical_descriptor_solved_path_20261012/run_1/result.json'),
        ('common_global_actual_complex_two_arm_action_reset_source','artifacts/muon_holomorphic_two_arm_reset_20261012/run_1/result.json'),
        ('common_global_full_coupled_phase_trace_and_area_source','artifacts/muon_coupled_complex_two_arm_reset_20261012/run_1/result.json'),
        ('common_global_continued_original_two_arm_reset_equations','artifacts/muon_coupled_complex_two_arm_reset_20261012/continued_run_1/result.json'),
        ('common_global_exact_stored_reset_port_attribution','artifacts/muon_exact_stored_reset_projection_20261012/run_1/result.json'),
        ('common_global_actual_canonical_momenta_and_trace_return','artifacts/muon_coupled_reset_canonical_trace_20261012/run_1/result.json'),
        ('common_global_paired_local_normal_action_and_joint_clock','artifacts/muon_complex_paired_normal_action_20261012/run_1/result.json'),
        ('common_global_moving_normal_and_full_Jacobi_response','artifacts/muon_complex_normal_trace_motion_20261012/run_1/result.json'),
        ('common_global_original_reset_trial_domain_and_force_images','artifacts/muon_reset_normal_trial_domain_20261012/run_1/result.json'),
        ('common_global_original_reset_trial_role_and_source_correction','artifacts/muon_reset_trial_role_application_20261012/run_3/result.json'),
        ('common_global_endpoint_second_source_quality_application','artifacts/muon_endpoint_second_domain_germ_20261012/run_1/result.json'),
        ('common_global_per_arm_canonical_normal_and_area_source_admission','artifacts/muon_per_arm_canonical_source_20261012/run_1/result.json'),
        ('common_global_admitted_parent_area_source_action_component','artifacts/muon_admitted_parent_source_germ_20261012/run_1/result.json'),
        ('common_global_full_moving_reference_field_trace_source','artifacts/muon_moving_reference_trace_source_20261012/run_1/result.json'),
        ('common_global_bounded_stored_admission_correction','artifacts/muon_stored_admission_correction_20261012/run_1/result.json'),
        ('common_global_changing_arm_source_application','artifacts/muon_changing_canonical_source_20261012/run_3/result.json'),
        ('common_global_corrected_birth_source_endpoint','artifacts/muon_corrected_birth_source_endpoint_20261012/run_1/result.json'),
        ('common_global_changing_source_action_accuracy','artifacts/muon_changing_source_action_accuracy_20261012/run_1/result.json'),
        ('common_global_incoming_normal_full18_current_source','artifacts/muon_holomorphic_current_source_20261012/incoming_normal_basis_run_1/result.json'),
        ('common_global_outgoing_normal_full18_current_source','artifacts/muon_holomorphic_current_source_20261012/outgoing_normal_basis_run_1/result.json'),
        ('common_global_incoming_area_full18_current_source','artifacts/muon_holomorphic_current_source_20261012/incoming_area_source_run_1/result.json'),
        ('common_global_outgoing_area_full18_current_source','artifacts/muon_holomorphic_current_source_20261012/outgoing_area_source_run_1/result.json'),
        ('common_global_incoming_normal_unit_em_current','artifacts/muon_holomorphic_current_source_20261012/incoming_normal_basis_em_current_run_1/result.json'),
        ('common_global_outgoing_normal_unit_em_current','artifacts/muon_holomorphic_current_source_20261012/outgoing_normal_basis_em_current_run_1/result.json'),
        ('common_global_incoming_area_unit_em_current','artifacts/muon_holomorphic_current_source_20261012/incoming_area_source_em_current_run_1/result.json'),
        ('common_global_outgoing_area_unit_em_current','artifacts/muon_holomorphic_current_source_20261012/outgoing_area_source_em_current_run_1/result.json'),
        ('common_global_incoming_normal_signed_magnetic_action','artifacts/muon_holomorphic_n1_magnetic_action_20261012/incoming_normal_basis_run_1/result.json'),
        ('common_global_outgoing_normal_signed_magnetic_action','artifacts/muon_holomorphic_n1_magnetic_action_20261012/outgoing_normal_basis_run_1/result.json'),
        ('common_global_incoming_area_signed_magnetic_action','artifacts/muon_holomorphic_n1_magnetic_action_20261012/incoming_area_source_run_1/result.json'),
        ('common_global_outgoing_area_signed_magnetic_action','artifacts/muon_holomorphic_n1_magnetic_action_20261012/outgoing_area_source_run_1/result.json'),
        ('common_global_outgoing_normal_magnetic_mixed_action','artifacts/muon_holomorphic_n1_magnetic_operands_20261012/outgoing_normal_basis_run_1/result.json'),
        ('common_global_outgoing_area_magnetic_mixed_action','artifacts/muon_holomorphic_n1_magnetic_operands_20261012/outgoing_area_source_run_1/result.json'),
        ('common_global_outgoing_normal_complete_quadratic_field_direction','artifacts/muon_holomorphic_n1_magnetic_quadratic_action_20261012/outgoing_normal_basis_run_1/result.json'),
        ('common_global_outgoing_area_complete_quadratic_field_direction','artifacts/muon_holomorphic_n1_magnetic_quadratic_action_20261012/outgoing_area_source_run_1/result.json'),
        ('common_global_outgoing_n3_n4_magnetic_operator_action','artifacts/muon_holomorphic_n3_magnetic_return_20261012/outgoing_normal_basis_run_1/result.json'),
        ('common_global_actual_magnetic_birth_constraint_roles','artifacts/muon_holomorphic_magnetic_birth_matching_20261012/run_1/result.json'),
        ('common_global_inherited_source_on_child_action_and_current','artifacts/muon_holomorphic_magnetic_inherited_cauchy_20261012/run_1/result.json'),
        ('common_global_complete_inherited_magnetic_endpoint_cotangent','artifacts/muon_inherited_magnetic_endpoint_cotangent_20261012/run_1/result.json'),
        ('common_global_one_sided_source_on_corner_returns','artifacts/muon_holomorphic_magnetic_source_corner_20261012/run_3/result.json'),
        ('common_global_inherited_source_on_combined_weak_action','artifacts/muon_inherited_magnetic_weak_combination_20261012/run_3/result.json'),
        ('common_global_inherited_magnetic_unsquared_pure_trace','artifacts/muon_inherited_magnetic_pure_trace_20261012/run_1/result.json'),
        ('common_global_unsquared_forced_boundary_and_direct_current_source','artifacts/muon_unsquared_forced_boundary_attachment_20261012/run_1/result.json'),
        ('common_global_exact_explicit_inherited_clock_contact','artifacts/muon_holomorphic_child_clock_application_20261011/run_1/result.json'),
        ('common_global_initial_canonical_radial_return','artifacts/muon_initial_canonical_radial_return_20261011/run_1/result.json'),
        ('common_global_causal_impulse_laplace_and_end_contacts','artifacts/muon_global_causal_laplace_response_20261011/run_2/result.json'),
        ('common_global_causal_scalar_matching_same_clock_overlap','artifacts/muon_global_scalar_matching_weight_20261011/run_3/result.json'),
        ('common_global_boundary_both_source_energy_and_operator_contacts','artifacts/muon_boundary_energy_contacts_20261011/run_1/result.json'),
        ('common_global_actual_birth_density_and_clock_origin_reset','artifacts/muon_birth_external_trace_chart_20261011/run_1/result.json'),
        ('corrected_native_dual_density_graph','artifacts/muon_native_dual_density_graph_20261011/run_1/result.json'),
        ('completed_corrected_candidate_heat_production_paused','artifacts/muon_transported_native_heat_20261011/run_1/result.json'),
        ('scalar_residue_and_radial_overlap_tail_application','artifacts/muon_native_radial_overlap_tail_20261011/run_1/result.json'),
        ('local_fixed_Y_matching_load_diagnostic','artifacts/muon_local_matching_load_band_20261011/run_1/result.json'),
        ('same_observation_leading_mass_decay_matching_residual','artifacts/muon_same_observation_matching_order_20261011/run_1/result.json'),
        ('separate_child_plus_action_contractions','artifacts/muon_child_plus_normal_action_contractions_20261011/run_1/result.json'),
        ('changed_lambda_gamma_original_coupled_base','artifacts/muon_coupled_birth_gamma_response_20261011/run_2/result.json'),
        ('changed_lambda_gamma_same_base_normal_contractions','artifacts/muon_gamma_matched_normal_contractions_20261011/run_2/result.json'),
        ('full_tensor_temporal_lifetime_equation','artifacts/muon_temporal_tensor_lifetime_matching_20261011/run_1/result.json')):
        q=ROOT/path
        if q.exists():
            h=sha256(q.read_bytes()).hexdigest();refs[path]=h;record=json.loads(q.read_bytes())
            evidence[key]=dict(path=path,sha256=h,classification=record['classification'],
                role='evaluated consumer application at its declared domain; not an independently additive a_mu contribution')
            # Prefixes also label local reset/face applications. Assign the
            # chronological fallback only to its explicit producer domains,
            # before the component-specific descriptions below.
            if key.startswith('common_global_'):
                evidence[key]['matching_scope']='evaluated component at the exact domain and parameter scope of its linked result; a physical branch, exterior pole, gamma/cutoff, charge/LSZ factor or Pauli normalization is not inferred'
                if path.split('/')[1] in {
                    'muon_chronological_n1_field_action_20261011',
                    'muon_chronological_current_body_20261011',
                    'muon_chronological_current_matching_20261011',
                    'muon_chronological_birth_current_images_20261011',
                    'muon_chronological_current_energy_20261011',
                    'muon_chronological_current_amputation_20261011',
                    'muon_chronological_common_y_current_20261011',
                    'muon_chronological_cauchy_trace_current_20261011',
                    'muon_common_domain_charge_transport_20261011',
                    'muon_common_domain_charge_source_clock_20261011',
                    'muon_global_causal_laplace_response_20261011',
                    'muon_global_scalar_matching_weight_20261011',
                }:
                    evidence[key]['matching_scope']='same converged classical base and corrected1151-trace chronological action, with both exact angular spectators, all original Gauss/frame/corner/final rows and literal source transpose. The complete computational source transfer and separate Gram/body forms do not assign an exterior pole, physical charge/body/LSZ factor or a measured mass/lifetime scale.'
            if key in ('common_global_actual_complex_two_arm_action_reset_source','common_global_full_coupled_phase_trace_and_area_source','common_global_continued_original_two_arm_reset_equations'):
                evidence[key]['matching_scope']='literal complex full536 parent/child action and original226 reset rows at the held affine parent and compatible child. Full292 Legendre/302 trace/frame projection retains Lyy, all analytic-dual source contacts and named frame reactions. The old y-held lift is not the full algebraic response. These are candidate action applications; the held parent is not a solved physical parent, and neither the physical first hit, exterior pole, gamma/cutoff nor Pauli normalization is selected.'
                evidence[key]['error_scope']='actual original reset residual and binary full phase/adjoint/area-source checks; small matrix residuals do not bound physical matching or native Pauli error'
            if key=='common_global_unsquared_forced_boundary_and_direct_current_source':
                evidence[key]['matching_scope']='actual complete reached n0+n2 induced-H source/transpose application on the retained column208 current. The full boundary composition is Gamma=Bi+Bf U, f=b-Bf r, L_eff=Li+Lf U, c_eff=c+Lf r. No arbitrary physical Bi/Bf or pole member is selected. The extra square final restriction remains distinct from the first-order exterior domain.'
                evidence[key]['source_scope']='executed source-only energy derivative on fixed weak operator and square core, with actual source/target phase contacts; the generic consumer requires every supplied operator, energy/magnetic, source and domain jet. Missing total physical jets are not assigned zero.'
                evidence[key]['recovery_sign']='core current=original unsquared current+p.T r_D; original unsquared current=core current-p.T r_D; the forced return/range source is counted once'
            if key in ('common_global_paired_local_normal_action_and_joint_clock','common_global_moving_normal_and_full_Jacobi_response','common_global_original_reset_trial_domain_and_force_images','common_global_original_reset_trial_role_and_source_correction'):
                evidence[key]['matching_scope']='evaluated trial-normal action, proper clock, moving coframe and joint canonical/Jacobi applications on the same unassigned-tension candidate. Full Lyy is retained. The original reset separates kinematic trace73, algebraic/Gauss80 and natural energy/temporal-dual73 responses; nonzero natural traction is a readout on a trial and must not be forced zero to define resistance.'
                evidence[key]['domain_scope']='actual field/geometric trace violations show that the local three-row normal/attachment glue does not supply the full birth/reset endpoint trace/source domain. Original73 reset trace rows are endpoint conditions, not authorization for continuous bulk reaction loads; their time images are endpoint/event-family contacts. The chronological application propagates owned per-arm canonical/source data and matches traces and internal cotangents at birth with actual outer returns. No physical mode is selected by coefficient Gram, instantaneous KKT momenta or eigenvector order.'
                evidence[key]['error_scope']='large time/moving-domain effects and projected step sensitivity are source-response diagnostics, not a percentage uncertainty on a_mu or an anomaly enclosure; complex contributions are preserved and the local I/R is not a physical cutoff'
            if key=='common_global_endpoint_second_source_quality_application':
                evidence[key]['matching_scope']='literal joint-action endpoint/event-family second contacts, original canonical rate rows and reference-clock source on two steps; original C73 is temporal birth/reset matching, not continuous material bulk glue'
                evidence[key]['source_quality_scope']='proper-normal second contact, phase jerk and lapse have relative step differences above one; they are unstable negative source-quality results, not certified physical normal acceleration, continuous reaction loads, zero missing jets or evidence of physical nonexistence'
                evidence[key]['error_scope']='actual DAE residuals and step differences retained; these do not enclose matching, domain, physical formation or soft Pauli uncertainty. The next action uses true-face per-arm canonical/source equations and actual birth/outer returns.'
            if key=='common_global_per_arm_canonical_normal_and_area_source_admission':
                evidence[key]['matching_scope']='actual final-candidate standalone parent Hessian/own Pi and child block with inherited parent source once; both original146 phase systems, natural temporal-dual effects and explicit supplied proper-normal pairings evaluated'
                evidence[key]['admission_scope']='historical ordinary binary application: unchanged absolute2e-10 guard fails for normal parent/child and area child; area parent passes separately. The additive bounded correction and fresh changing-source application now consume explicit high/low solutions with their own original-row checks; this older failure is preserved rather than silently relabeled.'
                evidence[key]['error_scope']='source-aware original equations and field/momentum differences, not an enclosure of changing action, physical normal mode, boundary/pole normalization or a_mu'
            if key=='common_global_admitted_parent_area_source_action_component':
                evidence[key]['matching_scope']='admitted parent area source advanced through original358 actual-face coefficient-germ action and literal transpose with supplied proper-normal covector; nonzero complex pairing preserved'
                evidence[key]['domain_scope']='historical held-face component, before the changing-source application: the child was unlaunched in this receipt. Held coefficients do not select the event/exterior domain; subsequent changing-stage sources and true endpoints are separate evaluated applications. Physical gamma/cutoff/pole/Pauli normalization remains unassigned.'
                evidence[key]['error_scope']='finite source/transpose absolute row checks do not enclose physical matching, omitted sectors or Pauli uncertainty'
            if key=='common_global_full_moving_reference_field_trace_source':
                evidence[key]['source_scope']='at fixed actual parent/independent fields, reference profile source is -dot(r_parent)+dot(r_child); full value/time/radial functions and exact wall retained before finite coefficient tests, with no source/geometry conjugation or duplicate actual-parent motion'
                evidence[key]['representation_scope']='old64 frozen affine coefficient rows have literal clock partial0, which is not the full moving trace source. All nonzero complementary functions and exact wall remain; test columns1/2 are separate output-function restrictions, not coefficient jets of column0. Comparison quadrature is not action-resistance or physical-state pairing.'
                evidence[key]['matching_scope']='full exact source and complement must enter weak trace/source and actual embedding/bundle matching; baseline same-chart discrepancies are diagnostic, not a physical failure verdict. Independent direct Higgs coefficients held here, while Higgs action/current response remains in saved full clock gradient and coupled inverse.'
                evidence[key]['error_scope']='profile identity/FD and fixed-basis comparison only, without physical pole/normalization/domain, continuum or Pauli enclosure'
            if key=='common_global_bounded_stored_admission_correction':
                evidence[key]['matching_scope']='one bounded three-correction check of each exact stored148 matrix/rhs/solution, all original146 rows, fixed momentum/source and named-frame reaction separated; high plus low is an explicit matrix-solution representation, ordinary rounded state checked separately'
                evidence[key]['error_scope']='Acb arithmetic bounds only on exact stored binary operands; original RHS assembly difference, action coefficients, evolving source/domain and physical observable are outside those bounds'
            if key=='common_global_changing_arm_source_application':
                evidence[key]['matching_scope']='actual changing nonlinear per-arm action at two incoming and two outgoing midpoint stages, fresh unchanged-momentum birth source reassembly, all original358 stage rows and actual146 endpoint fields, two-term normal/area source response and literal transpose readout; full reference source plus complementary function enters the weak action before restriction'
                evidence[key]['domain_scope']='incoming canonical arm is negative oriented; outgoing uses the retained same-coordinate affine parent/reference extension at positive increments. A solved incoming future is not grafted. Original birth/reset73 is endpoint matching only. Computational trial momentum, duration and coframe do not select the physical formation section, exterior or pole.'
                evidence[key]['error_scope']='binary reevaluated nonlinear action/base and exact supplied coefficient two-term response checks, separately reported stored-J assembly contacts; no temporal truncation, action/source, continuum, physical matching or Pauli enclosure'
            if key=='common_global_corrected_birth_source_endpoint':
                evidence[key]['matching_scope']='fresh full302 Legendre/trace/frame projection and all226 endpoint rows consume the same reassembled parent and child two-term source; theta=2own deltaPi minus joint deltaPi with direct area contacts once; natural forces remain response until the owned event stationarity application'
                evidence[key]['error_scope']='actual endpoint residual, source/analytic-dual contractions and limited directional step comparisons; no physical branch, mode, gamma/cutoff or normalized Pauli conclusion'
            if key=='common_global_changing_source_action_accuracy':
                evidence[key]['matching_scope']='limited fresh full-graph action-gradient directional controls at the final outgoing source stage; inherited parent, exact wall/profile, held-reference parameter partial and direct area contacts separated'
                evidence[key]['error_scope']='actual derivative/step sensitivity and literal projected readout diagnostic, not an action enclosure or a percentage error on a_mu'
            if key.endswith('_full18_current_source'):
                evidence[key]['matching_scope']='same reevaluated stage raw268 and explicit parent/reference values and source directions bind full18 homogeneous current coefficients, actual lapse/radius and full wall/profile source; both high/low columns applied before unsquared transfer, source return and independent literal transpose'
                evidence[key]['domain_scope']='owned computational initial-held/free-final domain and supplied full coordinate source; no physical spin vector, external Bi/Bf, pole/residue, charge/LSZ or angular complement selected. Preserved step orientation is explicit.'
                evidence[key]['error_scope']='binary analytic coefficient/first-direction and constant-stage exponential application; finite angular, stage, exterior/normalization and Pauli errors remain outside the current identity checks'
            if key.endswith('_unit_em_current'):
                evidence[key]['matching_scope']='actual stage Higgs-aligned holomorphic unit electromagnetic source JR=-Q(H)/N and declared literal dual LT=JR.T; high/low dQ and dN, operator/clock and both current-leg placements evaluated on the same finite source graph'
                evidence[key]['domain_scope']='initial-held/free-final coordinate tests at continued energy0; incoming negative step remains a backward control. The actual electromagnetic generator is not a physical external spin vector or charge/LSZ pole normalization.'
                evidence[key]['error_scope']='finite current/source-placement identities and cancellations; tiny absolute current/source norms are not Pauli contractions, complement bounds or a_mu uncertainties'
            if key.endswith('_signed_magnetic_action'):
                evidence[key]['matching_scope']='same complex changing stages rebuild the signed original336 n1 Maxwell/Higgs field action; full20 prescribed gauge wall trace, natural H, known wall lift, complete At/Gauss and named frame returns retained, with eR4^2/2 exactly once and actual Higgs-aligned Q and coordinate-time derivative'
                evidence[key]['domain_scope']='the owned C2 finite pulse and common Q/Qdot Hermite are explicit computational source approximations. Negative incoming initial-held/free-final weak control stays distinct from the positive future zero-Cauchy canonical prefix; the child initial-zero prefix does not replace its physical inherited birth matching. Physical moving-stop, adiabatic/exterior and pole domains are not silently held fixed.'
                evidence[key]['consumer_scope']='actual source fields and induced Higgs enter the unsquared magnetic operator insertion, right-current motion and literal-left motion before projection. Reached signed D3S contacts are separate linked applications, not a completed Gaussian mean, positive native realization or normalized soft Pauli result.'
                evidence[key]['error_scope']='binary original action, Schur, source, wall/Gauss/frame, temporal control and three-placement checks; absolute and scaled residuals are separate. No Pauli uncertainty follows from small current norms, reaction magnitudes or prescribed-wall identity checks.'
            if key.endswith('_magnetic_mixed_action'):
                evidence[key]['matching_scope']='actual causal total n1 B fields and coordinate rates enter signed D3S Maxwell curvature and intrinsic DH/Hdot/potential contacts, with both ordered angular and both mixed time placements. Same stage homogeneous normal/area field trials supply evaluated classical contractions before temporal integration.'
                evidence[key]['domain_scope']='the other even coefficients vanish only for this supplied homogeneous field trial. The complete supplied stage-row quadratic field derivative is separately evaluated in the linked quadratic-action consumer, including its geometry/profile/coframe complement. Physical source-stop/exterior and full event/geometry sectors remain active; they are not action-derived zeros. The signed field derivative is not a substitute for the physical native positive realization or its source/dual maps.'
                evidence[key]['error_scope']='binary literal-action contraction, Haar/Gaunt, complex-linearity and finite causal-prefix checks; no full native contact/own mean, overlap, normalized Pauli value or uncertainty enclosure'
            if key.endswith('_complete_quadratic_field_direction'):
                evidence[key]['matching_scope']='all actual causal B fields and coordinate rates contract the already supplied full changing-stage signed M/BF/BR/K derivatives, including geometry/density/profile/coframe/H/Hdot; both independently varied B response slots use the actual causal high/low field/rate first jets. The matched field-only D3 contribution is subtracted only to identify the reached geometry/profile/coframe complement.'
                evidence[key]['domain_scope']='complete supplied-direction quadratic field-sector derivative on the same finite fixed-time C2/Hermite prefix; physical pulse/stop/domain and full event/geometry/quantum sectors remain separate. This is not a formation zero or a normalized resistance/inertia derivative.'
                evidence[key]['error_scope']='binary coefficient/source/contraction identities and existing causal prefix approximation; a classical quadratic-action value does not supply native heat mean, same-background continuum overlap or a Pauli uncertainty'
            if key.endswith('_n3_n4_magnetic_operator_action'):
                evidence[key]['matching_scope']='actual outgoing causal n1 B source at sigma0.75 applies the retained source1 x odd3 Gaunt action into even2/4, with full source At/radial/H/Hdot, both directed angular placements and K/BF/BR/M contacts before assembly'
                evidence[key]['domain_scope']='named24 wall/H coordinate test images with checked right-inverse trace contract; neither a full84 inverse-domain reduction nor a physical current/adjoint source is inferred. The reached n4 image is retained and nonzero.'
                evidence[key]['error_scope']='same-source operator/test action and literal reverse/Haar checks; not a full native angular complement, loop/mean/overlap, pole or Pauli bound'
            if key in ('common_global_outgoing_normal_signed_magnetic_action','common_global_outgoing_area_signed_magnetic_action',
                    'common_global_outgoing_normal_magnetic_mixed_action','common_global_outgoing_area_magnetic_mixed_action',
                    'common_global_outgoing_normal_complete_quadratic_field_direction','common_global_outgoing_area_complete_quadratic_field_direction',
                    'common_global_outgoing_n3_n4_magnetic_operator_action'):
                evidence[key]['continuation_scope']='CONTROL_ONLY for the restarted-zero child domain. Its actual signed-action operator/contraction remains evaluated at that supplied source. The additive source-on child now inherits the reconstituted parent free q/Pi and changes all source-dependent downstream contractions; the old values are preserved and are not substituted for the joined response.'
            if key=='common_global_actual_magnetic_birth_constraint_roles':
                evidence[key]['matching_scope']='initial all-coordinate test diagnostic: actual inherited free q/Pi close, while larger prescribed-wall/Gauss rows are conormal reactions with nonzero source work. Actual born parent reconstitution and the named constraint-dual range are evaluated in the additive inherited source-on consumer; prescribed reactions are not forced to zero.'
            if key=='common_global_inherited_source_on_child_action_and_current':
                evidence[key]['matching_scope']='parent then child reconstituted on actual birth action at preserved free q/Pi; wall/frame reactions are retained and lie in their named conormal range. Dynamic trace and free momentum, complete source cotangent and independently differentiated high/low initial maps enter the source-on child action/current. Algebraic At value is not an inherited dynamic trace.'
                evidence[key]['domain_scope']='fixed supplied two-stage signed original field domain, actual birth/midpoint/true endpoint Q/coordinateQt C1 germs, source already on at birth. The full coupled geometric birth/formation/energy/tension/exterior equations are separate and are not solved by the field-sector pass.'
                evidence[key]['error_scope']='binary original free equations, conormal/source/canonical/current checks and declared source interpolation; neither these residuals nor current norms supply physical pole/residue/charge normalization or an a_mu bound'
            if key=='common_global_complete_inherited_magnetic_endpoint_cotangent':
                evidence[key]['matching_scope']='direct original endpoint qP.T PiP-qC.T PiC and complete normal/area first, including both Pi response slots plus moving-source contact, independently compared with prescribed-source cotangent. These are O(Ba Bb) classical action coefficients; they do not repair zero-magnetic base stationarity at linear soft readout order.'
                evidence[key]['error_scope']='same stored endpoint/source identity and literal first; not physical normal/inertia, pole/residue/charge or native Pauli error'
            if key=='common_global_one_sided_source_on_corner_returns':
                evidence[key]['matching_scope']='actual initial/outer and left/right coefficient-corner q,Pi and complete first faces reconstructed from stored inherited canonical states; each corner uses its own C1 source polynomial second germ for algebraic At rate. Full wall momentum jump and source work retained despite free momentum continuity.'
                evidence[key]['error_scope']='point Euler equations exclude this distributional return; exact source-on field-domain face and corner comparisons do not bound physical outer matching or anomaly'
            if key=='common_global_inherited_source_on_combined_weak_action':
                evidence[key]['matching_scope']='recomputed original signed bulk M/BF/BR/K action with coefficient and both source-first response slots on the inherited20-point child. Actual initial, coefficient-corner and outer q.TPi returns and prescribed wall-force work enter one combination; its independent weak identity is a check, not a Green-cancellation substitution for native response.'
                evidence[key]['domain_scope']='same prescribed-source fixed coordinate interval and signed action; full event/domain motion, physical exterior pole and positive native/current matching remain separate action applications'
                evidence[key]['error_scope']='retained weak-closure quadrature and representation defects at this finite scope; not quantum native own mean, both loop insertions, overlap subtraction or normalized soft Pauli uncertainty'
            if key=='common_global_inherited_magnetic_unsquared_pure_trace':
                evidence[key]['matching_scope']='actual inherited20-point source and full18 neutral/charged fibers apply the magnetic unsquared transfer derivative U_B, with left propagator, operator/clock/source and right propagator first slots. This supplies the executed B transfer operand for Gamma_B=Bi_B+Bf_B U+Bf U_B; physical Bi/Bf and their derivatives are not invented.'
                evidence[key]['domain_scope']='same signed constant-stage n0+n1 fermion coordinate-test restriction; reached n2 and full exterior/native domain remain required wherever the physical consumer reaches them. This transfer is distinct from the evaluated J.T A^-1 J current and from a positive native square.'
                evidence[key]['error_scope']='finite supplied source/quadrature/propagator and independent complex Duhamel check; no physical pole, mass/lifetime, LSZ, Pauli or continuum complement bound'
            if key=='common_global_actual_canonical_momenta_and_trace_return':
                evidence[key]['source_scope']='actual standalone parent and joint graph momenta remain separate; their nonzero difference is inherited source feedback, not a supplied momentum to graft between operators. Both actual Ly and analytic density/coframe source jets are exported without a physical stop/domain claim.'
            if key=='common_global_actual_birth_current_adjoint_source_images':
                evidence[key]['matching_scope']='complete6x48 current/analytic-adjoint columns and both angular spectators at the original common birth trace575 on the same upstream chronological graph; evaluated source-lift/image comparison, not a new temporal inverse, offset or all-row global stationarity check'
            if key=='four_placement_magnetic_matching_incoming':
                evidence[key]['correction_status']='older E-transpose source-derivative contact preserved as diagnostic; additive E-source contact repair and affected matching are active'
            if key=='full_tensor_temporal_lifetime_equation':
                evidence[key]['correction_status']='older static weak/spin injection fails the owned charged/neutral projector check; conditional scales remain diagnostic while the owned charged_dirac_injection replay is active'
            if key in ('corrected_full_wall_reached_return_heat','all_closed_lepton_families_for_each_outer_current'):
                evidence[key]['projection_scope']='mass/FW test covectors at a fixed cutoff probe; physical pole/charge/LSZ soft Pauli projection, mean, domain, completion and overlap remain in the same consumer'
                evidence[key]['uniform_bound_scope']='finite heat VALUE uniformly for c>0, not its separately evaluated cutoff derivative; binary coefficients, not outward continuum or Pauli enclosure'
            if key in ('same_current_scalar_matching_and_complete_C_covectors','complete_incoming_C_projection','complete_C_photon_adjoint_and_all_closed_leptons'):
                evidence[key]['matching_scope']='conditional normal right-symbol scalar matching and covectors; charged/neutral Ward generator, negative charged pole, first/higher Weyl contacts, internal same-action mass/kinetic subtraction and the source/domain identification remain active. Scalar counterterms are not an independent fixed-Y mass prediction.'
                evidence[key]['overlap_scope']='a paired family contraction does not subtract the same-background local reference or establish a physical Pauli contribution'
            if key in ('source_specific_original_field_own_mean','source_specific_all_lepton_field_heat_mean'):
                evidence[key]['source_scope']='the original incoming middle-family mass-axis0 p/u source; not grafted into the subsequently corrected complete C source. The latter requires its own source contraction or proved linear recombination.'
            if key=='same_observation_owned_decay_tensor':
                evidence[key]['matching_scope']='the owned charged Dirac injection corrects the older weak/spin injection; inclusive/non-VA radiative corrections, physical pole/domain and decay-scale identification remain coupled matching equations'
            if key=='reached_zero_source_all_lepton_quantum_field_mean':
                evidence[key]['matching_scope']='large finite1680 zero-source response; not a small perturbative quantum base or scalar mass shift. Actual same-background local subtraction, H-frame motion, coupled geometry/domain/graded gradient and nonlinear base matching remain in this consumer.'
            if key in ('source_specific_all_lepton_field_heat_mean','reached_zero_source_all_lepton_quantum_field_mean',
                       'reached_zero_source_mean_Higgs_frame_contact','reached_zero_source_mean_gauge_invariant_curvature'):
                evidence[key]['operator_scope']='evaluated original fixed-FE2 sewn field/heat sector. Restoring the connector changes K/M and its field heat cotangent; this result is not substituted for the corrected whole operator own mean.'
            if key=='complete_unsubtracted_C6_local_pole_residue':
                evidence[key]['matching_scope']='complete affine normal local symbol, including both charged signs and neutral complement, with analytic resolvent residues. No scalar counterterm, energy-origin fit or physical exterior/Feynman pole identification. Its common mass/rate equation residual is evaluated rather than assigned zero.'
            if key in ('complete_C6_band_C_covectors','complete_incoming_C_T_band_application','complete_outgoing_C_T_band_application',
                'complete_C6_band_energy_motion','both_external_energy_leg_contacts','incoming_full_ordered_momentum_source','outgoing_full_ordered_momentum_source'):
                evidence[key]['operator_scope']='complete corrected angular-source/four-placement application of the retained fixed-FE2 field inverse and local affine symbol. These values are preserved while the restored whole chronological field/operator graph is solved; they are not grafted onto that different inverse.'
                evidence[key]['matching_scope']='all charged signs, neutral complement and literal reverse retained; local affine residue is not physical exterior/charge/LSZ identification, higher Moyal, overlap or soft-limit enclosure'
            if key=='both_external_energy_leg_contacts':
                evidence[key]['energy_scope']='actual source-energy legs at the E=0 anchor, with the full nonrest two-spin band energy derivative; not the full current evaluated at a nonzero physical pole'
            if key=='restored_birth_window_heat':
                evidence[key]['operator_scope']='two-cell/seven-node restored window, with original complex pencil and independent reflected branch. Binary exponential underflow is explicit and is neither the global own mean nor an action-derived zero.'
            if key=='continued_local_weak_strong_composition_and_source_germs':
                evidence[key]['operator_scope']='actual restored nodes with analytically differentiated inherited germs, normal first derivative, clock/measure contact, ordered EiEj and mixed temporal-spatial principal term. Homogeneous-source zeros apply only to n0; no local overlap coefficient or real a4 imported.'
            if key=='whole_chronological_low_spectral_modes':
                evidence[key]['spectral_scope']='actual whole-domain low generalized modes; residuals of selected modes do not enclose the complete spectrum or select the physical relative contour'
            if key=='whole_chronological_negative_spectral_modes':
                evidence[key]['spectral_scope']='verified original full-body negative-real modes in the joined holomorphic weak K/M; positive-c heat grows exponentially on those modes. This executed domain mismatch prevents using that pencil as the accretive native heat operator. The causal/current pencil remains executable; the retained native factor/coframe and physical-domain matching must be applied.'
            if key=='whole_chronological_partial_low_heat_cotangent':
                evidence[key]['spectral_scope']='paired literal-transpose low spectral span on the entire1151-node graph, with original generalized mass pairing and full near-degenerate cluster. Its source cotangent is a partial application. The complementary spectrum contains verified growing modes; no completed own mean, nonlinear source, or Pauli allowance follows from this partial result.'
            if key=='whole_classical_nonlinear_stationarity':
                evidence[key]['operator_scope']='independent literal nonlinear residual on every1150 free84-field+4-multiplier node, with all383 corner pairs and the original final natural row; fixed geometry and no native source assignment. The tiny Higgs shift does not resolve the leading physical mass/rate matching.'
            if key=='complete_both_leg_C_T_external_energy_partial':
                evidence[key]['operator_scope']='complete C+T fixed-band E=0 partial, both external energy legs, all four placements and literal reverse. Physical on-pole external band/residue motion is a separate consumer; the fixed-FE2 inverse remains at its baseline scope.'
            if key in ('owned_common_A_real_native_reference','owned_common_A_real_native_reference_heat'):
                evidence[key]['operator_scope']='real native reference A=(partial_t+Omega_L,t)/N+W on geometric Ndt/unitHaar core; all3closed lepton families and n0..3 with exact spectator multiplicity. This is not the analytically transported corrected Lorentz background; it cannot replace that operator own mean or furnish same-background subtraction.'
                evidence[key]['error_scope']='stored-form binary comparison and conditional finite-contour tails only; original action A-dagger-A is positive before assembly rounding. Infinite angular complement, relative exterior/reset/stop domain, boson/ghost sectors and observable uncertainty are not included.'
            if key=='native_local_current_and_coupled_scalar_overlap_matching':
                evidence[key]['matching_scope']='pointwise full C6 native-to-canonical coframe/current map plus original coupled n1 scalar/gauge Green, all four canonical radial sources, At/Gauss and named frame reactions. The common lifetime scale is a declared probe; mass loads and charge/body/curvature residuals remain explicit. Its calibrated scalar covector diagnostic is not a completed native subtraction or a_mu.'
                evidence[key]['causal_scope']='the earlier radial quadrature is a precontour diagnostic. The retained exp(+iz tau) owner requires the retarded C(-is) Laplace application, including its nonzero residues and finite endpoint return; the latter is an active additive calculation.'
            if key=='common_global_actual_endpoint_and_nonstationary_amputation':
                evidence[key]['matching_scope']='actual endpoint and nonstationary body terms retained. The finite initial-value pole matrix I has determinant1 and energy derivative0; this proves that finite response cannot furnish LSZ. Applying the retained reset/stop/exterior return to the pole equation remains an owned action application, not a missing independent datum.'
            if key=='corrected_retarded_scalar_path_and_residues':
                evidence[key]['causal_scope']='the scalar exp(+iz tau) owner gives C(-is), with actual retarded rotation, nonzero residues and canonical final endpoint. The common1151 boundary response is separately evaluated rather than replaced by the local meromorphic or finite one-cell inverse.'
            if key in ('same_base_unsquared_native_current_range_match','actual_global_coupled_current_adjoint_native_source_match'):
                evidence[key]['matching_scope']='same converged background, native reflected base and independent analytic source tangents, both original and geometric measures, independently acted numerator and explicit derivative-image range contacts. This correspondence is an evaluated finite source application; it is not a physical pole normalization or Pauli error bound.'
            if key=='actual_global_coupled_current_adjoint_native_source_match':
                evidence[key]['source_scope']='actual global u/p column208 application through complete n0+n2/n1 Gaunt images, including nonzero induced Higgs source. All288 source columns remain addressable; this named subset is not assigned a physical spin state or complete readout.'
            if key=='common_global_actual_native_analytic_source_return':
                evidence[key]['source_scope']='same actual column208 induced At/Ar/Ai/H directions, complete reached even0+2 sectors and all original free rows; literal current return -p^T(Aw_original u_native-R_original) and corrected birth/final traces. Its represented closure is not an exterior pole/residue or soft Pauli result.'
            if key=='common_global_actual_shifted_boundary_and_forced_form_core_return':
                evidence[key]['matching_scope']='actual coupled column208 finite terminal form-core restriction, acted source-corrected conormal and independent square K-transpose response. Both analytic energy envelopes and the separate Hilbert shifted square are retained. Full18/36 Cauchy maps use declared edge-average body germs; neither the finite Dirichlet rectangle nor its source return selects the physical external pole or stop.'
            if key=='common_global_charge_transport_and_source_chart_weak_residual':
                evidence[key]['correction_status']='preserved represented p[8] source-clock diagnostic; actual ordinary source cells require dz/dtau_E=-i/N. The additive corrected source-clock projection evaluates that demonstrated correction without altering this frozen output.'
            if key=='common_global_corrected_source_clock_charge_projection':
                evidence[key]['matching_scope']='actual source-clock charge correction on all original nodes and complete C6 current directions, including complex charged/neutral terms; no physical charge, pole or Pauli normalization follows from its small integral.'
            if key in ('common_global_full_complex_child_action_constraints','common_global_full_complex_canonical_compatibility_application'):
                evidence[key]['matching_scope']='full same-background complex child252 action, all146 original Legendre/Gauss/multiplier rows, exact named central frames and action Pi. A nonzero reported multiplier residual precludes treating the candidate as a canonical exterior launch; a limited Newton attempt does not prove nonexistence.'
            if key=='common_global_exact_explicit_inherited_clock_contact':
                evidence[key]['matching_scope']='exact explicit inherited-clock derivative of the full action gradient, including geometry density/measure and scalar wall contacts; its evaluated canonical tangent RHS is not advanced before original compatibility is solved.'
            if key=='common_global_full_complex_terminal_stress_attribution':
                evidence[key]['matching_scope']='literal same-terminal cap/Maxwell/intrinsic-Higgs gradient split with every lapse/shift row: the global corrected field Maxwell stress dominates the new geometry constraint defect. This is an evaluated source attribution, not a fit, independent background choice or Pauli contribution.'
            if key.endswith('coupled_GG_GH_HG_HH'):
                evidence[key]['matching_scope']='exact same-source polynomial with common coupled field action: GG cancels before distinct physical exterior restrictions; GH, HG and HH remain. Numerical response coefficients inherit the recorded difference amplification. Distinct family exterior/pole maps can retain different gauge contractions, so this is not physical native overlap or a Pauli cancellation.'
            if key=='corrected_native_dual_density_graph':
                evidence[key]['domain_scope']='the explicit rho density/contact/corner map reproduces the original analytic action and current moments. This relation is distinct from a Hilbert adjoint with an ordinary shared left trace; the matched weak source/range complement is being applied.'
            if key=='completed_corrected_candidate_heat_production_paused':
                evidence[key]['operator_scope']='completed run before the user paused additional heat production; preserved without further production refinements. Original fixed-tree reflected-coframe candidate on declared initial-only/free-final shared left FE domain, not the newly converged same-background physical native operator or its total mean.'
                evidence[key]['physical_normalization_assigned']=False
                evidence[key]['additional_heat_production_paused']=True
            if key=='scalar_residue_and_radial_overlap_tail_application':
                evidence[key]['error_scope']='outward same-coordinate constrained tail bound through all Gauss/frame rows; nonzero source residues and both diagnostic bypasses retained. This is not a total Pauli bound and does not itself choose the causal bypass.'
            if key=='local_fixed_Y_matching_load_diagnostic':
                evidence[key]['matching_scope']='old complete C6 local affine/E=0 conditional symbol only. Its failed mass matching is retained as a diagnostic and is not used to normalize the new global physical Pauli calculation.'
    projected_diagnostics={}
    for side in ('incoming','outgoing'):
        key='complete_'+side+'_C_T_band_application'
        if key in evidence:
            rec=json.loads((ROOT/evidence[key]['path']).read_bytes())
            projected_diagnostics[side]=dict(source=evidence[key]['path'],sha256=evidence[key]['sha256'],
                scopes={r['scope']:dict(family=r['family'],
                    isotropic_spin_trace=r['all_four_placement_values']['total']['isotropic_spin_trace'],
                    anisotropic_spin_remainder_norm=r['all_four_placement_values']['total']['anisotropic_spin_remainder_norm'])
                    for r in rec['records']},
                all_four_placements_both_insertions_and_literal_reverse_retained=True)
    matching_diagnostics={}
    if 'complete_unsubtracted_C6_local_pole_residue' in evidence:
        ev=evidence['complete_unsubtracted_C6_local_pole_residue']
        rec=json.loads((ROOT/ev['path']).read_bytes())
        matching_diagnostics=dict(source=ev['path'],sha256=ev['sha256'],
            residuals=[{k:r[k]for k in ('side','independent_positive_mass_units_GeV',
                'same_observation_positive_electron_mass_equation_relative_residual',
                'inclusive_rate_fraction_required_for_that_unit')}
                for r in rec['records']if 'inclusive_rate_fraction_required_for_that_unit'in r],
            required_rate_fractions_are_equation_residuals_not_computed_radiative_corrections=True,
            physical_common_mass_or_decay_unit_identified=False)
    global_matching_diagnostics={}
    for key,ev in evidence.items():
        if key.startswith('common_global_') or key in ('corrected_retarded_scalar_path_and_residues',
            'same_base_unsquared_native_current_range_match','actual_global_coupled_current_adjoint_native_source_match'):
            record=json.loads((ROOT/ev['path']).read_bytes())
            global_matching_diagnostics[key]=dict(source=ev['path'],sha256=ev['sha256'],
                evaluated={k:v for k,v in record.items() if k not in ('input_hashes','archives')},
                numerical_diagnostics_are_not_anomaly_contributions_or_allowances=True)
    report=dict(classification='ACTIVE_CONSOLIDATED_MUON_CONTRIBUTION_AND_ERROR_ACCOUNTING',
        contribution_and_error_table=rows,input_hashes=refs,completed_local_subtotal=subtotal,
        completed_local_subtotal_g=2*(1+subtotal),complete_a_mu=None,complete_g_mu=None,complete_magnetic_moment=None,
        complete_observable=False,action_selected=False,Gate7_closed=False,
        frozen_local_approximation_order=local['approximation_order'],
        completed_local_uncertainty_contract=local['errors'],
        completed_local_input_contract={k:local[k]for k in local if 'gradient'in k or 'covariance'in k or 'correlation'in k},
        active_same_action_evidence=evidence,
        corrected_operator_own_mean_contract='Differentiate the restored full connector operator on its same joined field/domain graph. The original FE2 heat cotangent and source-specific mean are valid baseline applications, but cannot replace the corrected K/M heat cotangent or its own constrained mean.',
        reached_domain_correction='The joined holomorphic causal/action pencil has verified negative-real full-body modes. Bind the retained native covariant temporal factor, reflection/coframe pairing and relative exterior/stop domain before treating it as an accretive heat realization; do not change the measure to its absolute value or assign the growing complement zero.',
        physical_cutoff_contract='BHSM-AE4-BRANCH-BIRTH-CUTOFF-2026-10-08: c_mu=i_mu+/r_mu+ on childplus birth; proper-clock kinetic and restoring action contractions, gamma law and required source jets/matching remain in the combined consumer',
        active_background_contract='Literal wall/current applications use retained tree-matched lambda_H=GF*mh^2/sqrt(2)=0.1290946235307726 and unassigned gamma. The lambda_H=0.7853192208866044,gamma=0.11 coupled response is a distinct solved parameter-family trial. No response or heat is grafted between these backgrounds, and neither trial is silently promoted to the physical cutoff/matching solution.',
        scale_contract='solve C_decay(E)-E^4*hbar/tau=0 on the matching restriction; retain inclusive/non-VA radiative and domain corrections, then m_action=m_mu/E; a conditional finite tensor root is not a demonstrated physical decay-scale identification',
        refinement_priority='effect on normalized projected Pauli observable and larger matching/domain/omitted-sector uncertainty; no further reduction of negligible finite contour/matrix error',
        active_projected_matching_diagnostics=dict(
            common_domain_action_source_and_boundary_applications=global_matching_diagnostics,
            complete_unsubtracted_C6_C_T_local_affine_application=projected_diagnostics,
            common_mass_and_decay_equation_residuals=matching_diagnostics,
            historical_positive_only_scalar_pole_control='artifacts/muon_normal_matched_current_covectors_20261011/run_2/result.json',
            historical_positive_only_scalar_control_is_active_normalization=False,
            these_are_not_a_mu_values_or_error_allowances=True,
            required_application='same restored-operator own mean and stationary base, full current at its physical pole with actual charged generator and both energy legs, same-background overlap, completion and signed soft Pauli projection; update only affected projections'),
        final_error_contract='the native row and any surviving omitted matched local sectors require evaluated values, demonstrated cancellations, or justified projected allowances; no total uncertainty is formed while an unknown contribution remains',
        error_scope='reused frozen calibrated local values and their actual dependencies; active native action applications remain at their recorded scope')
    q=out/'contribution_error_table.json';q.write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    lines=['# Active muon contribution and error accounting','',
        'The completed matched local subtotal is `'+repr(subtotal)+'`. The disjoint native remainder is still being calculated. These values are not a completed muon prediction.','',
        '| Contribution | a_mu | Status and error contract |','|---|---:|---|']
    for row in rows:
        value='active calculation'if row['a_mu']is None else format(row['a_mu'],'.17g')
        lines.append('| '+row['component']+' | '+value+' | '+row['status']+'; '+row['uncertainty_contract']+' |')
    lines.extend(['','The JSON table retains the frozen local dependency and error objects. The native row consumes the corrected contact, both insertions, its own heat mean, boundary/corner returns, and same-background overlap as one combination, followed by physical pole/residue normalization and the signed soft Pauli readout.',
        '',report['scale_contract']+'. '+report['physical_cutoff_contract']+'.',
        '',report['refinement_priority']+'.','',
        'DERIVED: the owned combined action, source/clock/domain differentiation and normalized Pauli identities.',
        'EVALUATED: the unchanged matched local subtotal and action applications linked in the JSON evidence.',
        'CONTROL_ONLY: finite source-cell sewing, cutoff probes and conditional decay-scale restrictions remain at their declared scope.',
        'UNEVALUATED: the complete physically matched native row, the surviving finite weak/quark complement, and total observable uncertainty.',
        'OWNER_DEFINITION_GAP: none established by unfinished implementations.',''])
    (out/'contribution_error_table.md').write_text('\n'.join(lines),encoding='utf8',newline='\n')
    print(json.dumps(dict(table=q.relative_to(ROOT).as_posix(),sha256=sha256(q.read_bytes()).hexdigest(),local_subtotal=subtotal,complete_observable=False),sort_keys=True))
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=Path('artifacts/muon_observable_combination_20261011'));a=p.parse_args();materialize(a.output)
