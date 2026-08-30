"""Apply the second repaired rate-consistent Newton endpoint correction."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import materialize_n12_gate7_rate_consistent_newton_endpoint_candidate as candidate  # noqa: E402

BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_SECOND_RATE_CONSISTENT_NEWTON_ENDPOINT_CANDIDATE.json"


def main() -> None:
    candidate.CENTER = BASE / "BHSM_N12_GATE7_RATE_CONSISTENT_NEWTON_ENDPOINT_CANDIDATE.json"
    candidate.PREDICTOR = BASE / "BHSM_N12_GATE7_SECOND_RATE_CONSISTENT_BLOCK_NEWTON_PREDICTOR.json"
    candidate.THEORY = ROOT / "theory" / "n12_gate7_rate_consistent_newton_endpoint_candidate.md"
    candidate.RESULT = RESULT
    candidate.DATA = RESULT.with_suffix(".npz")
    candidate.THIS_SCRIPT = Path(__file__).resolve()
    candidate.main()
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    payload["artifact"] = "BHSM_N12_GATE7_SECOND_RATE_CONSISTENT_NEWTON_ENDPOINT_CANDIDATE"
    payload["status"] = (
        "SECOND_RATE_CONSISTENT_NEWTON_ENDPOINTS_PROJECTED_RECENTERED_AND_REEVALUATED"
        if payload["validation_passed"] else "SECOND_RATE_CONSISTENT_NEWTON_ENDPOINTS_INVALID"
    )
    payload["exact_next_dependency"] = "REPLAY_ALL_370_SECOND_RATE_CONSISTENT_NEWTON_MIDPOINTS"
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
