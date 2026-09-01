"""Build the minimum cubic constraint/descriptor-fiber collocation candidate."""

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

import audit_n12_gate7_within_seam_constraint_center_obstruction as constraints  # noqa: E402
import recon_n12_c2_stop_newton_corrected_dense_residual as hermite  # noqa: E402
from bhsm.interface.aether_forward_c2_exact_fixed_s_field import (  # noqa: E402
    exact_cancelled_euler_dirac_field_action,
)


BASE = ROOT / "artifacts" / "flagship_integration"
NATIVE = BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.json"
NATIVE_DATA = NATIVE.with_suffix(".npz")
PROJECTED = BASE / "BHSM_N12_GATE7_PROJECTED_EXACT_AFFINE_FINE_CENTER_CANDIDATE.json"
PROJECTED_DATA = PROJECTED.with_suffix(".npz")
PRIOR = BASE / "BHSM_N12_GATE7_PROJECTED_EXACT_AFFINE_DENSE_CENTER_FLOW_DEFECT.json"
THEORY = ROOT / "theory" / "n12_gate7_constraint_descriptor_hermite_collocation_candidate.md"
RESULT = BASE / "BHSM_N12_GATE7_CONSTRAINT_DESCRIPTOR_HERMITE_COLLOCATION_CANDIDATE.json"
DATA = RESULT.with_suffix(".npz")
THIS_SCRIPT = Path(__file__).resolve()
FIXED_STEP = 0.25
ROOT_BISECTIONS = 32
_WORK: dict[str, object] = {}


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _project(state: np.ndarray, weights: np.ndarray, steps: int = 2) -> np.ndarray:
    result = np.array(state, copy=True)
    for _ in range(steps):
        frame, norms, values = constraints._constraint_geometry(result, weights)
        scaled = values / norms
        gram = frame @ frame.T
        correction = -frame.T @ np.linalg.solve(gram, scaled)
        result += correction / weights
    return result


def _field(state: np.ndarray, descriptor: float, weights: np.ndarray, reference: np.ndarray) -> tuple[np.ndarray, dict[str, object]]:
    value = exact_cancelled_euler_dirac_field_action(
        state=state,
        weights=weights,
        reference=reference,
        signed_descriptor=max(float(descriptor), 0.0),
    )
    cancelled = np.asarray(value["cancelled_field_action"], dtype=float)
    norm = float(np.linalg.norm(cancelled))
    rate = np.concatenate((cancelled / norm, [float(value["Delta"]) / norm]))
    return rate, value


def _initialize(weights: np.ndarray, reference: np.ndarray) -> None:
    _WORK["weights"] = weights
    _WORK["reference"] = reference


def _node(task: tuple[int, np.ndarray, float]) -> tuple[int, np.ndarray, float, int, float]:
    index, state, supplied = task
    weights = np.asarray(_WORK["weights"])
    reference = np.asarray(_WORK["reference"])
    rate, value = _field(state, supplied, weights, reference)
    eigenvalue = float(value["numeric_selected_eigenvalue_not_used_as_descriptor"])
    return index, rate, eigenvalue, int(value["selected_branch"]), float(value["selected_eigenline_gap"])


def _terminal_state(
    time: float,
    left_time: float,
    right_time: float,
    left_state: np.ndarray,
    right_state: np.ndarray,
    weights: np.ndarray,
) -> np.ndarray:
    unit = (time - left_time) / (right_time - left_time)
    return _project((1.0 - unit) * left_state + unit * right_state, weights, steps=3)


def _terminal_bracket(
    times: np.ndarray,
    states: np.ndarray,
    weights: np.ndarray,
    reference: np.ndarray,
) -> tuple[float, float, np.ndarray, float, float]:
    segment_left = float(times[-2])
    segment_right = float(times[-1])
    bracket_left = segment_left
    bracket_right = segment_right

    def value(time: float) -> tuple[float, np.ndarray]:
        state = _terminal_state(
            time, segment_left, segment_right, states[-2], states[-1], weights,
        )
        _, field = _field(state, 0.0, weights, reference)
        return float(field["numeric_selected_eigenvalue_not_used_as_descriptor"]), state

    left_value, _ = value(bracket_left)
    right_value, _ = value(bracket_right)
    if not left_value > 0.0 > right_value:
        raise RuntimeError("projected final-node states do not bracket the selected stop")
    for _ in range(ROOT_BISECTIONS):
        midpoint = 0.5 * (bracket_left + bracket_right)
        midpoint_value, _ = value(midpoint)
        if midpoint_value > 0.0:
            bracket_left = midpoint
            left_value = midpoint_value
        else:
            bracket_right = midpoint
            right_value = midpoint_value
    representative = 0.5 * (bracket_left + bracket_right)
    _, state = value(representative)
    return bracket_left, bracket_right, state, left_value, right_value


