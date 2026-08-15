import json
from pathlib import Path


def test_refreshed_complete_merit_newton_artifact_is_classified():
    payload = json.loads(Path(
        "artifacts/BHSM_aether_n3_refreshed_complete_merit_newton_v18_01.json"
    ).read_text(encoding="utf-8"))
    assert payload["validation_passed"]
    result = payload["refreshed_complete_merit_newton"]
    assert result["physical_Jacobian_refreshed"]
    assert not result["handcrafted_direction_mixture"]
    assert not result["componentwise_event_monotonicity_required"]
    selected = result[
        "selected_true_merit_candidate_pending_child_acceptance"
    ]
    if selected is not None:
        assert selected["complete_norm_reduction"] > 0.0
        assert selected["eta_minimum"] > 1.0e-5
        assert len(selected["raw_vector_hex"]) == 376
