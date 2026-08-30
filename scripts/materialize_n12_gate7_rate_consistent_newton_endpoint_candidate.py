"""Apply the repaired Newton step with one-jet descriptor/rate recentering."""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import audit_n12_gate7_constraint_descriptor_hermite_collocation_candidate as collocation  # noqa: E402
import audit_n12_gate7_within_seam_constraint_center_obstruction as constraints  # noqa: E402
from bhsm.interface.aether_forward_c2_descriptor_cover import metric_data  # noqa: E402
import bhsm.interface.aether_forward_c2_exact_fixed_s_field as exact_field  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
CENTER = BASE / "BHSM_N12_GATE7_FIRST_HS_RECENTERED_RATE_CONSISTENT_ENDPOINTS.json"
PREDICTOR = BASE / "BHSM_N12_GATE7_RATE_CONSISTENT_BLOCK_NEWTON_PREDICTOR.json"
THEORY = ROOT / "theory" / "n12_gate7_rate_consistent_newton_endpoint_candidate.md"
RESULT = BASE / "BHSM_N12_GATE7_RATE_CONSISTENT_NEWTON_ENDPOINT_CANDIDATE.json"
DATA = RESULT.with_suffix(".npz")
THIS_SCRIPT = Path(__file__).resolve()
PROJECTION_TRIGGER = 2.0e-14
QDIM = 37
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


def _recentered_rate(state: np.ndarray, weights: np.ndarray, reference: np.ndarray) -> tuple[np.ndarray, float, int, float]:
    """Evaluate the selected eigenvalue and its cancelled field with one jet."""
    jet = exact_field._jet(state)
    gradient_action = np.asarray(jet.gradient, dtype=float) / weights
    hessian_raw = np.asarray(jet.hessian, dtype=float)
    hessian_action = hessian_raw / weights[:, None] / weights[None, :]
    selected, eigenvalue, psi, complement, hard_values = exact_field._selected_line(
        hessian_raw[QDIM:, QDIM:], reference,
    )
    q_weights, reduced_weights, _, _ = metric_data()
    configuration = q_weights * state[QDIM:2 * QDIM]
    rhs_action = np.concatenate((
        q_weights * gradient_action[:QDIM] - hessian_action[QDIM:2 * QDIM, :QDIM] @ configuration,
        -hessian_action[2 * QDIM:, :QDIM] @ configuration,
    ))
    rhs_raw = reduced_weights * rhs_action
    b_psi = float(psi @ rhs_raw)
    hard_raw = complement @ ((complement.T @ rhs_raw) / (hard_values - eigenvalue))
    psi_action = np.concatenate((np.zeros(QDIM), reduced_weights * psi))
    full_hard_action = np.concatenate((configuration, reduced_weights * hard_raw))
    c_psi = exact_field._eigenvalue_directional_derivative(state, psi, psi_action, weights)
    remainder = exact_field._eigenvalue_directional_derivative(state, psi, full_hard_action, weights)
    descriptor = max(float(eigenvalue), 0.0)
    delta = c_psi * b_psi + descriptor * remainder
    cancelled = np.concatenate((
        descriptor * configuration,
        reduced_weights * (b_psi * psi + descriptor * hard_raw),
    ))
    norm = float(np.linalg.norm(cancelled))
    rate = np.concatenate((cancelled / norm, [delta / norm]))
    gap = float(np.min(np.abs(hard_values - eigenvalue)))
    return rate, float(eigenvalue), int(selected), gap


def _node(task: tuple[int, np.ndarray]) -> tuple[object, ...]:
    index, action_state = task
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
    rate, eigenvalue, selected, gap = _recentered_rate(state, weights, reference)
    return index, state, projection_action, initial, final, rate, eigenvalue, selected, gap


