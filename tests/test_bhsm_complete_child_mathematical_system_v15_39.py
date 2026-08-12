from bhsm.interface.bhsm_complete_child_mathematical_system_v15_39 import (
    child_configuration_space,
    complete_child_functional,
    completion_payload,
    current_constructive_state,
    deterministic_json,
    downstream_attachment_definition,
    variational_problem,
)


def test_particle_is_defined_as_the_complete_child():
    result = child_configuration_space()
    assert result["particle_definition"].startswith("complete_persistent")
    assert result["material_interface"].endswith("sigma=0")
    assert result["child_scale"].startswith("x=log(B/A)")


def test_one_action_and_one_Einstein_eta_KKT_problem_are_declared():
    functional = complete_child_functional()
    problem = variational_problem()
    assert len(problem["independent_equations"]) == 6
    assert len(problem["KKT_equations"]) == 2
    assert functional["FR_moments"] == {"J_mean": 0.0, "J_squared_mean": 0.25}
    assert functional["free_pressure"] is False
    assert functional["free_wall_tension"] is False


def test_constructive_state_preserves_skin_result_without_semantic_drift():
    result = current_constructive_state()
    assert result["material"]["isolated_skin_lowest_eigenvalue"] < -14.0
    assert result["material"]["isolated_skin_is_particle"] is False
    assert result["FR_child"]["reduced_stationary_child"] is False
    assert result["FR_child"]["physical_child_scale"].startswith("POST_CUT_R=")
    assert result["geometry"]["nonround_conformal_Hamiltonian_companion"]
    assert result["geometry"]["momentum_balanced_TT_shear_initial_data"]
    assert result["geometry"]["nonlinear_negative_child_scale_reached"]
    assert result["geometry"]["reconstruction_firewall_event_data_carried"]
    assert result["geometry"]["post_cut_child_reconstruction"] == "CONSTRAINT_SOLVED_V15_46"
    assert result["geometry"]["post_cut_self_similar_persistence"] == "REJECTED_V15_47"
    assert result["geometry"]["post_cut_nonround_Lorentzian_chart"] == "DERIVED_V15_48"
    assert result["geometry"]["post_cut_Dirac_constraint_projection"] == "SOLVED_V15_49"
    assert result["geometry"]["post_cut_initial_Dirac_matrix_rank"] == 11
    assert result["geometry"]["post_cut_constrained_child_scale_velocity"] < 0.0
    assert result["geometry"]["post_cut_second_eta_firewall"] == "REACHED_V15_49"
    assert result["geometry"]["post_cut_return_before_second_firewall"] is False
    assert result["geometry"]["post_cut_diagonal_Sp1_quotient"] == "DERIVED_V15_50"
    assert result["geometry"]["post_cut_classical_connection_energy_double_counted"] is False
    assert result["geometry"]["post_cut_M4_free_conformal_zeta"] == "DERIVED_V15_51"
    assert result["geometry"]["post_cut_M4_free_conformal_C_SM"] == "59/30"
    assert result["geometry"]["post_cut_M4_attached_turning_points"] == 0
    assert result["geometry"]["post_cut_M4_free_conformal_term_sufficient"] is False
    assert result["geometry"]["post_cut_hybrid_actualization_cycle"] == "DERIVED_FINITE_CHART_V15_52"
    assert result["geometry"]["post_cut_hybrid_continuous_Floquet_spectral_radius"] == 0.0
    assert result["geometry"]["post_cut_hybrid_FR_projective_multiplier"] == 1.0
    assert result["geometry"]["post_cut_hybrid_SM_bundle"] == "DERIVED_V15_53"
    assert result["geometry"]["post_cut_hybrid_SM_family_dimension"] == 16
    assert result["geometry"]["post_cut_hybrid_SM_family_count"] == 3
    assert result["geometry"]["post_cut_hybrid_SM_local_anomalies"] == "ZERO"
    assert result["geometry"]["post_cut_hybrid_Berger_spectral_seed"] == "DERIVED_V15_54"
    assert "CANONICAL_BASIS_TRANSPORT_I3" in result["geometry"]["post_cut_hybrid_current_CKM"]
    assert "CANONICAL_BASIS_TRANSPORT_I3" in result["geometry"]["post_cut_hybrid_current_PMNS"]
    assert result["geometry"]["post_cut_hybrid_current_Jarlskog"] == 0.0
    assert result["geometry"]["post_cut_hybrid_internal_Dirac_lift"] == "DERIVED_V15_55"
    assert result["geometry"]["post_cut_hybrid_wall_normal_Higgs_overlap"] == 1.0
    assert result["geometry"]["post_cut_hybrid_background_Higgs"] == 0.0
    assert result["geometry"]["post_cut_hybrid_physical_fermion_masses"].startswith("ZERO")
    assert "UNOBSERVABLE" in result["geometry"]["post_cut_hybrid_physical_CKM_PMNS"]
    assert result["geometry"]["post_cut_hybrid_full_function_space_uniqueness"].startswith("DERIVED")
    assert result["geometry"]["post_cut_hybrid_weak_angle_on_ray"] == "3/8"
    assert result["geometry"]["post_cut_hybrid_color_confinement"].startswith("CLOSED_S3")
    assert result["geometry"]["post_cut_hybrid_neutrino_mass_squared_splittings"] == [0.0, 0.0]
    assert result["geometry"]["post_cut_hybrid_smooth_bulk_gauge_pushforward"] == "EXCLUDED_V15_60"
    assert result["geometry"]["post_cut_hybrid_parent_Higgs_doublet"] == "ABSENT_V15_60"
    assert result["geometry"]["post_cut_hybrid_matching_scale"].startswith("MU_STAR")
    assert result["geometry"]["post_cut_hybrid_intrinsic_M4_raw_parameter_rank"] == 75
    assert result["geometry"]["post_cut_hybrid_intrinsic_M4_C3_parameter_rank"] == 27
    assert result["geometry"]["post_cut_hybrid_intrinsic_M4_central_parameter_rank"] == 11
    assert result["geometry"]["post_cut_hybrid_background_coefficient_Jacobian_rank"] == 0
    assert result["geometry"]["post_cut_hybrid_state_level_unique"] is True
    assert result["geometry"]["post_cut_hybrid_theory_level_unique"] is False
    assert result["geometry"]["post_cut_hybrid_event_naturality_fiber_rank"] == 11
    assert result["geometry"]["post_cut_hybrid_minimal_new_law_count"] == 1
    assert "bar(Q_L)u_R" in result["geometry"]["post_cut_hybrid_composite_Higgs_channels"]
    assert result["geometry"]["post_cut_hybrid_weak_DtN_operator_order"] == 1
    assert result["geometry"]["post_cut_hybrid_weak_LR_Higgs_projection"] == 0.0
    assert "ELECTRIC_GAUSS_DtN" in result["geometry"]["post_cut_hybrid_full_gauge_nonlocal_DtN"]
    assert result["geometry"]["post_cut_hybrid_DtN_inverse_kernel_ray"] == "G_Y:G_2:G_3=3/5:1:1"
    assert result["geometry"]["post_cut_hybrid_LR_group_weights"]["up"] == "7/5"
    assert result["geometry"]["post_cut_hybrid_LR_fermion_susceptibility"].startswith("S(s;q)")
    assert result["geometry"]["post_cut_hybrid_LR_susceptibility_residue"].startswith("-1/8")
    assert result["geometry"]["post_cut_hybrid_split_gauge_Yukawa_completion_allowed"] is False
    assert result["geometry"]["post_cut_hybrid_unified_gauge_Yukawa_pushforward"].endswith("V15_69")
    assert "FAMILY-CENTRALITY_IS_FORCED" in result["geometry"]["post_cut_hybrid_Yukawa_Wilson_matrices"]
    assert result["geometry"]["post_cut_hybrid_cycle_family_operator"].endswith("V16_02")
    assert result["geometry"]["post_cut_hybrid_cycle_composite_gap"].endswith("V15_91")
    assert result["geometry"]["post_cut_hybrid_cycle_scale_renormalization"].endswith("V15_97")
    assert "0.97828731" in result["geometry"]["post_cut_hybrid_cycle_scale_renormalization"]
    assert result["geometry"]["post_cut_hybrid_proper_time_joint_pushforward"].endswith("V15_91")
    assert result["geometry"]["post_cut_hybrid_ADM_proper_DtN_gap"].endswith("V15_92")
    assert "V15_93" in result["geometry"]["post_cut_hybrid_reset_Hessian_matter_cones"]
    assert result["geometry"]["post_cut_hybrid_quadratic_backreaction_closure"].endswith("V15_94")
    assert "V15_95" in result["geometry"]["post_cut_hybrid_quantum_cone_repair_gate"]
    assert result["geometry"]["post_cut_hybrid_common_quantum_superdeterminant"].endswith("V15_96")
    assert "V15_97" in result["geometry"]["post_cut_hybrid_dense_proper_joint_pushforward"]
    assert result["geometry"]["post_cut_hybrid_dense_quantum_repair_gate"].endswith("V15_98")
    assert result["geometry"]["post_cut_hybrid_common_source_Frechet_response"].endswith("V15_99")
    assert result["geometry"]["post_cut_hybrid_quantum_functional_accounting"].endswith("V16_00")
    assert result["geometry"]["post_cut_hybrid_rank16_U1_HS_vertices"].endswith("V16_01")
    assert result["geometry"]["post_cut_hybrid_HS_channel_normalization"].endswith("V16_02")
    assert result["geometry"]["post_cut_hybrid_nonabelian_coexact_vertex"].endswith("V16_03")
    assert result["geometry"]["post_cut_hybrid_nonabelian_derham_response"].endswith("V16_04")
    assert result["geometry"]["post_cut_hybrid_common_gauge_HS_pushforward"].endswith("V16_05")
    assert result["geometry"]["post_cut_hybrid_Sobolev_metric_soft_mode_lift"].endswith("V16_07")
    assert result["geometry"]["post_cut_persistence_Floquet"].startswith("DERIVED_HYBRID")


