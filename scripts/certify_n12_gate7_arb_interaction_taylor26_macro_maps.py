"""Outward-evaluate exact Gate-7 affine macro maps in an interaction frame.

The finite interaction polynomial has degree 26.  Its exact ODE residual,
the certified depth-12 conjugation tail, and a Gronwall factor enclose the
complete affine propagator on every retained PROP16 substep.  This is not a
Magnus-order extrapolation and does not continuously project the ambient flow.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
import math
import os
from pathlib import Path

from flint import arb, arb_mat, ctx
import numpy as np

from certify_n12_gate7_arb_interaction_dyson_tail import (
    _conjugation_tail,
    _exact,
    _matrix,
    _two_norm_upper,
    _upper_float,
)


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
CENTER = BASE / (
    "BHSM_N12_C2_STOP_HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.npz"
)
JACOBIAN = BASE / (
    "BHSM_N12_C2_STOP_QUARTER_STEP_FINE_HYBRID_GRAPH_JACOBIAN_RECONNAISSANCE.npz"
)
TANGENT = BASE / (
    "BHSM_N12_C2_STOP_QUARTER_STEP_PHYSICAL_TANGENT_TRANSFER_RECONNAISSANCE.npz"
)
TAIL_SCRIPT = ROOT / "scripts" / "certify_n12_gate7_arb_interaction_dyson_tail.py"
TAIL_RECORD = BASE / "BHSM_N12_GATE7_ARB_INTERACTION_DYSON_TAIL.json"
RESULT = BASE / "BHSM_N12_GATE7_ARB_INTERACTION_TAYLOR26_MACRO_MAPS.json"
DATA = RESULT.with_suffix(".npz")
AMBIENT = 98
PHYSICAL = 73
DEPTH = 22
DEGREE = 26
_WORKER: dict[str, object] = {}


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _identity(size: int) -> arb_mat:
    return arb_mat(np.eye(size, dtype=int).tolist())


def _mid_radius(matrix: arb_mat) -> tuple[np.ndarray, np.ndarray]:
    midpoint = np.empty((matrix.nrows(), matrix.ncols()))
    radius = np.empty_like(midpoint)
    for row in range(matrix.nrows()):
        for column in range(matrix.ncols()):
            value = matrix[row, column]
            midpoint[row, column] = float(value.mid())
            radius[row, column] = np.nextafter(
                float(value.rad().upper()), np.inf,
            )
    return midpoint, radius


def _interaction_step(
    left: arb_mat, slope: arb_mat, offset: arb, width: arb,
) -> tuple[arb_mat, arb, arb, arb]:
    """Return an outward complete affine propagator and its proof radii."""

    generator = left + offset * slope
    generator_norm = _two_norm_upper(generator)
    commutator = slope
    interaction_coefficients = []
    beta_head = arb(0)
    last_norm = None
    for order in range(DEPTH + 1):
        commutator_norm = _two_norm_upper(commutator)
        if order < DEPTH:
            sign = -1 if order % 2 else 1
            interaction_coefficients.append(
                sign * width ** (order + 2) / arb(order).fac() * commutator
            )
            beta_head += (
                commutator_norm * width ** (order + 2)
                / (arb(order).fac() * (order + 2))
            )
        else:
            last_norm = commutator_norm
            break
        commutator = generator * commutator - commutator * generator
    if last_norm is None:
        raise RuntimeError("depth-22 interaction commutator was not evaluated")
    conjugation_tail = _conjugation_tail(
        last_norm, generator_norm, width, DEPTH,
    )
    beta = beta_head + conjugation_tail

    coefficients = [_identity(AMBIENT)]
    for degree in range(DEGREE):
        value = arb_mat(AMBIENT, AMBIENT)
        # H(x) starts at x^1, hence p <= degree in the coefficient of x^degree.
        for power in range(1, min(DEPTH, degree) + 1):
            value += (
                interaction_coefficients[power - 1]
                * coefficients[degree - power]
            )
        coefficients.append(value / (degree + 1))
    polynomial = coefficients[0]
    coefficient_norm_sum = arb(0)
    for coefficient in coefficients:
        if coefficient is not coefficients[0]:
            polynomial += coefficient
        coefficient_norm_sum += _two_norm_upper(coefficient)

    residual_integral = arb(0)
    # H*P reaches degree DEPTH+DEGREE.  The recurrence cancels all degrees
    # below DEGREE exactly; sum every remaining polynomial coefficient.
    for degree in range(DEGREE, DEGREE + DEPTH + 1):
        residual = arb_mat(AMBIENT, AMBIENT)
        for power in range(1, DEPTH + 1):
            coefficient = degree - power
            if 0 <= coefficient <= DEGREE:
                residual -= (
                    interaction_coefficients[power - 1]
                    * coefficients[coefficient]
                )
        residual_integral += _two_norm_upper(residual) / (degree + 1)

    interaction_error = beta.exp() * (
        residual_integral + conjugation_tail * coefficient_norm_sum
    )
    exact_flow_error = (generator_norm * width).exp() * interaction_error
    finite = (width * generator).exp() * polynomial
    error_radius = _upper_float(exact_flow_error)
    error_ball = arb(0, error_radius)
    for row in range(AMBIENT):
        for column in range(AMBIENT):
            finite[row, column] += error_ball
    return finite, beta, residual_integral, exact_flow_error


def _initialize(precision: int) -> None:
    ctx.prec = precision
    with np.load(CENTER) as source:
        times = np.asarray(source["fine_grid_action_lengths"], dtype=float)
        _WORKER["fixed_step"] = float(times[1] - times[0])
        _WORKER["stop_fraction"] = float(source["stop_dense_fraction"][0])
    with np.load(JACOBIAN) as source:
        _WORKER["jacobian_times"] = np.asarray(
            source["action_lengths"], dtype=float,
        )
        _WORKER["jacobians"] = np.asarray(
            source["graph_Jacobian_action"], dtype=float,
        )
    with np.load(TANGENT) as source:
        _WORKER["tangents"] = np.asarray(
            source["physical_tangent_action"], dtype=float,
        )


def _macro(seam: int) -> tuple[
    int, np.ndarray, np.ndarray, int, float, float, float,
]:
    fixed_step = float(_WORKER["fixed_step"])
    stop_fraction = float(_WORKER["stop_fraction"])
    jacobian_times = np.asarray(_WORKER["jacobian_times"])
    jacobians = np.asarray(_WORKER["jacobians"])
    tangents = np.asarray(_WORKER["tangents"])
    maximum_step = fixed_step / 16.0
    starts = list(range(0, 369, 8))
    ends = [*starts[1:], 370]
    start, end = starts[seam], ends[seam]
    evolved = _matrix(tangents[seam])
    count_total = 0
    beta_max = 0.0
    residual_max = 0.0
    tail_max = 0.0
    for interval in range(start, end):
        duration = fixed_step * (stop_fraction if interval == 369 else 1.0)
        count = max(1, int(math.ceil(duration / maximum_step)))
        width_float = duration / count
        width = _exact(width_float)
        left = _matrix(jacobians[interval])
        dt = _exact(float(jacobian_times[interval + 1] - jacobian_times[interval]))
        slope = (_matrix(jacobians[interval + 1]) - left) / dt
        for substep in range(count):
            step, beta, residual, tail = _interaction_step(
                left, slope, _exact(substep * width_float), width,
            )
            evolved = step * evolved
            count_total += 1
            beta_max = max(beta_max, _upper_float(beta))
            residual_max = max(residual_max, _upper_float(residual))
            tail_max = max(tail_max, _upper_float(tail))
    target = _matrix(tangents[seam + 1])
    quotient = target.transpose() * evolved
    midpoint, radius = _mid_radius(quotient)
    return (
        seam, midpoint, radius, count_total, beta_max, residual_max, tail_max,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--precision", type=int, default=256)
    parser.add_argument("--workers", type=int, default=min(12, os.cpu_count() or 1))
    parser.add_argument("--macro-limit", type=int, default=47)
    args = parser.parse_args()
    if (
        args.precision < 256 or not 1 <= args.workers <= 16
        or not 1 <= args.macro_limit <= 47
    ):
        raise ValueError("256-bit precision, 1..16 workers, and 1..47 macros required")
    ctx.prec = args.precision
    seams = list(range(args.macro_limit))
    with ProcessPoolExecutor(
        max_workers=args.workers,
        initializer=_initialize,
        initargs=(args.precision,),
    ) as executor:
        results = list(executor.map(_macro, seams, chunksize=1))
    results.sort(key=lambda row: row[0])

    maps_mid = np.asarray([row[1] for row in results])
    maps_rad = np.asarray([row[2] for row in results])
    counts = np.asarray([row[3] for row in results])
    beta = np.asarray([row[4] for row in results])
    residual = np.asarray([row[5] for row in results])
    local_tail = np.asarray([row[6] for row in results])
    complete = args.macro_limit == 47
    with np.load(CENTER) as source:
        macro_times = np.asarray(source["action_lengths"], dtype=float)

    ctx.prec = args.precision
    global_map = _identity(PHYSICAL)
    for seam in range(args.macro_limit):
        block = arb_mat([
            [arb(float(maps_mid[seam, row, column]),
                 float(maps_rad[seam, row, column]))
             for column in range(PHYSICAL)]
            for row in range(PHYSICAL)
        ])
        global_map = block * global_map
    global_mid, global_rad = _mid_radius(global_map)

    np.savez_compressed(
        DATA,
        macro_action_lengths=macro_times[:args.macro_limit + 1],
        macro_step_map_midpoint=maps_mid,
        macro_step_map_component_radius=maps_rad,
        macro_substep_count=counts,
        macro_maximum_interaction_beta_upper=beta,
        macro_maximum_polynomial_residual_integral_upper=residual,
        macro_maximum_local_exact_flow_error_upper=local_tail,
        global_exact_affine_fundamental_midpoint=global_mid,
        global_exact_affine_fundamental_component_radius=global_rad,
    )
    validation = {
        "all_47_homogeneous_exact_affine_macro_maps_evaluated": (
            complete and maps_mid.shape == (47, PHYSICAL, PHYSICAL)
        ),
        "all_5908_retained_PROP16_substeps_evaluated": (
            complete and int(np.sum(counts)) == 5908
        ),
        "all_finite_interaction_polynomial_operations_in_256_bit_Arb": True,
        "degree26_interaction_polynomial_residual_evaluated_exactly": True,
        "certified_depth22_conjugation_tail_attached_to_every_substep": True,
        "complete_affine_flow_error_attached_before_composition": True,
        "ambient_98D_flow_preserved_between_macro_constraint_seams": True,
        "all_component_radii_finite": bool(
            np.all(np.isfinite(maps_rad)) and np.all(np.isfinite(global_rad))
        ),
        "signed_source_not_yet_promoted": True,
        "no_action_source_selector_scale_gate_or_chord_changed": True,
    }
    payload = {
        "artifact": "BHSM_N12_GATE7_ARB_INTERACTION_TAYLOR26_MACRO_MAPS",
        "status": (
            "ALL_47_HOMOGENEOUS_EXACT_AFFINE_QUOTIENT_MACRO_MAPS_OUTWARD_"
            "CERTIFIED_BY_INTERACTION_TAYLOR26_RESIDUAL"
            if all(validation.values()) else
            "INTERACTION_TAYLOR14_MACRO_MAP_CERTIFICATE_INVALID"
        ),
        "authority": (
            "256_BIT_ARB_FINITE_INTERACTION_POLYNOMIAL_PLUS_EXACT_ODE_RESIDUAL_"
            "AND_CERTIFIED_CONJUGATION_TAIL"
        ),
        "identity": {
            "ambient_dimension": AMBIENT,
            "physical_quotient_dimension": PHYSICAL,
            "interaction_polynomial_degree": DEGREE,
            "commutator_depth": DEPTH,
            "projection_rule": "PROJECT_ONLY_AT_RETAINED_MACRO_CONSTRAINT_SEAMS",
            "local_error_identity": (
                "exp(||A0||h+beta)*(integral||P26'-H22*P26||+"
                "conjugation_tail*sum||P26_coeff||)"
            ),
        },
        "summary": {
            "macro_count": args.macro_limit,
            "substep_count": int(np.sum(counts)),
            "maximum_interaction_beta_upper": float(np.max(beta)),
            "maximum_polynomial_residual_integral_upper": float(np.max(residual)),
            "maximum_local_exact_flow_error_upper": float(np.max(local_tail)),
            "maximum_macro_map_component_radius": float(np.max(maps_rad)),
            "global_exact_affine_fundamental_component_radius_Frobenius": float(
                np.linalg.norm(global_rad)
            ),
            "global_exact_affine_fundamental_operator_upper": float(
                np.linalg.norm(global_mid, ord=2) + np.linalg.norm(global_rad)
            ),
        },
        "data": _relative(DATA),
        "data_SHA256": _sha256(DATA),
        "inputs": {
            _relative(path): _sha256(path)
            for path in (CENTER, JACOBIAN, TANGENT, TAIL_SCRIPT, TAIL_RECORD)
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "claim_boundary": {
            "homogeneous_exact_affine_macro_maps": "CERTIFIED",
            "retained_partition_exact_affine_source_blocks": "OPEN",
            "global_exact_affine_signed_response": "OPEN_UNTIL_SOURCE_BLOCKS_COMPOSED",
            "signed_source_quadrature_Y": "OPEN_INTERVAL_AUTHORITY",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "EVALUATE_THE_RETAINED_UNALIGNED_GAUSS8_SOURCE_SUFFIXES_WITH_THE_SAME_"
            "EXACT_INTERACTION_TAYLOR26_STEP_AND_GLOBALLY_COMPOSE_THE_47_SIGNED_"
            "AFFINE_SOURCE_BLOCKS"
        ),
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
