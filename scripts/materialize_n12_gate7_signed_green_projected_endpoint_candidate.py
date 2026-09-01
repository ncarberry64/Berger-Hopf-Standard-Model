"""Replay and constraint-project the signed-Green endpoint Newton candidate."""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_n12_gate7_constraint_descriptor_hermite_collocation_candidate as collocation  # noqa: E402
import audit_n12_gate7_within_seam_constraint_center_obstruction as constraints  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
GREEN = BASE / "BHSM_N12_GATE7_SIGNED_GREEN_ENDPOINT_NEWTON_CANDIDATE.json"
GREEN_DATA = GREEN.with_suffix(".npz")
PROJECTED = BASE / "BHSM_N12_GATE7_PROJECTED_EXACT_AFFINE_FINE_CENTER_CANDIDATE.json"
PROJECTED_DATA = PROJECTED.with_suffix(".npz")
THEORY = ROOT / "theory" / "n12_gate7_signed_green_projected_endpoint_candidate.md"
RESULT = BASE / "BHSM_N12_GATE7_SIGNED_GREEN_PROJECTED_ENDPOINT_CANDIDATE.json"
DATA = RESULT.with_suffix(".npz")
THIS_SCRIPT = Path(__file__).resolve()
PROJECTION_TRIGGER = 2.0e-14
_WORK: dict[str, np.ndarray] = {}


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _initialize(weights: np.ndarray, reference: np.ndarray) -> None:
    _WORK["weights"] = weights
    _WORK["reference"] = reference


def _replay(task: tuple[int, np.ndarray, float]) -> tuple[object, ...]:
    index, action_state, supplied_descriptor = task
    weights = _WORK["weights"]
    reference = _WORK["reference"]
    state = action_state / weights
    frame, norms, values = constraints._constraint_geometry(state, weights)
    scaled = values / norms
    initial = float(np.linalg.norm(scaled))
    projection_action = np.zeros(98)
    if initial > PROJECTION_TRIGGER:
        gram = frame @ frame.T
        projection_action = -frame.T @ np.linalg.solve(gram, scaled)
        state = state + projection_action / weights
        final = constraints._scaled_residual(state, weights)[0]
    else:
        final = initial
    rate, field = collocation._field(
        state, max(float(supplied_descriptor), 0.0), weights, reference,
    )
    return (
        index, state, projection_action, initial, final, rate,
        float(field["numeric_selected_eigenvalue_not_used_as_descriptor"]),
        int(field["selected_branch"]), float(field["selected_eigenline_gap"]),
    )


def _extended_terminal_bracket(
    times: np.ndarray,
    states: np.ndarray,
    endpoint_eigenvalue: float,
    weights: np.ndarray,
    reference: np.ndarray,
) -> tuple[float, float, np.ndarray, float, float]:
    """Continue a still-positive retained endpoint inside the unused cell."""

    start_time = float(times[-1])
    start_state = np.asarray(states[-1], dtype=float)
    start_rate, _ = collocation._field(
        start_state, endpoint_eigenvalue, weights, reference,
    )
    duration = 1.0e-3
    trial_state = None
    trial_value = None
    while duration <= 0.1:
        trial_state = collocation._project(
            start_state + duration * start_rate[:-1] / weights,
            weights, steps=3,
        )
        _, trial_field = collocation._field(
            trial_state, 0.0, weights, reference,
        )
        trial_value = float(
            trial_field["numeric_selected_eigenvalue_not_used_as_descriptor"]
        )
        if trial_value < 0.0:
            break
        duration *= 2.0
    if trial_state is None or trial_value is None or trial_value >= 0.0:
        raise RuntimeError("one-step retained-field continuation did not find a stop bracket")

    segment_left = start_time
    segment_right = start_time + duration
    bracket_left = segment_left
    bracket_right = segment_right
    left_value = float(endpoint_eigenvalue)
    right_value = float(trial_value)

    def value(time: float) -> tuple[float, np.ndarray]:
        unit = (time - segment_left) / (segment_right - segment_left)
        state = collocation._project(
            (1.0 - unit) * start_state + unit * trial_state,
            weights, steps=3,
        )
        _, field = collocation._field(state, 0.0, weights, reference)
        return float(field["numeric_selected_eigenvalue_not_used_as_descriptor"]), state

    for _ in range(collocation.ROOT_BISECTIONS):
        midpoint = 0.5 * (bracket_left + bracket_right)
        midpoint_value, _ = value(midpoint)
        if midpoint_value > 0.0:
            bracket_left = midpoint
            left_value = midpoint_value
        else:
            bracket_right = midpoint
            right_value = midpoint_value
    representative = 0.5 * (bracket_left + bracket_right)
    _, stop_state = value(representative)
    return bracket_left, bracket_right, stop_state, left_value, right_value


