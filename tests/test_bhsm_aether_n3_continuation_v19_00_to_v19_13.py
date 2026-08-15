import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def artifact(name: str) -> dict:
    return json.loads((ROOT / "artifacts" / name).read_text(encoding="utf-8"))


def test_v19_response_scales_are_measured_at_each_accepted_source():
    rows = (
        ("fifteenth", "v19_00", 0.801038620295453, 1.0e-6, 3.0e-7),
        ("sixteenth", "v19_04", 0.797947455518253, 1.0e-6, 3.0e-7),
        ("seventeenth", "v19_08", 0.797206261170734, 3.0e-7, 1.0e-7),
    )
    for ordinal, version, source_norm, coarse, fine in rows:
        payload = artifact(
            f"BHSM_aether_n3_{ordinal}_direct_residual_scale_audit_{version}.json"
        )
        result = payload[f"{ordinal}_direct_residual_scale_audit"]
        pair = result["selected_finest_common_stable_pair"]
        assert payload["validation_passed"] is True
        assert result["source_complete_norm"] == source_norm
        assert pair["coarse_step"] == coarse
        assert pair["fine_step"] == fine
        assert pair["all_directions_stable"] is True


def test_v19_probes_preserve_invalid_solver_classification():
    rows = (
        ("twelfth", "v19_01", 0.797947455518253),
        ("thirteenth", "v19_05", 0.797206261170734),
        ("fourteenth", "v19_09", 0.795262882781664),
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


def test_v19_03_and_v19_07_pass_the_unchanged_gate():
    rows = (
        ("twelfth", "v19_03", 0.801038620295453, 0.797947455518253),
        ("thirteenth", "v19_07", 0.797947455518253, 0.797206261170734),
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
        assert global_step["source_complete_norm"] == source
        assert global_step["candidate_complete_norm"] == candidate
        assert child["local_chart_rank"] == 14
        assert child["resolved_dynamic_flux_envelope"] < 2.0e-5
        assert persistence["all_steps_valid"] is True
        assert persistence["nonzero_relative_evolution_retained"] is True


def test_v19_11_rejects_only_the_primary_flux_failure():
    payload = artifact(
        "BHSM_aether_n3_fourteenth_bidirectional_probe_promotion_v19_11.json"
    )
    result = payload["fourteenth_bidirectional_probe_promotion"]
    child = result["event_to_complete_child"]
    persistence = result["persistence"]
    failed = [
        name for name, passed in payload["validation"].items() if not passed
    ]
    assert payload["status"] == "INVALIDATED"
    assert payload["validation_passed"] is False
    assert failed == ["resolved_dynamic_flux_closed"]
    assert child["resolved_dynamic_flux_envelope"] == 2.4244980204e-5
    assert persistence["all_steps_valid"] is True
    assert persistence["nonzero_relative_evolution_retained"] is True


def test_v19_12_v19_13_promote_the_next_exact_merit_fallback():
    child_payload = artifact(
        "BHSM_aether_n3_fourteenth_bidirectional_fallback_child_v19_12.json"
    )
    child = child_payload["fourteenth_bidirectional_fallback_child"]
    assert child_payload["validation_passed"] is True
    assert child["line_selection"]["backtrack"] == 6
    assert child["line_selection"]["complete_norm"] == 0.795953277613514
    assert child["chart"]["full_chart_rank"] == 14
    assert child["rejected_predecessor"]["acceptance_gate_changed"] is False

    payload = artifact(
        "BHSM_aether_n3_fourteenth_bidirectional_fallback_promotion_v19_13.json"
    )
    result = payload["fourteenth_bidirectional_fallback_promotion"]
    global_step = result["global_step"]
    promoted_child = result["event_to_complete_child"]
    persistence = result["persistence"]
    assert payload["validation_passed"] is True
    assert payload["FULL_BHSM_COMPLETE"] is False
    assert global_step["source_complete_norm"] == 0.797206261170734
    assert global_step["candidate_complete_norm"] == 0.795953277613514
    assert global_step["primary_candidate_flux_rejection_preserved"] is True
    assert promoted_child["local_chart_rank"] == 14
    assert promoted_child["resolved_dynamic_flux_envelope"] < 2.0e-5
    assert persistence["all_steps_valid"] is True
    assert persistence["nonzero_relative_evolution_retained"] is True


def test_downstream_doctrine_remains_explicitly_open():
    text = (
        ROOT / "docs" / "BHSM_DOWNSTREAM_PHYSICAL_DOCTRINE_LEDGER_V19_03.md"
    ).read_text(encoding="utf-8")
    names = (
        "ACTION_DERIVED_EVENT_HISTORY_TO_CHILD_SIGNATURE_MAP",
        "SCALE_DEPENDENT_EXTERNAL_PARTICLE_SIGNATURE_EQUIVALENCE",
        "AETHER_TO_REGULAR_SPACETIME_RECONSTRUCTION_AND_RETURN_MAP",
        "ACTION_DERIVED_CYCLE_ENVIRONMENT_PHYSICAL_SCALE_MAP",
        "INTRINSIC_DECAY_AS_AUTONOMOUS_PARTICLE_CLASS_EXIT",
        "EXTERNAL_INTERACTION_DRIVEN_PARTICLE_CLASS_TRANSITION",
        "ACTION_DERIVED_EXTREME_SCALE_MAP_TO_EFFECTIVE_COLOR_CONFINEMENT_PHENOMENOLOGY",
        "COMMON_ULTRAVIOLET_AND_COSMIC_SCALE_RESPONSE_LAW",
    )
    assert all(name in text for name in names)
    assert "OPEN HYPOTHESIS" in text
    assert "No item below authorizes equation 377" in text
