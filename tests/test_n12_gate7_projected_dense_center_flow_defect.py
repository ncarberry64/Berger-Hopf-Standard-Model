from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_PROJECTED_DENSE_CENTER_FLOW_DEFECT.json"


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def test_projected_dense_center_flow_defect_is_routed() -> None:
    record = json.loads(RESULT.read_text(encoding="utf-8"))
    assert record["validation_passed"] is True
    assert record["mesh"]["cells"] == 370
    summary = record["summary"]
    assert summary["maximum_scaled_constraint_2_norm"] < 2.0e-12
    assert summary["maximum_augmented_flow_defect_2_norm"] > 1.0e-6
    assert summary["minimum_selected_eigenline_gap"] > 1.0e-7
    assert record["adjudication"]["continuous_shadowing_center"] == "OPEN"
    data = ROOT / record["data"]
    assert _sha256(data) == record["data_SHA256"]
    with np.load(data) as source:
        assert source["augmented_flow_defect"].shape == (370, 99)
        assert source["scaled_constraint_2_norm"].shape == (370,)


def test_projected_dense_center_flow_defect_provenance_matches_disk() -> None:
    record = json.loads(RESULT.read_text(encoding="utf-8"))
    for relative, expected in record["inputs"].items():
        assert _sha256(ROOT / relative) == expected
