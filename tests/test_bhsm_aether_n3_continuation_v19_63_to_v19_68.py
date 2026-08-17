import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def artifact(name: str) -> dict:
    return json.loads((ROOT / "artifacts" / name).read_text(encoding="utf-8"))


def test_v19_66_primary_is_rejected_only_by_unchanged_flux_gate():
    payload = artifact(
        "BHSM_aether_n3_twenty_seventh_bidirectional_probe_promotion_v19_66.json"
    )
    result = payload["twenty_seventh_bidirectional_probe_promotion"]
    global_step = result["global_step"]
    child = result["event_to_complete_child"]
    persistence = result["persistence"]
    assert payload["status"] == "INVALIDATED"
    assert global_step["candidate_complete_norm"] == 0.788121714849599
    assert global_step["complete_norm_reduction"] > 0.0
    assert global_step["eta_minimum"] > 1.0e-5
    assert child["local_chart_rank"] == 14
    assert child["resolved_dynamic_flux_envelope"] > 2.0e-5
    assert persistence["all_steps_valid"] is True


def test_v19_67_selects_next_lowest_candidate_without_gate_change():
    payload = artifact(
        "BHSM_aether_n3_twenty_seventh_bidirectional_fallback_child_v19_67.json"
    )
    child = payload["twenty_seventh_bidirectional_fallback_child"]
    assert payload["validation_passed"] is True
    assert child["line_selection"]["orientation"] == "negative"
    assert child["line_selection"]["alpha"] == -0.00390625
    assert child["line_selection"]["complete_norm"] == 0.788591183052825
    assert child["rejected_predecessor"]["acceptance_gate_changed"] is False
    assert child["chart"]["full_chart_rank"] == 14
    assert child["additional_global_KKT_rows"] == 0


def test_v19_68_fallback_passes_complete_physical_gate():
    payload = artifact(
        "BHSM_aether_n3_twenty_seventh_bidirectional_fallback_promotion_v19_68.json"
    )
    result = payload["twenty_seventh_bidirectional_fallback_promotion"]
    global_step = result["global_step"]
    child = result["event_to_complete_child"]
    persistence = result["persistence"]
    assert payload["validation_passed"] is True
    assert payload["FULL_BHSM_COMPLETE"] is False
    assert global_step["source_complete_norm"] == 0.788717933323162
    assert global_step["candidate_complete_norm"] == 0.788591183052825
    assert global_step["primary_candidate_flux_rejection_preserved"] is True
    assert child["resolved_dynamic_flux_envelope"] < 2.0e-5
    assert child["local_chart_rank"] == 14
    assert persistence["all_steps_valid"] is True
    assert persistence["nonzero_relative_evolution_retained"] is True
