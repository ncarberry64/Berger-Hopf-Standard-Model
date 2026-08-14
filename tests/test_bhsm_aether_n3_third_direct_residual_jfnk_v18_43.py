from pathlib import Path

from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_third_direct_residual_jfnk_v18_43 import completion_payload


def test_v18_43_third_direct_residual_jfnk() -> None:
    payload = completion_payload()
    result = payload["third_direct_residual_jfnk"]
    assert result["source_state"].startswith("v18.41")
    assert result["direct_response"]["source_status"] == "VALIDATED"
    assert not result["direct_response"]["prior_failed_direction_models_reused"]
    assert result["physical_solve_dimension"] == [376, 376]
    assert result["event_multiplier_explicit"]
    assert not result["physical_equations_changed"]
    assert not result["event_definition_changed"]
    assert not result["componentwise_monotonicity_required"]
    assert Path(
        "artifacts/BHSM_aether_n3_third_direct_residual_jfnk_v18_43.json"
    ).read_text(encoding="utf-8") == deterministic_json(payload)
