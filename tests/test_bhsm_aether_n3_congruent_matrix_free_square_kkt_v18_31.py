from pathlib import Path

from bhsm.interface.aether_n3_congruent_matrix_free_square_kkt_v18_31 import completion_payload
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json


def test_v18_31_congruent_matrix_free_square_kkt() -> None:
    payload = completion_payload()
    result = payload["congruent_matrix_free_square_kkt"]
    assert payload["status"] == "INVALIDATED"
    assert not payload["newton_equation_converged"]
    assert result["source_state"].startswith("v18.29")
    assert result["physical_solve_dimension"] == [376, 376]
    assert result["event_multiplier_explicit"]
    assert not result["physical_equations_changed"]
    assert not result["componentwise_monotonicity_required"]
    assert not result["must_remain_on_previous_iterate_path"]
    assert result["coordinate_map"]["physical_residual_rows_left_scaled"] is False
    assert result["selected_true_merit_candidate_pending_child_acceptance"] is not None
    assert Path(
        "artifacts/BHSM_aether_n3_congruent_matrix_free_square_kkt_v18_31.json"
    ).read_text(encoding="utf-8") == deterministic_json(payload)
