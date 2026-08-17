import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def artifact(name: str) -> dict:
    return json.loads((ROOT / "artifacts" / name).read_text(encoding="utf-8"))


def test_v19_22_and_v19_26_remeasure_each_accepted_source():
    rows = (
        ("twentieth", "v19_22", 0.795019734745765, 1.0e-6, 3.0e-7),
        ("twenty_first", "v19_26", 0.794780177090688, 3.0e-7, 1.0e-7),
    )
    for ordinal, version, source, coarse, fine in rows:
        payload = artifact(
            f"BHSM_aether_n3_{ordinal}_direct_residual_scale_audit_{version}.json"
        )
        result = payload[f"{ordinal}_direct_residual_scale_audit"]
        pair = result["selected_finest_common_stable_pair"]
        assert payload["validation_passed"] is True
        assert result["source_complete_norm"] == source
        assert pair["coarse_step"] == coarse
        assert pair["fine_step"] == fine
        assert pair["all_directions_stable"] is True


def test_v19_23_and_v19_27_use_exact_merit_not_solver_claims():
    rows = (
        ("seventeenth", "v19_23", 0.794780177090688),
        ("eighteenth", "v19_27", 0.793187079982019),
    )
    for ordinal, version, expected_norm in rows:
        payload = artifact(
            f"BHSM_aether_n3_{ordinal}_bidirectional_merit_manifold_probe_{version}.json"
        )
        result = payload[f"{ordinal}_bidirectional_merit_manifold_probe"]
        selected = result[
            "selected_true_merit_candidate_pending_child_acceptance"
        ]
        assert payload["validation_passed"] is True
        assert payload["solver_interpretation"] == "INVALIDATED"
        assert selected["metrics"]["complete"] == expected_norm
        assert selected["complete_norm_reduction"] > 0.0
        assert result["componentwise_monotonicity_required"] is False
        assert result["must_remain_on_previous_iterate_path"] is False


def test_v19_24_and_v19_28_reconstruct_complete_moving_children():
    rows = (
        ("seventeenth", "v19_24"),
        ("eighteenth", "v19_28"),
    )
    for ordinal, version in rows:
        payload = artifact(
            f"BHSM_aether_n3_{ordinal}_bidirectional_probe_child_{version}.json"
        )
        child = payload[f"{ordinal}_bidirectional_probe_child"]
        assert payload["validation_passed"] is True
        assert child["whole_child_variable_count"] == 26
        assert child["physical_row_count"] == 14
        assert child["additional_global_KKT_rows"] == 0
        assert child["chart"]["full_chart_rank"] == 14
        assert child["nonzero_motion_retained"] is True


def test_v19_25_and_v19_29_pass_every_unchanged_promotion_gate():
    rows = (
        (
            "seventeenth", "v19_25",
            0.795019734745765, 0.794780177090688,
        ),
        (
            "eighteenth", "v19_29",
            0.794780177090688, 0.793187079982019,
        ),
    )
    for ordinal, version, source, candidate in rows:
        payload = artifact(
            f"BHSM_aether_n3_{ordinal}_bidirectional_probe_promotion_{version}.json"
        )
        result = payload[f"{ordinal}_bidirectional_probe_promotion"]
        global_step = result["global_step"]
        child = result["event_to_complete_child"]
        persistence = result["persistence"]
        assert payload["validation_passed"] is True
        assert payload["FULL_BHSM_COMPLETE"] is False
        assert global_step["source_complete_norm"] == source
        assert global_step["candidate_complete_norm"] == candidate
        assert global_step["complete_norm_reduction"] > 0.0
        assert child["local_chart_rank"] == 14
        assert child["resolved_dynamic_flux_envelope"] < 2.0e-5
        assert persistence["all_steps_valid"] is True
        assert persistence["nonzero_relative_evolution_retained"] is True
