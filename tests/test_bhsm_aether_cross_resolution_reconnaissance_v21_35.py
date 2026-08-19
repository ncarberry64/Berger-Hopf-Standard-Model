import ast
import json
from pathlib import Path

from bhsm.interface.aether_cross_resolution_reconnaissance_v21_35 import (
    boundary_jerk_weak_graph_domain_audit,
    completion_payload,
    deterministic_json,
    event_child_calderon_angle_stability_lemma,
    general_n_complete_child_reconstruction_statement,
    injected_n6_event_child_calderon_friedrichs_angle_audit,
    positive_duration_normal_adjoint_kernel_localization,
    soft_channel_positive_duration_observability_jet_lemma,
    soft_calderon_second_graph_domain_reduction,
    soft_second_graph_coefficient_bundle_audit,
    soft_uniform_smooth_boundary_lift_audit,
    soft_boundary_acceleration_compactness_criterion,
    soft_jacobi_semigroup_compactness_reduction,
    jacobi_form_coefficient_mosco_theorem,
    actual_child_S2_compactness_audit,
    gauge_fixed_S2_propagation_theorem,
    normal_section_S2_compactness_scope,
    soft_normal_fredholm_compactness_dichotomy,
    continuum_normal_cauchy_completeness_reduction,
    normal_boundary_cauchy_symbol_factorization,
    n6_inverse_square_tail_closure_audit,
    actual_corrected_event_child_soft_evans_audit,
    soft_normal_lyapunov_schmidt_reduction,
    uniform_boundary_jerk_compactness_reduction,
    uniform_positive_duration_normal_closed_range_reduction,
    weak_calderon_boundary_generator_reduction,
    whole_system_time_translation_tangent_interface,
)


def test_persisted_n6_and_general_n_audits_have_replayable_returns():
    source = Path(
        "src/bhsm/interface/aether_cross_resolution_reconnaissance_v21_35.py"
    ).read_text(encoding="utf-8")
    tree = ast.parse(source)
    required = {
        "reaction_calderon_nested_schur_trace_audit",
        "sequential_action_energy_projection_audit",
        "n6_full_compatibility_extension_audit",
        "n6_event_child_weak_reaction_audit",
        "coherent_n5_exact_attachment_weak_child_audit",
        "general_n_principal_energy_certificate",
    }
    functions = {
        node.name: node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in required
    }
    assert functions.keys() == required
    for node in functions.values():
        top_level_returns = [
            item for item in node.body if isinstance(item, ast.Return)
        ]
        assert len(top_level_returns) == 1
        assert node.body[-1] is top_level_returns[0]


def test_persisted_n6_repaired_ordered_event_child_and_persistence():
    payload = json.loads(Path(
        "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
    ).read_text(encoding="utf-8"))["cross_resolution_reconnaissance"]
    event = payload["N6_coherent_ordered_event_repair_audit"]
    child = payload["N6_repaired_event_complete_child_candidate"]
    persistence = payload[
        "N6_repaired_event_complete_child_positive_duration_persistence"
    ]

    assert event["old_projected_event"][
        "passes_existing_event_tolerance"
    ] is False
    assert abs(event["lambda_ordered"]) < 1.0e-9
    assert event["maximum_constraint_residual"] < 1.0e-8
    assert event["eta_Legendre_minimum"] > 0.0
    assert event["new_equations_constraints_or_acceptance_gates"] is False

    assert child["final_physical_norm"] < 1.0e-9
    assert child["final_compatibility_maximum"] < 1.0e-9
    assert child["exact_attachment_jump_norm"] < 1.0e-12
    assert child["two_sided_reaction_match_norm"] < 1.0e-8
    assert child["complete_persistent_child_validated"] is True
    assert child["new_equations_constraints_or_acceptance_gates"] is False

    assert persistence[
        "positive_duration_relative_persistence_validated"
    ] is True
    assert persistence["nonzero_relative_evolution_retained"] is True


