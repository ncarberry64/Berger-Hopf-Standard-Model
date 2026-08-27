import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"


def _load(name: str) -> dict:
    return json.loads((BASE / name).read_text(encoding="utf-8"))


def test_global_stop_reconnaissance_has_finite_bracket_and_open_margins() -> None:
    record = _load("BHSM_N12_C2_GLOBAL_CANONICAL_STOP_RECONNAISSANCE.json")
    bracket = record["candidate_first_stop_bracket"]
    margins = record["domain_trends"]
    assert record["status"] == "FINITE_GLOBAL_s_ZERO_BRACKET_RECONNAISSANCE_ONLY"
    assert bracket["action_length_left"] == 92.0
    assert bracket["action_length_trial"] == 94.0
    assert bracket["signed_descriptor_left"] > 0.0
    assert bracket["signed_descriptor_trial"] < 0.0
    assert bracket["Delta_left"] < 0.0
    assert margins["minimum_selected_eigenline_gap"] > 0.0
    assert margins["minimum_boundary_lapse"] > 0.0
    assert margins["minimum_boundary_radius"] > 0.0
    assert margins["minimum_cancelled_field_action_norm"] > 0.0
    assert record["candidate_stop_is_certified"] is False
    assert record["validation_passed"] is False
    assert record["FULL_BHSM_COMPLETE"] is False


def test_sampled_delta_concavity_is_strict_but_not_promoted() -> None:
    record = _load("BHSM_N12_C2_GLOBAL_DELTA_CONCAVITY_RECONNAISSANCE.json")
    rows = record["rows"]
    assert [row["index"] for row in rows] == [0, 12, 24, 27, 36, 46]
    assert all(row["selected_branch"] == 24 for row in rows)
    assert all(row["selected_eigenline_gap"] > 0.0 for row in rows)
    assert all(row["dDelta_da_interval"][1] < 0.0 for row in rows)
    assert record["sampled_center_concavity"][
        "every_outward_rounded_point_interval_is_strictly_negative"
    ] is True
    boundary = record["claim_boundary"]
    assert boundary["motion_between_sample_centers_interval_certified"] is False
    assert boundary["uniform_dDelta_da_negative_on_global_tube"] is False
    assert boundary["canonical_s_zero_first_hit_certified"] is False
    assert record["validation_passed"] is False
    assert record["FULL_BHSM_COMPLETE"] is False


def test_refined_stop_center_is_transverse_but_remains_reconnaissance() -> None:
    record = _load("BHSM_N12_C2_REFINED_CANONICAL_STOP_RECONNAISSANCE.json")
    stop = record["candidate_stop"]
    assert record["action_length"]["certified_core_to_candidate_stop"] > 92.0
    assert record["action_length"]["certified_core_to_candidate_stop"] < 94.0
    assert stop["Delta"] < 0.0
    assert stop["ds_da"] < 0.0
    assert stop["transverse_to_stop_face"] is True
    assert stop["selected_branch"] == 24
    assert stop["selected_eigenline_gap"] > 0.0
    assert stop["boundary_lapse"] > 0.0
    assert stop["boundary_radius"] > 0.0
    assert record["claim_boundary"]["between_core_and_stop_interval_shadowing"] is False
    assert record["validation_passed"] is False


def test_flow_cylinder_reduces_gate7_to_one_existence_witness() -> None:
    record = _load("BHSM_N12_GATE7_RESET_TO_STOP_FLOW_CYLINDER.json")
    theorem = record["theorem"]
    requirement = record["Gate7_requirement"]
    assert theorem["regular_child_dimension"] == 73
    assert theorem["Euler_Dirac_stop_face_dimension"] == 72
    assert theorem["flow_coordinate_dimension"] == 1
    assert requirement["classification"] == "EXISTENCE_ONLY"
    assert "AT_LEAST_ONE" in requirement["required"]
    assert "UNIVERSAL" in requirement["not_required"]
    assert requirement["proof_coordinate_witness_is_a_physical_selector"] is False
    assert record["claim_boundary"]["exact_flow_cylinder_theorem"] == "DERIVED"
    assert record["claim_boundary"]["finite_reset_to_stop_witness"] == "OPEN_CURRENT_OWNER"
    assert record["validation_passed"] is True
    assert record["FULL_BHSM_COMPLETE"] is False


