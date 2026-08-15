from pathlib import Path

from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_second_direct_line_child_v18_40 import completion_payload


def test_v18_40_second_direct_line_child() -> None:
    payload = completion_payload()
    result = payload["second_direct_line_child"]
    assert payload["validation_passed"]
    assert payload["status"] == "VALIDATED"
    assert result["source_solver_model"] == "INVALIDATED_NOT_REASSERTED"
    assert result["chart"]["full_chart_rank"] == 14
    assert result["additional_global_KKT_rows"] == 0
    assert result["nonzero_motion_retained"]
    assert Path(
        "artifacts/BHSM_aether_n3_second_direct_line_child_v18_40.json"
    ).read_text(encoding="utf-8") == deterministic_json(payload)
