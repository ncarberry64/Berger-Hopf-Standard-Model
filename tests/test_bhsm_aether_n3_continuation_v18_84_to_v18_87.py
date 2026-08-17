import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def artifact(name: str) -> dict:
    return json.loads((ROOT / "artifacts" / name).read_text(encoding="utf-8"))


def test_v18_84_resolves_the_unchanged_response_plateau():
    payload = artifact(
        "BHSM_aether_n3_eleventh_direct_residual_scale_audit_v18_84.json"
    )
    result = payload["eleventh_direct_residual_scale_audit"]
    pair = result["selected_finest_common_stable_pair"]
    assert payload["validation_passed"] is True
    assert result["source_complete_norm"] == 0.80554785212226
    assert pair["coarse_step"] == 1.0e-6
    assert pair["fine_step"] == 3.0e-7
    assert pair["all_directions_stable"] is True


def test_v18_85_selects_exact_merit_without_a_newton_claim():
    payload = artifact(
        "BHSM_aether_n3_eighth_bidirectional_merit_manifold_probe_v18_85.json"
    )
    result = payload["eighth_bidirectional_merit_manifold_probe"]
    selected = result[
        "selected_true_merit_candidate_pending_child_acceptance"
    ]
    assert payload["validation_passed"] is True
    assert payload["solver_interpretation"] == "INVALIDATED"
    assert selected["metrics"]["complete"] == 0.804250811090346
    assert selected["complete_norm_reduction"] > 0.0
    assert selected["eta_minimum"] > 1.0e-5
    assert result["componentwise_monotonicity_required"] is False
    assert result["must_remain_on_previous_iterate_path"] is False


def test_v18_86_reconstructs_the_complete_moving_child():
    payload = artifact(
        "BHSM_aether_n3_eighth_bidirectional_probe_child_v18_86.json"
    )
    child = payload["eighth_bidirectional_probe_child"]
    assert payload["validation_passed"] is True
    assert child["whole_child_variable_count"] == 26
    assert child["physical_row_count"] == 14
    assert child["additional_global_KKT_rows"] == 0
    assert child["chart"]["full_chart_rank"] == 14
    assert child["nonzero_motion_retained"] is True


def test_v18_87_passes_every_unchanged_promotion_gate():
    payload = artifact(
        "BHSM_aether_n3_eighth_bidirectional_probe_promotion_v18_87.json"
    )
    result = payload["eighth_bidirectional_probe_promotion"]
    global_step = result["global_step"]
    child = result["event_to_complete_child"]
    persistence = result["persistence"]
    assert payload["validation_passed"] is True
    assert payload["FULL_BHSM_COMPLETE"] is False
    assert global_step["candidate_complete_norm"] == 0.804250811090346
    assert global_step["complete_norm_reduction"] > 0.0
    assert child["local_chart_rank"] == 14
    assert child["resolved_dynamic_flux_envelope"] < 2.0e-5
    assert persistence["all_steps_valid"] is True
    assert persistence["nonzero_relative_evolution_retained"] is True
