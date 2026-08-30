from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_CONSTRAINT_DESCRIPTOR_HERMITE_COLLOCATION_CANDIDATE.json"


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def test_constraint_descriptor_hermite_candidate_is_routed() -> None:
    record = json.loads(RESULT.read_text(encoding="utf-8"))
    assert record["validation_passed"] is False
    assert record["status"] == "HERMITE_COLLOCATION_CANDIDATE_REQUIRES_OWNER_REFINEMENT"
    assert record["mesh"]["fine_intervals"] == 370
    assert record["mesh"]["Gauss_samples_per_interval"] == 3
    summary = record["summary"]
    assert summary["maximum_endpoint_scaled_constraint_2_norm"] < 2.0e-14
    assert summary["flow_defect_reduction_factor"] < 1.0
    assert summary["minimum_selected_eigenline_gap"] > 1.0e-7
    assert record["adjudication"]["continuous_center"].startswith("OPEN")
    assert record["claim_boundary"]["FULL_BHSM_COMPLETE"] is False
    data = ROOT / record["data"]
    assert _sha256(data) == record["data_SHA256"]
    with np.load(data) as source:
        assert source["corrected_augmented_endpoints"].shape == (371, 99)
        assert source["sampled_augmented_flow_defect"].shape == (1110, 99)


def test_constraint_descriptor_hermite_candidate_provenance_matches_disk() -> None:
    record = json.loads(RESULT.read_text(encoding="utf-8"))
    for relative, expected in record["inputs"].items():
        assert _sha256(ROOT / relative) == expected
