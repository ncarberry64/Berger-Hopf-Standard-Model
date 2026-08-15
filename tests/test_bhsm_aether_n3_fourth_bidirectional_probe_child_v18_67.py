import os
from pathlib import Path

from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_fourth_bidirectional_probe_child_v18_67 import completion_payload


def test_v18_67_fourth_bidirectional_probe_child() -> None:
    payload = completion_payload()
    result = payload["fourth_bidirectional_probe_child"]
    assert payload["validation_passed"]
    assert payload["status"] == "VALIDATED"
    assert result["chart"]["full_chart_rank"] == 14
    assert result["whole_child_variable_count"] == 26
    assert result["physical_row_count"] == 14
    assert result["nonzero_motion_retained"]
    if os.name == "nt":
        assert Path("artifacts/BHSM_aether_n3_fourth_bidirectional_probe_child_v18_67.json").read_text(encoding="utf-8") == deterministic_json(payload)
