import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def artifact(name: str) -> dict:
    return json.loads((ROOT / "artifacts" / name).read_text(encoding="utf-8"))


def test_v20_03_validates_response_gate():
    payload = artifact(
        "BHSM_aether_n3_thirty_ninth_direct_residual_scale_audit_v20_03.json"
    )
    result = payload["thirty_ninth_direct_residual_scale_audit"]
    pair = result["selected_finest_common_stable_pair"]
    assert payload["validation_passed"] is True
    assert result["source_complete_norm"] == 0.769441416391865
    assert pair["coarse_step"] == 3.0e-8
    assert pair["fine_step"] == 1.0e-8
    assert pair["maximum_event_row_absolute_change"] < 2.0e-4


def test_v20_04_preserves_exact_merit_authority():
    payload = artifact(
        "BHSM_aether_n3_thirty_sixth_bidirectional_merit_manifold_probe_v20_04.json"
    )
    result = payload["thirty_sixth_bidirectional_merit_manifold_probe"]
    selected = result["selected_true_merit_candidate_pending_child_acceptance"]
    assert payload["solver_interpretation"] == "INVALIDATED"
    assert result["direct_response"]["source_stability_gate_passed"] is True
    assert selected["metrics"]["complete"] == 0.768902386537366


def test_v20_06_passes_unchanged_physical_gate():
    payload = artifact(
        "BHSM_aether_n3_thirty_sixth_bidirectional_probe_promotion_v20_06.json"
    )
    result = payload["thirty_sixth_bidirectional_probe_promotion"]
    child = result["event_to_complete_child"]
    persistence = result["persistence"]
    assert payload["validation_passed"] is True
    assert payload["FULL_BHSM_COMPLETE"] is False
    assert result["global_step"]["candidate_complete_norm"] == 0.768902386537366
    assert child["local_chart_rank"] == 14
    assert child["resolved_dynamic_flux_envelope"] < 2.0e-5
    assert persistence["all_steps_valid"] is True
    assert persistence["nonzero_relative_evolution_retained"] is True
