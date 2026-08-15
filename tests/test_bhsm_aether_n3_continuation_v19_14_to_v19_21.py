import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def artifact(name: str) -> dict:
    return json.loads((ROOT / "artifacts" / name).read_text(encoding="utf-8"))


def test_v19_14_and_v19_18_remeasure_the_accepted_sources():
    rows = (
        ("eighteenth", "v19_14", 0.795953277613514, 3.0e-7, 1.0e-7),
        ("nineteenth", "v19_18", 0.795713884217715, 1.0e-6, 3.0e-7),
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


def test_v19_15_and_v19_19_use_exact_merit_not_solver_claims():
    rows = (
        ("fifteenth", "v19_15", 0.795713884217715),
        ("sixteenth", "v19_19", 0.795019734745765),
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


def test_v19_16_and_v19_20_reconstruct_complete_moving_children():
    rows = (
        ("fifteenth", "v19_16"),
        ("sixteenth", "v19_20"),
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


def test_v19_17_and_v19_21_pass_every_unchanged_promotion_gate():
    rows = (
        (
            "fifteenth", "v19_17",
            0.795953277613514, 0.795713884217715,
        ),
        (
            "sixteenth", "v19_21",
            0.795713884217715, 0.795019734745765,
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
