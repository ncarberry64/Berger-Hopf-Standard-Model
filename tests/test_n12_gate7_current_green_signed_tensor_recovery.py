from __future__ import annotations

import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / (
    "artifacts/current_semantics/"
    "BHSM_N12_GATE7_CURRENT_GREEN_SIGNED_TENSOR_RECOVERY_COMPUTE_JUSTIFICATION.json"
)
BENCHMARK = ROOT / (
    "artifacts/flagship_integration/"
    ".current_green_signed_transverse_tensor_recovery_work/midpoint_001.npz"
)


def _payload() -> dict[str, object]:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_recovery_benchmark_reproduces_the_published_tensor_norms() -> None:
    payload = _payload()
    assert payload["campaign_authorized"] is True
    assert payload["validation_passed"] is True
    with np.load(BENCHMARK) as source:
        assert source["quadratic_tensor"].shape == (99, 73, 73)
        assert source["transverse_basis"].shape == (74, 73)
        assert float(source["total_Frobenius_relative_residual"]) < 5.0e-13
        assert float(
            source["output_Frobenius_maximum_relative_residual"]
        ) < 5.0e-13
        assert float(source["basis_orthonormal_residual_2_norm"]) < 5.0e-13
        assert float(source["basis_axis_residual_2_norm"]) < 5.0e-13


def test_recovery_stays_inside_the_fixed_compute_and_claim_boundaries() -> None:
    payload = _payload()
    cost = payload["cost"]
    assert cost["selected_worker_count"] == 4
    assert cost["projected_recovery_CPU_hours"] < cost[
        "fixed_campaign_CPU_ceiling"
    ]
    boundary = payload["claim_boundary"]
    assert boundary["SIGNED_CENTER_TENSORS_RECOVERED"] is False
    assert boundary["SIGNED_CAUSAL_TRANSVERSE_OPERATOR_DERIVED"] is False
    assert boundary["OUTWARD_TRANSVERSE_REMAINDER_DERIVED"] is False
    assert boundary["GATE7_CLOSED"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False
