from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/derive_n12_canonical_momentum_action_jacobian.py"
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_CANONICAL_MOMENTUM_ACTION_JACOBIAN.json"
)
DATA = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_CANONICAL_MOMENTUM_ACTION_JACOBIAN.npz"
)


def test_n12_canonical_momentum_action_jacobian() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["crosscheck"]["maximum_relative_residual"] < 1.0e-8
    assert payload["continuation_consequence"][
        "complex_action_evaluations_removed_per_full_reset_Jacobian"
    ] == 196
    assert payload["continuation_consequence"][
        "finite_terminal_stratum_certified_here"
    ] is False
    with np.load(DATA) as data:
        assert data["event"].shape == (2, 98)
        assert data["child"].shape == (2, 98)
