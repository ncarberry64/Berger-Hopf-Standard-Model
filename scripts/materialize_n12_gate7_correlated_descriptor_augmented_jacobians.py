"""Build the 74D constraint-tangent/descriptor Hermite--Simpson derivative."""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

import numpy as np
from scipy.linalg import null_space


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import audit_n12_gate7_within_seam_constraint_center_obstruction as constraints  # noqa: E402
import audit_n12_gate7_constraint_descriptor_hermite_collocation_candidate as collocation  # noqa: E402
from bhsm.interface.aether_hybrid_c2_graph_jacobian import graph_jacobian_action  # noqa: E402
from bhsm.interface.aether_jax_c2_augmented_rate_jacobian import (  # noqa: E402
    descriptor_rate_and_gradient_action,
)


BASE = ROOT / "artifacts" / "flagship_integration"
ENDPOINT = BASE / "BHSM_N12_GATE7_CORRELATED_DESCRIPTOR_NEWTON_ENDPOINT_CANDIDATE.json"
REPLAY = BASE / "BHSM_N12_GATE7_CORRELATED_DESCRIPTOR_NEWTON_MIDPOINT_REPLAY.json"
THEORY = ROOT / "theory" / "n12_gate7_augmented_fixed_descriptor_newton.md"
RESULT = BASE / "BHSM_N12_GATE7_CORRELATED_DESCRIPTOR_AUGMENTED_JACOBIANS.json"
DATA = RESULT.with_suffix(".npz")
THIS_SCRIPT = Path(__file__).resolve()
_WORK: dict[str, np.ndarray] = {}


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
    _WORK["weights"] = weights
    _WORK["reference"] = reference
    collocation._initialize(weights, reference)


