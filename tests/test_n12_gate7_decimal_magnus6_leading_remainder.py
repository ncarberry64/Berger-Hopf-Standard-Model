from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_GATE7_DECIMAL_MAGNUS6_LEADING_REMAINDER_AUDIT.json"
)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def test_exact_omega5_is_kept_separate_from_binary64_tail_authority() -> None:
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["claim_boundary"]["affine_Omega5_identity"] == "ESTABLISHED"
    assert payload["claim_boundary"]["binary64_Magnus6_tail"].startswith("REJECTED")
    assert payload["claim_boundary"][
        "analytic_Magnus4_higher_commutator_remainder"
    ].startswith("OPEN")
    assert payload["summary"]["maximum_Magnus6_minus_Magnus4_profile_shift"] < 4e-19
    assert not 32.0 < payload["summary"]["observed_refinement_ratio"] < 128.0
    assert payload["FULL_BHSM_COMPLETE"] is False
    for relative, digest in payload["inputs"].items():
        assert _sha256(ROOT / relative) == digest
    assert _sha256(ROOT / payload["data"]) == payload["data_SHA256"]
    with np.load(ROOT / payload["data"]) as data:
        assert data["Magnus6_minus_Magnus4_2_norm"].shape == (371,)
        assert np.all(np.isfinite(data["Magnus6_PROP16_to_32_2_norm"]))
