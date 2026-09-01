"""Global, graph-preserving reconnaissance for the first C2 canonical stop.

This script integrates the denominator-free coupled system

    dY/da = G_theta(Y,s) / (w ||G_theta(Y,s)||_2),
    ds/da = Delta(Y,s) / ||G_theta(Y,s)||_2,

where ``a`` is weighted action arclength.  It starts at the last certified
sheared C2 core and uses a fixed fourth-order Runge--Kutta macro mesh.  The
output is deliberately reconnaissance: it locates a finite global proof
domain and a candidate ``s=0`` bracket, but does not turn center arithmetic
into an interval first-hit theorem.
"""

from __future__ import annotations

import hashlib
import json
import math
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
CORE = BASE / "BHSM_N12_C2_LOHNER_STEP_1222.json"
CORE_DATA = CORE.with_suffix(".npz")
RESULT = BASE / "BHSM_N12_C2_GLOBAL_CANONICAL_STOP_RECONNAISSANCE.json"
DATA = RESULT.with_suffix(".npz")
ACTION_STEP = 2.0
MAX_ACTION_LENGTH = 140.0


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _rhs(
    state: np.ndarray,
    descriptor: float,
    weights: np.ndarray,
    reference: np.ndarray,
) -> tuple[np.ndarray, float, dict[str, object]]:
    field = exact_cancelled_euler_dirac_field_action(
        state=state,
        weights=weights,
        reference=reference,
        signed_descriptor=max(float(descriptor), 0.0),
    )
    cancelled = np.asarray(field["cancelled_field_action"], dtype=float)
    norm = float(np.linalg.norm(cancelled))
    if not norm > 0.0:
        raise ArithmeticError("cancelled action field vanished before a stop")
    return cancelled / weights / norm, float(field["Delta"]) / norm, field


def _row(
    index: int,
    action_length: float,
    state: np.ndarray,
    descriptor: float,
    weights: np.ndarray,
    field: dict[str, object],
) -> dict[str, object]:
    geometry = boundary_geometry_action_covectors(state=state, weights=weights)
    numeric = float(field["numeric_selected_eigenvalue_not_used_as_descriptor"])
    return {
        "index": index,
        "action_length": action_length,
        "signed_descriptor": descriptor,
        "numeric_selected_eigenvalue_not_used_as_descriptor": numeric,
        "numeric_descriptor_graph_residual": numeric - descriptor,
        "Delta": float(field["Delta"]),
        "cancelled_field_action_norm": float(np.linalg.norm(
            field["cancelled_field_action"]
        )),
        "selected_branch": int(field["selected_branch"]),
        "selected_eigenline_gap": float(field["selected_eigenline_gap"]),
        "boundary_lapse": float(np.exp(float(geometry["log_lapse"]))),
        "boundary_radius": float(np.exp(float(geometry["log_R4"]))),
    }


def _rk4_trial(
    state: np.ndarray,
    descriptor: float,
    step: float,
    weights: np.ndarray,
    reference: np.ndarray,
) -> tuple[np.ndarray, float]:
    k1y, k1s, _ = _rhs(state, descriptor, weights, reference)
    k2y, k2s, _ = _rhs(
        state + 0.5 * step * k1y,
        descriptor + 0.5 * step * k1s,
        weights,
        reference,
    )
    k3y, k3s, _ = _rhs(
        state + 0.5 * step * k2y,
        descriptor + 0.5 * step * k2s,
        weights,
        reference,
    )
    k4y, k4s, _ = _rhs(
        state + step * k3y,
        descriptor + step * k3s,
        weights,
        reference,
    )
    return (
        state + step * (k1y + 2.0 * k2y + 2.0 * k3y + k4y) / 6.0,
        descriptor + step * (k1s + 2.0 * k2s + 2.0 * k3s + k4s) / 6.0,
    )


