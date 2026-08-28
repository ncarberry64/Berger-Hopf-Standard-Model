from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts/flagship_integration"
ARTIFACT = BASE / "BHSM_N12_STOP_JAX_ACTION_CALIBRATION.json"


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def test_macro_calibration_is_reproducible_predictor_only() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["grid"]["kind"] == "RETAINED_MACRO_SEAMS"
    assert payload["grid"]["nodes"] == 48
    assert payload["structural_validation_passed"] is True
    assert payload["validation"]["calibration_is_predictor_only"] is True
    assert payload["validation_passed"] is False
    data_path = ROOT / payload["data"]
    assert _sha256(data_path) == payload["data_SHA256"]
    with np.load(data_path) as data:
        assert data["gradient_correction"].shape == (48, 98)
        assert data["hessian_correction"].shape == (48, 98, 98)
        assert all(np.all(np.isfinite(data[name])) for name in data.files)
    for relative, expected in payload["inputs"].items():
        assert _sha256(ROOT / relative) == expected
    assert payload["FULL_BHSM_COMPLETE"] is False