def test_finite_stop_multiple_shooting_center_localizes_47_seams() -> None:
    record = _load("BHSM_N12_C2_STOP_MULTIPLE_SHOOTING_CENTER.json")
    mesh = record["mesh"]
    defect = record["center_defect_profile"]
    margins = record["sampled_domain_margins"]
    assert mesh["nodes"] == 48
    assert mesh["seams"] == 47
    assert mesh["action_length_stop"] > 92.0
    assert defect["worst_state_defect_seam"] == 0
    assert defect["worst_descriptor_defect_seam"] == 0
    assert defect["maximum_state_rate_defect_after_first_four_seams"] < 4.0e-7
    assert defect["first_four_seam_fraction_of_integrated_defect_proxy"] > 0.7
    assert margins["all_selected_branches_are_24"] is True
    assert margins["minimum_selected_eigenline_gap"] > 0.0
    assert margins["minimum_boundary_lapse"] > 0.0
    assert margins["minimum_boundary_radius"] > 0.0
    assert record["claim_boundary"]["between_node_interval_remainder_certified"] is False
    assert record["validation_passed"] is False
    assert record["FULL_BHSM_COMPLETE"] is False


def test_full_stop_boundary_cluster_spectrum_covers_all_3008_subspans() -> None:
    record = _load("BHSM_N12_C2_STOP_FULL_BOUNDARY_CLUSTER_SPECTRUM.json")
    rows = record["rows"]
    assert record["status"] == (
        "ALL_3008_STOP_PATH_BOUNDARY_CLUSTER_DENOMINATORS_CERTIFIED"
    )
    assert record["mesh"]["macro_seams"] == 47
    assert record["mesh"]["subspans_per_macro_seam"] == 64
    assert record["mesh"]["total_subspans"] == 3008
    assert [(row["seam"], row["subspan"]) for row in rows] == [
        (seam, subspan) for seam in range(47) for subspan in range(64)
    ]
    assert all(row["selected_branch"] == 24 for row in rows)
    assert all(row["all_three_quarter_gap_bootstraps_closed"] for row in rows)
    assert all(row["boundary_cluster_certificate_closed"] for row in rows)
    assert record["summary"]["minimum_selected_line_boundary_gap_lower"] > 0.0
    assert record["validation_passed"] is True
    assert record["claim_boundary"][
        "selected_line_on_reference_Hermite_stop_path"
    ] == "CERTIFIED_SIMPLE"
    assert record["claim_boundary"]["branchwise_selected_projector_tube"] == "OPEN"
    assert record["claim_boundary"]["Green_Hermite_shadowing"] == "OPEN"
    assert record["FULL_BHSM_COMPLETE"] is False


def test_full_stop_selected_projector_graph_is_uniformly_neumann_small() -> None:
    record = _load("BHSM_N12_C2_STOP_FULL_SELECTED_PROJECTOR_GRAPH.json")
    rows = record["rows"]
    assert record["status"] == (
        "ALL_3008_STOP_PATH_SELECTED_PROJECTOR_GRAPHS_CERTIFIED"
    )
    assert [(row["seam"], row["subspan"]) for row in rows] == [
        (seam, subspan) for seam in range(47) for subspan in range(64)
    ]
    assert all(row["selected_branch"] == 24 for row in rows)
    assert all(row["certified_global_gap_lower"] > 0.0 for row in rows)
    assert all(row["graph_Neumann_closed"] for row in rows)
    assert record["summary"]["maximum_selected_projector_motion_upper"] < 0.015
    assert record["summary"]["minimum_consumed_gap_lower"] > 0.0
    assert record["validation"][
        "far_branch_ordered_Weyl_denominators_combined_with_global_gap"
    ] is True
    assert record["claim_boundary"][
        "all_3008_selected_projector_graphs"
    ] == "CERTIFIED"
    assert record["claim_boundary"]["bordered_hard_response_tube"] == "OPEN"
    assert record["claim_boundary"]["Green_Hermite_shadowing"] == "OPEN"
    assert record["FULL_BHSM_COMPLETE"] is False
