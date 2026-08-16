import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def artifact(name: str) -> dict:
    return json.loads((ROOT / "artifacts" / name).read_text(encoding="utf-8"))


def test_v20_07_records_response_noise_floor():
    payload = artifact(
        "BHSM_aether_n3_fortieth_direct_residual_scale_audit_v20_07.json"
    )
    result = payload["fortieth_direct_residual_scale_audit"]
    assert payload["status"] == "INVALIDATED"
    assert result["source_complete_norm"] == 0.768902386537366
    assert result["selected_finest_common_stable_pair"] is None
    assert result["physical_residual_changed"] is False


def test_v20_08_keeps_invalidated_response_proposal_only():
    payload = artifact(
        "BHSM_aether_n3_thirty_seventh_bidirectional_merit_manifold_probe_v20_08.json"
    )
    result = payload["thirty_seventh_bidirectional_merit_manifold_probe"]
    response = result["direct_response"]
    selected = result["selected_true_merit_candidate_pending_child_acceptance"]
    assert payload["solver_interpretation"] == "INVALIDATED"
    assert response["source_status"] == "INVALIDATED"
    assert response["source_stability_gate_passed"] is False
    assert response["invalidated_scale_used_only_to_generate_bounded_proposals"] is True
    assert selected["metrics"]["complete"] == 0.768773268629423


def test_v20_10_passes_unchanged_physical_gate():
    payload = artifact(
        "BHSM_aether_n3_thirty_seventh_bidirectional_probe_promotion_v20_10.json"
    )
    result = payload["thirty_seventh_bidirectional_probe_promotion"]
    child = result["event_to_complete_child"]
    persistence = result["persistence"]
    assert payload["validation_passed"] is True
    assert payload["FULL_BHSM_COMPLETE"] is False
    assert result["global_step"]["candidate_complete_norm"] == 0.768773268629423
    assert child["local_chart_rank"] == 14
    assert child["resolved_dynamic_flux_envelope"] < 2.0e-5
    assert persistence["all_steps_valid"] is True
    assert persistence["nonzero_relative_evolution_retained"] is True
