from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_WITHIN_SEAM_CONSTRAINT_CENTER_OBSTRUCTION.json"


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def test_within_seam_center_obstruction_is_materialized() -> None:
    record = json.loads(RESULT.read_text(encoding="utf-8"))
    assert record["validation_passed"] is True
    summary = record["summary"]
    assert summary["birth_macro_node_scaled_constraint_2_norm"] < 2.0e-12
    assert summary["maximum_corrected_macro_node_scaled_constraint_2_norm"] > 1.0e-11
    assert summary["first_hit_midpoint_scaled_constraint_2_norm"] > 1.0e-11
    assert summary["maximum_macro_node_linearized_correction_to_center_radius_ratio"] > 10.0
    assert summary["maximum_seam_midpoint_scaled_constraint_2_norm"] > 1.0e-5
    assert summary["maximum_four_step_Newton_final_scaled_constraint_2_norm"] < 2.0e-14
    assert record["adjudication"]["Newton_projected_midpoints"] == "DIAGNOSTIC_ONLY_NOT_A_FLOW_CONNECTION"
    data = ROOT / record["data"]
    assert _sha256(data) == record["data_SHA256"]
    with np.load(data) as source:
        assert source["macro_node_scaled_constraint_2_norm"].shape == (48,)
        assert source["macro_node_linearized_action_correction_2_norm"].shape == (48,)
        assert source["seam_midpoint_initial_scaled_constraint_2_norm"].shape == (47,)


def test_within_seam_center_obstruction_provenance_matches_disk() -> None:
    record = json.loads(RESULT.read_text(encoding="utf-8"))
    for relative, expected in record["inputs"].items():
        assert _sha256(ROOT / relative) == expected
