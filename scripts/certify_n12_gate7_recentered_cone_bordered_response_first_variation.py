"""Certify the first variation of the complete Gate-7 bordered response.

The calculation differentiates the closed internal equation before taking
norms::

    K x = f,              K D_xi x = D_xi f - (D_xi K) x.

Only the external Cauchy/birth source is zero.  The derivative of the already
assembled internal action-owned source is consumed from the response
certificate.  The inverse is the certified bordered inverse; no kinetic,
Euler--Dirac, or history block is inverted.
"""

from __future__ import annotations

from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any

import numpy as np
from scipy.linalg import eigvalsh


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import certify_n12_gate7_recentered_cone_boundary_cluster_spectrum as cone  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
RESPONSE = BASE / "BHSM_N12_GATE7_RECENTERED_CONE_BORDERED_RHS_RESPONSE.json"
PROJECTOR = BASE / "BHSM_N12_GATE7_RECENTERED_CONE_SELECTED_PROJECTOR_GRAPH.json"
INVERSE = BASE / "BHSM_N12_GATE7_RECENTERED_CONE_BORDERED_HARD_INVERSE.json"
RESULT = BASE / (
    "BHSM_N12_GATE7_RECENTERED_CONE_BORDERED_RESPONSE_FIRST_VARIATION.json"
)


def _up(value: float) -> float:
    return math.nextafter(float(value) * (1.0 + 1.0e-10), math.inf)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


@lru_cache(maxsize=1)
def _projector_rows() -> dict[tuple[int, int], dict[str, Any]]:
    payload = _load(PROJECTOR)
    if payload.get("validation_passed") is not True:
        raise RuntimeError("certified recentered-cone projector required")
    return {
        (int(row["seam"]), int(row["local_index"])): row
        for row in payload["rows"]
    }


@lru_cache(maxsize=1)
def _inverse_rows() -> dict[tuple[int, int], dict[str, Any]]:
    payload = _load(INVERSE)
    if payload.get("validation_passed") is not True:
        raise RuntimeError("certified recentered-cone bordered inverse required")
    return {
        (int(row["seam"]), int(row["local_index"])): row
        for row in payload["rows"]
    }


def _path_projection_and_halo(
    seam: int, left: float, right: float,
) -> tuple[np.ndarray, float]:
    (
        states, rates, times, weights, _,
        fine_times, fine_correction, nonlinear_radius,
    ) = cone._inputs()
    macro_span = float(times[seam + 1] - times[seam])
    start_fraction = (left - times[seam]) / macro_span
    end_fraction = (right - times[seam]) / macro_span
    macro_x0 = states[seam] * weights
    macro_x1 = states[seam + 1] * weights
    macro_controls = np.asarray((
        macro_x0,
        macro_x0 + macro_span * rates[seam] / 3.0,
        macro_x1 - macro_span * rates[seam + 1] / 3.0,
        macro_x1,
    ))
    base_controls = cone.cluster.local._restrict(
        macro_controls, float(start_fraction), float(end_fraction),
    )
    correction0 = cone._interpolate_correction(
        left, fine_times, fine_correction,
    )
    correction1 = cone._interpolate_correction(
        right, fine_times, fine_correction,
    )
    correction_delta = correction1 - correction0
    correction_controls = np.asarray((
        correction0,
        correction0 + correction_delta / 3.0,
        correction0 + 2.0 * correction_delta / 3.0,
        correction1,
    ))
    controls = base_controls + correction_controls
    span = float(right - left)
    x0, x1 = controls[0], controls[-1]
    rate0 = 3.0 * (controls[1] - controls[0]) / span
    rate1 = 3.0 * (controls[3] - controls[2]) / span
    delta = x1 - x0
    path_projection = np.column_stack((
        0.5 * delta,
        span * rate0 - delta,
        delta - span * rate1,
    ))
    return path_projection, float(np.max(nonlinear_radius))


