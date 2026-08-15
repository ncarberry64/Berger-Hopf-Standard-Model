import os
from pathlib import Path

from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_third_bidirectional_merit_manifold_probe_v18_62 import completion_payload


def test_v18_62_third_bidirectional_merit_manifold_probe() -> None:
    payload = completion_payload()
    result = payload["third_bidirectional_merit_manifold_probe"]
    assert payload["validation_passed"]
    assert payload["status"] == "VALIDATED"
    assert result["line_scan"]["both_orientations_scanned"]
    assert result["line_scan"]["exact_nonlinear_residual_authoritative"]
    assert result["direct_response"]["used_only_as_local_geometric_probe"]
    assert result["linear_probe"]["convergence_not_required_to_legitimize_proposal"]
    assert result["physical_solve_dimension"] == [376, 376]
    assert not result["componentwise_monotonicity_required"]
    if os.name == "nt":
        assert Path("artifacts/BHSM_aether_n3_third_bidirectional_merit_manifold_probe_v18_62.json").read_text(encoding="utf-8") == deterministic_json(payload)
