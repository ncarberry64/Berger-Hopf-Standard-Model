"""Halve every fine span using its already-evaluated exact midpoint field."""

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


BASE = ROOT / "artifacts" / "flagship_integration"
NATIVE = BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.json"
NATIVE_DATA = NATIVE.with_suffix(".npz")
ENDPOINT = BASE / "BHSM_N12_GATE7_CURRENT_LINEARIZATION_NEWTON_ENDPOINT_CANDIDATE.json"
REPLAY = BASE / "BHSM_N12_GATE7_CURRENT_LINEARIZATION_NEWTON_COLLOCATION_REPLAY.json"
REPLAY_DATA = REPLAY.with_suffix(".npz")
THEORY = ROOT / "theory" / "n12_gate7_refined_within_seam_hermite_collocation.md"
RESULT = BASE / "BHSM_N12_GATE7_REFINED_WITHIN_SEAM_HERMITE_COLLOCATION.json"
DATA = RESULT.with_suffix(".npz")
THIS_SCRIPT = Path(__file__).resolve()
FIXED_STEP = 0.25
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


def _sample(task: tuple[object, ...]) -> tuple[int, dict[str, float | int], np.ndarray]:
    order, interval, sample, unit, left, right, left_rate, right_rate, duration = task
    weights = _WORK["weights"]
    reference = _WORK["reference"]
    augmented, path_rate = collocation.hermite._hermite(
        left, right, left_rate, right_rate, float(unit), float(duration),
    )
    descriptor = max(float(augmented[-1]), 0.0)
    state = augmented[:-1] / weights
    exact_rate, field = collocation._field(state, descriptor, weights, reference)
    defect = path_rate - exact_rate
    eigenvalue = float(field["numeric_selected_eigenvalue_not_used_as_descriptor"])
    row = {
        "interval": int(interval),
        "sample": int(sample),
        "unit_fraction": float(unit),
        "descriptor": descriptor,
        "numeric_descriptor_fiber_residual": eigenvalue - descriptor,
        "scaled_constraint_2_norm": collocation.constraints._scaled_residual(state, weights)[0],
        "augmented_flow_defect_2_norm": float(np.linalg.norm(defect)),
        "state_flow_defect_2_norm": float(np.linalg.norm(defect[:-1])),
        "descriptor_rate_defect_absolute": abs(float(defect[-1])),
        "selected_branch": int(field["selected_branch"]),
        "selected_eigenline_gap": float(field["selected_eigenline_gap"]),
    }
    return int(order), row, defect


