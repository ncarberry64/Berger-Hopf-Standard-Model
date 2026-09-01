from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_EXACT_AFFINE_TERMINAL_INTERVAL_NEWTON_FIRST_HIT.json"


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def test_interval_newton_materializes_the_canonical_first_hit() -> None:
    record = json.loads(RESULT.read_text(encoding="utf-8"))
    assert record["validation_passed"] is True
    interval = record["interval_Newton"]["first_hit_action_time_interval"]
    assert 92.30037143976939 < interval[0] < interval[1] < 92.30513924040065
    assert interval[1] - interval[0] < 8.0e-6
    assert interval[0] <= record["representative"]["action_time"] <= interval[1]
    assert "NOT_A_NUMERICALLY_RESOLVED_ZERO" in record["representative"]["role"]
    data = ROOT / record["data"]
    assert _sha256(data) == record["data_SHA256"]
    with np.load(data) as source:
        assert source["representative_state"].shape == (98,)
        assert float(source["first_hit_action_time_radius"]) > 0.0


def test_interval_newton_first_hit_provenance_matches_disk() -> None:
    record = json.loads(RESULT.read_text(encoding="utf-8"))
    for relative, expected in record["inputs"].items():
        assert _sha256(ROOT / relative) == expected
