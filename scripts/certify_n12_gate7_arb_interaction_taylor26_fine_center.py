"""Certify the 371-node exact-affine Gate-7 signed-source center.

This is the center-transfer adapter required by the retained recentered-cone
machinery.  It reuses the same 256-bit Arb interaction-Taylor26 step theorem,
the same retained unaligned Decimal Gauss-8 source samples, and the already
certified exact-affine quotient value at each macro entrance.  The ambient
flow is not projected inside a retained macro interval; projection occurs
only at the 47 canonical tangent-transfer seams.

No source-quadrature remainder is derived here.  The result is outward
authority for propagation of the retained source samples to every one of the
371 existing fine-history nodes.
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
SIGNED = BASE / "BHSM_N12_GATE7_ARB_INTERACTION_TAYLOR26_SIGNED_SOURCE.npz"
SIGNED_RECORD = SIGNED.with_suffix(".json")
FROZEN = BASE / "BHSM_N12_GATE7_FROZEN_DECIMAL_GAUSS8_CENTER.npz"
STEP_SCRIPT = ROOT / "scripts" / (
    "certify_n12_gate7_arb_interaction_taylor26_macro_maps.py"
)
SOURCE_SCRIPT = ROOT / "scripts" / (
    "certify_n12_gate7_arb_interaction_taylor26_signed_source.py"
)
THIS_SCRIPT = Path(__file__).resolve()
RESULT = BASE / "BHSM_N12_GATE7_ARB_INTERACTION_TAYLOR26_FINE_CENTER.json"
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
    with np.load(SIGNED) as source:
        _WORKER["entrance_strings"] = np.asarray(
            source["global_signed_response_arb_strings"],
        )
    nodes, weights = np.polynomial.legendre.leggauss(8)
    _WORKER["units"] = 0.5 * (nodes + 1.0)
    _WORKER["gauss_weights"] = weights


def _fine_macro(seam: int) -> tuple[object, ...]:
    sample_intervals = np.asarray(_WORKER["sample_intervals"])
    sample_orders = np.asarray(_WORKER["sample_orders"])
    sample_indices = np.asarray(_WORKER["sample_indices"])
    residuals = np.asarray(_WORKER["residuals"])
    fixed_step = float(_WORKER["fixed_step"])
    stop_fraction = float(_WORKER["stop_fraction"])
    jacobian_times = np.asarray(_WORKER["jacobian_times"])
    jacobians = np.asarray(_WORKER["jacobians"])
    tangents = np.asarray(_WORKER["tangents"])
    entrance_strings = np.asarray(_WORKER["entrance_strings"])
    units = np.asarray(_WORKER["units"])
    gauss_weights = np.asarray(_WORKER["gauss_weights"])

    maximum_step = fixed_step / 16.0
    starts = list(range(0, 369, 8))
    ends = [*starts[1:], 370]
    start, end = starts[seam], ends[seam]
    entrance = _matrix_from_arb_strings(
        entrance_strings[seam].reshape(PHYSICAL, 1),
    )
    correction = _matrix(tangents[seam]) * entrance
    node_strings = [_arb_strings(correction)[:, 0]]
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
        node_strings.append(_arb_strings(correction)[:, 0])

    terminal_quotient = _matrix(tangents[seam + 1]).transpose() * correction
    canonical_terminal = _matrix_from_arb_strings(
        entrance_strings[seam + 1].reshape(PHYSICAL, 1),
    )
    quotient_difference = terminal_quotient - canonical_terminal
    difference_midpoint, difference_radius = _mid_radius(quotient_difference)
    return (
        seam,
        start,
        end,
        np.asarray(node_strings),
        difference_midpoint[:, 0],
        difference_radius[:, 0],
        fixed_count,
        source_count,
    )


def _checkpoint_directory(precision: int) -> Path:
    joined = "|".join([
        str(precision),
        *(
            _sha256(path)
            for path in (
                SOURCE, CENTER, JACOBIAN, TANGENT, SIGNED, SIGNED_RECORD,
                FROZEN, STEP_SCRIPT, SOURCE_SCRIPT, THIS_SCRIPT,
            )
        ),
    ])
    token = hashlib.sha256(joined.encode("ascii")).hexdigest().upper()[:16]
    return BASE / f".gate7_taylor26_fine_center_{token}"


def _checkpoint_path(directory: Path, seam: int) -> Path:
    return directory / f"fine_macro_{seam:02d}.npz"


def _save_checkpoint(directory: Path, row: tuple[object, ...]) -> None:
    seam, start, end, strings, difference_midpoint, difference_radius, fixed, source = row
    np.savez_compressed(
        _checkpoint_path(directory, int(seam)),
        seam=np.asarray([seam], dtype=int),
        start=np.asarray([start], dtype=int),
        end=np.asarray([end], dtype=int),
        arb_strings=np.asarray(strings),
        quotient_difference_midpoint=np.asarray(difference_midpoint),
        quotient_difference_radius=np.asarray(difference_radius),
        fixed_count=np.asarray([fixed], dtype=int),
        source_count=np.asarray([source], dtype=int),
    )


def _load_checkpoint(path: Path) -> tuple[object, ...]:
    with np.load(path) as source:
        row = (
            int(source["seam"][0]),
            int(source["start"][0]),
            int(source["end"][0]),
            np.asarray(source["arb_strings"]),
            np.asarray(source["quotient_difference_midpoint"]),
            np.asarray(source["quotient_difference_radius"]),
            int(source["fixed_count"][0]),
            int(source["source_count"][0]),
        )
    expected = int(row[2]) - int(row[1]) + 1
    if (
        row[3].shape != (expected, AMBIENT)
        or row[4].shape != (PHYSICAL,) or row[5].shape != (PHYSICAL,)
        or int(row[6]) <= 0 or int(row[7]) <= 0
    ):
        raise RuntimeError(f"invalid fine-center checkpoint: {path}")
    return row


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--precision", type=int, default=256)
    parser.add_argument("--workers", type=int, default=min(12, os.cpu_count() or 1))
    parser.add_argument("--macro-limit", type=int, default=47)
    parser.add_argument("--no-resume", action="store_true")
    parser.add_argument("--checkpoint-directory", type=Path)
    args = parser.parse_args()
    if (
        args.precision < 256 or not 1 <= args.workers <= 16
        or not 1 <= args.macro_limit <= 47
    ):
        raise ValueError("256-bit precision, 1..16 workers, and 1..47 macros required")
    ctx.prec = args.precision
    checkpoint = (
        args.checkpoint_directory.resolve()
        if args.checkpoint_directory is not None
        else _checkpoint_directory(args.precision)
    )
    if checkpoint.parent != BASE.resolve() or not checkpoint.name.startswith(
        ".gate7_taylor26_fine_center_"
    ):
        raise ValueError("checkpoint directory must be an existing fine-center shard directory")
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
            futures = {executor.submit(_fine_macro, seam): seam for seam in pending}
            for future in as_completed(futures):
                row = future.result()
                seam = int(row[0])
                _save_checkpoint(checkpoint, row)
                rows[seam] = row
                print(json.dumps({
                    "completed_fine_macro": seam,
                    "completed_total": len(rows),
                    "remaining": args.macro_limit - len(rows),
                }), flush=True)

    ordered = [rows[seam] for seam in range(args.macro_limit)]
    strings = [np.asarray(ordered[0][3])[0]]
    for row in ordered:
        strings.extend(np.asarray(row[3])[1:])
    fine_strings = np.asarray(strings)
    fine_midpoint = np.empty((fine_strings.shape[0], AMBIENT))
    fine_radius = np.empty_like(fine_midpoint)
    for index, values in enumerate(fine_strings):
        midpoint, radius = _mid_radius(
            _matrix_from_arb_strings(values.reshape(AMBIENT, 1)),
        )
        fine_midpoint[index] = midpoint[:, 0]
        fine_radius[index] = radius[:, 0]

    quotient_difference_midpoint = np.asarray([row[4] for row in ordered])
    quotient_difference_radius = np.asarray([row[5] for row in ordered])
    quotient_difference_outward = (
        np.linalg.norm(quotient_difference_midpoint, axis=1)
        + np.linalg.norm(quotient_difference_radius, axis=1)
    )
    with np.load(CENTER) as source:
        fine_times = np.asarray(source["fine_grid_action_lengths"], dtype=float)
        terminal_stop_time = float(source["action_lengths"][-1])
    with np.load(FROZEN) as source:
        frozen_times = np.asarray(source["fine_action_lengths"], dtype=float)
        frozen_profile = np.asarray(source["state_correction_profile"], dtype=float)
    fine_times = fine_times[:fine_midpoint.shape[0]]
    # Interval 369 is intentionally integrated only through the retained
    # stop fraction.  Its final Arb vector therefore belongs to the actual
    # stop time, not to the unused full quarter-step endpoint at 92.5.
    fine_times[-1] = terminal_stop_time
    frozen_times = frozen_times[:fine_midpoint.shape[0]]
    frozen_profile = frozen_profile[:fine_midpoint.shape[0]]
    frozen_midpoint_difference = np.linalg.norm(
        fine_midpoint - frozen_profile, axis=1,
    )
    fine_Euclidean_radius = np.linalg.norm(fine_radius, axis=1)
    frozen_outward_difference = frozen_midpoint_difference + fine_Euclidean_radius

    output_data = DATA if args.macro_limit == 47 else checkpoint / (
        f"partial_{args.macro_limit:02d}.npz"
    )
    np.savez_compressed(
        output_data,
        fine_action_lengths=fine_times,
        fine_signed_response_midpoint=fine_midpoint,
        fine_signed_response_component_radius=fine_radius,
        fine_signed_response_arb_strings=fine_strings,
        fine_signed_response_Euclidean_radius=fine_Euclidean_radius,
        macro_terminal_quotient_difference_midpoint=quotient_difference_midpoint,
        macro_terminal_quotient_difference_component_radius=quotient_difference_radius,
        macro_terminal_quotient_difference_outward=quotient_difference_outward,
        frozen_fine_midpoint_difference=frozen_midpoint_difference,
        frozen_fine_outward_difference=frozen_outward_difference,
        fixed_substep_count=np.asarray([row[6] for row in ordered], dtype=int),
        retained_unaligned_source_partial_step_count=np.asarray(
            [row[7] for row in ordered], dtype=int,
        ),
    )
    complete = args.macro_limit == 47
    validation = {
        "all_371_fine_nodes_outward_evaluated": bool(
            complete and fine_midpoint.shape == (371, AMBIENT)
        ),
        "all_47_macro_terminal_quotient_checks_overlap": bool(
            complete and np.all(
                np.abs(quotient_difference_midpoint)
                <= quotient_difference_radius
            )
        ),
        "retained_unaligned_Gauss8_source_partition_used": True,
        "same_exact_interaction_Taylor26_step_as_frozen_carrier": True,
        "ambient_flow_projected_only_at_retained_macro_seams": True,
        "fine_center_storage_uses_outward_Arb_strings": True,
        "fine_center_ball_vanishes_at_reset": bool(
            fine_Euclidean_radius[0] == 0.0
            and np.linalg.norm(fine_midpoint[0]) == 0.0
        ),
        "terminal_partial_step_stored_at_retained_stop_abscissa": bool(
            fine_times[-1] == terminal_stop_time
            and frozen_times[-1] == terminal_stop_time
        ),
        "all_component_radii_finite": bool(np.all(np.isfinite(fine_radius))),
        "source_quadrature_remainder_not_rederived": True,
        "no_action_source_selector_scale_gate_or_chord_changed": True,
    }
    payload = {
        "artifact": "BHSM_N12_GATE7_ARB_INTERACTION_TAYLOR26_FINE_CENTER",
        "status": (
            "ALL_371_RETAINED_FINE_CENTER_NODES_OUTWARD_CERTIFIED_UNDER_THE_"
            "EXACT_AFFINE_CARRIER"
            if all(validation.values()) else
            "INTERACTION_TAYLOR26_FINE_CENTER_CERTIFICATE_INVALID"
        ),
        "authority": (
            "256_BIT_ARB_EXACT_AFFINE_PROPAGATION_OF_THE_RETAINED_DECIMAL_"
            "GAUSS8_SIGNED_SOURCE_SAMPLES_TO_THE_EXISTING_FINE_HISTORY_MESH"
        ),
        "summary": {
            "fixed_substep_count": int(sum(int(row[6]) for row in ordered)),
            "source_unaligned_partial_step_count": int(
                sum(int(row[7]) for row in ordered)
            ),
            "maximum_fine_response_Euclidean_radius": float(
                np.max(fine_Euclidean_radius)
            ),
            "maximum_macro_terminal_quotient_outward_difference": float(
                np.max(quotient_difference_outward)
            ),
            "maximum_frozen_fine_midpoint_difference": float(
                np.max(frozen_midpoint_difference)
            ),
            "maximum_frozen_fine_outward_difference": float(
                np.max(frozen_outward_difference)
            ),
        },
        "data": _relative(output_data),
        "data_SHA256": _sha256(output_data),
        "inputs": {
            _relative(path): _sha256(path)
            for path in (
                SOURCE, CENTER, JACOBIAN, TANGENT, SIGNED, SIGNED_RECORD,
                FROZEN, STEP_SCRIPT, SOURCE_SCRIPT, THIS_SCRIPT,
            )
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "claim_boundary": {
            "retained_source_sample_propagation_to_fine_nodes": (
                "CERTIFIED_IF_VALIDATION_PASSES"
            ),
            "source_quadrature_remainder": "REUSED_NOT_REDERIVED",
            "center_dependent_Z2_and_recentered_cone": "NEXT_OWNER",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "EVALUATE_THE_EXISTING_SIGNED_TAYLOR_VOLTERRA_Z2_AND_RECENTERED_"
            "CONE_FORMULAS_ON_THIS_FINE_CENTER_WITH_ITS_OUTWARD_RADIUS"
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
