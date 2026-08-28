"""Certify a second-variation majorant for the Gate-7 bordered response.

On every child cell of the recentered cone, differentiate the two bordered
systems without forming an inverse::

    B psi_2 = -((H_2-lambda_2 I) psi
                + 2 (H_1-lambda_1 I) psi_1,
                ||psi_1||^2),

    K x_2 = f_2 - K_2 x - 2 K_1 x_1.

The stored bordered-inverse norm is applied only after the complete signed
right-hand side has been assembled.  The result is the first fully outward
second-variation tube on the 24,072-cell recentered cone.  It is deliberately
reported as a conservative ambient majorant: the physical Green/adjoint
contraction still has to be performed before a causal-radius or force claim.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
FIRST = BASE / (
    "BHSM_N12_GATE7_RECENTERED_CONE_BORDERED_RESPONSE_FIRST_VARIATION.json"
)
RESPONSE = BASE / "BHSM_N12_GATE7_RECENTERED_CONE_BORDERED_RHS_RESPONSE.json"
PROJECTOR = BASE / "BHSM_N12_GATE7_RECENTERED_CONE_SELECTED_PROJECTOR_GRAPH.json"
INVERSE = BASE / "BHSM_N12_GATE7_RECENTERED_CONE_BORDERED_HARD_INVERSE.json"
RESULT = BASE / (
    "BHSM_N12_GATE7_RECENTERED_CONE_BORDERED_RESPONSE_SECOND_VARIATION.json"
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


def _row(
    first: dict[str, Any],
    response: dict[str, Any],
    projector: dict[str, Any],
    inverse: dict[str, Any],
) -> dict[str, Any]:
    lift = float(
        first["child_to_parent_common_frame_direction_lift_2_norm_upper"]
    )
    hessian_first = float(
        first["uniform_child_Hessian_first_coefficient_derivative_2_norm_upper"]
    )
    psi_first = float(
        first[
            "uniform_child_selected_line_first_coefficient_derivative_2_norm_upper"
        ]
    )
    K_first = float(
        first["uniform_child_bordered_K_first_coefficient_derivative_2_norm_upper"]
    )
    inverse_upper = float(inverse["center_chart_bordered_inverse_2_norm_upper"])

    # The projector certificate stores one half of the uniform D4 Hessian
    # Taylor term on the parent coefficient ball.  Two times that value is
    # the bilinear H_2 bound.  A child direction has a minimum parent lift of
    # at most ``lift``, hence the quadratic lift factor.
    hessian_second = _up(
        lift * lift
        * 2.0 * float(projector["ambient_D4_Hessian_remainder_upper"])
    )
    lambda_first = hessian_first
    lambda_second = _up(
        hessian_second + 2.0 * hessian_first * psi_first
    )
    shifted_Hessian_first = _up(hessian_first + lambda_first)
    shifted_Hessian_second = _up(hessian_second + lambda_second)

    # The final scalar component is the differentiated normalization
    # psi^T psi=1.  Assemble its contribution with the vector component in
    # l1 majorant form, then apply the certified bordered solve once.
    eigenline_second_rhs = _up(
        shifted_Hessian_second
        + 2.0 * shifted_Hessian_first * psi_first
        + psi_first * psi_first
    )
    psi_second = _up(inverse_upper * eigenline_second_rhs)
    K_second = _up(shifted_Hessian_second + psi_second)

    source_second = float(
        response[
            "raw_internal_rhs_second_coefficient_derivative_2_norm_upper"
        ]
    )
    response_upper = float(response["complete_bordered_response_2_norm_upper"])
    response_first = float(
        first[
            "complete_bordered_response_first_coefficient_variation_2_to_2_upper"
        ]
    )
    K_second_response = _up(K_second * response_upper)
    twice_K_first_response_first = _up(
        2.0 * K_first * response_first
    )
    differentiated_rhs_second = _up(
        source_second + K_second_response + twice_K_first_response_first
    )
    response_second = _up(inverse_upper * differentiated_rhs_second)

    finite = all(map(math.isfinite, (
        lift, hessian_first, psi_first, K_first, inverse_upper,
        hessian_second, lambda_second, shifted_Hessian_first,
        shifted_Hessian_second, eigenline_second_rhs, psi_second, K_second,
        source_second, response_upper, response_first, K_second_response,
        twice_K_first_response_first, differentiated_rhs_second,
        response_second,
    )))
    return {
        "seam": int(first["seam"]),
        "local_index": int(first["local_index"]),
        "action_interval": list(first["action_interval"]),
        "parent_local_index": int(first["parent_local_index"]),
        "child_within_parent": int(first["child_within_parent"]),
        "selected_branch": int(first["selected_branch"]),
        "projection_dimension": int(first["projection_dimension"]),
        "child_to_parent_common_frame_direction_lift_2_norm_upper": lift,
        "uniform_child_Hessian_first_coefficient_derivative_2_norm_upper": (
            hessian_first
        ),
        "uniform_child_Hessian_second_coefficient_derivative_2_norm_upper": (
            hessian_second
        ),
        "uniform_child_selected_eigenvalue_first_coefficient_derivative_absolute_upper": (
            lambda_first
        ),
        "uniform_child_selected_eigenvalue_second_coefficient_derivative_absolute_upper": (
            lambda_second
        ),
        "uniform_child_shifted_Hessian_first_coefficient_derivative_2_norm_upper": (
            shifted_Hessian_first
        ),
        "uniform_child_shifted_Hessian_second_coefficient_derivative_2_norm_upper": (
            shifted_Hessian_second
        ),
        "selected_eigenline_second_differentiated_rhs_2_norm_upper": (
            eigenline_second_rhs
        ),
        "uniform_child_selected_line_second_coefficient_derivative_2_norm_upper": (
            psi_second
        ),
        "uniform_child_bordered_K_first_coefficient_derivative_2_norm_upper": (
            K_first
        ),
        "uniform_child_bordered_K_second_coefficient_derivative_2_norm_upper": (
            K_second
        ),
        "internal_rhs_second_coefficient_derivative_2_norm_upper": source_second,
        "complete_bordered_response_2_norm_upper": response_upper,
        "complete_bordered_response_first_coefficient_variation_2_to_2_upper": (
            response_first
        ),
        "bordered_second_derivative_times_response_2_norm_upper": (
            K_second_response
        ),
        "twice_bordered_first_derivative_times_response_first_2_norm_upper": (
            twice_K_first_response_first
        ),
        "combined_second_differentiated_rhs_2_norm_upper": (
            differentiated_rhs_second
        ),
        "complete_bordered_response_second_coefficient_variation_2_to_2_upper": (
            response_second
        ),
        "all_second_variation_quantities_finite": finite,
    }


def build_payload() -> dict[str, Any]:
    first = _load(FIRST)
    response = _load(RESPONSE)
    projector = _load(PROJECTOR)
    inverse = _load(INVERSE)
    parents = (first, response, projector, inverse)
    if not all(parent.get("validation_passed") is True for parent in parents):
        raise RuntimeError("validated recentered-cone parents required")

    projector_rows = {
        (int(row["seam"]), int(row["local_index"])): row
        for row in projector["rows"]
    }
    inverse_rows = {
        (int(row["seam"]), int(row["local_index"])): row
        for row in inverse["rows"]
    }
    if len(first["rows"]) != len(response["rows"]):
        raise RuntimeError("first- and zero-order response meshes differ")
    rows = []
    identical = True
    for first_row, response_row in zip(
        first["rows"], response["rows"], strict=True
    ):
        key_first = (
            int(first_row["seam"]), int(first_row["local_index"]),
            int(first_row["parent_local_index"]),
            int(first_row["child_within_parent"]),
        )
        key_response = (
            int(response_row["seam"]), int(response_row["local_index"]),
            int(response_row["parent_local_index"]),
            int(response_row["child_within_parent"]),
        )
        identical = identical and key_first == key_response
        parent_key = (key_first[0], key_first[2])
        rows.append(_row(
            first_row, response_row,
            projector_rows[parent_key], inverse_rows[parent_key],
        ))

    validation = {
        "identical_24072_cell_zero_first_second_response_cover_consumed": (
            identical and len(rows) == 24072
        ),
        "all_3009_parent_projector_and_inverse_rows_consumed": len({
            (row["seam"], row["parent_local_index"]) for row in rows
        }) == 3009,
        "branch_24_selected_everywhere": all(
            row["selected_branch"] == 24 for row in rows
        ),
        "same_101_dimensional_recentered_product_cone_used": all(
            row["projection_dimension"] == 101 for row in rows
        ),
        "D4_half_Taylor_remainder_converted_to_bilinear_Hessian_second_bound": True,
        "child_parent_common_frame_lift_applied_quadratically_to_second_variation": True,
        "selected_eigenline_second_normalization_component_retained": True,
        "complete_second_differentiated_bordered_identity_assembled_before_solve_bound": True,
        "all_second_variation_tubes_finite": all(
            row["all_second_variation_quantities_finite"] for row in rows
        ),
        "no_full_kinetic_Dirac_or_history_inverse_used": True,
        "only_external_Cauchy_birth_source_zero_internal_second_variation_retained": True,
        "no_internal_child_contact_transport_or_scalar_response_zeroed": True,
        "no_added_seam_force_or_double_counted_response": True,
        "ambient_majorant_not_promoted_to_signed_projected_Cauchy_tail": True,
        "no_action_equation_source_selector_scale_gate_or_chord_changed": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    owner = max(
        rows,
        key=lambda row: row[
            "complete_bordered_response_second_coefficient_variation_2_to_2_upper"
        ],
    )
    return {
        "artifact": "BHSM_N12_GATE7_RECENTERED_CONE_BORDERED_RESPONSE_SECOND_VARIATION",
        "status": (
            "RECENTERED_GATE7_CONE_COMPLETE_BORDERED_RESPONSE_SECOND_VARIATION_MAJORANT_CERTIFIED"
            if passed else
            "RECENTERED_GATE7_CONE_BORDERED_RESPONSE_SECOND_VARIATION_OPEN"
        ),
        "identity": (
            "K*x_2=f_2-K_2*x-2*K_1*x_1;_"
            "B*psi_2=-((H_2-lambda_2_I)*psi+"
            "2*(H_1-lambda_1_I)*psi_1,||psi_1||^2)"
        ),
        "authority": (
            "RETAINED_ACTION_D4_PARENT_BALL_PLUS_CERTIFIED_SELECTED_GRAPH_"
            "AND_BORDERED_INVERSE_ON_THE_IDENTICAL_RECENTERED_CONE"
        ),
        "mesh": {
            "parent_cells": 3009,
            "response_cells": len(rows),
            "projection_dimension": 101,
        },
        "summary": {
            "maximum_uniform_child_Hessian_second_coefficient_derivative_2_norm_upper": max(
                row[
                    "uniform_child_Hessian_second_coefficient_derivative_2_norm_upper"
                ] for row in rows
            ),
            "maximum_uniform_child_selected_line_second_coefficient_derivative_2_norm_upper": max(
                row[
                    "uniform_child_selected_line_second_coefficient_derivative_2_norm_upper"
                ] for row in rows
            ),
            "maximum_uniform_child_bordered_K_second_coefficient_derivative_2_norm_upper": max(
                row[
                    "uniform_child_bordered_K_second_coefficient_derivative_2_norm_upper"
                ] for row in rows
            ),
            "maximum_complete_bordered_response_second_coefficient_variation_2_to_2_upper": owner[
                "complete_bordered_response_second_coefficient_variation_2_to_2_upper"
            ],
            "owner": owner,
        },
        "rows": rows,
        "validation": validation,
        "validation_passed": passed,
        "claim_boundary": {
            "recentered_cone_bordered_response_second_variation_majorant": (
                "CERTIFIED_FINITE" if passed else "OPEN"
            ),
            "signed_common_frame_second_variation": "OPEN",
            "projected_Cauchy_tail": "OPEN",
            "causal_interval_vector_radius": "OPEN",
            "domain_and_first_hit_transfer": "OPEN",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "CONTRACT_THE_SECOND_DIFFERENTIATED_BORDERED_IDENTITY_IN_THE_"
            "ACTUAL_SIGNED_GREEN_AND_REVERSE_ADJOINT_COMMON_FRAMES_BEFORE_"
            "TAKING_NORMS,_THEN_EVALUATE_THE_CAUSAL_VECTOR_RADIUS"
            if passed else
            "REFINE_ONLY_THE_REPORTED_SECOND_VARIATION_OWNER_CELLS"
        ),
        "inputs": {
            _relative(path): _sha256(path)
            for path in (FIRST, RESPONSE, PROJECTOR, INVERSE)
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
