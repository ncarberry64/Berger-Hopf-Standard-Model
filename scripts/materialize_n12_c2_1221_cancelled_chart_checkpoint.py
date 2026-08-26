"""Materialize an ambient child-local checkpoint at the tracked 1221 edge.

The duplicated joint state and identity direction frame are proof machinery
for local retained-action majorants.  They are not a new event state, reset,
or physical selector.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
SOURCE = BASE / "BHSM_N12_C2_LOHNER_BORDERED_MATRIX_1221.npz"
RESULT = BASE / "BHSM_N12_C2_1221_CANCELLED_CHART_CHECKPOINT.npz"
METADATA = RESULT.with_suffix(".json")


def main() -> None:
    with np.load(SOURCE) as source:
        child = np.asarray(source["center_state"], dtype=float)
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)
    joint = np.concatenate((child, child))
    frame = np.eye(joint.size)
    np.savez_compressed(
        RESULT,
        state=joint,
        paired_jacobian=frame,
        branch_reference=reference,
        n6_ordered_branch_index=np.asarray(24),
        state_weights=weights,
        child_state=child,
    )
    payload = {
        "artifact": "BHSM_N12_C2_1221_CANCELLED_CHART_CHECKPOINT",
        "status": "AMBIENT_CHILD_LOCAL_MAJORANT_CHECKPOINT",
        "source": SOURCE.relative_to(ROOT).as_posix(),
        "joint_state_semantics": "DUPLICATED_CHILD_CENTER_FOR_LOCAL_ACTION_BOUNDS_ONLY",
        "direction_frame": "FULL_196_DIMENSIONAL_AMBIENT_IDENTITY",
        "event_state_claimed": False,
        "physical_reset_member_selected": False,
        "FULL_BHSM_COMPLETE": False,
    }
    METADATA.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
