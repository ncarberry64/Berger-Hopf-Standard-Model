import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def artifact(name: str) -> dict:
    return json.loads((ROOT / "artifacts" / name).read_text(encoding="utf-8"))


def test_v19_83_recovers_existing_response_stability_gate():
    payload = artifact(
        "BHSM_aether_n3_thirty_fourth_direct_residual_scale_audit_v19_83.json"
    )
    result = payload["thirty_fourth_direct_residual_scale_audit"]
    selected = result["selected_finest_common_stable_pair"]
    assert payload["status"] == "VALIDATED"
    assert result["source_complete_norm"] == 0.781663574515915
    assert selected["coarse_step"] == 3.0e-8
    assert selected["fine_step"] == 1.0e-8
    assert selected["maximum_event_row_absolute_change"] < 2.0e-4


def test_v19_84_keeps_solver_interpretation_invalidated():
    payload = artifact(
        "BHSM_aether_n3_thirty_first_bidirectional_merit_manifold_probe_v19_84.json"
    )
    result = payload["thirty_first_bidirectional_merit_manifold_probe"]
    response = result["direct_response"]
    selected = result["selected_true_merit_candidate_pending_child_acceptance"]
    assert payload["solver_interpretation"] == "INVALIDATED"
    assert response["source_stability_gate_passed"] is True
    assert response["used_only_as_local_geometric_probe"] is True
    assert result["line_scan"]["exact_nonlinear_residual_authoritative"] is True
    assert selected["metrics"]["complete"] == 0.777227123413482


def test_v19_86_passes_unchanged_physical_promotion_gates():
    payload = artifact(
        "BHSM_aether_n3_thirty_first_bidirectional_probe_promotion_v19_86.json"
    )
    result = payload["thirty_first_bidirectional_probe_promotion"]
    global_step = result["global_step"]
    child = result["event_to_complete_child"]
    persistence = result["persistence"]
    assert payload["validation_passed"] is True
    assert payload["FULL_BHSM_COMPLETE"] is False
    assert global_step["source_complete_norm"] == 0.781663574515915
    assert global_step["candidate_complete_norm"] == 0.777227123413482
    assert global_step["source_solver_interpretation"] == "INVALIDATED"
    assert child["local_chart_rank"] == 14
    assert child["resolved_dynamic_flux_envelope"] < 2.0e-5
    assert persistence["all_steps_valid"] is True
    assert persistence["nonzero_relative_evolution_retained"] is True
