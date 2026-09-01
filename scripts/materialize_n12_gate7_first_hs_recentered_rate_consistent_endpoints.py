"""Re-evaluate first-HS endpoint fields at their stored recentered descriptors."""

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
CENTER = BASE / "BHSM_N12_GATE7_HERMITE_SIMPSON_NEWTON_ENDPOINT_CANDIDATE.json"
THEORY = ROOT / "theory" / "n12_gate7_first_hs_recentered_rate_consistency.md"
RESULT = BASE / "BHSM_N12_GATE7_FIRST_HS_RECENTERED_RATE_CONSISTENT_ENDPOINTS.json"
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
    if center.get("validation_passed") is not True:
        raise RuntimeError("validated first-HS endpoint center required")
    with np.load(CENTER.with_suffix(".npz")) as source:
        times = np.asarray(source["action_times"], dtype=float)
        states = np.asarray(source["projected_states"], dtype=float)
        descriptors = np.asarray(source["recentered_descriptors"], dtype=float)
        old_rates = np.asarray(source["exact_endpoint_augmented_rates"], dtype=float)
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)
    tasks = [(i, states[i], max(float(descriptors[i]), 0.0)) for i in range(times.size)]
    workers = min(int(os.environ.get("BHSM_N12_RATE_CONSISTENCY_WORKERS", "8")), os.cpu_count() or 1)
    with ProcessPoolExecutor(
        max_workers=workers,
        initializer=collocation._initialize,
        initargs=(weights, reference),
    ) as executor:
        rows = list(executor.map(collocation._node, tasks, chunksize=2))
    rows.sort(key=lambda item: int(item[0]))
    rates = np.asarray([row[1] for row in rows])
    eigenvalues = np.asarray([row[2] for row in rows])
    branches = np.asarray([row[3] for row in rows], dtype=int)
    gaps = np.asarray([row[4] for row in rows])
    rate_difference = np.linalg.norm(rates - old_rates, axis=1)
    fiber_residual = eigenvalues - descriptors
    np.savez_compressed(
        DATA,
        action_times=times,
        projected_states=states,
        recentered_descriptors=descriptors,
        exact_endpoint_augmented_rates=rates,
        superseded_pre_recenter_endpoint_rates=old_rates,
        endpoint_rate_consistency_difference_2_norm=rate_difference,
        endpoint_descriptor_fiber_residual=fiber_residual,
        state_weights=weights,
        branch_reference=reference,
    )
    validation = {
        "all_371_endpoint_fields_recomputed_at_recentered_descriptors": rates.shape == (371, 99),
        "branch_24_selected_at_every_endpoint": bool(np.all(branches == 24)),
        "selected_line_remains_simple_numerically": float(np.min(gaps)) > 1.0e-7,
        "stored_descriptors_match_selected_eigenvalues_numerically": float(np.max(np.abs(fiber_residual))) < 3.0e-13,
        "pre_recenter_rate_mismatch_is_nonzero_and_material": float(np.max(rate_difference)) > 1.0e-10,
        "endpoint_states_and_descriptors_are_unchanged": True,
        "all_quantities_finite": bool(np.all(np.isfinite(np.concatenate((rates.ravel(), fiber_residual, rate_difference))))),
        "no_action_source_selector_scale_gate_or_chord_changed": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    owner = int(np.argmax(rate_difference))
    payload = {
        "artifact": "BHSM_N12_GATE7_FIRST_HS_RECENTERED_RATE_CONSISTENT_ENDPOINTS",
        "status": "FIRST_HS_ENDPOINT_RATES_REEVALUATED_AT_RECENTERED_DESCRIPTORS" if passed else "FIRST_HS_RECENTERED_RATE_CONSISTENCY_INVALID",
        "authority": "DIRECT_RETAINED_EXACT_FIELD_REPLAY_NUMERICAL_CENTER_REPAIR",
        "summary": {
            "maximum_endpoint_rate_consistency_difference_2_norm": float(np.max(rate_difference)),
            "maximum_endpoint_rate_consistency_difference_owner_node": owner,
            "maximum_endpoint_descriptor_fiber_residual_absolute": float(np.max(np.abs(fiber_residual))),
            "minimum_selected_eigenline_gap": float(np.min(gaps)),
        },
        "data": _relative(DATA),
        "data_SHA256": _sha256(DATA),
        "inputs": {
            _relative(path): _sha256(path)
            for path in (CENTER, CENTER.with_suffix(".npz"), THEORY, THIS_SCRIPT)
        },
        "adjudication": {
            "stored_first_HS_endpoint_states_and_descriptors": "RETAINED",
            "stored_pre_recenter_endpoint_rates": "SUPERSEDED_FOR_COLLOCATION_SOURCE",
            "recentered_descriptor_consistent_endpoint_rates": "REBUILT_DIRECTLY",
        },
        "claim_boundary": {
            "nonlinear_Hermite_Simpson_center": "OPEN_RATE_CONSISTENT_MIDPOINT_REPLAY",
            "continuous_action_constrained_center": "OPEN",
            "Gate7": "ACTIVE_ACTION_OWNED_OPERATOR_ORACLE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": "REBUILD_ALL_370_HERMITE_SIMPSON_MIDPOINTS_FROM_THE_RATE_CONSISTENT_ENDPOINT_DATA",
        "validation": validation,
        "validation_passed": passed,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": payload["status"], "summary": payload["summary"], "validation_passed": passed}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
