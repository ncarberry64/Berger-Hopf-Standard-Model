import json
from pathlib import Path

from bhsm.interface.aether_cross_resolution_reconnaissance_v21_35 import (
    completion_payload,
    deterministic_json,
    general_n_complete_child_reconstruction_statement,
)


def test_independent_cross_resolution_reconnaissance_contract():
    payload = completion_payload(points=32)
    result = payload["cross_resolution_reconnaissance"]
    assert payload["FULL_BHSM_COMPLETE"] is False
    assert payload["validation_passed"] is True
    assert [row["order"] for row in result["orders"]] == [3, 4, 5]
    assert all(
        not row["initialization"]["accepted_N3_trajectory_used"]
        for row in result["orders"]
    )
    assert [
        row["complete_child_structure"]["full_unreduced_child_row_count"]
        for row in result["orders"]
    ] == [14, 16, 18]
    assert result["questions"][
        "same_rank14_complete_child_reconstructs"
    ]["classification"] == "RECLASSIFIED"
    assert result["orders"][1]["initialization"]["eta_domain_admissible"] is True
    assert result["orders"][2]["initialization"]["eta_domain_admissible"] is False
    assert result["orders"][2]["local_flow"]["physical_probe_admissible"] is False
    assert result["questions"]["N5_confirms_or_contradicts_N4"][
        "answer"
    ] == "CURRENT_BRANCH_INADMISSIBLE_NO_CROSS_RESOLUTION_VERDICT"
    ownership = payload["ingredient_process_ownership_audit"]
    assert ownership["validation_passed"] is True
    assert ownership["eta_audit"]["classification"] == "ETA-D"
    assert ownership["ordered_event_ownership"][
        "classification"
    ] == "EVENT_ENCLOSURE_EQUIVALENCE_OPEN"
    assert ownership["cross_resolution_stage_status"]["N5"][
        "EVENT_STATUS"
    ] == "PASS_QUALITATIVE_TIME_NOT_QUADRATURE_CONVERGED"
    assert ownership["cross_resolution_stage_status"]["N4"][
        "CHILD_STATUS"
    ] == "PASS"
    scale = payload["physical_scale_accessibility_audit"]
    assert scale["validation_passed"] is True
    assert scale["physical_scale_coordinate"][
        "numerical_resolution_N_is_rho"
    ] is False
    assert scale["action_sector_ownership"][
        "C_ES_status"
    ] == "OPEN_UNDEFINED_NOT_ZERO"
    assert scale["event_approach_metric_audit"][
        "chi_E_status"
    ] == "OPEN_UNDEFINED_UNTIL_G_IS_DERIVED"
    assert scale["scale_sweep_falsification_protocol"][
        "global_encapsulation_cost_implemented"
    ] is False
    network = payload["breadth_first_closure_network_audit"]
    assert network["validation_passed"] is True
    assert network["doctrine"][
        "observed_particle_values_may_select_upstream_branch"
    ] is False
    assert network["interfaces"]["event_child_reconstruction_return"][
        "equations"
    ]["row_count"] == "2N+8"
    assert network["interfaces"]["generic_family_children_mixing"][
        "current_child_export_is_sufficient"
    ] is False
    flux_variation = network["dynamic_flux_variation_interface"]
    assert flux_variation["higher_variation_verdict"][
        "third_variation_alone_is_sufficient"
    ] is False
    assert flux_variation["physical_rows_or_gates_changed"] is False
    assert "RICHARDSON" in flux_variation[
        "immediate_unchanged_map_derivative"
    ]


def test_reconnaissance_serialization_is_deterministic():
    payload = completion_payload(points=32)
    first = deterministic_json(payload)
    second = deterministic_json(payload)
    assert first == second
    assert json.loads(first)["validation_passed"] is True


