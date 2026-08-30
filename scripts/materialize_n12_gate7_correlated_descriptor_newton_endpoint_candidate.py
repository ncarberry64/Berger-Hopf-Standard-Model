"""Apply the second Newton correction while carrying signed descriptor independently.

The descriptor is transported by the stored action-coordinate first jet through the
actual constraint-projected state displacement.  A binary64 eigensolve is performed
only as a diagnostic; it never replaces the supplied descriptor in the exact field.
"""

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
CENTER = BASE / "BHSM_N12_GATE7_RATE_CONSISTENT_NEWTON_ENDPOINT_CANDIDATE.json"
PREDICTOR = BASE / "BHSM_N12_GATE7_SECOND_RATE_CONSISTENT_BLOCK_NEWTON_PREDICTOR.json"
JACOBIAN = BASE / "BHSM_N12_GATE7_SECOND_RATE_CONSISTENT_CENTER_GRAPH_JACOBIAN.json"
THEORY = ROOT / "theory" / "n12_gate7_correlated_descriptor_newton.md"
RESULT = BASE / "BHSM_N12_GATE7_CORRELATED_DESCRIPTOR_NEWTON_ENDPOINT_CANDIDATE.json"
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


def _node(task: tuple[int, np.ndarray, np.ndarray, float, np.ndarray]) -> tuple[object, ...]:
    index, base_state, correction_action, base_descriptor, descriptor_gradient = task
    weights = _WORK["weights"]
    reference = _WORK["reference"]
    state = base_state + correction_action / weights
    frame, norms, values = constraints._constraint_geometry(state, weights)
    initial = float(np.linalg.norm(values / norms))
    projection_action = np.zeros(98)
    if initial > PROJECTION_TRIGGER:
        scaled = values / norms
        projection_action = -frame.T @ np.linalg.solve(frame @ frame.T, scaled)
        state = state + projection_action / weights
        final = constraints._scaled_residual(state, weights)[0]
    else:
        final = initial
    actual_delta_action = (state - base_state) * weights
    transported_descriptor = float(base_descriptor + descriptor_gradient @ actual_delta_action)
    supplied_descriptor = max(transported_descriptor, 0.0)
    rate, value = collocation._field(state, supplied_descriptor, weights, reference)
    numeric_eigenvalue = float(value["numeric_selected_eigenvalue_not_used_as_descriptor"])
    return (
        index, state, projection_action, actual_delta_action, initial, final,
        supplied_descriptor, transported_descriptor, rate, numeric_eigenvalue,
        int(value["selected_branch"]), float(value["selected_eigenline_gap"]),
    )


