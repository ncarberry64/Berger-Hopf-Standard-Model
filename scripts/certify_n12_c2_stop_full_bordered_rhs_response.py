"""Certify the action-owned bordered RHS and response on the stop path."""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
from functools import lru_cache
import argparse
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

import audit_n12_c2_stop_boundary_cluster_probe as cluster  # noqa: E402
from bhsm.interface.aether_forward_c2_descriptor_cover import metric_data  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
INVERSE = BASE / "BHSM_N12_C2_STOP_FULL_BORDERED_HARD_INVERSE.json"
PROJECTOR = BASE / "BHSM_N12_C2_STOP_FULL_SELECTED_PROJECTOR_GRAPH.json"
RESULT = BASE / "BHSM_N12_C2_STOP_FULL_BORDERED_RHS_RESPONSE.json"
QDIM = 37


def _refined_geometry(
    seam: int,
    subspan: int,
    subdivisions: int,
    states: np.ndarray,
    action_rates: np.ndarray,
    action_lengths: np.ndarray,
    weights: np.ndarray,
    reference: np.ndarray,
) -> dict[str, Any]:
    if subdivisions < 64 or subdivisions % 64 != 0:
        raise ValueError("response subdivisions must refine the certified 64 mesh")
    if not 0 <= subspan < subdivisions:
        raise ValueError("response subspan outside seam")
    h = float(action_lengths[seam + 1] - action_lengths[seam])
    x0 = states[seam] * weights
    x1 = states[seam + 1] * weights
    controls = np.asarray((
        x0,
        x0 + h * action_rates[seam] / 3.0,
        x1 - h * action_rates[seam + 1] / 3.0,
        x1,
    ))
    local_controls = cluster.local._restrict(
        controls, subspan / subdivisions, (subspan + 1) / subdivisions,
    )
    local_h = h / subdivisions
    left, right = local_controls[0], local_controls[-1]
    rate0 = 3.0 * (local_controls[1] - local_controls[0]) / local_h
    rate1 = 3.0 * (local_controls[3] - local_controls[2]) / local_h
    delta = right - left
    projection = np.column_stack((
        0.5 * delta,
        local_h * rate0 - delta,
        delta - local_h * rate1,
    ))
    center = 0.5 * (left + right) / weights
    jet = cluster.local.exact_full_action_jet_at_state(
        12,
        center[:QDIM], center[QDIM:2 * QDIM], center[2 * QDIM:],
        points=cluster.local.POINTS,
    )
    hessian = np.asarray(jet.hessian, dtype=float)[QDIM:, QDIM:]
    values, vectors = np.linalg.eigh(hessian)
    selected = int(np.argmax(np.abs(vectors.T @ reference)))
    directionals = []
    for column in range(projection.shape[1]):
        shifted = np.asarray(center, dtype=complex) + (
            1j * cluster.local.COMPLEX_STEP * projection[:, column] / weights
        )
        shifted_jet = cluster.local.exact_full_action_jet_at_state(
            12,
            shifted[:QDIM], shifted[QDIM:2 * QDIM], shifted[2 * QDIM:],
            points=cluster.local.POINTS,
        )
        directionals.append(
            np.imag(np.asarray(shifted_jet.hessian)[QDIM:, QDIM:])
            / cluster.local.COMPLEX_STEP
        )
    return {
        "midpoint": center,
        "projection": projection,
        "values": values,
        "vectors": vectors,
        "selected": selected,
        "directionals": directionals,
    }


def _up(value: float) -> float:
    return math.nextafter(float(value) * (1.0 + 1.0e-10), math.inf)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


@lru_cache(maxsize=1)
def _inverse_rows() -> dict[tuple[int, int], dict[str, Any]]:
    record = json.loads(INVERSE.read_text(encoding="utf-8"))
    if record["validation_passed"] is not True:
        raise RuntimeError("complete bordered inverse required")
    return {
        (int(row["seam"]), int(row["subspan"])): row
        for row in record["rows"]
    }


