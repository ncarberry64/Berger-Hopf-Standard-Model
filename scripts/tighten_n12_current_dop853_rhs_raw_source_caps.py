"""Sharpen current RHS caps in the exact raw output frame, without new jets.

Read a snapshot of already-computed current RHS rows.  Rebuild only their
same-center tangent/remainder geometry and evaluate the four raw source
product-rule terms.  No action Hessian, eigenvector or directional Hessian
is recomputed.  An incomplete snapshot remains explicitly a partial cover.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import time
from typing import Any

for _thread_variable in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_thread_variable] = "1"

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import certify_n12_current_dop853_bordered_rhs_response as current

DEFAULT_SOURCE = current.DEFAULT_RESULT.with_suffix(".rows.jsonl")
DEFAULT_RESULT = current.BASE / (current.PREFIX + "TIGHT_RAW_RHS_RESPONSE.json")


def _geometry_only(interval: int, subspan: int, subdivisions: int) -> tuple[np.ndarray, np.ndarray]:
    """Bitwise same geometric algebra as the retained RHS driver, no jets."""
    dense = current.response.dense
    values, coefficients, _, weights, __, bracket_raw, stop_raw = dense._dense_arrays()
    right = float(stop_raw[0]) if interval == int(bracket_raw[0]) else 1.0
    controls = dense._dense_bernstein_controls(values[interval], coefficients[interval])
    controls = dense._restrict(controls, 0.0, right)
    controls = dense._restrict(controls, subspan / subdivisions, (subspan + 1) / subdivisions)[:, :-1]
    center_action = np.mean(controls, axis=0)
    midpoint_curve = dense._split(controls, 0.5)[0][-1]
    first_controls = 7.0 * (controls[1:] - controls[:-1])
    tangent = 0.5 * dense._split(first_controls, 0.5)[0][-1]
    second_controls = 42.0 * (controls[2:] - 2.0 * controls[1:-1] + controls[:-2])
    remainder_vertices = np.vstack((np.zeros((1, controls.shape[1])), second_controls / 8.0))
    residual_offset = center_action - midpoint_curve
    residual_axes = (remainder_vertices - residual_offset).T
    tangent_energy = float(tangent @ tangent)
    residual_energy = float(np.sum(residual_axes**2))
    if tangent_energy == 0:
        projection = residual_axes
    elif residual_energy == 0:
        projection = tangent[:, None]
    else:
        ratio = math.sqrt(residual_energy / tangent_energy)
        a, b = math.sqrt(1.0 + ratio), math.sqrt(1.0 + 1.0 / ratio)
        projection = np.column_stack((a * tangent, b * residual_axes))
    return center_action / weights, projection


def _output_legs(weights: np.ndarray, q_weights: np.ndarray, reduced_weights: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Exact dual legs for r=Wred([Wq*DqS,0]-Hred,q*Wq*v).

    action_bound takes weighted-action direction vectors.  Its gradient leg
    therefore is Wq*Wred_v, once, while its reduced Hessian leg is Wred.
    In the retained metric Wred_v=1.  No spectral preconditioner is inserted.
    """
    expected = np.concatenate((q_weights, reduced_weights))
    if not np.array_equal(weights, expected) or not np.array_equal(reduced_weights[:37], np.ones(37)):
        raise ValueError("current state weights must equal the retained action metric; velocity weights must be one")
    identity = np.eye(reduced_weights.size)
    gradient = np.zeros((weights.size, reduced_weights.size))
    gradient[:37] = (q_weights * reduced_weights[:37])[:, None] * identity[:37]
    mixed_output = np.zeros_like(gradient)
    mixed_output[37:] = reduced_weights[:, None] * identity
    return gradient, mixed_output


def _initialize(config: dict[str, str]) -> None:
    current._initialize(config)


