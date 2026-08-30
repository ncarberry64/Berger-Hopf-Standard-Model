"""Rebuild the 48 constraint tangents on the second Newton center."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import materialize_n12_gate7_signed_green_current_center_macro_tangent as tangent  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_SECOND_CURRENT_CENTER_MACRO_TANGENT.json"


def main() -> None:
    tangent.CENTER = BASE / "BHSM_N12_GATE7_CURRENT_LINEARIZATION_NEWTON_ENDPOINT_CANDIDATE.json"
    tangent.CENTER_DATA = tangent.CENTER.with_suffix(".npz")
    tangent.PRIOR = BASE / "BHSM_N12_GATE7_SIGNED_GREEN_CURRENT_CENTER_MACRO_TANGENT.json"
    tangent.THEORY = ROOT / "theory" / "n12_gate7_second_current_center_macro_tangent.md"
    tangent.RESULT = RESULT
    tangent.DATA = RESULT.with_suffix(".npz")
    tangent.THIS_SCRIPT = Path(__file__).resolve()
    tangent.main()
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    payload["artifact"] = "BHSM_N12_GATE7_SECOND_CURRENT_CENTER_MACRO_TANGENT"
    payload["status"] = "SECOND_CURRENT_CENTER_48_SEAM_CONSTRAINT_TANGENTS_MATERIALIZED"
    payload["adjudication"] = {
        "first_current_center_macro_tangents": "SUPERSEDED_FOR_THIRD_NEWTON_PROJECTION",
        "second_current_center_constraint_projection": "MATERIALIZED_AT_ALL_RETAINED_SEAMS",
    }
    payload["exact_next_dependency"] = (
        "APPLY_A_THIRD_SIGNED_GREEN_NEWTON_STEP_WITH_THE_SECOND_CURRENT_"
        "CENTER_GRAPH_JACOBIAN_AND_THESE_TANGENTS"
    )
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


if __name__ == "__main__":
    main()
