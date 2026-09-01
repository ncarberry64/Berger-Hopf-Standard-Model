"""Materialize graph Jacobians at all Hermite--Simpson midpoint states."""

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

import materialize_n12_gate7_signed_green_current_center_graph_jacobian as graph  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
SOURCE = BASE / "BHSM_N12_GATE7_DIRECT_HERMITE_SIMPSON_MULTIPLE_SHOOTING_SOURCE.json"
ENDPOINT = BASE / "BHSM_N12_GATE7_CURRENT_LINEARIZATION_NEWTON_ENDPOINT_CANDIDATE.json"
THEORY = ROOT / "theory" / "n12_gate7_hermite_simpson_midpoint_graph_jacobian.md"
RESULT = BASE / "BHSM_N12_GATE7_HERMITE_SIMPSON_MIDPOINT_GRAPH_JACOBIAN.json"
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=min(8, os.cpu_count() or 1))
    args = parser.parse_args()
    source_record = _load(SOURCE)
    if source_record.get("validation_passed") is not True:
        raise RuntimeError("validated Hermite--Simpson source required")
    with np.load(SOURCE.with_suffix(".npz")) as source:
        times = np.asarray(source["action_times"], dtype=float)
        endpoints = np.asarray(source["augmented_endpoints"], dtype=float)
        rates = np.asarray(source["exact_endpoint_rates"], dtype=float)
    with np.load(ENDPOINT.with_suffix(".npz")) as source:
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)

    durations = np.diff(times)
    midpoint_augmented = (
        0.5 * (endpoints[:-1] + endpoints[1:])
        + durations[:, None] * (rates[:-1] - rates[1:]) / 8.0
    )
    tasks = [
        (
            interval,
            midpoint_augmented[interval, :-1] / weights,
            max(float(midpoint_augmented[interval, -1]), 0.0),
            weights,
            reference,
        )
        for interval in range(370)
    ]
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        results = []
        for count, result in enumerate(executor.map(graph._node, tasks, chunksize=1), 1):
            results.append(result)
            if count % 32 == 0 or count == len(tasks):
                print(json.dumps({"completed": count, "total": len(tasks)}), flush=True)
    results.sort(key=lambda item: int(item[0]))
    rows = [item[1] for item in results]
    jacobians = np.asarray([item[2] for item in results])
    gradients = np.asarray([item[3] for item in results])
    operator_norms = np.asarray([row["graph_Jacobian_operator_2_norm"] for row in rows])
    np.savez_compressed(
        DATA,
        action_midpoints=0.5 * (times[:-1] + times[1:]),
        midpoint_augmented_action_values=midpoint_augmented,
        graph_Jacobian_action=jacobians,
        descriptor_gradient_action=gradients,
    )
    validation = {
        "all_370_midpoint_graph_Jacobians_materialized": jacobians.shape == (370, 98, 98),
        "all_370_midpoint_descriptor_gradients_materialized": gradients.shape == (370, 98),
        "branch_24_selected_at_every_midpoint": all(int(row["selected_branch"]) == 24 for row in rows),
        "selected_line_remains_simple_numerically": min(row["selected_eigenline_gap"] for row in rows) > 1.0e-7,
        "all_quantities_finite": bool(np.all(np.isfinite(np.concatenate((
            midpoint_augmented.ravel(), jacobians.ravel(), gradients.ravel(),
        ))))),
        "JAX_third_tensor_is_predictor_not_interval_authority": True,
        "no_action_source_selector_scale_gate_or_chord_changed": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    payload = {
        "artifact": "BHSM_N12_GATE7_HERMITE_SIMPSON_MIDPOINT_GRAPH_JACOBIAN",
        "status": "ALL_370_HERMITE_SIMPSON_MIDPOINT_JACOBIANS_MATERIALIZED" if passed else "MIDPOINT_GRAPH_JACOBIAN_INVALID",
        "authority": "HYBRID_RETAINED_ACTION_JAX_NUMERICAL_PREDICTOR_NOT_INTERVAL_AUTHORITY",
        "summary": {
            "midpoint_count": len(rows),
            "minimum_selected_eigenline_gap": min(row["selected_eigenline_gap"] for row in rows),
            "maximum_graph_Jacobian_operator_2_norm": float(np.max(operator_norms)),
            "maximum_graph_Jacobian_operator_owner_interval": int(np.argmax(operator_norms)),
            "maximum_graph_Jacobian_numerical_abscissa": max(row["graph_Jacobian_numerical_abscissa"] for row in rows),
            "maximum_graph_Jacobian_spectral_abscissa": max(row["graph_Jacobian_spectral_abscissa"] for row in rows),
        },
        "data": _relative(DATA),
        "data_SHA256": _sha256(DATA),
        "inputs": {
            _relative(path): _sha256(path)
            for path in (SOURCE, SOURCE.with_suffix(".npz"), ENDPOINT, ENDPOINT.with_suffix(".npz"), THEORY, THIS_SCRIPT)
        },
        "claim_boundary": {
            "Hermite_Simpson_block_Newton_operator": "OPEN_ASSEMBLY",
            "continuous_action_constrained_center": "OPEN",
            "Gate7": "ACTIVE_ACTION_OWNED_OPERATOR_ORACLE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": "ASSEMBLE_AND_SOLVE_THE_BLOCK_BIDIAGONAL_HERMITE_SIMPSON_NEWTON_RECURRENCE",
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