def test_latest_n4_child_checkpoint_uses_fixed_merit_full_space_proposal():
    payload = json.loads(Path(
        "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
    ).read_text(encoding="utf-8"))
    child = payload["cross_resolution_reconnaissance"][
        "N4_event_conditioned_complete_child_reconstruction"
    ]
    assert child["chart"]["solver_variable_count"] == 34
    assert child["chart"][
        "merit_reference_preserved_from_checkpoint"
    ] is True
    promotion = child["rolling_checkpoint_promotion"]
    assert promotion["eligible"] is True
    assert promotion["fixed_reference_merit_reduced"] is True
    assert promotion["componentwise_monotonicity_required"] is False
    assert child["complete_child_candidate_validated"] is True
    assert child["persistence_evaluated"] is True
    assert child["persistence_validated"] is True
    assert child["validation"]["dynamic_flux_closed"] is True
    assert child["physical_residuals"][
        "dynamic_flux_norm_at_1e-1"
    ] < 1.0e-5
    persistence = payload["cross_resolution_reconnaissance"][
        "N4_complete_child_positive_duration_persistence"
    ]
    assert persistence[
        "positive_duration_relative_persistence_validated"
    ] is True
    assert persistence["nonzero_relative_evolution_retained"] is True
    assert persistence["finite_duration_numerical_movie_converged"] is False
    n5 = payload["cross_resolution_reconnaissance"][
        "N5_independent_eta_branch_event_classification"
    ]
    assert n5[
        "qualitative_ordered_event_existence_validated"
    ] is True
    assert n5["quantitative_event_time_validated"] is False
    assert n5["accepted_N3_trajectory_or_N4_child_used"] is False
    assert len(n5["quadrature_runs"]) == 3
    assert payload["cross_resolution_reconnaissance"][
        "questions"
    ]["N5_confirms_or_contradicts_N4"]["event_child_confirmation"] is True
    n5_chart = payload["cross_resolution_reconnaissance"][
        "N5_event_conditioned_complete_child_chart_audit"
    ]
    assert n5_chart["physical_row_count"] == 18
    assert n5_chart["accepted_N3_trajectory_or_N4_child_used"] is False
    assert n5_chart["complete_child_candidate_validated"] is False
    assert n5_chart["physical_equations_changed"] is False
    assert n5_chart["event_definition_changed"] is False
    assert n5_chart["structurally_full_row_rank"] is True
    assert n5_chart["chart"][
        "dynamic_flux_jacobian_step_converged"
    ] is False
    n5_child = payload["cross_resolution_reconnaissance"][
        "N5_event_conditioned_complete_child_reconstruction"
    ]
    assert n5_child["continuation_checkpoint_used"] is True
    assert n5_child["proposal_model"][
        "fixed_merit_scaling_preserved_from_checkpoint"
    ] is True
    assert n5_child["solver"]["fixed_reference_merit_reduced"] is True
    assert n5_child["proposal_model"][
        "componentwise_monotonicity_required"
    ] is False
    assert n5_child["checkpoint_promotion_eligible"] is True
    assert n5_child["complete_child_candidate_validated"] is True
    assert n5_child["complete_persistent_child_validated"] is True
    assert n5_child["physical_residuals"]["dynamic_flux_norm"] < 2.0e-5
    assert n5_child["fiber_reduction"][
        "final_fixed_reference_merit"
    ] < 1.0e-12
    assert n5_child["fiber_reduction"][
        "new_rows_constraints_or_gates"
    ] is False
    assert "binary64_hex" in n5_child["child_state"]
    assert payload["cross_resolution_reconnaissance"][
        "N5_child_flux_step_and_outer_direction_audit"
    ]["physical_map_or_gate_changed"] is False
    persistence = payload["cross_resolution_reconnaissance"][
        "N5_complete_child_positive_duration_persistence"
    ]
    assert persistence[
        "positive_duration_relative_persistence_validated"
    ] is True
    assert persistence["nonzero_relative_evolution_retained"] is True
    assert persistence["finite_duration_numerical_movie_converged"] is True
    frame = payload["cross_resolution_reconnaissance"][
        "cross_resolution_principal_symbol_frame_audit"
    ]
    assert frame["validation_passed"] is True
    assert all(
        row["maximum_raw_shift_ratio_C2_beta2_over_N2"] > 1.0
        for row in frame["rows"]
    )
    assert all(
        row["canonical_K_positive_on_sampled_open_cap"]
        for row in frame["rows"]
    )
    assert frame["raw_crossing_is_a_physical_defect"] is False
    assert frame["raw_crossing_is_a_new_acceptance_gate"] is False
    assert frame["N5_over_N4_weighted_principal_minimum_ratio"] > 0.5
    assert frame[
        "principal_geometry_degeneracy_supported_as_the_owner_of_the_"
        "reported_full_map_small_singular_values"
    ] is False
    strong = payload["cross_resolution_reconnaissance"][
        "cross_resolution_strong_constraint_infsup_audit"
    ]
    assert strong["validation_passed"] is True
    assert all(
        row["normalizations"]["strong_H4"]["rank"]
        == row["normalizations"]["strong_H4"]["row_count"]
        for row in strong["rows"]
    )
    assert strong["rows"][2]["normalizations"]["weak_Hminus6_dual"][
        "rank"
    ] < strong["rows"][2]["normalizations"]["weak_Hminus6_dual"][
        "row_count"
    ]
    assert strong["physical_rows_changed"] is False
    assert strong["acceptance_gates_changed"] is False
    boundary = payload["cross_resolution_reconnaissance"][
        "cross_resolution_boundary_symplectic_polarization_audit"
    ]
    assert boundary["validation_passed"] is True
    assert boundary["action_Hessian_itself_is_a_positive_boundary_norm"] is False
    assert boundary[
        "taking_entrywise_or_spectral_absolute_values_is_action_derived"
    ] is False
    assert boundary["required_positive_polarization"][
        "J_boundary_derived_now"
    ] is False
    assert boundary["required_positive_polarization"][
        "blocks_general_N_root_relation_convergence"
    ] is False
    assert boundary["fixed_analytic_boundary_norm_for_general_N"][
        "requires_a_positive_Calderon_polarization"
    ] is False
    assert [
        row["Hamiltonian_generator_type"] for row in boundary["rows"]
    ] == [
        "HYPERBOLIC_HYPERBOLIC",
        "HYPERBOLIC_ELLIPTIC",
        "HYPERBOLIC_ELLIPTIC",
    ]
    assert boundary["N3_may_be_declared_underresolved_from_this_alone"] is False
    assert boundary["physical_rows_changed"] is False
    assert boundary["acceptance_gates_changed"] is False
    lift = payload["cross_resolution_reconnaissance"][
        "nested_attachment_lift_consistency_audit"
    ]
    assert lift["validation_passed"] is True
    assert all(
        row["block_relative_changes"]["trace"] < 1.0e-13
        and row["block_relative_changes"]["strong_H4_constraints"] < 1.0e-13
        and row["block_relative_changes"]["energy"] < 1.0e-12
        for row in lift["comparisons"]
    )
    assert all(
        row["block_relative_changes"]["attachment_momentum"] > 0.5
        for row in lift["comparisons"]
    )
    assert lift[
        "current_lift_may_be_promoted_as_a_general_N_Calderon_projector"
    ] is False
    assert lift["new_physics_rows_constraints_or_gates_added"] is False
    reaction = payload["cross_resolution_reconnaissance"][
        "on_shell_boundary_reaction_audit"
    ]
    assert reaction["validation_passed"] is True
    assert reaction["N5_exact_checkpoint_measurement"][
        "validated_dynamic_F18_norm"
    ] < 2.0e-7
    assert reaction["N5_exact_checkpoint_measurement"][
        "raw_two_sided_radial_flux_norm"
    ] > 1.0
    assert reaction[
        "current_Hessian_minimal_lift_promoted_as_general_N_physics"
    ] is False
    assert reaction["validated_finite_N_F18_root_changed"] is False
    assert reaction["new_equations_constraints_or_acceptance_gates"] is False
    bvp = payload["cross_resolution_reconnaissance"][
        "child_history_bvp_bordered_operator_audit"
    ]
    assert bvp["validation_passed"] is True
    assert [row["bordered_dimension"] for row in bvp["rows"]] == [18, 23, 28]
    assert all(
        row["bordered_rank"] == row["bordered_dimension"]
        for row in bvp["rows"]
    )
    assert bvp["probe_boundary_acceleration_is_a_physical_junction_solution"] is False
    assert bvp["finite_rank_implies_uniform_general_N_inf_sup"] is False
    assert bvp["existing_N3_N4_N5_F_rows_or_persistence_changed"] is False
    assert bvp["new_equations_constraints_or_acceptance_gates"] is False
    match = payload["cross_resolution_reconnaissance"][
        "event_child_two_sided_reaction_match_audit"
    ]
    assert match["validation_passed"] is True
    assert all(
        row["two_sided_reaction_match_norm"] < 1.0e-6
        for row in match["rows"]
    )
    assert match[
        "configuration_or_rate_continuity_imposed_as_a_new_gate"
    ] is False
    assert match["accepted_F_N_roots_or_persistence_changed"] is False
    assert match["new_equations_constraints_or_acceptance_gates"] is False
    energy = payload["cross_resolution_reconnaissance"][
        "action_energy_topology_coherent_event_audit"
    ]
    assert energy["validation_passed"] is True
    assert energy["projection_comparison"][
        "H6_H5_H6_projection_eta_minimum"
    ] <= 0.0
    assert energy["projection_comparison"][
        "action_energy_projection_eta_minimum"
    ] > 0.0
    assert energy["coherent_N4_to_N5_event"]["branch_index"] == 10
    assert energy["coherent_complete_child_graph_validated"] is True
    assert energy["coherent_complete_child_persistence_validated"] is True
    graph = payload["cross_resolution_reconnaissance"][
        "coherent_N4_to_N5_complete_child_graph"
    ]
    assert graph["independent_N5_child_used_as_graph_seed"] is False
    assert graph["physical_equations_or_gates_changed"] is False
    assert graph["complete_child_candidate_validated"] is True
    assert graph["complete_persistent_child_validated"] is True
    assert graph["fiber_reduction"]["final_fixed_reference_merit"] < 1.0e-12
    assert graph["physical_residuals"]["dynamic_flux_norm"] < 2.0e-5
    coherent_persistence = payload["cross_resolution_reconnaissance"][
        "coherent_N4_to_N5_complete_child_positive_duration_persistence"
    ]
    assert coherent_persistence[
        "positive_duration_relative_persistence_validated"
    ] is True
    assert coherent_persistence["nonzero_relative_evolution_retained"] is True
    assert coherent_persistence[
        "finite_duration_numerical_movie_converged"
    ] is True
    schur = payload["cross_resolution_reconnaissance"][
        "reaction_calderon_nested_schur_trace_audit"
    ]
    assert schur["validation_passed"] is True
    assert all(
        row["exact_nested_bordered_matrix_error"] < 1.0e-12
        for row in schur["shell_rows"]
    )
    assert all(
        row["schur_correction_relative_to_low_operator"] > 1.0
        for row in schur["shell_rows"]
    )
    assert schur["trace_scaling"]["L2_trace_loglog_slope"] > 0.4
    assert abs(schur["trace_scaling"]["H1_trace_loglog_slope"]) < 0.1
    assert schur["derived_domain_reclassification"][
        "pure_state_energy_space_is_a_complete_Calderon_domain"
    ] is False
    assert schur["derived_domain_reclassification"][
        "new_physical_equation_constraint_or_gate"
    ] is False
    assert schur["finite_N_roots_events_or_persistence_changed"] is False
    weak = payload["cross_resolution_reconnaissance"][
        "weak_conormal_reaction_graph_audit"
    ]
    assert weak["validation_passed"] is True
    assert weak["uniform_attachment_trace_theorem"][
        "analytic_smallest_singular_lower_bound"
    ] > 0.0
    assert weak["uniform_attachment_trace_theorem"][
        "uniform_right_lift_norm_upper_bound"
    ] < 5.0
    assert weak["coherent_high_shell_tail"][
        "correction_norm_loglog_slope"
    ] < -1.0
    assert all(
        row["exact_raw_nested_operator_error"] < 1.0e-12
        for row in weak["coherent_high_shell_tail"]["rows"]
    )
    assert weak["mixed_weak_history_system"][
        "strong_boundary_acceleration_trace_required"
    ] is False
    assert weak["mixed_weak_history_system"][
        "new_equation_constraint_or_acceptance_gate"
    ] is False
    assert weak["uniform_general_N_graph_convergence_proved"] is False
    assert weak["finite_N_roots_events_persistence_or_gates_changed"] is False
    quotient = payload["cross_resolution_reconnaissance"][
        "boundary_compatible_gauge_quotient_audit"
    ]
    assert quotient["validation_passed"] is True
    assert quotient["principal_null_space"][
        "slice_intersects_principal_null_space_trivially"
    ] is True
    assert quotient["principal_null_space"][
        "retained_principal_determinant"
    ] == 8.0
    assert quotient["boundary_compatibility"][
        "quotient_changes_boundary_data"
    ] is False
    assert all(
        row["quotient_improvement_factor"] > 10.0
        for row in quotient["rows"]
    )
    assert quotient["rows"][-1]["quotient_soft_mode_blocks"][
        "shape_b"
    ] > 0.9
    assert quotient[
        "candidate_slice_promoted_as_a_global_gauge_theorem"
    ] is False
    assert quotient[
        "instantaneous_Cauchy_matrix_is_the_full_history_Jacobi_operator"
    ] is False
    assert quotient["finite_N_children_or_gates_changed"] is False
    sequential = payload["cross_resolution_reconnaissance"][
        "sequential_action_energy_projection_audit"
    ]
    assert sequential["validation_passed"] is True
    assert [row["N"] for row in sequential["rows"]] == [6, 7, 8, 9, 10]
    assert all(
        row[label]["maximum_constraint_residual"] < 1.0e-8
        and row[label]["eta_Legendre_minimum"] > 0.0
        and "coordinate_time_vector_timelike_margin" in row[label]
        and "projected_state_binary64_hex" in row[label]
        for row in sequential["rows"] for label in ("event", "child")
    )
    assert sequential[
        "complete_child_dynamic_reaction_rows_solved_at_N6_TO_N10"
    ] is False
    jacobi = payload["cross_resolution_reconnaissance"][
        "positive_duration_gauge_fixed_jacobi_audit"
    ]
    assert jacobi["validation_passed"] is True
    assert jacobi["principal_energy_estimate"][
        "absolute_principal_smallest_eigenvalue"
    ] > 0.0
    assert jacobi["principal_energy_estimate"][
        "proves_finite_N5_weak_Jacobi_well_posedness_modulo_kernel"
    ] is True
    assert jacobi["principal_energy_estimate"][
        "proves_N_uniform_normal_gap"
    ] is False
    assert jacobi["remaining_shape_soft_mode"][
        "is_a_principal_gauge_kernel"
    ] is False
    assert jacobi["normal_kernel_policy"][
        "child_manifold_tangent_kernel_is_physical_and_retained"
    ] is True
    assert jacobi["new_action_terms_equations_constraints_or_gates"] is False
    n6_extension = payload["cross_resolution_reconnaissance"][
        "N6_full_compatibility_extension_audit"
    ]
    assert n6_extension["validation_passed"] is True
    assert n6_extension["final_compatibility_norm"] < n6_extension[
        "initial_compatibility_norm"
    ]
    assert n6_extension["complete_dynamic_reaction_rows_solved"] is False
    assert n6_extension["is_a_complete_N6_child_claim"] is False
    assert n6_extension[
        "new_equations_constraints_or_acceptance_gates"
    ] is False
    boundary_match = payload["cross_resolution_reconnaissance"][
        "N6_complete_boundary_BVP_match_audit"
    ]
    assert boundary_match["validation_passed"] is True
    assert boundary_match["final_exact_attachment_jump_norm"] < 1.0e-9
    assert boundary_match["final_compatibility_maximum"] < 1.0e-9
    assert boundary_match[
        "new_equation_constraint_or_acceptance_gate"
    ] is False
    reaction = payload["cross_resolution_reconnaissance"][
        "N6_event_child_weak_reaction_audit"
    ]
    assert reaction["validation_passed"] is True
    assert reaction["attachment_configuration_jump_norm"] < 1.0e-9
    assert reaction["two_sided_reaction_match_norm"] < 1.0e-6
    assert reaction["legacy_local_dynamic_flux_row_used"] is False
    assert reaction[
        "new_action_equation_constraint_or_acceptance_gate"
    ] is False
    n6_candidate = payload["cross_resolution_reconnaissance"][
        "N6_weak_complete_child_candidate"
    ]
    assert n6_candidate["complete_child_candidate_validated"] is True
    assert n6_candidate["complete_persistent_child_validated"] is True
    assert n6_candidate[
        "legacy_local_dynamic_flux_map_used_as_general_N_physics"
    ] is False
    n6_persistence = payload["cross_resolution_reconnaissance"][
        "N6_weak_complete_child_positive_duration_persistence"
    ]
    assert n6_persistence[
        "positive_duration_relative_persistence_validated"
    ] is True
    assert n6_persistence["nonzero_relative_evolution_retained"] is True
    assert n6_persistence[
        "finite_duration_numerical_movie_converged"
    ] is True
    n5_matched = payload["cross_resolution_reconnaissance"][
        "coherent_N5_exact_attachment_weak_child_audit"
    ]
    assert n5_matched["validation_passed"] is True
    assert n5_matched["final_exact_attachment_jump_norm"] < 1.0e-9
    assert n5_matched["final_compatibility_maximum"] < 1.0e-9
    assert n5_matched["two_sided_reaction_match_norm"] < 1.0e-6
    assert n5_matched["legacy_local_dynamic_flux_map_reopened"] is False
    assert n5_matched["new_equation_constraint_or_acceptance_gate"] is False
    n5_matched_candidate = payload["cross_resolution_reconnaissance"][
        "coherent_N5_exact_attachment_weak_child_candidate"
    ]
    assert n5_matched_candidate[
        "complete_persistent_child_validated"
    ] is True
    n5_matched_persistence = payload["cross_resolution_reconnaissance"][
        "coherent_N5_exact_attachment_positive_duration_persistence"
    ]
    assert n5_matched_persistence[
        "positive_duration_relative_persistence_validated"
    ] is True
    assert n5_matched_persistence[
        "nonzero_relative_evolution_retained"
    ] is True
    legacy_matched = payload["cross_resolution_reconnaissance"][
        "legacy_N3_N4_exact_attachment_weak_child_audit"
    ]
    assert legacy_matched["validation_passed"] is True
    assert [row["N"] for row in legacy_matched["rows"]] == [3, 4]
    assert all(
        row["final_exact_attachment_jump_norm"] < 1.0e-9
        and row["final_compatibility_maximum"] < 1.0e-9
        and row["two_sided_reaction_match_norm"] < 1.0e-6
        for row in legacy_matched["rows"]
    )
    assert legacy_matched[
        "legacy_local_dynamic_flux_maps_reopened"
    ] is False
    for order in (3, 4):
        candidate = payload["cross_resolution_reconnaissance"][
            f"N{order}_exact_attachment_weak_child_candidate"
        ]
        persistence = payload["cross_resolution_reconnaissance"][
            f"N{order}_exact_attachment_positive_duration_persistence"
        ]
        assert candidate["complete_persistent_child_validated"] is True
        assert persistence[
            "positive_duration_relative_persistence_validated"
        ] is True
        assert persistence["nonzero_relative_evolution_retained"] is True
    graph = payload["cross_resolution_reconnaissance"][
        "matched_weak_reaction_graph_convergence_audit"
    ]
    assert graph["validation_passed"] is True
    assert [row["N"] for row in graph["rows"]] == [3, 4, 5, 6]
    assert graph["general_N_convergence_proved"] is False
    assert graph[
        "raw_DtN_jump_reclassified_as_a_physical_graph_failure"
    ] is False
    assert all(
        comparison[
            "bounded_Calderon_graph_projector_operator_difference"
        ] <= 1.0
        for comparison in graph["comparisons"]
    )
    assert graph["increase_N_mechanically_as_the_next_step"] is False
    assert graph["new_equations_constraints_or_acceptance_gates"] is False


