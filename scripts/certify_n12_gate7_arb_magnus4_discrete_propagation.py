"""Outward-enclose the fixed discrete Magnus-4 Gate-7 source propagation.

Arb ball matrices evaluate every affine-generator commutator, matrix
exponential, product, source contraction, and macro quotient projection.  The
substeps are aligned within each fine cell so suffix products are shared by
all Gauss nodes.  This certifies evaluation of that finite discrete operator;
it does not bound the analytic Magnus truncation or signed-source quadrature.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from flint import arb, arb_mat, ctx
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
SOURCE = BASE / "BHSM_N12_GATE7_DECIMAL_SIGNED_SOURCE_QUADRATURE_AUDIT.npz"
CENTER = BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.npz"
JACOBIAN = BASE / "BHSM_N12_C2_STOP_QUARTER_STEP_FINE_HYBRID_GRAPH_JACOBIAN_RECONNAISSANCE.npz"
TANGENT = BASE / "BHSM_N12_C2_STOP_QUARTER_STEP_PHYSICAL_TANGENT_TRANSFER_RECONNAISSANCE.npz"
REFERENCE = BASE / "BHSM_N12_GATE7_DECIMAL_SIGNED_Y_GREEN_MAGNUS4_PROP16_AUDIT.npz"
RESULT = BASE / "BHSM_N12_GATE7_ARB_MAGNUS4_DISCRETE_PROPAGATION.json"
DATA = RESULT.with_suffix(".npz")
DIMENSION = 98


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _matrix(values: np.ndarray) -> arb_mat:
    # Materialize every stored binary64 number as its exact dyadic rational.
    array = np.asarray(values, dtype=float)
    return arb_mat([
        [_exact(value) for value in row]
        for row in array.reshape(array.shape[0], -1)
    ])


def _exact(value: float) -> arb:
    numerator, denominator = float(value).as_integer_ratio()
    return arb(numerator) / denominator


def _identity(size: int) -> arb_mat:
    return arb_mat(np.eye(size, dtype=int).tolist())


def _mid_radius(vector: arb_mat) -> tuple[np.ndarray, np.ndarray]:
    midpoint = np.empty(vector.nrows())
    radius = np.empty(vector.nrows())
    for index in range(vector.nrows()):
        value = vector[index, 0]
        midpoint[index] = float(value.mid())
        radius[index] = np.nextafter(float(value.rad().upper()), np.inf)
    return midpoint, radius


def _magnus_step(
    left_generator: arb_mat, slope: arb_mat, commutator: arb_mat,
    offset: arb, width: arb,
) -> arb_mat:
    midpoint_generator = left_generator + (offset + width / 2) * slope
    exponent = width * midpoint_generator - (width**3 / 12) * commutator
    return exponent.exp()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--precision", type=int, default=128)
    parser.add_argument("--interval-limit", type=int, default=370)
    parser.add_argument("--reset-at-macro", action="store_true")
    args = parser.parse_args()
    if args.precision < 80 or not 1 <= args.interval_limit <= 370:
        raise ValueError("precision >= 80 and 1..370 intervals required")
    ctx.prec = args.precision

    with np.load(SOURCE) as source:
        sample_intervals = np.asarray(source["sample_intervals"], dtype=int)
        sample_orders = np.asarray(source["sample_orders"], dtype=int)
        sample_indices = np.asarray(source["sample_indices"], dtype=int)
        residuals = np.asarray(source["state_rate_residuals"], dtype=float)
    with np.load(CENTER) as source:
        fine_times = np.asarray(source["fine_grid_action_lengths"], dtype=float)
        macro_times = np.asarray(source["action_lengths"], dtype=float)
        stop_fraction = float(source["stop_dense_fraction"][0])
    with np.load(JACOBIAN) as source:
        jacobian_times = np.asarray(source["action_lengths"], dtype=float)
        jacobians = np.asarray(source["graph_Jacobian_action"], dtype=float)
    with np.load(TANGENT) as source:
        tangents = np.asarray(source["physical_tangent_action"], dtype=float)
    with np.load(REFERENCE) as source:
        reference = np.asarray(source["Gauss8_correction_profile"], dtype=float)
    terminal_time = fine_times[369] + stop_fraction * (
        fine_times[370] - fine_times[369]
    )
    if (
        not np.array_equal(fine_times[:370], jacobian_times[:370])
        or abs(float(jacobian_times[-1]) - float(terminal_time)) > 1.0e-13
    ):
        raise RuntimeError("fine center and graph-Jacobian grids differ")

    nodes, weights = np.polynomial.legendre.leggauss(8)
    units = 0.5 * (nodes + 1.0)
    fixed_step = float(fine_times[1] - fine_times[0])
    maximum_step = fixed_step / 16.0
    correction = arb_mat(DIMENSION, 1)
    midpoints = [np.zeros(DIMENSION)]
    radii = [np.zeros(DIMENSION)]
    next_macro = 1
    exponential_count = 0

    for interval in range(args.interval_limit):
        if args.reset_at_macro and interval > 0 and interval % 8 == 0:
            correction = _matrix(reference[interval].reshape(DIMENSION, 1))
        duration_float = fixed_step * (
            stop_fraction if interval == 369 else 1.0
        )
        count = max(1, int(np.ceil(duration_float / maximum_step)))
        width_float = duration_float / count
        duration = _exact(duration_float)
        width = _exact(width_float)
        left_generator = _matrix(jacobians[interval])
        dt = _exact(float(jacobian_times[interval + 1] - jacobian_times[interval]))
        slope = (_matrix(jacobians[interval + 1]) - left_generator) / dt
        commutator = left_generator * slope - slope * left_generator

        fixed_maps = []
        for substep in range(count):
            fixed_maps.append(_magnus_step(
                left_generator, slope, commutator,
                _exact(substep * width_float), width,
            ))
        exponential_count += count
        suffix = [_identity(DIMENSION) for _ in range(count + 1)]
        for substep in range(count - 1, -1, -1):
            suffix[substep] = suffix[substep + 1] * fixed_maps[substep]

        mask = (sample_intervals == interval) & (sample_orders == 8)
        local_indices = sample_indices[mask]
        local_residuals = residuals[mask]
        permutation = np.argsort(local_indices)
        local_residuals = local_residuals[permutation]
        if local_residuals.shape != (8, DIMENSION):
            raise RuntimeError("complete ordered Gauss-8 source required")

        source_vector = arb_mat(DIMENSION, 1)
        for unit_float, weight_float, residual in zip(
            units, weights, local_residuals, strict=True,
        ):
            location_float = duration_float * float(unit_float)
            substep = min(int(location_float / width_float), count - 1)
            boundary_float = (substep + 1) * width_float
            partial_width_float = boundary_float - location_float
            partial = _magnus_step(
                left_generator, slope, commutator,
                _exact(location_float), _exact(partial_width_float),
            )
            exponential_count += 1
            propagated = suffix[substep + 1] * partial * _matrix(
                residual.reshape(DIMENSION, 1)
            )
            source_vector -= (
                duration * _exact(float(weight_float)) / 2
            ) * propagated

        correction = suffix[0] * correction + source_vector
        right_time = float(fine_times[interval] + duration_float)
        if (
            next_macro < macro_times.size
            and abs(right_time - float(macro_times[next_macro])) < 1.0e-9
        ):
            target = _matrix(tangents[next_macro])
            correction = target * (target.transpose() * correction)
            next_macro += 1
        midpoint, radius = _mid_radius(correction)
        midpoints.append(midpoint)
        radii.append(radius)
        if interval % 8 == 7 or interval + 1 == args.interval_limit:
            print(json.dumps({
                "completed_intervals": interval + 1,
                "exponentials": exponential_count,
                "maximum_component_radius": float(np.max(radius)),
            }), flush=True)

    midpoints = np.asarray(midpoints)
    radii = np.asarray(radii)
    reference_prefix = reference[:args.interval_limit + 1]
    midpoint_difference = np.linalg.norm(midpoints - reference_prefix, axis=1)
    Euclidean_radius = np.linalg.norm(radii, axis=1)
    outward_difference = midpoint_difference + Euclidean_radius
    np.savez_compressed(
        DATA,
        fine_action_lengths=np.concatenate((
            fine_times[:args.interval_limit],
            [fine_times[args.interval_limit - 1] + (
                fixed_step * stop_fraction if args.interval_limit == 370 else fixed_step
            )],
        )),
        Arb_midpoint_profile=midpoints,
        Arb_component_radius_profile=radii,
        Arb_Euclidean_radius_profile=Euclidean_radius,
        aligned_to_reference_midpoint_difference=midpoint_difference,
        aligned_to_reference_outward_difference=outward_difference,
    )
    complete = args.interval_limit == 370
    validation = {
        "Arb_precision_at_least_128_bits": args.precision >= 128,
        "every_stored_binary64_matrix_source_weight_and_time_input_exact_dyadic": True,
        "affine_commutators_matrix_exponentials_products_and_projections_in_Arb": True,
        "aligned_substep_suffix_products_shared_without_source_duplication": True,
        "complete_370_interval_history": complete,
        "every_eight_cell_quotient_block_recentered_to_stored_binary_center": (
            args.reset_at_macro
        ),
        "outward_ball_vanishes_at_reset": bool(Euclidean_radius[0] == 0.0),
        "finite_discrete_operator_only_not_analytic_Magnus_remainder": True,
        "signed_source_quadrature_error_remains_separate": True,
        "no_action_source_selector_scale_gate_or_chord_changed": True,
    }
    payload = {
        "artifact": "BHSM_N12_GATE7_ARB_MAGNUS4_DISCRETE_PROPAGATION",
        "status": (
            "ALL_RECENTERED_QUOTIENT_BLOCKS_OF_THE_FIXED_ALIGNED_MAGNUS4_"
            "DISCRETE_OPERATOR_OUTWARD_EVALUATED;_"
            "ANALYTIC_MAGNUS_AND_SIGNED_SOURCE_REMAINDERS_OPEN"
            if complete and args.reset_at_macro else
            "PARTIAL_OR_UNRECENTERED_ARB_MAGNUS4_BENCHMARK_ONLY"
        ),
        "authority": (
            "ARB_BALL_AUTHORITY_FOR_EACH_FINITE_RECENTERED_ALIGNED_MAGNUS4_"
            "QUOTIENT_BLOCK_ONLY"
        ),
        "identity": {
            "precision_bits": args.precision,
            "fine_intervals": args.interval_limit,
            "aligned_substeps_per_complete_cell": 16,
            "source_order": 8,
            "reset_to_stored_binary_center_at_each_macro": args.reset_at_macro,
            "Magnus_exponent": "h*A_mid-h^3*[A_left,A_prime]/12",
            "exponential_count": exponential_count,
        },
        "summary": {
            "maximum_Arb_Euclidean_radius": float(np.max(Euclidean_radius)),
            "maximum_aligned_to_reference_midpoint_difference": float(
                np.max(midpoint_difference)
            ),
            "maximum_aligned_to_reference_outward_difference": float(
                np.max(outward_difference)
            ),
            "terminal_Arb_Euclidean_radius": float(Euclidean_radius[-1]),
            "terminal_aligned_to_reference_outward_difference": float(
                outward_difference[-1]
            ),
        },
        "data": DATA.relative_to(ROOT).as_posix(),
        "data_SHA256": _sha256(DATA),
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path)
            for path in (SOURCE, CENTER, JACOBIAN, TANGENT, REFERENCE)
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "claim_boundary": {
            "finite_aligned_Magnus4_evaluation_roundoff": (
                "CERTIFIED_ON_ALL_RECENTERED_QUOTIENT_BLOCKS"
                if complete and args.reset_at_macro else "PARTIAL_BENCHMARK"
            ),
            "aligned_vs_prior_unaligned_proof_coordinate": "OUTWARD_COMPARED",
            "global_block_composition": "OPEN_CORRELATED_RADII_ASSEMBLY",
            "analytic_Magnus4_remainder": "OPEN_INTERVAL_AUTHORITY",
            "signed_Y": "OPEN_INTERVAL_AUTHORITY",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
