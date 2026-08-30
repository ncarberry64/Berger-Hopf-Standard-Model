from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_EXACT_CENTER_PHYSICAL_FIELD_JACOBIAN.json"


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def test_direct_exact_center_physical_field_jacobian_is_materialized() -> None:
    record = json.loads(RESULT.read_text(encoding="utf-8"))
    assert record["validation_passed"] is True
    assert record["summary"]["node_count"] == 48
    assert record["summary"]["physical_dimension"] == 73
    assert record["summary"]["minimum_tangent_alignment_singular_value"] > 0.99
    assert record["claim_boundary"]["continuous_outward_variational_carrier"] == "OPEN"
    data = ROOT / record["data"]
    assert _sha256(data) == record["data_SHA256"]
    with np.load(data) as source:
        assert source["physical_tangent_action"].shape == (48, 98, 73)
        assert source["normalized_field_first_physical_action"].shape == (48, 98, 73)
        assert source["physical_field_generator"].shape == (48, 73, 73)
        assert np.all(np.isfinite(source["physical_field_generator"]))


def test_exact_center_field_jacobian_provenance_matches_disk() -> None:
    record = json.loads(RESULT.read_text(encoding="utf-8"))
    for relative, expected in record["inputs"].items():
        assert _sha256(ROOT / relative) == expected