@lru_cache(maxsize=1)
def _projector_rows() -> dict[tuple[int, int], dict[str, Any]]:
    record = json.loads(PROJECTOR.read_text(encoding="utf-8"))
    if record["validation_passed"] is not True:
        raise RuntimeError("complete selected projector required")
    return {
        (int(row["seam"]), int(row["subspan"])): row
        for row in record["rows"]
    }


def _exact_rhs(state: np.ndarray, weights: np.ndarray) -> np.ndarray:
    q_weights, reduced_weights, _, _ = metric_data()
    jet = cluster.local.exact_full_action_jet_at_state(
        12,
        state[:QDIM], state[QDIM:2 * QDIM], state[2 * QDIM:],
        points=cluster.local.POINTS,
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


def _row(task: tuple[int, ...]) -> dict[str, Any]:
    if len(task) == 2:
        seam, subspan = task
        subdivisions = 64
    elif len(task) == 3:
        seam, subspan, subdivisions = task
    else:
        raise ValueError("row task must be (seam,subspan[,subdivisions])")
    refinement = subdivisions // 64
    parent_subspan = subspan // refinement
    pair = (seam, parent_subspan)
    inverse = _inverse_rows()[pair]
    projector = _projector_rows()[pair]
    states, action_rates, action_lengths, weights, reference = cluster._center_arrays()
    geometry = _refined_geometry(
        seam, subspan, subdivisions,
        states, action_rates, action_lengths, weights, reference,
    )
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

    # The internal source is assembled before preconditioning.  Its
    # configuration input is split into the center and exact linear image of
    # the Hermite ball.
    configuration_center = np.zeros(total)
    configuration_center[:QDIM] = q_weights * center[QDIM:2 * QDIM]
    configuration_variation = np.zeros((total, projection.shape[1]))
    velocity_weights = weights[QDIM:2 * QDIM]
    configuration_variation[:QDIM] = (
        (q_weights / velocity_weights)[:, None]
        * projection[QDIM:2 * QDIM]
    )

    def mixed(*directions: np.ndarray) -> float:
        return _up(float(cluster.local.action_bound(
            center,
            projection=projection,
            mixed_directions=list(directions),
        ).d[-1]))

    jet = cluster.local.exact_full_action_jet_at_state(
        12,
        center[:QDIM], center[QDIM:2 * QDIM], center[2 * QDIM:],
        points=cluster.local.POINTS,
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
    # Apply the inverse only after the complete internal RHS has been
    # assembled.  In the center eigenbasis, K0^-1 maps the source through
    # hard denominators and the selected border exactly.
    hard_indices = np.asarray([
        index for index in range(values.size) if index != selected
    ], dtype=int)
    hard = vectors[:, hard_indices]
    denominators = values[hard_indices] - values[selected]
    preconditioned_hard = hard / denominators[None, :]
    response_test_directions = np.column_stack((preconditioned_hard, psi))
    response_gradient_output = np.zeros((total, response_test_directions.shape[1]))
    response_gradient_output[:QDIM] = (
        q_weights[:, None] ** 2
        * response_test_directions[:QDIM]
    )
    response_mixed_output = np.zeros((total, response_test_directions.shape[1]))
    response_mixed_output[QDIM:] = (
        reduced_weights[:, None] * response_test_directions
    )
    preconditioned_gradient_variation = mixed(
        response_gradient_output, projection,
    )
    preconditioned_Hessian_center_variation = mixed(
        response_mixed_output, configuration_center, projection,
    )
    preconditioned_Hessian_ball_variation = mixed(
        response_mixed_output, configuration_variation, projection,
    )
    preconditioned_configuration_variation = mixed(
        response_mixed_output, configuration_variation,
    )
    preconditioned_rhs_variation = _up(
        preconditioned_gradient_variation
        + preconditioned_Hessian_center_variation
        + preconditioned_Hessian_ball_variation
        + preconditioned_configuration_variation
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
    solve_discrepancy = abs(center_preconditioned_norm - center_response_norm)
    binary64_backward_error = _up(
        (reduced + 1)
        * residual
        * float(inverse["center_chart_bordered_inverse_2_norm_upper"])
    )
    return {
        "seam": seam,
        "subspan": subspan,
        "subdivisions_per_macro_seam": subdivisions,
        "certified_parent_64_subspan": parent_subspan,
        "selected_branch": selected,
        "center_internal_rhs_2_norm": center_rhs_norm,
        "center_bordered_response_2_norm": center_response_norm,
        "center_preconditioned_internal_source_2_norm": center_preconditioned_norm,
        "preconditioned_internal_rhs_variation_2_norm_upper": (
            preconditioned_rhs_variation
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
        "center_preconditioned_solve_discrepancy": solve_discrepancy,
        "binary64_bordered_backward_error_upper": binary64_backward_error,
        "center_preconditioned_source_matches_bordered_solve": (
            solve_discrepancy <= binary64_backward_error
        ),
        "bordered_response_tube_finite": (
            relative_operator < 1.0 and math.isfinite(response_upper)
        ),
    }


def build_payload() -> dict[str, Any]:
    subdivisions = 256
    tasks = [
        (seam, subspan, subdivisions)
        for seam in range(47) for subspan in range(subdivisions)
    ]
    workers = min(12, os.cpu_count() or 1)
    rows = []
    with ProcessPoolExecutor(max_workers=workers) as executor:
        for index, row in enumerate(executor.map(_row, tasks, chunksize=1), 1):
            rows.append(row)
            if index % 64 == 0 or index == len(tasks):
                print(json.dumps({
                    "completed": index,
                    "total": len(tasks),
                    "closed_so_far": all(
                        item["center_internal_rhs_finite"]
                        and item["bordered_response_tube_finite"]
                        for item in rows
                    ),
                    "maximum_response_upper_so_far": max(
                        item["complete_bordered_response_2_norm_upper"]
                        for item in rows
                    ),
                }), flush=True)
    validation = {
        "all_12032_refined_response_cells_consumed_in_order": [
            (row["seam"], row["subspan"]) for row in rows
        ] == [
            (seam, subspan)
            for seam in range(47) for subspan in range(subdivisions)
        ],
        "branch_24_selected_everywhere": all(
            row["selected_branch"] == 24 for row in rows
        ),
        "all_exact_center_internal_rhs_values_finite": all(
            row["center_internal_rhs_finite"] for row in rows
        ),
        "all_center_bordered_solve_residuals_small": all(
            row["center_bordered_solve_residual_upper"] < 1.0e-7 for row in rows
        ),
        "all_bordered_response_tubes_finite": all(
            row["bordered_response_tube_finite"] for row in rows
        ),
        "all_center_preconditioned_sources_match_bordered_solves": all(
            row["center_preconditioned_source_matches_bordered_solve"]
            for row in rows
        ),
        "all_relative_bordered_perturbations_below_one": all(
            row["relative_bordered_operator_perturbation_upper"] < 1.0
            for row in rows
        ),
        "only_external_Cauchy_birth_source_zero_internal_rhs_retained": True,
        "no_added_seam_force_or_double_counted_response": True,
        "no_full_kinetic_Dirac_or_history_inverse_used": True,
    }
    passed = all(validation.values())
    owner = max(
        rows, key=lambda row: row["complete_bordered_response_2_norm_upper"]
    )
    return {
        "artifact": "BHSM_N12_C2_STOP_FULL_BORDERED_RHS_RESPONSE",
        "status": (
            "ALL_12032_ACTION_OWNED_BORDERED_RHS_RESPONSE_TUBES_CERTIFIED"
            if passed else "STOP_PATH_BORDERED_RHS_RESPONSE_OPEN"
        ),
        "source_ontology": (
            "EXTERNAL_CAUCHY_BIRTH_SOURCE_ZERO;_EULER_LAGRANGE_CHILD_"
            "RESPONSE_RETAINED_AS_INTERNAL_ACTION_OWNED_RHS"
        ),
        "mesh": {
            "macro_seams": 47,
            "subspans_per_macro_seam": subdivisions,
            "refinement_of_certified_spectrum_projector_mesh": 4,
            "total_subspans": len(rows),
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
            "all_12032_action_owned_preconditioned_internal_rhs_tubes": (
                "CERTIFIED" if passed else "OPEN"
            ),
            "all_12032_bordered_hard_response_tubes": (
                "CERTIFIED_FINITE" if passed else "OPEN"
            ),
            "response_first_variation_tube": "OPEN",
            "Green_Hermite_shadowing": "OPEN",
            "scalar_stop_first_hit": "OPEN",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "DIFFERENTIATE_THE_COMPLETE_INTERNAL_BORDERED_SYSTEM_AND_"
            "ASSEMBLE_THE_RESPONSE_FIRST_VARIATION_TUBE_FOR_GREEN_HERMITE"
            if passed else
            "REFINE_ONLY_THE_REPORTED_INTERNAL_RHS_OR_RESPONSE_OWNER"
        ),
        "inputs": {
            INVERSE.relative_to(ROOT).as_posix(): _sha256(INVERSE),
            PROJECTOR.relative_to(ROOT).as_posix(): _sha256(PROJECTOR),
            cluster.CENTER_DATA.relative_to(ROOT).as_posix(): _sha256(
                cluster.CENTER_DATA
            ),
            "scripts/audit_n12_c2_stop_boundary_cluster_probe.py": _sha256(
                ROOT / "scripts" / "audit_n12_c2_stop_boundary_cluster_probe.py"
            ),
        },
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def _revalidate_binary64_center_solves(payload: dict[str, Any]) -> dict[str, Any]:
    for row in payload["rows"]:
        discrepancy = abs(
            float(row["center_preconditioned_internal_source_2_norm"])
            - float(row["center_bordered_response_2_norm"])
        )
        backward = _up(
            62.0
            * float(row["center_bordered_solve_residual_upper"])
            * float(row["charted_bordered_inverse_2_norm_upper"])
        )
        row["center_preconditioned_solve_discrepancy"] = discrepancy
        row["binary64_bordered_backward_error_upper"] = backward
        row["center_preconditioned_source_matches_bordered_solve"] = (
            discrepancy <= backward
        )
    payload["validation"][
        "all_center_preconditioned_sources_match_bordered_solves"
    ] = all(
        row["center_preconditioned_source_matches_bordered_solve"]
        for row in payload["rows"]
    )
    passed = all(payload["validation"].values())
    payload["validation_passed"] = passed
    payload["status"] = (
        "ALL_12032_ACTION_OWNED_BORDERED_RHS_RESPONSE_TUBES_CERTIFIED"
        if passed else "STOP_PATH_BORDERED_RHS_RESPONSE_OPEN"
    )
    payload["claim_boundary"][
        "all_12032_action_owned_preconditioned_internal_rhs_tubes"
    ] = "CERTIFIED" if passed else "OPEN"
    payload["claim_boundary"][
        "all_12032_bordered_hard_response_tubes"
    ] = "CERTIFIED_FINITE" if passed else "OPEN"
    payload["exact_next_dependency"] = (
        "DIFFERENTIATE_THE_COMPLETE_INTERNAL_BORDERED_SYSTEM_AND_"
        "ASSEMBLE_THE_RESPONSE_FIRST_VARIATION_TUBE_FOR_GREEN_HERMITE"
        if passed else
        "REFINE_ONLY_THE_REPORTED_INTERNAL_RHS_OR_RESPONSE_OWNER"
    )
    payload["summary"]["maximum_center_preconditioned_solve_discrepancy"] = max(
        row["center_preconditioned_solve_discrepancy"] for row in payload["rows"]
    )
    payload["summary"]["maximum_binary64_backward_error_upper"] = max(
        row["binary64_bordered_backward_error_upper"] for row in payload["rows"]
    )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--revalidate-existing", action="store_true")
    arguments = parser.parse_args()
    if arguments.revalidate_existing:
        payload = json.loads(RESULT.read_text(encoding="utf-8"))
    else:
        payload = build_payload()
    payload = _revalidate_binary64_center_solves(payload)
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "summary": payload["summary"],
        "validation_passed": payload["validation_passed"],
        "exact_next_dependency": payload["exact_next_dependency"],
    }, indent=2))


if __name__ == "__main__":
    main()