def test_n6_inverse_square_tail_closure_audit_is_fail_closed():
    audit = n6_inverse_square_tail_closure_audit()
    assert audit["validation_passed"] is True
    law = audit["action_derived_inverse_square_law"]
    assert law["proved_shell_estimate"] == (
        "norm(r_n,weak)<=C_r*n^-2_FOR_EACH_EVENT_OR_CHILD_COMPONENT_"
        "AND_norm(r_n,event_child)<=C_r_product*n^-2"
    )
    assert law["fitted_constant_used"] is False
    split = audit["exact_boundary_bulk_split"]
    assert split[
        "raw_boundary_distribution_used_in_the_bulk_tail_bound"
    ] is False
    inverse = audit["normal_inverse_summability"]
    assert inverse["sharp_power_threshold"] == "alpha<1"
    assert inverse["borderline_alpha_equal_one_is_summable"] is False
    assert inverse["uniform_inverse_case"]["series_bound_value"] == 8.0 / 49.0
    assert inverse[
        "allowed_growth_proved_below_threshold_for_BHSM_tail"
    ] is False
    asymptotic = audit["asymptotic_high_shell_fredholm_theorem"]
    assert asymptotic["asymptotic_inverse_growth"] == (
        "kappa_M=O(1),_alpha=0<1"
    )
    assert asymptotic[
        "asymptotic_inverse_square_correction_is_summable"
    ] is True
    assert asymptotic["summed_high_tail_bound"] == (
        "sum_(n>M0)norm(delta_Y_n)<=(2*C_r_product/beta_P)*"
        "sum_(n>M0)n^-2<=2*C_r_product/(beta_P*M0)"
    )
    assert asymptotic["uses_a_higher_N_complete_child_root"] is False
    bridge = audit["finite_bridge_obstruction"]
    assert bridge["hard_momentum_channel_closed"] is True
    assert bridge["finite_bridge_certified"] is False
    assert bridge["brute_force_complete_roots_for_every_N_required"] is False
    joint = audit["joint_event_child_tail"]
    assert joint["event_first_omitted_shell_bound"] == "C_r_event/49"
    assert joint["product_first_omitted_shell_bound"] == "C_r_product/49"
    assert joint["event_tail_numeric_probe_required_for_the_proof"] is False
    assert joint["child_only_tail_used_as_the_whole_system_defect"] is False
    response = audit["identity_response_trace_consistency"]
    assert response["pointwise_exact_at_finite_quadrature"] is False
    assert response["converges_to_the_exact_identity_response"] is True
    assert response["rows"][-1]["maximum_sigma_error"] < response["rows"][0][
        "maximum_sigma_error"
    ]
    scalar = audit["finite_bridge_soft_scalar_reduction"]
    assert scalar["soft_denominator"] == "d_s(t)=D_t-C_t*A_t^(-1)*B_t"
    assert scalar[
        "endpoint_nonzero_measurements_prove_no_interior_crossing"
    ] is False
    assert scalar["new_equation_constraint_gate_or_selector"] is False
    nonlinear = audit["nonlinear_Hessian_remainder"]
    assert nonlinear[
        "eta_persistence_neighborhood_closed_for_the_whole_tail"
    ] is False
    assert nonlinear["asymptotic_tail_only_radii_polynomial_closes"] is True
    assert nonlinear["full_N6_to_infinity_radii_polynomial_closes"] is False
    assert nonlinear["repository_radii_polynomial"] == (
        "p(r)=Y+(Z0+Z1-1)*r+Z2*r^2"
    )
    assert audit["infinite_tail_complete_child_constructed"] is False
    assert audit["category_3_collapse_sequence_constructed"] is False
    assert audit[
        "equations_gates_running_law_or_frozen_predictions_changed"
    ] is False


