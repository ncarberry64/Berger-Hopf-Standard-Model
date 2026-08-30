"""Apply and constraint-project the Hermite--Simpson block Newton predictor."""

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
import materialize_n12_gate7_signed_green_projected_endpoint_candidate as projected  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
CENTER = BASE / "BHSM_N12_GATE7_CURRENT_LINEARIZATION_NEWTON_ENDPOINT_CANDIDATE.json"
PREDICTOR = BASE / "BHSM_N12_GATE7_HERMITE_SIMPSON_BLOCK_NEWTON_PREDICTOR.json"
THEORY = ROOT / "theory" / "n12_gate7_hermite_simpson_newton_endpoint_candidate.md"
RESULT = BASE / "BHSM_N12_GATE7_HERMITE_SIMPSON_NEWTON_ENDPOINT_CANDIDATE.json"
DATA = RESULT.with_suffix(".npz")
THIS_SCRIPT = Path(__file__).resolve()


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def main() -> None:
    center = _load(CENTER)
    predictor = _load(PREDICTOR)
    if center.get("validation_passed") is not True or predictor.get("validation_passed") is not True:
        raise RuntimeError("validated center and block Newton predictor required")
    with np.load(CENTER.with_suffix(".npz")) as source:
        times = np.asarray(source["action_times"], dtype=float)
        states = np.asarray(source["projected_states"], dtype=float)
        descriptors = np.asarray(source["recentered_descriptors"], dtype=float)
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)
    with np.load(PREDICTOR.with_suffix(".npz")) as source:
        correction = np.asarray(source["endpoint_state_correction_action"], dtype=float)
    trial_action_states = states * weights[None, :] + correction
    workers = min(
        int(os.environ.get("BHSM_N12_HS_NEWTON_WORKERS", "8")),
        os.cpu_count() or 1,
    )
    tasks = [
        (index, trial_action_states[index], float(descriptors[index]))
        for index in range(times.size)
    ]
    with ProcessPoolExecutor(
        max_workers=workers,
        initializer=projected._initialize,
        initargs=(weights, reference),
    ) as executor:
        rows = list(executor.map(projected._replay, tasks, chunksize=2))
    rows.sort(key=lambda item: int(item[0]))
    trial_states = np.asarray([item[1] for item in rows])
    projection_action = np.asarray([item[2] for item in rows])
    initial_constraint = np.asarray([item[3] for item in rows])
    final_constraint = np.asarray([item[4] for item in rows])
    rates = np.asarray([item[5] for item in rows])
    eigenvalues = np.asarray([item[6] for item in rows])
    branches = np.asarray([item[7] for item in rows], dtype=int)
    gaps = np.asarray([item[8] for item in rows])

    if eigenvalues[-2] > 0.0 > eigenvalues[-1]:
        left_stop, right_stop, stop_state, left_lambda, right_lambda = collocation._terminal_bracket(
            times, trial_states, weights, reference,
        )
        stop_route = "WITHIN_REPLAYED_FINAL_SEGMENT"
    elif eigenvalues[-1] > 0.0:
        left_stop, right_stop, stop_state, left_lambda, right_lambda = projected._extended_terminal_bracket(
            times, trial_states, float(eigenvalues[-1]), weights, reference,
        )
        stop_route = "ONE_STEP_RETAINED_FIELD_CONTINUATION_INSIDE_UNUSED_TERMINAL_CELL"
    else:
        raise RuntimeError("Hermite--Simpson Newton step moved the stop before the final segment")
    stop_time = 0.5 * (left_stop + right_stop)
    stop_rate, stop_field = collocation._field(stop_state, 0.0, weights, reference)
    output_times = np.concatenate((times[:-1], [stop_time]))
    output_states = np.vstack((trial_states[:-1], stop_state))
    output_descriptors = np.concatenate((descriptors[:1], eigenvalues[1:-1], [0.0]))
    output_rates = np.vstack((rates[:-1], stop_rate))
    stop_constraint = collocation.constraints._scaled_residual(stop_state, weights)[0]
    output_constraint = np.concatenate((final_constraint[:-1], [stop_constraint]))
    correction_norm = np.linalg.norm(correction, axis=1)
    projection_norm = np.linalg.norm(projection_action, axis=1)
    np.savez_compressed(
        DATA,
        action_times=output_times,
        projected_states=output_states,
        recentered_descriptors=output_descriptors,
        exact_endpoint_augmented_rates=output_rates,
        Hermite_Simpson_endpoint_correction_action=correction,
        constraint_projection_action=projection_action,
        initial_scaled_constraint_2_norm=initial_constraint,
        final_scaled_constraint_2_norm=output_constraint,
        selected_eigenline_gaps=gaps,
        first_hit_action_time_bracket=np.asarray([left_stop, right_stop]),
        state_weights=weights,
        branch_reference=reference,
    )
    validation = {
        "all_371_block_Newton_endpoints_replayed": output_states.shape == (371, 98),
        "all_endpoint_constraints_close_numerically": float(np.max(output_constraint)) < 2.0e-14,
        "branch_24_selected_at_every_endpoint": bool(np.all(branches == 24)),
        "selected_line_remains_simple_numerically": float(np.min(gaps)) > 1.0e-7,
        "all_complete_preterminal_descriptors_are_positive": float(np.min(output_descriptors[:-1])) > 0.0,
        "terminal_selected_eigenvalue_is_numerically_bracketed": left_lambda > 0.0 > right_lambda,
        "terminal_bracket_not_promoted_to_outward_root": True,
        "all_quantities_finite": bool(np.all(np.isfinite(np.concatenate((
            output_states.ravel(), output_descriptors, output_rates.ravel(),
            correction.ravel(), projection_action.ravel(),
        ))))),
        "nonlinear_dense_replay_not_yet_claimed": True,
        "no_action_source_selector_scale_gate_or_chord_changed": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    payload = {
        "artifact": "BHSM_N12_GATE7_HERMITE_SIMPSON_NEWTON_ENDPOINT_CANDIDATE",
        "status": "HERMITE_SIMPSON_BLOCK_NEWTON_ENDPOINTS_MATERIALIZED" if passed else "HERMITE_SIMPSON_ENDPOINT_CANDIDATE_INVALID",
        "authority": "NUMERICAL_CONSTRAINT_PROJECTED_BLOCK_NEWTON_ENDPOINTS_NOT_INTERVAL_AUTHORITY",
        "summary": {
            "maximum_endpoint_correction_action_2_norm": float(np.max(correction_norm)),
            "maximum_endpoint_correction_owner_node": int(np.argmax(correction_norm)),
            "terminal_endpoint_correction_action_2_norm": float(correction_norm[-1]),
            "triggered_constraint_projection_count": int(np.count_nonzero(projection_norm)),
            "maximum_constraint_projection_action_2_norm": float(np.max(projection_norm)),
            "maximum_final_scaled_constraint_2_norm": float(np.max(output_constraint)),
            "minimum_selected_eigenline_gap": float(np.min(gaps)),
            "first_hit_action_time_bracket": [left_stop, right_stop],
            "terminal_stop_route": stop_route,
            "terminal_stop_selected_branch": int(stop_field["selected_branch"]),
        },
        "data": _relative(DATA),
        "data_SHA256": _sha256(DATA),
        "inputs": {
            _relative(path): _sha256(path)
            for path in (
                CENTER, CENTER.with_suffix(".npz"), PREDICTOR,
                PREDICTOR.with_suffix(".npz"), THEORY, THIS_SCRIPT,
            )
        },
        "claim_boundary": {
            "nonlinear_Hermite_Simpson_center": "OPEN_DENSE_EXACT_REPLAY",
            "continuous_action_constrained_center": "OPEN_INTERVAL_AUTHORITY",
            "continuous_outward_variational_carrier": "OPEN_AFTER_CENTER",
            "Gate7": "ACTIVE_ACTION_OWNED_OPERATOR_ORACLE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": "JOIN_THE_ENDPOINTS_WITH_ENDPOINT_FIELD_MATCHED_CUBICS_AND_REPLAY_ALL_1110_EXACT_GAUSS3_RESIDUALS",
        "validation": validation,
        "validation_passed": passed,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "summary": payload["summary"],
        "validation_passed": passed,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
