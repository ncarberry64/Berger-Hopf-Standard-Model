from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "derive_n12_c2_1222_transposed_duration_action_coverage.py"
RESULT = ROOT / "artifacts" / "flagship_integration" / (
    "BHSM_N12_C2_1222_TRANSPOSED_DURATION_ACTION_COVERAGE.json"
)


def test_1222_transposed_duration_action_coverage() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["coverage"]["segments"] == 1222
    assert payload["adjudication"][
        "all_1222_interval_transposed_duration_actions"
    ] == "CERTIFIED"
    assert payload["adjudication"][
        "actual_graded_heat_minus_zeta_coefficient_cotangent"
    ] == "OPEN"
    with np.load(ROOT / payload["data"]) as data:
        assert data["segment_duration_action_dual_ball_center"].shape == (1222, 98)
        assert data["segment_duration_action_dual_ball_radius_upper"].shape == (1222,)
        assert np.all(data["segment_duration_action_dual_ball_radius_upper"] > 0.0)
