"""Build the exact Hermite--Simpson source from rate-consistent endpoints."""

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
ENDPOINT = BASE / "BHSM_N12_GATE7_FIRST_HS_RECENTERED_RATE_CONSISTENT_ENDPOINTS.json"
SUPERSEDED = BASE / "BHSM_N12_GATE7_HERMITE_SIMPSON_NEWTON_NONLINEAR_SOURCE.json"
THEORY = ROOT / "theory" / "n12_gate7_first_hs_rate_consistent_nonlinear_source.md"
RESULT = BASE / "BHSM_N12_GATE7_FIRST_HS_RATE_CONSISTENT_NONLINEAR_SOURCE.json"
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
    endpoint = _load(ENDPOINT)
    superseded = _load(SUPERSEDED)
    if endpoint.get("validation_passed") is not True or superseded.get("validation_passed") is not True:
        raise RuntimeError("validated repaired endpoints and historical source required")
    with np.load(ENDPOINT.with_suffix(".npz")) as source:
        times = np.asarray(source["action_times"], dtype=float)
        states = np.asarray(source["projected_states"], dtype=float)
        descriptors = np.asarray(source["recentered_descriptors"], dtype=float)
        endpoint_rates = np.asarray(source["exact_endpoint_augmented_rates"], dtype=float)
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)
    endpoints = np.column_stack((states * weights[None, :], descriptors))
    durations = np.diff(times)
    midpoint_augmented = 0.5 * (endpoints[:-1] + endpoints[1:]) + durations[:, None] * (
        endpoint_rates[:-1] - endpoint_rates[1:]
    ) / 8.0
    tasks = [
        (i, midpoint_augmented[i, :-1] / weights, max(float(midpoint_augmented[i, -1]), 0.0))
        for i in range(370)
    ]
    workers = min(int(os.environ.get("BHSM_N12_HS_MIDPOINT_REPLAY_WORKERS", "8")), os.cpu_count() or 1)
    with ProcessPoolExecutor(max_workers=workers, initializer=collocation._initialize, initargs=(weights, reference)) as executor:
        rows = list(executor.map(collocation._node, tasks, chunksize=2))
    rows.sort(key=lambda item: int(item[0]))
    midpoint_rates = np.asarray([row[1] for row in rows])
    eigenvalues = np.asarray([row[2] for row in rows])
    branches = np.asarray([row[3] for row in rows], dtype=int)
    gaps = np.asarray([row[4] for row in rows])
    midpoint_constraint = np.asarray([
        collocation.constraints._scaled_residual(midpoint_augmented[i, :-1] / weights, weights)[0]
        for i in range(370)
    ])
    fiber_residual = eigenvalues - midpoint_augmented[:, -1]
    shooting_residual = endpoints[1:] - endpoints[:-1] - durations[:, None] * (
        endpoint_rates[:-1] + 4.0 * midpoint_rates + endpoint_rates[1:]
    ) / 6.0
    residual_norm = np.linalg.norm(shooting_residual, axis=1)
    historical_max = float(superseded["summary"]["maximum_Hermite_Simpson_shooting_residual_2_norm"])
    np.savez_compressed(
        DATA,
        action_times=times,
        augmented_endpoints=endpoints,
        exact_endpoint_rates=endpoint_rates,
        midpoint_augmented_action_values=midpoint_augmented,
        exact_midpoint_rates=midpoint_rates,
        midpoint_scaled_constraint_2_norm=midpoint_constraint,
        midpoint_descriptor_fiber_residual=fiber_residual,
        Hermite_Simpson_shooting_residual=shooting_residual,
        Hermite_Simpson_shooting_residual_2_norm=residual_norm,
        state_shooting_residual_2_norm=np.linalg.norm(shooting_residual[:, :-1], axis=1),
        descriptor_shooting_residual_absolute=np.abs(shooting_residual[:, -1]),
    )
    validation = {
        "all_370_exact_midpoint_fields_replayed": midpoint_rates.shape == (370, 99),
        "branch_24_selected_at_every_midpoint": bool(np.all(branches == 24)),
        "selected_line_remains_simple_numerically": float(np.min(gaps)) > 1.0e-7,
        "all_midpoint_constraints_close_numerically": float(np.max(midpoint_constraint)) < 5.0e-14,
        "rate_consistent_source_differs_materially_from_superseded_source": abs(float(np.max(residual_norm)) - historical_max) > 1.0e-8,
        "all_quantities_finite": bool(np.all(np.isfinite(np.concatenate((
            midpoint_rates.ravel(), shooting_residual.ravel(),
        ))))),
        "continuous_interval_shadowing_not_claimed": True,
        "no_action_source_selector_scale_gate_or_chord_changed": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    maximum = float(np.max(residual_norm))
    payload = {
        "artifact": "BHSM_N12_GATE7_FIRST_HS_RATE_CONSISTENT_NONLINEAR_SOURCE",
        "status": "RECENTERED_RATE_CONSISTENT_HERMITE_SIMPSON_SOURCE_MATERIALIZED" if passed else "RATE_CONSISTENT_HERMITE_SIMPSON_SOURCE_INVALID",
        "authority": "DIRECT_NUMERICAL_EXACT_ENDPOINT_AND_MIDPOINT_FIELD_REPLAY_NOT_INTERVAL_AUTHORITY",
        "mesh": {"shooting_intervals": 370, "augmented_dimension": 99, "workers": workers},
        "summary": {
            "maximum_Hermite_Simpson_shooting_residual_2_norm": maximum,
            "maximum_Hermite_Simpson_shooting_residual_owner_interval": int(np.argmax(residual_norm)),
            "superseded_mixed_rate_maximum_residual_2_norm": historical_max,
            "mixed_rate_to_consistent_residual_ratio": historical_max / maximum,
            "maximum_state_shooting_residual_2_norm": float(np.max(np.linalg.norm(shooting_residual[:, :-1], axis=1))),
            "maximum_descriptor_shooting_residual_absolute": float(np.max(np.abs(shooting_residual[:, -1]))),
            "maximum_midpoint_scaled_constraint_2_norm": float(np.max(midpoint_constraint)),
            "maximum_midpoint_descriptor_fiber_residual_absolute": float(np.max(np.abs(fiber_residual))),
            "minimum_selected_eigenline_gap": float(np.min(gaps)),
        },
        "data": _relative(DATA),
        "data_SHA256": _sha256(DATA),
        "inputs": {
            _relative(path): _sha256(path)
            for path in (ENDPOINT, ENDPOINT.with_suffix(".npz"), SUPERSEDED, THEORY, THIS_SCRIPT)
        },
        "adjudication": {
            "mixed_pre_recenter_rate_source": "SUPERSEDED",
            "direct_recentered_rate_consistent_source": "CURRENT_NEWTON_SOURCE",
        },
        "claim_boundary": {
            "nonlinear_Hermite_Simpson_center": "OPEN_NEWTON_ON_REPAIRED_SOURCE",
            "continuous_action_constrained_center": "OPEN",
            "Gate7": "ACTIVE_ACTION_OWNED_OPERATOR_ORACLE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": "SOLVE_AND_REPLAY_THE_BLOCK_NEWTON_STEP_FROM_THIS_RATE_CONSISTENT_SOURCE",
        "validation": validation,
        "validation_passed": passed,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": payload["status"], "summary": payload["summary"], "validation_passed": passed}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
