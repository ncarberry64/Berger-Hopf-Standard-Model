from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/derive_n12_full_reset_action_jacobian.py"
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_FULL_RESET_ACTION_JACOBIAN.json"
)
DATA = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_FULL_RESET_ACTION_JACOBIAN.npz"
)


def test_n12_full_reset_action_jacobian() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["dimensions"] == {
        "columns": 196,
        "physical_tangent_nullity": 139,
        "rank": 57,
        "rows": 57,
    }
    assert payload["transported_ordered_eigenline_index"] == 24
    assert payload["paired_crosscheck"]["relative_Frobenius_residual"] < 3.0e-5
    assert payload["continuation_consequence"][
        "finite_terminal_stratum_certified_here"
    ] is False
    with np.load(DATA) as data:
        assert data["analytic_full_reset_jacobian"].shape == (57, 196)
        assert data["analytic_normal_jacobian"].shape == (57, 57)

