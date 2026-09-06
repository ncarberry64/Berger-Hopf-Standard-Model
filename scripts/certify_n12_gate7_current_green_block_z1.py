"""Resolve the certified frozen linear defect in the current Green split.

The accepted 74-dimensional outward contraction already certified the exact
Arb linear shards and their causal block-row norm.  This script reuses the
exported interval matrices from that certified campaign and resolves the same
rows into longitudinal/transverse blocks for the current Green-image
partition.  It performs no action evaluation and changes no proof datum.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np
from flint import arb_mat, ctx


sys.path.insert(0, str(Path(__file__).resolve().parent))
import certify_n12_gate7_accepted_replay_center_outward_74d as cert  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
F = ROOT / "artifacts/flagship_integration"
A = ROOT / "artifacts/action_extension"
PARENT = F / "BHSM_N12_GATE7_ACCEPTED_REPLAY_CENTER_OUTWARD_74D_CONTRACTION.json"
ACTION_SCREEN = F / "BHSM_N12_GATE7_ACCEPTED_REPLAY_ACTION_BLOCK_SCREEN.json"
PARTITION = A / "BHSM_AE4_CURRENT_C2_GREEN_IMAGE_PARTITION_RECONCILIATION.json"
RESULT = F / "BHSM_N12_GATE7_CURRENT_GREEN_BLOCK_Z1.json"
DATA = RESULT.with_suffix(".npz")
THEORY = ROOT / "theory/n12_gate7_current_green_block_z1.md"
THIS_SCRIPT = Path(__file__).resolve()
DEFAULT_CACHE = F / ".accepted_replay_outward_74d_work"
DIMENSION = 74
INTERVALS = 370
PRECISION = 384


def _sha(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _aggregate_sha(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in paths:
        digest.update(path.name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(bytes.fromhex(_sha(path)))
    return digest.hexdigest().upper()


def _positive_dot_upper(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    inner = left.shape[1]
    gamma = inner * np.finfo(float).eps / (1.0 - inner * np.finfo(float).eps)
    value = left @ right
    return np.nextafter(value / (1.0 - gamma), math.inf)


def _ball_matmul(
    left_mid: np.ndarray,
    left_rad: np.ndarray,
    right_mid: np.ndarray,
    right_rad: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Directed binary64 enclosure of an interval matrix product."""
    inner = left_mid.shape[1]
    eps = np.finfo(float).eps
    gamma = inner * eps / (1.0 - inner * eps)
    midpoint = left_mid @ right_mid
    absolute_center = _positive_dot_upper(abs(left_mid), abs(right_mid))
    center_roundoff = np.nextafter(gamma * absolute_center, math.inf)
    cross = _positive_dot_upper(abs(left_mid), right_rad)
    cross = np.nextafter(
        cross + _positive_dot_upper(left_rad, abs(right_mid)), math.inf,
    )
    cross = np.nextafter(
        cross + _positive_dot_upper(left_rad, right_rad), math.inf,
    )
    return midpoint, np.nextafter(cross + center_roundoff, math.inf)


