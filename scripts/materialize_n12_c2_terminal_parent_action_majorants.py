"""Regenerate the 1.5e-10 terminal-parent action majorants for C2."""

from __future__ import annotations

import os
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
os.environ["BHSM_N12_CHECKPOINT"] = str(
    ROOT / "artifacts/flagship_integration/BHSM_N12_FINITE_TERMINAL_RESET_STRATUM_CANDIDATE.npz"
)
os.environ["BHSM_N12_ACTION_MAJORANT_RESULT"] = str(
    ROOT / "artifacts/flagship_integration/BHSM_N12_C2_TERMINAL_PARENT_ACTION_MAJORANTS_1P5E10.json"
)
os.environ["BHSM_N12_CERTIFICATE_BALL"] = "1.5e-10"

from derive_n12_action_ball_majorants import main  # noqa: E402


if __name__ == "__main__":
    main()
