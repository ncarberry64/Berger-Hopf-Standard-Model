from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_DIRECT_HERMITE_SIMPSON_MULTIPLE_SHOOTING_SOURCE.json"


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def test_direct_multiple_shooting_source_is_materialized_not_promoted() -> None:
    record = json.loads(RESULT.read_text(encoding="utf-8"))
    assert record["validation_passed"] is True
    assert record["mesh"] == {"augmented_dimension": 99, "shooting_intervals": 370}
    assert record["adjudication"]["interpolation_only_refinement"].startswith("REJECTED")
    assert record["adjudication"]["repeated_signed_Green_fixed_point"].startswith("REJECTED")
    assert record["claim_boundary"]["continuous_action_constrained_center"].startswith("OPEN")
    assert record["FULL_BHSM_COMPLETE"] is False
    data = ROOT / record["data"]
    assert _sha256(data) == record["data_SHA256"]
    with np.load(data) as source:
        assert source["Hermite_Simpson_shooting_residual"].shape == (370, 99)
        assert source["exact_midpoint_rates"].shape == (370, 99)


def test_direct_multiple_shooting_source_provenance_matches_disk() -> None:
    record = json.loads(RESULT.read_text(encoding="utf-8"))
    for relative, expected in record["inputs"].items():
        assert _sha256(ROOT / relative) == expected
