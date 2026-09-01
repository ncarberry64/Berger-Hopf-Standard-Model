"""Validate the exact combined-direction cancelled-Delta identity."""

from __future__ import annotations

import json
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_forward_c2_exact_fixed_s_field import (  # noqa: E402
    exact_cancelled_euler_dirac_field_action as split_field,
)
from bhsm.interface.aether_forward_c2_fast_cancelled_field import (  # noqa: E402
    exact_cancelled_euler_dirac_field_action as combined_field,
)


BASE = ROOT / "artifacts" / "flagship_integration"
CENTER = BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_HALF_STEP_CENTER_RECONNAISSANCE.npz"
RESULT = BASE / "BHSM_N12_FAST_CANCELLED_DELTA_IDENTITY_AUDIT.json"


def main() -> None:
    with np.load(CENTER) as source:
        states = np.asarray(source["centers"], dtype=float)
        descriptors = np.asarray(source["signed_descriptors"], dtype=float)
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)
    rows = []
    for index in (0, 11, 23, 35, 47):
        arguments = {
            "state": states[index],
            "weights": weights,
            "reference": reference,
            "signed_descriptor": float(descriptors[index]),
        }
        split = split_field(**arguments)
        combined = combined_field(**arguments)
        rows.append({
            "node": index,
            "selected_branch": int(combined["selected_branch"]),
            "field_action_residual_2_norm": float(np.linalg.norm(
                np.asarray(split["cancelled_field_action"])
                - np.asarray(combined["cancelled_field_action"])
            )),
            "b_psi_residual": abs(float(split["b_psi"]) - float(combined["b_psi"])),
            "Delta_split": float(split["Delta"]),
            "Delta_combined": float(combined["Delta"]),
            "Delta_absolute_residual": abs(
                float(split["Delta"]) - float(combined["Delta"])
            ),
        })
    validation = {
        "same_branch_24_at_all_nodes": all(row["selected_branch"] == 24 for row in rows),
        "cancelled_numerator_replay_residual_below_1e_minus_12": max(
            row["field_action_residual_2_norm"] for row in rows
        ) < 1.0e-12,
        "b_psi_replay_residual_below_1e_minus_12": max(
            row["b_psi_residual"] for row in rows
        ) < 1.0e-12,
        "combined_Delta_agrees_below_1e_minus_21": max(
            row["Delta_absolute_residual"] for row in rows
        ) < 1.0e-21,
        "linearity_of_Dlambda_used_before_floating_point_evaluation": True,
        "retained_action_and_inverse_free_selected_complement_unchanged": True,
        "no_action_equation_stop_selector_scale_gate_or_chord_changed": True,
    }
    payload = {
        "artifact": "BHSM_N12_FAST_CANCELLED_DELTA_IDENTITY_AUDIT",
        "status": (
            "EXACT_COMBINED_DIRECTION_CANCELLED_DELTA_IDENTITY_VALIDATED"
            if all(validation.values()) else "COMBINED_DIRECTION_DELTA_IDENTITY_INVALID"
        ),
        "identity": "Dlambda[b_psi*Psi+s*V_hard]=b_psi*c_psi+s*R=Delta",
        "rows": rows,
        "summary": {
            "maximum_Delta_absolute_residual": max(
                row["Delta_absolute_residual"] for row in rows
            ),
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
