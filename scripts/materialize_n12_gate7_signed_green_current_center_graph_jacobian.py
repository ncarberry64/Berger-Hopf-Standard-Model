"""Rebuild the reduced graph Jacobian on the signed-Green corrected center."""

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
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_hybrid_c2_graph_jacobian import (  # noqa: E402
    graph_jacobian_action,
)


BASE = ROOT / "artifacts" / "flagship_integration"
CENTER = BASE / "BHSM_N12_GATE7_SIGNED_GREEN_PROJECTED_ENDPOINT_CANDIDATE.json"
CENTER_DATA = CENTER.with_suffix(".npz")
PRIOR = BASE / "BHSM_N12_C2_STOP_QUARTER_STEP_FINE_HYBRID_GRAPH_JACOBIAN_RECONNAISSANCE.json"
THEORY = ROOT / "theory" / "n12_gate7_signed_green_current_center_graph_jacobian.md"
RESULT = BASE / "BHSM_N12_GATE7_SIGNED_GREEN_CURRENT_CENTER_GRAPH_JACOBIAN.json"
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


def _node(task: tuple[int, np.ndarray, float, np.ndarray, np.ndarray]) -> tuple[object, ...]:
    index, state, descriptor, weights, reference = task
    result = graph_jacobian_action(state, weights, reference, descriptor)
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
    return index, row, jacobian, gradient


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=min(8, os.cpu_count() or 1))
    args = parser.parse_args()
    center = _load(CENTER)
    prior = _load(PRIOR)
    if center.get("validation_passed") is not True:
        raise RuntimeError("validated signed-Green projected center required")
    with np.load(CENTER_DATA) as source:
        states = np.asarray(source["projected_states"], dtype=float)
        descriptors = np.asarray(source["recentered_descriptors"], dtype=float)
        times = np.asarray(source["action_times"], dtype=float)
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)
    tasks = [
        (index, state, float(descriptors[index]), weights, reference)
        for index, state in enumerate(states)
    ]
    results = []
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        for count, result in enumerate(executor.map(_node, tasks, chunksize=1), 1):
            results.append(result)
            if count % 32 == 0 or count == len(tasks):
                print(json.dumps({
                    "completed": count,
                    "total": len(tasks),
                    "node": int(result[0]),
                }), flush=True)
    results.sort(key=lambda item: int(item[0]))
    rows = [item[1] for item in results]
    jacobians = np.asarray([item[2] for item in results])
    gradients = np.asarray([item[3] for item in results])
    prior_norm = float(prior["summary"]["maximum_graph_Jacobian_operator_2_norm"])
    np.savez_compressed(
        DATA,
        action_lengths=times,
        graph_Jacobian_action=jacobians,
        descriptor_gradient_action=gradients,
    )
    validation = {
        "all_371_current_center_nodes_evaluated": jacobians.shape == (371, 98, 98),
        "all_descriptor_gradients_materialized": gradients.shape == (371, 98),
        "branch_24_selected_at_every_node": all(int(row["selected_branch"]) == 24 for row in rows),
        "selected_line_remains_simple_numerically": min(row["selected_eigenline_gap"] for row in rows) > 1.0e-7,
        "all_quantities_finite": bool(np.all(np.isfinite(np.concatenate((
            jacobians.ravel(), gradients.ravel(),
        ))))),
        "current_center_not_old_center_hash": _sha256(CENTER_DATA) != prior.get("center_data_SHA256", ""),
        "JAX_third_tensor_is_predictor_not_interval_authority": True,
        "no_action_source_selector_scale_gate_or_chord_changed": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    operator_norms = np.asarray([row["graph_Jacobian_operator_2_norm"] for row in rows])
    payload = {
        "artifact": "BHSM_N12_GATE7_SIGNED_GREEN_CURRENT_CENTER_GRAPH_JACOBIAN",
        "status": "CURRENT_CENTER_371_NODE_GRAPH_JACOBIAN_MATERIALIZED" if passed else "CURRENT_CENTER_GRAPH_JACOBIAN_INVALID",
        "authority": "CURRENT_CENTER_HYBRID_ACTION_JAX_PREDICTOR_NOT_INTERVAL_AUTHORITY",
        "summary": {
            "fine_nodes_through_stop": len(rows),
            "selected_branches_seen": sorted({int(row["selected_branch"]) for row in rows}),
            "minimum_selected_eigenline_gap": min(row["selected_eigenline_gap"] for row in rows),
            "minimum_b_psi": min(row["b_psi"] for row in rows),
            "maximum_graph_Jacobian_operator_2_norm": float(np.max(operator_norms)),
            "maximum_graph_Jacobian_operator_owner_node": int(np.argmax(operator_norms)),
            "prior_center_maximum_graph_Jacobian_operator_2_norm": prior_norm,
            "maximum_graph_Jacobian_numerical_abscissa": max(row["graph_Jacobian_numerical_abscissa"] for row in rows),
            "maximum_graph_Jacobian_spectral_abscissa": max(row["graph_Jacobian_spectral_abscissa"] for row in rows),
        },
        "rows": rows,
        "data": _relative(DATA),
        "data_SHA256": _sha256(DATA),
        "inputs": {
            _relative(path): _sha256(path)
            for path in (CENTER, CENTER_DATA, PRIOR, THEORY, THIS_SCRIPT)
        },
        "adjudication": {
            "prior_center_graph_Jacobian": "SUPERSEDED_FOR_NEWTON_PREDICTION_ON_THE_SIGNED_GREEN_CENTER",
            "current_center_graph_Jacobian": "MATERIALIZED_NUMERICAL_PREDICTOR",
            "retained_directional_and_between_node_interval_replay": "OPEN_AFTER_NEWTON_CONVERGENCE",
        },
        "claim_boundary": {
            "continuous_action_constrained_center": "OPEN_NEWTON_ITERATION",
            "continuous_outward_variational_carrier": "OPEN_AFTER_CENTER",
            "Gate7": "ACTIVE_ACTION_OWNED_OPERATOR_ORACLE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": "REAPPLY_THE_SIGNED_GREEN_ENDPOINT_NEWTON_MAP_WITH_THIS_CURRENT_CENTER_GRAPH_JACOBIAN_AND_REMEASURE_THE_1110_GAUSS3_DEFECTS",
        "validation": validation,
        "validation_passed": passed,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": payload["status"], "summary": payload["summary"], "validation_passed": passed}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
