import os
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
    if os.name == "nt":
        assert Path("artifacts/BHSM_aether_n3_second_bidirectional_probe_promotion_v18_58.json").read_text(encoding="utf-8") == deterministic_json(payload)
