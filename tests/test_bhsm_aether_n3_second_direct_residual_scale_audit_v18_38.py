from pathlib import Path

from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_second_direct_residual_scale_audit_v18_38 import completion_payload


def test_v18_38_second_direct_residual_scale_audit() -> None:
    payload = completion_payload()
    result = payload["second_direct_residual_scale_audit"]
    assert payload["validation_passed"]
    assert payload["status"] == "VALIDATED"
    assert result["selected_finest_common_stable_pair"] is not None
    assert result["physical_solve_dimension"] == [376, 376]
    assert result["event_multiplier_explicit"]
    assert not result["physical_residual_changed"]
    assert Path(
        "artifacts/BHSM_aether_n3_second_direct_residual_scale_audit_v18_38.json"
    ).read_text(encoding="utf-8") == deterministic_json(payload)
