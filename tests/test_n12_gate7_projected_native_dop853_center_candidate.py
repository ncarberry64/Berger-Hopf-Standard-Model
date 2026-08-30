from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_PROJECTED_NATIVE_DOP853_CENTER_CANDIDATE.json"


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def test_projected_native_dop853_center_candidate_is_materialized() -> None:
    record = json.loads(RESULT.read_text(encoding="utf-8"))
    assert record["validation_passed"] is True
    summary = record["summary"]
    assert summary["node_count"] == 371
    assert summary["maximum_native_scaled_constraint_2_norm"] > 1.0e-11
    assert summary["maximum_projected_scaled_constraint_2_norm"] < 2.0e-14
    assert summary["maximum_reconnaissance_halo_utilization"] < 1.0
    assert record["adjudication"]["continuous_projected_trajectory"] == "OPEN"
    data = ROOT / record["data"]
    assert _sha256(data) == record["data_SHA256"]
    with np.load(data) as source:
        assert source["projected_states"].shape == (371, 98)
        assert source["one_step_action_corrections"].shape == (371, 98)
        assert np.all(np.diff(source["action_times"]) > 0.0)


def test_projected_native_dop853_center_candidate_provenance_matches_disk() -> None:
    record = json.loads(RESULT.read_text(encoding="utf-8"))
    for relative, expected in record["inputs"].items():
        assert _sha256(ROOT / relative) == expected
