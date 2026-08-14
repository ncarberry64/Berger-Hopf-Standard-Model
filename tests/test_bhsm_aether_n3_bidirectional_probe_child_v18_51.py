from pathlib import Path

from bhsm.interface.aether_n3_bidirectional_probe_child_v18_51 import completion_payload
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json


def test_v18_51_bidirectional_probe_child() -> None:
    payload = completion_payload()
    result = payload["bidirectional_probe_child"]
    assert payload["validation_passed"]
    assert payload["status"] == "VALIDATED"
    assert result["line_selection"]["orientation"] in {"positive", "negative"}
    assert result["source_solver_interpretation"] == "INVALIDATED_NOT_REASSERTED"
    assert result["chart"]["full_chart_rank"] == 14
    assert result["additional_global_KKT_rows"] == 0
    assert result["nonzero_motion_retained"]
    assert Path("artifacts/BHSM_aether_n3_bidirectional_probe_child_v18_51.json").read_text(encoding="utf-8") == deterministic_json(payload)
