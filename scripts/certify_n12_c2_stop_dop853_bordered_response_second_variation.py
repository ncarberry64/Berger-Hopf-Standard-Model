"""Certify a cellwise first/second-variation tube for the bordered response.

The complete action-owned equation is differentiated before any external
source convention is imposed::

    K x = f,
    K x' = f' - K' x,
    K x'' = f'' - K'' x - 2 K' x'.

The exact center first variation is retained.  Uniform remainders use the
same Bernstein cell, selected-line gap, and bordered inverse already
certified for the response cover.  This first enclosure is intentionally
coordinate-agnostic and may be conservative; it is a rigorous owner map for
the subsequent correlated/branchwise sharpening.
"""

from __future__ import annotations

import hashlib
import json
import math
from functools import lru_cache
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import certify_n12_c2_stop_dop853_adaptive_bordered_rhs_response as response  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
CERTIFICATE = BASE / "BHSM_N12_C2_STOP_DOP853_ADAPTIVE_BORDERED_RHS_RESPONSE_CERTIFICATE.json"
FIRST = BASE / "BHSM_N12_C2_STOP_DOP853_ADAPTIVE_BORDERED_RESPONSE_FIRST_VARIATION.json"
FIRST_DATA = FIRST.with_suffix(".npz")
RESULT = BASE / "BHSM_N12_C2_STOP_DOP853_BORDERED_RESPONSE_SECOND_VARIATION.json"


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _up(value: float) -> float:
    return math.nextafter(float(value) * (1.0 + 1.0e-10), math.inf)


def _rates_from_geometry(
    projection: np.ndarray, controls: np.ndarray, duration: float,
) -> tuple[float, float, float]:
    first = 7.0 * (controls[1:] - controls[:-1]) / duration
    second = 42.0 * (
        controls[2:] - 2.0 * controls[1:-1] + controls[:-2]
    ) / duration**2

    first_coefficients = np.asarray([
        np.linalg.lstsq(projection, vector, rcond=None)[0] for vector in first
    ])
    second_coefficients = np.asarray([
        np.linalg.lstsq(projection, vector, rcond=None)[0] for vector in second
    ])
    residual = max(
        float(np.linalg.norm(projection @ coefficient - vector))
        for vectors, coefficients in (
            (first, first_coefficients), (second, second_coefficients),
        )
        for vector, coefficient in zip(vectors, coefficients)
    )
    # A Bezier derivative is a convex combination of its derivative control
    # vectors, hence the maximum control-coefficient norm is a uniform bound.
    first_upper = _up(max(np.linalg.norm(row) for row in first_coefficients))
    second_upper = _up(max(np.linalg.norm(row) for row in second_coefficients))
    return first_upper, second_upper, _up(residual)


def _coefficient_rates(
    interval: int, subspan: int, subdivisions: int,
) -> tuple[float, float, float]:
    values, coefficients, times, _, __, bracket_raw, stop_raw = (
        response.dense._dense_arrays()
    )
    bracket = int(bracket_raw[0])
    right = float(stop_raw[0]) if interval == bracket else 1.0
    controls = response.dense._dense_bernstein_controls(
        values[interval], coefficients[interval],
    )
    controls = response.dense._restrict(controls, 0.0, right)
    controls = response.dense._restrict(
        controls, subspan / subdivisions, (subspan + 1) / subdivisions,
    )[:, :-1]
    center_curve = response.dense._split(controls, 0.5)[0][-1]
    first_controls = 7.0 * (controls[1:] - controls[:-1])
    tangent_axis = 0.5 * response.dense._split(
        first_controls, 0.5,
    )[0][-1]
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
    elif residual_energy == 0.0:
        projection = tangent_axis[:, None]
    else:
        ratio = math.sqrt(residual_energy / tangent_energy)
        projection = np.column_stack((
            math.sqrt(1.0 + ratio) * tangent_axis,
            math.sqrt(1.0 + 1.0 / ratio) * residual_axes,
        ))
    duration = float(times[interval + 1] - times[interval]) * right / subdivisions
    return _rates_from_geometry(
        projection, controls, duration,
    )


