import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def artifact(name: str) -> dict:
    return json.loads((ROOT / "artifacts" / name).read_text(encoding="utf-8"))


def test_v19_87_validates_direct_response_pair():
    payload = artifact(
        "BHSM_aether_n3_thirty_fifth_direct_residual_scale_audit_v19_87.json"
    )
    result = payload["thirty_fifth_direct_residual_scale_audit"]
    pair = result["selected_finest_common_stable_pair"]
    assert payload["validation_passed"] is True
    assert result["source_complete_norm"] == 0.777227123413482
    assert pair["coarse_step"] == 1.0e-7
    assert pair["fine_step"] == 3.0e-8
    assert pair["maximum_event_row_absolute_change"] < 2.0e-4


def test_v19_88_exact_merit_remains_authoritative():
    payload = artifact(
        "BHSM_aether_n3_thirty_second_bidirectional_merit_manifold_probe_v19_88.json"
    )
    result = payload["thirty_second_bidirectional_merit_manifold_probe"]
    selected = result["selected_true_merit_candidate_pending_child_acceptance"]
    assert payload["solver_interpretation"] == "INVALIDATED"
    assert result["direct_response"]["source_stability_gate_passed"] is True
    assert result["line_scan"]["exact_nonlinear_residual_authoritative"] is True
    assert selected["metrics"]["complete"] == 0.777122666596459


def test_v19_90_passes_unchanged_physical_gate():
    payload = artifact(
        "BHSM_aether_n3_thirty_second_bidirectional_probe_promotion_v19_90.json"
    )
    result = payload["thirty_second_bidirectional_probe_promotion"]
    step = result["global_step"]
    child = result["event_to_complete_child"]
    persistence = result["persistence"]
    assert payload["validation_passed"] is True
    assert payload["FULL_BHSM_COMPLETE"] is False
    assert step["candidate_complete_norm"] == 0.777122666596459
    assert step["source_solver_interpretation"] == "INVALIDATED"
    assert child["local_chart_rank"] == 14
    assert child["resolved_dynamic_flux_envelope"] < 2.0e-5
    assert persistence["all_steps_valid"] is True
    assert persistence["nonzero_relative_evolution_retained"] is True