def _ball_add(
    left_mid: np.ndarray,
    left_rad: np.ndarray,
    right_mid: np.ndarray,
    right_rad: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    midpoint = left_mid + right_mid
    rounding = np.finfo(float).eps * (abs(left_mid) + abs(right_mid))
    return midpoint, np.nextafter(left_rad + right_rad + rounding, math.inf)


def _sum_squares_upper(values: np.ndarray) -> float:
    flat = np.asarray(values, dtype=float).ravel()
    count = max(1, flat.size)
    gamma = (2 * count) * np.finfo(float).eps / (
        1.0 - (2 * count) * np.finfo(float).eps
    )
    squared = flat * flat
    total = float(np.sum(squared))
    return math.nextafter(total / (1.0 - gamma), math.inf)


def _norm_upper(midpoint: np.ndarray, radius: np.ndarray) -> float:
    center = math.sqrt(_sum_squares_upper(midpoint))
    error = math.sqrt(_sum_squares_upper(radius))
    return math.nextafter(center + error, math.inf)


def _ball_projected_bounds(
    midpoint: np.ndarray,
    radius: np.ndarray,
    output_axis: np.ndarray,
    input_axis: np.ndarray,
) -> tuple[float, float, float]:
    """Return LL, LT, TL bounds for one causal source block.

    The fixed normalized binary axes are the exact partition used by the
    certified central and mixed campaigns.  Component balls are retained for
    the causal block itself.
    """
    zero_column = np.zeros((DIMENSION, 1))
    right_mid, right_rad = _ball_matmul(
        midpoint, radius, input_axis[:, None], zero_column,
    )
    left_mid, left_rad = _ball_matmul(
        output_axis[None, :], zero_column.T, midpoint, radius,
    )
    ll_mid_array, ll_rad_array = _ball_matmul(
        output_axis[None, :], zero_column.T, right_mid, right_rad,
    )
    ll_mid = float(ll_mid_array[0, 0])
    ll_rad = float(ll_rad_array[0, 0])
    ll_upper = math.nextafter(abs(ll_mid) + ll_rad, math.inf)

    longitudinal_output_mid = output_axis[:, None] * ll_mid
    longitudinal_output_rad = np.nextafter(
        abs(output_axis[:, None]) * ll_rad
        + np.finfo(float).eps * abs(longitudinal_output_mid),
        math.inf,
    )
    tl_mid, tl_rad = _ball_add(
        right_mid, right_rad, -longitudinal_output_mid,
        longitudinal_output_rad,
    )

    longitudinal_input_mid = ll_mid * input_axis[None, :]
    longitudinal_input_rad = np.nextafter(
        ll_rad * abs(input_axis[None, :])
        + np.finfo(float).eps * abs(longitudinal_input_mid),
        math.inf,
    )
    lt_mid, lt_rad = _ball_add(
        left_mid, left_rad, -longitudinal_input_mid,
        longitudinal_input_rad,
    )
    return (
        ll_upper,
        _norm_upper(lt_mid, lt_rad),
        _norm_upper(tl_mid, tl_rad),
    )


def build_payload(cache: Path) -> dict[str, object]:
    linear_path = cache / "linear_composition.npz"
    z1_path = cache / "z1_composition.npz"
    raw_linear_paths = [cache / f"linear_{index:03d}.npz"
                        for index in range(INTERVALS)]
    required = (PARENT, PARENT.with_suffix(".npz"), ACTION_SCREEN,
                ACTION_SCREEN.with_suffix(".npz"), PARTITION,
                PARTITION.with_suffix(".npz"), THEORY, THIS_SCRIPT,
                linear_path, z1_path)
    missing = [str(path) for path in (*required, *raw_linear_paths)
               if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))

    parent = json.loads(PARENT.read_text(encoding="utf-8"))
    action_screen = json.loads(ACTION_SCREEN.read_text(encoding="utf-8"))
    partition = json.loads(PARTITION.read_text(encoding="utf-8"))
    expected_z1_hash = parent["derived_work_aggregate_SHA256"][
        "outward_Z1_composition"
    ]
    if _sha(z1_path) != expected_z1_hash:
        raise RuntimeError("cached Z1 composition does not match certified parent")
    expected_linear_aggregate = parent["derived_work_aggregate_SHA256"][
        "370_outward_linear_preconditioned_shards"
    ]
    if _aggregate_sha(raw_linear_paths) != expected_linear_aggregate:
        raise RuntimeError("cached linear shards do not match certified parent")

    with np.load(linear_path) as source:
        c_mid = np.asarray(source["C_mid"], dtype=float)
        c_rad = np.asarray(source["C_rad"], dtype=float)
        dl_mid = np.asarray(source["DL_mid"], dtype=float)
        dl_rad = np.asarray(source["DL_rad"], dtype=float)
        dr_mid = np.asarray(source["DR_mid"], dtype=float)
        dr_rad = np.asarray(source["DR_rad"], dtype=float)
        cached_y = float(source["outward_Y_causal_74D_block_sup"])
        cached_gap = float(source["minimum_branch_gap_lower"])
    with np.load(z1_path) as source:
        certified_full_rows = np.asarray(source["row_upper"], dtype=float)
    with np.load(PARTITION.with_suffix(".npz")) as source:
        axis_mid = np.asarray(
            source["current_center_green_image_unit_mid"], dtype=float,
        )
    axes = np.zeros_like(axis_mid)
    axes[1:] = axis_mid[1:] / np.linalg.norm(axis_mid[1:], axis=1)[:, None]

    expected_shape = (INTERVALS, DIMENSION, DIMENSION)
    arrays = (c_mid, c_rad, dl_mid, dl_rad, dr_mid, dr_rad)
    if any(array.shape != expected_shape for array in arrays):
        raise RuntimeError("cached linear composition changed shape")
    if certified_full_rows.shape != (INTERVALS,):
        raise RuntimeError("certified Z1 row profile changed shape")

    rows = np.zeros((INTERVALS + 1, 4))
    ctx.prec = PRECISION
    # Only the longitudinal-input columns must be carried explicitly.  The
    # two transverse-input blocks safely inherit the certified full row norm.
    # This reduces the exact recurrence width by a factor of 74 without
    # changing the causal matrices or introducing a sampled direction.
    longitudinal_columns = arb_mat(DIMENSION, 0)
    for interval in range(INTERVALS):
        with np.load(raw_linear_paths[interval]) as source:
            if int(source["precision_bits"]) != PRECISION:
                raise RuntimeError("cached linear shard precision changed")
            c_value = cert._arb_mat_from_array(
                cert._parse_arb_string_array(source["C_arb"])
            )
            dl_value = cert._arb_mat_from_array(
                cert._parse_arb_string_array(source["DL_arb"])
            )
            dr_value = cert._arb_mat_from_array(
                cert._parse_arb_string_array(source["DR_arb"])
            )
        longitudinal_columns = -c_value * longitudinal_columns
        if interval > 0:
            addition = dl_value * cert._arb_matrix(axes[interval][:, None])
            for i in range(DIMENSION):
                longitudinal_columns[i, longitudinal_columns.ncols() - 1] += (
                    addition[i, 0]
                )
        appended = dr_value * cert._arb_matrix(axes[interval + 1][:, None])
        extended = arb_mat(DIMENSION, longitudinal_columns.ncols() + 1)
        for i in range(DIMENSION):
            for j in range(longitudinal_columns.ncols()):
                extended[i, j] = longitudinal_columns[i, j]
            extended[i, longitudinal_columns.ncols()] = appended[i, 0]
        longitudinal_columns = extended

        output_axis = cert._arb_matrix(axes[interval + 1][None, :])
        longitudinal_output = output_axis * longitudinal_columns
        transverse_output = (
            longitudinal_columns - output_axis.transpose() * longitudinal_output
        )
        ll_mid, ll_rad = cert._matrix_export(longitudinal_output)
        tl_mid, tl_rad = cert._matrix_export(transverse_output)
        ll_sum = 0.0
        tl_sum = 0.0
        for source in range(interval + 1):
            ll_sum = math.nextafter(
                ll_sum + abs(float(ll_mid[0, source]))
                + float(ll_rad[0, source]), math.inf,
            )
            tl_sum = math.nextafter(
                tl_sum + _norm_upper(
                    tl_mid[:, source], tl_rad[:, source],
                ), math.inf,
            )
        rows[interval + 1, 0] = ll_sum
        rows[interval + 1, 2] = tl_sum
        # Orthogonal projections have operator norm one.  The already
        # certified full causal row therefore directly bounds both blocks
        # whose input is transverse.
        rows[interval + 1, 1] = certified_full_rows[interval]
        rows[interval + 1, 3] = certified_full_rows[interval]

    labels = np.asarray(("L_FROM_L", "L_FROM_T", "T_FROM_L", "T_FROM_T"))
    maxima = np.max(rows, axis=0)
    owners = np.argmax(rows, axis=0)
    parent_z1 = float(parent["outward_operands"]["Z1_upper"])
    tolerance = math.nextafter(parent_z1, math.inf)
    validation = {
        "certified_parent_linear_shard_aggregate_retained": bool(
            _aggregate_sha(raw_linear_paths) == expected_linear_aggregate
        ),
        "cached_Z1_composition_hash_matches_certified_parent": (
            _sha(z1_path) == expected_z1_hash
        ),
        "cached_outward_Y_matches_certified_parent": (
            float(parent["outward_operands"]["Y_lower"]) <= cached_y
            <= float(parent["outward_operands"]["Y_upper"])
        ),
        "cached_minimum_gap_matches_certified_parent": (
            cached_gap == float(action_screen["minimum_branch_gap_lower"])
        ),
        "same_current_Green_partition_retained": (
            partition["validation"]["current_371_node_causal_green_image_used"]
            and axes.shape == (INTERVALS + 1, DIMENSION)
        ),
        "all_post_reset_partition_axes_normalized": bool(
            np.max(abs(np.linalg.norm(axes[1:], axis=1) - 1.0)) < 2.0e-15
        ),
        "all_block_bounds_finite_nonnegative": bool(
            np.all(np.isfinite(rows)) and np.all(rows >= 0.0)
        ),
        "each_resolved_block_is_bounded_by_full_certified_Z1": bool(
            np.all(maxima <= tolerance)
        ),
        "transverse_transverse_uses_parent_full_row_contraction": bool(
            np.array_equal(rows[1:, 3], certified_full_rows)
        ),
        "no_action_center_branch_scale_partition_or_fit_changed": True,
        "two_radius_nonlinear_certificate_not_claimed": True,
        "FULL_BHSM_COMPLETE": False,
    }
    passed = all(
        value for key, value in validation.items()
        if key != "FULL_BHSM_COMPLETE"
    ) and not validation["FULL_BHSM_COMPLETE"]
    if not passed:
        failed = [key for key, value in validation.items()
                  if key != "FULL_BHSM_COMPLETE" and not value]
        raise RuntimeError(
            f"block Z1 validation failed: {failed}; maxima={maxima.tolist()}; "
            f"parent={parent_z1}"
        )

    np.savez_compressed(
        DATA,
        block_labels=labels,
        causal_block_Z1_upper_by_node=rows,
        causal_block_Z1_maximum_upper=maxima,
        causal_block_Z1_owner_node=owners,
        certified_full_Z1_row_upper=np.concatenate(([0.0], certified_full_rows)),
        linear_composition_cache_SHA256=np.asarray(_sha(linear_path)),
        z1_composition_SHA256=np.asarray(_sha(z1_path)),
    )
    inputs = {
        _relative(path): _sha(path) for path in required[:8]
    }
    return {
        "artifact": "BHSM_N12_GATE7_CURRENT_GREEN_BLOCK_Z1",
        "status": "CURRENT_GREEN_LONGITUDINAL_TRANSVERSE_FROZEN_LINEAR_DEFECT_CERTIFIED",
        "authority": "DIRECTED_INTERVAL_RECOMPOSITION_OF_CERTIFIED_ARB_LINEAR_SHARDS_IN_THE_FIXED_CURRENT_GREEN_PARTITION",
        "block_order": labels.tolist(),
        "maximum_block_Z1_upper": {
            label: float(value) for label, value in zip(labels, maxima, strict=True)
        },
        "maximum_block_Z1_owner_node": {
            label: int(value) for label, value in zip(labels, owners, strict=True)
        },
        "certified_parent_full_Z1_upper": parent_z1,
        "cache_attestation": {
            "linear_composition_SHA256": _sha(linear_path),
            "z1_composition_SHA256": _sha(z1_path),
            "certified_370_linear_shards_aggregate_SHA256": parent[
                "derived_work_aggregate_SHA256"
            ]["370_outward_linear_preconditioned_shards"],
            "linear_shards_reverified_at_runtime": True,
        },
        "data": _relative(DATA),
        "data_SHA256": _sha(DATA),
        "exact_next_calculation": "COMPOSE_THE_FULL_TRANSVERSE_HERMITE_SIMPSON_CENTER_MAJORANT_THROUGH_THE_SAME_FROZEN_CAUSAL_PRECONDITIONER_AND_ATTACH_ITS_OUTWARD_AXIS_NEIGHBORHOOD_REMAINDER_THEN_TEST_THE_TWO_RADIUS_POLYNOMIAL",
        "claim_boundary": {
            "CURRENT_GREEN_LONGITUDINAL_TRANSVERSE_BLOCK_Z1_DERIVED": True,
            "CURRENT_GREEN_TRANSVERSE_TRANSVERSE_FULL_OPERATOR_BOUND_DERIVED": False,
            "CURRENT_CENTER_GREEN_CAUSAL_TWO_RADIUS_CERTIFICATE_DERIVED": False,
            "G7_ROOT_NONEXISTENCE_DERIVED": False,
            "G7_PHYSICAL_SPACETIME_INSTABILITY_DERIVED": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": inputs,
        "validation": validation,
        "validation_passed": passed,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--linear-cache", type=Path, default=DEFAULT_CACHE)
    args = parser.parse_args()
    payload = build_payload(args.linear_cache.resolve())
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "maximum_block_Z1_upper": payload["maximum_block_Z1_upper"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
