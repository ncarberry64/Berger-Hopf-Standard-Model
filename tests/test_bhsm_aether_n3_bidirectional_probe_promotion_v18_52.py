from pathlib import Path

from bhsm.interface.aether_n3_bidirectional_probe_promotion_v18_52 import completion_payload
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json


def test_v18_52_bidirectional_probe_promotion() -> None:
    payload = completion_payload()
    result = payload["bidirectional_probe_promotion"]
    assert not payload["validation_passed"]
    assert payload["status"] == "INVALIDATED"
    assert result["global_step"]["source_solver_interpretation"] == "INVALIDATED"
    assert not result["global_step"]["source_solver_interpretation_reasserted"]
    assert result["global_step"]["both_orientations_were_scanned"]
    assert result["global_step"]["complete_norm_reduction"] > 0.0
    assert result["event_to_complete_child"]["local_chart_rank"] == 14
    assert result["persistence"]["all_steps_valid"]
    assert result["persistence"]["nonzero_relative_evolution_retained"]
    assert not payload["validation"]["resolved_dynamic_flux_closed"]
    assert result["event_to_complete_child"]["resolved_dynamic_flux_envelope"] > 2.0e-5
    assert Path("artifacts/BHSM_aether_n3_bidirectional_probe_promotion_v18_52.json").read_text(encoding="utf-8") == deterministic_json(payload)
