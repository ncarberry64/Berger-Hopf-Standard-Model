import os
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
    if os.name == "nt":
        assert Path("artifacts/BHSM_aether_n3_second_bidirectional_probe_child_v18_57.json").read_text(encoding="utf-8") == deterministic_json(payload)
