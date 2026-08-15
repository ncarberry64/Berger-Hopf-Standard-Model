import json
from pathlib import Path


def test_v18_70_direct_response_artifact() -> None:
    payload = json.loads(Path(
        "artifacts/BHSM_aether_n3_eighth_direct_residual_scale_audit_v18_70.json"
    ).read_text(encoding="utf-8"))
    result = payload["eighth_direct_residual_scale_audit"]
    selected = result["selected_finest_common_stable_pair"]
    assert payload["validation_passed"]
    assert selected["all_directions_stable"]
    assert selected["coarse_step"] == 1.0e-6
    assert selected["fine_step"] == 3.0e-7
    assert result["physical_residual_changed"] is False
    assert result["event_definition_changed"] is False
