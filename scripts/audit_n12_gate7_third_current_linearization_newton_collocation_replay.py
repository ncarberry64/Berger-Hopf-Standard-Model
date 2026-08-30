"""Replay the third current-linearization Newton collocation candidate."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_n12_gate7_signed_green_hermite_collocation_replay as replay  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_THIRD_CURRENT_LINEARIZATION_NEWTON_COLLOCATION_REPLAY.json"


def main() -> None:
    replay.ENDPOINT = BASE / "BHSM_N12_GATE7_THIRD_CURRENT_LINEARIZATION_NEWTON_ENDPOINT_CANDIDATE.json"
    replay.ENDPOINT_DATA = replay.ENDPOINT.with_suffix(".npz")
    replay.PRIOR = BASE / "BHSM_N12_GATE7_CURRENT_LINEARIZATION_NEWTON_COLLOCATION_REPLAY.json"
    replay.THEORY = ROOT / "theory" / "n12_gate7_third_current_linearization_newton_collocation_replay.md"
    replay.RESULT = RESULT
    replay.DATA = RESULT.with_suffix(".npz")
    replay.THIS_SCRIPT = Path(__file__).resolve()
    replay.main()
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    payload["artifact"] = "BHSM_N12_GATE7_THIRD_CURRENT_LINEARIZATION_NEWTON_COLLOCATION_REPLAY"
    payload["exact_next_dependency"] = (
        "USE_THE_THIRD_NONLINEAR_REPLAY_TO_ADJUDICATE_SIGNED_GREEN_NEWTON_"
        "CONVERGENCE_VERSUS_DIRECT_HIGH_ORDER_MULTIPLE_SHOOTING"
    )
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


if __name__ == "__main__":
    main()
