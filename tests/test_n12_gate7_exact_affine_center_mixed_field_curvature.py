from __future__ import annotations

import json
import hashlib
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_MIXED_FIELD_CURVATURE.json"
DATA = RESULT.with_suffix(".npz")


def _payload() -> dict:
    return json.loads(RESULT.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def test_exact_affine_center_mixed_map_closes_with_scale_aware_solve_audit() -> None:
    payload = _payload()
    assert payload["validation_passed"] is True
    assert all(payload["validation"].values())
    assert payload["validation"][
        "all_bordered_response_normwise_backward_errors_below_1e_minus_12"
    ]
    summary = payload["summary"]
    assert summary["maximum_bordered_response_normwise_backward_error"] < 1.0e-12
    assert summary["maximum_absolute_bordered_response_residual"] >= 0.0


def test_exact_affine_center_mixed_map_has_the_retained_physical_shape() -> None:
    payload = _payload()
    assert payload["summary"]["evaluated_nodes"] == 48
    assert len(payload["rows"]) == 48
    with np.load(DATA) as source:
        mixed = np.asarray(
            source["physical_time_transverse_mixed_Green_curvature"]
        )
        nodes = np.asarray(source["node_indices"])
    assert mixed.shape == (48, 72, 72)
    assert np.array_equal(nodes, np.arange(48))
    assert np.all(np.isfinite(mixed))


def test_exact_affine_center_mixed_code_provenance_is_current() -> None:
    inputs = _payload()["inputs"]
    for relative in (
        "scripts/derive_n12_gate7_exact_affine_center_mixed_field_curvature.py",
        "scripts/derive_n12_gate7_exact_signed_mixed_field_curvature.py",
    ):
        assert inputs[relative] == _sha256(ROOT / relative)


def test_exact_affine_center_mixed_claim_boundary_remains_open_outward() -> None:
    boundary = _payload()["claim_boundary"]
    assert boundary["physical_transverse_Green_mixed_center_curvature"] == "DERIVED"
    assert boundary["outward_mixed_curvature_remainder"] == "OPEN"
    assert boundary["full_transverse_curvature"] == "OPEN"
    assert boundary["causal_interval_vector_radius"] == "OPEN"
    assert boundary["Gate7"] == "ACTIVE"
    assert boundary["FULL_BHSM_COMPLETE"] is False
