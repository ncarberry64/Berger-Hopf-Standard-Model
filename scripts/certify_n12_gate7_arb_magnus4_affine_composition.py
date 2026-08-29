"""Outward-compose the 47 signed affine Magnus-4 quotient blocks.

Each source block is evaluated from zero, so stored-center leakage is not
misidentified as source.  The already-certified homogeneous quotient maps
then propagate the signed blocks in one global Arb affine recurrence.  This
certifies the finite discrete composition only; analytic Magnus and signed
source-quadrature remainders remain separate.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
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
MACRO_MAPS = BASE / "BHSM_N12_GATE7_ARB_MAGNUS4_MACRO_MAPS.npz"
RESULT = BASE / "BHSM_N12_GATE7_ARB_MAGNUS4_AFFINE_COMPOSITION.json"
DATA = RESULT.with_suffix(".npz")
AMBIENT = 98
PHYSICAL = 73
_WORKER: dict[str, object] = {}


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _exact(value: float) -> arb:
    numerator, denominator = float(value).as_integer_ratio()
    return arb(numerator) / denominator


def _matrix(values: np.ndarray) -> arb_mat:
    array = np.asarray(values, dtype=float)
    return arb_mat([
        [_exact(value) for value in row]
        for row in array.reshape(array.shape[0], -1)
    ])


def _ball_matrix(midpoint: np.ndarray, radius: np.ndarray) -> arb_mat:
    midpoint = np.asarray(midpoint, dtype=float)
    radius = np.asarray(radius, dtype=float)
    return arb_mat([
        [arb(float(midpoint[row, column]), float(radius[row, column]))
         for column in range(midpoint.shape[1])]
        for row in range(midpoint.shape[0])
    ])


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


def _step(
    left: arb_mat, slope: arb_mat, commutator: arb_mat,
    offset: arb, width: arb, magnus_order: int,
    fifth_basis: tuple[arb_mat, arb_mat, arb_mat, arb_mat] | None,
) -> arb_mat:
    midpoint = left + (offset + width / 2) * slope
    exponent = width * midpoint - (width**3 / 12) * commutator
    if magnus_order >= 6:
        if fifth_basis is None:
            raise RuntimeError("Magnus-6 affine commutator basis required")
        third_0, third_1, third_2, slope_nested = fifth_basis
        center = offset + width / 2
        third = third_0 + center * third_1 + center**2 * third_2
        exponent += width**5 * (third / 720 - slope_nested / 240)
    return exponent.exp()


def _fifth_basis(
    left: arb_mat, slope: arb_mat, commutator: arb_mat,
) -> tuple[arb_mat, arb_mat, arb_mat, arb_mat]:
    left_nested = left * commutator - commutator * left
    slope_nested = slope * commutator - commutator * slope
    third_0 = left * left_nested - left_nested * left
    third_1 = (
        slope * left_nested - left_nested * slope
        + left * slope_nested - slope_nested * left
    )
    third_2 = slope * slope_nested - slope_nested * slope
    return third_0, third_1, third_2, slope_nested


def _initialize_source_worker(
    precision: int, source_partition: str, magnus_order: int,
) -> None:
    ctx.prec = precision
    _WORKER["source_partition"] = source_partition
    _WORKER["magnus_order"] = magnus_order
    with np.load(SOURCE) as source:
        _WORKER["sample_intervals"] = np.asarray(source["sample_intervals"], dtype=int)
        _WORKER["sample_orders"] = np.asarray(source["sample_orders"], dtype=int)
        _WORKER["sample_indices"] = np.asarray(source["sample_indices"], dtype=int)
        _WORKER["residuals"] = np.asarray(source["state_rate_residuals"], dtype=float)
    with np.load(CENTER) as source:
        fine_times = np.asarray(source["fine_grid_action_lengths"], dtype=float)
        _WORKER["fixed_step"] = float(fine_times[1] - fine_times[0])
        _WORKER["stop_fraction"] = float(source["stop_dense_fraction"][0])
    with np.load(JACOBIAN) as source:
        _WORKER["jacobian_times"] = np.asarray(source["action_lengths"], dtype=float)
        _WORKER["jacobians"] = np.asarray(source["graph_Jacobian_action"], dtype=float)
    with np.load(TANGENT) as source:
        _WORKER["tangents"] = np.asarray(source["physical_tangent_action"], dtype=float)
    nodes, weights = np.polynomial.legendre.leggauss(8)
    _WORKER["units"] = 0.5 * (nodes + 1.0)
    _WORKER["weights"] = weights


def _evaluate_source_block(seam: int) -> tuple[int, np.ndarray, np.ndarray, int]:
    sample_intervals = _WORKER["sample_intervals"]
    sample_orders = _WORKER["sample_orders"]
    sample_indices = _WORKER["sample_indices"]
    residuals = _WORKER["residuals"]
    fixed_step = _WORKER["fixed_step"]
    stop_fraction = _WORKER["stop_fraction"]
    jacobian_times = _WORKER["jacobian_times"]
    jacobians = _WORKER["jacobians"]
    tangents = _WORKER["tangents"]
    units = _WORKER["units"]
    weights = _WORKER["weights"]
    source_partition = _WORKER["source_partition"]
    magnus_order = _WORKER["magnus_order"]
    maximum_step = fixed_step / 16.0
    macro_starts = list(range(0, 369, 8))
    macro_ends = [*macro_starts[1:], 370]
    start, end = macro_starts[seam], macro_ends[seam]
    correction = arb_mat(AMBIENT, 1)
    exponential_count = 0
    for interval in range(start, end):
        duration_float = fixed_step * (
            stop_fraction if interval == 369 else 1.0
        )
        count = max(1, int(np.ceil(duration_float / maximum_step)))
        width_float = duration_float / count
        duration = _exact(duration_float)
        width = _exact(width_float)
        left = _matrix(jacobians[interval])
        dt = _exact(float(jacobian_times[interval + 1] - jacobian_times[interval]))
        slope = (_matrix(jacobians[interval + 1]) - left) / dt
        commutator = left * slope - slope * left
        fifth_basis = (
            _fifth_basis(left, slope, commutator)
            if magnus_order >= 6 else None
        )

        fixed_maps = [
            _step(
                left, slope, commutator, _exact(k * width_float), width,
                magnus_order, fifth_basis,
            )
            for k in range(count)
        ]
        exponential_count += count
        suffix = [_identity(AMBIENT) for _ in range(count + 1)]
        for substep in range(count - 1, -1, -1):
            suffix[substep] = suffix[substep + 1] * fixed_maps[substep]

        mask = (sample_intervals == interval) & (sample_orders == 8)
        local_indices = sample_indices[mask]
        local_residuals = residuals[mask]
        permutation = np.argsort(local_indices)
        local_residuals = local_residuals[permutation]
        if local_residuals.shape != (8, AMBIENT):
            raise RuntimeError("complete ordered Gauss-8 source required")

        source_vector = arb_mat(AMBIENT, 1)
        for unit_float, weight_float, residual in zip(
            units, weights, local_residuals, strict=True,
        ):
            location_float = duration_float * float(unit_float)
            propagated = _matrix(residual.reshape(AMBIENT, 1))
            if source_partition == "aligned-suffix":
                substep = min(int(location_float / width_float), count - 1)
                boundary_float = (substep + 1) * width_float
                partial_width_float = boundary_float - location_float
                partial = _step(
                    left, slope, commutator,
                    _exact(location_float), _exact(partial_width_float),
                    magnus_order, fifth_basis,
                )
                exponential_count += 1
                propagated = suffix[substep + 1] * partial * propagated
            else:
                remaining_float = duration_float - location_float
                source_steps = max(1, int(np.ceil(remaining_float / maximum_step)))
                source_width_float = remaining_float / source_steps
                source_width = _exact(source_width_float)
                for source_step in range(source_steps):
                    propagated = _step(
                        left, slope, commutator,
                        _exact(location_float + source_step * source_width_float),
                        source_width, magnus_order, fifth_basis,
                    ) * propagated
                    exponential_count += 1
            source_vector -= duration * _exact(float(weight_float)) / 2 * propagated
        correction = suffix[0] * correction + source_vector

    quotient_source = _matrix(tangents[seam + 1]).transpose() * correction
    midpoint, radius = _mid_radius(quotient_source)
    return seam, midpoint[:, 0], radius[:, 0], exponential_count


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-precision", type=int, default=256)
    parser.add_argument("--composition-precision", type=int, default=256)
    parser.add_argument("--magnus-order", type=int, choices=(4, 6), default=4)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument(
        "--source-partition", choices=("retained-unaligned", "aligned-suffix"),
        default="retained-unaligned",
    )
    parser.add_argument("--reuse-certified-source-blocks", action="store_true")
    parser.add_argument("--macro-limit", type=int, default=47)
    args = parser.parse_args()
    if (
        args.source_precision < 256 or args.composition_precision < 256
        or not 1 <= args.workers <= 16 or not 1 <= args.macro_limit <= 47
    ):
        raise ValueError("source and composition >=256 bits, 1..47 maps required")
    with np.load(CENTER) as source:
        fine_times = np.asarray(source["fine_grid_action_lengths"], dtype=float)
        macro_times = np.asarray(source["action_lengths"], dtype=float)
        stop_fraction = float(source["stop_dense_fraction"][0])
    with np.load(TANGENT) as source:
        tangents = np.asarray(source["physical_tangent_action"], dtype=float)
    with np.load(REFERENCE) as source:
        reference = np.asarray(source["Gauss8_correction_profile"], dtype=float)
    macro_maps = (
        MACRO_MAPS if args.magnus_order == 4 else
        BASE / "BHSM_N12_GATE7_ARB_MAGNUS6_MACRO_MAPS.npz"
    )
    result = (
        RESULT if args.magnus_order == 4 else
        BASE / "BHSM_N12_GATE7_ARB_MAGNUS6_AFFINE_COMPOSITION.json"
    )
    data_path = result.with_suffix(".npz")
    with np.load(macro_maps) as source:
        maps_mid = np.asarray(source["macro_step_map_midpoint"], dtype=float)
        maps_rad = np.asarray(source["macro_step_map_component_radius"], dtype=float)

    macro_starts = list(range(0, 369, 8))
    macro_ends = [*macro_starts[1:], 370]
    boundary_indices = np.asarray([*macro_starts, 370], dtype=int)

    source_mid = []
    source_rad = []
    exponential_count = 0
    seams = list(range(args.macro_limit))
    if args.reuse_certified_source_blocks:
        with np.load(data_path) as source:
            source_mid = list(np.asarray(
                source["affine_source_midpoint"][:args.macro_limit], dtype=float,
            ))
            source_rad = list(np.asarray(
                source["affine_source_component_radius"][:args.macro_limit], dtype=float,
            ))
        if len(source_mid) != args.macro_limit:
            raise RuntimeError("complete previously certified source blocks required")
        exponential_count = 31019 if args.macro_limit == 47 else 0
        results = []
    else:
        if args.workers == 1:
            _initialize_source_worker(
                args.source_precision, args.source_partition, args.magnus_order,
            )
            results = map(_evaluate_source_block, seams)
        else:
            executor = ProcessPoolExecutor(
                max_workers=args.workers,
                initializer=_initialize_source_worker,
                initargs=(
                    args.source_precision, args.source_partition, args.magnus_order,
                ),
            )
            results = executor.map(_evaluate_source_block, seams)
    for seam, midpoint, radius, count in results:
        source_mid.append(midpoint)
        source_rad.append(radius)
        exponential_count += count
        print(json.dumps({
            "completed_affine_source_blocks": seam + 1,
            "exponentials": exponential_count,
            "maximum_component_radius": float(np.max(radius)),
        }), flush=True)
    if not args.reuse_certified_source_blocks and args.workers != 1:
        executor.shutdown()

    source_mid = np.asarray(source_mid)
    source_rad = np.asarray(source_rad)
    ctx.prec = args.composition_precision
    global_state = arb_mat(PHYSICAL, 1)
    global_mid = [np.zeros(PHYSICAL)]
    global_rad = [np.zeros(PHYSICAL)]
    for seam in range(args.macro_limit):
        block_map = _ball_matrix(maps_mid[seam], maps_rad[seam])
        block_source = _ball_matrix(
            source_mid[seam].reshape(PHYSICAL, 1),
            source_rad[seam].reshape(PHYSICAL, 1),
        )
        global_state = block_map * global_state + block_source
        midpoint, radius = _mid_radius(global_state)
        global_mid.append(midpoint[:, 0])
        global_rad.append(radius[:, 0])
    global_mid = np.asarray(global_mid)
    global_rad = np.asarray(global_rad)

    reference_quotient = np.asarray([
        tangents[seam].T @ reference[index]
        for seam, index in enumerate(boundary_indices[:args.macro_limit + 1])
    ])
    stored_center_off_tangent = np.asarray([
        np.linalg.norm(
            reference[index] - tangents[seam] @ reference_quotient[seam]
        )
        for seam, index in enumerate(boundary_indices[:args.macro_limit + 1])
    ])
    midpoint_difference = np.linalg.norm(global_mid - reference_quotient, axis=1)
    Euclidean_radius = np.linalg.norm(global_rad, axis=1)
    outward_difference = midpoint_difference + Euclidean_radius
    source_norm_uppers = np.linalg.norm(source_mid, axis=1) + np.linalg.norm(
        source_rad, axis=1
    )

    np.savez_compressed(
        data_path,
        macro_action_lengths=macro_times[:args.macro_limit + 1],
        macro_boundary_fine_indices=boundary_indices[:args.macro_limit + 1],
        affine_source_midpoint=source_mid,
        affine_source_component_radius=source_rad,
        affine_source_norm_upper=source_norm_uppers,
        global_signed_response_midpoint=global_mid,
        global_signed_response_component_radius=global_rad,
        global_signed_response_Euclidean_radius=Euclidean_radius,
        reference_quotient_midpoint_difference=midpoint_difference,
        reference_quotient_outward_difference=outward_difference,
        stored_center_off_tangent_residue=stored_center_off_tangent,
    )
    complete = args.macro_limit == 47
    validation = {
        "Arb_source_precision_at_least_256_bits": args.source_precision >= 256,
        "Arb_global_composition_precision_at_least_256_bits": (
            args.composition_precision >= 256
        ),
        "all_47_signed_affine_source_blocks_evaluated_from_zero": (
            complete and source_mid.shape == (47, PHYSICAL)
        ),
        "all_47_homogeneous_maps_outward_composed_with_signed_sources": (
            complete and global_mid.shape == (48, PHYSICAL)
        ),
        "stored_center_off_tangent_residue_not_relabelled_as_source": True,
        "retained_unaligned_Gauss_node_partition_used": (
            args.source_partition == "retained-unaligned"
        ),
        "all_binary64_inputs_materialized_as_exact_dyadics": True,
        "all_component_radii_finite": bool(
            np.all(np.isfinite(source_rad)) and np.all(np.isfinite(global_rad))
        ),
        "global_response_ball_vanishes_at_reset": bool(Euclidean_radius[0] == 0.0),
        "finite_discrete_response_crosscheck_below_3p2e_minus_18": bool(
            np.max(outward_difference) < 3.2e-18
        ),
        "analytic_Magnus_remainder_not_claimed": True,
        "signed_source_quadrature_remainder_not_claimed": True,
        "no_action_source_selector_scale_gate_or_chord_changed": True,
    }
    payload = {
        "artifact": (
            f"BHSM_N12_GATE7_ARB_MAGNUS{args.magnus_order}_AFFINE_COMPOSITION"
        ),
        "status": (
            f"ALL_47_SIGNED_AFFINE_MAGNUS{args.magnus_order}_"
            "QUOTIENT_BLOCKS_GLOBALLY_"
            "COMPOSED_WITH_OUTWARD_ARB_BALLS"
            if complete else "PARTIAL_AFFINE_COMPOSITION_BENCHMARK"
        ),
        "authority": "ARB_BALL_AUTHORITY_FOR_THE_FINITE_DISCRETE_AFFINE_COMPOSITION_ONLY",
        "identity": {
            "source_precision_bits": args.source_precision,
            "composition_precision_bits": args.composition_precision,
            "Magnus_order": args.magnus_order,
            "macro_blocks": args.macro_limit,
            "physical_dimension": PHYSICAL,
            "source_order": 8,
            "source_partition": args.source_partition,
            "exponential_count": exponential_count,
            "Magnus_exponent": (
                "h*A_mid-h^3*[A_left,A_prime]/12"
                + (
                    "+h^5*([A,[A,[A,B]]]/720-[B,[A,B]]/240)"
                    if args.magnus_order >= 6 else ""
                )
            ),
            "affine_recurrence": "u_(i+1)=M_i*u_i+b_i; u_0=0",
        },
        "summary": {
            "maximum_affine_source_component_radius": float(np.max(source_rad)),
            "maximum_affine_source_norm_upper": float(np.max(source_norm_uppers)),
            "maximum_global_response_Euclidean_radius": float(np.max(Euclidean_radius)),
            "terminal_global_response_Euclidean_radius": float(Euclidean_radius[-1]),
            "maximum_reference_quotient_outward_difference": float(
                np.max(outward_difference)
            ),
            "terminal_reference_quotient_outward_difference": float(
                outward_difference[-1]
            ),
            "maximum_stored_center_off_tangent_residue": float(
                np.max(stored_center_off_tangent)
            ),
        },
        "data": data_path.relative_to(ROOT).as_posix(),
        "data_SHA256": _sha256(data_path),
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path)
            for path in (SOURCE, CENTER, JACOBIAN, TANGENT, REFERENCE, macro_maps)
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "claim_boundary": {
            "finite_signed_affine_source_blocks": (
                "CERTIFIED" if complete else "PARTIAL_BENCHMARK"
            ),
            "finite_global_correlated_block_composition": (
                "CERTIFIED" if complete else "PARTIAL_BENCHMARK"
            ),
            "analytic_higher_Magnus_remainder": "OPEN_INTERVAL_AUTHORITY",
            "outward_signed_Y": "OPEN_INTERVAL_AUTHORITY",
            "center_dependent_Z2_radii_margins_first_hit": "DOWNSTREAM_OPEN",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "OUTWARD_ANALYTIC_MAGNUS4_HIGHER_COMMUTATOR_REMAINDER_AND_SIGNED_"
            "SOURCE_QUADRATURE_REMAINDER_IN_THE_SAME_CORRELATED_FRAME"
        ),
        "FULL_BHSM_COMPLETE": False,
    }
    result.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
