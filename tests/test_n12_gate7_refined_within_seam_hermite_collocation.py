from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_REFINED_WITHIN_SEAM_HERMITE_COLLOCATION.json"


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def test_refined_within_seam_collocation_reduces_defect() -> None:
    record = json.loads(RESULT.read_text(encoding="utf-8"))
    assert record["validation_passed"] is True
    assert record["mesh"]["refined_nodes"] == 741
    assert record["mesh"]["refined_intervals"] == 740
    assert record["summary"]["flow_defect_reduction_factor"] > 1.0
    assert record["summary"]["minimum_selected_eigenline_gap"] > 1.0e-7
    data = ROOT / record["data"]
    assert _sha256(data) == record["data_SHA256"]
    with np.load(data) as source:
        assert source["refined_augmented_nodes"].shape == (741, 99)
        assert source["sampled_augmented_flow_defect"].shape == (2220, 99)


def test_refined_within_seam_collocation_provenance_matches_disk() -> None:
    record = json.loads(RESULT.read_text(encoding="utf-8"))
    for relative, expected in record["inputs"].items():
        assert _sha256(ROOT / relative) == expected