def test_downstream_standard_model_is_defined_on_actual_child_pullback():
    result = downstream_attachment_definition()
    assert result["M4_action"].startswith("Gamma_M4_physical=Pullback")
    assert result["derived_domain"].startswith("M4=R_t")
    assert result["derived_spatial_radius"].startswith("R4=A*B")
    assert result["free_conformal_zeta_energy"].startswith("E0=(59/30)")
    assert result["faithful_gauge_group"].endswith("/Z6")
    assert result["hypercharge_operator"].startswith("Y_BH=")
    assert "physical_CKM_and_PMNS_are_unobservable" in result["current_action_mixing_result"]
    assert result["internal_Dirac_spectrum"].startswith("lambda_ell")
    assert result["Yukawa_pullback"].startswith("integral_ds")
    assert result["gauge_normalization"].startswith("K_F")
    assert result["color"].startswith("closed_S3")
    assert result["neutrino"].startswith("omega_n")
    assert result["microscopic_coefficient_functor"].startswith("M_micro")
    assert "owned-C3-invariant_dimension_27" in result["intrinsic_action_fiber"]
    assert result["minimal_action_completion_signature"].startswith("one_universal")
    assert result["composite_Higgs_gap_equation"].startswith("Delta=K_LR")
    assert "N_T=sqrt(Delta1)" in result["round_cap_gauge_DtN"]
    assert result["full_gauge_composite_kernel"].startswith("K_LR,f")
    assert result["LR_susceptibility"].startswith("chi_LR=")
    assert result["unified_gauge_Yukawa_pushforward"].startswith("one_Gamma_boundary")
    assert "809.858537" in result["one_cycle_joint_gauge_Yukawa"]
    assert "NONZERO_UNIT_HS_BASIS_VERTEX" in result["one_cycle_joint_gauge_Yukawa"]
    assert "FLOQUET_MASS_IS_0" in result["one_cycle_joint_gauge_Yukawa"]
    assert "Y_f=y_f*I3" in result["cycle_family_centrality"]
    assert "7.0359e-5<1" in result["cycle_composite_gap"]
    assert "0.97828731" in result["cycle_scale_renormalization"]
    assert "3.104487" in result["proper_time_gauge_cone"]
    assert "2405.175268" in result["proper_ADM_DtN_gap"]
    assert "0.657256738" in result["reset_Hessian_and_matter_cones"]
    assert "H_eff=H_matter" in result["quadratic_backreaction_closure"]
    assert "852.168262>K_B" in result["quantum_cone_repair_gate"]
    assert "Gamma_1=1.27293717" in result["common_quantum_superdeterminant"]
    assert "NONCOMMUTING_RESPONSE_ENGINE" in result["common_source_Frechet_response"]
    assert "314_GLOBAL_KKT" in result["quantum_functional_accounting"]
    assert "NO_NYQUIST_DOUBLER" in result["rank16_U1_HS_vertex_matrices"]
    assert "diag(9,9,3,3)" in result["HS_channel_normalization"]
    assert "-2ad(F0z)" in result["nonabelian_deRham_response"]
    assert "Z_PAIR=0.002612911482" in result["common_gauge_HS_pushforward"]
    assert "1.0460221e7" in result["Sobolev_metric_soft_mode_lift"]
    assert result["electric_gauge_DtN"].startswith("N_0=Omega")
    assert result["evaluation_order"][0] == "solve_complete_child"
    assert result["evaluation_order"][-1] == "test_unique_actualization"


def test_payload_is_deterministic_and_constructive():
    payload = completion_payload()
    assert payload["validation_passed"]
    assert payload["active_calculation"].startswith("REINTEGRATE_THE_N3")
    assert payload["FULL_BHSM_COMPLETE"] is False
    first = deterministic_json(payload)
    second = deterministic_json(completion_payload())
    assert first == second
    assert "NaN" not in first and "Infinity" not in first