def _evaluate(source: dict[str, Any]) -> dict[str, Any]:
    started = time.perf_counter()
    key = current._key(source)
    center, projection = _geometry_only(*key)
    response = current.response
    *_, weights, __, ___, ____ = response.dense._dense_arrays()
    q_weights, reduced_weights, _, _ = response.metric_data()
    gradient_output, mixed_output = _output_legs(weights, q_weights, reduced_weights)
    configuration = np.zeros(weights.size)
    configuration[:37] = q_weights * center[37:74]
    configuration_motion = np.zeros((weights.size, projection.shape[1]))
    configuration_motion[:37] = (q_weights / weights[37:74])[:, None] * projection[37:74]

    def mixed(*directions: np.ndarray) -> float:
        return response._up(float(response.dense.cluster.local.action_bound(
            center, projection=projection, mixed_directions=list(directions),
        ).d[-1]))

    # D r = gradient D2 - Hessian D3*configuration - Hessian D2*Dconfiguration.
    # The ball variation of configuration in the D3 term gives its fourth
    # listed contribution.  Signs are assembled in r0; bounds use triangle.
    terms = {
        "gradient_D2": mixed(gradient_output, projection),
        "mixed_Hessian_D3_center_configuration": mixed(mixed_output, configuration, projection),
        "mixed_Hessian_D3_configuration_motion": mixed(mixed_output, configuration_motion, projection),
        "mixed_Hessian_D2_configuration_motion": mixed(mixed_output, configuration_motion),
    }
    variation = response._up(sum(terms.values()))
    source_cap, response_cap = current._finite_cap(
        source["center_internal_rhs_2_norm"], variation,
        source["instantaneous_bordered_inverse_2_norm_upper"],
    )
    old = source["raw_internal_rhs_first_coefficient_derivative_2_norm_upper"]
    row = dict(source)
    row.update(
        previous_raw_source_variation_upper=old,
        previous_complete_bordered_response_2_norm_upper=source["complete_bordered_response_2_norm_upper"],
        raw_source_product_rule_terms=terms,
        raw_internal_rhs_first_coefficient_derivative_2_norm_upper=variation,
        internal_rhs_2_norm_upper=source_cap,
        complete_bordered_response_2_norm_upper=response_cap,
        finite_response_method="UNIFORM_INSTANTANEOUS_INVERSE_TIMES_DIRECT_RAW_SOURCE_CAP;_NO_SPECTRAL_PRECONDITIONER_OR_NEUMANN_GATE",
        direct_raw_variation_no_larger_than_previous=variation <= old,
        direct_raw_cap_elapsed_seconds=time.perf_counter() - started,
    )
    return row


