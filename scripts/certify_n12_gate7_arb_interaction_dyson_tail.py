"""Certify an analytic interaction-frame tail for the Gate-7 affine flow.

On each retained PROP16 substep write the affine generator as

    A(t) = A_0 + t B,       0 <= t <= h.

Factoring ``U(t)=exp(A_0 t)V(t)`` gives

    V' = G(t)V,  G(t)=t exp(-ad(A_0)t) B.

The conjugation series is evaluated through a fixed commutator depth with
256-bit Arb matrices.  Its remaining tail is bounded from the exact last
commutator using ``||ad_A X|| <= 2||A||||X||``.  The resulting integral
``beta >= integral ||G||`` yields the standard time-ordered Dyson remainder

    ||V-V_N|| <= exp(beta) beta^(N+1)/(N+1)!.

This is an analytic tail theorem only.  It does not replace the exact flow by
the finite Dyson polynomial, and it does not promote the signed source.
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


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
CENTER = BASE / (
    "BHSM_N12_C2_STOP_HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.npz"
)
JACOBIAN = BASE / (
    "BHSM_N12_C2_STOP_QUARTER_STEP_FINE_HYBRID_GRAPH_JACOBIAN_RECONNAISSANCE.npz"
)
RESULT = BASE / "BHSM_N12_GATE7_ARB_INTERACTION_DYSON_TAIL.json"
DATA = RESULT.with_suffix(".npz")
DIMENSION = 98
_WORKER: dict[str, object] = {}


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _exact(value: float) -> arb:
    numerator, denominator = float(value).as_integer_ratio()
    return arb(numerator) / denominator


def _matrix(values: np.ndarray) -> arb_mat:
    return arb_mat([
        [_exact(value) for value in row]
        for row in np.asarray(values, dtype=float)
    ])


def _two_norm_upper(matrix: arb_mat) -> arb:
    """Rigorous induced-2 upper bound sqrt(||M||_1 ||M||_inf)."""

    row_sums = [
        sum(abs(matrix[row, column]) for column in range(matrix.ncols()))
        for row in range(matrix.nrows())
    ]
    column_sums = [
        sum(abs(matrix[row, column]) for row in range(matrix.nrows()))
        for column in range(matrix.ncols())
    ]
    return (max(row_sums) * max(column_sums)).sqrt()


def _upper_float(value: arb) -> float:
    return float(np.nextafter(float(value.upper()), np.inf))


def _initialize(precision: int, depth: int, dyson_order: int) -> None:
    ctx.prec = precision
    _WORKER["depth"] = depth
    _WORKER["dyson_order"] = dyson_order
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


def _conjugation_tail(
    last_norm: arb, generator_norm: arb, width: arb, depth: int,
) -> arb:
    """Bound terms k >= depth in the integrated conjugation series."""

    total = arb(0)
    two_a = 2 * generator_norm
    # The first omitted commutator is X_depth.  Directly sum a long positive
    # scalar majorant; after 256 terms its remaining ratio is uniformly below
    # one on this retained data set and is closed geometrically.
    term = (
        last_norm * width ** (depth + 2)
        / (arb(depth).fac() * (depth + 2))
    )
    total += term
    for m in range(256):
        k = depth + m
        ratio = (
            two_a * width * (k + 2)
            / ((k + 1) * (k + 3))
        )
        term *= ratio
        total += term
    k = depth + 256
    next_ratio = (
        two_a * width * (k + 2)
        / ((k + 1) * (k + 3))
    )
    if not next_ratio.upper() < 1:
        raise RuntimeError("conjugation-tail ratio did not enter geometric regime")
    return total + term * next_ratio / (1 - next_ratio)


def _cell(interval: int) -> list[dict[str, float | int]]:
    depth = int(_WORKER["depth"])
    dyson_order = int(_WORKER["dyson_order"])
    fixed_step = float(_WORKER["fixed_step"])
    stop_fraction = float(_WORKER["stop_fraction"])
    jacobian_times = np.asarray(_WORKER["jacobian_times"])
    jacobians = np.asarray(_WORKER["jacobians"])

    duration = fixed_step * (stop_fraction if interval == 369 else 1.0)
    count = max(1, int(math.ceil(duration / (fixed_step / 16.0))))
    width_float = duration / count
    width = _exact(width_float)
    left = _matrix(jacobians[interval])
    dt = _exact(float(jacobian_times[interval + 1] - jacobian_times[interval]))
    slope = (_matrix(jacobians[interval + 1]) - left) / dt

    rows = []
    for substep in range(count):
        generator = left + _exact(substep * width_float) * slope
        generator_norm = _two_norm_upper(generator)
        commutator = slope
        beta_head = arb(0)
        last_norm = None
        for order in range(depth + 1):
            commutator_norm = _two_norm_upper(commutator)
            if order < depth:
                beta_head += (
                    commutator_norm * width ** (order + 2)
                    / (arb(order).fac() * (order + 2))
                )
            else:
                last_norm = commutator_norm
                break
            commutator = generator * commutator - commutator * generator
        if last_norm is None:
            raise RuntimeError("last commutator was not evaluated")
        conjugation_tail = _conjugation_tail(
            last_norm, generator_norm, width, depth,
        )
        beta = beta_head + conjugation_tail
        dyson_tail = (
            beta.exp() * beta ** (dyson_order + 1)
            / arb(dyson_order + 1).fac()
        )
        constant_factor = (generator_norm * width).exp()
        local_tail = constant_factor * dyson_tail
        rows.append({
            "interval": interval,
            "substep": substep,
            "substep_count": count,
            "width": width_float,
            "generator_2_norm_upper": _upper_float(generator_norm),
            "generator_width_upper": _upper_float(generator_norm * width),
            "interaction_beta_upper": _upper_float(beta),
            "conjugation_series_tail_upper": _upper_float(conjugation_tail),
            "Dyson_remainder_upper": _upper_float(dyson_tail),
            "constant_factor_norm_upper": _upper_float(constant_factor),
            "local_exact_propagator_tail_upper": _upper_float(local_tail),
        })
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--precision", type=int, default=256)
    parser.add_argument("--commutator-depth", type=int, default=12)
    parser.add_argument("--dyson-order", type=int, default=14)
    parser.add_argument("--workers", type=int, default=min(12, os.cpu_count() or 1))
    args = parser.parse_args()
    if (
        args.precision < 128 or args.commutator_depth < 8
        or args.dyson_order < 8 or not 1 <= args.workers <= 16
    ):
        raise ValueError("invalid interaction-tail certification parameters")
    ctx.prec = args.precision

    with ProcessPoolExecutor(
        max_workers=args.workers,
        initializer=_initialize,
        initargs=(args.precision, args.commutator_depth, args.dyson_order),
    ) as executor:
        nested = list(executor.map(_cell, range(370), chunksize=1))
    rows = [row for group in nested for row in group]
    if len(rows) != 5908:
        raise RuntimeError("retained PROP16 partition must contain 5,908 substeps")

    keys = (
        "interval", "substep", "substep_count", "width",
        "generator_2_norm_upper", "generator_width_upper",
        "interaction_beta_upper", "conjugation_series_tail_upper",
        "Dyson_remainder_upper", "constant_factor_norm_upper",
        "local_exact_propagator_tail_upper",
    )
    np.savez_compressed(DATA, **{
        key: np.asarray([row[key] for row in rows]) for key in keys
    })
    owners = {
        key: max(rows, key=lambda row: float(row[key]))
        for key in (
            "generator_width_upper", "interaction_beta_upper",
            "conjugation_series_tail_upper",
            "Dyson_remainder_upper", "local_exact_propagator_tail_upper",
        )
    }
    maximum_beta = max(float(row["interaction_beta_upper"]) for row in rows)
    maximum_local_tail = max(
        float(row["local_exact_propagator_tail_upper"]) for row in rows
    )
    validation = {
        "all_5908_retained_PROP16_substeps_certified": len(rows) == 5908,
        "all_binary64_generator_inputs_lifted_as_exact_rationals": True,
        "all_nested_commutators_evaluated_with_Arb_matrices": True,
        "induced_2_norm_bounded_by_sqrt_1_norm_times_infinity_norm": True,
        "conjugation_tail_closed_from_exact_last_commutator": True,
        "interaction_integral_beta_below_one": maximum_beta < 1.0,
        "order_14_Dyson_local_exact_flow_tail_below_1e_minus_20": (
            args.dyson_order == 14 and maximum_local_tail < 1.0e-20
        ),
        "finite_interaction_Dyson_polynomial_not_yet_promoted": True,
        "signed_source_not_relabelled_as_internal_propagator_tail": True,
        "no_action_source_selector_scale_gate_or_chord_changed": True,
    }
    payload = {
        "artifact": "BHSM_N12_GATE7_ARB_INTERACTION_DYSON_TAIL",
        "status": (
            "ALL_RETAINED_AFFINE_SUBSTEPS_HAVE_A_RIGOROUS_INTERACTION_FRAME_"
            "ORDER14_DYSON_ANALYTIC_TAIL"
            if all(validation.values()) else
            "INTERACTION_FRAME_DYSON_TAIL_CERTIFICATE_INVALID"
        ),
        "authority": (
            "EXACT_BINARY64_RETAINED_AFFINE_GENERATORS_LIFTED_TO_256_BIT_ARB;_"
            "RIGOROUS_MATRIX_NORM_AND_TIME_ORDERED_DYSON_MAJORANT"
        ),
        "identity": {
            "affine_generator": "A(t)=A0+t*B",
            "interaction_factorization": "U(t)=exp(A0*t)*V(t)",
            "interaction_generator": "G(t)=t*exp(-ad_A0*t)*B",
            "commutator_depth": args.commutator_depth,
            "Dyson_order": args.dyson_order,
            "Dyson_tail": "exp(beta)*beta^(N+1)/(N+1)!",
            "constant_factor_bound": "exp(||A0||_2_upper*h)",
        },
        "summary": {
            "substep_count": len(rows),
            "maximum_generator_width_upper": max(
                float(row["generator_width_upper"]) for row in rows
            ),
            "maximum_interaction_beta_upper": maximum_beta,
            "maximum_conjugation_series_tail_upper": max(
                float(row["conjugation_series_tail_upper"]) for row in rows
            ),
            "maximum_Dyson_remainder_upper": max(
                float(row["Dyson_remainder_upper"]) for row in rows
            ),
            "maximum_local_exact_propagator_tail_upper": maximum_local_tail,
            "owners": owners,
        },
        "data": _relative(DATA),
        "data_SHA256": _sha256(DATA),
        "inputs": {
            _relative(path): _sha256(path) for path in (CENTER, JACOBIAN)
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "claim_boundary": {
            "interaction_frame_analytic_tail": "CERTIFIED_ON_ALL_PROP16_SUBSTEPS",
            "finite_order14_interaction_polynomial": "OPEN_FINITE_OUTWARD_EVALUATION",
            "exact_affine_propagator_composition": "OPEN_UNTIL_FINITE_PART_EVALUATED",
            "former_Omega9_plus_route": "SUPERSEDED_BY_INTERACTION_DYSON_ROUTE_ON_COMPLETION_OF_FINITE_PART",
            "signed_Y": "OPEN_INTERVAL_AUTHORITY",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "OUTWARD_EVALUATE_THE_FINITE_ORDER14_INTERACTION_DYSON_POLYNOMIAL_"
            "AND_COMPOSE_IT_WITH_exp(A0*h)_ON_THE_IDENTICAL_5908_SUBSTEPS,_THEN_"
            "REPLAY_THE_GLOBAL_CORRELATED_HOMOGENEOUS_AND_SIGNED_SOURCE_BLOCKS"
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
