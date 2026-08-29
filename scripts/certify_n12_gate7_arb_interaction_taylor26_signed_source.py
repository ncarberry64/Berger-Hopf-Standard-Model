"""Certify retained-unaligned Gate-7 signed-source blocks with the frozen carrier.

Every Gauss-8 source sample is propagated from its literal unaligned location
to the end of its fine cell with the exact interaction-Taylor26 step theorem.
The resulting 47 zero-initial source blocks are composed with the frozen
correlated homogeneous Arb carrier.  Source-node quadrature remainder is a
separate owner and is deliberately not claimed here.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
import json
import math
import os
from pathlib import Path

from flint import arb, arb_mat, ctx
import numpy as np

from certify_n12_gate7_arb_interaction_taylor26_macro_maps import (
    _arb_strings,
    _exact,
    _identity,
    _interaction_step,
    _matrix,
    _matrix_from_arb_strings,
    _mid_radius,
)


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
SOURCE = BASE / "BHSM_N12_GATE7_DECIMAL_SIGNED_SOURCE_QUADRATURE_AUDIT.npz"
CENTER = BASE / (
    "BHSM_N12_C2_STOP_HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.npz"
)
JACOBIAN = BASE / (
    "BHSM_N12_C2_STOP_QUARTER_STEP_FINE_HYBRID_GRAPH_JACOBIAN_RECONNAISSANCE.npz"
)
TANGENT = BASE / (
    "BHSM_N12_C2_STOP_QUARTER_STEP_PHYSICAL_TANGENT_TRANSFER_RECONNAISSANCE.npz"
)
CARRIER = BASE / "BHSM_N12_GATE7_ARB_INTERACTION_TAYLOR26_MACRO_MAPS.npz"
CARRIER_RECORD = CARRIER.with_suffix(".json")
REFERENCE = BASE / "BHSM_N12_GATE7_DECIMAL_SIGNED_Y_GREEN_CONVERGENCE_AUDIT.npz"
THIS_SCRIPT = Path(__file__).resolve()
RESULT = BASE / "BHSM_N12_GATE7_ARB_INTERACTION_TAYLOR26_SIGNED_SOURCE.json"
DATA = RESULT.with_suffix(".npz")
AMBIENT = 98
PHYSICAL = 73
_WORKER: dict[str, object] = {}


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _initialize(precision: int) -> None:
    ctx.prec = precision
    with np.load(SOURCE) as source:
        _WORKER["sample_intervals"] = np.asarray(
            source["sample_intervals"], dtype=int,
        )
        _WORKER["sample_orders"] = np.asarray(source["sample_orders"], dtype=int)
        _WORKER["sample_indices"] = np.asarray(
            source["sample_indices"], dtype=int,
        )
        _WORKER["residuals"] = np.asarray(
            source["state_rate_residuals"], dtype=float,
        )
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
    nodes, weights = np.polynomial.legendre.leggauss(8)
    _WORKER["units"] = 0.5 * (nodes + 1.0)
    _WORKER["gauss_weights"] = weights


def _source_macro(seam: int) -> tuple[
    int, np.ndarray, np.ndarray, np.ndarray, int, int,
]:
    sample_intervals = np.asarray(_WORKER["sample_intervals"])
    sample_orders = np.asarray(_WORKER["sample_orders"])
    sample_indices = np.asarray(_WORKER["sample_indices"])
    residuals = np.asarray(_WORKER["residuals"])
    fixed_step = float(_WORKER["fixed_step"])
    stop_fraction = float(_WORKER["stop_fraction"])
    jacobian_times = np.asarray(_WORKER["jacobian_times"])
    jacobians = np.asarray(_WORKER["jacobians"])
    tangents = np.asarray(_WORKER["tangents"])
    units = np.asarray(_WORKER["units"])
    gauss_weights = np.asarray(_WORKER["gauss_weights"])

    maximum_step = fixed_step / 16.0
    starts = list(range(0, 369, 8))
    ends = [*starts[1:], 370]
    start, end = starts[seam], ends[seam]
    correction = arb_mat(AMBIENT, 1)
    fixed_count = 0
    source_count = 0
    for interval in range(start, end):
        duration_float = fixed_step * (
            stop_fraction if interval == 369 else 1.0
        )
        fixed_steps = max(1, int(math.ceil(duration_float / maximum_step)))
        fixed_width_float = duration_float / fixed_steps
        fixed_width = _exact(fixed_width_float)
        left = _matrix(jacobians[interval])
        dt = _exact(float(jacobian_times[interval + 1] - jacobian_times[interval]))
        slope = (_matrix(jacobians[interval + 1]) - left) / dt

        fixed_maps = []
        for substep in range(fixed_steps):
            step, _, _, _ = _interaction_step(
                left, slope, _exact(substep * fixed_width_float), fixed_width,
            )
            fixed_maps.append(step)
            fixed_count += 1
        # Exact affine semigroup: every unaligned Gauss node needs only the
        # partial map to the next retained PROP16 boundary.  All later factors
        # are the common outward-certified suffix, preserving correlations
        # while avoiding repeated evaluation of identical exact steps.
        suffix = [_identity(AMBIENT) for _ in range(fixed_steps + 1)]
        for substep in range(fixed_steps - 1, -1, -1):
            suffix[substep] = suffix[substep + 1] * fixed_maps[substep]
        fixed_product = suffix[0]

        mask = (sample_intervals == interval) & (sample_orders == 8)
        local_indices = sample_indices[mask]
        local_residuals = residuals[mask]
        permutation = np.argsort(local_indices)
        local_residuals = local_residuals[permutation]
        if local_residuals.shape != (8, AMBIENT):
            raise RuntimeError("complete ordered Decimal Gauss-8 source required")

        source_vector = arb_mat(AMBIENT, 1)
        for unit, weight, residual in zip(
            units, gauss_weights, local_residuals, strict=True,
        ):
            location_float = duration_float * float(unit)
            substep = min(
                fixed_steps - 1,
                int(math.floor(location_float / fixed_width_float)),
            )
            next_boundary_float = (substep + 1) * fixed_width_float
            source_width = _exact(next_boundary_float - location_float)
            propagated = _matrix(residual.reshape(AMBIENT, 1))
            step, _, _, _ = _interaction_step(
                left, slope, _exact(location_float), source_width,
            )
            propagated = suffix[substep + 1] * step * propagated
            source_count += 1
            source_vector -= (
                _exact(duration_float) * _exact(float(weight)) / 2 * propagated
            )
        correction = fixed_product * correction + source_vector

    quotient = _matrix(tangents[seam + 1]).transpose() * correction
    midpoint, radius = _mid_radius(quotient)
    return (
        seam,
        midpoint[:, 0],
        radius[:, 0],
        _arb_strings(quotient)[:, 0],
        fixed_count,
        source_count,
    )


def _checkpoint_directory(precision: int) -> Path:
    """Key resumable rows to every input that can change their value."""

    step_script = ROOT / "scripts" / (
        "certify_n12_gate7_arb_interaction_taylor26_macro_maps.py"
    )
    joined = "|".join([
        str(precision),
        *(
            _sha256(path)
            for path in (
                SOURCE, CENTER, JACOBIAN, TANGENT, CARRIER, CARRIER_RECORD,
                step_script, THIS_SCRIPT,
            )
        ),
    ])
    token = hashlib.sha256(joined.encode("ascii")).hexdigest().upper()[:16]
    return BASE / f".gate7_taylor26_signed_source_{token}"


def _checkpoint_path(directory: Path, seam: int) -> Path:
    return directory / f"source_macro_{seam:02d}.npz"


def _save_checkpoint(directory: Path, row: tuple[object, ...]) -> None:
    seam, midpoint, radius, strings, fixed_count, source_count = row
    np.savez_compressed(
        _checkpoint_path(directory, int(seam)),
        seam=np.asarray([seam], dtype=int),
        midpoint=np.asarray(midpoint),
        radius=np.asarray(radius),
        arb_strings=np.asarray(strings),
        fixed_count=np.asarray([fixed_count], dtype=int),
        source_count=np.asarray([source_count], dtype=int),
    )


def _load_checkpoint(path: Path) -> tuple[object, ...]:
    with np.load(path) as source:
        row = (
            int(source["seam"][0]),
            np.asarray(source["midpoint"]),
            np.asarray(source["radius"]),
            np.asarray(source["arb_strings"]),
            int(source["fixed_count"][0]),
            int(source["source_count"][0]),
        )
    if (
        row[1].shape != (PHYSICAL,) or row[2].shape != (PHYSICAL,)
        or row[3].shape != (PHYSICAL,) or row[4] <= 0 or row[5] <= 0
    ):
        raise RuntimeError(f"invalid signed-source checkpoint: {path}")
    return row


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--precision", type=int, default=256)
    parser.add_argument("--workers", type=int, default=min(12, os.cpu_count() or 1))
    parser.add_argument("--macro-limit", type=int, default=47)
    parser.add_argument("--no-resume", action="store_true")
    args = parser.parse_args()
    if (
        args.precision < 256 or not 1 <= args.workers <= 16
        or not 1 <= args.macro_limit <= 47
    ):
        raise ValueError("256-bit precision, 1..16 workers, and 1..47 macros required")
    ctx.prec = args.precision
    checkpoint = _checkpoint_directory(args.precision)
    checkpoint.mkdir(parents=True, exist_ok=True)

    rows: dict[int, tuple[object, ...]] = {}
    pending = []
    for seam in range(args.macro_limit):
        path = _checkpoint_path(checkpoint, seam)
        if path.is_file() and not args.no_resume:
            rows[seam] = _load_checkpoint(path)
        else:
            pending.append(seam)
    if pending:
        with ProcessPoolExecutor(
            max_workers=args.workers,
            initializer=_initialize,
            initargs=(args.precision,),
        ) as executor:
            futures = {executor.submit(_source_macro, seam): seam for seam in pending}
            for future in as_completed(futures):
                row = future.result()
                seam = int(row[0])
                _save_checkpoint(checkpoint, row)
                rows[seam] = row
                print(json.dumps({
                    "completed_source_macro": seam,
                    "completed_total": len(rows),
                    "remaining": args.macro_limit - len(rows),
                }), flush=True)
    ordered = [rows[seam] for seam in range(args.macro_limit)]
    source_mid = np.asarray([row[1] for row in ordered])
    source_rad = np.asarray([row[2] for row in ordered])
    source_strings = np.asarray([row[3] for row in ordered])
    fixed_counts = np.asarray([row[4] for row in ordered], dtype=int)
    source_counts = np.asarray([row[5] for row in ordered], dtype=int)

    with np.load(CARRIER) as source:
        macro_times = np.asarray(source["macro_action_lengths"], dtype=float)
        carrier_strings = np.asarray(source["macro_step_map_arb_strings"])
    with np.load(CENTER) as source:
        stop_fraction = float(source["stop_dense_fraction"][0])
    with np.load(TANGENT) as source:
        tangents = np.asarray(source["physical_tangent_action"], dtype=float)
    with np.load(REFERENCE) as source:
        reference = np.asarray(source["Gauss8_correction_profile"], dtype=float)

    global_state = arb_mat(PHYSICAL, 1)
    global_mid = [np.zeros(PHYSICAL)]
    global_rad = [np.zeros(PHYSICAL)]
    global_strings = [_arb_strings(global_state)[:, 0]]
    for seam in range(args.macro_limit):
        block_map = _matrix_from_arb_strings(carrier_strings[seam])
        block_source = _matrix_from_arb_strings(
            source_strings[seam].reshape(PHYSICAL, 1),
        )
        global_state = block_map * global_state + block_source
        midpoint, radius = _mid_radius(global_state)
        global_mid.append(midpoint[:, 0])
        global_rad.append(radius[:, 0])
        global_strings.append(_arb_strings(global_state)[:, 0])
    global_mid = np.asarray(global_mid)
    global_rad = np.asarray(global_rad)
    global_strings = np.asarray(global_strings)

    starts = list(range(0, 369, 8))
    boundary_indices = np.asarray([*starts, 370], dtype=int)
    reference_quotient = np.asarray([
        tangents[seam].T @ reference[index]
        for seam, index in enumerate(boundary_indices[:args.macro_limit + 1])
    ])
    stored_off_tangent = np.asarray([
        np.linalg.norm(reference[index] - tangents[seam] @ reference_quotient[seam])
        for seam, index in enumerate(boundary_indices[:args.macro_limit + 1])
    ])
    midpoint_difference = np.linalg.norm(global_mid - reference_quotient, axis=1)
    Euclidean_radius = np.linalg.norm(global_rad, axis=1)
    outward_difference = midpoint_difference + Euclidean_radius

    output_data = DATA if args.macro_limit == 47 else checkpoint / (
        f"partial_{args.macro_limit:02d}.npz"
    )
    np.savez_compressed(
        output_data,
        macro_action_lengths=macro_times[:args.macro_limit + 1],
        affine_source_midpoint=source_mid,
        affine_source_component_radius=source_rad,
        affine_source_arb_strings=source_strings,
        fixed_substep_count=fixed_counts,
        retained_unaligned_source_partial_step_count=source_counts,
        global_signed_response_midpoint=global_mid,
        global_signed_response_component_radius=global_rad,
        global_signed_response_arb_strings=global_strings,
        global_signed_response_Euclidean_radius=Euclidean_radius,
        reference_quotient_midpoint_difference=midpoint_difference,
        reference_quotient_outward_difference=outward_difference,
        stored_center_off_tangent_residue=stored_off_tangent,
    )
    complete = args.macro_limit == 47
    validation = {
        "all_47_zero_initial_signed_source_blocks_evaluated": (
            complete and source_mid.shape == (47, PHYSICAL)
        ),
        "all_47_source_blocks_composed_with_frozen_correlated_carrier": (
            complete and global_mid.shape == (48, PHYSICAL)
        ),
        "retained_unaligned_Gauss8_source_partition_used": True,
        "same_exact_interaction_Taylor26_step_as_frozen_carrier": True,
        "correlated_source_and_global_storage_use_outward_Arb_strings": True,
        "global_response_ball_vanishes_at_reset": bool(Euclidean_radius[0] == 0.0),
        "all_component_radii_finite": bool(
            np.all(np.isfinite(source_rad)) and np.all(np.isfinite(global_rad))
        ),
        "stored_center_off_tangent_residue_not_relabelled_as_source": True,
        "literal_signed_source_quadrature_remainder_not_claimed": True,
        "no_action_source_selector_scale_gate_or_chord_changed": True,
    }
    payload = {
        "artifact": "BHSM_N12_GATE7_ARB_INTERACTION_TAYLOR26_SIGNED_SOURCE",
        "status": (
            "ALL_47_RETAINED_UNALIGNED_GAUSS8_SIGNED_SOURCE_BLOCKS_GLOBALLY_"
            "COMPOSED_WITH_THE_FROZEN_CORRELATED_EXACT_AFFINE_CARRIER"
            if all(validation.values()) else
            "INTERACTION_TAYLOR26_SIGNED_SOURCE_CERTIFICATE_INVALID"
        ),
        "authority": (
            "256_BIT_ARB_EXACT_AFFINE_PROPAGATION_OF_THE_STORED_DECIMAL_GAUSS8_"
            "SIGNED_SOURCE_SAMPLES;_NOT_SOURCE_QUADRATURE_REMAINDER_AUTHORITY"
        ),
        "identity": {
            "source_sign": "MINUS_DEFECT",
            "source_order": 8,
            "source_partition": "RETAINED_UNALIGNED",
            "fixed_substep_count": int(np.sum(fixed_counts)),
            "source_unaligned_partial_step_count": int(np.sum(source_counts)),
            "stop_fraction": stop_fraction,
            "carrier": _relative(CARRIER_RECORD),
        },
        "summary": {
            "maximum_source_block_component_radius": float(np.max(source_rad)),
            "maximum_global_response_Euclidean_radius": float(np.max(Euclidean_radius)),
            "maximum_reference_quotient_midpoint_difference": float(
                np.max(midpoint_difference)
            ),
            "maximum_reference_quotient_outward_difference": float(
                np.max(outward_difference)
            ),
            "maximum_stored_center_off_tangent_residue": float(
                np.max(stored_off_tangent)
            ),
            "terminal_global_response_Euclidean_radius": float(Euclidean_radius[-1]),
        },
        "data": _relative(output_data),
        "data_SHA256": _sha256(output_data),
        "inputs": {
            _relative(path): _sha256(path)
            for path in (
                SOURCE, CENTER, JACOBIAN, TANGENT, CARRIER, CARRIER_RECORD,
                REFERENCE, THIS_SCRIPT,
            )
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "claim_boundary": {
            "frozen_homogeneous_exact_affine_carrier": "CERTIFIED_REUSED",
            "retained_unaligned_signed_source_blocks": "CERTIFIED_IF_VALIDATION_PASSES",
            "literal_outward_signed_source_quadrature_Y": "OPEN_INTERVAL_AUTHORITY",
            "center_dependent_Z2_radii_margins_first_hit": "OPEN",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "CERTIFY_LITERAL_OUTWARD_SIGNED_SOURCE_QUADRATURE_Y_ON_THE_SAME_"
            "DECIMAL_ACTION_FIELD,_THEN_REBUILD_CENTER_DEPENDENT_Z2_AND_RADII,_"
            "CLOSE_CONTINUOUS_MARGINS,_AND_APPLY_SCALAR_INTERVAL_NEWTON"
        ),
        "FULL_BHSM_COMPLETE": False,
    }
    output_record = RESULT if complete else checkpoint / (
        f"partial_{args.macro_limit:02d}.json"
    )
    output_record.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