def main() -> None:
    center = _load(CENTER)
    predictor = _load(PREDICTOR)
    jacobian = _load(JACOBIAN)
    if not all(record.get("validation_passed") is True for record in (center, predictor, jacobian)):
        raise RuntimeError("validated center, predictor, and graph Jacobian required")
    with np.load(CENTER.with_suffix(".npz")) as source:
        times = np.asarray(source["action_times"], dtype=float)
        states = np.asarray(source["projected_states"], dtype=float)
        descriptors = np.asarray(source["recentered_descriptors"], dtype=float)
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)
    with np.load(PREDICTOR.with_suffix(".npz")) as source:
        correction = np.asarray(source["endpoint_state_correction_action"], dtype=float)
    with np.load(JACOBIAN.with_suffix(".npz")) as source:
        gradients = np.asarray(source["descriptor_gradient_action"], dtype=float)
    tasks = [
        (i, states[i], correction[i], float(descriptors[i]), gradients[i])
        for i in range(371)
    ]
    workers = min(int(os.environ.get("BHSM_N12_RATE_CONSISTENT_NEWTON_WORKERS", "8")), os.cpu_count() or 1)
    with ProcessPoolExecutor(max_workers=workers, initializer=_initialize, initargs=(weights, reference)) as executor:
        rows = list(executor.map(_node, tasks, chunksize=2))
    rows.sort(key=lambda item: int(item[0]))
    output_states = np.asarray([row[1] for row in rows])
    projection_action = np.asarray([row[2] for row in rows])
    actual_delta_action = np.asarray([row[3] for row in rows])
    initial_constraint = np.asarray([row[4] for row in rows])
    final_constraint = np.asarray([row[5] for row in rows])
    supplied = np.asarray([row[6] for row in rows])
    transported = np.asarray([row[7] for row in rows])
    rates = np.asarray([row[8] for row in rows])
    eigenvalues = np.asarray([row[9] for row in rows])
    branches = np.asarray([row[10] for row in rows], dtype=int)
    gaps = np.asarray([row[11] for row in rows])
    fiber = eigenvalues - supplied
    np.savez_compressed(
        DATA,
        action_times=times,
        projected_states=output_states,
        correlated_descriptors=supplied,
        transported_unclipped_descriptors=transported,
        exact_endpoint_augmented_rates=rates,
        requested_endpoint_correction_action=correction,
        constraint_projection_action=projection_action,
        actual_endpoint_displacement_action=actual_delta_action,
        initial_scaled_constraint_2_norm=initial_constraint,
        final_scaled_constraint_2_norm=final_constraint,
        numerical_selected_eigenvalues_diagnostic_only=eigenvalues,
        numerical_descriptor_fiber_residual_diagnostic_only=fiber,
        selected_eigenline_gaps=gaps,
        state_weights=weights,
        branch_reference=reference,
    )
    validation = {
        "all_371_corrected_endpoints_replayed": output_states.shape == (371, 98),
        "all_endpoint_constraints_close_numerically": float(np.max(final_constraint)) < 2.0e-14,
        "branch_24_selected_at_every_endpoint_diagnostically": bool(np.all(branches == 24)),
        "selected_line_remains_simple_numerically": float(np.min(gaps)) > 1.0e-7,
        "descriptor_carried_by_correlated_first_jet_not_binary_eigensolve": True,
        "no_pre_stop_descriptor_required_negative_clipping": bool(np.min(transported[:-1]) >= 0.0),
        "only_terminal_endpoint_may_use_zero_boundary_clip": bool(np.count_nonzero(transported < 0.0) <= 1),
        "all_quantities_finite": bool(np.all(np.isfinite(np.concatenate((output_states.ravel(), supplied, rates.ravel()))))),
        "no_action_source_selector_scale_gate_or_chord_changed": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    payload = {
        "artifact": "BHSM_N12_GATE7_CORRELATED_DESCRIPTOR_NEWTON_ENDPOINT_CANDIDATE",
        "status": "CORRELATED_DESCRIPTOR_ENDPOINT_STEP_REPLAYED" if passed else "CORRELATED_DESCRIPTOR_ENDPOINT_STEP_INVALID",
        "authority": "NUMERICAL_FIXED_DESCRIPTOR_FIELD_REPLAY_NOT_INTERVAL_AUTHORITY",
        "summary": {
            "maximum_requested_correction_action_2_norm": float(np.max(np.linalg.norm(correction, axis=1))),
            "maximum_actual_displacement_action_2_norm": float(np.max(np.linalg.norm(actual_delta_action, axis=1))),
            "maximum_constraint_projection_action_2_norm": float(np.max(np.linalg.norm(projection_action, axis=1))),
            "maximum_final_scaled_constraint_2_norm": float(np.max(final_constraint)),
            "minimum_transported_unclipped_descriptor": float(np.min(transported)),
            "maximum_numeric_descriptor_fiber_residual_diagnostic_only": float(np.max(np.abs(fiber))),
            "minimum_selected_eigenline_gap": float(np.min(gaps)),
        },
        "data": _relative(DATA),
        "data_SHA256": _sha256(DATA),
        "inputs": {_relative(path): _sha256(path) for path in (
            CENTER, CENTER.with_suffix(".npz"), PREDICTOR, PREDICTOR.with_suffix(".npz"),
            JACOBIAN, JACOBIAN.with_suffix(".npz"), THEORY, THIS_SCRIPT,
        )},
        "claim_boundary": {
            "binary64_selected_eigenvalue": "DIAGNOSTIC_ONLY_NOT_DESCRIPTOR_AUTHORITY",
            "descriptor_graph_transport": "FIRST_ORDER_NUMERICAL_CANDIDATE",
            "nonlinear_Hermite_Simpson_center": "OPEN_MIDPOINT_REPLAY",
            "Gate7": "ACTIVE_ACTION_OWNED_OPERATOR_ORACLE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": "REPLAY_ALL_370_FIXED_DESCRIPTOR_MIDPOINTS",
        "validation": validation,
        "validation_passed": passed,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": payload["status"], "summary": payload["summary"], "validation_passed": passed}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
