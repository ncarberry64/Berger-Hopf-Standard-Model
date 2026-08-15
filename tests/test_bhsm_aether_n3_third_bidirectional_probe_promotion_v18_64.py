from pathlib import Path

from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_third_bidirectional_probe_promotion_v18_64 import completion_payload


def test_v18_64_third_bidirectional_probe_promotion() -> None:
    payload = completion_payload()
    result = payload["third_bidirectional_probe_promotion"]
    assert payload["validation_passed"]
    assert payload["status"] == "VALIDATED"
    assert result["global_step"]["complete_norm_reduction"] > 0.0
    assert result["event_to_complete_child"]["resolved_dynamic_flux_envelope"] < 2.0e-5
    assert result["persistence"]["all_steps_valid"]
    assert result["persistence"]["nonzero_relative_evolution_retained"]
    assert Path("artifacts/BHSM_aether_n3_third_bidirectional_probe_promotion_v18_64.json").read_text(encoding="utf-8") == deterministic_json(payload)
