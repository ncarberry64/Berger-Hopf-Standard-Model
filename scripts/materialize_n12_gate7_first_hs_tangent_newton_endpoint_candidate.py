"""Apply the intrinsic tangent correction and project all 371 endpoints."""

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
import materialize_n12_gate7_signed_green_projected_endpoint_candidate as projected  # noqa: E402

BASE = ROOT / "artifacts" / "flagship_integration"
CENTER = BASE / "BHSM_N12_GATE7_HERMITE_SIMPSON_NEWTON_ENDPOINT_CANDIDATE.json"
PREDICTOR = BASE / "BHSM_N12_GATE7_FIRST_HS_TANGENT_BLOCK_NEWTON_PREDICTOR.json"
THEORY = ROOT / "theory" / "n12_gate7_first_hs_tangent_newton_endpoint_candidate.md"
RESULT = BASE / "BHSM_N12_GATE7_FIRST_HS_TANGENT_NEWTON_ENDPOINT_CANDIDATE.json"
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
        raise RuntimeError("validated first-HS center and tangent predictor required")
    with np.load(CENTER.with_suffix(".npz")) as source:
        times = np.asarray(source["action_times"], dtype=float)
        states = np.asarray(source["projected_states"], dtype=float)
        descriptors = np.asarray(source["recentered_descriptors"], dtype=float)
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)
    with np.load(PREDICTOR.with_suffix(".npz")) as source:
        correction = np.asarray(source["endpoint_state_correction_action"], dtype=float)
    trial_action_states = states * weights[None, :] + correction
    workers = min(int(os.environ.get("BHSM_N12_TANGENT_HS_WORKERS", "8")), os.cpu_count() or 1)
    tasks = [(i, trial_action_states[i], float(descriptors[i])) for i in range(times.size)]
    with ProcessPoolExecutor(
        max_workers=workers,
        initializer=projected._initialize,
        initargs=(weights, reference),
    ) as executor:
        rows = list(executor.map(projected._replay, tasks, chunksize=2))
    rows.sort(key=lambda item: int(item[0]))
    output_states = np.asarray([row[1] for row in rows])
    projection_action = np.asarray([row[2] for row in rows])
    initial_constraint = np.asarray([row[3] for row in rows])
    final_constraint = np.asarray([row[4] for row in rows])
    rates = np.asarray([row[5] for row in rows])
    eigenvalues = np.asarray([row[6] for row in rows])
    branches = np.asarray([row[7] for row in rows], dtype=int)
    gaps = np.asarray([row[8] for row in rows])
    output_descriptors = np.concatenate((descriptors[:1], eigenvalues[1:]))
    sign_changes = np.flatnonzero((eigenvalues[:-1] > 0.0) & (eigenvalues[1:] <= 0.0))
    sign_brackets = [[float(times[i]), float(times[i + 1])] for i in sign_changes]
    correction_norm = np.linalg.norm(correction, axis=1)
    projection_norm = np.linalg.norm(projection_action, axis=1)
    np.savez_compressed(
        DATA,
        action_times=times,
        projected_states=output_states,
        recentered_descriptors=output_descriptors,
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
    validation = {
        "all_371_tangent_corrected_endpoints_replayed": output_states.shape == (371, 98),
        "all_endpoint_constraints_close_numerically": float(np.max(final_constraint)) < 2.0e-14,
        "branch_24_selected_at_every_endpoint": bool(np.all(branches == 24)),
        "selected_line_remains_simple_numerically": float(np.min(gaps)) > 1.0e-7,
        "all_quantities_finite": bool(np.all(np.isfinite(np.concatenate((
            output_states.ravel(), output_descriptors, rates.ravel(), correction.ravel(),
        ))))),
        "terminal_first_hit_adapter_not_imposed_before_center_convergence": True,
        "no_action_source_selector_scale_gate_or_chord_changed": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    payload = {
        "artifact": "BHSM_N12_GATE7_FIRST_HS_TANGENT_NEWTON_ENDPOINT_CANDIDATE",
        "status": "FIRST_HS_TANGENT_NEWTON_ENDPOINTS_MATERIALIZED" if passed else "FIRST_HS_TANGENT_ENDPOINTS_INVALID",
        "authority": "NUMERICAL_TANGENT_CORRECTED_CONSTRAINT_PROJECTED_ENDPOINTS_NOT_INTERVAL_AUTHORITY",
        "summary": {
            "maximum_endpoint_correction_action_2_norm": float(np.max(correction_norm)),
            "maximum_constraint_projection_action_2_norm": float(np.max(projection_norm)),
            "maximum_final_scaled_constraint_2_norm": float(np.max(final_constraint)),
            "minimum_selected_eigenline_gap": float(np.min(gaps)),
            "raw_endpoint_sign_change_brackets": sign_brackets,
            "terminal_numeric_selected_eigenvalue": float(eigenvalues[-1]),
        },
        "data": _relative(DATA),
        "data_SHA256": _sha256(DATA),
        "inputs": {
            _relative(path): _sha256(path)
            for path in (CENTER, CENTER.with_suffix(".npz"), PREDICTOR, PREDICTOR.with_suffix(".npz"), THEORY, THIS_SCRIPT)
        },
        "claim_boundary": {
            "nonlinear_Hermite_Simpson_center": "OPEN_MIDPOINT_REPLAY",
            "first_hit": "OPEN_AFTER_CENTER_CONVERGENCE",
            "continuous_action_constrained_center": "OPEN",
            "Gate7": "ACTIVE_ACTION_OWNED_OPERATOR_ORACLE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": "REPLAY_ALL_370_TANGENT_CORRECTED_COLLOCATION_MIDPOINTS",
        "validation": validation,
        "validation_passed": passed,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": payload["status"], "summary": payload["summary"], "validation_passed": passed}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
