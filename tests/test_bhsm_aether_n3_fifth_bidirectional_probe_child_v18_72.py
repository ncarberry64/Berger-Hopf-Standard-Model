import json
from pathlib import Path


def test_v18_72_complete_child_artifact() -> None:
    payload = json.loads(Path(
        "artifacts/BHSM_aether_n3_fifth_bidirectional_probe_child_v18_72.json"
    ).read_text(encoding="utf-8"))
    result = payload["fifth_bidirectional_probe_child"]
    rows = result["physical_residuals"]
    assert payload["validation_passed"]
    assert result["chart"]["full_chart_rank"] == 14
    assert rows["maximum_trace"] < 1.0e-9
    assert rows["maximum_seven_constraints"] < 1.0e-9
    assert rows["momentum_norm"] < 1.0e-7
    assert rows["dynamic_flux_norm_at_4e-4"] < 2.0e-5
    assert result["nonzero_motion_retained"]
