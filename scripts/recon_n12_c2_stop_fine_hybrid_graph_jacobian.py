"""Evaluate the calibrated hybrid graph Jacobian on every fine center node.

The retained action supplies each base gradient/Hessian and the cross-checked
JAX third tensor supplies their derivative.  This is a fast correlated-center
profile; retained directional replay and an interval between-node remainder
remain the certificate authority.
"""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
import argparse
import json
import os
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_hybrid_c2_graph_jacobian import (  # noqa: E402
    graph_jacobian_action,
)


BASE = ROOT / "artifacts" / "flagship_integration"
CENTER_DATA = Path(os.environ.get(
    "BHSM_N12_STOP_CENTER_DATA",
    str(BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_HALF_STEP_CENTER_RECONNAISSANCE.npz"),
))
RESULT = Path(os.environ.get(
    "BHSM_N12_STOP_FINE_JACOBIAN_RESULT",
    str(BASE / "BHSM_N12_C2_STOP_FINE_HYBRID_GRAPH_JACOBIAN_RECONNAISSANCE.json"),
))
DATA_RESULT = RESULT.with_suffix(".npz")


def _arrays() -> tuple[np.ndarray, ...]:
    with np.load(CENTER_DATA) as source:
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)
        fine_times = np.asarray(source["fine_grid_action_lengths"], dtype=float)
        fine_values = np.asarray(source["fine_grid_augmented_action_values"], dtype=float)
        bracket = int(source["stop_bracket_fine_grid_index"][0])
        stop_time = float(source["action_lengths"][-1])
        stop_augmented = np.concatenate((
            np.asarray(source["centers"][-1], dtype=float) * weights,
            np.asarray([float(source["signed_descriptors"][-1])]),
        ))
    times = np.concatenate((fine_times[:bracket + 1], np.asarray([stop_time])))
    augmented = np.vstack((fine_values[:bracket + 1], stop_augmented))
    states = augmented[:, :-1] / weights
    descriptors = augmented[:, -1]
    return states, descriptors, times, weights, reference


def _node(task: tuple[int, np.ndarray, float, np.ndarray, np.ndarray]) -> tuple:
    index, state, descriptor, weights, reference = task
    result = graph_jacobian_action(
        state, weights, reference, descriptor,
    )
    jacobian = np.asarray(result.pop("graph_Jacobian_action"), dtype=float)
    gradient = np.asarray(result.pop("descriptor_gradient_action"), dtype=float)
    symmetric = 0.5 * (jacobian + jacobian.T)
    eigenvalues = np.linalg.eigvals(jacobian)
    row = {
        "node": index,
        **result,
        "graph_Jacobian_operator_2_norm": float(np.linalg.norm(jacobian, 2)),
        "graph_Jacobian_numerical_abscissa": float(np.linalg.eigvalsh(symmetric)[-1]),
        "graph_Jacobian_spectral_abscissa": float(np.max(eigenvalues.real)),
        "descriptor_gradient_action_2_norm": float(np.linalg.norm(gradient)),
    }
    return row, jacobian, gradient


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=min(12, os.cpu_count() or 1))
    args = parser.parse_args()
    states, descriptors, times, weights, reference = _arrays()
    tasks = [
        (index, state, float(descriptors[index]), weights, reference)
        for index, state in enumerate(states)
    ]
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        results = []
        for count, result in enumerate(executor.map(_node, tasks, chunksize=1), 1):
            results.append(result)
            if count % 32 == 0 or count == len(tasks):
                print(json.dumps({
                    "completed": count,
                    "total": len(tasks),
                    "node": result[0]["node"],
                }), flush=True)
    rows = [item[0] for item in results]
    jacobians = np.asarray([item[1] for item in results])
    gradients = np.asarray([item[2] for item in results])
    np.savez_compressed(
        DATA_RESULT,
        action_lengths=times,
        graph_Jacobian_action=jacobians,
        descriptor_gradient_action=gradients,
    )
    payload = {
        "artifact": "BHSM_N12_C2_STOP_FINE_HYBRID_GRAPH_JACOBIAN_RECONNAISSANCE",
        "authority": "CALIBRATED_CENTER_PROFILE_NOT_INTERVAL_AUTHORITY",
        "center": CENTER_DATA.relative_to(ROOT).as_posix(),
        "summary": {
            "fine_nodes_through_stop": len(rows),
            "selected_branches_seen": sorted({int(row["selected_branch"]) for row in rows}),
            "minimum_selected_eigenline_gap": min(row["selected_eigenline_gap"] for row in rows),
            "minimum_b_psi": min(row["b_psi"] for row in rows),
            "maximum_graph_Jacobian_operator_2_norm": max(row["graph_Jacobian_operator_2_norm"] for row in rows),
            "maximum_graph_Jacobian_numerical_abscissa": max(row["graph_Jacobian_numerical_abscissa"] for row in rows),
            "maximum_graph_Jacobian_spectral_abscissa": max(row["graph_Jacobian_spectral_abscissa"] for row in rows),
        },
        "rows": rows,
        "data": DATA_RESULT.relative_to(ROOT).as_posix(),
        "validation_passed": False,
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