def test_n6_n12_joint_schur_chord_probe_is_fail_closed():
    payload = json.loads(Path(
        "artifacts/BHSM_N6_N12_JOINT_SCHUR_CHORD_COVER.json"
    ).read_text(encoding="utf-8"))
    probe = payload["latest_probe"]
    cover = probe["affine_schur_interval_cover"]
    status = probe["certification_status"]
    anchor = payload["finite_anchor_history"]
    assert probe["continuation_final_norm"] < anchor[
        "zero_padded_repaired_N6_in_N12_exact_joint_norm"
    ]
    assert probe["minimum_hard_singular"] > 0.0
    assert probe["minimum_full_schur_singular"] > 0.0
    assert probe["minimum_abs_soft_denominator"] > 0.0
    assert cover["accepted_interval_count"] + cover[
        "rejected_interval_count"
    ] > 0
    assert cover["accepted_interval_count"] > 0
    assert cover["rejected_interval_count"] == 0
    assert cover["minimum_certified_hard_gap"] > 0.0
    assert cover["minimum_certified_full_gap"] > 0.0
    assert cover["minimum_certified_soft_denominator"] > 0.0
    assert status["fixed_paired_linear_schur_homotopy_enclosed"] is True
    assert status["paired_slopes_are_proposal_curvature_only"] is True
    assert status["nonlinear_segment_radii_polynomials_certified"] is False
    assert status["CONTINUUM_EVENT_CHILD_CERTIFIED"] is False
    assert payload["higher_N_complete_child_promoted"] is False
    assert payload["frozen_predictions_touched"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False


def test_persisted_n6_local_energy_reconnaissance_is_not_mass():
    payload = json.loads(Path(
        "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
    ).read_text(encoding="utf-8"))["cross_resolution_reconnaissance"]
    audit = payload["N6_reduced_local_energy_readout_reconnaissance"]
    assert audit["validation_passed"] is True
    assert audit["is_Delta_H6"] is False
    assert audit["is_a_mass_measurement"] is False
    assert audit["v14_54_conditional_contract"][
        "complete_Q_xi_evaluator_exists"
    ] is False
    assert audit["family_cycle_ownership_gate"]["gate_closed"] is False
    assert audit["new_mass_formula_invented"] is False


def test_uniform_positive_duration_normal_closed_range_reduction():
    audit = uniform_positive_duration_normal_closed_range_reduction()
    assert audit["validation_passed"] is True
    closed = audit["already_closed_uniform_blocks"]
    assert closed["canonical_principal_absolute_gap"] > 0.0
    assert closed["uniform_attachment_trace_infsup"] > 0.0
    soft = audit["isolated_soft_momentum_channel"]
    assert soft["finite_N_exact_response_projection_magnitude"] > 0.0
    assert soft["legitimate_child_manifold_tangent"] is False
    assert soft["finite_N_zero_mode"] is False
    assert audit["failure_localization"][
        "uniform_failure_demonstrated"
    ] is False
    assert audit[
        "new_physics_equations_constraints_regularizers_objectives_or_gates"
    ] is False


def test_positive_duration_normal_adjoint_kernel_localization():
    audit = positive_duration_normal_adjoint_kernel_localization()
    assert audit["validation_passed"] is True
    implication = audit["positive_duration_energy_implication"]
    assert implication[
        "vanishing_finite_event_rows_already_prove_E_g(0)=0"
    ] is False
    soft = audit["soft_channel_consequence"]
    assert soft["is_a_finite_N_zero_mode"] is False
    assert soft["continuum_non_tangent_kernel_excluded"] is False
    assert soft["genuine_uniform_failure_demonstrated"] is False
    assert audit[
        "new_physics_equations_constraints_regularizers_objectives_or_gates"
    ] is False


def test_injected_n6_event_child_calderon_friedrichs_angle_audit():
    audit = injected_n6_event_child_calderon_friedrichs_angle_audit(
        points=96, maximum_order=13
    )
    assert audit["validation_passed"] is True
    assert audit["fixed_pair_event_to_history_Cauchy_completeness"] is True
    assert audit["minimum_measured_Friedrichs_sine"] > 0.0
    assert all(
        row["linearized_graph_intersection_dimension"] == 0
        for row in audit["rows"]
    )
    soft = audit["soft_mode_localization"]
    assert soft["action_owned_scale_coordinate"] is True
    assert soft["maximum_N12_N13_absolute_q_w_component"] < 3.0e-4
    assert soft[
        "complete_persistent_child_scale_family_integrability_proved"
    ] is False
    assert soft["promoted_as_a_legitimate_child_manifold_tangent"] is False
    assert soft["minimum_N12_N13_second_principal_angle_sine"] > 1.0e-2
    assert soft[
        "minimum_N8_N13_child_time_tangent_alignment_cosine"
    ] > 0.99
    assert soft[
        "minimum_N8_N13_event_time_tangent_alignment_cosine"
    ] > 0.99
    assert soft["time_translation_field_D_t_U_is_a_Jacobi_tangent"] is True
    assert soft["common_event_child_time_tangent_limit_proved"] is False
    assert audit[
        "uniform_nonlinear_child_bundle_Cauchy_completeness"
    ] is False
    assert audit[
        "new_physics_equations_constraints_regularizers_objectives_or_gates"
    ] is False


def test_event_child_calderon_angle_stability_lemma():
    audit = event_child_calderon_angle_stability_lemma()
    assert audit["validation_passed"] is True
    exact = audit["normal_exact_sequence"]
    assert exact["boundary_normal_quotient_dimension"] == 7
    assert all(
        row["dimension_identity_remainder"] == 0 for row in exact["rows"]
    )
    stability = audit["projector_stability_lemma"]
    assert stability["reference_gap"] > 0.0
    assert (
        stability[
            "fixed_injected_N6_through_N13_total_projector_change_budget"
        ]
        == 0.5 * stability["reference_gap"]
    )
    assert audit["uniform_positive_angle_proved"] is False
    assert audit["candidate_scale_tangent_resolution"][
        "scale_family_integrability_proved"
    ] is False
    assert audit["candidate_scale_tangent_resolution"][
        "action_autonomy_makes_D_t_U_an_exact_Jacobi_tangent"
    ] is True
    assert audit[
        "new_physics_equations_constraints_regularizers_objectives_or_gates"
    ] is False


def test_whole_system_time_translation_tangent_interface():
    audit = whole_system_time_translation_tangent_interface()
    assert audit["validation_passed"] is True
    policy = audit["tangent_policy"]
    assert policy["classification_category"] == (
        "LEGITIMATE_TANGENT_DIRECTION_OF_THE_WHOLE_EVENT_CHILD_"
        "HISTORY_MANIFOLD"
    )
    assert policy["soft_Calderon_mode_reclassified_as_this_tangent"] is False
    assert policy[
        "soft_mode_may_be_quotiented_before_identification_proof"
    ] is False
    assert policy["removed_as_a_physical_defect"] is False
    assert policy["time_event_coordinate_or_multiplier_added"] is False
    assert policy["existing_positive_duration_gauge_quotient_preserved"] is True
    boundary = audit["boundary_identification"]
    assert boundary["minimum_N8_N13_child_alignment_cosine"] > 0.99
    assert boundary["minimum_N8_N13_event_alignment_cosine"] > 0.99
    normal = audit["normal_angle_after_tangent_quotient"]
    assert normal[
        "measured_N12_N13_minimum_second_principal_angle_sine"
    ] > 1.0e-2
    assert normal["uniform_general_N_lower_bound_proved"] is False
    assert audit[
        "new_physics_equations_constraints_regularizers_objectives_or_gates"
    ] is False


def test_soft_channel_positive_duration_observability_jet_lemma():
    audit = soft_channel_positive_duration_observability_jet_lemma()
    assert audit["validation_passed"] is True
    separation = audit["type_separation"]
    assert separation["boundary_alignment_implies_field_equality"] is False
    assert separation["soft_channel_is_reclassified_as_a_time_tangent"] is False
    assert separation["soft_channel_classification_category"] == (
        "NORMAL_DIRECTION_CONTROLLED_BY_THE_EXISTING_POSITIVE_"
        "DURATION_GAUGE_FIXED_JACOBI_EVOLUTION"
    )
    lemma = audit["one_dimensional_observability_lemma"]
    assert "tau^(5/2)" in lemma["L2_observability_lower_bound"]
    assert audit["current_evidence"]["N_uniform_jerk_bound_proved"] is False
    assert audit[
        "new_physics_equations_constraints_regularizers_objectives_or_gates"
    ] is False


def test_uniform_boundary_jerk_compactness_reduction():
    audit = uniform_boundary_jerk_compactness_reduction()
    assert audit["validation_passed"] is True
    fixed = audit["fixed_background_soft_observability"]
    assert fixed["homogeneous_history_kernel_possible"] is False
    assert "tau_fixed^(5/2)" in fixed["lower_bound"]
    bundle = audit["nonlinear_child_bundle_extension"]
    assert bundle["proved_from_N3_through_N6_examples"] is False
    assert bundle[
        "proved_by_the_oscillatory_N6_through_N10_constraint_projections"
    ] is False
    assert bundle["genuine_uniform_failure_demonstrated"] is False
    assert audit[
        "new_physics_equations_constraints_regularizers_objectives_or_gates"
    ] is False


def test_boundary_jerk_weak_graph_domain_audit():
    audit = boundary_jerk_weak_graph_domain_audit()
    assert audit["validation_passed"] is True
    assert max(
        audit["N6_to_N10_classical_norm_growth"]["event"][
            "velocity_H5_norm"
        ],
        audit["N6_to_N10_classical_norm_growth"]["event"][
            "multiplier_H6_norm"
        ],
    ) > 10.0
    assert all(
        ratio < 1.6
        for side in audit["N6_to_N10_weak_graph_norm_growth"].values()
        for ratio in side.values()
    )
    reclassified = audit["reclassification"]
    assert reclassified[
        "uniform_H6_bundle_bound_is_an_existing_BHSM_gate"
    ] is False
    assert "WEAK_EULER_DIRAC_GRAPH_DOMAIN" in reclassified[
        "correct_history_domain"
    ]
    assert audit["genuine_uniform_closed_range_failure_demonstrated"] is False
    assert audit[
        "new_physics_equations_constraints_regularizers_objectives_or_gates"
    ] is False


def test_weak_calderon_boundary_generator_reduction():
    audit = weak_calderon_boundary_generator_reduction()
    assert audit["validation_passed"] is True
    evolution = audit["boundary_evolution"]
    assert "(I-P_N)A_NP_N" in evolution["projector_speed_bound"]
    assert evolution["tangential_block_cancels"] == "P_N*A_N*P_N"
    assert evolution["single_valued_DtN_chart_required"] is False
    owned = audit["already_owned_constants"]
    assert owned["uniform_trace_right_lift_bound"] < 5.0
    assert owned["validated_positive_duration"] > 0.0
    assert owned["validated_eta_margin_on_the_existing_witness"] > 0.0
    assert audit["open_uniform_constants"][
        "static_N_projector_differences_bound_D_t_P_N"
    ] is False
    assert "NOT_YET" in audit["open_uniform_constants"][
        "A_soft_parallel_amplitude_generator"
    ]
    failure = audit["failure_localization"]
    assert failure[
        "genuine_uniform_normal_closed_range_failure_demonstrated"
    ] is False
    assert failure["classification_category"] == (
        "NORMAL_DIRECTION_CONTROLLED_BY_THE_EXISTING_POSITIVE_"
        "DURATION_GAUGE_FIXED_JACOBI_EVOLUTION"
    )
    assert audit[
        "new_physics_equations_constraints_regularizers_objectives_or_gates"
    ] is False


def test_soft_calderon_second_graph_domain_reduction():
    audit = soft_calderon_second_graph_domain_reduction()
    assert audit["validation_passed"] is True
    scale = audit["graph_scale"]
    assert "D_t_xi_IN_D1" in scale["second_graph_domain"]
    assert scale["new_physical_domain_or_acceptance_condition"] is False
    identity = audit["exact_jerk_identity"]
    assert "[D_t,Gamma_acc,N]" in identity["boundary_jerk"]
    assert identity[
        "third_or_fourth_order_solver_proposal_derivative_required"
    ] is False
    insufficient = audit["why_first_graph_energy_is_insufficient"]
    assert insufficient["measured_L2_boundary_trace_loglog_slope"] > 0.4
    assert abs(insufficient["measured_H1_boundary_trace_loglog_slope"]) < 0.1
    assert insufficient[
        "trace_of_D_t_xi_controlled_by_first_energy_alone"
    ] is False
    failure = audit["failure_dichotomy"]
    assert failure[
        "genuine_uniform_normal_closed_range_failure_demonstrated"
    ] is False
    assert audit[
        "new_physics_equations_constraints_regularizers_objectives_or_gates"
    ] is False


def test_soft_second_graph_coefficient_bundle_audit():
    audit = soft_second_graph_coefficient_bundle_audit()
    assert audit["validation_passed"] is True
    assert [row["N"] for row in audit["rows"]] == [6, 7, 8, 9, 10]
    assert audit["maximum_measured_growth"] < 1.5
    lemma = audit["differentiated_energy_lemma"]
    assert "[D_t,J_U]" in lemma["differentiated_equation"]
    assert lemma["new_BHSM_equation_or_gate"] is False
    gap = audit["remaining_gap"]
    assert gap[
        "uniform_initial_D2_lift_for_the_action_selected_soft_boundary_datum"
    ] is False
    assert gap[
        "genuine_uniform_normal_closed_range_failure_demonstrated"
    ] is False
    assert audit[
        "new_physics_equations_constraints_regularizers_objectives_or_gates"
    ] is False


def test_soft_uniform_smooth_boundary_lift_audit():
    audit = soft_uniform_smooth_boundary_lift_audit(maximum_order=16)
    assert audit["validation_passed"] is True
    assert all(
        row["boundary_right_inverse_defect"] < 1.0e-14
        for row in audit["rows"]
    )
    assert max(
        row["H6_operator_norm"] for row in audit["rows"]
    ) == min(row["H6_operator_norm"] for row in audit["rows"])
    vertical = audit["remaining_vertical_problem"]
    assert vertical["uniform_vertical_D2_bound_proved"] is False
    assert vertical[
        "genuine_uniform_normal_closed_range_failure_demonstrated"
    ] is False
    assert audit[
        "new_physics_equations_constraints_regularizers_objectives_or_gates"
    ] is False


def test_soft_boundary_acceleration_compactness_criterion():
    audit = soft_boundary_acceleration_compactness_criterion()
    assert audit["validation_passed"] is True
    modulus = audit["minimal_weighted_modulus"]
    assert "Omega_N" in modulus["definition"]
    assert "t^2/4" in modulus["pointwise_consequence"]
    hierarchy = audit["certificate_hierarchy"]
    assert hierarchy[
        "uniform_D2_bound_is_a_new_physical_acceptance_gate"
    ] is False
    assert hierarchy["uniform_global_H6_bound_required"] is False
    failure = audit["failure_policy"]
    assert failure["such_a_sequence_is_currently_constructed"] is False
    assert "L2" in failure["genuine_closed_range_failure_requires"]
    assert audit[
        "new_physics_equations_constraints_regularizers_objectives_or_gates"
    ] is False


def test_soft_jacobi_semigroup_compactness_reduction():
    audit = soft_jacobi_semigroup_compactness_reduction()
    assert audit["validation_passed"] is True
    lemma = audit["semigroup_compactness_lemma"]
    assert "Trotter" not in lemma["Trotter_Kato_conclusion"] or (
        "TO_ZERO" in lemma["Trotter_Kato_conclusion"]
    )
    evidence = audit["current_evidence"]
    assert evidence["uniform_principal_gap"] > 0.0
    assert evidence["uniform_trace_right_lift_bound"] < 5.0
    assert evidence["nonlinear_corrected_background_Mosco_convergence"] is False
    assert evidence[
        "action_selected_soft_Cauchy_vector_strong_convergence"
    ] is False
    failure = audit["failure_localization"]
    assert failure["failure_of_either_statement_proves_category_3"] is False
    assert failure["category_3_still_requires_L2_history_collapse"] is True
    assert audit[
        "new_physics_equations_constraints_regularizers_objectives_or_gates"
    ] is False


def test_jacobi_form_coefficient_mosco_theorem():
    audit = jacobi_form_coefficient_mosco_theorem()
    assert audit["validation_passed"] is True
    inventory = audit["retained_action_coefficient_inventory"]
    assert inventory["highest_radial_derivative_order"] == 1
    assert inventory["new_action_term"] is False
    conclusion = audit["form_and_resolvent_conclusion"]
    assert conclusion["Mosco_convergence"] is True
    assert conclusion[
        "strong_resolvent_convergence_for_a_common_stable_shift"
    ] is True
    assert conclusion["zero_frequency_normal_inverse_uniformity_inferred"] is False
    status = audit["closed_and_open"]
    assert status["operator_coefficient_to_Mosco_implication"] == "PROVED"
    assert status[
        "actual_corrected_child_bundle_has_an_N_uniform_S2_bound"
    ] is False
    assert status[
        "genuine_uniform_normal_closed_range_failure_demonstrated"
    ] is False
    assert audit[
        "new_physics_equations_constraints_regularizers_objectives_or_gates"
    ] is False


def test_actual_child_S2_compactness_audit():
    audit = actual_child_S2_compactness_audit()
    assert audit["validation_passed"] is True
    assert [row["N"] for row in audit["rows"]] == [3, 4, 5, 6]
    assert all(
        row["complete_persistent_child_validated"] for row in audit["rows"]
    )
    assert max(audit["N4_to_N6_norm_spread_ratios"].values()) < 1.3
    n56 = audit["comparisons"][-1]["restricted_relative_differences"]
    assert all(value < 0.2 for value in n56.values())
    gap = audit["theorem_gap"]
    assert gap["full_static_S2_estimate_from_snapshot_rows_is_valid"] is False
    assert gap["coupled_spatial_dynamic_S2_estimate_proved"] is False
    assert "D_chi_v" in gap["velocity_derivative_fact"]
    assert gap["genuine_uniform_failure_demonstrated"] is False
    assert audit[
        "new_physics_equations_constraints_regularizers_objectives_or_gates"
    ] is False


def test_gauge_fixed_S2_propagation_theorem():
    audit = gauge_fixed_S2_propagation_theorem()
    assert audit["validation_passed"] is True
    constants = audit["action_owned_constants"]
    assert constants["canonical_principal_absolute_gap"] > 0.0
    assert constants["weighted_Hardy_Poincare_constant"] > 0.0
    spatial = audit["spatial_Garding_estimate"]
    assert spatial["velocity_H1_controlled_by_this_static_estimate"] is False
    propagation = audit["positive_duration_velocity_propagation"]
    assert "Gronwall" not in propagation["Gronwall_bound"] or (
        "E_S2(t)" in propagation["Gronwall_bound"]
    )
    assert propagation["requires_nonzero_motion_to_vanish"] is False
    assert propagation["new_persistence_gate"] is False
    assert audit["proved_implication"][
        "initial_N_uniform_bound_proved_from_N3_to_N6"
    ] is False
    assert audit[
        "genuine_uniform_normal_closed_range_failure_demonstrated"
    ] is False
    assert audit[
        "new_physics_equations_constraints_regularizers_objectives_or_gates"
    ] is False


def test_normal_section_S2_compactness_scope():
    audit = normal_section_S2_compactness_scope()
    assert audit["validation_passed"] is True
    decomposition = audit["normal_tangent_decomposition"]
    assert decomposition["local_child_manifold_dimension"] == "6N-6"
    compactness = audit["correct_compactness_statement"]
    assert "ALL_COMPLETE_CHILD_ROOTS" in compactness["not_required"]
    assert compactness[
        "nonzero_motion_momentum_and_time_dependence_allowed"
    ] is True
    assert compactness["componentwise_or_coordinate_monotonicity_required"] is False
    assert compactness["new_branch_selector_added"] is False
    transfer = audit["propagation_transfer"]
    assert transfer["tangent_directions_enter_the_observability_inf_sup"] is False
    assert audit[
        "genuine_uniform_normal_closed_range_failure_demonstrated"
    ] is False
    assert audit[
        "new_physics_equations_constraints_regularizers_objectives_or_gates"
    ] is False


def test_soft_normal_fredholm_compactness_dichotomy():
    audit = soft_normal_fredholm_compactness_dichotomy()
    assert audit["validation_passed"] is True
    setup = audit["Fredholm_setup"]
    assert setup["normal_boundary_dimension"] == 7
    assert setup["Fredholm_index"] == 0
    assert setup["physical_tangent_kernel_included_in_normal_problem"] is False
    compactness = audit["compactness_contradiction"]
    assert "NONZERO_x_star" in compactness["limit"]
    policy = audit["classification_policy"]
    assert "L2_HISTORY_COLLAPSE" in policy["category_3_requires"]
    assert policy["genuine_uniform_failure_demonstrated"] is False
    assert policy["current_category"] == (
        "NORMAL_DIRECTION_CONTROLLED_BY_THE_EXISTING_POSITIVE_"
        "DURATION_GAUGE_FIXED_JACOBI_EVOLUTION"
    )
    assert audit[
        "new_physics_equations_constraints_regularizers_objectives_or_gates"
    ] is False


def test_continuum_normal_cauchy_completeness_reduction():
    audit = continuum_normal_cauchy_completeness_reduction()
    assert audit["validation_passed"] is True
    boundary = audit["boundary_Cauchy_vector"]
    assert boundary["dimension"] == 7
    assert boundary["existing_rows"] == [
        "ATTACHMENT_TRACE_3",
        "CANONICAL_MOMENTUM_2",
        "WEAK_DYNAMIC_REACTION_2",
    ]
    assert boundary["dimension_match_alone_proves_isomorphism"] is False
    assert boundary["new_Cauchy_datum_added"] is False
    uniqueness = audit["radial_uniqueness_reduction"]
    assert uniqueness["determinant"] != 0.0
    assert uniqueness["weighted_absolute_gap"] > 0.0
    assert uniqueness["seven_row_boundary_symbol_invertibility_proved"] is False
    symbol = audit["boundary_symbol_gap"]
    assert symbol["general_N_symbol_gap_proved"] is False
    consequence = audit["Fredholm_status"]
    assert consequence["continuum_normal_kernel"] == (
        "OPEN_PENDING_BOUNDARY_SYMBOL_GAP"
    )
    assert consequence[
        "uniform_normal_closed_range_on_each_S2_eta_precompact_bundle"
    ] is False
    assert consequence["global_unbounded_child_manifold_claimed"] is False
    assert consequence["category_3_failure_demonstrated"] is False
    assert audit[
        "new_physics_equations_constraints_regularizers_objectives_or_gates"
    ] is False


def test_normal_boundary_cauchy_symbol_factorization():
    audit = normal_boundary_cauchy_symbol_factorization()
    assert audit["validation_passed"] is True
    symbol = audit["action_normalized_symbol"]
    assert symbol["seven_by_seven_symbol"] == "B7=I3_TRACE_DIRECT_SUM_M4"
    assert symbol["single_valued_DtN_matrix_required"] is False
    fixed = audit["fixed_injected_pair"]
    assert fixed["minimum_exact_seven_by_seven_gap"] > 0.0
    assert fixed["finite_pair_Cauchy_completeness"] is True
    assert fixed["is_a_uniform_nonlinear_child_bundle_proof"] is False
    for row in fixed["rows"]:
        assert row["exact_seven_by_seven_boundary_symbol_gap"] > 0.0
        assert row["linearized_graph_intersection_dimension"] == 0
        assert (
            row["exact_seven_by_seven_boundary_symbol_gap"]
            >= row["universal_gamma_over_sqrt2_lower_bound"]
        )
    separation = audit["tangent_and_soft_separation"]
    assert separation[
        "near_intersection_identified_with_that_full_history_tangent"
    ] is False
    assert separation["conditional_value_promoted"] is False
    evans = audit["pole_safe_soft_Evans_factor"]
    assert evans["basis_and_DtN_pole_invariant"] is True
    assert evans["fixed_injected_pair_determines_e_soft_star"] is False
    assert evans[
        "actual_corrected_child_limit_and_soft_vector_identified"
    ] is False
    dichotomy = audit["uniform_closed_range_dichotomy"]
    assert dichotomy["fixed_pair_rank_proves_required_statement"] is False
    assert dichotomy["decreasing_injected_gap_proves_failure"] is False
    assert dichotomy["genuine_uniform_failure_demonstrated"] is False
    assert audit[
        "new_physics_equations_constraints_regularizers_objectives_or_gates"
    ] is False


def test_actual_corrected_event_child_soft_evans_audit():
    audit = actual_corrected_event_child_soft_evans_audit()
    assert audit["validation_passed"] is True
    assert [row["N"] for row in audit["rows"]] == [3, 4, 5, 6]
    for row in audit["rows"]:
        assert row["complete_persistent_child_validated"] is True
        assert row["attachment_configuration_jump_norm"] < 1.0e-10
        assert row["minimum_event_child_eta_Legendre"] > 0.0
        assert row["minimum_graph_symbol_singular_value"] > 0.0
        assert row["absolute_pole_safe_Evans_wedge"] > 0.0
    sequence = audit["sequence_diagnostic"]
    assert sequence["soft_factor_monotone_in_N"] is False
    assert sequence["four_independent_resolutions_prove_a_unique_limit"] is False
    assert sequence[
        "fixed_injected_background_substituted_for_actual_roots"
    ] is False
    policy = audit["classification_policy"]
    assert policy["legitimate_tangent_identified"] is False
    assert policy["genuine_uniform_normal_failure_demonstrated"] is False
    assert audit[
        "new_physics_equations_constraints_regularizers_objectives_or_gates"
    ] is False


def test_soft_normal_lyapunov_schmidt_reduction():
    audit = soft_normal_lyapunov_schmidt_reduction()
    assert audit["validation_passed"] is True
    normal = audit["normal_decomposition"]
    assert normal["hard_response_measurement"] > 0.0
    assert normal["new_branch_selector"] is False
    scalar = audit["soft_scalar"]
    assert scalar["is_an_added_equation"] is False
    assert scalar["finite_exact_response_projection"] > 0.0
    assert scalar["uniform_general_N_derivative_bound_proved"] is False
    assert scalar[
        "static_Evans_zero_alone_proves_history_closed_range_failure"
    ] is False
    history = audit["positive_duration_soft_operator"]
    assert history[
        "static_boundary_factor_may_vanish_while_history_is_observable"
    ] is True
    assert history[
        "uniform_history_lower_bound_proved_on_actual_sequence"
    ] is False
    classification = audit["three_way_classification"]
    assert classification[
        "category_1_proved_for_the_hard_test_soft_line"
    ] is False
    assert classification["category_3_proved"] is False
    correspondence = audit["nested_normal_section_correspondence"]
    assert correspondence[
        "root_chart_uniqueness_is_the_history_closed_range_theorem"
    ] is False
    assert correspondence[
        "all_three_hypotheses_currently_proved_together"
    ] is False
    compact = audit["compact_bundle_observability_implication"]
    assert compact["proves_category_2_if_hypotheses_close"] is True
    assert compact["actual_compact_background_Cauchy_set_proved"] is False
    assert audit[
        "new_physics_equations_constraints_regularizers_objectives_or_gates"
    ] is False


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
    injected_graph = payload["cross_resolution_reconnaissance"][
        "injected_matched_background_calderon_graph_audit"
    ]
    assert injected_graph["validation_passed"] is True
    assert [row["N"] for row in injected_graph["rows"]] == list(
        range(5, 14)
    )
    assert injected_graph["late_tail"]["maximum_projector_step"] < 0.02
    assert injected_graph["late_tail"]["minimum_projector_step"] < 0.001
    assert injected_graph["analytic_operator_theorem"][
        "nonlinear_root_manifold_convergence_implied"
    ] is False
    assert injected_graph[
        "raw_DtN_matrices_used_as_the_convergence_object"
    ] is False
    assert injected_graph["increase_N_nonlinear_roots_mechanically"] is False
    assert injected_graph[
        "new_equations_constraints_or_acceptance_gates"
    ] is False
    weak_tail = payload["cross_resolution_reconnaissance"][
        "weak_constraint_boundary_source_tail_audit"
    ]
    assert weak_tail["validation_passed"] is True
    assert weak_tail["exact_boundary_lapse_covector"][
        "belongs_to_bulk_constraint_failure"
    ] is False
    assert weak_tail["measured_loglog_tail_slope_N12_to_N40"] < -0.5
    assert weak_tail["strong_L2_constraint_codomain_required"] is False
    right_inverse = payload["cross_resolution_reconnaissance"][
        "weak_complete_child_normal_right_inverse_audit"
    ]
    assert right_inverse["validation_passed"] is True
    assert right_inverse["map"]["row_count"] == 19
    assert right_inverse["derivative"]["rank"] == 19
    assert right_inverse["center_residual"][
        "action_normalized_total_norm"
    ] < 1.0e-8
    assert right_inverse["derivative"][
        "smallest_normal_singular_value"
    ] > 0.1
    assert right_inverse["derivative"][
        "right_inverse_defect_operator_norm"
    ] < 1.0e-9
    assert right_inverse[
        "new_equations_constraints_or_acceptance_gates"
    ] is False
    lipschitz = payload["cross_resolution_reconnaissance"][
        "weak_complete_child_normal_lipschitz_audit"
    ]
    assert lipschitz["validation_passed"] is True
    assert lipschitz["normal_dimension"] == 19
    assert lipschitz["two_scale_tensor_relative_change"] < 5.0e-2
    measured_radii = lipschitz["finite_N_measured_radii_polynomial"]
    assert measured_radii["discriminant"] > 0.0
    assert len(measured_radii["negative_interval_roots"]) == 2
    assert measured_radii[
        "is_a_rigorous_infinite_dimensional_existence_proof"
    ] is False
    assert lipschitz[
        "new_equations_constraints_or_acceptance_gates"
    ] is False
    boundary_layer = payload["cross_resolution_reconnaissance"][
        "weak_boundary_layer_radii_obstruction_audit"
    ]
    assert boundary_layer["validation_passed"] is True
    assert boundary_layer["boundary_H_minus_1_tail_norm"] > 0.2
    assert boundary_layer[
        "minimum_principal_correction_to_radius_ratio"
    ] > 1.0e3
    assert min(
        boundary_layer[
            "asymptotic_cutoff_estimates_to_reach_that_radius"
        ].values()
    ) > 1.0e8
    assert boundary_layer["validation"][
        "finite_N6_root_and_persistence_remain_valid"
    ] is True
    assert boundary_layer[
        "new_equations_constraints_or_acceptance_gates"
    ] is False
    parametrix = payload["cross_resolution_reconnaissance"][
        "casimir_boundary_layer_parametrix_audit"
    ]
    assert parametrix["validation_passed"] is True
    assert parametrix["map"]["Jacobian_rank"] == parametrix["map"]["rows"]
    assert parametrix["map"]["smallest_nonzero_singular_value"] < 1.0e-10
    assert parametrix["strict_exact_merit_reduction_found"] is False
    assert parametrix["q_only_finite_boundary_layer_lift_promoted"] is False
    assert parametrix["is_a_higher_N_complete_child_root"] is False
    assert parametrix[
        "new_equations_constraints_or_acceptance_gates"
    ] is False
    hard_response = payload["cross_resolution_reconnaissance"][
        "mixed_euler_dirac_hard_momentum_response_audit"
    ]
    assert hard_response["validation_passed"] is True
    assert hard_response["exact_full_weak_norm"]["after"] < (
        hard_response["exact_full_weak_norm"]["before"]
    )
    assert hard_response["exact_momentum_dual_norm"]["after"] < (
        hard_response["exact_momentum_dual_norm"]["before"]
    )
    assert hard_response["eta_Legendre_minimum"] > 0.0
    assert hard_response["soft_channel"][
        "is_a_legitimate_child_manifold_tangent"
    ] is False
    assert hard_response["soft_channel"][
        "uniform_normal_closed_range_failure_proved"
    ] is False
    assert hard_response[
        "new_equations_constraints_regularizers_objectives_or_gates"
    ] is False


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
