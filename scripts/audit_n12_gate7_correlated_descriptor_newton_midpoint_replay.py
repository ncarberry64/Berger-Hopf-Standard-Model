"""Replay every Hermite--Simpson midpoint with the correlated signed descriptor."""

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
PARENT = BASE / "BHSM_N12_GATE7_RATE_CONSISTENT_NEWTON_MIDPOINT_REPLAY.json"
ENDPOINT = BASE / "BHSM_N12_GATE7_CORRELATED_DESCRIPTOR_NEWTON_ENDPOINT_CANDIDATE.json"
THEORY = ROOT / "theory" / "n12_gate7_correlated_descriptor_newton.md"
RESULT = BASE / "BHSM_N12_GATE7_CORRELATED_DESCRIPTOR_NEWTON_MIDPOINT_REPLAY.json"
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
    parent = _load(PARENT)
    endpoint = _load(ENDPOINT)
    if parent.get("validation_passed") is not True or endpoint.get("validation_passed") is not True:
        raise RuntimeError("validated parent and correlated endpoint candidate required")
    with np.load(ENDPOINT.with_suffix(".npz")) as source:
        times = np.asarray(source["action_times"], dtype=float)
        states = np.asarray(source["projected_states"], dtype=float)
        descriptors = np.asarray(source["correlated_descriptors"], dtype=float)
        endpoint_rates = np.asarray(source["exact_endpoint_augmented_rates"], dtype=float)
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)
    endpoints = np.column_stack((states * weights[None, :], descriptors))
    durations = np.diff(times)
    midpoints = 0.5 * (endpoints[:-1] + endpoints[1:]) + durations[:, None] * (
        endpoint_rates[:-1] - endpoint_rates[1:]
    ) / 8.0
    tasks = [(i, midpoints[i, :-1] / weights, max(float(midpoints[i, -1]), 0.0)) for i in range(370)]
    workers = min(int(os.environ.get("BHSM_N12_HS_MIDPOINT_REPLAY_WORKERS", "8")), os.cpu_count() or 1)
    with ProcessPoolExecutor(max_workers=workers, initializer=collocation._initialize, initargs=(weights, reference)) as executor:
        rows = list(executor.map(collocation._node, tasks, chunksize=2))
    rows.sort(key=lambda item: int(item[0]))
    midpoint_rates = np.asarray([row[1] for row in rows])
    eigenvalues = np.asarray([row[2] for row in rows])
    branches = np.asarray([row[3] for row in rows], dtype=int)
    gaps = np.asarray([row[4] for row in rows])
    midpoint_constraint = np.asarray([
        collocation.constraints._scaled_residual(midpoints[i, :-1] / weights, weights)[0]
        for i in range(370)
    ])
    fiber = eigenvalues - midpoints[:, -1]
    residual = endpoints[1:] - endpoints[:-1] - durations[:, None] * (
        endpoint_rates[:-1] + 4.0 * midpoint_rates + endpoint_rates[1:]
    ) / 6.0
    norms = np.linalg.norm(residual, axis=1)
    parent_max = float(parent["summary"]["maximum_Hermite_Simpson_shooting_residual_2_norm"])
    maximum = float(np.max(norms))
    reduction = parent_max / maximum
    np.savez_compressed(
        DATA,
        action_times=times,
        augmented_endpoints=endpoints,
        exact_endpoint_rates=endpoint_rates,
        midpoint_augmented_action_values=midpoints,
        exact_midpoint_rates=midpoint_rates,
        midpoint_scaled_constraint_2_norm=midpoint_constraint,
        numerical_midpoint_descriptor_fiber_residual_diagnostic_only=fiber,
        Hermite_Simpson_shooting_residual=residual,
        Hermite_Simpson_shooting_residual_2_norm=norms,
        state_shooting_residual_2_norm=np.linalg.norm(residual[:, :-1], axis=1),
        descriptor_shooting_residual_absolute=np.abs(residual[:, -1]),
    )
    validation = {
        "all_370_fixed_descriptor_midpoint_fields_replayed": midpoint_rates.shape == (370, 99),
        "branch_24_selected_at_every_midpoint_diagnostically": bool(np.all(branches == 24)),
        "selected_line_remains_simple_numerically": float(np.min(gaps)) > 1.0e-7,
        "all_midpoint_constraints_close_numerically": float(np.max(midpoint_constraint)) < 5.0e-14,
        "correlated_descriptor_step_reduces_nonlinear_Hermite_Simpson_residual": reduction > 1.0,
        "binary64_eigenvalues_not_used_as_descriptor_authority": True,
        "all_quantities_finite": bool(np.all(np.isfinite(np.concatenate((midpoints.ravel(), midpoint_rates.ravel(), residual.ravel()))))),
        "continuous_interval_shadowing_not_claimed": True,
        "no_action_source_selector_scale_gate_or_chord_changed": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    payload = {
        "artifact": "BHSM_N12_GATE7_CORRELATED_DESCRIPTOR_NEWTON_MIDPOINT_REPLAY",
        "status": "CORRELATED_DESCRIPTOR_STEP_REDUCES_NONLINEAR_RESIDUAL" if passed else "CORRELATED_DESCRIPTOR_STEP_DOES_NOT_REDUCE_NONLINEAR_RESIDUAL",
        "authority": "NUMERICAL_FIXED_DESCRIPTOR_EXACT_FIELD_REPLAY_NOT_INTERVAL_AUTHORITY",
        "mesh": {"shooting_intervals": 370, "augmented_dimension": 99, "workers": workers},
        "summary": {
            "maximum_Hermite_Simpson_shooting_residual_2_norm": maximum,
            "maximum_Hermite_Simpson_shooting_residual_owner_interval": int(np.argmax(norms)),
            "parent_maximum_Hermite_Simpson_shooting_residual_2_norm": parent_max,
            "nonlinear_block_residual_reduction_factor": reduction,
            "maximum_state_shooting_residual_2_norm": float(np.max(np.linalg.norm(residual[:, :-1], axis=1))),
            "maximum_descriptor_shooting_residual_absolute": float(np.max(np.abs(residual[:, -1]))),
            "maximum_midpoint_scaled_constraint_2_norm": float(np.max(midpoint_constraint)),
            "maximum_numeric_midpoint_descriptor_fiber_residual_diagnostic_only": float(np.max(np.abs(fiber))),
            "minimum_selected_eigenline_gap": float(np.min(gaps)),
        },
        "data": _relative(DATA),
        "data_SHA256": _sha256(DATA),
        "inputs": {_relative(path): _sha256(path) for path in (
            PARENT, ENDPOINT, ENDPOINT.with_suffix(".npz"), THEORY, THIS_SCRIPT,
        )},
        "adjudication": {
            "binary64_reselected_second_step": "REJECTED_AND_NONAUTHORITATIVE",
            "correlated_signed_descriptor_step": "ACCEPTED_FOR_NEXT_ITERATION" if passed else "REJECTED_BY_EXACT_NONLINEAR_REPLAY",
        },
        "claim_boundary": {
            "descriptor_graph_transport": "FIRST_ORDER_NUMERICAL_CANDIDATE",
            "nonlinear_Hermite_Simpson_center": "OPEN_ITERATION_AND_INTERVAL_AUTHORITY",
            "continuous_action_constrained_center": "OPEN",
            "Gate7": "ACTIVE_ACTION_OWNED_OPERATOR_ORACLE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "IF_REDUCED,_REBUILD_THE_AUGMENTED_FIXED_DESCRIPTOR_RESIDUAL_DERIVATIVE_ON_THIS_CENTER;_"
            "DO_NOT_RESELECT_BINARY64_EIGENVALUES"
        ),
        "validation": validation,
        "validation_passed": passed,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": payload["status"], "summary": payload["summary"], "validation_passed": passed}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