def test_general_n_reconstruction_statement_preserves_the_physical_map():
    statement = general_n_complete_child_reconstruction_statement()
    ledgers = statement["validated_resolution_ledger"]
    assert [row["whole_child_variables"] for row in ledgers] == [26, 34, 42]
    assert [row["compatibility_rows"] for row in ledgers] == [12, 14, 16]
    assert [row["complete_child_rows"] for row in ledgers] == [14, 16, 18]
    assert [
        row["compatibility_fiber_dimension"] for row in ledgers
    ] == [14, 20, 26]
    assert [
        row["complete_child_fiber_dimension"] for row in ledgers
    ] == [12, 18, 24]
    theorem = statement["local_reconstruction_theorem"]
    assert theorem["new_equations_constraints_or_acceptance_gates"] is False
    continuation = statement["cross_resolution_continuation_criterion"]
    assert continuation["extra_gauge_or_physical_selector_added"] is False
    transfer = statement["galerkin_transfer_certificate"]
    assert transfer["continuum_spaces"]["state_space"] == (
        "X_E=R_scale_CROSS_H1_radial_geometry_CROSS_L2_velocity_"
        "CROSS_H1_lapse_shift"
    )
    assert transfer["continuum_spaces"]["classical_regular_domain"] == (
        "X_s=H6_q_CROSS_H5_v_CROSS_H6_m"
    )
    assert transfer["continuum_spaces"][
        "pure_action_energy_state_space_is_the_complete_reaction_domain"
    ] is False
    assert "D_EULER_DIRAC" in transfer["continuum_spaces"][
        "reaction_Calderon_graph_domain"
    ]
    assert transfer["set_valued_continuum_relation"][
        "physical_branch_selector_added"
    ] is False
    calderon = transfer["event_to_child_on_shell_calderon_interface"]
    assert calderon["validated_finite_N_local_map"][
        "N3_N4_N5_roots_and_positive_duration_persistence"
    ] is True
    assert calderon["validated_finite_N_local_map"][
        "is_already_a_global_function_space_child_BVP"
    ] is False
    assert calderon["differentiated_BVP"][
        "N5_proposal_Jacobian_reopened"
    ] is False
    reaction = calderon["lift_independent_boundary_reaction"]
    assert reaction[
        "raw_Gamma1_event_plus_raw_Gamma1_child_is_sufficient"
    ] is False
    assert reaction[
        "existing_local_Hessian_lift_is_the_general_N_projector"
    ] is False
    symbol = calderon["retained_radial_principal_symbol_audit"]
    assert symbol["algebraic_rank"]["generic_rank"] == 3
    assert symbol["algebraic_rank"]["generic_nullity"] == 2
    assert symbol["physical_v_mode_coefficient"]["reduced"] == (
        "-2K*(1-C^2*beta^2/N^2)"
    )
    assert symbol["algebra_validation_passed"] is True
    assert symbol["new_physics_or_acceptance_gate"] is False
    weighted = calderon["weighted_pole_attachment_principal_estimate"]
    assert weighted["validation_passed"] is True
    assert weighted["canonical_physical_matrix"][
        "smallest_absolute_eigenvalue"
    ] > 0.0
    assert weighted["action_weight_factorization"][
        "uniform_general_N_bound_proved"
    ] is False
    assert weighted["new_equations_constraints_or_acceptance_gates"] is False
    assert calderon["new_action_terms_equations_constraints_or_gates"] is False
    assert transfer["current_evidence"][
        "finite_rank_implies_a_uniform_inf_sup_bound"
    ] is False
    assert transfer["solver_proposal_curvature_is_part_of_this_certificate"] is False
    assert transfer["new_equations_constraints_or_acceptance_gates"] is False
    assert statement["resolution_independent_limit_criterion"][
        "three_resolutions_alone_prove_the_limit"
    ] is False
    assert statement["FULL_BHSM_COMPLETE"] is False
