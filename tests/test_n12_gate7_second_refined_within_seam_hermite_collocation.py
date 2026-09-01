from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_SECOND_REFINED_WITHIN_SEAM_HERMITE_COLLOCATION.json"


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def test_second_refined_within_seam_collocation_is_routed() -> None:
    record = json.loads(RESULT.read_text(encoding="utf-8"))
    assert record["validation_passed"] is False
    assert record["mesh"]["refined_nodes"] == 1481
    assert record["mesh"]["refined_intervals"] == 1480
    assert record["summary"]["minimum_selected_eigenline_gap"] > 1.0e-7
    assert record["summary"]["flow_defect_reduction_factor"] < 1.0
    assert record["claim_boundary"]["continuous_action_constrained_center"] == (
        "OPEN_INTERVAL_AUTHORITY"
    )
    assert record["FULL_BHSM_COMPLETE"] is False
    data = ROOT / record["data"]
    assert _sha256(data) == record["data_SHA256"]
    with np.load(data) as source:
        assert source["refined_augmented_nodes"].shape == (1481, 99)
        assert source["sampled_augmented_flow_defect"].shape == (4440, 99)


def test_second_refined_provenance_matches_disk() -> None:
    record = json.loads(RESULT.read_text(encoding="utf-8"))
    for relative, expected in record["inputs"].items():
        assert _sha256(ROOT / relative) == expected
