import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def artifact(name: str) -> dict:
    return json.loads((ROOT / "artifacts" / name).read_text(encoding="utf-8"))


def test_response_scales_are_remeasured_at_each_accepted_state():
    rows = (
        ("twelfth", "v18_88", 0.804250811090346),
        ("thirteenth", "v18_92", 0.801699023846746),
        ("fourteenth", "v18_96", 0.801684037952532),
    )
    for ordinal, version, source_norm in rows:
        payload = artifact(
            f"BHSM_aether_n3_{ordinal}_direct_residual_scale_audit_{version}.json"
        )
        result = payload[f"{ordinal}_direct_residual_scale_audit"]
        pair = result["selected_finest_common_stable_pair"]
        assert payload["validation_passed"] is True
        assert result["source_complete_norm"] == source_norm
        assert pair["coarse_step"] == 3.0e-7
        assert pair["fine_step"] == 1.0e-7
        assert pair["all_directions_stable"] is True


def test_bidirectional_probes_use_exact_merit_not_invalid_solver_claims():
    rows = (
        ("ninth", "v18_89", 0.801699023846746),
        ("tenth", "v18_93", 0.801684037952532),
        ("eleventh", "v18_97", 0.801038620295453),
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
        assert selected["eta_minimum"] > 1.0e-5
        assert result["componentwise_monotonicity_required"] is False
        assert result["must_remain_on_previous_iterate_path"] is False


def test_every_selected_state_reconstructs_a_complete_moving_child():
    rows = (
        ("ninth", "v18_90"),
        ("tenth", "v18_94"),
        ("eleventh", "v18_98"),
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


def test_all_three_promotions_pass_the_unchanged_physical_gate():
    rows = (
        ("ninth", "v18_91", 0.801699023846746),
        ("tenth", "v18_95", 0.801684037952532),
        ("eleventh", "v18_99", 0.801038620295453),
    )
    previous = 0.804250811090346
    for ordinal, version, expected_norm in rows:
        payload = artifact(
            f"BHSM_aether_n3_{ordinal}_bidirectional_probe_promotion_{version}.json"
        )
        result = payload[f"{ordinal}_bidirectional_probe_promotion"]
        global_step = result["global_step"]
        child = result["event_to_complete_child"]
        persistence = result["persistence"]
        assert payload["validation_passed"] is True
        assert payload["FULL_BHSM_COMPLETE"] is False
        assert global_step["source_complete_norm"] == previous
        assert global_step["candidate_complete_norm"] == expected_norm
        assert global_step["complete_norm_reduction"] > 0.0
        assert child["local_chart_rank"] == 14
        assert child["resolved_dynamic_flux_envelope"] < 2.0e-5
        assert persistence["all_steps_valid"] is True
        assert persistence["nonzero_relative_evolution_retained"] is True
        previous = expected_norm
