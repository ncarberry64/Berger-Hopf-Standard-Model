from pathlib import Path

from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_third_direct_line_promotion_v18_45 import completion_payload


def test_v18_45_third_direct_line_promotion() -> None:
    payload = completion_payload()
    result = payload["third_direct_line_promotion"]
    assert not payload["validation_passed"]
    assert payload["status"] == "INVALIDATED"
    assert result["global_step"]["source_solver_model_status"] == "INVALIDATED"
    assert not result["global_step"]["source_solver_model_reasserted"]
    assert result["global_step"]["complete_norm_reduction"] > 0.0
    assert result["event_to_complete_child"]["local_chart_rank"] == 14
    assert result["persistence"]["all_steps_valid"]
    assert result["persistence"]["nonzero_relative_evolution_retained"]
    assert not payload["validation"]["resolved_dynamic_flux_closed"]
    assert result["event_to_complete_child"]["resolved_dynamic_flux_envelope"] > 2.0e-5
    assert Path(
        "artifacts/BHSM_aether_n3_third_direct_line_promotion_v18_45.json"
    ).read_text(encoding="utf-8") == deterministic_json(payload)
