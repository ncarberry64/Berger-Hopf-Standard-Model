import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def artifact(name: str) -> dict:
    return json.loads((ROOT / "artifacts" / name).read_text(encoding="utf-8"))


def test_v20_16_preserves_invalidated_response_as_proposal_only():
    payload = artifact(
        "BHSM_aether_n3_thirty_ninth_bidirectional_merit_manifold_probe_v20_16.json"
    )
    result = payload["thirty_ninth_bidirectional_merit_manifold_probe"]
    response = result["direct_response"]
    assert payload["solver_interpretation"] == "INVALIDATED"
    assert response["source_status"] == "INVALIDATED"
    assert response["invalidated_scale_used_only_to_generate_bounded_proposals"] is True


def test_v20_18_primary_is_rejected_by_unchanged_flux_gate():
    payload = artifact(
        "BHSM_aether_n3_thirty_ninth_bidirectional_probe_promotion_v20_18.json"
    )
    result = payload["thirty_ninth_bidirectional_probe_promotion"]
    assert payload["status"] == "INVALIDATED"
    assert result["global_step"]["candidate_complete_norm"] == 0.768573744724912
    assert result["event_to_complete_child"]["resolved_dynamic_flux_envelope"] > 2.0e-5


def test_v20_20_fallback_passes_unchanged_physical_gate():
    payload = artifact(
        "BHSM_aether_n3_thirty_ninth_bidirectional_fallback_promotion_v20_20.json"
    )
    result = payload["thirty_ninth_bidirectional_fallback_promotion"]
    child = result["event_to_complete_child"]
    persistence = result["persistence"]
    assert payload["validation_passed"] is True
    assert payload["FULL_BHSM_COMPLETE"] is False
    assert result["global_step"]["primary_candidate_flux_rejection_preserved"] is True
    assert result["global_step"]["candidate_complete_norm"] == 0.768614585778829
    assert child["local_chart_rank"] == 14
    assert child["resolved_dynamic_flux_envelope"] < 2.0e-5
    assert persistence["all_steps_valid"] is True
    assert persistence["nonzero_relative_evolution_retained"] is True
