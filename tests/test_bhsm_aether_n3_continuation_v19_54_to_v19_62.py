import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def artifact(name: str) -> dict:
    return json.loads((ROOT / "artifacts" / name).read_text(encoding="utf-8"))


def test_v19_57_and_v19_61_pass_unchanged_physical_gate():
    rows = (
        ("twenty_fifth", "v19_57", 0.789572774913855, 0.788966669806045),
        ("twenty_sixth", "v19_61", 0.788966669806045, 0.788717933323162),
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


def test_v19_62_exact_f376_replay_and_layout():
    payload = artifact(
        "BHSM_N3_RESIDUAL_OWNERSHIP_AND_CLOSURE_DISTANCE_AUDIT_V19_62.json"
    )
    audit = payload["residual_ownership_and_closure_distance_audit"]
    latest = audit["accepted_frontiers"][-1]
    assert payload["validation_passed"] is True
    assert latest["version"] == "v19.61"
    assert latest["total_l2_norm"] == 0.788717933323162
    assert len(audit["accepted_frontiers"]) == 20
    assert set(latest["blocks"]) == {
        "F_scale", "F_u", "F_w", "F_v", "F_lapse", "F_shift",
        "F_period", "F_event",
    }
    assert audit["residual_definition"]["row_scaling_added"] is False
    assert audit["residual_definition"]["equations_changed"] is False


def test_v19_62_supports_distributed_descent_classification():
    payload = artifact(
        "BHSM_N3_RESIDUAL_OWNERSHIP_AND_CLOSURE_DISTANCE_AUDIT_V19_62.json"
    )
    audit = payload["residual_ownership_and_closure_distance_audit"]
    latest = audit["accepted_frontiers"][-1]
    assert audit["classification"] == "OUTCOME A: DISTRIBUTED_DESCENT_CONTINUES"
    assert audit["total_trend"]["label"] == "FALLING"
    assert audit["latest_dominance"]["largest_block"] == "F_period"
    assert audit["latest_dominance"]["fraction_total_squared"] < 0.60
    assert audit["latest_history_localization"]["fraction_stationarity_squared"] < 0.70
    assert latest["blocks"]["F_period"]["l2_norm"] > 0.0
    assert audit["block_trends"]["F_period"]["label"] == "FALLING"
    assert audit["block_trends"]["F_w"]["label"] == "FALLING"
    assert audit["block_trends"]["F_v"]["label"] == "FALLING"
    assert audit["first_action_owned_blocker"] is None
    assert len(audit["latest_largest_20_rows"]) == 20
    assert payload["active_calculation"] == "RESUME_UNCHANGED_N3_CONTINUATION"


def test_v19_62_does_not_claim_local_root_basin():
    payload = artifact(
        "BHSM_N3_RESIDUAL_OWNERSHIP_AND_CLOSURE_DISTANCE_AUDIT_V19_62.json"
    )
    evidence = payload["residual_ownership_and_closure_distance_audit"][
        "local_root_basin_evidence"
    ]
    assert evidence["increasing_fractional_merit_reduction"] is False
    assert evidence["coherent_direction_response"] is False
    assert evidence["increasingly_accurate_local_linearization"] is False
