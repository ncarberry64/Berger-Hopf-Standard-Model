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
        "X=H6_q_CROSS_H5_v_CROSS_H6_m"
    )
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
