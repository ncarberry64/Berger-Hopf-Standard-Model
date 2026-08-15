import json
from pathlib import Path


def test_v18_58_second_bidirectional_probe_promotion() -> None:
    payload = json.loads(Path(
        "artifacts/BHSM_aether_n3_second_bidirectional_probe_promotion_v18_58.json"
    ).read_text(encoding="utf-8"))
    result = payload["second_bidirectional_probe_promotion"]
    assert payload["validation_passed"]
    assert payload["status"] == "VALIDATED"
    assert result["global_step"]["complete_norm_reduction"] > 0.0
    assert result["event_to_complete_child"]["resolved_dynamic_flux_envelope"] < 2.0e-5
    assert result["persistence"]["all_steps_valid"]
    assert result["persistence"]["nonzero_relative_evolution_retained"]
    assert result["global_step"]["eta_minimum"] > 1.0e-5
    assert result["event_to_complete_child"]["local_chart_rank"] == 14
    assert result["persistence"]["maximum_constraint_residual"] < 1.0e-8
    assert result["persistence"]["minimum_eta"] > 0.0
