import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def artifact(name: str) -> dict:
    return json.loads((ROOT / "artifacts" / name).read_text(encoding="utf-8"))


def test_v19_91_validates_existing_response_gate():
    payload = artifact(
        "BHSM_aether_n3_thirty_sixth_direct_residual_scale_audit_v19_91.json"
    )
    result = payload["thirty_sixth_direct_residual_scale_audit"]
    pair = result["selected_finest_common_stable_pair"]
    assert payload["validation_passed"] is True
    assert result["source_complete_norm"] == 0.777122666596459
    assert pair["maximum_event_row_absolute_change"] < 2.0e-4


def test_v19_92_keeps_exact_merit_authoritative():
    payload = artifact(
        "BHSM_aether_n3_thirty_third_bidirectional_merit_manifold_probe_v19_92.json"
    )
    result = payload["thirty_third_bidirectional_merit_manifold_probe"]
    selected = result["selected_true_merit_candidate_pending_child_acceptance"]
    assert payload["solver_interpretation"] == "INVALIDATED"
    assert result["direct_response"]["source_stability_gate_passed"] is True
    assert selected["metrics"]["complete"] == 0.774048801461998


def test_v19_94_passes_unchanged_physical_gate():
    payload = artifact(
        "BHSM_aether_n3_thirty_third_bidirectional_probe_promotion_v19_94.json"
    )
    result = payload["thirty_third_bidirectional_probe_promotion"]
    child = result["event_to_complete_child"]
    persistence = result["persistence"]
    assert payload["validation_passed"] is True
    assert payload["FULL_BHSM_COMPLETE"] is False
    assert result["global_step"]["candidate_complete_norm"] == 0.774048801461998
    assert child["local_chart_rank"] == 14
    assert child["resolved_dynamic_flux_envelope"] < 2.0e-5
    assert persistence["all_steps_valid"] is True
    assert persistence["nonzero_relative_evolution_retained"] is True