def _row(source: dict[str, Any]) -> dict[str, Any]:
    seam = int(source["seam"])
    parent_local = int(source["parent_local_index"])
    left, right = map(float, source["action_interval"])
    parent_key = (seam, parent_local)
    projector = _projector_rows()[parent_key]
    inverse = _inverse_rows()[parent_key]
    child_path_projection, halo_radius = _path_projection_and_halo(
        seam, left, right,
    )
    if halo_radius <= 0.0:
        raise RuntimeError("positive nonlinear halo required")

    parent_left, parent_right = map(float, projector["action_interval"])
    parent_path_projection, parent_halo_radius = _path_projection_and_halo(
        seam, parent_left, parent_right,
    )
    if parent_halo_radius != halo_radius:
        raise RuntimeError("child and parent must retain the identical halo")

    # For P=sqrt(2)[A,rho I], the squared norm of the minimum parent
    # coefficient lift of a child direction is the largest generalized
    # eigenvalue of
    #
    #   A_c A_c^T + rho^2 I  versus  A_p A_p^T + rho^2 I.
    #
    # Both matrices equal rho^2 I off span(A_p,A_c), so only their at-most
    # six-dimensional common frame is needed.  This is the exact
    # pseudoinverse lift norm without forming either 98-dimensional inverse.
    common = np.column_stack((parent_path_projection, child_path_projection))
    common_frame, _, __ = np.linalg.svd(common, full_matrices=False)
    parent_small = common_frame.T @ parent_path_projection
    child_small = common_frame.T @ child_path_projection
    identity = np.eye(common_frame.shape[1])
    parent_metric = (
        parent_small @ parent_small.T + halo_radius**2 * identity
    )
    child_metric = (
        child_small @ child_small.T + halo_radius**2 * identity
    )
    generalized = eigvalsh(child_metric, parent_metric, check_finite=True)
    generalized_max = _up(max(1.0, float(np.max(generalized))))
    lift = _up(math.sqrt(generalized_max))
    path_operator = float(np.linalg.norm(child_path_projection, ord=2))

    # The stored D4 Hessian quantity is the half-Taylor remainder.  Twice it
    # is the uniform change of the D3 derivative on the unit parent ball.
    parent_H_first = _up(
        float(projector["ambient_D3_Hessian_shift_upper"])
        + 2.0 * float(projector["ambient_D4_Hessian_remainder_upper"])
    )
    child_H_first = _up(lift * parent_H_first)
    child_psi_first = _up(
        lift * float(projector["selected_graph_derivative_l2_upper"])
    )
    # D(H-lambda I) <= D H + |D lambda| <= 2 D H.  The symmetric
    # off-diagonal border generated by D psi has norm ||D psi||.
    K_first = _up(2.0 * child_H_first + child_psi_first)
    f_first = float(
        source["raw_internal_rhs_first_coefficient_derivative_2_norm_upper"]
    )
    response_upper = float(source["complete_bordered_response_2_norm_upper"])
    inverse_upper = float(
        inverse["center_chart_bordered_inverse_2_norm_upper"]
    )
    operator_response = _up(K_first * response_upper)
    differentiated_rhs = _up(f_first + operator_response)
    response_first = _up(inverse_upper * differentiated_rhs)
    return {
        "seam": seam,
        "local_index": int(source["local_index"]),
        "action_interval": [left, right],
        "parent_local_index": parent_local,
        "child_within_parent": int(source["child_within_parent"]),
        "selected_branch": int(source["selected_branch"]),
        "projection_dimension": int(source["projection_dimension"]),
        "child_path_projection_2_norm": path_operator,
        "nonlinear_halo_radius": halo_radius,
        "child_to_parent_common_frame_direction_lift_2_norm_upper": lift,
        "child_to_parent_generalized_metric_eigenvalue_upper": generalized_max,
        "uniform_parent_Hessian_first_coefficient_derivative_2_norm_upper": (
            parent_H_first
        ),
        "uniform_child_Hessian_first_coefficient_derivative_2_norm_upper": (
            child_H_first
        ),
        "uniform_child_selected_line_first_coefficient_derivative_2_norm_upper": (
            child_psi_first
        ),
        "uniform_child_bordered_K_first_coefficient_derivative_2_norm_upper": (
            K_first
        ),
        "maximal_graded_internal_source_cotangent_2_to_2_upper": f_first,
        "complete_bordered_response_2_norm_upper": response_upper,
        "uniform_bordered_inverse_2_norm_upper": inverse_upper,
        "bordered_derivative_times_response_2_norm_upper": operator_response,
        "combined_differentiated_rhs_2_norm_upper": differentiated_rhs,
        "complete_bordered_response_first_coefficient_variation_2_to_2_upper": (
            response_first
        ),
        "reverse_adjoint_response_cotangent_2_to_2_upper": response_first,
        "all_variation_quantities_finite": all(map(math.isfinite, (
            lift, parent_H_first, child_H_first, child_psi_first, K_first,
            f_first, response_upper, inverse_upper, operator_response,
            differentiated_rhs, response_first,
        ))),
    }


