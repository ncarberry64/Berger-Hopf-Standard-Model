import os
from pathlib import Path


def test_v18_56_second_bidirectional_merit_manifold_probe() -> None:
    payload = json.loads(Path(
        "artifacts/BHSM_aether_n3_second_bidirectional_merit_manifold_probe_v18_56.json"
    ).read_text(encoding="utf-8"))
    result = payload["second_bidirectional_merit_manifold_probe"]
    assert payload["validation_passed"]
    assert payload["status"] == "VALIDATED"
    assert result["line_scan"]["both_orientations_scanned"]
    assert result["line_scan"]["exact_nonlinear_residual_authoritative"]
    assert result["direct_response"]["used_only_as_local_geometric_probe"]
    assert result["linear_probe"]["convergence_not_required_to_legitimize_proposal"]
    assert result["physical_solve_dimension"] == [376, 376]
    assert not result["componentwise_monotonicity_required"]
    if os.name == "nt":
        assert Path("artifacts/BHSM_aether_n3_second_bidirectional_merit_manifold_probe_v18_56.json").read_text(encoding="utf-8") == deterministic_json(payload)
