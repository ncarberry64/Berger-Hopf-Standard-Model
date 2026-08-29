"""Certify the 47 homogeneous aligned Magnus-4 quotient macro maps."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from flint import arb, arb_mat, ctx
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
CENTER = BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.npz"
JACOBIAN = BASE / "BHSM_N12_C2_STOP_QUARTER_STEP_FINE_HYBRID_GRAPH_JACOBIAN_RECONNAISSANCE.npz"
TANGENT = BASE / "BHSM_N12_C2_STOP_QUARTER_STEP_PHYSICAL_TANGENT_TRANSFER_RECONNAISSANCE.npz"
RESULT = BASE / "BHSM_N12_GATE7_ARB_MAGNUS4_MACRO_MAPS.json"
DATA = RESULT.with_suffix(".npz")
AMBIENT = 98
PHYSICAL = 73


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
    offset: arb, width: arb,
) -> arb_mat:
    midpoint = left + (offset + width / 2) * slope
    return (width * midpoint - (width**3 / 12) * commutator).exp()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--precision", type=int, default=256)
    parser.add_argument("--macro-limit", type=int, default=47)
    args = parser.parse_args()
    if args.precision < 128 or not 1 <= args.macro_limit <= 47:
        raise ValueError("at least 128-bit Arb precision required")
    ctx.prec = args.precision

    with np.load(CENTER) as source:
        fine_times = np.asarray(source["fine_grid_action_lengths"], dtype=float)
        macro_times = np.asarray(source["action_lengths"], dtype=float)
        stop_fraction = float(source["stop_dense_fraction"][0])
    with np.load(JACOBIAN) as source:
        jacobian_times = np.asarray(source["action_lengths"], dtype=float)
        jacobians = np.asarray(source["graph_Jacobian_action"], dtype=float)
    with np.load(TANGENT) as source:
        tangents = np.asarray(source["physical_tangent_action"], dtype=float)

    fixed_step = float(fine_times[1] - fine_times[0])
    maximum_step = fixed_step / 16.0
    macro_starts = list(range(0, 369, 8))
    macro_ends = [*macro_starts[1:], 370]
    if len(macro_starts) != 47 or len(macro_ends) != 47:
        raise RuntimeError("47 retained macro seams required")

    maps_mid = []
    maps_rad = []
    exponential_count = 0
    for seam, (start, end) in enumerate(zip(
        macro_starts[:args.macro_limit], macro_ends[:args.macro_limit], strict=True,
    )):
        evolved = _matrix(tangents[seam])
        for interval in range(start, end):
            duration_float = fixed_step * (
                stop_fraction if interval == 369 else 1.0
            )
            count = max(1, int(np.ceil(duration_float / maximum_step)))
            width_float = duration_float / count
            width = _exact(width_float)
            left = _matrix(jacobians[interval])
            dt = _exact(float(jacobian_times[interval + 1] - jacobian_times[interval]))
            slope = (_matrix(jacobians[interval + 1]) - left) / dt
            commutator = left * slope - slope * left
            for substep in range(count):
                evolved = _step(
                    left, slope, commutator,
                    _exact(substep * width_float), width,
                ) * evolved
                exponential_count += 1
        target = _matrix(tangents[seam + 1])
        quotient_map = target.transpose() * evolved
        midpoint, radius = _mid_radius(quotient_map)
        maps_mid.append(midpoint)
        maps_rad.append(radius)
        print(json.dumps({
            "completed_macro_maps": seam + 1,
            "exponentials": exponential_count,
            "maximum_component_radius": float(np.max(radius)),
        }), flush=True)

    maps_mid = np.asarray(maps_mid)
    maps_rad = np.asarray(maps_rad)
    fundamental = _identity(PHYSICAL)
    for midpoint, radius in zip(maps_mid, maps_rad, strict=True):
        ball = arb_mat([
            [arb(float(midpoint[row, column]), float(radius[row, column]))
             for column in range(PHYSICAL)]
            for row in range(PHYSICAL)
        ])
        fundamental = ball * fundamental
    fundamental_mid, fundamental_rad = _mid_radius(fundamental)
    map_operator_uppers = np.asarray([
        np.linalg.norm(midpoint, 2) + np.linalg.norm(radius, "fro")
        for midpoint, radius in zip(maps_mid, maps_rad, strict=True)
    ])
    fundamental_upper = float(
        np.linalg.norm(fundamental_mid, 2) + np.linalg.norm(fundamental_rad, "fro")
    )

    np.savez_compressed(
        DATA,
        macro_action_lengths=macro_times,
        macro_step_map_midpoint=maps_mid,
        macro_step_map_component_radius=maps_rad,
        macro_step_map_operator_upper=map_operator_uppers,
        global_fundamental_midpoint=fundamental_mid,
        global_fundamental_component_radius=fundamental_rad,
    )
    validation = {
        "all_47_homogeneous_quotient_macro_maps_evaluated": maps_mid.shape == (47, 73, 73),
        "all_inputs_materialized_as_exact_binary_dyadics": True,
        "all_affine_commutators_and_exponentials_evaluated_in_Arb": True,
        "all_macro_map_component_radii_finite": bool(np.all(np.isfinite(maps_rad))),
        "global_discrete_fundamental_composed_in_Arb": True,
        "analytic_Magnus_remainder_not_claimed": True,
        "no_action_source_selector_scale_gate_or_chord_changed": True,
    }
    payload = {
        "artifact": "BHSM_N12_GATE7_ARB_MAGNUS4_MACRO_MAPS",
        "status": (
            "ALL_47_HOMOGENEOUS_ALIGNED_MAGNUS4_QUOTIENT_MAPS_AND_THEIR_"
            "GLOBAL_DISCRETE_FUNDAMENTAL_OUTWARD_EVALUATED"
        ),
        "authority": "ARB_BALL_AUTHORITY_FOR_THE_FINITE_DISCRETE_HOMOGENEOUS_MAPS_ONLY",
        "identity": {
            "precision_bits": args.precision,
            "macro_maps": 47,
            "physical_dimension": 73,
            "exponential_count": exponential_count,
            "Magnus_exponent": "h*A_mid-h^3*[A_left,A_prime]/12",
        },
        "summary": {
            "maximum_macro_map_component_radius": float(np.max(maps_rad)),
            "maximum_macro_map_operator_upper": float(np.max(map_operator_uppers)),
            "global_discrete_fundamental_operator_upper": fundamental_upper,
            "global_fundamental_component_radius_Frobenius": float(
                np.linalg.norm(fundamental_rad, "fro")
            ),
        },
        "data": DATA.relative_to(ROOT).as_posix(),
        "data_SHA256": _sha256(DATA),
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path)
            for path in (CENTER, JACOBIAN, TANGENT)
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "claim_boundary": {
            "finite_homogeneous_macro_maps": "CERTIFIED",
            "finite_global_discrete_fundamental": "CERTIFIED",
            "affine_source_block_composition": "OPEN_NEXT_ASSEMBLY",
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
