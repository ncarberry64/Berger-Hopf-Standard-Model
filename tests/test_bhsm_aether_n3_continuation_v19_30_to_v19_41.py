import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def artifact(name: str) -> dict:
    return json.loads((ROOT / "artifacts" / name).read_text(encoding="utf-8"))


def test_v19_30_v19_34_v19_38_remeasure_accepted_sources():
    rows = (
        ("twenty_second", "v19_30", 0.793187079982019, 3.0e-7, 1.0e-7),
        ("twenty_third", "v19_34", 0.792728134993666, 1.0e-6, 3.0e-7),
        ("twenty_fourth", "v19_38", 0.792726003595835, 1.0e-6, 3.0e-7),
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


def test_v19_probes_keep_invalid_solver_and_exact_merit_authority():
    rows = (
        ("nineteenth", "v19_31", 0.015625, 0.792728134993666),
        (
            "twentieth", "v19_35",
            4.65661e-10, 0.792726003595835,
        ),
        ("twenty_first", "v19_39", 0.0625, 0.791308733253912),
    )
    for ordinal, version, alpha, expected_norm in rows:
        payload = artifact(
            f"BHSM_aether_n3_{ordinal}_bidirectional_merit_manifold_probe_{version}.json"
        )
        result = payload[f"{ordinal}_bidirectional_merit_manifold_probe"]
        selected = result[
            "selected_true_merit_candidate_pending_child_acceptance"
        ]
        assert payload["validation_passed"] is True
        assert payload["solver_interpretation"] == "INVALIDATED"
        assert selected["alpha"] == alpha
        assert selected["metrics"]["complete"] == expected_norm
        assert selected["complete_norm_reduction"] > 0.0
        assert result["componentwise_monotonicity_required"] is False


def test_every_candidate_reconstructs_a_rank_14_moving_child():
    rows = (
        ("nineteenth", "v19_32"),
        ("twentieth", "v19_36"),
        ("twenty_first", "v19_40"),
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


def test_v19_33_v19_37_v19_41_pass_unchanged_promotion_gates():
    rows = (
        (
            "nineteenth", "v19_33",
            0.793187079982019, 0.792728134993666,
        ),
        (
            "twentieth", "v19_37",
            0.792728134993666, 0.792726003595835,
        ),
        (
            "twenty_first", "v19_41",
            0.792726003595835, 0.791308733253912,
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


def test_microscopic_v19_35_line_fraction_is_not_a_persistent_stall():
    v19_35 = artifact(
        "BHSM_aether_n3_twentieth_bidirectional_merit_manifold_probe_v19_35.json"
    )["twentieth_bidirectional_merit_manifold_probe"][
        "selected_true_merit_candidate_pending_child_acceptance"
    ]
    v19_39 = artifact(
        "BHSM_aether_n3_twenty_first_bidirectional_merit_manifold_probe_v19_39.json"
    )["twenty_first_bidirectional_merit_manifold_probe"][
        "selected_true_merit_candidate_pending_child_acceptance"
    ]
    assert v19_35["alpha"] < 1.0e-9
    assert v19_39["alpha"] == 0.0625
    assert v19_39["complete_norm_reduction"] > 1.0e-3
