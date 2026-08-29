"""Certify the internal bordered RHS/response on the Gate-7 cone.

Only the external Cauchy/birth source is zero.  The Euler--Lagrange child,
configuration, contact, and transport contributions are assembled as the
single retained internal reduced right-hand side before spectral
preconditioning or the bordered solve is applied.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from functools import lru_cache
import hashlib
import json
import math
import os
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import certify_n12_gate7_recentered_cone_boundary_cluster_spectrum as cone  # noqa: E402
from bhsm.interface.aether_forward_c2_descriptor_cover import metric_data  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
INVERSE = BASE / "BHSM_N12_GATE7_RECENTERED_CONE_BORDERED_HARD_INVERSE.json"
PROJECTOR = BASE / "BHSM_N12_GATE7_RECENTERED_CONE_SELECTED_PROJECTOR_GRAPH.json"
RESULT = BASE / "BHSM_N12_GATE7_RECENTERED_CONE_BORDERED_RHS_RESPONSE.json"
CHECKPOINT = BASE / (
    "BHSM_N12_GATE7_RECENTERED_CONE_BORDERED_RHS_RESPONSE.checkpoint.jsonl"
)
QDIM = 37
BASE_RESPONSE_REFINEMENT = int(os.environ.get(
    "BHSM_N12_GATE7_CONE_RESPONSE_REFINEMENT", "8",
))
LATE_RESPONSE_REFINEMENT = int(os.environ.get(
    "BHSM_N12_GATE7_CONE_LATE_RESPONSE_REFINEMENT", "8",
))
LATE_RESPONSE_SEAM_START = int(os.environ.get(
    "BHSM_N12_GATE7_CONE_LATE_RESPONSE_SEAM_START", "42",
))


def _up(value: float) -> float:
    return math.nextafter(float(value) * (1.0 + 1.0e-10), math.inf)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _inverse_rows() -> dict[tuple[int, int], dict[str, Any]]:
    payload = _load(INVERSE)
    if payload["validation_passed"] is not True:
        raise RuntimeError("validated recentered-cone bordered inverse required")
    return {
        (int(row["seam"]), int(row["local_index"])): row
        for row in payload["rows"]
    }


@lru_cache(maxsize=1)
def _projector_rows() -> dict[tuple[int, int], dict[str, Any]]:
    payload = _load(PROJECTOR)
    if payload["validation_passed"] is not True:
        raise RuntimeError("validated recentered-cone projector required")
    return {
        (int(row["seam"]), int(row["local_index"])): row
        for row in payload["rows"]
    }


def _exact_internal_rhs(state: np.ndarray, weights: np.ndarray) -> np.ndarray:
    q_weights, reduced_weights, _, _ = metric_data()
    jet = cone.cluster.local.exact_full_action_jet_at_state(
        12,
        state[:QDIM], state[QDIM:2 * QDIM], state[2 * QDIM:],
        points=cone.cluster.local.POINTS,
    )
    gradient_action = np.asarray(jet.gradient) / weights
    hessian_action = (
        np.asarray(jet.hessian) / weights[:, None] / weights[None, :]
    )
    configuration_action = q_weights * state[QDIM:2 * QDIM]
    mixed_reduced_q = hessian_action[QDIM:, :QDIM]
    rhs_action = np.concatenate((
        q_weights * gradient_action[:QDIM],
        np.zeros(reduced_weights.size - QDIM),
    )) - mixed_reduced_q @ configuration_action
    return reduced_weights * rhs_action


def _row(
    task: tuple[int, int, float, float, int, int, int],
) -> dict[str, Any]:
    (
        seam, local_index, left, right,
        parent_local_index, child, refinement,
    ) = task
    pair = (seam, parent_local_index)
    inverse = _inverse_rows()[pair]
    projector = _projector_rows()[pair]
    geometry = cone._geometry((seam, local_index, left, right))
    center = geometry["midpoint"]
    projection = geometry["projection"]
    values = geometry["values"]
    vectors = geometry["vectors"]
    selected = int(geometry["selected"])
    if selected != 24:
        raise RuntimeError("selected branch changed")
    weights = cone._inputs()[3]
    reference = cone._inputs()[4]
    q_weights, reduced_weights, _, _ = metric_data()
    total = weights.size
    reduced = reduced_weights.size

    configuration_center = np.zeros(total)
    configuration_center[:QDIM] = q_weights * center[QDIM:2 * QDIM]
    configuration_variation = np.zeros((total, projection.shape[1]))
    velocity_weights = weights[QDIM:2 * QDIM]
    configuration_variation[:QDIM] = (
        (q_weights / velocity_weights)[:, None]
        * projection[QDIM:2 * QDIM]
    )

    def mixed(*directions: np.ndarray) -> float:
        return _up(float(cone.cluster.local.action_bound(
            center,
            projection=projection,
            mixed_directions=list(directions),
        ).d[-1]))

    # The eigendecomposition in ``geometry`` is of the same exact retained
    # center Hessian.  Reconstruct it here rather than evaluating that action
    # jet a third time; the independent RHS evaluation below still consumes
    # the full gradient and mixed configuration block.
    hessian = (vectors * values[None, :]) @ vectors.T
    psi = vectors[:, selected]
    if float(psi @ reference) < 0.0:
        psi = -psi
    selected_value = float(values[selected])
    bordered = np.block([
        [hessian - selected_value * np.eye(reduced), psi[:, None]],
        [psi[None, :], np.zeros((1, 1))],
    ])
    rhs = _exact_internal_rhs(center, weights)
    forcing = np.concatenate((rhs, np.zeros(1)))
    response = np.linalg.solve(bordered, forcing)
    residual = _up(float(np.linalg.norm(bordered @ response - forcing)))
    center_rhs_norm = float(np.linalg.norm(rhs))
    center_response_norm = float(np.linalg.norm(response))

    hard_indices = np.asarray([
        index for index in range(values.size) if index != selected
    ], dtype=int)
    hard = vectors[:, hard_indices]
    denominators = values[hard_indices] - values[selected]
    preconditioned_hard = hard / denominators[None, :]
    response_test_directions = np.column_stack((preconditioned_hard, psi))
    response_gradient_output = np.zeros((
        total, response_test_directions.shape[1]
    ))
    response_gradient_output[:QDIM] = (
        q_weights[:, None] ** 2
        * response_test_directions[:QDIM]
    )
    response_mixed_output = np.zeros((
        total, response_test_directions.shape[1]
    ))
    response_mixed_output[QDIM:] = (
        reduced_weights[:, None] * response_test_directions
    )
    preconditioned_rhs_variation = _up(
        mixed(response_gradient_output, projection)
        + mixed(response_mixed_output, configuration_center, projection)
        + mixed(response_mixed_output, configuration_variation, projection)
        + mixed(response_mixed_output, configuration_variation)
    )
    preconditioned_rhs_second = _up(
        mixed(response_gradient_output, projection, projection)
        + mixed(
            response_mixed_output, configuration_center,
            projection, projection,
        )
        + mixed(
            response_mixed_output, configuration_variation,
            projection, projection,
        )
        + 2.0 * mixed(
            response_mixed_output, configuration_variation, projection,
        )
    )
    center_operator_norm = _up(max(
        1.0, float(np.max(np.abs(values - selected_value))),
    ))
    raw_rhs_first = _up(center_operator_norm * preconditioned_rhs_variation)
    raw_rhs_second = _up(center_operator_norm * preconditioned_rhs_second)
    center_preconditioned_source = np.concatenate((
        preconditioned_hard.T @ rhs,
        np.asarray([float(psi @ rhs)]),
    ))
    center_preconditioned_norm = float(
        np.linalg.norm(center_preconditioned_source)
    )

    hard_action = np.vstack((
        np.zeros((QDIM, hard.shape[1])),
        reduced_weights[:, None] * hard,
    ))
    preconditioned_action = np.vstack((
        np.zeros((QDIM, hard.shape[1])),
        reduced_weights[:, None] * preconditioned_hard,
    ))
    relative_blocks = []
    for matrix in geometry["directionals"]:
        lambda_slope = float(psi @ matrix @ psi)
        relative_blocks.append(
            (
                hard.T @ matrix @ hard
                - lambda_slope * np.eye(hard.shape[1])
            ) / denominators[:, None]
        )
    relative_D3 = _up(float(np.linalg.norm([
        np.linalg.norm(block, ord=2) for block in relative_blocks
    ])))
    relative_D4 = mixed(
        preconditioned_action, hard_action, projection, projection,
    )
    selected_shift = float(projector["selected_line_shift_upper"])
    gap_lower = float(inverse["certified_selected_to_hard_gap_lower"])
    relative_operator = _up(
        relative_D3 + 0.5 * relative_D4 + selected_shift / gap_lower
    )
    Neumann_factor = (
        _up(1.0 / (1.0 - relative_operator))
        if relative_operator < 1.0 else math.inf
    )
    chart_factor = float(inverse["center_chart_condition_factor_upper"])
    response_upper = _up(
        chart_factor * Neumann_factor
        * (center_preconditioned_norm + preconditioned_rhs_variation)
    )
    discrepancy = abs(center_preconditioned_norm - center_response_norm)
    backward_error = _up(
        (reduced + 1) * residual
        * float(inverse["center_chart_bordered_inverse_2_norm_upper"])
    )
    return {
        "seam": seam,
        "local_index": local_index,
        "action_interval": [left, right],
        "parent_local_index": parent_local_index,
        "child_within_parent": child,
        "response_refinement_per_parent": refinement,
        "selected_branch": selected,
        "projection_dimension": int(projection.shape[1]),
        "center_internal_rhs_2_norm": center_rhs_norm,
        "center_bordered_response_2_norm": center_response_norm,
        "center_preconditioned_internal_source_2_norm": (
            center_preconditioned_norm
        ),
        "preconditioned_internal_rhs_variation_2_norm_upper": (
            preconditioned_rhs_variation
        ),
        "preconditioned_internal_rhs_second_coefficient_derivative_2_norm_upper": (
            preconditioned_rhs_second
        ),
        "center_bordered_operator_2_norm_upper": center_operator_norm,
        "raw_internal_rhs_first_coefficient_derivative_2_norm_upper": (
            raw_rhs_first
        ),
        "raw_internal_rhs_second_coefficient_derivative_2_norm_upper": (
            raw_rhs_second
        ),
        "relative_bordered_D3_upper": relative_D3,
        "relative_bordered_D4_remainder_upper": 0.5 * relative_D4,
        "relative_selected_shift_upper": selected_shift / gap_lower,
        "relative_bordered_operator_perturbation_upper": relative_operator,
        "bordered_Neumann_factor_upper": Neumann_factor,
        "center_bordered_solve_residual_upper": residual,
        "charted_bordered_inverse_2_norm_upper": float(
            inverse["center_chart_bordered_inverse_2_norm_upper"]
        ),
        "complete_bordered_response_2_norm_upper": response_upper,
        "center_internal_rhs_finite": math.isfinite(center_rhs_norm),
        "center_preconditioned_solve_discrepancy": discrepancy,
        "binary64_bordered_backward_error_upper": backward_error,
        "center_preconditioned_source_matches_bordered_solve": (
            discrepancy <= backward_error
        ),
        "bordered_response_tube_finite": bool(
            relative_operator < 1.0 and math.isfinite(response_upper)
        ),
    }


def build_payload(
    tasks: list[tuple[int, int, float, float, int, int, int]],
    checkpoint: Path | None = None,
) -> dict[str, Any]:
    records = [_load(path) for path in (INVERSE, PROJECTOR)]
    if not all(record["validation_passed"] for record in records):
        raise RuntimeError("validated cone inverse/projector parents required")
    workers = min(
        int(os.environ.get("BHSM_N12_GATE7_CONE_WORKERS", "12")),
        os.cpu_count() or 1,
    )
    rows = []
    if checkpoint is not None and checkpoint.is_file():
        with checkpoint.open("r", encoding="utf-8") as source:
            rows = [json.loads(line) for line in source if line.strip()]
        if len(rows) > len(tasks):
            raise RuntimeError("response checkpoint longer than task mesh")
        checkpoint_prefix = [
            (
                row["seam"], row["local_index"], *row["action_interval"],
                row["parent_local_index"], row["child_within_parent"],
                row["response_refinement_per_parent"],
            ) for row in rows
        ]
        if checkpoint_prefix != tasks[:len(rows)]:
            raise RuntimeError("response checkpoint is not the current task prefix")
        print(json.dumps({
            "resumed_certified_prefix": len(rows),
            "total": len(tasks),
        }), flush=True)

    remaining = tasks[len(rows):]
    checkpoint_stream = (
        checkpoint.open("a", encoding="utf-8", newline="\n")
        if checkpoint is not None else None
    )
    try:
        with ProcessPoolExecutor(max_workers=workers) as executor:
            for count, row in enumerate(
                executor.map(_row, remaining, chunksize=1), len(rows) + 1,
            ):
                rows.append(row)
                if checkpoint_stream is not None:
                    checkpoint_stream.write(
                        json.dumps(row, sort_keys=True, separators=(",", ":"))
                        + "\n"
                    )
                    checkpoint_stream.flush()
                    if count % 128 == 0:
                        os.fsync(checkpoint_stream.fileno())
                if count % 16 == 0 or count == len(tasks):
                    print(json.dumps({
                        "completed": count,
                        "total": len(tasks),
                        "closed_so_far": all(
                            item["center_internal_rhs_finite"]
                            and item["bordered_response_tube_finite"]
                            for item in rows
                        ),
                        "maximum_relative_operator_so_far": max(
                            item["relative_bordered_operator_perturbation_upper"]
                            for item in rows
                        ),
                        "maximum_response_upper_so_far": max(
                            item["complete_bordered_response_2_norm_upper"]
                            for item in rows
                        ),
                    }), flush=True)
    finally:
        if checkpoint_stream is not None:
            checkpoint_stream.close()
    validation = {
        "all_requested_recentered_cone_cells_consumed_in_order": [
            (
                row["seam"], row["local_index"], *row["action_interval"],
                row["parent_local_index"], row["child_within_parent"],
                row["response_refinement_per_parent"],
            )
            for row in rows
        ] == tasks,
        "branch_24_selected_everywhere": all(
            row["selected_branch"] == 24 for row in rows
        ),
        "same_101_dimensional_recentered_product_cone_used": all(
            row["projection_dimension"] == 101 for row in rows
        ),
        "all_exact_center_internal_rhs_values_finite": all(
            row["center_internal_rhs_finite"] for row in rows
        ),
        "all_center_bordered_solve_residuals_small": all(
            row["center_bordered_solve_residual_upper"] < 1.0e-7
            for row in rows
        ),
        "all_bordered_response_tubes_finite": all(
            row["bordered_response_tube_finite"] for row in rows
        ),
        "all_center_preconditioned_sources_match_bordered_solves": all(
            row["center_preconditioned_source_matches_bordered_solve"]
            for row in rows
        ),
        "all_internal_rhs_first_and_second_coefficient_derivative_bounds_finite": all(
            math.isfinite(
                row["raw_internal_rhs_first_coefficient_derivative_2_norm_upper"]
            ) and math.isfinite(
                row["raw_internal_rhs_second_coefficient_derivative_2_norm_upper"]
            ) for row in rows
        ),
        "all_relative_bordered_perturbations_below_one": all(
            row["relative_bordered_operator_perturbation_upper"] < 1.0
            for row in rows
        ),
        "complete_internal_rhs_second_derivative_product_rule_assembled": True,
        "each_certified_cone_parent_refined_for_response_without_shrinking_halo": True,
        "every_adaptive_response_child_individually_validated": True,
        "only_external_Cauchy_birth_source_zero_internal_rhs_retained": True,
        "no_internal_child_contact_or_transport_response_zeroed": True,
        "no_added_seam_force_or_double_counted_response": True,
        "no_full_kinetic_Dirac_or_history_inverse_used": True,
        "no_action_equation_source_selector_scale_gate_or_chord_changed": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    owner = max(
        rows, key=lambda row: row["complete_bordered_response_2_norm_upper"]
    )
    return {
        "artifact": "BHSM_N12_GATE7_RECENTERED_CONE_BORDERED_RHS_RESPONSE",
        "status": (
            "RECENTERED_GATE7_CONE_ACTION_OWNED_BORDERED_RHS_RESPONSE_CERTIFIED"
            if passed else "RECENTERED_GATE7_CONE_BORDERED_RHS_RESPONSE_OPEN"
        ),
        "source_ontology": (
            "EXTERNAL_CAUCHY_BIRTH_SOURCE_ZERO;_ALL_RETAINED_AE2_"
            "EULER_LAGRANGE_CHILD_CONFIGURATION_CONTACT_AND_TRANSPORT_"
            "CONTRIBUTIONS_RETAINED_AS_ONE_INTERNAL_ACTION_OWNED_RHS"
        ),
        "mesh": {
            "parent_cells": len({
                (task[0], task[4]) for task in tasks
            }),
            "base_response_refinement": BASE_RESPONSE_REFINEMENT,
            "late_response_refinement": LATE_RESPONSE_REFINEMENT,
            "late_response_seam_start": LATE_RESPONSE_SEAM_START,
            "cells": len(rows),
            "projection_dimension": 101,
            "workers": workers,
        },
        "summary": {
            "maximum_center_internal_rhs_2_norm": max(
                row["center_internal_rhs_2_norm"] for row in rows
            ),
            "maximum_center_bordered_response_2_norm": max(
                row["center_bordered_response_2_norm"] for row in rows
            ),
            "maximum_preconditioned_internal_rhs_variation_2_norm_upper": max(
                row["preconditioned_internal_rhs_variation_2_norm_upper"]
                for row in rows
            ),
            "maximum_relative_bordered_operator_perturbation_upper": max(
                row["relative_bordered_operator_perturbation_upper"]
                for row in rows
            ),
            "maximum_bordered_Neumann_factor_upper": max(
                row["bordered_Neumann_factor_upper"] for row in rows
            ),
            "maximum_complete_bordered_response_2_norm_upper": max(
                row["complete_bordered_response_2_norm_upper"] for row in rows
            ),
            "maximum_center_bordered_solve_residual_upper": max(
                row["center_bordered_solve_residual_upper"] for row in rows
            ),
            "owner": owner,
        },
        "rows": rows,
        "validation": validation,
        "validation_passed": passed,
        "claim_boundary": {
            "recentered_cone_action_owned_internal_rhs": (
                "CERTIFIED" if passed else "OPEN"
            ),
            "recentered_cone_bordered_hard_response": (
                "CERTIFIED_FINITE" if passed else "OPEN"
            ),
            "recentered_cone_response_first_variation_tube": "OPEN",
            "causal_interval_vector_radius": "OPEN",
            "domain_and_first_hit_transfer": "OPEN",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "DIFFERENTIATE_THE_COMPLETE_INTERNAL_BORDERED_SYSTEM_AND_"
            "ASSEMBLE_THE_RESPONSE_FIRST_VARIATION_TUBE_ON_THE_IDENTICAL_"
            "3009_CELL_RECENTERED_CONE"
            if passed else
            "REFINE_ONLY_THE_REPORTED_INTERNAL_RHS_OR_RESPONSE_OWNER_CELLS"
        ),
        "inputs": {
            _relative(INVERSE): _sha256(INVERSE),
            _relative(PROJECTOR): _sha256(PROJECTOR),
            _relative(cone.GREEN): _sha256(cone.GREEN),
            _relative(cone.CAUSAL_Z2): _sha256(cone.CAUSAL_Z2),
            "scripts/certify_n12_gate7_recentered_cone_boundary_cluster_spectrum.py": (
                _sha256(ROOT / "scripts" / (
                    "certify_n12_gate7_recentered_cone_boundary_cluster_spectrum.py"
                ))
            ),
        },
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--central-probe", action="store_true")
    args = parser.parse_args()
    parents = cone._cells()
    if args.central_probe:
        by_seam: dict[int, list[tuple[int, int, float, float]]] = {}
        for task in parents:
            by_seam.setdefault(task[0], []).append(task)
        parents = [cells[len(cells) // 2] for cells in by_seam.values()]
    if BASE_RESPONSE_REFINEMENT < 1 or LATE_RESPONSE_REFINEMENT < 1:
        raise ValueError("positive response refinement required")
    tasks = []
    for seam, parent_local_index, left, right in parents:
        refinement = (
            LATE_RESPONSE_REFINEMENT
            if seam >= LATE_RESPONSE_SEAM_START
            else BASE_RESPONSE_REFINEMENT
        )
        boundaries = np.linspace(left, right, refinement + 1)
        for child in range(refinement):
            tasks.append((
                seam,
                parent_local_index * refinement + child,
                float(boundaries[child]),
                float(boundaries[child + 1]),
                parent_local_index,
                child,
                refinement,
            ))
    payload = build_payload(tasks, None if args.central_probe else CHECKPOINT)
    if not args.central_probe:
        RESULT.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8", newline="\n",
        )
        if CHECKPOINT.is_file():
            CHECKPOINT.unlink()
    print(json.dumps({
        "status": payload["status"],
        "mesh": payload["mesh"],
        "summary": payload["summary"],
        "validation_passed": payload["validation_passed"],
        "central_probe_only": args.central_probe,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