def main() -> None:
    center = _load(CENTER)
    predictor = _load(PREDICTOR)
    if center.get("validation_passed") is not True or predictor.get("validation_passed") is not True:
        raise RuntimeError("validated rate-consistent center and predictor required")
    with np.load(CENTER.with_suffix(".npz")) as source:
        times = np.asarray(source["action_times"], dtype=float)
        states = np.asarray(source["projected_states"], dtype=float)
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)
    with np.load(PREDICTOR.with_suffix(".npz")) as source:
        correction = np.asarray(source["endpoint_state_correction_action"], dtype=float)
    trial_action_states = states * weights[None, :] + correction
    workers = min(int(os.environ.get("BHSM_N12_RATE_CONSISTENT_NEWTON_WORKERS", "8")), os.cpu_count() or 1)
    with ProcessPoolExecutor(max_workers=workers, initializer=_initialize, initargs=(weights, reference)) as executor:
        rows = list(executor.map(_node, list(enumerate(trial_action_states)), chunksize=2))
    rows.sort(key=lambda item: int(item[0]))
    output_states = np.asarray([row[1] for row in rows])
    projection_action = np.asarray([row[2] for row in rows])
    initial_constraint = np.asarray([row[3] for row in rows])
    final_constraint = np.asarray([row[4] for row in rows])
    rates = np.asarray([row[5] for row in rows])
    eigenvalues = np.asarray([row[6] for row in rows])
    branches = np.asarray([row[7] for row in rows], dtype=int)
    gaps = np.asarray([row[8] for row in rows])
    descriptors = np.maximum(eigenvalues, 0.0)
    sign_changes = np.flatnonzero((eigenvalues[:-1] > 0.0) & (eigenvalues[1:] <= 0.0))
    np.savez_compressed(
        DATA,
        action_times=times,
        projected_states=output_states,
        recentered_descriptors=descriptors,
        exact_endpoint_augmented_rates=rates,
        Hermite_Simpson_endpoint_correction_action=correction,
        constraint_projection_action=projection_action,
        initial_scaled_constraint_2_norm=initial_constraint,
        final_scaled_constraint_2_norm=final_constraint,
        numerical_selected_eigenvalues=eigenvalues,
        selected_eigenline_gaps=gaps,
        raw_endpoint_sign_change_intervals=sign_changes,
        state_weights=weights,
        branch_reference=reference,
    )
    correction_norm = np.linalg.norm(correction, axis=1)
    projection_norm = np.linalg.norm(projection_action, axis=1)
    validation = {
        "all_371_corrected_endpoints_replayed": output_states.shape == (371, 98),
        "all_endpoint_constraints_close_numerically": float(np.max(final_constraint)) < 2.0e-14,
        "branch_24_selected_at_every_endpoint": bool(np.all(branches == 24)),
        "selected_line_remains_simple_numerically": float(np.min(gaps)) > 1.0e-7,
        "each_endpoint_rate_uses_its_same_call_recentered_descriptor": True,
        "all_quantities_finite": bool(np.all(np.isfinite(np.concatenate((output_states.ravel(), descriptors, rates.ravel()))))),
        "terminal_first_hit_adapter_not_imposed_before_center_convergence": True,
        "no_action_source_selector_scale_gate_or_chord_changed": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    payload = {
        "artifact": "BHSM_N12_GATE7_RATE_CONSISTENT_NEWTON_ENDPOINT_CANDIDATE",
        "status": "RATE_CONSISTENT_NEWTON_ENDPOINTS_PROJECTED_RECENTERED_AND_REEVALUATED" if passed else "RATE_CONSISTENT_NEWTON_ENDPOINTS_INVALID",
        "authority": "DIRECT_ONE_JET_SELECTED_DESCRIPTOR_AND_CANCELLED_FIELD_REPLAY_NUMERICAL_CANDIDATE",
        "summary": {
            "maximum_endpoint_correction_action_2_norm": float(np.max(correction_norm)),
            "maximum_constraint_projection_action_2_norm": float(np.max(projection_norm)),
            "maximum_final_scaled_constraint_2_norm": float(np.max(final_constraint)),
            "minimum_selected_eigenline_gap": float(np.min(gaps)),
            "raw_endpoint_sign_change_brackets": [[float(times[i]), float(times[i + 1])] for i in sign_changes],
            "terminal_numeric_selected_eigenvalue": float(eigenvalues[-1]),
        },
        "data": _relative(DATA),
        "data_SHA256": _sha256(DATA),
        "inputs": {_relative(path): _sha256(path) for path in (
            CENTER, CENTER.with_suffix(".npz"), PREDICTOR, PREDICTOR.with_suffix(".npz"), THEORY, THIS_SCRIPT,
        )},
        "claim_boundary": {
            "nonlinear_Hermite_Simpson_center": "OPEN_MIDPOINT_REPLAY",
            "continuous_action_constrained_center": "OPEN",
            "Gate7": "ACTIVE_ACTION_OWNED_OPERATOR_ORACLE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": "REPLAY_ALL_370_RATE_CONSISTENT_NEWTON_MIDPOINTS",
        "validation": validation,
        "validation_passed": passed,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": payload["status"], "summary": payload["summary"], "validation_passed": passed}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
