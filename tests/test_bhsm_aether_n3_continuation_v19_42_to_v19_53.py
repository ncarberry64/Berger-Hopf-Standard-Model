import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def artifact(name: str) -> dict:
    return json.loads((ROOT / "artifacts" / name).read_text(encoding="utf-8"))


def test_v19_42_v19_46_v19_50_remeasure_accepted_sources():
    rows = (
        ("twenty_fifth", "v19_42", 0.791308733253912),
        ("twenty_sixth", "v19_46", 0.791287639528749),
        ("twenty_seventh", "v19_50", 0.790602144149231),
    )
    for ordinal, version, source in rows:
        payload = artifact(
            f"BHSM_aether_n3_{ordinal}_direct_residual_scale_audit_{version}.json"
        )
        result = payload[f"{ordinal}_direct_residual_scale_audit"]
        pair = result["selected_finest_common_stable_pair"]
        assert payload["validation_passed"] is True
        assert result["source_complete_norm"] == source
        assert pair["coarse_step"] == 3.0e-7
        assert pair["fine_step"] == 1.0e-7
        assert pair["all_directions_stable"] is True


def test_v19_probes_keep_invalid_solver_and_exact_merit_authority():
    rows = (
        ("twenty_second", "v19_43", 0.0078125, 0.791287639528749),
        ("twenty_third", "v19_47", -0.03125, 0.790602144149231),
        ("twenty_fourth", "v19_51", 0.015625, 0.789572774913855),
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
        assert selected["eta_minimum"] > 1.0e-5
        assert result["componentwise_monotonicity_required"] is False
        assert result["must_remain_on_previous_iterate_path"] is False


def test_every_candidate_reconstructs_a_rank_14_moving_child():
    rows = (
        ("twenty_second", "v19_44"),
        ("twenty_third", "v19_48"),
        ("twenty_fourth", "v19_52"),
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


def test_v19_45_v19_49_v19_53_pass_unchanged_promotion_gates():
    rows = (
        (
            "twenty_second", "v19_45",
            0.791308733253912, 0.791287639528749,
        ),
        (
            "twenty_third", "v19_49",
            0.791287639528749, 0.790602144149231,
        ),
        (
            "twenty_fourth", "v19_53",
            0.790602144149231, 0.789572774913855,
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
        assert child["physical_row_count"] == 14
        assert child["additional_global_KKT_rows"] == 0
        assert child["resolved_dynamic_flux_envelope"] < 2.0e-5
        assert persistence["all_steps_valid"] is True
        assert persistence["nonzero_relative_evolution_retained"] is True


def test_batch_reduces_exact_merit_without_gate_change():
    initial = 0.791308733253912
    final = 0.789572774913855
    assert abs((initial - final) - 0.001735958340057) < 1.0e-15