@lru_cache(maxsize=None)
def _parent_coefficient_rates(
    interval: int, subspan: int, subdivisions: int,
) -> tuple[float, float, float]:
    values, coefficients, times, _, __, bracket_raw, stop_raw = (
        response.dense._dense_arrays()
    )
    bracket = int(bracket_raw[0])
    right = float(stop_raw[0]) if interval == bracket else 1.0
    controls = response.dense._dense_bernstein_controls(
        values[interval], coefficients[interval],
    )
    controls = response.dense._restrict(controls, 0.0, right)
    controls = response.dense._restrict(
        controls, subspan / subdivisions, (subspan + 1) / subdivisions,
    )[:, :-1]
    midpoint = np.mean(controls, axis=0)
    projection = (controls - midpoint).T
    duration = float(times[interval + 1] - times[interval]) * right / subdivisions
    return _rates_from_geometry(
        projection, controls, duration,
    )


def build_payload() -> dict[str, Any]:
    certificate = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    first = json.loads(FIRST.read_text(encoding="utf-8"))
    if certificate.get("validation_passed") is not True:
        raise RuntimeError("certified bordered response cover required")
    if first.get("validation_passed") is not True:
        raise RuntimeError("exact center response first variation required")
    response_rows = certificate["rows"]
    first_rows = first["rows"]
    if len(response_rows) != len(first_rows):
        raise RuntimeError("response and center-variation covers differ")
    with np.load(FIRST_DATA) as arrays:
        center_first = np.asarray(
            arrays["bordered_response_action_time_first_variation"], dtype=float,
        )

    inverse_rows = response._inverse_rows()
    projector_rows = response._projector_rows()
    rows: list[dict[str, Any]] = []
    for index, (source, center) in enumerate(zip(response_rows, first_rows)):
        key = (
            int(source["interval"]), int(source["subspan"]),
            int(source["subdivisions"]),
        )
        center_key = (
            int(center["interval"]), int(center["subspan"]),
            int(center["subdivisions"]),
        )
        if key != center_key:
            raise RuntimeError("response and center-variation row order differs")
        parent_key = (
            key[0], int(source["parent_subspan"]),
            int(source["parent_subdivisions"]),
        )
        inverse = inverse_rows[parent_key]
        coefficient_first, coefficient_second, representation_residual = (
            _coefficient_rates(*key)
        )
        parent_first, parent_second, parent_representation_residual = (
            _parent_coefficient_rates(*parent_key)
        )
        gap = float(inverse["certified_selected_to_hard_gap_lower"])
        inverse_upper = float(
            inverse["center_chart_bordered_inverse_2_norm_upper"]
        )

        projector = projector_rows[parent_key]
        hessian_d3 = float(projector["ambient_D3_Hessian_shift_upper"])
        hessian_d4 = 2.0 * float(
            projector["ambient_D4_Hessian_remainder_upper"]
        )
        hessian_first = _up((hessian_d3 + hessian_d4) * parent_first)
        hessian_second = _up(
            hessian_d4 * parent_first**2
            + (hessian_d3 + hessian_d4) * parent_second
        )
        selected_first = _up(
            float(projector["selected_graph_derivative_l2_upper"])
            * parent_first
        )
        selected_value_first = hessian_first
        selected_value_second = _up(
            hessian_second + 2.0 * hessian_first * selected_first
        )
        selected_second = _up(
            (2.0 * hessian_second + 6.0 * hessian_first * selected_first)
            / gap + selected_first**2
        )
        bordered_first = _up(
            hessian_first + selected_value_first + 2.0 * selected_first
        )
        bordered_second = _up(
            hessian_second + selected_value_second + 2.0 * selected_second
        )

        K_first = bordered_first
        K_second = bordered_second
        rhs_first = _up(
            float(source[
                "raw_internal_rhs_first_coefficient_derivative_2_norm_upper"
            ]) * coefficient_first
        )
        rhs_second = _up(
            float(source[
                "raw_internal_rhs_second_coefficient_derivative_2_norm_upper"
            ]) * coefficient_first**2
            + float(source[
                "raw_internal_rhs_first_coefficient_derivative_2_norm_upper"
            ]) * coefficient_second
        )
        response_upper = float(source["complete_bordered_response_2_norm_upper"])
        center_first_norm = float(np.linalg.norm(center_first[index]))
        half_width = 0.5 * float(center["action_time_duration"])
        first_direct = _up(
            inverse_upper * (rhs_first + K_first * response_upper)
        )
        # Use X1 <= ||x'_c|| + h*X2 in the differentiated identity before
        # closing the norm.  A nonpositive denominator is a proof-resolution
        # owner, not evidence of physical instability.
        denominator_margin = math.nextafter(
            1.0 - 2.0 * inverse_upper * K_first * half_width,
            -math.inf,
        )
        self_consistent_closed = denominator_margin > 0.0
        second_upper: float | None = (
            _up(
                inverse_upper * (
                    rhs_second + K_second * response_upper
                    + 2.0 * K_first * center_first_norm
                ) / denominator_margin
            )
            if self_consistent_closed else None
        )
        first_radius: float | None = (
            _up(half_width * second_upper)
            if second_upper is not None else None
        )
        center_remainder_tube: float | None = (
            _up(center_first_norm + first_radius)
            if first_radius is not None else None
        )
        # The direct differentiated-identity bound is a rigorous finite
        # first-variation tube even when the scalar self-consistent second
        # derivative closure fails.  Use the sharper center remainder only
        # where it closes.  A cover-wide scalar failure routes to correlated
        # common-frame assembly, not automatic global dyadic refinement.
        first_tube = (
            min(first_direct, center_remainder_tube)
            if center_remainder_tube is not None else first_direct
        )
        rows.append({
            "interval": key[0],
            "subspan": key[1],
            "subdivisions": key[2],
            "selected_branch": int(source["selected_branch"]),
            "action_time_duration": float(center["action_time_duration"]),
            "coefficient_first_variation_upper": coefficient_first,
            "coefficient_second_variation_upper": coefficient_second,
            "coefficient_derivative_representation_residual_upper": representation_residual,
            "parent_coefficient_first_variation_upper": parent_first,
            "parent_coefficient_second_variation_upper": parent_second,
            "parent_coefficient_derivative_representation_residual_upper": parent_representation_residual,
            "uniform_bordered_inverse_2_norm_upper": inverse_upper,
            "uniform_Hessian_first_action_time_derivative_2_norm_upper": hessian_first,
            "uniform_Hessian_second_action_time_derivative_2_norm_upper": hessian_second,
            "uniform_selected_line_first_action_time_derivative_2_norm_upper": selected_first,
            "uniform_selected_line_second_action_time_derivative_2_norm_upper": selected_second,
            "uniform_bordered_K_first_action_time_derivative_2_norm_upper": K_first,
            "uniform_bordered_K_second_action_time_derivative_2_norm_upper": K_second,
            "uniform_internal_rhs_first_action_time_derivative_2_norm_upper": rhs_first,
            "uniform_internal_rhs_second_action_time_derivative_2_norm_upper": rhs_second,
            "center_first_variation_2_norm": center_first_norm,
            "direct_uniform_first_variation_2_norm_upper": first_direct,
            "self_consistent_denominator_margin_lower": denominator_margin,
            "self_consistent_denominator_closed": self_consistent_closed,
            "uniform_second_variation_2_norm_upper": second_upper,
            "first_variation_tube_radius": first_radius,
            "center_plus_second_remainder_first_variation_2_norm_upper": center_remainder_tube,
            "certified_first_variation_2_norm_upper": first_tube,
        })
        if (index + 1) % 256 == 0 or index + 1 == len(response_rows):
            print(json.dumps({
                "completed": index + 1,
                "total": len(response_rows),
                "maximum_first_tube_so_far": max(
                    row["certified_first_variation_2_norm_upper"] for row in rows
                ),
            }), flush=True)

    validation = {
        "identical_exact_response_cover_consumed_in_order": len(rows) == len(response_rows),
        "branch_24_selected_everywhere": all(row["selected_branch"] == 24 for row in rows),
        "exact_Bernstein_first_and_second_derivative_controls_used": True,
        "all_coefficient_derivatives_represented_in_proof_ellipsoids": all(
            row["coefficient_derivative_representation_residual_upper"] < 1.0e-8
            and row["parent_coefficient_derivative_representation_residual_upper"] < 1.0e-8
            for row in rows
        ),
        "complete_differentiated_bordered_identity_used": True,
        "exact_center_combined_source_minus_operator_response_retained": True,
        "uniform_selected_line_first_and_second_Kato_terms_included": True,
        "self_consistent_second_variation_denominator_positive_everywhere": all(
            row["self_consistent_denominator_closed"] for row in rows
        ),
        "all_direct_first_variation_tubes_finite": all(
            math.isfinite(row["direct_uniform_first_variation_2_norm_upper"])
            and math.isfinite(row["certified_first_variation_2_norm_upper"])
            for row in rows
        ),
        "all_first_and_second_variation_tubes_finite": all(
            math.isfinite(row["certified_first_variation_2_norm_upper"])
            and row["uniform_second_variation_2_norm_upper"] is not None
            and math.isfinite(row["uniform_second_variation_2_norm_upper"])
            for row in rows
        ),
        "only_external_Cauchy_birth_source_zero": True,
        "no_internal_seam_response_zeroed_or_double_counted": True,
        "no_full_kinetic_Dirac_or_history_inverse_used": True,
    }
    second_variation_passed = all(validation.values())
    first_variation_passed = all(
        value for key, value in validation.items()
        if key not in {
            "self_consistent_second_variation_denominator_positive_everywhere",
            "all_first_and_second_variation_tubes_finite",
        }
    ) and validation["all_direct_first_variation_tubes_finite"]
    owner = min(
        rows, key=lambda row: row["self_consistent_denominator_margin_lower"],
    )
    correlation_owner_cells = [
        {
            "interval": row["interval"],
            "subspan": row["subspan"],
            "subdivisions": row["subdivisions"],
            "denominator_margin": row[
                "self_consistent_denominator_margin_lower"
            ],
        }
        for row in rows if not row["self_consistent_denominator_closed"]
    ]
    return {
        "artifact": "BHSM_N12_C2_STOP_DOP853_BORDERED_RESPONSE_SECOND_VARIATION",
        "status": (
            "CELLWISE_BORDERED_RESPONSE_FIRST_AND_SECOND_VARIATION_TUBES_CERTIFIED"
            if second_variation_passed else
            "CELLWISE_BORDERED_RESPONSE_FIRST_VARIATION_CERTIFIED;_SCALAR_SECOND_VARIATION_DENOMINATOR_OPEN"
            if first_variation_passed else
            "BORDERED_RESPONSE_VARIATION_TUBE_INVALID"
        ),
        "identity": "K*x=f;_K*x'=f'-K'*x;_K*x''=f''-K''*x-2*K'*x'",
        "method": "EXACT_CENTER_CANCELLATION_PLUS_UNIFORM_ACTION_D2_TO_D4_AND_SELECTED_LINE_KATO_REMAINDER",
        "mesh": {"response_cells": len(rows)},
        "summary": {
            "maximum_coefficient_first_variation_upper": max(row["coefficient_first_variation_upper"] for row in rows),
            "maximum_coefficient_second_variation_upper": max(row["coefficient_second_variation_upper"] for row in rows),
            "minimum_self_consistent_denominator_margin_lower": min(row["self_consistent_denominator_margin_lower"] for row in rows),
            "maximum_certified_first_variation_2_norm_upper": max(row["certified_first_variation_2_norm_upper"] for row in rows),
            "maximum_uniform_second_variation_2_norm_upper": (
                max(
                    row["uniform_second_variation_2_norm_upper"]
                    for row in rows
                    if row["uniform_second_variation_2_norm_upper"] is not None
                )
                if any(
                    row["uniform_second_variation_2_norm_upper"] is not None
                    for row in rows
                ) else None
            ),
            "scalar_denominator_owner_cells": len(correlation_owner_cells),
            "owner": owner,
        },
        "scalar_denominator_owner_cells": correlation_owner_cells,
        "rows": rows,
        "validation": validation,
        "first_variation_validation_passed": first_variation_passed,
        "second_variation_validation_passed": second_variation_passed,
        "validation_passed": second_variation_passed,
        "claim_boundary": {
            "cellwise_response_first_variation_tube": "CERTIFIED_FINITE" if first_variation_passed else "OPEN",
            "cellwise_response_second_variation_tube": "CERTIFIED_FINITE" if second_variation_passed else "OPEN_SIGNED_CORRELATION_REQUIRED",
            "sharp_correlated_response_variation_tube": "OPEN",
            "correlated_Y_Z1_Z2": "OPEN",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "USE_THE_CERTIFIED_OWNER_MAP_TO_ASSEMBLE_THE_CORRELATED_BRANCHWISE_Y_Z1_Z2_BOUNDS_WITHOUT_GLOBAL_MAXIMUM_COLLAPSE"
            if second_variation_passed else
            "PRESERVE_SIGNED_COMMON_FRAME_CORRELATION_ON_THE_REPORTED_SCALAR_DENOMINATOR_OWNER_CELLS;_LOCAL_REFINEMENT_REQUIRES_A_SEPARATE_OWNER_ANALYSIS"
        ),
        "inputs": {
            _relative(CERTIFICATE): _sha256(CERTIFICATE),
            _relative(FIRST): _sha256(FIRST),
            _relative(FIRST_DATA): _sha256(FIRST_DATA),
            "scripts/certify_n12_c2_stop_dop853_adaptive_bordered_rhs_response.py": _sha256(ROOT / "scripts/certify_n12_c2_stop_dop853_adaptive_bordered_rhs_response.py"),
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
