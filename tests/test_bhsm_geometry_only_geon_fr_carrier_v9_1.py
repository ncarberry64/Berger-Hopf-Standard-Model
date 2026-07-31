from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

from bhsm.interface.master_action import (
    eight_dimensional_vacuum_flavor_completion as v90,
    geometry_only_geon_fr_carrier_completion as v91,
)


ROOT = Path(__file__).resolve().parents[1]


def test_configuration_space_is_exactly_typed_and_framed():
    row = v91.configuration_space_definition()
    assert row["spacetime"] == "M8=I_t x S7"
    assert row["canonical_spatial_manifold"].startswith("Sigma=S7")
    assert row["spin_structure"].startswith("unique")
    assert "s>9/2" in row["regularity"]["metrics"]
    assert "(0,fr)" in row["gauge_group"]
    assert row["large_diffeomorphisms_quotiented"] is False
    assert row["topology_change_allowed"] is False


def test_full_ansatz_moduli_and_collective_spaces_are_not_conflated():
    rows = v91.configuration_space_strata()
    assert len(rows) == 6
    assert rows[1]["space"] == "small-diffeomorphism quotient Q_geom^0"
    assert "cannot determine" in rows[3]["topology_use"]
    assert "undefined" in rows[-1]["topology_use"]


def test_small_diffeomorphism_quotient_has_no_order_two_fr_loop():
    row = v91.small_diffeomorphism_pi1_theorem()
    assert row["total_space_contractible"]
    assert row["action_free"]
    assert row["pi1_Q_geom_0"] == "0"
    assert row["nontrivial_order_two_loop"] is False
    assert row["nontrivial_FR_character"] is None
    assert row["FR_line_bundle"] is None


def test_large_diffeomorphism_z2_is_not_misidentified_as_rotation_exchange():
    row = v91.large_diffeomorphism_audit()
    assert row["orientation_preserving_mapping_class_group"].endswith("Z2")
    assert row["belongs_to_small_diff_quotient"] is False
    assert row["identified_with_two_pi_rotation"] is False
    assert row["identified_with_geon_exchange"] is False
    assert row["action_selects_between_characters"] is False
    assert row["local_spinor_bundle_produced"] is False


def test_prior_v66_mapping_space_result_is_preserved_but_not_promoted():
    row = v91.prior_fr_reconciliation()
    assert row["v6_6_pi1"] == "pi4(S3)=Z2"
    assert row["equal_to_Q_geom_0"] is False
    assert row["action_derived_map_from_Q_geom_0_to_v6_6_space"] is None
    assert row["promotion_in_v9_1"] is False


def test_all_requested_loop_candidates_are_classified():
    rows = v91.candidate_loop_ledger()
    assert len(rows) == 9
    by_name = {row["candidate"]: row for row in rows}
    assert by_name["2pi spatial rotation"]["order"] == 1
    assert by_name["Spin(8) triality permutation"]["order"] == 3
    assert by_name["connected-sum or handle geon"]["closed_in_Q_geom_0"] is False


def test_metric_does_not_naturally_select_g2_or_triality_projectors():
    row = v91.g2_selection_no_go()
    assert row["compatible_G2_fiber_for_fixed_metric_orientation"] == "SO(7)/G2=RP7"
    assert row["metric_selects_unique_point"] is False
    assert row["torsion_free_G2_on_S7"] is False
    assert "H^3(S7)=0" in row["torsion_free_topology_reason"]
    assert all(
        row[key] is None
        for key in ("eta_phi", "J_u", "Pi_10", "P_chi0", "P_chi1", "P_chi2")
    )


def test_fr_sign_line_cannot_masquerade_as_local_chiral_carrier():
    row = v91.local_carrier_no_go()
    assert row["local_spacetime_bundle"] is None
    assert row["Spin_1_3_Clifford_action"] is None
    assert row["left_right_chirality_operator"] is None
    assert row["configuration_to_M4_transgression"] is None


def test_topology_report_is_fail_closed_and_input_clean():
    report = v91.topology_status_report()
    assert report["validation_passed"]
    assert report["final_verdict"] == v91.FINAL_VERDICT
    assert report["physical_promotion"] is False
    assert report["measured_flavor_data_used"] is False
    assert report["new_fundamental_fermion_added"] is False
    assert report["frozen_predictions_changed"] is False