def _snapshot_rows(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    lines = path.read_bytes().decode("utf-8").splitlines()
    header = json.loads(lines[0])
    rows = []
    for index, line in enumerate(lines[1:], 1):
        try:
            row = json.loads(line)["row"]
        except json.JSONDecodeError:
            if index == len(lines) - 1:
                break  # Never alter the active source checkpoint.
            raise
        if not current._closed(row):
            raise ValueError(f"source RHS row is not closed: {current._key(row)}")
        rows.append(row)
    if len({current._key(row) for row in rows}) != len(rows):
        raise ValueError("source snapshot contains duplicate rows")
    return header, rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_RESULT)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    config = {"spectrum": str(current.DEFAULT_SPECTRUM), "projector": str(current.DEFAULT_PROJECTOR),
              "inverse": str(current.DEFAULT_INVERSE), "center": str(current.DEFAULT_CENTER)}
    keys, count, base_inputs = current._binding(config)
    header, source_rows = _snapshot_rows(args.source)
    if header["inputs"] != base_inputs:
        raise ValueError("source checkpoint binding differs from the current action/source driver")
    allowed = set(keys)
    if any(current._key(row) not in allowed for row in source_rows):
        raise ValueError("source row is outside the current certified parent cover")
    if args.pilot:
        selected = {(0, 0, 8), (92, 0, 8), (182, 2, 4)}
        source_rows = [row for row in source_rows if current._key(row) in selected]
    source_rows.sort(key=lambda row: keys.index(current._key(row)))
    snapshot = args.output.with_suffix(".input-snapshot.jsonl")
    snapshot.parent.mkdir(parents=True, exist_ok=True)
    snapshot.write_text(json.dumps(header) + "\n" + "".join(json.dumps({"row": row}, allow_nan=False) + "\n" for row in source_rows), encoding="utf-8")
    inputs = dict(base_inputs)
    inputs[current._relative(Path(__file__))] = current._sha256(Path(__file__))
    inputs[current._relative(snapshot)] = current._sha256(snapshot)
    checkpoint = args.output.with_suffix(".rows.jsonl")
    requested_keys = [current._key(row) for row in source_rows]
    saved = current._load_checkpoint(checkpoint, inputs, requested_keys)
    if not checkpoint.exists():
        checkpoint.write_text(json.dumps({"inputs": inputs, "source_rows": len(source_rows)}) + "\n", encoding="utf-8")
    remaining = [row for row in source_rows if current._key(row) not in saved]
    workers = min(max(1, args.workers), os.cpu_count() or 1, len(remaining) or 1)
    print(json.dumps({"stage": "DIRECT_RAW_SOURCE_START", "snapshot_rows": len(source_rows), "resumed": len(saved), "workers": workers}), flush=True)
    started = time.perf_counter()
    with ProcessPoolExecutor(max_workers=workers, initializer=_initialize, initargs=(config,)) as executor:
        for row in executor.map(_evaluate, remaining, chunksize=1):
            with checkpoint.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps({"row": row}, allow_nan=False) + "\n")
                stream.flush()
            saved[current._key(row)] = row
            if args.pilot or len(saved) % 32 == 0 or len(saved) == len(source_rows):
                print(json.dumps({"completed": len(saved), "total": len(source_rows), "key": current._key(row),
                                  "raw_variation_upper": row["raw_internal_rhs_first_coefficient_derivative_2_norm_upper"],
                                  "response_cap": row["complete_bordered_response_2_norm_upper"],
                                  "row_seconds": row["direct_raw_cap_elapsed_seconds"]}), flush=True)
    ordered = [saved[key] for key in requested_keys]
    complete = requested_keys == keys and current._partition_is_exact(ordered, count)
    validation = {
        "all_rows_closed_by_uniform_instantaneous_inverse": all(current._closed(row) for row in ordered),
        "all_direct_raw_source_bounds_improve_previous": all(row["direct_raw_variation_no_larger_than_previous"] for row in ordered),
        "exact_raw_source_gradient_and_Hessian_dual_legs_used": True,
        "geometric_projection_same_bitwise_algebra_as_source_driver": True,
        "no_exact_action_or_directional_Hessian_reevaluation": True,
        "no_Neumann_diagnosis_promoted": True,
    }
    passed = all(validation.values())
    payload = {
        "artifact": "BHSM_N12_CURRENT_DOP853_DIRECT_RAW_RHS_RESPONSE",
        "status": ("ALL_CURRENT_DOP853_DIRECT_RAW_RHS_AND_FINITE_RESPONSES_CERTIFIED" if complete else "CURRENT_DOP853_DIRECT_RAW_RHS_PARTIAL_COVER_EVALUATED") if passed else "CURRENT_DOP853_DIRECT_RAW_RHS_OPEN",
        "mesh": {"snapshot_cells": len(ordered), "full_current_cover_cells": len(keys), "retained_dense_intervals": count, "complete_cover": complete},
        "summary": {
            "maximum_internal_rhs_2_norm_upper": max(row["internal_rhs_2_norm_upper"] for row in ordered),
            "maximum_complete_bordered_response_2_norm_upper": max(row["complete_bordered_response_2_norm_upper"] for row in ordered),
            "minimum_raw_source_improvement_factor": min(row["previous_raw_source_variation_upper"] / row["raw_internal_rhs_first_coefficient_derivative_2_norm_upper"] for row in ordered),
            "owner": max(ordered, key=lambda row: row["complete_bordered_response_2_norm_upper"]),
        },
        "rows": ordered, "validation": validation, "validation_passed": passed,
        "claim_boundary": {"current_entire_cover_response_finite": "CERTIFIED_UNIFORM_CAP" if passed and complete else "OPEN_UNTIL_ALL_CURRENT_COVER_ROWS_INCLUDED",
                           "tight_response_level_Neumann_proof": "NOT_PROMOTED", "correlated_shadowing_tube": "OPEN", "scalar_first_hit_interval": "OPEN", "FULL_BHSM_COMPLETE": False},
        "inputs": inputs, "elapsed_seconds": time.perf_counter() - started,
        "exact_next_dependency": "CONSUME_THESE_DIRECT_RAW_SOURCE_CAPS_IN_THE_CURRENT_CORRELATED_GREEN_SHADOWING_PROOF",
        "FLAGSHIP_READY": False, "FULL_BHSM_COMPLETE": False,
    }
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": payload["status"], "summary": payload["summary"], "validation_passed": passed, "output": str(args.output.resolve())}, indent=2), flush=True)
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
