import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def artifact(name: str) -> dict:
    return json.loads((ROOT / "artifacts" / name).read_text(encoding="utf-8"))


def test_v19_70_and_v19_74_use_exact_merit_not_solver_status():
    rows = (
        ("twenty_eighth", "v19_70", 0.78740009582354),
        ("twenty_ninth", "v19_74", 0.783424601549721),
    )
    for ordinal, version, expected in rows:
        payload = artifact(
            f"BHSM_aether_n3_{ordinal}_bidirectional_merit_manifold_probe_{version}.json"
        )
        result = payload[f"{ordinal}_bidirectional_merit_manifold_probe"]
        selected = result[
            "selected_true_merit_candidate_pending_child_acceptance"
        ]
        assert payload["solver_interpretation"] == "INVALIDATED"
        assert payload["validation_passed"] is True
        assert selected["metrics"]["complete"] == expected
        assert selected["complete_norm_reduction"] > 0.0
        assert result["componentwise_monotonicity_required"] is False


def test_v19_72_and_v19_76_pass_unchanged_complete_gate():
    rows = (
        (
            "twenty_eighth", "v19_72",
            0.788591183052825, 0.78740009582354,
        ),
        (
            "twenty_ninth", "v19_76",
            0.78740009582354, 0.783424601549721,
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
        assert child["local_chart_rank"] == 14
        assert child["resolved_dynamic_flux_envelope"] < 2.0e-5
        assert persistence["all_steps_valid"] is True
        assert persistence["nonzero_relative_evolution_retained"] is True


def test_v19_76_is_material_recent_merit_reduction():
    payload = artifact(
        "BHSM_aether_n3_twenty_ninth_bidirectional_probe_promotion_v19_76.json"
    )
    reduction = payload["twenty_ninth_bidirectional_probe_promotion"][
        "global_step"
    ]["complete_norm_reduction"]
    assert reduction == 0.003975494273818
