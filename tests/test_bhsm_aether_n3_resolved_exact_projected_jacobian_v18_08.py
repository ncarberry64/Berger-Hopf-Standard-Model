import json
from pathlib import Path


def test_resolved_exact_projected_jacobian_is_invalidated():
    payload = json.loads(Path(
        "artifacts/BHSM_aether_n3_resolved_exact_projected_jacobian_v18_08.json"
    ).read_text(encoding="utf-8"))
    assert not payload["validation_passed"]
    assert payload["status"] == "INVALIDATED"
    result = payload["resolved_exact_projected_jacobian"]
    assert result["jacobian"]["absolute_step"] == 3.0e-5
    assert result["derivative_step_resolution"]["inherited_1e_4_step_rejected"]
    assert max(row["relative_residual"] for row in result["directional_validation"]) > 1.0e-2
    assert not result["physical_action_changed"]
    assert not result["physical_event_changed"]
    assert not result["global_KKT_row_added"]
