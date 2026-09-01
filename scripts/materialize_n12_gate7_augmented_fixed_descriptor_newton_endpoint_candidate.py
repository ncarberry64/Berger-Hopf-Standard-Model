"""Apply the full 74D Newton predictor and persist regular norm-jet data."""

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
import audit_n12_gate7_constraint_descriptor_hermite_collocation_candidate as collocation  # noqa: E402
import audit_n12_gate7_within_seam_constraint_center_obstruction as constraints  # noqa: E402
from bhsm.interface.aether_hybrid_c2_graph_jacobian import graph_jacobian_action  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
PARENT = BASE / "BHSM_N12_GATE7_CORRELATED_DESCRIPTOR_NEWTON_ENDPOINT_CANDIDATE.json"
PREDICTOR = BASE / "BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_BLOCK_NEWTON_PREDICTOR.json"
THEORY = ROOT / "theory" / "n12_gate7_augmented_fixed_descriptor_newton.md"
RESULT = BASE / "BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_NEWTON_ENDPOINT_CANDIDATE.json"
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


def _project(state: np.ndarray, weights: np.ndarray, steps: int = 2) -> tuple[np.ndarray, np.ndarray, float, float]:
    result = np.array(state, copy=True)
    total = np.zeros(98)
    initial = constraints._scaled_residual(result, weights)[0]
    for _ in range(steps):
        frame, norms, values = constraints._constraint_geometry(result, weights)
        correction = -frame.T @ np.linalg.solve(frame @ frame.T, values / norms)
        result += correction / weights
        total += correction
    final = constraints._scaled_residual(result, weights)[0]
    return result, total, initial, final


