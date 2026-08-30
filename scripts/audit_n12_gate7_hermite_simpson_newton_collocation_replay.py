"""Replay the Hermite--Simpson block Newton endpoint candidate."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_n12_gate7_signed_green_hermite_collocation_replay as replay  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_HERMITE_SIMPSON_NEWTON_COLLOCATION_REPLAY.json"


def main() -> None:
    replay.ENDPOINT = BASE / "BHSM_N12_GATE7_HERMITE_SIMPSON_NEWTON_ENDPOINT_CANDIDATE.json"
    replay.ENDPOINT_DATA = replay.ENDPOINT.with_suffix(".npz")
    replay.PRIOR = BASE / "BHSM_N12_GATE7_CURRENT_LINEARIZATION_NEWTON_COLLOCATION_REPLAY.json"
    replay.THEORY = ROOT / "theory" / "n12_gate7_hermite_simpson_newton_collocation_replay.md"
    replay.RESULT = RESULT
    replay.DATA = RESULT.with_suffix(".npz")
    replay.THIS_SCRIPT = Path(__file__).resolve()
    replay.main()
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    payload["artifact"] = "BHSM_N12_GATE7_HERMITE_SIMPSON_NEWTON_COLLOCATION_REPLAY"
    payload["exact_next_dependency"] = (
        "IF_THE_DIRECT_BLOCK_NEWTON_STEP_REDUCES_THE_NONLINEAR_DEFECT,_REBUILD_"
        "THE_BLOCK_OPERATOR_AND_ITERATE;_OTHERWISE_LOCALIZE_THE_BLOCK_"
        "LINEARIZATION_OR_CONSTRAINT_PROJECTION_FAILURE"
    )
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


if __name__ == "__main__":
    main()