def test_closed_flrw_reduction_retains_lapse_and_has_exact_desitter_solution():
    row = v91.closed_flrw_reduction()
    assert "N(t)" in row["ansatz"]
    assert "lapse_constraint" in row
    assert row["exact_constraint_residual"] == "0"
    assert row["exact_evolution_residual"] == "0"
    assert row["stationary"] is False
    assert row["periodic"] is False
    assert row["Hamiltonian_reduction_supplies_stationary_vacuum"] is False


def test_closed_flrw_is_crosschecked_by_independent_numerical_methods():
    row = v91.flrw_numerical_crosscheck()
    assert row["classification"] == "ANSATZ_VALIDATION_ONLY"
    assert row["physical_promotion"] is False
    assert row["representative_inputs_are_physical"] is False
    assert row["methods_agree"]
    assert "certified residual bounds" in row["serialization_policy"]
    for bound in row["certified_residual_bounds"].values():
        assert bound["relation"] == "<"
        assert isinstance(bound["certified_upper_bound"], float)
    assert row["action_per_unit_S7_scipy"] == row["action_per_unit_S7_mpmath"]
    assert row["stationary_geon_constructed"] is False


def test_action_display_rounding_removes_cross_platform_quadrature_ulps():
    windows_value = -157.91486389119677
    linux_value = -157.91486389119675
    assert v91._stable_float(windows_value) == v91._stable_float(linux_value)


def test_berger_hopf_reduction_includes_connection_and_static_no_go():
    row = v91.berger_hopf_reduction()
    assert row["lapse_retained"]
    assert row["canonical_connection_curvature_included"]
    assert set(row["Einstein_shape_roots"]) == {"1/5", "1"}
    assert "<0" in row["vertical_derivative"]
    assert row["positive_scale_static_solution"] is False
    assert row["static_product_geon_vacuum"] is False


def test_remaining_ansatz_ladder_does_not_manufacture_a_branch():
    rows = v91.ansatz_ladder_audit()
    assert len(rows) == 5
    assert all(row["physical_vacuum_selected"] is False for row in rows)
    local = v91.cohomogeneity_one_and_localized_audit()
    assert local["cohomogeneity_one_wall"]["scalar_target_topological_charge"] is None
    assert local["localized_geon"]["existence_theorem"] is None


def test_vacuum_status_reports_no_physical_residual_for_an_unselected_vacuum():
    row = v91.vacuum_status()
    assert row["validation_passed"]
    assert row["action_selected_unique_vacuum"] is False
    assert row["stationary_geon_vacuum"] is None
    assert row["action_value_of_physical_vacuum"] is None
    assert row["physical_equation_residual"] is None
    assert row["physical_stability_spectrum"] is None


def test_no_go_names_every_failed_completion_requirement():
    row = v91.geometry_only_no_go_theorem()
    failed = row["failed_requirements"]
    assert len(failed) == 11
    assert failed["nontrivial_pi1_Q_geom"].startswith("PROVED_FALSE")
    assert failed["spinorial_composite_lift"].startswith("ABSENT")
    assert failed["positive_Gram_form"] == "NOT_EVALUABLE"
    assert row["stronger_than_numerical_nonfinding"]
    assert row["verdict"] == v91.FINAL_VERDICT


def test_dependency_graph_stops_at_the_first_missing_action_owned_arrows():
    rows = v91.dependency_graph()
    by_arrow = {row["node_or_arrow"]: row for row in rows}
    assert by_arrow["S8"]["status"] == "ACTION_OWNED"
    assert by_arrow["Q_geom^0 -> L_FR"]["value"] is None
    assert by_arrow["C_f -> A_f"]["value"] is None
    assert by_arrow["(G_f,Q_f,K_ud) -> V_BHSM"]["value"] is None


def test_composite_states_and_immersions_are_null_not_synthetic():
    row = v91.composite_immersion_audit()
    assert all(
        state is None
        for sector in row["nonlinear_states"].values()
        for state in sector.values()
    )
    assert all(value is None for value in row["immersions_C_f"].values())
    assert all(value is None for value in row["evaluated_derivatives_A_f"].values())
    assert row["chirality_gate"] == "BLOCKED"
    assert row["FR_sign_gate"] == "BLOCKED"


