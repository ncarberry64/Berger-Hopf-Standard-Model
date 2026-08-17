import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def artifact(name: str) -> dict:
    return json.loads((ROOT / "artifacts" / name).read_text(encoding="utf-8"))


def test_v18_74_and_v18_78_reproduce_their_accepted_sources():
    rows = (
        (
            "BHSM_aether_n3_ninth_direct_residual_scale_audit_v18_74.json",
            "ninth_direct_residual_scale_audit",
            0.807144219141348,
        ),
        (
            "BHSM_aether_n3_tenth_direct_residual_scale_audit_v18_78.json",
            "tenth_direct_residual_scale_audit",
            0.806818034168188,
        ),
    )
    for name, key, expected in rows:
        payload = artifact(name)
        result = payload[key]
        assert payload["validation_passed"] is True
        assert abs(result["source_complete_norm"] - expected) < 5.0e-12
        pair = result["selected_finest_common_stable_pair"]
        assert pair["coarse_step"] == 1.0e-6
        assert pair["fine_step"] == 3.0e-7
        assert pair["all_directions_stable"] is True


def test_v18_75_and_v18_79_keep_solver_rules_out_of_physics():
    rows = (
        (
            "BHSM_aether_n3_sixth_bidirectional_merit_manifold_probe_v18_75.json",
            "sixth_bidirectional_merit_manifold_probe",
        ),
        (
            "BHSM_aether_n3_seventh_bidirectional_merit_manifold_probe_v18_79.json",
            "seventh_bidirectional_merit_manifold_probe",
        ),
    )
    for name, key in rows:
        payload = artifact(name)
        result = payload[key]
        selected = result[
            "selected_true_merit_candidate_pending_child_acceptance"
        ]
        assert payload["validation_passed"] is True
        assert payload["solver_interpretation"] == "INVALIDATED"
        assert selected["complete_norm_reduction"] > 0.0
        assert selected["eta_minimum"] > 1.0e-5
        assert result["componentwise_monotonicity_required"] is False
        assert result["must_remain_on_previous_iterate_path"] is False


def test_v18_77_is_a_fully_gated_physical_promotion():
    payload = artifact(
        "BHSM_aether_n3_sixth_bidirectional_probe_promotion_v18_77.json"
    )
    result = payload["sixth_bidirectional_probe_promotion"]
    assert payload["validation_passed"] is True
    assert payload["FULL_BHSM_COMPLETE"] is False
    assert result["global_step"]["candidate_complete_norm"] == 0.806818034168188
    assert result["event_to_complete_child"]["local_chart_rank"] == 14
    assert result["event_to_complete_child"]["resolved_dynamic_flux_envelope"] < 2.0e-5
    assert result["persistence"]["all_steps_valid"] is True
    assert result["persistence"]["nonzero_relative_evolution_retained"] is True


def test_v18_81_rejects_the_lower_norm_primary_state_on_flux_only():
    payload = artifact(
        "BHSM_aether_n3_seventh_bidirectional_probe_promotion_v18_81.json"
    )
    result = payload["seventh_bidirectional_probe_promotion"]
    validation = payload["validation"]
    assert payload["validation_passed"] is False
    assert validation["resolved_dynamic_flux_closed"] is False
    assert all(
        value for name, value in validation.items()
        if name != "resolved_dynamic_flux_closed"
    )
    assert result["global_step"]["candidate_complete_norm"] == 0.804728752733494
    assert result["event_to_complete_child"]["resolved_dynamic_flux_envelope"] > 2.0e-5


def test_v18_83_promotes_the_next_exact_merit_state_without_gate_changes():
    child = artifact(
        "BHSM_aether_n3_seventh_bidirectional_fallback_child_v18_82.json"
    )["seventh_bidirectional_fallback_child"]
    payload = artifact(
        "BHSM_aether_n3_seventh_bidirectional_fallback_promotion_v18_83.json"
    )
    result = payload["seventh_bidirectional_fallback_promotion"]
    gate = result["event_to_complete_child"]
    assert payload["validation_passed"] is True
    assert payload["FULL_BHSM_COMPLETE"] is False
    assert child["rejected_predecessor"]["acceptance_gate_changed"] is False
    assert result["global_step"]["primary_candidate_flux_rejection_preserved"] is True
    assert result["global_step"]["candidate_complete_norm"] == 0.80554785212226
    assert gate["local_chart_rank"] == 14
    assert gate["physical_row_count"] == 14
    assert gate["additional_global_KKT_rows"] == 0
    assert gate["resolved_dynamic_flux_envelope"] < 2.0e-5
    assert result["persistence"]["all_steps_valid"] is True
    assert result["persistence"]["nonzero_relative_evolution_retained"] is True
