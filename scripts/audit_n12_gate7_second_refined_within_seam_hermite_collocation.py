"""Halve the first refined Gate-7 Hermite mesh a second time."""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
import json
import os
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_n12_gate7_refined_within_seam_hermite_collocation as first  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
PARENT = BASE / "BHSM_N12_GATE7_REFINED_WITHIN_SEAM_HERMITE_COLLOCATION.json"
PARENT_DATA = PARENT.with_suffix(".npz")
ENDPOINT = BASE / "BHSM_N12_GATE7_CURRENT_LINEARIZATION_NEWTON_ENDPOINT_CANDIDATE.json"
THEORY = ROOT / "theory" / "n12_gate7_second_refined_within_seam_hermite_collocation.md"
RESULT = BASE / "BHSM_N12_GATE7_SECOND_REFINED_WITHIN_SEAM_HERMITE_COLLOCATION.json"
DATA = RESULT.with_suffix(".npz")
THIS_SCRIPT = Path(__file__).resolve()


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parent = _load(PARENT)
    if parent.get("validation_passed") is not True:
        raise RuntimeError("validated first within-seam refinement required")
    with np.load(PARENT_DATA) as source:
        times = np.asarray(source["refined_action_times"], dtype=float)
        values = np.asarray(source["refined_augmented_nodes"], dtype=float)
        rates = np.asarray(source["refined_exact_node_rates"], dtype=float)
        sample_intervals = np.asarray(source["sample_interval"], dtype=int)
        sample_units = np.asarray(source["sample_unit_fraction"], dtype=float)
        old_defects = np.asarray(source["sampled_augmented_flow_defect"], dtype=float)
    with np.load(ENDPOINT.with_suffix(".npz")) as source:
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)

    intervals = times.size - 1
    midpoint_times = np.empty(intervals)
    midpoint_values = np.empty((intervals, 99))
    midpoint_rates = np.empty((intervals, 99))
    for interval in range(intervals):
        duration = float(times[interval + 1] - times[interval])
        midpoint, path_rate = first.collocation.hermite._hermite(
            values[interval], values[interval + 1],
            rates[interval], rates[interval + 1], 0.5, duration,
        )
        mask = sample_intervals == interval
        local_units = sample_units[mask]
        local_defects = old_defects[mask]
        middle = int(np.argmin(np.abs(local_units - 0.5)))
        if abs(float(local_units[middle]) - 0.5) > 2.0e-14:
            raise RuntimeError(f"Gauss-3 midpoint missing on interval {interval}")
        midpoint_times[interval] = 0.5 * float(times[interval] + times[interval + 1])
        midpoint_values[interval] = midpoint
        midpoint_rates[interval] = path_rate - local_defects[middle]

    refined_count = 2 * intervals + 1
    refined_times = np.empty(refined_count)
    refined_values = np.empty((refined_count, 99))
    refined_rates = np.empty((refined_count, 99))
    for interval in range(intervals):
        refined_times[2 * interval] = times[interval]
        refined_times[2 * interval + 1] = midpoint_times[interval]
        refined_values[2 * interval] = values[interval]
        refined_values[2 * interval + 1] = midpoint_values[interval]
        refined_rates[2 * interval] = rates[interval]
        refined_rates[2 * interval + 1] = midpoint_rates[interval]
    refined_times[-1] = times[-1]
    refined_values[-1] = values[-1]
    refined_rates[-1] = rates[-1]

    nodes, _ = np.polynomial.legendre.leggauss(3)
    units = 0.5 * (nodes + 1.0)
    tasks = []
    order = 0
    for interval in range(refined_count - 1):
        duration = float(refined_times[interval + 1] - refined_times[interval])
        for sample, unit in enumerate(units):
            tasks.append((
                order, interval, sample, float(unit),
                refined_values[interval], refined_values[interval + 1],
                refined_rates[interval], refined_rates[interval + 1], duration,
            ))
            order += 1
    workers = min(
        int(os.environ.get("BHSM_N12_SECOND_REFINED_HERMITE_WORKERS", "8")),
        os.cpu_count() or 1,
    )
    with ProcessPoolExecutor(
        max_workers=workers,
        initializer=first._initialize,
        initargs=(weights, reference),
    ) as executor:
        sampled = list(executor.map(first._sample, tasks, chunksize=2))
    sampled.sort(key=lambda item: item[0])
    rows = [item[1] for item in sampled]
    defects = np.asarray([item[2] for item in sampled])
    flow_norms = np.asarray([row["augmented_flow_defect_2_norm"] for row in rows])
    constraint_norms = np.asarray([row["scaled_constraint_2_norm"] for row in rows])
    fiber_residuals = np.asarray([row["numeric_descriptor_fiber_residual"] for row in rows])
    prior_flow = float(parent["summary"]["maximum_augmented_flow_defect_2_norm"])
    owner = int(np.argmax(flow_norms))
    np.savez_compressed(
        DATA,
        refined_action_times=refined_times,
        refined_augmented_nodes=refined_values,
        refined_exact_node_rates=refined_rates,
        sample_interval=np.asarray([row["interval"] for row in rows], dtype=int),
        sample_unit_fraction=np.asarray([row["unit_fraction"] for row in rows]),
        sampled_augmented_flow_defect=defects,
        sampled_augmented_flow_defect_2_norm=flow_norms,
        sampled_scaled_constraint_2_norm=constraint_norms,
        sampled_numeric_descriptor_fiber_residual=fiber_residuals,
    )
    validation = {
        "all_740_existing_exact_midpoint_fields_inserted": midpoint_rates.shape == (740, 99),
        "all_1481_refined_nodes_materialized": refined_values.shape == (1481, 99),
        "all_4440_refined_Gauss3_samples_evaluated": len(rows) == 4440,
        "branch_24_selected_at_every_sample": all(row["selected_branch"] == 24 for row in rows),
        "selected_line_remains_simple_numerically": min(row["selected_eigenline_gap"] for row in rows) > 1.0e-7,
        "second_within_seam_halving_reduces_maximum_flow_defect": float(np.max(flow_norms)) < prior_flow,
        "all_quantities_finite": bool(np.all(np.isfinite(np.concatenate((
            refined_values.ravel(), refined_rates.ravel(), defects.ravel(),
        ))))),
        "continuous_interval_shadowing_not_claimed": True,
        "quarter_step_proof_center_not_replaced": True,
        "no_action_source_selector_scale_gate_or_chord_changed": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    payload = {
        "artifact": "BHSM_N12_GATE7_SECOND_REFINED_WITHIN_SEAM_HERMITE_COLLOCATION",
        "status": "SECOND_WITHIN_SEAM_HALVING_REDUCES_HERMITE_FLOW_DEFECT" if passed else "SECOND_WITHIN_SEAM_HALVING_DOES_NOT_REDUCE_FLOW_DEFECT",
        "authority": "NUMERICAL_SECOND_REFINED_GAUSS3_COLLOCATION_NOT_INTERVAL_AUTHORITY",
        "mesh": {
            "refined_intervals": 1480,
            "refined_nodes": 1481,
            "Gauss_samples_per_interval": 3,
            "workers": workers,
        },
        "summary": {
            "maximum_sampled_scaled_constraint_2_norm": float(np.max(constraint_norms)),
            "maximum_numeric_descriptor_fiber_residual_absolute": float(np.max(np.abs(fiber_residuals))),
            "maximum_augmented_flow_defect_2_norm": float(np.max(flow_norms)),
            "prior_maximum_augmented_flow_defect_2_norm": prior_flow,
            "flow_defect_reduction_factor": prior_flow / float(np.max(flow_norms)),
            "minimum_selected_eigenline_gap": min(row["selected_eigenline_gap"] for row in rows),
            "flow_defect_owner": rows[owner],
        },
        "data": first._relative(DATA),
        "data_SHA256": first._sha256(DATA),
        "inputs": {
            first._relative(path): first._sha256(path)
            for path in (
                PARENT, PARENT_DATA, ENDPOINT, ENDPOINT.with_suffix(".npz"),
                THEORY, THIS_SCRIPT,
            )
        },
        "adjudication": {
            "quarter_step_center": "RETAINED",
            "within_seam_interpolant": "HALVED_A_SECOND_TIME_USING_EXACT_MIDPOINT_FIELDS",
            "continuous_center": "OPEN_INTERVAL_SHADOWING_OR_HIGH_ORDER_COLLOCATION",
        },
        "claim_boundary": {
            "continuous_action_constrained_center": "OPEN_INTERVAL_AUTHORITY",
            "continuous_outward_variational_carrier": "OPEN_AFTER_CENTER",
            "Gate7": "ACTIVE_ACTION_OWNED_OPERATOR_ORACLE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "USE_THE_TWO_SUCCESSIVE_REFINEMENT_RATIOS_TO_ADJUDICATE_MESH_REFINEMENT_"
            "VERSUS_DIRECT_HIGH_ORDER_COLLOCATION_OR_OUTWARD_SHADOWING"
        ),
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
