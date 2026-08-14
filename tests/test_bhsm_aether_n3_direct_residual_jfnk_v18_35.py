from pathlib import Path

from bhsm.interface.aether_n3_direct_residual_jfnk_v18_35 import completion_payload
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json


def test_v18_35_direct_residual_jfnk() -> None:
    payload = completion_payload()
    result = payload["direct_residual_jfnk"]
    assert result["source_state"].startswith("v18.33")
    assert result["direct_response"]["source_status"] == "VALIDATED"
    assert not result["direct_response"]["decomposed_v18_30_v18_31_models_reused"]
    assert result["physical_solve_dimension"] == [376, 376]
    assert result["event_multiplier_explicit"]
    assert not result["physical_equations_changed"]
    assert not result["event_definition_changed"]
    assert not result["componentwise_monotonicity_required"]
    assert Path(
        "artifacts/BHSM_aether_n3_direct_residual_jfnk_v18_35.json"
    ).read_text(encoding="utf-8") == deterministic_json(payload)
