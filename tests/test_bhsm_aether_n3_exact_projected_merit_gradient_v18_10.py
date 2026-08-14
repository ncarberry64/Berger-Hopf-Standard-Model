import json
from pathlib import Path


def test_exact_projected_merit_gradient_is_classified():
    payload = json.loads(Path(
        "artifacts/BHSM_aether_n3_exact_projected_merit_gradient_v18_10.json"
    ).read_text(encoding="utf-8"))
    result = payload["exact_projected_merit_gradient"]
    assert not result["merit_gradient"]["physical_residual_changed"]
    assert not result["merit_gradient"]["physical_event_changed"]
    assert not result["merit_gradient"]["global_KKT_row_added"]
    assert result["merit_gradient"]["norm"] > 0.0
    assert result["merit_gradient"]["predicted_unit_direction_slope"] < 0.0
    selected = result["selected_true_merit_candidate_pending_child_acceptance"]
    if selected is not None:
        assert selected["complete_norm_reduction"] > 0.0
        assert selected["eta_minimum"] > 1.0e-5
