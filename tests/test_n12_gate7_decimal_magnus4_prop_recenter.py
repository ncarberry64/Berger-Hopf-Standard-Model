from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_GATE7_DECIMAL_MAGNUS4_PROP_RECENTER_AUDIT.json"
)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def test_magnus4_recenter_removes_leading_midpoint_defect_without_promotion() -> None:
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    summary = payload["summary"]
    assert summary["maximum_Magnus4_PROP16_to_Richardson_reference"] < 3.2e-18
    assert summary["midpoint_to_Magnus4_reference_mismatch_reduction"] > 1.0e4
    assert summary["candidate_Magnus4_Y_plus_Z1_inflation_to_cone_lower"] > 9.0
    assert payload["identity"]["source_terms_added"] == 0
    assert payload["claim_boundary"]["Magnus4_PROP16_center_promotion"].startswith("OPEN")
    assert payload["claim_boundary"]["outward_Magnus4_Z1"] == "OPEN_INTERVAL_AUTHORITY"
    for relative, digest in payload["inputs"].items():
        assert _sha256(ROOT / relative) == digest
    assert _sha256(ROOT / payload["data"]) == payload["data_SHA256"]
    with np.load(ROOT / payload["data"]) as data:
        recenter = data["signed_affine_commutator_recenter"]
        proxy = data["causal_Magnus4_Z1_numerical_proxy"]
        assert recenter.shape == (371, 98)
        assert proxy.shape == (371,)
        assert np.all(recenter[0] == 0.0)
        assert proxy[0] == 0.0

