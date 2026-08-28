from __future__ import annotations

import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
TRANSVERSE = BASE / "BHSM_N12_GATE7_EXACT_SIGNED_FULL_TRANSVERSE_CURVATURE_ADJUDICATION.json"
RAW = BASE / "BHSM_N12_GATE7_EXACT_SIGNED_FULL_TRANSVERSE_CURVATURE.json"
CENTER = BASE / "BHSM_N12_GATE7_EXACT_CENTER_CAUSAL_VECTOR_CERTIFICATE.json"
CENTER_DATA = CENTER.with_suffix(".npz")


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_full_transverse_curvature_adjudication_closes() -> None:
    raw = _load(RAW)
    payload = _load(TRANSVERSE)
    shards = [ROOT / path for path in raw["data_shards"]]
    assert len(shards) == 2
    assert all(path.is_file() and path.stat().st_size < 100_000_000 for path in shards)
    with np.load(shards[0]) as first, np.load(shards[1]) as second:
        assert np.concatenate((first["node_indices"], second["node_indices"])).tolist() == list(range(48))
        assert first["physical_time_transverse_D2f"].shape == (24, 72, 72, 72)
        assert second["physical_time_transverse_D2f"].shape == (24, 72, 72, 72)
    assert payload["validation_passed"] is True
    assert all(payload["validation"].values())
    assert payload["summary"]["transverse_curvature_owner_node"] == 0
    assert payload["summary"]["acceptance_ceiling_to_exact_maximum_ratio"] > 3000.0


def test_tensor_residuals_are_relative_binary64_scale() -> None:
    summary = _load(TRANSVERSE)["summary"]
    assert summary["maximum_first_response_relative_Frobenius_residual"] < 1.0e-12
    assert summary["maximum_second_response_relative_Frobenius_residual"] < 1.0e-12


def test_exact_center_causal_vector_certificate_closes() -> None:
    payload = _load(CENTER)
    assert payload["validation_passed"] is True
    assert all(payload["validation"].values())
    assert payload["summary"]["halo_to_exact_center_radius_ratio"] > 1.0e4
    assert payload["claim_boundary"]["causal_interval_vector_radius"] == "OPEN"


def test_exact_center_radius_data_are_finite() -> None:
    with np.load(CENTER_DATA) as source:
        vector = np.asarray(source["signed_center_vector"])
        radius = np.asarray(source["exact_total_center_radius"])
    assert vector.shape == (48, 73)
    assert radius.shape == (48,)
    assert np.all(np.isfinite(vector))
    assert np.all(np.isfinite(radius))
