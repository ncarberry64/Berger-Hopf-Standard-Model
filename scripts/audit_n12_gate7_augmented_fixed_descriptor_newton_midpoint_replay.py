"""Replay all augmented fixed-descriptor Hermite--Simpson midpoint fields."""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
import argparse
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
PARENT = BASE / "BHSM_N12_GATE7_CORRELATED_DESCRIPTOR_NEWTON_MIDPOINT_REPLAY.json"
ENDPOINT = BASE / "BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_NEWTON_ENDPOINT_CANDIDATE.json"
THEORY = ROOT / "theory" / "n12_gate7_augmented_fixed_descriptor_newton.md"
RESULT = BASE / "BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_NEWTON_MIDPOINT_REPLAY.json"
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


def _node(task: tuple[int, np.ndarray, float]) -> tuple[int, np.ndarray, float, int, float, float]:
    index, state, supplied = task
    weights = np.asarray(collocation._WORK["weights"])
    reference = np.asarray(collocation._WORK["reference"])
    rate, value = collocation._field(state, supplied, weights, reference)
    cancelled_norm = float(np.linalg.norm(np.asarray(value["cancelled_field_action"], dtype=float)))
    return (
        index,
        rate,
        float(value["numeric_selected_eigenvalue_not_used_as_descriptor"]),
        int(value["selected_branch"]),
        float(value["selected_eigenline_gap"]),
        cancelled_norm,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=min(4, os.cpu_count() or 1))
    args = parser.parse_args()
    parent = _load(PARENT)
    endpoint = _load(ENDPOINT)
    if parent.get("validation_passed") is not True or endpoint.get("validation_passed") is not True:
        raise RuntimeError("validated correlated replay and augmented endpoint candidate required")
    with np.load(ENDPOINT.with_suffix(".npz")) as source:
        parameters = np.asarray(source["collocation_arc_parameters"], dtype=float)
        states = np.asarray(source["projected_states"], dtype=float)
        descriptors = np.asarray(source["independent_signed_descriptors"], dtype=float)
        endpoint_rates = np.asarray(source["exact_endpoint_augmented_rates"], dtype=float)
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)
    endpoints = np.column_stack((states * weights[None, :], descriptors))
    durations = np.diff(parameters)
    midpoints = 0.5 * (endpoints[:-1] + endpoints[1:]) + durations[:, None] * (
        endpoint_rates[:-1] - endpoint_rates[1:]
    ) / 8.0
    if float(np.min(midpoints[:, -1])) < 0.0:
        raise ArithmeticError("augmented midpoint descriptor left the pre-stop domain")
    tasks = [(i, midpoints[i, :-1] / weights, float(midpoints[i, -1])) for i in range(370)]
    rows = []
    with ProcessPoolExecutor(
        max_workers=args.workers,
        initializer=collocation._initialize,
        initargs=(weights, reference),
    ) as executor:
        for count, row in enumerate(executor.map(_node, tasks, chunksize=1), 1):
            rows.append(row)
            if count % 32 == 0 or count == len(tasks):
                print(json.dumps({"completed": count, "total": len(tasks), "interval": int(row[0])}), flush=True)
    rows.sort(key=lambda item: int(item[0]))
    midpoint_rates = np.asarray([row[1] for row in rows])
    diagnostic_eigenvalues = np.asarray([row[2] for row in rows])
    branches = np.asarray([row[3] for row in rows], dtype=int)
    gaps = np.asarray([row[4] for row in rows])
    midpoint_cancelled_norms = np.asarray([row[5] for row in rows])
    midpoint_constraints = np.asarray([
        collocation.constraints._scaled_residual(midpoints[i, :-1] / weights, weights)[0]
        for i in range(370)
    ])
    diagnostic_fiber_residual = diagnostic_eigenvalues - midpoints[:, -1]
    residual = endpoints[1:] - endpoints[:-1] - durations[:, None] * (
        endpoint_rates[:-1] + 4.0 * midpoint_rates + endpoint_rates[1:]
    ) / 6.0
    norms = np.linalg.norm(residual, axis=1)
    state_norms = np.linalg.norm(residual[:, :-1], axis=1)
    descriptor_residual = np.abs(residual[:, -1])
    parent_maximum = float(parent["summary"]["maximum_Hermite_Simpson_shooting_residual_2_norm"])
    maximum = float(np.max(norms))
    reduction = parent_maximum / maximum
    np.savez_compressed(
        DATA,
        collocation_arc_parameters=parameters,
        augmented_endpoints=endpoints,
        exact_endpoint_augmented_rates=endpoint_rates,
        midpoint_augmented_action_values=midpoints,
        exact_midpoint_augmented_rates=midpoint_rates,
        exact_midpoint_cancelled_field_action_norm=midpoint_cancelled_norms,
        midpoint_scaled_constraint_2_norm=midpoint_constraints,
        numerical_midpoint_descriptor_fiber_residual_diagnostic_only=diagnostic_fiber_residual,
        Hermite_Simpson_shooting_residual=residual,
        Hermite_Simpson_shooting_residual_2_norm=norms,
        state_shooting_residual_2_norm=state_norms,
        descriptor_shooting_residual_absolute=descriptor_residual,
        state_weights=weights,
        branch_reference=reference,
    )
    validation = {
        "all_370_fixed_descriptor_midpoint_fields_replayed": midpoint_rates.shape == (370, 99),
        "branch_24_selected_at_every_midpoint_diagnostically": bool(np.all(branches == 24)),
        "selected_line_remains_simple_numerically": float(np.min(gaps)) > 1.0e-7,
        "all_midpoint_constraints_close_numerically": float(np.max(midpoint_constraints)) < 5.0e-14,
        "all_independent_descriptors_remain_nonnegative": float(np.min(midpoints[:, -1])) >= 0.0,
        "all_midpoint_cancelled_norms_are_positive": float(np.min(midpoint_cancelled_norms)) > 0.0,
        "augmented_fixed_descriptor_step_reduces_nonlinear_Hermite_Simpson_residual": reduction > 1.0,
        "binary64_eigenvalues_not_used_as_descriptor_authority": True,
        "collocation_abscissae_are_not_labeled_proper_time": True,
        "all_quantities_finite": bool(np.all(np.isfinite(np.concatenate((midpoints.ravel(), midpoint_rates.ravel(), residual.ravel()))))),
        "continuous_interval_shadowing_not_claimed": True,
        "no_action_source_selector_scale_gate_or_chord_changed": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    payload = {
        "artifact": "BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_NEWTON_MIDPOINT_REPLAY",
        "status": "AUGMENTED_FIXED_DESCRIPTOR_STEP_REDUCES_NONLINEAR_RESIDUAL" if passed else "AUGMENTED_FIXED_DESCRIPTOR_STEP_DOES_NOT_REDUCE_NONLINEAR_RESIDUAL",
        "authority": "NUMERICAL_FIXED_DESCRIPTOR_EXACT_FIELD_REPLAY_NOT_INTERVAL_AUTHORITY",
        "mesh": {"shooting_intervals": 370, "augmented_dimension": 99, "correction_dimension": 74, "workers": args.workers},
        "parameterization": {"stored_abscissa": "NORMALIZED_CANCELLED_FIELD_ARC_COLLOCATION_PARAMETER", "proper_time": "REQUIRES_CERTIFIED_DENSITY_PULLBACK"},
        "summary": {
            "maximum_Hermite_Simpson_shooting_residual_2_norm": maximum,
            "maximum_Hermite_Simpson_shooting_residual_owner_interval": int(np.argmax(norms)),
            "parent_maximum_Hermite_Simpson_shooting_residual_2_norm": parent_maximum,
            "nonlinear_block_residual_reduction_factor": reduction,
            "maximum_state_shooting_residual_2_norm": float(np.max(state_norms)),
            "maximum_descriptor_shooting_residual_absolute": float(np.max(descriptor_residual)),
            "maximum_midpoint_scaled_constraint_2_norm": float(np.max(midpoint_constraints)),
            "minimum_independent_midpoint_descriptor": float(np.min(midpoints[:, -1])),
            "minimum_midpoint_cancelled_field_action_norm": float(np.min(midpoint_cancelled_norms)),
            "maximum_numeric_midpoint_descriptor_fiber_residual_diagnostic_only": float(np.max(np.abs(diagnostic_fiber_residual))),
            "minimum_selected_eigenline_gap": float(np.min(gaps)),
        },
        "data": _relative(DATA),
        "data_SHA256": _sha256(DATA),
        "inputs": {_relative(path): _sha256(path) for path in (
            PARENT, ENDPOINT, ENDPOINT.with_suffix(".npz"), THEORY, THIS_SCRIPT,
        )},
        "adjudication": {
            "binary64_descriptor_reselection": "REJECTED_AND_NONAUTHORITATIVE",
            "independent_signed_descriptor_augmented_step": "ACCEPTED_FOR_NEXT_ITERATION" if passed else "REJECTED_BY_EXACT_NONLINEAR_REPLAY",
        },
        "claim_boundary": {
            "descriptor_fiber_transport": "FIRST_ORDER_NUMERICAL_CANDIDATE",
            "nonlinear_Hermite_Simpson_center": "OPEN_ITERATION_AND_INTERVAL_AUTHORITY",
            "proper_time_and_Weyl_first_jet": "OPEN_72D_RESET_HISTORY_COMPOSITION",
            "continuous_action_constrained_center": "OPEN",
            "Gate7": "ACTIVE_ACTION_OWNED_OPERATOR_ORACLE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "IF_REDUCED,_REBUILD_THE_74D_AUGMENTED_RESIDUAL_DERIVATIVE_ON_THIS_CENTER;_"
            "DO_NOT_RESELECT_BINARY64_EIGENVALUES_OR_CALL_ARC_PARAMETERS_PROPER_TIME"
        ),
        "validation": validation,
        "validation_passed": passed,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": payload["status"], "summary": payload["summary"], "validation_passed": passed}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
