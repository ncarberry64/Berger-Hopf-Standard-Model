"""Audit binary64 selected-descriptor reproducibility on the rejected step."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import materialize_n12_gate7_rate_consistent_newton_endpoint_candidate as candidate  # noqa: E402

BASE = ROOT / "artifacts" / "flagship_integration"
REJECTED = BASE / "BHSM_N12_GATE7_SECOND_RATE_CONSISTENT_NEWTON_ENDPOINT_CANDIDATE.json"
CORRELATED = BASE / "BHSM_N12_GATE7_CORRELATED_DESCRIPTOR_NEWTON_ENDPOINT_CANDIDATE.json"
RESULT = BASE / "BHSM_N12_GATE7_BINARY64_DESCRIPTOR_RESELECTION_REPRODUCIBILITY_AUDIT.json"
THIS_SCRIPT = Path(__file__).resolve()
NODES = (123, 124, 325, 326)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def main() -> None:
    with np.load(REJECTED.with_suffix(".npz")) as source:
        stored_states = np.asarray(source["projected_states"], dtype=float)
        stored_rates = np.asarray(source["exact_endpoint_augmented_rates"], dtype=float)
        stored_eigenvalues = np.asarray(source["numerical_selected_eigenvalues"], dtype=float)
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)
    with np.load(CORRELATED.with_suffix(".npz")) as source:
        rebuilt_states = np.asarray(source["projected_states"], dtype=float)
    rows = []
    for index in NODES:
        rate, eigenvalue, selected, gap = candidate._recentered_rate(
            rebuilt_states[index], weights, reference,
        )
        rows.append({
            "node": index,
            "state_absolute_maximum_difference": float(np.max(np.abs(rebuilt_states[index] - stored_states[index]))),
            "selected_eigenvalue_absolute_difference": abs(float(eigenvalue) - float(stored_eigenvalues[index])),
            "normalized_rate_2_norm_difference": float(np.linalg.norm(rate - stored_rates[index])),
            "recomputed_selected_branch": int(selected),
            "recomputed_selected_gap": float(gap),
        })
    maximum_state = max(row["state_absolute_maximum_difference"] for row in rows)
    maximum_eigenvalue = max(row["selected_eigenvalue_absolute_difference"] for row in rows)
    maximum_rate = max(row["normalized_rate_2_norm_difference"] for row in rows)
    validation = {
        "same_mathematical_endpoint_reconstructions_agree_near_binary64_roundoff": maximum_state < 2.0e-15,
        "selected_branch_remains_24": all(row["recomputed_selected_branch"] == 24 for row in rows),
        "selected_line_remains_simple_numerically": min(row["recomputed_selected_gap"] for row in rows) > 1.0e-7,
        "near_zero_selected_value_is_not_reproducible_at_its_signal_scale": maximum_eigenvalue > 1.0e-13,
        "normalized_reselected_rate_is_not_reproducible_at_Newton_residual_scale": maximum_rate > 1.0e-6,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    payload = {
        "artifact": "BHSM_N12_GATE7_BINARY64_DESCRIPTOR_RESELECTION_REPRODUCIBILITY_AUDIT",
        "status": "BINARY64_SELECTED_DESCRIPTOR_RESELECTION_REJECTED_AS_NEWTON_MAP_AUTHORITY",
        "authority": "DIRECT_REPLAY_DIAGNOSTIC_NOT_INTERVAL_AUTHORITY",
        "sampled_nodes": list(NODES),
        "rows": rows,
        "summary": {
            "maximum_state_absolute_difference": maximum_state,
            "maximum_selected_eigenvalue_absolute_difference": maximum_eigenvalue,
            "maximum_normalized_rate_2_norm_difference": maximum_rate,
        },
        "inputs": {_relative(path): _sha256(path) for path in (
            REJECTED, REJECTED.with_suffix(".npz"), CORRELATED,
            CORRELATED.with_suffix(".npz"), THIS_SCRIPT,
        )},
        "adjudication": {
            "binary64_selected_eigenvalue": "DIAGNOSTIC_ONLY",
            "Newton_descriptor_coordinate": "MUST_BE_CARRIED_AS_AN_INDEPENDENT_CORRELATED_VARIABLE_OR_OUTWARD_HIGH_PRECISION_OBJECT",
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": payload["status"], "summary": payload["summary"], "validation_passed": payload["validation_passed"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
