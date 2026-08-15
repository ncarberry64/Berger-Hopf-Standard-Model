import json
from pathlib import Path


def test_second_refreshed_complete_merit_newton_validates():
    payload = json.loads(Path(
        "artifacts/BHSM_aether_n3_second_refreshed_complete_merit_newton_v18_03.json"
    ).read_text(encoding="utf-8"))
    assert payload["validation_passed"]
    result = payload["second_refreshed_complete_merit_newton"]
    assert result["physical_Jacobian_refreshed"]
    assert not result["componentwise_event_monotonicity_required"]
    assert not result["handcrafted_direction_mixture"]
    selected = result["selected_true_merit_candidate_pending_child_acceptance"]
    if selected is not None:
        assert selected["complete_norm_reduction"] > 0.0
        assert selected["eta_minimum"] > 1.0e-5
        assert len(selected["raw_vector_hex"]) == 376