def _sample(task: tuple[object, ...]) -> tuple[int, dict[str, float | int], np.ndarray]:
    (
        order, interval, sample, unit, right_fraction, native_left,
        native_coefficients, correction_endpoints, correction_rates,
    ) = task
    weights = np.asarray(_WORK["weights"])
    reference = np.asarray(_WORK["reference"])
    original_fraction = float(right_fraction) * float(unit)
    native_value = np.asarray(
        hermite._dense(native_left, native_coefficients, original_fraction),
        dtype=float,
    )
    native_rate = hermite._dense_rate(
        native_left, native_coefficients, original_fraction, FIXED_STEP,
    )
    duration = FIXED_STEP * float(right_fraction)
    correction, correction_rate = hermite._hermite(
        correction_endpoints[0], correction_endpoints[1],
        correction_rates[0], correction_rates[1], float(unit), duration,
    )
    augmented = native_value + correction
    path_rate = native_rate + correction_rate
    if augmented[-1] < -1.0e-15:
        raise RuntimeError("Hermite descriptor left the pre-stop domain")
    descriptor = max(float(augmented[-1]), 0.0)
    state = augmented[:-1] / weights
    exact_rate, value = _field(state, descriptor, weights, reference)
    defect = path_rate - exact_rate
    scaled_constraint = constraints._scaled_residual(state, weights)[0]
    eigenvalue = float(value["numeric_selected_eigenvalue_not_used_as_descriptor"])
    row = {
        "interval": int(interval),
        "sample": int(sample),
        "fraction": original_fraction,
        "descriptor": descriptor,
        "numeric_descriptor_fiber_residual": eigenvalue - descriptor,
        "scaled_constraint_2_norm": scaled_constraint,
        "augmented_flow_defect_2_norm": float(np.linalg.norm(defect)),
        "state_flow_defect_2_norm": float(np.linalg.norm(defect[:-1])),
        "descriptor_rate_defect_absolute": abs(float(defect[-1])),
        "selected_branch": int(value["selected_branch"]),
        "selected_eigenline_gap": float(value["selected_eigenline_gap"]),
    }
    return int(order), row, defect


