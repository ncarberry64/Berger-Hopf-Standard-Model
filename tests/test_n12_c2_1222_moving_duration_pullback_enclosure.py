from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "derive_n12_c2_1222_moving_duration_pullback_enclosure.py"
RESULT = ROOT / "artifacts" / "flagship_integration" / "BHSM_N12_C2_1222_MOVING_DURATION_PULLBACK_ENCLOSURE.json"
DATA = RESULT.with_suffix(".npz")


def test_moving_duration_pullback_rebuilds_byte_identically() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    first = RESULT.read_bytes()
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    assert RESULT.read_bytes() == first


def test_moving_duration_pullback_scope_and_arrays() -> None:
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert sum(payload["segment_provenance"]["block_counts"].values()) == 1222
    assert payload["claim_boundary"]["moving_duration_reset_pullback_norm"].startswith("CERTIFIED")
    assert payload["claim_boundary"]["moving_duration_reset_pullback_covector_value"].startswith("OPEN")
    assert payload["claim_boundary"]["FULL_BHSM_COMPLETE"] is False
    with np.load(DATA) as data:
        assert data["segment_Delta_lower"].shape == (1222,)
        assert data["segment_Delta_action_derivative_upper"].shape == (1222,)
        assert data["segment_duration_pullback_from_start_upper"].shape == (1222,)
        assert np.all(data["segment_Delta_lower"] > 0.0)
        assert np.all(np.isfinite(data["segment_duration_pullback_from_start_upper"]))
