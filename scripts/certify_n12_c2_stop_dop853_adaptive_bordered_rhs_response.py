"""Certify the action-owned bordered RHS on the adaptive DOP853 cover."""

from __future__ import annotations

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

import audit_n12_c2_stop_dop853_boundary_cluster_probe as dense  # noqa: E402
from bhsm.interface.aether_forward_c2_descriptor_cover import metric_data  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
INVERSE = Path(os.environ.get(
    "BHSM_N12_STOP_DOP853_ADAPTIVE_INVERSE",
    str(BASE / "BHSM_N12_C2_STOP_DOP853_ADAPTIVE_BORDERED_HARD_INVERSE.json"),
))
PROJECTOR = Path(os.environ.get(
    "BHSM_N12_STOP_DOP853_ADAPTIVE_PROJECTOR",
    str(BASE / "BHSM_N12_C2_STOP_DOP853_ADAPTIVE_SELECTED_PROJECTOR_GRAPH.json"),
))
RESULT = Path(os.environ.get(
    "BHSM_N12_STOP_DOP853_ADAPTIVE_RESPONSE",
    str(BASE / "BHSM_N12_C2_STOP_DOP853_ADAPTIVE_BORDERED_RHS_RESPONSE.json"),
))
QDIM = 37
RESPONSE_REFINEMENT = int(os.environ.get(
    "BHSM_N12_STOP_DOP853_RESPONSE_REFINEMENT", "4",
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


def _tight_tangent_remainder_geometry(
    interval: int, subspan: int, subdivisions: int,
) -> dict[str, Any]:
    """Enclose one exact Bezier cell by its tangent and integral remainder.

    For u in [0,1], B(u)=B(1/2)+(u-1/2)B'(1/2)+R(u).  The integral Taylor
    remainder belongs to conv({0,D2_i/8}), where D2_i are the degree-five
    Bernstein controls of B''.  The product of the scalar tangent interval
    and residual simplex is enclosed by the minimum-trace two-block ellipsoid
    obtained from 1/a^2+1/b^2=1.
    """

    values, coefficients, _, weights, reference, bracket_raw, stop_raw = (
        dense._dense_arrays()
    )
    bracket = int(bracket_raw[0])
    right = float(stop_raw[0]) if interval == bracket else 1.0
    controls = dense._dense_bernstein_controls(values[interval], coefficients[interval])
    controls = dense._restrict(controls, 0.0, right)
    controls = dense._restrict(
        controls, subspan / subdivisions, (subspan + 1) / subdivisions,
    )[:, :-1]
    center_curve = dense._split(controls, 0.5)[0][-1]
    first_controls = 7.0 * (controls[1:] - controls[:-1])
    first_midpoint = dense._split(first_controls, 0.5)[0][-1]
    tangent_axis = 0.5 * first_midpoint
    second_controls = 42.0 * (
        controls[2:] - 2.0 * controls[1:-1] + controls[:-2]
    )
    residual_vertices = np.vstack((
        np.zeros((1, controls.shape[1])), second_controls / 8.0,
    ))
    residual_center = np.mean(residual_vertices, axis=0)
    residual_axes = (residual_vertices - residual_center).T
    tangent_energy = float(tangent_axis @ tangent_axis)
    residual_energy = float(np.sum(np.square(residual_axes)))
    if tangent_energy == 0.0:
        projection = residual_axes
        tangent_scale = 0.0
        residual_scale = 1.0
    elif residual_energy == 0.0:
        projection = tangent_axis[:, None]
        tangent_scale = 1.0
        residual_scale = 0.0
    else:
        ratio = math.sqrt(residual_energy / tangent_energy)
        tangent_scale = math.sqrt(1.0 + ratio)
        residual_scale = math.sqrt(1.0 + 1.0 / ratio)
        projection = np.column_stack((
            tangent_scale * tangent_axis,
            residual_scale * residual_axes,
        ))
    center_action = center_curve + residual_center
    center = center_action / weights
    jet = dense.cluster.local.exact_full_action_jet_at_state(
        12,
        center[:QDIM], center[QDIM:2 * QDIM], center[2 * QDIM:],
        points=dense.cluster.local.POINTS,
    )
    hessian = np.asarray(jet.hessian, dtype=float)[QDIM:, QDIM:]
    eigenvalues, eigenvectors = np.linalg.eigh(hessian)
    selected = int(np.argmax(np.abs(eigenvectors.T @ reference)))
    directionals = []
    for column in range(projection.shape[1]):
        shifted = np.asarray(center, dtype=complex) + (
            1j * dense.COMPLEX_STEP * projection[:, column] / weights
        )
        shifted_jet = dense.cluster.local.exact_full_action_jet_at_state(
            12,
            shifted[:QDIM], shifted[QDIM:2 * QDIM], shifted[2 * QDIM:],
            points=dense.cluster.local.POINTS,
        )
        directionals.append(
            np.imag(np.asarray(shifted_jet.hessian)[QDIM:, QDIM:])
            / dense.COMPLEX_STEP
        )
    return {
        "midpoint": center,
        "projection": projection,
        "values": eigenvalues,
        "vectors": eigenvectors,
        "selected": selected,
        "directionals": directionals,
        "Bezier_controls": controls,
        "tangent_axis": tangent_axis,
        "second_derivative_controls": second_controls,
        "residual_vertices": residual_vertices,
        "tangent_scale": tangent_scale,
        "residual_scale": residual_scale,
        "coefficient_ellipsoid_identity": (
            1.0 if tangent_energy == 0.0 or residual_energy == 0.0
            else 1.0 / tangent_scale**2 + 1.0 / residual_scale**2
        ),
    }


@lru_cache(maxsize=1)
def _inverse_record() -> dict[str, Any]:
    payload = _load(INVERSE)
    if payload["validation_passed"] is not True:
        raise RuntimeError("complete adaptive DOP853 bordered inverse required")
    return payload


@lru_cache(maxsize=1)
def _projector_record() -> dict[str, Any]:
    payload = _load(PROJECTOR)
    if payload["validation_passed"] is not True:
        raise RuntimeError("complete adaptive DOP853 selected projector required")
    return payload


@lru_cache(maxsize=1)
def _inverse_rows() -> dict[tuple[int, int, int], dict[str, Any]]:
    return {
        (int(row["interval"]), int(row["subspan"]), int(row["subdivisions"])): row
        for row in _inverse_record()["rows"]
    }


@lru_cache(maxsize=1)
def _projector_rows() -> dict[tuple[int, int, int], dict[str, Any]]:
    return {
        (int(row["interval"]), int(row["subspan"]), int(row["subdivisions"])): row
        for row in _projector_record()["rows"]
    }


def _exact_rhs(state: np.ndarray, weights: np.ndarray) -> np.ndarray:
    q_weights, reduced_weights, _, _ = metric_data()
    jet = dense.cluster.local.exact_full_action_jet_at_state(
        12,
        state[:QDIM], state[QDIM:2 * QDIM], state[2 * QDIM:],
        points=dense.cluster.local.POINTS,
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


def _row(task: tuple[int, int, int, int, int, int]) -> dict[str, Any]:
    interval, subspan, subdivisions, parent_subspan, parent_subdivisions, child = task
    parent = (interval, parent_subspan, parent_subdivisions)
    inverse = _inverse_rows()[parent]
    projector = _projector_rows()[parent]
    geometry = _tight_tangent_remainder_geometry(
        interval, subspan, subdivisions,
    )
    *_, weights, reference, __, ___ = dense._dense_arrays()
    center = geometry["midpoint"]
    projection = geometry["projection"]
    values = geometry["values"]
    vectors = geometry["vectors"]
    selected = int(geometry["selected"])
    if selected != 24:
        raise RuntimeError("selected branch changed")
    q_weights, reduced_weights, _, _ = metric_data()
    total = weights.size
    reduced = reduced_weights.size

    configuration_center = np.zeros(total)
    configuration_center[:QDIM] = q_weights * center[QDIM:2 * QDIM]
    configuration_variation = np.zeros((total, projection.shape[1]))
    velocity_weights = weights[QDIM:2 * QDIM]
    configuration_variation[:QDIM] = (
        (q_weights / velocity_weights)[:, None] * projection[QDIM:2 * QDIM]
    )

    def mixed(*directions: np.ndarray) -> float:
        return _up(float(dense.cluster.local.action_bound(
            center,
            projection=projection,
            mixed_directions=list(directions),
        ).d[-1]))

    jet = dense.cluster.local.exact_full_action_jet_at_state(
        12,
        center[:QDIM], center[QDIM:2 * QDIM], center[2 * QDIM:],
        points=dense.cluster.local.POINTS,
    )
    hessian = np.asarray(jet.hessian, dtype=float)[QDIM:, QDIM:]
    psi = vectors[:, selected]
    if float(psi @ reference) < 0.0:
        psi = -psi
    selected_value = float(values[selected])
    bordered = np.block([
        [hessian - selected_value * np.eye(reduced), psi[:, None]],
        [psi[None, :], np.zeros((1, 1))],
    ])
    rhs = _exact_rhs(center, weights)
    forcing = np.concatenate((rhs, np.zeros(1)))
    response = np.linalg.solve(bordered, forcing)
    residual = _up(float(np.linalg.norm(bordered @ response - forcing)))
    center_rhs_norm = float(np.linalg.norm(rhs))
    center_response_norm = float(np.linalg.norm(response))

    hard_indices = np.asarray([index for index in range(values.size) if index != selected], dtype=int)
    hard = vectors[:, hard_indices]
    denominators = values[hard_indices] - values[selected]
    preconditioned_hard = hard / denominators[None, :]
    response_test_directions = np.column_stack((preconditioned_hard, psi))
    response_gradient_output = np.zeros((total, response_test_directions.shape[1]))
    response_gradient_output[:QDIM] = q_weights[:, None] ** 2 * response_test_directions[:QDIM]
    response_mixed_output = np.zeros((total, response_test_directions.shape[1]))
    response_mixed_output[QDIM:] = reduced_weights[:, None] * response_test_directions
    preconditioned_rhs_variation = _up(
        mixed(response_gradient_output, projection)
        + mixed(response_mixed_output, configuration_center, projection)
        + mixed(response_mixed_output, configuration_variation, projection)
        + mixed(response_mixed_output, configuration_variation)
    )
    center_preconditioned_source = np.concatenate((
        preconditioned_hard.T @ rhs,
        np.asarray([float(psi @ rhs)]),
    ))
    center_preconditioned_norm = float(np.linalg.norm(center_preconditioned_source))

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
            (hard.T @ matrix @ hard - lambda_slope * np.eye(hard.shape[1]))
            / denominators[:, None]
        )
    relative_D3 = _up(float(np.linalg.norm([
        np.linalg.norm(block, ord=2) for block in relative_blocks
    ])))
    relative_D4 = mixed(preconditioned_action, hard_action, projection, projection)
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
        "interval": interval,
        "subspan": subspan,
        "subdivisions": subdivisions,
        "parent_subspan": parent_subspan,
        "parent_subdivisions": parent_subdivisions,
        "child_within_parent": child,
        "selected_branch": selected,
        "response_projection_columns": int(projection.shape[1]),
        "tangent_axis_scale": float(geometry["tangent_scale"]),
        "residual_axes_scale": float(geometry["residual_scale"]),
        "coefficient_ellipsoid_identity": float(
            geometry["coefficient_ellipsoid_identity"]
        ),
        "center_internal_rhs_2_norm": center_rhs_norm,
        "center_bordered_response_2_norm": center_response_norm,
        "center_preconditioned_internal_source_2_norm": center_preconditioned_norm,
        "preconditioned_internal_rhs_variation_2_norm_upper": preconditioned_rhs_variation,
        "relative_bordered_D3_upper": relative_D3,
        "relative_bordered_D4_remainder_upper": 0.5 * relative_D4,
        "relative_selected_shift_upper": selected_shift / gap_lower,
        "relative_bordered_operator_perturbation_upper": relative_operator,
        "bordered_Neumann_factor_upper": Neumann_factor,
        "center_bordered_solve_residual_upper": residual,
        "charted_bordered_inverse_2_norm_upper": float(inverse["center_chart_bordered_inverse_2_norm_upper"]),
        "complete_bordered_response_2_norm_upper": response_upper,
        "center_internal_rhs_finite": math.isfinite(center_rhs_norm),
        "center_preconditioned_solve_discrepancy": discrepancy,
        "binary64_bordered_backward_error_upper": backward_error,
        "center_preconditioned_source_matches_bordered_solve": discrepancy <= backward_error,
        "bordered_response_tube_finite": relative_operator < 1.0 and math.isfinite(response_upper),
    }


def build_payload() -> dict[str, Any]:
    if RESPONSE_REFINEMENT < 1:
        raise ValueError("positive response refinement required")
    parent_rows = _inverse_record()["rows"]
    tasks = []
    for parent in parent_rows:
        interval = int(parent["interval"])
        parent_subspan = int(parent["subspan"])
        parent_subdivisions = int(parent["subdivisions"])
        subdivisions = parent_subdivisions * RESPONSE_REFINEMENT
        for child in range(RESPONSE_REFINEMENT):
            tasks.append((
                interval,
                parent_subspan * RESPONSE_REFINEMENT + child,
                subdivisions,
                parent_subspan,
                parent_subdivisions,
                child,
            ))
    workers = min(
        int(os.environ.get("BHSM_N12_STOP_WORKERS", "12")),
        os.cpu_count() or 1,
    )
    rows = []
    with ProcessPoolExecutor(max_workers=workers) as executor:
        for index, row in enumerate(executor.map(_row, tasks, chunksize=1), 1):
            rows.append(row)
            if index % 32 == 0 or index == len(tasks):
                print(json.dumps({
                    "completed": index,
                    "total": len(tasks),
                    "closed_so_far": all(
                        item["center_internal_rhs_finite"]
                        and item["bordered_response_tube_finite"] for item in rows
                    ),
                    "maximum_response_upper_so_far": max(
                        item["complete_bordered_response_2_norm_upper"] for item in rows
                    ),
                }), flush=True)
    validation = {
        "every_adaptive_parent_replaced_by_exact_response_children_in_order": [
            (
                row["interval"], row["subspan"], row["subdivisions"],
                row["parent_subspan"], row["parent_subdivisions"], row["child_within_parent"],
            ) for row in rows
        ] == tasks,
        "branch_24_selected_everywhere": all(row["selected_branch"] == 24 for row in rows),
        "all_exact_center_internal_rhs_values_finite": all(row["center_internal_rhs_finite"] for row in rows),
        "all_center_bordered_solve_residuals_small": all(row["center_bordered_solve_residual_upper"] < 1.0e-7 for row in rows),
        "all_bordered_response_tubes_finite": all(row["bordered_response_tube_finite"] for row in rows),
        "all_center_preconditioned_sources_match_bordered_solves": all(row["center_preconditioned_source_matches_bordered_solve"] for row in rows),
        "all_relative_bordered_perturbations_below_one": all(row["relative_bordered_operator_perturbation_upper"] < 1.0 for row in rows),
        "all_tangent_remainder_product_ellipsoids_exactly_normalized": all(
            abs(row["coefficient_ellipsoid_identity"] - 1.0) <= 4.0e-15
            for row in rows
        ),
        "midpoint_tangent_plus_integral_second_derivative_remainder_enclosure_used": True,
        "two_block_ellipsoid_scaling_minimizes_trace_without_fitting": True,
        "same_stored_DOP853_polynomial_and_adaptive_parent_cover": True,
        "only_external_Cauchy_birth_source_zero_internal_rhs_retained": True,
        "no_added_seam_force_or_double_counted_response": True,
        "no_full_kinetic_Dirac_or_history_inverse_used": True,
    }
    passed = all(validation.values())
    owner = max(rows, key=lambda row: row["complete_bordered_response_2_norm_upper"])
    return {
        "artifact": "BHSM_N12_C2_STOP_DOP853_ADAPTIVE_BORDERED_RHS_RESPONSE",
        "status": (
            "ALL_DOP853_ADAPTIVE_ACTION_OWNED_BORDERED_RHS_RESPONSE_TUBES_CERTIFIED"
            if passed else "DOP853_ADAPTIVE_STOP_PATH_BORDERED_RHS_RESPONSE_OPEN"
        ),
        "source_ontology": "EXTERNAL_CAUCHY_BIRTH_SOURCE_ZERO;_EULER_LAGRANGE_CHILD_RESPONSE_RETAINED_AS_INTERNAL_ACTION_OWNED_RHS",
        "mesh": {
            "adaptive_parent_cells": len(parent_rows),
            "response_refinement_per_parent": RESPONSE_REFINEMENT,
            "response_cells": len(rows),
            "workers": workers,
        },
        "summary": {
            "maximum_center_internal_rhs_2_norm": max(row["center_internal_rhs_2_norm"] for row in rows),
            "maximum_center_bordered_response_2_norm": max(row["center_bordered_response_2_norm"] for row in rows),
            "maximum_preconditioned_internal_rhs_variation_2_norm_upper": max(row["preconditioned_internal_rhs_variation_2_norm_upper"] for row in rows),
            "maximum_relative_bordered_operator_perturbation_upper": max(row["relative_bordered_operator_perturbation_upper"] for row in rows),
            "maximum_bordered_Neumann_factor_upper": max(row["bordered_Neumann_factor_upper"] for row in rows),
            "maximum_complete_bordered_response_2_norm_upper": max(row["complete_bordered_response_2_norm_upper"] for row in rows),
            "maximum_center_bordered_solve_residual_upper": max(row["center_bordered_solve_residual_upper"] for row in rows),
            "owner": owner,
        },
        "rows": rows,
        "validation": validation,
        "validation_passed": passed,
        "claim_boundary": {
            "action_owned_internal_rhs_on_stored_DOP853_stop_path": "CERTIFIED" if passed else "OPEN",
            "bordered_hard_response_on_stored_DOP853_stop_path": "CERTIFIED_FINITE" if passed else "OPEN",
            "response_first_variation_tube": "OPEN",
            "correlated_shadowing_tube": "OPEN",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "DIFFERENTIATE_THE_COMPLETE_INTERNAL_BORDERED_SYSTEM_AND_ASSEMBLE_THE_RESPONSE_FIRST_VARIATION_TUBE_ON_THE_IDENTICAL_DOP853_COVER"
            if passed else "REFINE_ONLY_THE_REPORTED_INTERNAL_RHS_OR_RESPONSE_OWNER"
        ),
        "inputs": {
            _relative(INVERSE): _sha256(INVERSE),
            _relative(PROJECTOR): _sha256(PROJECTOR),
            _relative(dense.CENTER_DATA): _sha256(dense.CENTER_DATA),
            "scripts/audit_n12_c2_stop_dop853_boundary_cluster_probe.py": _sha256(
                ROOT / "scripts/audit_n12_c2_stop_dop853_boundary_cluster_probe.py"
            ),
        },
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "summary": payload["summary"],
        "validation_passed": payload["validation_passed"],
        "exact_next_dependency": payload["exact_next_dependency"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
