import json
from pathlib import Path


def test_v18_71_exact_merit_probe_artifact() -> None:
    payload = json.loads(Path(
        "artifacts/BHSM_aether_n3_fifth_bidirectional_merit_manifold_probe_v18_71.json"
    ).read_text(encoding="utf-8"))
    result = payload["fifth_bidirectional_merit_manifold_probe"]
    selected = result["selected_true_merit_candidate_pending_child_acceptance"]
    assert payload["validation_passed"]
    assert payload["solver_interpretation"] == "INVALIDATED"
    assert result["line_scan"]["both_orientations_scanned"]
    assert selected["complete_norm_reduction"] > 0.0
    assert selected["eta_minimum"] > 1.0e-5
    assert result["physical_equations_changed"] is False
