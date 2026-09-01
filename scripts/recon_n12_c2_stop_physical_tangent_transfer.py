"""Reconnoiter the constraint-reduced reset-to-stop tangent transfer.

The N12 state has 98 raw coordinates.  Variation of the 24 retained lapse/
shift multipliers and the zero Legendre-energy condition cut out the
73-dimensional physical child tangent.  This script constructs that tangent
directly from the full retained action jet at every high-order stop-center
node and transports the terminal ``s=0`` covector backwards through it.

This is a center/Magnus reconnaissance calculation.  It does not claim an
interval history tube or a validated first-hit theorem.
"""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
import argparse
import json
import os
from pathlib import Path
import sys

import numpy as np
from scipy.linalg import null_space
from scipy.sparse.linalg import expm_multiply


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import audit_n12_c2_stop_boundary_cluster_probe as cluster  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
CENTER_DATA = Path(os.environ.get(
    "BHSM_N12_STOP_CENTER_DATA",
    str(BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_CENTER_RECONNAISSANCE.npz"),
))
JACOBIAN_DATA = Path(os.environ.get(
    "BHSM_N12_STOP_JACOBIAN_DATA",
    str(BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_GRAPH_JACOBIAN_RECONNAISSANCE.npz"),
))
RESULT = Path(os.environ.get(
    "BHSM_N12_STOP_TANGENT_RESULT",
    str(BASE / "BHSM_N12_C2_STOP_PHYSICAL_TANGENT_TRANSFER_RECONNAISSANCE.json"),
))
DATA_RESULT = RESULT.with_suffix(".npz")
QDIM = 37
MDIM = 24
STATE_DIMENSION = 98
PHYSICAL_DIMENSION = 73


def _arrays() -> tuple[np.ndarray, ...]:
    with np.load(CENTER_DATA) as center:
        states = np.asarray(center["centers"], dtype=float)
        action_lengths = np.asarray(center["action_lengths"], dtype=float)
        weights = np.asarray(center["state_weights"], dtype=float)
        action_rates = np.asarray(center["action_rates"], dtype=float)
    with np.load(JACOBIAN_DATA) as jacobian:
        matrices = np.asarray(jacobian["graph_Jacobian_action"], dtype=float)
        descriptor_gradients = np.asarray(
            jacobian["descriptor_gradient_action"], dtype=float,
        )
        jacobian_times = (
            np.asarray(jacobian["action_lengths"], dtype=float)
            if "action_lengths" in jacobian.files
            else action_lengths
        )
    if matrices.shape[0] != jacobian_times.size:
        raise RuntimeError("Jacobian node count does not match its time grid")
    if not np.array_equal(jacobian_times, action_lengths):
        sampled_matrices = []
        sampled_gradients = []
        for time in action_lengths:
            index = min(
                max(int(np.searchsorted(jacobian_times, time, side="right") - 1), 0),
                jacobian_times.size - 2,
            )
            left, right = jacobian_times[index:index + 2]
            fraction = min(max(float((time - left) / (right - left)), 0.0), 1.0)
            sampled_matrices.append(
                (1.0 - fraction) * matrices[index] + fraction * matrices[index + 1]
            )
            sampled_gradients.append(
                (1.0 - fraction) * descriptor_gradients[index]
                + fraction * descriptor_gradients[index + 1]
            )
        matrices = np.asarray(sampled_matrices)
        descriptor_gradients = np.asarray(sampled_gradients)
    return (
        states, action_lengths, weights, action_rates, matrices,
        descriptor_gradients,
    )


def _constraint_geometry(task: tuple[int, np.ndarray, np.ndarray]) -> tuple:
    index, state, weights = task
    jet = cluster.local.exact_full_action_jet_at_state(
        12,
        state[:QDIM], state[QDIM:2 * QDIM], state[2 * QDIM:],
        points=cluster.local.POINTS,
    )
    gradient = np.asarray(jet.gradient, dtype=float)
    hessian = np.asarray(jet.hessian, dtype=float)
    velocity = state[QDIM:2 * QDIM]

    # The 24 multiplier variations are the Euler--Dirac constraints.
    raw_rows = [hessian[2 * QDIM:, :]]

    # E=v.L_v-L.  Its exact raw-coordinate differential is
    # (H_vq^T v-L_q, H_vv^T v, H_vm^T v-L_m).
    energy_row = np.concatenate((
        hessian[QDIM:2 * QDIM, :QDIM].T @ velocity - gradient[:QDIM],
        hessian[QDIM:2 * QDIM, QDIM:2 * QDIM].T @ velocity,
        hessian[QDIM:2 * QDIM, 2 * QDIM:].T @ velocity
        - gradient[2 * QDIM:],
    ))
    raw_constraint = np.vstack((raw_rows[0], energy_row))
    action_constraint = raw_constraint / weights[None, :]
    constraint_values = np.concatenate((
        gradient[2 * QDIM:],
        np.asarray([velocity @ gradient[QDIM:2 * QDIM] - float(jet.value)]),
    ))
    row_norms = np.linalg.norm(action_constraint, axis=1)
    if np.any(row_norms == 0.0):
        raise RuntimeError("zero action constraint row")
    normalized = action_constraint / row_norms[:, None]
    singular_values = np.linalg.svd(normalized, compute_uv=False)
    tangent = null_space(normalized, rcond=1.0e-11)
    return (
        index, normalized, tangent, constraint_values, row_norms,
        singular_values,
    )


def build_payload(*, workers: int) -> dict[str, object]:
    (
        states, action_lengths, weights, action_rates, jacobians,
        descriptor_gradients,
    ) = _arrays()
    if states.shape != (48, STATE_DIMENSION):
        raise RuntimeError("expected the retained 48-node N12 stop center")
    tasks = [(i, states[i], weights) for i in range(states.shape[0])]
    with ProcessPoolExecutor(max_workers=workers) as executor:
        geometry = list(executor.map(_constraint_geometry, tasks))
    geometry.sort(key=lambda item: item[0])
    constraints = np.asarray([item[1] for item in geometry])
    tangents = np.asarray([item[2] for item in geometry])
    constraint_values = np.asarray([item[3] for item in geometry])
    row_norms = np.asarray([item[4] for item in geometry])
    singular_values = np.asarray([item[5] for item in geometry])
    if tangents.shape != (48, STATE_DIMENSION, PHYSICAL_DIMENSION):
        raise RuntimeError(
            f"physical tangent shape changed: received {tangents.shape}"
        )

    flow_tangency = np.asarray([
        np.linalg.norm(constraints[i] @ action_rates[i])
        for i in range(states.shape[0])
    ])

    # Second-order (trapezoidal Magnus) propagation on each retained macro
    # seam, followed by the exact endpoint quotient frames.
    step_maps = []
    tangent_leakage = []
    for index, step in enumerate(np.diff(action_lengths)):
        generator = 0.5 * (jacobians[index] + jacobians[index + 1])
        evolved = expm_multiply(float(step) * generator, tangents[index])
        target = tangents[index + 1]
        step_maps.append(target.T @ evolved)
        normal = np.eye(STATE_DIMENSION) - target @ target.T
        tangent_leakage.append(float(np.linalg.norm(normal @ evolved, 2)))
    step_maps = np.asarray(step_maps)

    terminal_tangent = tangents[-1]
    terminal_descriptor_raw = descriptor_gradients[-1]
    terminal_descriptor = terminal_tangent.T @ terminal_descriptor_raw
    terminal_flow = terminal_tangent.T @ action_rates[-1]
    terminal_crossing = float(terminal_descriptor @ terminal_flow)
    direct_crossing = float(terminal_descriptor_raw @ action_rates[-1])

    pulled = terminal_descriptor.copy()
    pullback_norms = [float(np.linalg.norm(pulled))]
    for step_map in reversed(step_maps):
        pulled = step_map.T @ pulled
        pullback_norms.append(float(np.linalg.norm(pulled)))
    pullback_norms = np.asarray(list(reversed(pullback_norms)))
    initial_pullback_norm = float(np.linalg.norm(pulled))

    # Also assemble the quotient fundamental matrix for its singular-value
    # profile.  This is diagnostic only and is intentionally not inverted.
    fundamental = np.eye(PHYSICAL_DIMENSION)
    for step_map in step_maps:
        fundamental = step_map @ fundamental
    fundamental_singular = np.linalg.svd(fundamental, compute_uv=False)

    initial_certified_normal_radius = 4.3223310537263596e-15
    inherited_endpoint_tube_radius = 9.503197056856919e-11
    normal_s_uncertainty = initial_certified_normal_radius * initial_pullback_norm
    normal_time_uncertainty = normal_s_uncertainty / abs(terminal_crossing)
    inherited_normal_time_scale = (
        inherited_endpoint_tube_radius * initial_pullback_norm
        / abs(terminal_crossing)
    )

    np.savez_compressed(
        DATA_RESULT,
        normalized_constraint_action=constraints,
        physical_tangent_action=tangents,
        constraint_values=constraint_values,
        constraint_row_norms=row_norms,
        constraint_singular_values=singular_values,
        physical_step_maps=step_maps,
        physical_fundamental=fundamental,
        terminal_descriptor_physical=terminal_descriptor,
        initial_terminal_descriptor_pullback_physical=pulled,
        pullback_norm_profile=pullback_norms,
        tangent_leakage_operator=tangent_leakage,
    )
    summary = {
        "constraint_count": int(constraints.shape[1]),
        "physical_tangent_dimension": int(tangents.shape[2]),
        "minimum_normalized_constraint_singular_value": float(
            np.min(singular_values[:, -1])
        ),
        "maximum_action_constraint_value_2_norm": float(
            np.max(np.linalg.norm(constraint_values, axis=1))
        ),
        "maximum_normalized_constraint_flow_residual": float(
            np.max(flow_tangency)
        ),
        "maximum_Magnus_step_tangent_leakage_operator_norm": float(
            np.max(tangent_leakage)
        ),
        "terminal_descriptor_crossing_on_physical_tangent": terminal_crossing,
        "terminal_descriptor_crossing_direct": direct_crossing,
        "terminal_crossing_projection_residual": abs(
            terminal_crossing - direct_crossing
        ),
        "initial_terminal_normal_pullback_2_norm": initial_pullback_norm,
        "maximum_terminal_normal_pullback_profile_2_norm": float(
            np.max(pullback_norms)
        ),
        "physical_fundamental_operator_2_norm": float(fundamental_singular[0]),
        "physical_fundamental_minimum_singular_value": float(
            fundamental_singular[-1]
        ),
        "physical_fundamental_condition_number": float(
            fundamental_singular[0] / fundamental_singular[-1]
        ),
        "certified_initial_normal_radius": initial_certified_normal_radius,
        "certified_initial_radius_terminal_s_uncertainty_linearized": float(
            normal_s_uncertainty
        ),
        "certified_initial_radius_terminal_time_uncertainty_linearized": float(
            normal_time_uncertainty
        ),
        "inherited_1221_radius_terminal_time_scale_linearized": float(
            inherited_normal_time_scale
        ),
    }
    return {
        "artifact": "BHSM_N12_C2_STOP_PHYSICAL_TANGENT_TRANSFER_RECONNAISSANCE",
        "authority": "CENTER_AND_SECOND_ORDER_MAGNUS_ONLY_NOT_INTERVAL_HISTORY_AUTHORITY",
        "construction": {
            "Euler_Dirac_multiplier_constraints": MDIM,
            "zero_Legendre_energy_constraints": 1,
            "ambient_action_coordinate_dimension": STATE_DIMENSION,
            "physical_child_tangent_dimension": PHYSICAL_DIMENSION,
            "inverse_free": True,
            "terminal_normal": "D_s_RESTRICTED_TO_THE_ACTION_CONSTRAINT_TANGENT",
            "transport": "TRAPEZOIDAL_MAGNUS_ON_THE_47_RETAINED_MACRO_SEAMS",
        },
        "summary": summary,
        "data": DATA_RESULT.relative_to(ROOT).as_posix(),
        "validation_passed": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=min(12, os.cpu_count() or 1))
    args = parser.parse_args()
    payload = build_payload(workers=args.workers)
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