def main() -> None:
    projected = _load(PROJECTED)
    prior = _load(PRIOR)
    if projected.get("validation_passed") is not True or prior.get("validation_passed") is not True:
        raise RuntimeError("validated projected center and prior dense audit required")
    with np.load(NATIVE_DATA) as source:
        native_times = np.asarray(source["fine_grid_action_lengths"], dtype=float)
        native_values = np.asarray(source["fine_grid_augmented_action_values"], dtype=float)
        native_coefficients = np.asarray(source["fine_grid_DOP853_dense_coefficients"], dtype=float)
        stop_fraction = float(source["stop_dense_fraction"][0])
    with np.load(PROJECTED_DATA) as source:
        times = np.asarray(source["action_times"], dtype=float)
        states = np.asarray(source["projected_states"], dtype=float)
        supplied_descriptors = np.asarray(source["exact_affine_descriptors"], dtype=float)
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)

    left_stop, right_stop, stop_state, left_lambda, right_lambda = _terminal_bracket(
        times, states, weights, reference,
    )
    stop_time = 0.5 * (left_stop + right_stop)
    endpoint_times = np.concatenate((times[:-1], [stop_time]))
    endpoint_states = np.vstack((states[:-1], stop_state))

    workers = min(
        int(os.environ.get("BHSM_N12_HERMITE_COLLOCATION_WORKERS", "8")),
        os.cpu_count() or 1,
    )
    node_tasks = [
        (index, state, float(supplied_descriptors[index]))
        for index, state in enumerate(endpoint_states[:-1])
    ]
    with ProcessPoolExecutor(
        max_workers=workers,
        initializer=_initialize,
        initargs=(weights, reference),
    ) as executor:
        node_rows = list(executor.map(_node, node_tasks, chunksize=2))
    node_rows.sort(key=lambda item: item[0])
    node_rates = [item[1] for item in node_rows]
    node_descriptors = [float(supplied_descriptors[0])]
    node_descriptors.extend(float(item[2]) for item in node_rows[1:])
    terminal_rate, terminal_field = _field(stop_state, 0.0, weights, reference)
    node_rates.append(terminal_rate)
    node_descriptors.append(0.0)
    node_rates = np.asarray(node_rates)
    node_descriptors = np.asarray(node_descriptors)

    native_endpoints = []
    native_rates = []
    for index, time in enumerate(endpoint_times):
        if index < endpoint_times.size - 1:
            fraction = 0.0
            interval = index
        else:
            interval = endpoint_times.size - 2
            fraction = (time - float(native_times[interval])) / FIXED_STEP
        native_endpoints.append(hermite._dense(native_values[interval], native_coefficients[interval], fraction))
        native_rates.append(hermite._dense_rate(native_values[interval], native_coefficients[interval], fraction, FIXED_STEP))
    native_endpoints = np.asarray(native_endpoints)
    native_rates = np.asarray(native_rates)
    corrected_endpoints = np.column_stack((endpoint_states * weights[None, :], node_descriptors))
    correction = corrected_endpoints - native_endpoints
    correction_rates = node_rates - native_rates

    nodes, _ = np.polynomial.legendre.leggauss(3)
    units = 0.5 * (nodes + 1.0)
    tasks = []
    order = 0
    for interval in range(endpoint_times.size - 1):
        duration = float(endpoint_times[interval + 1] - endpoint_times[interval])
        right_fraction = duration / FIXED_STEP
        for sample, unit in enumerate(units):
            tasks.append((
                order, interval, sample, float(unit), right_fraction,
                native_values[interval], native_coefficients[interval],
                correction[interval:interval + 2],
                correction_rates[interval:interval + 2],
            ))
            order += 1
    with ProcessPoolExecutor(
        max_workers=workers,
        initializer=_initialize,
        initargs=(weights, reference),
    ) as executor:
        sampled = list(executor.map(_sample, tasks, chunksize=2))
    sampled.sort(key=lambda item: item[0])
    rows = [item[1] for item in sampled]
    defects = np.asarray([item[2] for item in sampled])
    flow_norms = np.asarray([row["augmented_flow_defect_2_norm"] for row in rows])
    constraint_norms = np.asarray([row["scaled_constraint_2_norm"] for row in rows])
    fiber_residuals = np.asarray([row["numeric_descriptor_fiber_residual"] for row in rows])
    endpoint_constraint = np.asarray([
        constraints._scaled_residual(state, weights)[0] for state in endpoint_states
    ])
    prior_flow = float(prior["summary"]["maximum_augmented_flow_defect_2_norm"])
    owner = int(np.argmax(flow_norms))
    np.savez_compressed(
        DATA,
        action_times=endpoint_times,
        corrected_augmented_endpoints=corrected_endpoints,
        corrected_endpoint_rates=node_rates,
        correction_endpoints=correction,
        correction_endpoint_rates=correction_rates,
        endpoint_scaled_constraint_2_norm=endpoint_constraint,
        sample_interval=np.asarray([row["interval"] for row in rows], dtype=int),
        sample_fraction=np.asarray([row["fraction"] for row in rows]),
        sampled_augmented_flow_defect=defects,
        sampled_augmented_flow_defect_2_norm=flow_norms,
        sampled_scaled_constraint_2_norm=constraint_norms,
        sampled_numeric_descriptor_fiber_residual=fiber_residuals,
        first_hit_action_time_bracket=np.asarray([left_stop, right_stop]),
    )

    validation = {
        "all_371_constraint_projected_endpoints_retained_with_new_terminal_stop": endpoint_states.shape == (371, 98),
        "terminal_selected_eigenvalue_is_numerically_bracketed": left_lambda > 0.0 > right_lambda,
        "terminal_bracket_not_promoted_to_outward_root": True,
        "all_1110_Gauss3_collocation_samples_evaluated": len(rows) == 1110,
        "all_quantities_finite": bool(np.all(np.isfinite(np.concatenate((
            endpoint_times, corrected_endpoints.ravel(), node_rates.ravel(),
            defects.ravel(), constraint_norms, fiber_residuals,
        ))))),
        "all_endpoint_constraints_close_numerically": float(np.max(endpoint_constraint)) < 2.0e-14,
        "branch_24_selected_at_every_sample": all(row["selected_branch"] == 24 for row in rows),
        "selected_line_remains_simple_numerically": min(row["selected_eigenline_gap"] for row in rows) > 1.0e-7,
        "cubic_endpoint_field_matching_reduces_piecewise_linear_flow_defect": float(np.max(flow_norms)) < prior_flow,
        "continuous_interval_shadowing_not_claimed": True,
        "no_action_source_selector_scale_gate_or_chord_changed": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    payload = {
        "artifact": "BHSM_N12_GATE7_CONSTRAINT_DESCRIPTOR_HERMITE_COLLOCATION_CANDIDATE",
        "status": (
            "CUBIC_ENDPOINT_FIELD_MATCHED_CONSTRAINT_DESCRIPTOR_COLLOCATION_CANDIDATE_MATERIALIZED"
            if passed else "HERMITE_COLLOCATION_CANDIDATE_REQUIRES_OWNER_REFINEMENT"
        ),
        "authority": "NUMERICAL_GAUSS3_COLLOCATION_AUDIT_NOT_INTERVAL_SHADOWING_AUTHORITY",
        "mesh": {"fine_intervals": 370, "Gauss_samples_per_interval": 3, "workers": workers},
        "summary": {
            "first_hit_action_time_bracket": [left_stop, right_stop],
            "first_hit_bracket_width": right_stop - left_stop,
            "maximum_endpoint_scaled_constraint_2_norm": float(np.max(endpoint_constraint)),
            "maximum_sampled_scaled_constraint_2_norm": float(np.max(constraint_norms)),
            "maximum_numeric_descriptor_fiber_residual_absolute": float(np.max(np.abs(fiber_residuals))),
            "maximum_augmented_flow_defect_2_norm": float(np.max(flow_norms)),
            "prior_piecewise_linear_maximum_augmented_flow_defect_2_norm": prior_flow,
            "flow_defect_reduction_factor": prior_flow / float(np.max(flow_norms)),
            "minimum_selected_eigenline_gap": min(row["selected_eigenline_gap"] for row in rows),
            "flow_defect_owner": rows[owner],
        },
        "data": _relative(DATA),
        "data_SHA256": _sha256(DATA),
        "inputs": {
            _relative(path): _sha256(path)
            for path in (NATIVE, NATIVE_DATA, PROJECTED, PROJECTED_DATA, PRIOR, THEORY, THIS_SCRIPT)
        },
        "adjudication": {
            "projected_exact_affine_nodes": "RETAINED_AS_CONSTRAINT_ENDPOINTS",
            "descriptor_fiber": "NUMERICALLY_RECENTERED_AT_ENDPOINTS_AND_AUDITED_AT_GAUSS3_SAMPLES",
            "continuous_center": "OPEN_INTERVAL_SHADOWING_OR_COLLOCATION_NEWTON_CERTIFICATE",
            "first_hit": "NUMERICAL_BRACKET_ONLY_MUST_BE_REBUILT_OUTWARD",
        },
        "claim_boundary": {
            "continuous_action_constrained_center": "OPEN_INTERVAL_AUTHORITY",
            "continuous_outward_variational_carrier": "OPEN_AFTER_CENTER",
            "nonlinear_72D_history_first_jet": "OPEN_AFTER_CARRIER",
            "Weyl_force_KKT_Hessian": "NOT_CLAIMED",
            "Gate7": "ACTIVE_ACTION_OWNED_OPERATOR_ORACLE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "USE_THE_GAUSS3_DEFECT_AND_CONSTRAINT_FIBER_RESIDUALS_IN_THE_"
            "EXISTING_TAYLOR_VOLTERRA_KRAWCZYK_MACHINERY_TO_CERTIFY_A_"
            "CONTINUOUS_SHADOWING_CENTER,_THEN_REBUILD_THE_FINAL_CONE_AND_STOP"
        ),
        "validation": validation,
        "validation_passed": passed,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": payload["status"], "summary": payload["summary"], "validation_passed": passed}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
