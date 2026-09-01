from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
SOURCE = BASE / "BHSM_N12_GATE7_DECIMAL_SIGNED_SOURCE_QUADRATURE_AUDIT.json"
GREEN = BASE / "BHSM_N12_GATE7_DECIMAL_SIGNED_Y_GREEN_CONVERGENCE_AUDIT.json"


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def test_decimal_source_cross_quadrature_is_complete_and_subhalo() -> None:
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["intervals"] == list(range(370))
    assert payload["orders"] == [6, 8]
    assert payload["summary"]["selected_branches_seen"] == [24]
    assert payload["summary"]["maximum_local_candidate_halo_utilization"] < 0.01
    assert payload["claim_boundary"]["outward_interval_Y"] == "OPEN"
    for relative, digest in payload["inputs"].items():
        assert _sha256(ROOT / relative) == digest
    with np.load(ROOT / payload["data"]) as data:
        assert data["state_rate_residuals"].shape == (370 * 14, 98)
        assert set(data["sample_orders"].tolist()) == {6, 8}


def test_decimal_signed_green_cross_order_profile_is_subhalo() -> None:
    payload = json.loads(GREEN.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["identity"]["propagator_substeps_per_quarter_cell"] == 16
    assert payload["summary"]["candidate_halo_utilization"] < 0.06
    assert payload["claim_boundary"]["outward_interval_Y_and_Z1"] == "OPEN"
    for relative, digest in payload["inputs"].items():
        assert _sha256(ROOT / relative) == digest
    with np.load(ROOT / payload["data"]) as data:
        assert data["Gauss6_correction_profile"].shape == (371, 98)
        assert data["Gauss8_correction_profile"].shape == (371, 98)
        assert data["cross_order_profile_increment"].shape == (371,)

