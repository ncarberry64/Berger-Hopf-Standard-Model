import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def artifact(name: str) -> dict:
    return json.loads((ROOT / "artifacts" / name).read_text(encoding="utf-8"))


def test_v20_35_records_response_noise_floor():
    payload = artifact(
        "BHSM_aether_n3_forty_sixth_direct_residual_scale_audit_v20_35.json"
    )
    result = payload["forty_sixth_direct_residual_scale_audit"]
    assert payload["status"] == "INVALIDATED"
    assert result["source_complete_norm"] == 0.767087818463417
    assert result["selected_finest_common_stable_pair"] is None


def test_v20_36_keeps_response_proposal_only():
    payload = artifact(
        "BHSM_aether_n3_forty_third_bidirectional_merit_manifold_probe_v20_36.json"
    )
    result = payload["forty_third_bidirectional_merit_manifold_probe"]
    response = result["direct_response"]
    selected = result["selected_true_merit_candidate_pending_child_acceptance"]
    assert payload["solver_interpretation"] == "INVALIDATED"
    assert response["source_status"] == "INVALIDATED"
    assert response["invalidated_scale_used_only_to_generate_bounded_proposals"] is True
    assert selected["metrics"]["complete"] == 0.767070408740601


def test_v20_38_passes_unchanged_physical_gate():
    payload = artifact(
        "BHSM_aether_n3_forty_third_bidirectional_probe_promotion_v20_38.json"
    )
    result = payload["forty_third_bidirectional_probe_promotion"]
    child = result["event_to_complete_child"]
    persistence = result["persistence"]
    assert payload["validation_passed"] is True
    assert payload["FULL_BHSM_COMPLETE"] is False
    assert result["global_step"]["candidate_complete_norm"] == 0.767070408740601
    assert child["local_chart_rank"] == 14
    assert child["resolved_dynamic_flux_envelope"] < 2.0e-5
    assert persistence["all_steps_valid"] is True
    assert persistence["nonzero_relative_evolution_retained"] is True
