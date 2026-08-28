from __future__ import annotations

import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_SIGNED_CAUSAL_VECTOR_BOOTSTRAP.json"
DATA = RESULT.with_suffix(".npz")


def _payload() -> dict:
    return json.loads(RESULT.read_text(encoding="utf-8"))


def test_signed_center_vector_bootstrap_closes_structurally() -> None:
    payload = _payload()
    assert payload["structural_validation_passed"] is True
    assert all(payload["structural_validation"].values())
    assert payload["validation_passed"] is False


def test_signed_vector_preserves_large_halo_headroom() -> None:
    summary = _payload()["summary"]
    assert summary["maximum_total_center_radius"] < 1.0e-12
    assert summary["halo_to_center_radius_ratio"] > 1.0e4
    assert summary[
        "maximum_uniform_transverse_profile_inflation_before_halo_failure"
    ] > 1000.0


def test_saved_vector_radius_shapes_are_exact() -> None:
    with np.load(DATA) as source:
        vector = np.asarray(source["signed_center_vector"])
        radius = np.asarray(source["total_center_radius"])
        green = np.asarray(source["causal_green_norm"])
    assert vector.shape == (48, 73)
    assert radius.shape == (48,)
    assert green.shape == (48, 48)
    assert np.all(np.isfinite(vector))
    assert np.allclose(np.triu(green), 0.0, atol=0.0, rtol=0.0)


def test_claim_boundary_does_not_promote_outward_authority() -> None:
    boundary = _payload()["claim_boundary"]
    assert boundary["signed_directional_and_mixed_center_vector"] == "DERIVED"
    assert boundary["center_transverse_quadratic_error"] == "RECONNAISSANCE_BOUND_ONLY"
    assert boundary["causal_interval_vector_radius"] == "OPEN"
    assert boundary["Gate7"] == "ACTIVE"
    assert boundary["FULL_BHSM_COMPLETE"] is False