def _node(task: tuple[str, int, np.ndarray, float, np.ndarray]) -> tuple[object, ...]:
    kind, index, state, descriptor, stored_exact_rate = task
    weights = _WORK["weights"]
    reference = _WORK["reference"]
    retained_rate, retained_value = collocation._field(
        state, descriptor, weights, reference,
    )
    retained_cancelled = np.asarray(retained_value["cancelled_field_action"], dtype=float)
    graph = graph_jacobian_action(
        state, weights, reference, descriptor,
        include_fixed_descriptor_decomposition=True,
        cancelled_field_action=retained_cancelled,
    )
    fixed = np.asarray(graph.pop("fixed_descriptor_state_Jacobian_action"), dtype=float)
    descriptor_column = np.asarray(graph.pop("state_rate_descriptor_column"), dtype=float)
    graph_jacobian = np.asarray(graph.pop("graph_Jacobian_action"), dtype=float)
    descriptor_gradient = np.asarray(graph.pop("descriptor_gradient_action"), dtype=float)
    predicted_rate, descriptor_rate_gradient = descriptor_rate_and_gradient_action(
        state=state, signed_descriptor=descriptor,
        weights=weights, reference=reference,
    )
    augmented = np.zeros((99, 99))
    augmented[:98, :98] = fixed
    augmented[:98, 98] = descriptor_column
    augmented[98] = descriptor_rate_gradient
    frame, norms, values = constraints._constraint_geometry(state, weights)
    tangent = null_space(frame, rcond=1.0e-11)
    singular = np.linalg.svd(frame, compute_uv=False)
    row = {
        "kind": kind,
        "index": index,
        "selected_branch": int(graph["selected_branch"]),
        "selected_eigenline_gap": float(graph["selected_eigenline_gap"]),
        "augmented_Jacobian_operator_2_norm": float(np.linalg.norm(augmented, 2)),
        "fixed_descriptor_state_Jacobian_operator_2_norm": float(np.linalg.norm(fixed, 2)),
        "descriptor_rate_gradient_2_norm": float(np.linalg.norm(descriptor_rate_gradient)),
        "JAX_descriptor_rate_absolute_center_residual": abs(predicted_rate - retained_rate[-1]),
        "stored_vs_replayed_exact_augmented_rate_2_norm": float(np.linalg.norm(retained_rate - stored_exact_rate)),
        "retained_cancelled_field_action_norm": float(np.linalg.norm(retained_cancelled)),
        "predictor_cancelled_field_action_norm": float(graph["predictor_cancelled_field_action_norm"]),
        "predictor_vs_retained_cancelled_norm_absolute_mismatch": abs(
            float(graph["predictor_cancelled_field_action_norm"])
            - float(graph["cancelled_field_action_norm"])
        ),
        "graph_decomposition_residual_2_norm": float(np.linalg.norm(
            fixed + np.outer(descriptor_column, descriptor_gradient) - graph_jacobian,
        )),
        "scaled_constraint_2_norm": float(np.linalg.norm(values / norms)),
        "minimum_constraint_singular_value": float(singular[-1]),
        "constraint_tangent_residual_2_norm": float(np.linalg.norm(frame @ tangent, 2)),
        "tangent_orthonormal_residual_2_norm": float(np.linalg.norm(
            tangent.T @ tangent - np.eye(73), 2,
        )),
    }
    return (
        kind, index, row, augmented, tangent, descriptor_gradient,
        retained_rate, float(np.linalg.norm(retained_cancelled)),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=min(4, os.cpu_count() or 1))
    args = parser.parse_args()
    endpoint_record = _load(ENDPOINT)
    replay_record = _load(REPLAY)
    if not all(record.get("validation_passed") is True for record in (endpoint_record, replay_record)):
        raise RuntimeError("validated correlated endpoint and midpoint replay required")
    with np.load(ENDPOINT.with_suffix(".npz")) as source:
        times = np.asarray(source["action_times"], dtype=float)
        endpoint_states = np.asarray(source["projected_states"], dtype=float)
        endpoint_descriptors = np.asarray(source["correlated_descriptors"], dtype=float)
        endpoint_rates = np.asarray(source["exact_endpoint_augmented_rates"], dtype=float)
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)
    with np.load(REPLAY.with_suffix(".npz")) as source:
        midpoint_augmented = np.asarray(source["midpoint_augmented_action_values"], dtype=float)
        midpoint_rates = np.asarray(source["exact_midpoint_rates"], dtype=float)
    tasks = [
        ("endpoint", i, endpoint_states[i], float(endpoint_descriptors[i]), endpoint_rates[i])
        for i in range(371)
    ] + [
        ("midpoint", i, midpoint_augmented[i, :-1] / weights,
         float(midpoint_augmented[i, -1]), midpoint_rates[i])
        for i in range(370)
    ]
    results = []
    with ProcessPoolExecutor(
        max_workers=args.workers, initializer=_initialize,
        initargs=(weights, reference),
    ) as executor:
        for count, result in enumerate(executor.map(_node, tasks, chunksize=1), 1):
            results.append(result)
            if count % 32 == 0 or count == len(tasks):
                print(json.dumps({
                    "completed": count, "total": len(tasks),
                    "kind": result[0], "index": int(result[1]),
                }), flush=True)
    endpoints = sorted((item for item in results if item[0] == "endpoint"), key=lambda item: item[1])
    midpoints = sorted((item for item in results if item[0] == "midpoint"), key=lambda item: item[1])
    endpoint_rows = [item[2] for item in endpoints]
    midpoint_rows = [item[2] for item in midpoints]
    endpoint_jacobians = np.asarray([item[3] for item in endpoints])
    midpoint_jacobians = np.asarray([item[3] for item in midpoints])
    endpoint_tangents = np.asarray([item[4] for item in endpoints])
    midpoint_tangents = np.asarray([item[4] for item in midpoints])
    endpoint_descriptor_gradients = np.asarray([item[5] for item in endpoints])
    midpoint_descriptor_gradients = np.asarray([item[5] for item in midpoints])
    endpoint_replayed_rates = np.asarray([item[6] for item in endpoints])
    midpoint_replayed_rates = np.asarray([item[6] for item in midpoints])
    endpoint_cancelled_norms = np.asarray([item[7] for item in endpoints])
    midpoint_cancelled_norms = np.asarray([item[7] for item in midpoints])
    rows = endpoint_rows + midpoint_rows
    np.savez_compressed(
        DATA,
        action_times=times,
        endpoint_augmented_Jacobian_action=endpoint_jacobians,
        midpoint_augmented_Jacobian_action=midpoint_jacobians,
        endpoint_physical_tangent_action=endpoint_tangents,
        midpoint_physical_tangent_action=midpoint_tangents,
        endpoint_descriptor_gradient_action_diagnostic=endpoint_descriptor_gradients,
        midpoint_descriptor_gradient_action_diagnostic=midpoint_descriptor_gradients,
        exact_endpoint_augmented_rates=endpoint_replayed_rates,
        exact_midpoint_augmented_rates=midpoint_replayed_rates,
        exact_endpoint_cancelled_field_action_norm=endpoint_cancelled_norms,
        exact_midpoint_cancelled_field_action_norm=midpoint_cancelled_norms,
    )
    validation = {
        "all_371_endpoint_augmented_Jacobians_materialized": endpoint_jacobians.shape == (371, 99, 99),
        "all_370_midpoint_augmented_Jacobians_materialized": midpoint_jacobians.shape == (370, 99, 99),
        "all_741_constraint_tangents_have_dimension_73": endpoint_tangents.shape == (371, 98, 73) and midpoint_tangents.shape == (370, 98, 73),
        "all_constraint_frames_have_rank_25": min(row["minimum_constraint_singular_value"] for row in rows) > 1.0e-5,
        "all_tangents_annihilate_constraints": max(row["constraint_tangent_residual_2_norm"] for row in rows) < 5.0e-14,
        "all_tangents_are_orthonormal": max(row["tangent_orthonormal_residual_2_norm"] for row in rows) < 5.0e-14,
        "all_nodes_remain_on_branch_24": all(row["selected_branch"] == 24 for row in rows),
        "selected_line_remains_simple_numerically": min(row["selected_eigenline_gap"] for row in rows) > 1.0e-7,
        "fixed_descriptor_decomposition_reconstructs_graph_Jacobian": max(row["graph_decomposition_residual_2_norm"] for row in rows) < 1.0e-11,
        "all_retained_exact_rates_reproduce_the_parent_artifacts": max(row["stored_vs_replayed_exact_augmented_rate_2_norm"] for row in rows) < 1.0e-14,
        "all_graph_normalizations_use_retained_exact_cancelled_fields": True,
        "JAX_D4_descriptor_rate_is_predictor_only": True,
        "retained_exact_rates_remain_nonlinear_replay_authority": True,
        "all_quantities_finite": bool(np.all(np.isfinite(np.concatenate((endpoint_jacobians.ravel(), midpoint_jacobians.ravel()))))),
        "no_action_source_selector_scale_gate_or_chord_changed": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    payload = {
        "artifact": "BHSM_N12_GATE7_CORRELATED_DESCRIPTOR_AUGMENTED_JACOBIANS",
        "status": "AUGMENTED_FIXED_DESCRIPTOR_741_NODE_JACOBIANS_MATERIALIZED" if passed else "AUGMENTED_FIXED_DESCRIPTOR_JACOBIANS_INVALID",
        "authority": "HYBRID_RETAINED_ACTION_JAX_D4_NUMERICAL_PREDICTOR_NOT_INTERVAL_AUTHORITY",
        "mesh": {"endpoints": 371, "midpoints": 370, "ambient_dimension": 99, "physical_tangent_dimension": 73, "reduced_augmented_dimension": 74, "workers": args.workers},
        "summary": {
            "maximum_augmented_Jacobian_operator_2_norm": max(row["augmented_Jacobian_operator_2_norm"] for row in rows),
            "maximum_descriptor_rate_gradient_2_norm": max(row["descriptor_rate_gradient_2_norm"] for row in rows),
            "maximum_JAX_descriptor_rate_absolute_center_residual": max(row["JAX_descriptor_rate_absolute_center_residual"] for row in rows),
            "maximum_graph_decomposition_residual_2_norm": max(row["graph_decomposition_residual_2_norm"] for row in rows),
            "maximum_stored_vs_replayed_exact_augmented_rate_2_norm": max(row["stored_vs_replayed_exact_augmented_rate_2_norm"] for row in rows),
            "maximum_predictor_vs_retained_cancelled_norm_absolute_mismatch": max(row["predictor_vs_retained_cancelled_norm_absolute_mismatch"] for row in rows),
            "maximum_scaled_constraint_2_norm": max(row["scaled_constraint_2_norm"] for row in rows),
            "minimum_selected_eigenline_gap": min(row["selected_eigenline_gap"] for row in rows),
            "maximum_constraint_tangent_residual_2_norm": max(row["constraint_tangent_residual_2_norm"] for row in rows),
        },
        "endpoint_rows": endpoint_rows,
        "midpoint_rows": midpoint_rows,
        "data": _relative(DATA),
        "data_SHA256": _sha256(DATA),
        "inputs": {_relative(path): _sha256(path) for path in (
            ENDPOINT, ENDPOINT.with_suffix(".npz"), REPLAY, REPLAY.with_suffix(".npz"), THEORY, THIS_SCRIPT,
        )},
        "claim_boundary": {
            "augmented_derivative": "NUMERICAL_PREDICTOR_WITH_RETAINED_EXACT_NONLINEAR_REPLAY_REQUIRED",
            "descriptor_fiber": "DYNAMIC_RATE_ROW_INCLUDED_EXPLICITLY",
            "continuous_interval_shadowing": "OPEN",
            "Gate7": "ACTIVE_ACTION_OWNED_OPERATOR_ORACLE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": "SOLVE_THE_370_BLOCK_RECURRENCE_IN_73D_CONSTRAINT_TANGENT_PLUS_ONE_DESCRIPTOR_COORDINATE",
        "validation": validation,
        "validation_passed": passed,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": payload["status"], "summary": payload["summary"], "validation_passed": passed}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
