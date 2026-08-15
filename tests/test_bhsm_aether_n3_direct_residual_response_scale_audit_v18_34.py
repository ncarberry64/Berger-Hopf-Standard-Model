from pathlib import Path

from bhsm.interface.aether_n3_direct_residual_response_scale_audit_v18_34 import completion_payload
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json


def test_v18_34_direct_residual_response_scale_audit() -> None:
    payload = completion_payload()
    result = payload["direct_residual_response_scale_audit"]
    assert payload["validation_passed"]
    assert payload["status"] == "VALIDATED"
    assert result["selected_finest_common_stable_pair"] is not None
    assert result["physical_solve_dimension"] == [376, 376]
    assert result["event_multiplier_explicit"]
    assert not result["physical_residual_changed"]
    assert not result["event_definition_changed"]
    assert Path(
        "artifacts/BHSM_aether_n3_direct_residual_response_scale_audit_v18_34.json"
    ).read_text(encoding="utf-8") == deterministic_json(payload)
