from __future__ import annotations

import json
from pathlib import Path

from bhsm.interface.master_action import composite_carrier_current_reduction as v84


def test_exact_frozen_block_ranks():
    carriers = v84.frozen_composite_carriers()["sectors"]
    assert [row["block_rank"] for row in carriers["charged_lepton"]] == [1, 6, 10]
    assert [row["block_rank"] for row in carriers["up"]] == [1, 7, 11]
    assert [row["block_rank"] for row in carriers["down"]] == [1, 7, 9]


def test_exact_minimal_channel_table():
    assert v84.weak_current_channel_table()["matrix"] == [
        [[0, 0], [3, 0], [4, -2]],
        [[3, 3], [3, 3], [1, 1]],
        [[5, 4], [4, 4], [2, 2]],
    ]


def test_minimal_right_clebsch_gordan_coefficients_are_nonzero():
    result = v84.right_clebsch_gordan_witnesses()
    assert result["all_minimal_right_CG_coefficients_nonzero"] is True
    assert [row["coefficient"] for row in result["rows"]] == [
        "1", "-sqrt(7)/7", "1/3",
        "1", "-sqrt(6)/6", "1/6",
        "1", "2*sqrt(455)/65", "-sqrt(105)/15",
    ]


def test_normalized_peter_weyl_reduced_elements():
    result = v84.normalized_peter_weyl_intertwiners()
    assert result["all_reduced_elements_nonzero"] is True
    assert result["formal_equal_coefficient_matrix_rank"] == 3
    assert result["physical_matrix_claimed"] is False
    assert [row["normalized_reduced_element"] for row in result["rows"]] == [
        "1", "-sqrt(7)", "3",
        "sqrt(7)", "-7*sqrt(6)/6", "sqrt(3)/2",
        "sqrt(11)", "42*sqrt(65)/65", "-sqrt(21)",
    ]
    assert [row["reduced_element_squared"] for row in result["rows"]] == [
        "1", "7", "9",
        "7", "49/6", "3/4",
        "11", "1764/65", "21",
    ]


def test_nonlinear_current_algebra_closes_by_cubic_order():
    result = v84.nonlinear_channel_witnesses()
    assert result["all_nine_generated"] is True
    assert result["maximum_required_degree"] == 3
    assert all(row["target_generated"] for row in result["rows"])


def test_current_and_rank_no_go_theorems():
    irreducible = v84.single_irreducible_current_no_go()
    separable = v84.separable_current_rank_theorem()
    common = v84.common_structure_mixing_audit()
    assert irreducible["distinct_diagonal_irreps"] == 3
    assert irreducible["single_irrep_sufficient"] is False
    assert separable["single_point_rank_bound"] == 1
    assert separable["minimum_separable_channels_for_rank_three"] == 3
    assert common["FR"]["can_generate_generic_CKM"] is False
    assert common["triality"]["can_generate_generic_CKM"] is False
    assert common["G2_polarization"]["can_generate_generic_CKM"] is False


def test_mass_basis_mismatch_criterion():
    result = v84.mass_basis_mismatch_criterion()
    assert result["same_embedding_result"] == "U_u=U_d implies V_CKM=I3"
    assert result["block_central_common_slot_functions_sufficient"] is False
    assert result["physical_CKM_derived"] is False


def test_component_selection_and_claim_boundary():
    obstruction = v84.component_selection_obstruction()
    assert obstruction["unique_component_selected_by_block_labels"] is False
    assert len(obstruction["nontrivial_blocks"]) == 6
    payload = v84.status_report()
    assert payload["physical_masses"] is None
    assert payload["CKM_matrix"] is None
    assert payload["frozen_predictions_changed"] is False
    assert payload["official_prediction_logic_changed"] is False
    assert payload["validation_passed"] is True
    json.dumps(payload, sort_keys=True)


def test_committed_artifact_matches_status_report():
    root = Path(__file__).resolve().parents[1]
    artifact = root / "artifacts" / f"{v84.ARTIFACT_NAME}.json"
    assert json.loads(artifact.read_text(encoding="utf-8")) == v84.status_report()

