"""Non-proof continuation beyond loss of the fixed-descriptor chart.

The action-owned scaled field ``G_theta=Delta F_s`` is evaluated without
dividing by ``Delta``.  Euler centers generated here are only seeds for later
interval boxes.  In particular, a center sign change of the selected
Euler--Dirac eigenvalue is not a certified canonical stop.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_forward_c2_exact_fixed_s_field import (  # noqa: E402
    exact_cancelled_euler_dirac_field_action,
)
from bhsm.interface.aether_forward_c2_geometry_incidence import (  # noqa: E402
    boundary_geometry_action_covectors,
)


BASE = ROOT / "artifacts" / "flagship_integration"
SOURCE = BASE / "BHSM_N12_C2_LOG_DESCRIPTOR_DELTA_STOP_RECONNAISSANCE.npz"
RESULT = BASE / "BHSM_N12_C2_CANCELLED_EULER_DIRAC_FLOW_RECONNAISSANCE.json"
DATA = RESULT.with_suffix(".npz")
ACTION_STEP = 0.25
MAX_STEPS = 160


def _row(index: int, theta: float, state: np.ndarray, field: dict) -> dict:
    geometry = boundary_geometry_action_covectors(
        state=state, weights=WEIGHTS,
    )
    lapse = float(np.exp(float(geometry["log_lapse"])))
    radius = float(np.exp(float(geometry["log_R4"])))
    return {
        "index": index,
        "theta": theta,
        "selected_branch": int(field["selected_branch"]),
        "selected_eigenvalue": float(field["selected_eigenvalue"]),
        "selected_eigenline_gap": float(field["selected_eigenline_gap"]),
        "Delta": float(field["Delta"]),
        "cancelled_field_action_norm": float(np.linalg.norm(
            field["cancelled_field_action"]
        )),
        "boundary_lapse": lapse,
        "boundary_radius": radius,
        "proper_time_density_d_tau_d_theta": (
            lapse * float(field["selected_eigenvalue"])
        ),
    }


with np.load(SOURCE) as source:
    INITIAL = np.asarray(source["last_positive_state"], dtype=float)
    WEIGHTS = np.asarray(source["state_weights"], dtype=float)
    REFERENCE = np.asarray(source["branch_reference"], dtype=float)


def main() -> None:
    state = INITIAL.copy()
    theta = 0.0
    centers = [state.copy()]
    rows = []
    first_nonpositive = None
    for index in range(MAX_STEPS + 1):
        field = exact_cancelled_euler_dirac_field_action(
            state=state, weights=WEIGHTS, reference=REFERENCE,
        )
        row = _row(index, theta, state, field)
        rows.append(row)
        if (
            row["selected_eigenvalue"] <= 0.0
            or row["selected_eigenline_gap"] <= 0.0
            or row["boundary_lapse"] <= 0.0
            or row["boundary_radius"] <= 0.0
        ):
            first_nonpositive = row
            break
        norm = max(row["cancelled_field_action_norm"], 1.0e-300)
        step = ACTION_STEP / norm
        theta += step
        state = state + step * np.asarray(
            field["cancelled_field_action"], dtype=float
        ) / WEIGHTS
        centers.append(state.copy())
        if (index + 1) % 8 == 0:
            print(json.dumps(row), flush=True)
    np.savez_compressed(
        DATA,
        centers=np.asarray(centers),
        last_center=state,
        state=np.concatenate((state, state)),
        state_weights=WEIGHTS,
        branch_reference=REFERENCE,
    )
    payload = {
        "artifact": "BHSM_N12_C2_CANCELLED_EULER_DIRAC_FLOW_RECONNAISSANCE",
        "status": "RECONNAISSANCE_ONLY_NOT_A_CERTIFICATE",
        "method": "ACTION_ARCLENGTH_EULER_CENTERS_FOR_G_theta_EQUALS_Delta_F_s",
        "action_step": ACTION_STEP,
        "rows": rows,
        "first_nonpositive_center": first_nonpositive,
        "center_sign_change_is_certified_stop": False,
        "permitted_use": "RECENTERED_INTERVAL_BOX_SEEDS_ONLY",
        "fixed_descriptor_Delta_division_used": False,
        "full_Euler_Dirac_inverse_formed": False,
        "data": DATA.relative_to(ROOT).as_posix(),
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "centers": len(centers),
        "first_nonpositive_center": first_nonpositive,
        "final_row": rows[-1],
    }, indent=2), flush=True)


if __name__ == "__main__":
    main()
