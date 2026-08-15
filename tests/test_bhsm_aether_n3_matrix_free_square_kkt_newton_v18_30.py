from pathlib import Path

from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_matrix_free_square_kkt_newton_v18_30 import completion_payload


def test_v18_30_matrix_free_square_kkt_newton() -> None:
    payload = completion_payload()
    result = payload["matrix_free_square_kkt_newton"]
    assert payload["status"] == "RECLASSIFIED"
    assert not payload["newton_equation_converged"]
    assert payload["selected_candidate_below_response_validation_scale"]
    assert result["source_state"].startswith("v18.29")
    assert result["physical_solve_dimension"] == [376, 376]
    assert result["event_multiplier_explicit"]
    assert not result["physical_equations_changed"]
    assert not result["componentwise_monotonicity_required"]
    assert not result["must_remain_on_previous_iterate_path"]
    assert result["event_response"]["full_event_hessian_claimed"] is False
    assert Path(
        "artifacts/BHSM_aether_n3_matrix_free_square_kkt_newton_v18_30.json"
    ).read_text(encoding="utf-8") == deterministic_json(payload)
