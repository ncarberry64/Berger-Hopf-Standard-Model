from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_PROJECTED_EXACT_AFFINE_FINE_CENTER_CANDIDATE.json"


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def test_projected_exact_affine_fine_center_candidate_is_materialized() -> None:
    record = json.loads(RESULT.read_text(encoding="utf-8"))
    assert record["validation_passed"] is True
    summary = record["summary"]
    assert summary["node_count"] == 371
    assert summary["maximum_exact_affine_state_response_2_norm"] > 1.0e-7
    assert summary["maximum_projected_scaled_constraint_2_norm"] < 2.0e-14
    assert summary["maximum_projection_to_existing_radius_ratio"] > 10.0
    assert record["adjudication"]["projected_native_only_candidate"].startswith("SUPERSEDED")
    data = ROOT / record["data"]
    assert _sha256(data) == record["data_SHA256"]
    with np.load(data) as source:
        assert source["projected_states"].shape == (371, 98)
        assert source["exact_affine_descriptors"].shape == (371,)


def test_projected_exact_affine_fine_center_candidate_provenance_matches_disk() -> None:
    record = json.loads(RESULT.read_text(encoding="utf-8"))
    for relative, expected in record["inputs"].items():
        assert _sha256(ROOT / relative) == expected