def build_payload() -> dict[str, object]:
    core = json.loads(CORE.read_text(encoding="utf-8"))
    if core.get("validation_passed") is not True:
        raise RuntimeError("validated sheared C2 core required")
    with np.load(CORE_DATA) as source:
        state = np.asarray(source["endpoint_predictor_center"], dtype=float)
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)
    descriptor = float(core["segment"]["signed_descriptor_end"])
    action_length = 0.0
    states = [state.copy()]
    descriptors = [descriptor]
    rows: list[dict[str, object]] = []
    bracket: dict[str, object] | None = None
    maximum = {"index": 0, "action_length": 0.0, "signed_descriptor": descriptor}

    while action_length <= MAX_ACTION_LENGTH:
        _, _, field = _rhs(state, descriptor, weights, reference)
        row = _row(
            len(rows), action_length, state, descriptor, weights, field
        )
        rows.append(row)
        if descriptor > float(maximum["signed_descriptor"]):
            maximum = {
                "index": len(rows) - 1,
                "action_length": action_length,
                "signed_descriptor": descriptor,
            }
        trial_state, trial_descriptor = _rk4_trial(
            state, descriptor, ACTION_STEP, weights, reference
        )
        if trial_descriptor <= 0.0:
            bracket = {
                "left_index": len(rows) - 1,
                "action_length_left": action_length,
                "signed_descriptor_left": descriptor,
                "Delta_left": float(field["Delta"]),
                "action_length_trial": action_length + ACTION_STEP,
                "signed_descriptor_trial": trial_descriptor,
            }
            break
        state = trial_state
        descriptor = trial_descriptor
        action_length += ACTION_STEP
        states.append(state.copy())
        descriptors.append(descriptor)
        if len(rows) % 4 == 0:
            print(json.dumps(row), flush=True)

    if bracket is None:
        raise ArithmeticError("no candidate canonical-stop bracket on global mesh")
    array_states = np.asarray(states)
    action_states = (array_states - array_states[0]) * weights
    singular_values = np.linalg.svd(action_states, compute_uv=False)
    graph_residual = max(abs(float(row["numeric_descriptor_graph_residual"])) for row in rows)
    np.savez_compressed(
        DATA,
        centers=array_states,
        signed_descriptors=np.asarray(descriptors),
        action_lengths=ACTION_STEP * np.arange(len(states)),
        state_weights=weights,
        branch_reference=reference,
        left_positive_state=states[-1],
        left_positive_descriptor=np.asarray(descriptors[-1]),
        first_trial_state=trial_state,
        first_trial_descriptor=np.asarray(trial_descriptor),
    )
    return {
        "artifact": "BHSM_N12_C2_GLOBAL_CANONICAL_STOP_RECONNAISSANCE",
        "status": "FINITE_GLOBAL_s_ZERO_BRACKET_RECONNAISSANCE_ONLY",
        "method": (
            "FOURTH_ORDER_RUNGE_KUTTA_ON_DENOMINATOR_FREE_COUPLED_"
            "ACTION_ARCLENGTH_SYSTEM"
        ),
        "action_step": ACTION_STEP,
        "maximum": maximum,
        "candidate_first_stop_bracket": bracket,
        "domain_trends": {
            "minimum_selected_eigenline_gap": min(
                float(row["selected_eigenline_gap"]) for row in rows
            ),
            "minimum_boundary_lapse": min(
                float(row["boundary_lapse"]) for row in rows
            ),
            "minimum_boundary_radius": min(
                float(row["boundary_radius"]) for row in rows
            ),
            "minimum_cancelled_field_action_norm": min(
                float(row["cancelled_field_action_norm"]) for row in rows
            ),
            "maximum_absolute_numeric_graph_residual": graph_residual,
        },
        "global_geometry": {
            "weighted_action_length_left": float(
                ACTION_STEP * (len(states) - 1)
            ),
            "weighted_endpoint_displacement": float(
                np.linalg.norm(action_states[-1])
            ),
            "principal_displacement_energy_fraction": float(
                singular_values[0] ** 2 / np.sum(singular_values**2)
            ),
        },
        "rows": rows,
        "candidate_stop_is_certified": False,
        "reason_not_yet_certified": (
            "CENTER_RK4_BRACKET_REQUIRES_ONE_FINITE_MOVING_EIGENLINE_CONE_OR_"
            "MULTIPLE_SHOOTING_SHADOWING_THEOREM"
        ),
        "binary64_eigenvalue_used_only_as_graph_residual_diagnostic": True,
        "Delta_zero_not_used_as_a_stop": True,
        "full_Euler_Dirac_inverse_formed": False,
        "inputs": {
            CORE.relative_to(ROOT).as_posix(): _sha256(CORE),
            CORE_DATA.relative_to(ROOT).as_posix(): _sha256(CORE_DATA),
        },
        "data": DATA.relative_to(ROOT).as_posix(),
        "data_SHA256": _sha256(DATA),
        "validation_passed": False,
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "maximum": payload["maximum"],
        "candidate_first_stop_bracket": payload["candidate_first_stop_bracket"],
        "domain_trends": payload["domain_trends"],
        "global_geometry": payload["global_geometry"],
    }, indent=2), flush=True)


if __name__ == "__main__":
    main()
