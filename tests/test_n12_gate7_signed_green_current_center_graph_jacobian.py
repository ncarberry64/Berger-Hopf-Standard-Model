from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_SIGNED_GREEN_CURRENT_CENTER_GRAPH_JACOBIAN.json"


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def test_current_center_graph_jacobian_is_materialized() -> None:
    record = json.loads(RESULT.read_text(encoding="utf-8"))
    assert record["validation_passed"] is True
    assert record["summary"]["fine_nodes_through_stop"] == 371
    assert record["summary"]["selected_branches_seen"] == [24]
    assert record["summary"]["minimum_selected_eigenline_gap"] > 1.0e-7
    assert record["claim_boundary"]["FULL_BHSM_COMPLETE"] is False
    data = ROOT / record["data"]
    assert _sha256(data) == record["data_SHA256"]
    with np.load(data) as source:
        assert source["graph_Jacobian_action"].shape == (371, 98, 98)
        assert source["descriptor_gradient_action"].shape == (371, 98)


def test_current_center_graph_jacobian_provenance_matches_disk() -> None:
    record = json.loads(RESULT.read_text(encoding="utf-8"))
    for relative, expected in record["inputs"].items():
        assert _sha256(ROOT / relative) == expected
