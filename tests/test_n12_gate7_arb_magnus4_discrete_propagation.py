from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_GATE7_ARB_MAGNUS4_DISCRETE_PROPAGATION.json"
)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def test_all_magnus4_quotient_blocks_have_outward_arb_evaluation_balls() -> None:
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["identity"]["fine_intervals"] == 370
    assert payload["identity"]["precision_bits"] == 128
    assert payload["identity"]["reset_to_stored_binary_center_at_each_macro"] is True
    assert payload["summary"]["maximum_Arb_Euclidean_radius"] < 9.0e-35
    assert payload["summary"]["maximum_aligned_to_reference_outward_difference"] < 1.1e-19
    assert payload["claim_boundary"][
        "finite_aligned_Magnus4_evaluation_roundoff"
    ] == "CERTIFIED_ON_ALL_RECENTERED_QUOTIENT_BLOCKS"
    assert payload["claim_boundary"]["global_block_composition"].startswith("OPEN")
    assert payload["claim_boundary"]["analytic_Magnus4_remainder"] == "OPEN_INTERVAL_AUTHORITY"
    for relative, digest in payload["inputs"].items():
        assert _sha256(ROOT / relative) == digest
    assert _sha256(ROOT / payload["data"]) == payload["data_SHA256"]
    with np.load(ROOT / payload["data"]) as data:
        radius = data["Arb_Euclidean_radius_profile"]
        assert radius.shape == (371,)
        assert radius[0] == 0.0
        assert np.all(np.isfinite(radius))

