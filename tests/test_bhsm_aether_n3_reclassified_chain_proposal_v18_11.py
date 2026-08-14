import json
from pathlib import Path


def test_reclassified_chain_model_is_only_a_proposal():
    payload = json.loads(Path(
        "artifacts/BHSM_aether_n3_reclassified_chain_proposal_v18_11.json"
    ).read_text(encoding="utf-8"))
    assert payload["validation_passed"]
    assert payload["status"] == "RECLASSIFIED"
    result = payload["reclassified_chain_proposal"]
    assert result["proposal_model"]["derivative_claim"].startswith("INVALIDATED")
    assert result["proposal_model"]["used_only_to_propose_trials"]
    assert result["proposal_model"]["physical_solve_dimension"] == [376, 376]
    assert result["proposal_model"]["event_multiplier_explicit"]
    assert not result["componentwise_monotonicity_required"]
    assert not result["must_remain_on_previous_iterate_path"]
    selected = result["selected_true_merit_candidate_pending_child_acceptance"]
    if selected is not None:
        assert selected["complete_norm_reduction"] > 0.0
        assert selected["eta_minimum"] > 1.0e-5
