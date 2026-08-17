import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def artifact(name: str) -> dict:
    return json.loads((ROOT / "artifacts" / name).read_text(encoding="utf-8"))


def test_v19_77_records_response_noise_floor_without_physical_change():
    payload = artifact(
        "BHSM_aether_n3_thirty_third_direct_residual_scale_audit_v19_77.json"
    )
    result = payload["thirty_third_direct_residual_scale_audit"]
    assert payload["status"] == "INVALIDATED"
    assert result["source_complete_norm"] == 0.783424601549721
    assert result["selected_finest_common_stable_pair"] is None
    assert result["physical_residual_changed"] is False
    assert result["event_definition_changed"] is False


def test_v19_78_invalidated_derivative_is_proposal_only():
    payload = artifact(
        "BHSM_aether_n3_thirtieth_bidirectional_merit_manifold_probe_v19_78.json"
    )
    result = payload["thirtieth_bidirectional_merit_manifold_probe"]
    response = result["direct_response"]
    selected = result[
        "selected_true_merit_candidate_pending_child_acceptance"
    ]
    assert payload["validation_passed"] is True
    assert payload["solver_interpretation"] == "INVALIDATED"
    assert response["source_status"] == "INVALIDATED"
    assert response["source_stability_gate_passed"] is False
    assert response[
        "invalidated_scale_used_only_to_generate_bounded_proposals"
    ] is True
    assert result["line_scan"]["exact_nonlinear_residual_authoritative"] is True
    assert selected["metrics"]["complete"] == 0.781619005072963


def test_v19_80_primary_flux_rejected_and_v19_82_fallback_promoted():
    primary = artifact(
        "BHSM_aether_n3_thirtieth_bidirectional_probe_promotion_v19_80.json"
    )["thirtieth_bidirectional_probe_promotion"]
    assert primary["event_to_complete_child"][
        "resolved_dynamic_flux_envelope"
    ] > 2.0e-5

    payload = artifact(
        "BHSM_aether_n3_thirtieth_bidirectional_fallback_promotion_v19_82.json"
    )
    result = payload["thirtieth_bidirectional_fallback_promotion"]
    global_step = result["global_step"]
    child = result["event_to_complete_child"]
    persistence = result["persistence"]
    assert payload["validation_passed"] is True
    assert payload["FULL_BHSM_COMPLETE"] is False
    assert global_step["source_complete_norm"] == 0.783424601549721
    assert global_step["candidate_complete_norm"] == 0.781663574515915
    assert global_step["primary_candidate_flux_rejection_preserved"] is True
    assert child["local_chart_rank"] == 14
    assert child["resolved_dynamic_flux_envelope"] < 2.0e-5
    assert persistence["all_steps_valid"] is True
    assert persistence["nonzero_relative_evolution_retained"] is True