def test_physical_operators_current_matrix_and_invariants_fail_closed():
    row = v91.physical_operator_and_flavor_readout()
    assert all(
        row[key] is None
        for key in (
            "K8_gauge_fixed",
            "H8_gauge_fixed",
            "G_u",
            "Q_u",
            "G_d",
            "Q_d",
            "K_ud",
            "V_BHSM",
            "s12",
            "s13",
            "s23",
            "J",
        )
    )
    assert row["Gram_positivity_gate"] == "NOT_EVALUABLE"
    assert row["current_full_rank_gate"] == "NOT_EVALUABLE"
    assert row["physical_matrix_promoted"] is False
    assert row["comparison_with_external_data_performed"] is False


def test_mass_and_lepton_outputs_remain_null_without_scale_fitting():
    row = v91.mass_and_lepton_audit()
    assert row["universal_physical_scale"] is None
    assert row["charged_lepton_masses"] is None
    assert row["PMNS"] is None
    assert row["one_over_4pi_origin"] is None
    assert row["separate_sector_scales_fit"] is False


def test_minimal_extensions_are_compared_only_after_no_go_and_none_adopted():
    row = v91.minimal_extension_comparison()
    assert row["comparison_performed_only_after_geometry_no_go"]
    assert len(row["candidates"]) == 7
    assert row["candidate_closing_all_missing_arrows"] is None
    assert row["unique_minimal_extension"] is None
    assert row["extension_adopted"] is False
    assert row["BHSM_v2_parent_action_proposed"] is False


def test_completion_gate_and_full_report_preserve_original_action_scope():
    gate = v91.completion_gate_payload()
    report = v91.status_report()
    assert gate["version"] == "v9.1"
    assert gate["current_verdict"] == v91.FINAL_VERDICT
    assert gate["minimal_extension_adopted"] is False
    assert gate["BHSM_1_0_release_complete"] is False
    assert report["original_or_extended_action"] == "ORIGINAL_S8_ACTION_ONLY"
    assert report["validation_passed"]
    assert report["physical_matrix_promoted"] is False
    assert report["measured_flavor_data_used"] is False
    assert report["new_fundamental_fermion_added"] is False
    assert report["new_continuous_parameter_added"] is False


def test_materializer_is_byte_idempotent(tmp_path):
    first_paths = v91.materialize(tmp_path)
    first = {path.name: path.read_bytes() for path in first_paths}
    second_paths = v91.materialize(tmp_path)
    second = {path.name: path.read_bytes() for path in second_paths}
    assert first == second
    artifact = json.loads(
        (tmp_path / "artifacts" / f"{v91.ARTIFACT_NAME}.json").read_text(
            encoding="utf-8"
        )
    )
    assert artifact["physical_operator_and_flavor_readout"]["V_BHSM"] is None


def test_cli_json_and_markdown_are_fail_closed():
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "src")
    command = [
        sys.executable,
        "-m",
        "bhsm.interface",
        "geometry-only-geon-fr-status",
    ]
    json_run = subprocess.run(
        command + ["--format", "json"],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=True,
    )
    markdown_run = subprocess.run(
        command + ["--format", "markdown"],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=True,
    )
    assert json.loads(json_run.stdout)["final_verdict"] == v91.FINAL_VERDICT
    assert v91.FINAL_VERDICT in markdown_run.stdout
    assert "physical promotion: `false`" in markdown_run.stdout


def test_repository_artifact_and_theorem_report_match_the_implementation():
    artifact_path = ROOT / "artifacts" / f"{v91.ARTIFACT_NAME}.json"
    report_path = (
        ROOT / "docs" / "bhsm_geometry_only_geon_fr_carrier_completion_v9_1.md"
    )
    assert artifact_path.read_text(encoding="utf-8") == v91.deterministic_json(
        v91.status_report()
    )
    report = report_path.read_text(encoding="utf-8")
    assert v91.FINAL_VERDICT in report
    assert v91.NEXT_MISSING_OBJECT in report
    assert "pi_1(\\mathcal Q_{\\rm geom}^0)" in report


def test_v90_proxy_firewall_remains_unchanged():
    vacuum = v90.vacuum_proxy_crosscheck()
    lens = v90.lens_numerical_crosscheck()
    assert vacuum["classification"] == "PROXY_STRESS_TEST_ONLY"
    assert lens["classification"] == "PROXY_STRESS_TEST_ONLY"
    assert vacuum["physical_promotion"] is False
    assert lens["physical_promotion"] is False
