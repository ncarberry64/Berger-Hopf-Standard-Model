"""Materialize the terminal event-side eigenline on the root solution ball."""

from __future__ import annotations

import os
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
BASE = Path("artifacts/flagship_integration")
os.environ["BHSM_N12_CHECKPOINT"] = str(
    BASE / "BHSM_N12_FINITE_TERMINAL_CERTIFICATE_CHECKPOINT.npz"
)
os.environ["BHSM_N12_THIRD_VARIATION_RESULT"] = str(
    BASE / "BHSM_N12_FINITE_TERMINAL_RESET_STRATUM_CANDIDATE.npz"
)
os.environ["BHSM_N12_ACTION_MAJORANT_RESULT"] = str(
    BASE / "BHSM_N12_FINITE_TERMINAL_SOLUTION_BALL_ACTION_MAJORANTS.json"
)
os.environ["BHSM_N12_ORDERED_MIXED_MAJORANT_RESULT"] = str(
    BASE / "BHSM_N12_FINITE_TERMINAL_EVENT_EIGENLINE_MIXED_MAJORANTS.json"
)
os.environ["BHSM_N12_ORDERED_EIGENLINE_BALL_RESULT"] = str(
    BASE / "BHSM_N12_FINITE_TERMINAL_EVENT_EIGENLINE_SOLUTION_BALL.json"
)
os.environ["BHSM_N12_EIGENLINE_SIDE"] = "event"
sys.path.insert(0, str(ROOT / "scripts"))

from certify_n12_ordered_event_eigenline_ball import main  # noqa: E402


if __name__ == "__main__":
    main()