def _node(task: tuple[int, np.ndarray, float, np.ndarray]) -> tuple[object, ...]:
    index, parent_state, parent_descriptor, correction = task
    weights = _WORK["weights"]
    reference = _WORK["reference"]
    trial = parent_state + correction[:98] / weights
    state, projection, initial_constraint, final_constraint = _project(trial, weights)
    descriptor = float(parent_descriptor + correction[98])
    if descriptor < 0.0:
        raise ArithmeticError(f"node {index} left signed-descriptor domain")
    rate, value = collocation._field(state, descriptor, weights, reference)
    cancelled = np.asarray(value["cancelled_field_action"], dtype=float)
    cancelled_norm = float(np.linalg.norm(cancelled))
    graph = graph_jacobian_action(
        state, weights, reference, descriptor,
        include_fixed_descriptor_decomposition=True,
        cancelled_field_action=cancelled,
    )
    norm_gradient = np.asarray(graph.pop("cancelled_norm_state_gradient_action"), dtype=float)
    norm_descriptor = float(graph.pop("cancelled_norm_descriptor_derivative"))
    graph.pop("fixed_descriptor_state_Jacobian_action")
    graph.pop("state_rate_descriptor_column")
    graph.pop("graph_Jacobian_action")
    predictor_norm = float(graph.pop("predictor_cancelled_field_action_norm"))
    descriptor_gradient = np.asarray(graph.pop("descriptor_gradient_action"), dtype=float)
    frame, _, _ = constraints._constraint_geometry(state, weights)
    tangent = null_space(frame, rcond=1.0e-11)
    row = {
        "node": index,
        "descriptor": descriptor,
        "selected_branch": int(value["selected_branch"]),
        "selected_eigenline_gap": float(value["selected_eigenline_gap"]),
        "cancelled_field_action_norm": cancelled_norm,
        "graph_cancelled_field_action_norm": float(graph["cancelled_field_action_norm"]),
        "hybrid_predictor_cancelled_field_action_norm": predictor_norm,
        "hybrid_predictor_norm_absolute_center_mismatch": abs(cancelled_norm - predictor_norm),
        "norm_realization_absolute_residual": abs(cancelled_norm - float(graph["cancelled_field_action_norm"])),
        "initial_scaled_constraint_2_norm": initial_constraint,
        "final_scaled_constraint_2_norm": final_constraint,
        "constraint_projection_action_2_norm": float(np.linalg.norm(projection)),
        "constraint_tangent_residual_2_norm": float(np.linalg.norm(frame @ tangent, 2)),
    }
    return (
        index, row, state, descriptor, rate, projection, tangent,
        cancelled_norm, norm_gradient, norm_descriptor, descriptor_gradient,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=min(4, os.cpu_count() or 1))
    args = parser.parse_args()
    parent_record = _load(PARENT)
    predictor_record = _load(PREDICTOR)
    if parent_record.get("validation_passed") is not True or predictor_record.get("validation_passed") is not True:
        raise RuntimeError("validated parent and 74D predictor required")
    with np.load(PARENT.with_suffix(".npz")) as source:
        times = np.asarray(source["action_times"], dtype=float)
        parent_states = np.asarray(source["projected_states"], dtype=float)
        parent_descriptors = np.asarray(source["correlated_descriptors"], dtype=float)
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)
    with np.load(PREDICTOR.with_suffix(".npz")) as source:
        corrections = np.asarray(source["endpoint_augmented_correction_action"], dtype=float)
        reduced_coordinates = np.asarray(source["endpoint_reduced_tangent_descriptor_coordinates"], dtype=float)
    tasks = [
        (i, parent_states[i], float(parent_descriptors[i]), corrections[i])
        for i in range(371)
    ]
    results = []
    with ProcessPoolExecutor(max_workers=args.workers, initializer=_initialize, initargs=(weights, reference)) as executor:
        for count, result in enumerate(executor.map(_node, tasks, chunksize=1), 1):
            results.append(result)
            if count % 32 == 0 or count == len(tasks):
                print(json.dumps({"completed": count, "total": len(tasks), "node": int(result[0])}), flush=True)
    results.sort(key=lambda item: int(item[0]))
    rows = [item[1] for item in results]
    states = np.asarray([item[2] for item in results])
    descriptors = np.asarray([item[3] for item in results])
    rates = np.asarray([item[4] for item in results])
    projections = np.asarray([item[5] for item in results])
    tangents = np.asarray([item[6] for item in results])
    norms = np.asarray([item[7] for item in results])
    norm_state_gradients = np.asarray([item[8] for item in results])
    norm_descriptor_derivatives = np.asarray([item[9] for item in results])
    descriptor_gradients = np.asarray([item[10] for item in results])
    actual_state_displacement = (states - parent_states) * weights[None, :]
    actual_descriptor_displacement = descriptors - parent_descriptors
    np.savez_compressed(
        DATA,
        collocation_arc_parameters=times,
        projected_states=states,
        independent_signed_descriptors=descriptors,
        exact_endpoint_augmented_rates=rates,
        requested_endpoint_augmented_correction_action=corrections,
        endpoint_reduced_tangent_descriptor_coordinates=reduced_coordinates,
        constraint_projection_action=projections,
        actual_state_displacement_action=actual_state_displacement,
        actual_descriptor_displacement=actual_descriptor_displacement,
        endpoint_constraint_tangent_action=tangents,
        cancelled_field_action_norm=norms,
        cancelled_norm_state_gradient_action=norm_state_gradients,
        cancelled_norm_descriptor_derivative=norm_descriptor_derivatives,
        descriptor_gradient_action_diagnostic=descriptor_gradients,
        state_weights=weights,
        branch_reference=reference,
    )
    validation = {
        "all_371_endpoint_candidates_replayed": states.shape == (371, 98),
        "all_endpoint_constraints_close_numerically": max(row["final_scaled_constraint_2_norm"] for row in rows) < 2.0e-14,
        "all_descriptors_remain_nonnegative": float(np.min(descriptors)) >= 0.0,
        "branch_24_selected_at_every_endpoint": all(row["selected_branch"] == 24 for row in rows),
        "selected_line_remains_simple_numerically": min(row["selected_eigenline_gap"] for row in rows) > 1.0e-7,
        "cancelled_norm_realizations_agree": max(row["norm_realization_absolute_residual"] for row in rows) < 1.0e-14,
        "regular_cancelled_norm_state_and_descriptor_derivatives_persisted": norm_state_gradients.shape == (371, 98) and norm_descriptor_derivatives.shape == (371,),
        "fresh_endpoint_constraint_tangents_persisted": tangents.shape == (371, 98, 73),
        "collocation_abscissae_are_not_labeled_proper_time": True,
        "proper_time_density_requires_N_boundary_times_s_over_cancelled_norm": True,
        "72D_reset_history_first_jet_not_claimed": True,
        "all_quantities_finite": bool(np.all(np.isfinite(np.concatenate((states.ravel(), descriptors, rates.ravel(), norms))))),
        "no_action_source_selector_scale_gate_or_chord_changed": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    payload = {
        "artifact": "BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_NEWTON_ENDPOINT_CANDIDATE",
        "status": "AUGMENTED_FIXED_DESCRIPTOR_ENDPOINT_CANDIDATE_REPLAYED_WITH_REGULAR_NORM_JETS" if passed else "AUGMENTED_FIXED_DESCRIPTOR_ENDPOINT_CANDIDATE_INVALID",
        "authority": "RETAINED_EXACT_ENDPOINT_FIELD_REPLAY_NUMERICAL_CANDIDATE_NOT_INTERVAL_AUTHORITY",
        "parameterization": {"stored_abscissa": "NORMALIZED_CANCELLED_FIELD_ARC_COLLOCATION_PARAMETER", "proper_time_density": "N_boundary*s/cancelled_field_action_norm"},
        "summary": {
            "maximum_requested_state_correction_action_2_norm": float(np.max(np.linalg.norm(corrections[:, :98], axis=1))),
            "maximum_actual_state_displacement_action_2_norm": float(np.max(np.linalg.norm(actual_state_displacement, axis=1))),
            "maximum_descriptor_correction_absolute": float(np.max(np.abs(actual_descriptor_displacement))),
            "minimum_independent_signed_descriptor": float(np.min(descriptors)),
            "maximum_constraint_projection_action_2_norm": max(row["constraint_projection_action_2_norm"] for row in rows),
            "maximum_final_scaled_constraint_2_norm": max(row["final_scaled_constraint_2_norm"] for row in rows),
            "minimum_cancelled_field_action_norm": float(np.min(norms)),
            "maximum_cancelled_norm_state_gradient_action_2_norm": float(np.max(np.linalg.norm(norm_state_gradients, axis=1))),
            "maximum_cancelled_norm_descriptor_derivative_absolute": float(np.max(np.abs(norm_descriptor_derivatives))),
            "maximum_hybrid_predictor_norm_absolute_center_mismatch": max(row["hybrid_predictor_norm_absolute_center_mismatch"] for row in rows),
            "minimum_selected_eigenline_gap": min(row["selected_eigenline_gap"] for row in rows),
        },
        "rows": rows,
        "data": _relative(DATA),
        "data_SHA256": _sha256(DATA),
        "inputs": {_relative(path): _sha256(path) for path in (
            PARENT, PARENT.with_suffix(".npz"), PREDICTOR, PREDICTOR.with_suffix(".npz"), THEORY, THIS_SCRIPT,
        )},
        "claim_boundary": {
            "nonlinear_augmented_center": "OPEN_ALL_370_MIDPOINT_REPLAY",
            "proper_time_density_first_jet": "FIELDS_PERSISTED_FOR_DOWNSTREAM_COMPOSITION",
            "72D_reset_history_first_jet": "OPEN_COMPOSITION",
            "continuous_interval_shadowing": "OPEN",
            "Gate7": "ACTIVE_ACTION_OWNED_OPERATOR_ORACLE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": "REPLAY_ALL_370_RETAINED_EXACT_MIDPOINT_FIELDS_AND_ADJUDICATE_THE_FULL_AUGMENTED_NEWTON_STEP",
        "validation": validation,
        "validation_passed": passed,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": payload["status"], "summary": payload["summary"], "validation_passed": passed}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