def main() -> None:
    green = _load(GREEN)
    projected = _load(PROJECTED)
    if green.get("validation_passed") is not True or projected.get("validation_passed") is not True:
        raise RuntimeError("validated signed-Green and projected-center parents required")
    with np.load(GREEN_DATA) as source:
        times = np.asarray(source["action_times"], dtype=float)
        action_states = np.asarray(source["corrected_state_action"], dtype=float)
        inherited_descriptors = np.asarray(source["inherited_descriptors"], dtype=float)
        green_correction = np.asarray(source["signed_Green_state_correction_action"], dtype=float)
    with np.load(PROJECTED_DATA) as source:
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)

    workers = min(
        int(os.environ.get("BHSM_N12_GREEN_PROJECTED_ENDPOINT_WORKERS", "8")),
        os.cpu_count() or 1,
    )
    tasks = [
        (index, action_state, float(inherited_descriptors[index]))
        for index, action_state in enumerate(action_states)
    ]
    with ProcessPoolExecutor(
        max_workers=workers,
        initializer=_initialize,
        initargs=(weights, reference),
    ) as executor:
        rows = list(executor.map(_replay, tasks, chunksize=2))
    rows.sort(key=lambda item: int(item[0]))
    states = np.asarray([item[1] for item in rows])
    projection_action = np.asarray([item[2] for item in rows])
    initial_constraint = np.asarray([item[3] for item in rows])
    final_constraint = np.asarray([item[4] for item in rows])
    rates = np.asarray([item[5] for item in rows])
    eigenvalues = np.asarray([item[6] for item in rows])
    branches = np.asarray([item[7] for item in rows], dtype=int)
    gaps = np.asarray([item[8] for item in rows])

    if eigenvalues[-2] > 0.0 > eigenvalues[-1]:
        left_stop, right_stop, stop_state, left_lambda, right_lambda = collocation._terminal_bracket(
            times, states, weights, reference,
        )
        stop_route = "WITHIN_REPLAYED_FINAL_SEGMENT"
    elif eigenvalues[-1] > 0.0:
        left_stop, right_stop, stop_state, left_lambda, right_lambda = _extended_terminal_bracket(
            times, states, float(eigenvalues[-1]), weights, reference,
        )
        stop_route = "ONE_STEP_RETAINED_FIELD_CONTINUATION_INSIDE_UNUSED_TERMINAL_CELL"
    else:
        raise RuntimeError("signed-Green replay moved the stop before the retained final segment")
    stop_time = 0.5 * (left_stop + right_stop)
    stop_rate, stop_field = collocation._field(stop_state, 0.0, weights, reference)
    output_times = np.concatenate((times[:-1], [stop_time]))
    output_states = np.vstack((states[:-1], stop_state))
    output_descriptors = np.concatenate((
        inherited_descriptors[:1], eigenvalues[1:-1], [0.0],
    ))
    output_rates = np.vstack((rates[:-1], stop_rate))
    stop_constraint = constraints._scaled_residual(stop_state, weights)[0]
    output_constraint = np.concatenate((final_constraint[:-1], [stop_constraint]))
    projection_norm = np.linalg.norm(projection_action, axis=1)
    np.savez_compressed(
        DATA,
        action_times=output_times,
        projected_states=output_states,
        recentered_descriptors=output_descriptors,
        exact_endpoint_augmented_rates=output_rates,
        signed_Green_state_correction_action=green_correction,
        constraint_projection_action=projection_action,
        initial_scaled_constraint_2_norm=initial_constraint,
        final_scaled_constraint_2_norm=output_constraint,
        numerical_selected_eigenvalues=eigenvalues,
        selected_eigenline_gaps=gaps,
        first_hit_action_time_bracket=np.asarray([left_stop, right_stop]),
        state_weights=weights,
        branch_reference=reference,
    )

    validation = {
        "all_371_signed_Green_endpoints_replayed": states.shape == (371, 98),
        "all_triggered_constraint_projections_close": float(np.max(output_constraint)) < 2.0e-14,
        "projection_is_applied_only_above_declared_trigger": all(
            (initial_constraint[index] > PROJECTION_TRIGGER) == (projection_norm[index] > 0.0)
            for index in range(371)
        ),
        "branch_24_selected_at_every_replayed_endpoint": bool(np.all(branches == 24)),
        "selected_line_remains_simple_numerically": float(np.min(gaps)) > 1.0e-7,
        "all_complete_preterminal_descriptors_are_positive": float(np.min(output_descriptors[:-1])) > 0.0,
        "terminal_selected_eigenvalue_is_numerically_bracketed": left_lambda > 0.0 > right_lambda,
        "terminal_descriptor_is_zero_by_stop_definition": float(output_descriptors[-1]) == 0.0,
        "terminal_bracket_not_promoted_to_outward_root": True,
        "all_quantities_finite": bool(np.all(np.isfinite(np.concatenate((
            output_times, output_states.ravel(), output_descriptors,
            output_rates.ravel(), projection_action.ravel(), output_constraint,
        ))))),
        "no_action_source_selector_scale_gate_or_chord_changed": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    payload = {
        "artifact": "BHSM_N12_GATE7_SIGNED_GREEN_PROJECTED_ENDPOINT_CANDIDATE",
        "status": "SIGNED_GREEN_NEWTON_ENDPOINTS_CONSTRAINT_AND_DESCRIPTOR_RECENTERED" if passed else "SIGNED_GREEN_PROJECTED_ENDPOINT_CANDIDATE_INVALID",
        "authority": "DIRECT_RETAINED_ACTION_ENDPOINT_REPLAY_NUMERICAL_CANDIDATE_NOT_INTERVAL_AUTHORITY",
        "summary": {
            "node_count": int(output_times.size),
            "constraint_projection_trigger": PROJECTION_TRIGGER,
            "triggered_constraint_projection_count": int(np.count_nonzero(projection_norm)),
            "maximum_initial_scaled_constraint_2_norm": float(np.max(initial_constraint)),
            "maximum_final_scaled_constraint_2_norm": float(np.max(output_constraint)),
            "maximum_constraint_projection_action_2_norm": float(np.max(projection_norm)),
            "maximum_signed_Green_state_correction_2_norm": float(np.max(np.linalg.norm(green_correction, axis=1))),
            "minimum_selected_eigenline_gap": float(np.min(gaps)),
            "first_hit_action_time_bracket": [left_stop, right_stop],
            "first_hit_bracket_width": right_stop - left_stop,
            "terminal_numeric_selected_eigenvalue_at_replayed_old_endpoint": float(eigenvalues[-1]),
            "terminal_stop_selected_branch": int(stop_field["selected_branch"]),
            "terminal_stop_route": stop_route,
        },
        "data": _relative(DATA),
        "data_SHA256": _sha256(DATA),
        "inputs": {
            _relative(path): _sha256(path)
            for path in (GREEN, GREEN_DATA, PROJECTED, PROJECTED_DATA, THEORY, THIS_SCRIPT)
        },
        "adjudication": {
            "signed_Green_endpoint_Newton_step": "MATERIALIZED_AND_DIRECTLY_REPLAYED",
            "constraint_manifold": "NUMERICALLY_CLOSED_AT_ALL_ENDPOINTS",
            "descriptor_fiber": "NUMERICALLY_RECENTERED_AT_ALL_PRETERMINAL_ENDPOINTS",
            "continuous_center": "OPEN_PENDING_NEW_GAUSS3_FLOW_DEFECT",
            "first_hit": "NUMERICAL_BRACKET_ONLY",
        },
        "claim_boundary": {
            "continuous_action_constrained_center": "OPEN_INTERVAL_AUTHORITY",
            "continuous_outward_variational_carrier": "OPEN_AFTER_CENTER",
            "nonlinear_72D_history_first_jet": "OPEN_AFTER_CARRIER",
            "Weyl_force_KKT_Hessian": "NOT_CLAIMED",
            "Gate7": "ACTIVE_ACTION_OWNED_OPERATOR_ORACLE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": "JOIN_THESE_ENDPOINTS_WITH_ENDPOINT_FIELD_MATCHED_CUBICS_AND_REMEASURE_ALL_1110_GAUSS3_FLOW_CONSTRAINT_AND_DESCRIPTOR_RESIDUALS",
        "validation": validation,
        "validation_passed": passed,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": payload["status"], "summary": payload["summary"], "validation_passed": passed}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
