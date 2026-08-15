import json
from pathlib import Path


def test_v18_73_physical_promotion_artifact() -> None:
    payload = json.loads(Path(
        "artifacts/BHSM_aether_n3_fifth_bidirectional_probe_promotion_v18_73.json"
    ).read_text(encoding="utf-8"))
    result = payload["fifth_bidirectional_probe_promotion"]
    global_step = result["global_step"]
    child = result["event_to_complete_child"]
    persistence = result["persistence"]
    assert payload["validation_passed"]
    assert global_step["candidate_complete_norm"] < global_step["source_complete_norm"]
    assert child["local_chart_rank"] == 14
    assert child["resolved_dynamic_flux_envelope"] < 2.0e-5
    assert persistence["maximum_constraint_residual"] < 1.0e-8
    assert persistence["minimum_eta"] > 0.0
    assert persistence["nonzero_relative_evolution_retained"]
