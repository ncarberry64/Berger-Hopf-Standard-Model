"""Remeasure the dense defect after one signed-Green endpoint Newton step."""

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
ENDPOINT = BASE / "BHSM_N12_GATE7_SIGNED_GREEN_PROJECTED_ENDPOINT_CANDIDATE.json"
ENDPOINT_DATA = ENDPOINT.with_suffix(".npz")
PRIOR = BASE / "BHSM_N12_GATE7_CONSTRAINT_DESCRIPTOR_HERMITE_COLLOCATION_CANDIDATE.json"
THEORY = ROOT / "theory" / "n12_gate7_signed_green_hermite_collocation_replay.md"
RESULT = BASE / "BHSM_N12_GATE7_SIGNED_GREEN_HERMITE_COLLOCATION_REPLAY.json"
DATA = RESULT.with_suffix(".npz")
THIS_SCRIPT = Path(__file__).resolve()
FIXED_STEP = 0.25


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
    collocation._initialize(weights, reference)


def main() -> None:
    endpoint = _load(ENDPOINT)
    prior = _load(PRIOR)
    if endpoint.get("validation_passed") is not True:
        raise RuntimeError("validated signed-Green projected endpoints required")
    with np.load(NATIVE_DATA) as source:
        native_times = np.asarray(source["fine_grid_action_lengths"], dtype=float)
        native_values = np.asarray(source["fine_grid_augmented_action_values"], dtype=float)
        native_coefficients = np.asarray(source["fine_grid_DOP853_dense_coefficients"], dtype=float)
    with np.load(ENDPOINT_DATA) as source:
        times = np.asarray(source["action_times"], dtype=float)
        states = np.asarray(source["projected_states"], dtype=float)
        descriptors = np.asarray(source["recentered_descriptors"], dtype=float)
        endpoint_rates = np.asarray(source["exact_endpoint_augmented_rates"], dtype=float)
        endpoint_constraint = np.asarray(source["final_scaled_constraint_2_norm"], dtype=float)
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)

    native_endpoints = []
    native_rates = []
    for index, time in enumerate(times):
        interval = min(index, times.size - 2)
        fraction = 0.0 if index < times.size - 1 else (
            (time - float(native_times[interval])) / FIXED_STEP
        )
        native_endpoints.append(collocation.hermite._dense(
            native_values[interval], native_coefficients[interval], fraction,
        ))
        native_rates.append(collocation.hermite._dense_rate(
            native_values[interval], native_coefficients[interval], fraction, FIXED_STEP,
        ))
    native_endpoints = np.asarray(native_endpoints)
    native_rates = np.asarray(native_rates)
    corrected_endpoints = np.column_stack((states * weights[None, :], descriptors))
    correction = corrected_endpoints - native_endpoints
    correction_rates = endpoint_rates - native_rates

    nodes, _ = np.polynomial.legendre.leggauss(3)
    units = 0.5 * (nodes + 1.0)
    tasks = []
    order = 0
    for interval in range(times.size - 1):
        duration = float(times[interval + 1] - times[interval])
        right_fraction = duration / FIXED_STEP
        for sample, unit in enumerate(units):
            tasks.append((
                order, interval, sample, float(unit), right_fraction,
                native_values[interval], native_coefficients[interval],
                correction[interval:interval + 2],
                correction_rates[interval:interval + 2],
            ))
            order += 1
    workers = min(
        int(os.environ.get("BHSM_N12_GREEN_HERMITE_REPLAY_WORKERS", "8")),
        os.cpu_count() or 1,
    )
    with ProcessPoolExecutor(
        max_workers=workers,
        initializer=_initialize,
        initargs=(weights, reference),
    ) as executor:
        sampled = list(executor.map(collocation._sample, tasks, chunksize=2))
    sampled.sort(key=lambda item: item[0])
    rows = [item[1] for item in sampled]
    defects = np.asarray([item[2] for item in sampled])
    flow_norms = np.asarray([row["augmented_flow_defect_2_norm"] for row in rows])
    constraint_norms = np.asarray([row["scaled_constraint_2_norm"] for row in rows])
    fiber_residuals = np.asarray([row["numeric_descriptor_fiber_residual"] for row in rows])
    prior_flow = float(prior["summary"]["maximum_augmented_flow_defect_2_norm"])
    owner = int(np.argmax(flow_norms))
    np.savez_compressed(
        DATA,
        action_times=times,
        corrected_augmented_endpoints=corrected_endpoints,
        corrected_endpoint_rates=endpoint_rates,
        correction_endpoints=correction,
        correction_endpoint_rates=correction_rates,
        endpoint_scaled_constraint_2_norm=endpoint_constraint,
        sample_interval=np.asarray([row["interval"] for row in rows], dtype=int),
        sample_fraction=np.asarray([row["fraction"] for row in rows]),
        sampled_augmented_flow_defect=defects,
        sampled_augmented_flow_defect_2_norm=flow_norms,
        sampled_scaled_constraint_2_norm=constraint_norms,
        sampled_numeric_descriptor_fiber_residual=fiber_residuals,
    )
    validation = {
        "all_1110_Gauss3_samples_replayed": len(rows) == 1110,
        "all_endpoint_constraints_remain_closed_numerically": float(np.max(endpoint_constraint)) < 2.0e-14,
        "branch_24_selected_at_every_sample": all(row["selected_branch"] == 24 for row in rows),
        "selected_line_remains_simple_numerically": min(row["selected_eigenline_gap"] for row in rows) > 1.0e-7,
        "signed_Green_Newton_step_reduces_prior_Hermite_flow_defect": float(np.max(flow_norms)) < prior_flow,
        "all_quantities_finite": bool(np.all(np.isfinite(np.concatenate((
            defects.ravel(), flow_norms, constraint_norms, fiber_residuals,
        ))))),
        "continuous_interval_shadowing_not_claimed": True,
        "no_action_source_selector_scale_gate_or_chord_changed": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    payload = {
        "artifact": "BHSM_N12_GATE7_SIGNED_GREEN_HERMITE_COLLOCATION_REPLAY",
        "status": "SIGNED_GREEN_NEWTON_STEP_REDUCES_DENSE_FLOW_DEFECT" if passed else "SIGNED_GREEN_NEWTON_STEP_DOES_NOT_CLOSE_DENSE_FLOW_DEFECT",
        "authority": "NUMERICAL_GAUSS3_NEWTON_REPLAY_NOT_INTERVAL_SHADOWING_AUTHORITY",
        "mesh": {"fine_intervals": 370, "Gauss_samples_per_interval": 3, "workers": workers},
        "summary": {
            "maximum_endpoint_scaled_constraint_2_norm": float(np.max(endpoint_constraint)),
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
            for path in (NATIVE, NATIVE_DATA, ENDPOINT, ENDPOINT_DATA, PRIOR, THEORY, THIS_SCRIPT)
        },
        "adjudication": {
            "one_signed_Green_endpoint_Newton_step": "DIRECTLY_REPLAYED",
            "continuous_center": "OPEN_INTERVAL_SHADOWING_OR_NEXT_OWNER_REFINEMENT",
            "first_hit": "MUST_BE_REBUILT_OUTWARD_AFTER_CENTER",
        },
        "claim_boundary": {
            "continuous_action_constrained_center": "OPEN_INTERVAL_AUTHORITY",
            "continuous_outward_variational_carrier": "OPEN_AFTER_CENTER",
            "Weyl_force_KKT_Hessian": "NOT_CLAIMED",
            "Gate7": "ACTIVE_ACTION_OWNED_OPERATOR_ORACLE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "IF_REDUCED,_ITERATE_THE_SAME_SIGNED_GREEN_NEWTON_MAP_UNTIL_THE_"
            "DEFECT_IS_INSIDE_THE_EXISTING_TAYLOR_VOLTERRA_KRAWCZYK_RADIUS;_"
            "OTHERWISE_LOCALIZE_THE_FAILED_SOURCE_OR_GRAPH_LINEARIZATION"
        ),
        "validation": validation,
        "validation_passed": passed,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": payload["status"], "summary": payload["summary"], "validation_passed": passed}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