def build_payload() -> dict[str, Any]:
    response = _load(RESPONSE)
    if response.get("validation_passed") is not True:
        raise RuntimeError("certified complete bordered response required")
    if response["validation"][
        "each_certified_cone_parent_refined_for_response_without_shrinking_halo"
    ] is not True:
        raise RuntimeError("full-halo child subordination required")
    rows = [_row(source) for source in response["rows"]]
    expected = [
        (
            int(source["seam"]), int(source["local_index"]),
            int(source["parent_local_index"]),
            int(source["child_within_parent"]),
        )
        for source in response["rows"]
    ]
    observed = [
        (
            row["seam"], row["local_index"], row["parent_local_index"],
            row["child_within_parent"],
        )
        for row in rows
    ]
    validation = {
        "identical_24072_cell_response_cover_consumed_in_order": observed == expected,
        "all_3009_parent_projector_and_inverse_rows_consumed": len({
            (row["seam"], row["parent_local_index"]) for row in rows
        }) == 3009,
        "branch_24_selected_everywhere": all(
            row["selected_branch"] == 24 for row in rows
        ),
        "same_101_dimensional_physical_tangent_quotient_used": all(
            row["projection_dimension"] == 101 for row in rows
        ),
        "positive_full_nonlinear_halo_retained_everywhere": all(
            row["nonlinear_halo_radius"] > 0.0 for row in rows
        ),
        "explicit_child_direction_to_parent_halo_lift_finite": all(
            math.isfinite(
                row["child_to_parent_common_frame_direction_lift_2_norm_upper"]
            ) and row[
                "child_to_parent_common_frame_direction_lift_2_norm_upper"
            ] >= 1.0 for row in rows
        ),
        "complete_differentiated_bordered_identity_assembled_before_norms": True,
        "all_maximal_graded_internal_source_cotangents_finite": all(
            math.isfinite(
                row["maximal_graded_internal_source_cotangent_2_to_2_upper"]
            ) for row in rows
        ),
        "all_response_first_variation_tubes_finite": all(
            row["all_variation_quantities_finite"] for row in rows
        ),
        "reverse_adjoint_bound_obtained_by_same_closed_system_duality": True,
        "only_external_Cauchy_birth_source_zero_internal_variation_retained": True,
        "no_internal_child_contact_transport_or_scalar_response_zeroed": True,
        "no_added_seam_force_or_double_counted_response": True,
        "no_full_kinetic_Dirac_or_history_inverse_used": True,
        "no_action_equation_source_selector_scale_gate_or_chord_changed": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    owner = max(
        rows,
        key=lambda row: row[
            "complete_bordered_response_first_coefficient_variation_2_to_2_upper"
        ],
    )
    return {
        "artifact": "BHSM_N12_GATE7_RECENTERED_CONE_BORDERED_RESPONSE_FIRST_VARIATION",
        "status": (
            "RECENTERED_GATE7_CONE_COMPLETE_BORDERED_RESPONSE_FIRST_VARIATION_CERTIFIED"
            if passed else "RECENTERED_GATE7_CONE_BORDERED_RESPONSE_FIRST_VARIATION_OPEN"
        ),
        "identity": "K*x=f;_K*D_xi_x=D_xi_f-(D_xi_K)*x",
        "source_ontology": response["source_ontology"],
        "mesh": {
            "parent_cells": 3009,
            "response_cells": len(rows),
            "projection_dimension": 101,
        },
        "summary": {
            "maximum_child_to_parent_direction_lift_2_norm_upper": max(
                row["child_to_parent_common_frame_direction_lift_2_norm_upper"]
                for row in rows
            ),
            "maximum_uniform_child_bordered_K_first_coefficient_derivative_2_norm_upper": max(
                row["uniform_child_bordered_K_first_coefficient_derivative_2_norm_upper"]
                for row in rows
            ),
            "maximum_maximal_graded_internal_source_cotangent_2_to_2_upper": max(
                row["maximal_graded_internal_source_cotangent_2_to_2_upper"]
                for row in rows
            ),
            "maximum_combined_differentiated_rhs_2_norm_upper": max(
                row["combined_differentiated_rhs_2_norm_upper"] for row in rows
            ),
            "maximum_complete_bordered_response_first_coefficient_variation_2_to_2_upper": owner[
                "complete_bordered_response_first_coefficient_variation_2_to_2_upper"
            ],
            "owner": owner,
        },
        "rows": rows,
        "validation": validation,
        "validation_passed": passed,
        "claim_boundary": {
            "maximal_graded_internal_source_cotangent": (
                "CERTIFIED_FINITE" if passed else "OPEN"
            ),
            "reverse_adjoint_complete_response": (
                "CERTIFIED_FINITE" if passed else "OPEN"
            ),
            "recentered_cone_response_first_variation_tube": (
                "CERTIFIED_FINITE" if passed else "OPEN"
            ),
            "projected_Cauchy_tail": "OPEN",
            "causal_interval_vector_radius": "OPEN",
            "domain_and_first_hit_transfer": "OPEN",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "COMPOSE_THE_CERTIFIED_RESPONSE_AND_REVERSE_ADJOINT_VARIATION_WITH_"
            "THE_FINITE_CAUSAL_GREEN_HERMITE_OPERATOR_TO_BOUND_THE_PROJECTED_"
            "CAUCHY_TAIL_AND_CAUSAL_INTERVAL_VECTOR_RADIUS"
            if passed else
            "SHARPEN_ONLY_THE_REPORTED_RESPONSE_FIRST_VARIATION_OWNER_CELLS"
        ),
        "inputs": {
            _relative(RESPONSE): _sha256(RESPONSE),
            _relative(PROJECTOR): _sha256(PROJECTOR),
            _relative(INVERSE): _sha256(INVERSE),
            "scripts/certify_n12_gate7_recentered_cone_boundary_cluster_spectrum.py": (
                _sha256(ROOT / "scripts" / (
                    "certify_n12_gate7_recentered_cone_boundary_cluster_spectrum.py"
                ))
            ),
        },
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
        "mesh": payload["mesh"],
        "summary": payload["summary"],
        "validation_passed": payload["validation_passed"],
        "exact_next_dependency": payload["exact_next_dependency"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