def main() -> None:
    endpoint = _load(ENDPOINT)
    replay = _load(REPLAY)
    if endpoint.get("validation_passed") is not True or replay.get("validation_passed") is not True:
        raise RuntimeError("validated second Newton endpoints and replay required")
    with np.load(NATIVE_DATA) as source:
        native_values = np.asarray(source["fine_grid_augmented_action_values"], dtype=float)
        native_coefficients = np.asarray(source["fine_grid_DOP853_dense_coefficients"], dtype=float)
    with np.load(REPLAY_DATA) as source:
        times = np.asarray(source["action_times"], dtype=float)
        endpoints = np.asarray(source["corrected_augmented_endpoints"], dtype=float)
        endpoint_rates = np.asarray(source["corrected_endpoint_rates"], dtype=float)
        correction = np.asarray(source["correction_endpoints"], dtype=float)
        correction_rates = np.asarray(source["correction_endpoint_rates"], dtype=float)
        sample_intervals = np.asarray(source["sample_interval"], dtype=int)
        sample_fractions = np.asarray(source["sample_fraction"], dtype=float)
        old_defects = np.asarray(source["sampled_augmented_flow_defect"], dtype=float)
    with np.load(ENDPOINT.with_suffix(".npz")) as source:
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)

    midpoint_values = []
    midpoint_rates = []
    midpoint_times = []
    for interval in range(times.size - 1):
        duration = float(times[interval + 1] - times[interval])
        right_fraction = duration / FIXED_STEP
        fraction = 0.5 * right_fraction
        native_midpoint = collocation.hermite._dense(
            native_values[interval], native_coefficients[interval], fraction,
        )
        native_midpoint_rate = collocation.hermite._dense_rate(
            native_values[interval], native_coefficients[interval], fraction, FIXED_STEP,
        )
        correction_midpoint, correction_midpoint_rate = collocation.hermite._hermite(
            correction[interval], correction[interval + 1],
            correction_rates[interval], correction_rates[interval + 1],
            0.5, duration,
        )
        midpoint = native_midpoint + correction_midpoint
        path_rate = native_midpoint_rate + correction_midpoint_rate
        mask = sample_intervals == interval
        local_fraction = sample_fractions[mask]
        local_defect = old_defects[mask]
        middle = int(np.argmin(np.abs(local_fraction - fraction)))
        if abs(float(local_fraction[middle]) - fraction) > 2.0e-14:
            raise RuntimeError("the retained Gauss-3 midpoint is missing")
        midpoint_values.append(midpoint)
        midpoint_rates.append(path_rate - local_defect[middle])
        midpoint_times.append(0.5 * float(times[interval] + times[interval + 1]))
    midpoint_values = np.asarray(midpoint_values)
    midpoint_rates = np.asarray(midpoint_rates)

    refined_times = np.empty(741)
    refined_values = np.empty((741, 99))
    refined_rates = np.empty((741, 99))
    for interval in range(370):
        refined_times[2 * interval] = times[interval]
        refined_times[2 * interval + 1] = midpoint_times[interval]
        refined_values[2 * interval] = endpoints[interval]
        refined_values[2 * interval + 1] = midpoint_values[interval]
        refined_rates[2 * interval] = endpoint_rates[interval]
        refined_rates[2 * interval + 1] = midpoint_rates[interval]
    refined_times[-1] = times[-1]
    refined_values[-1] = endpoints[-1]
    refined_rates[-1] = endpoint_rates[-1]

    nodes, _ = np.polynomial.legendre.leggauss(3)
    units = 0.5 * (nodes + 1.0)
    tasks = []
    order = 0
    for interval in range(740):
        duration = float(refined_times[interval + 1] - refined_times[interval])
        for sample, unit in enumerate(units):
            tasks.append((
                order, interval, sample, float(unit),
                refined_values[interval], refined_values[interval + 1],
                refined_rates[interval], refined_rates[interval + 1], duration,
            ))
            order += 1
    workers = min(
        int(os.environ.get("BHSM_N12_REFINED_HERMITE_WORKERS", "8")),
        os.cpu_count() or 1,
    )
    with ProcessPoolExecutor(max_workers=workers, initializer=_initialize, initargs=(weights, reference)) as executor:
        sampled = list(executor.map(_sample, tasks, chunksize=2))
    sampled.sort(key=lambda item: item[0])
    rows = [item[1] for item in sampled]
    defects = np.asarray([item[2] for item in sampled])
    flow_norms = np.asarray([row["augmented_flow_defect_2_norm"] for row in rows])
    constraint_norms = np.asarray([row["scaled_constraint_2_norm"] for row in rows])
    fiber_residuals = np.asarray([row["numeric_descriptor_fiber_residual"] for row in rows])
    prior_flow = float(replay["summary"]["maximum_augmented_flow_defect_2_norm"])
    owner = int(np.argmax(flow_norms))
    np.savez_compressed(
        DATA,
        refined_action_times=refined_times,
        refined_augmented_nodes=refined_values,
        refined_exact_node_rates=refined_rates,
        sample_interval=np.asarray([row["interval"] for row in rows], dtype=int),
        sample_unit_fraction=np.asarray([row["unit_fraction"] for row in rows]),
        sampled_augmented_flow_defect=defects,
        sampled_augmented_flow_defect_2_norm=flow_norms,
        sampled_scaled_constraint_2_norm=constraint_norms,
        sampled_numeric_descriptor_fiber_residual=fiber_residuals,
    )
    validation = {
        "all_370_existing_exact_midpoint_fields_inserted": midpoint_rates.shape == (370, 99),
        "all_741_refined_nodes_materialized": refined_values.shape == (741, 99),
        "all_2220_refined_Gauss3_samples_evaluated": len(rows) == 2220,
        "branch_24_selected_at_every_sample": all(row["selected_branch"] == 24 for row in rows),
        "selected_line_remains_simple_numerically": min(row["selected_eigenline_gap"] for row in rows) > 1.0e-7,
        "within_seam_halving_reduces_maximum_flow_defect": float(np.max(flow_norms)) < prior_flow,
        "all_quantities_finite": bool(np.all(np.isfinite(np.concatenate((
            refined_values.ravel(), refined_rates.ravel(), defects.ravel(),
        ))))),
        "continuous_interval_shadowing_not_claimed": True,
        "quarter_step_proof_center_not_replaced": True,
        "no_action_source_selector_scale_gate_or_chord_changed": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    payload = {
        "artifact": "BHSM_N12_GATE7_REFINED_WITHIN_SEAM_HERMITE_COLLOCATION",
        "status": "WITHIN_SEAM_HALVING_REDUCES_HERMITE_FLOW_DEFECT" if passed else "WITHIN_SEAM_HALVING_DOES_NOT_REDUCE_FLOW_DEFECT",
        "authority": "NUMERICAL_REFINED_GAUSS3_COLLOCATION_NOT_INTERVAL_AUTHORITY",
        "mesh": {"refined_intervals": 740, "refined_nodes": 741, "Gauss_samples_per_interval": 3, "workers": workers},
        "summary": {
            "maximum_sampled_scaled_constraint_2_norm": float(np.max(constraint_norms)),
            "maximum_numeric_descriptor_fiber_residual_absolute": float(np.max(np.abs(fiber_residuals))),
            "maximum_augmented_flow_defect_2_norm": float(np.max(flow_norms)),
            "prior_maximum_augmented_flow_defect_2_norm": prior_flow,
            "flow_defect_reduction_factor": prior_flow / float(np.max(flow_norms)),
            "minimum_selected_eigenline_gap": min(row["selected_eigenline_gap"] for row in rows),
            "flow_defect_owner": rows[owner],
        },
        "data": _relative(DATA),
        "data_SHA256": _sha256(DATA),
        "inputs": {
            _relative(path): _sha256(path)
            for path in (NATIVE, NATIVE_DATA, ENDPOINT, ENDPOINT.with_suffix(".npz"), REPLAY, REPLAY_DATA, THEORY, THIS_SCRIPT)
        },
        "adjudication": {
            "quarter_step_center": "RETAINED",
            "within_seam_interpolant": "HALVED_USING_ALREADY_EVALUATED_EXACT_MIDPOINT_FIELDS",
            "continuous_center": "OPEN_INTERVAL_SHADOWING_OR_FURTHER_OWNER_REFINEMENT",
        },
        "claim_boundary": {
            "continuous_action_constrained_center": "OPEN_INTERVAL_AUTHORITY",
            "continuous_outward_variational_carrier": "OPEN_AFTER_CENTER",
            "Gate7": "ACTIVE_ACTION_OWNED_OPERATOR_ORACLE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "IF_THE_EXPECTED_INTERPOLATION_ORDER_IS_OBSERVED,_REFINE_ONLY_UNTIL_"
            "THE_DEFECT_FITS_THE_TAYLOR_VOLTERRA_KRAWCZYK_BUDGET;_OTHERWISE_"
            "ROUTE_TO_DIRECT_HIGH_ORDER_MULTIPLE_SHOOTING"
        ),
        "validation": validation,
        "validation_passed": passed,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": payload["status"], "summary": payload["summary"], "validation_passed": passed}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
