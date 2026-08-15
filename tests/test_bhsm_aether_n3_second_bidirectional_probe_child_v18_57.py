import json
from pathlib import Path


def test_v18_57_second_bidirectional_probe_child() -> None:
    payload = json.loads(Path(
        "artifacts/BHSM_aether_n3_second_bidirectional_probe_child_v18_57.json"
    ).read_text(encoding="utf-8"))
    result = payload["second_bidirectional_probe_child"]
    assert payload["validation_passed"]
    assert payload["status"] == "VALIDATED"
    assert result["chart"]["full_chart_rank"] == 14
    assert result["whole_child_variable_count"] == 26
    assert result["physical_row_count"] == 14
    assert result["nonzero_motion_retained"]
    rows = result["physical_residuals"]
    assert rows["maximum_trace"] < 1.0e-9
    assert rows["maximum_seven_constraints"] < 1.0e-9
    assert rows["momentum_norm"] < 1.0e-7
    assert rows["dynamic_flux_norm_at_4e-4"] < 2.0e-5
