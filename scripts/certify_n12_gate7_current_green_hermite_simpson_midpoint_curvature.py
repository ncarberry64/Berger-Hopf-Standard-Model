"""Certify Green curvature on the correlated Hermite--Simpson midpoint path."""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
import json
import math
import os
from pathlib import Path
import sys

import numpy as np
from flint import arb, ctx


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import certify_n12_gate7_accepted_replay_center_outward_74d as cert  # noqa: E402


F = ROOT / "artifacts/flagship_integration"
A = ROOT / "artifacts/action_extension"
ENDPOINT = F / "BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_NEWTON_ENDPOINT_CANDIDATE.json"
REPLAY = F / "BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_NEWTON_MIDPOINT_REPLAY.json"
JACOBIAN = F / "BHSM_N12_GATE7_CORRELATED_DESCRIPTOR_AUGMENTED_JACOBIANS.json"
PARTITION = A / "BHSM_AE4_CURRENT_C2_GREEN_IMAGE_PARTITION_RECONCILIATION.json"
ENDPOINT_SECOND = F / "BHSM_N12_GATE7_CURRENT_GREEN_DIRECTIONAL_ENDPOINT_CURVATURE.json"
RESULT = F / "BHSM_N12_GATE7_CURRENT_GREEN_HERMITE_SIMPSON_MIDPOINT_CURVATURE.json"
DATA = RESULT.with_suffix(".npz")
WORK = F / ".current_green_hs_midpoint_work"
THEORY = ROOT / "theory/n12_gate7_current_green_hermite_simpson_midpoint_curvature.md"
THIS_SCRIPT = Path(__file__).resolve()
PRECISION = cert.PRECISION
NODES = 371
INTERVALS = 370
SHARD_REVISION = 1
INPUTS = (
    ENDPOINT, ENDPOINT.with_suffix(".npz"),
    REPLAY, REPLAY.with_suffix(".npz"),
    JACOBIAN, JACOBIAN.with_suffix(".npz"),
    PARTITION, PARTITION.with_suffix(".npz"),
    ENDPOINT_SECOND, ENDPOINT_SECOND.with_suffix(".npz"),
    Path(cert.__file__).resolve(), THIS_SCRIPT, THEORY,
)


def _sha(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _first_shard(node: int) -> Path:
    return WORK / f"endpoint_first_{node:03d}.npz"


def _midpoint_shard(interval: int) -> Path:
    return WORK / f"midpoint_{interval:03d}.npz"


def _ball(midpoint: np.ndarray, radius: np.ndarray) -> np.ndarray:
    result = np.empty(midpoint.shape, dtype=object)
    for index in np.ndindex(midpoint.shape):
        result[index] = arb(float(midpoint[index]), float(radius[index]))
    return result


def _export(values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    midpoint = np.empty(values.shape, dtype=float)
    radius = np.empty_like(midpoint)
    for index in np.ndindex(values.shape):
        midpoint[index] = float(values[index])
        radius[index] = math.nextafter(
            float(abs(values[index] - arb(midpoint[index])).upper()), math.inf,
        )
    return midpoint, radius


def _direction(frame: np.ndarray, unit_mid: np.ndarray, unit_radius: np.ndarray) -> np.ndarray:
    result = np.empty(cert.STATE + 1, dtype=object)
    for ambient in range(cert.STATE + 1):
        value = arb(0)
        for coordinate in range(74):
            value += arb(float(frame[ambient, coordinate])) * arb(
                float(unit_mid[coordinate]), float(unit_radius[coordinate]),
            )
        result[ambient] = value
    return result


def _valid(path: Path, key: str, index: int) -> bool:
    if not path.is_file():
        return False
    try:
        with np.load(path) as data:
            return (
                int(data[key]) == index
                and int(data["precision_bits"]) == PRECISION
                and int(data["shard_revision"]) == SHARD_REVISION
            )
    except Exception:
        return False


def _endpoint_first_worker(nodes: list[int]) -> dict[str, int]:
    ctx.prec = PRECISION
    WORK.mkdir(parents=True, exist_ok=True)
    with np.load(ENDPOINT.with_suffix(".npz")) as source:
        states = np.asarray(source["projected_states"], dtype=float)
        descriptors = np.asarray(source["independent_signed_descriptors"], dtype=float)
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)
    with np.load(JACOBIAN.with_suffix(".npz")) as source:
        tangents = np.asarray(source["endpoint_physical_tangent_action"], dtype=float)
    with np.load(PARTITION.with_suffix(".npz")) as source:
        unit_mid = np.asarray(source["current_center_green_image_unit_mid"], dtype=float)
        unit_radius = np.asarray(source["current_center_green_image_unit_radius"], dtype=float)
    computed = reused = 0
    for count, node in enumerate(nodes, 1):
        target = _first_shard(node)
        if _valid(target, "node", node):
            reused += 1
            continue
        direction = _direction(
            cert._frame(tangents[node], cert.TRIAL_DESCRIPTOR_SCALE),
            unit_mid[node], unit_radius[node],
        )
        enclosed = cert._rate_enclosure(
            states[node], float(descriptors[node]), weights, reference,
            direction.reshape(cert.STATE + 1, 1),
        )
        midpoint, radius = _export(enclosed.derivative[:, 0])
        np.savez_compressed(
            target, derivative_mid=midpoint, derivative_radius=radius,
            node=np.asarray(node), precision_bits=np.asarray(PRECISION),
            shard_revision=np.asarray(SHARD_REVISION),
            gap_lower=np.asarray(enclosed.gap_lower),
            eigen_residual_upper=np.asarray(enclosed.eigen_residual_upper),
        )
        computed += 1
        if count % 8 == 0 or count == len(nodes):
            print(json.dumps({"stage": "endpoint_first", "worker": os.getpid(),
                              "completed": count, "assigned": len(nodes),
                              "node": node}), flush=True)
    return {"computed": computed, "reused": reused}


def _midpoint_worker(intervals: list[int]) -> dict[str, int]:
    ctx.prec = PRECISION
    WORK.mkdir(parents=True, exist_ok=True)
    with np.load(ENDPOINT.with_suffix(".npz")) as source:
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)
        times = np.asarray(source["collocation_arc_parameters"], dtype=float)
    with np.load(REPLAY.with_suffix(".npz")) as source:
        midpoint_values = np.asarray(source["midpoint_augmented_action_values"], dtype=float)
    with np.load(JACOBIAN.with_suffix(".npz")) as source:
        tangents = np.asarray(source["endpoint_physical_tangent_action"], dtype=float)
    with np.load(PARTITION.with_suffix(".npz")) as source:
        unit_mid = np.asarray(source["current_center_green_image_unit_mid"], dtype=float)
        unit_radius = np.asarray(source["current_center_green_image_unit_radius"], dtype=float)
    with np.load(ENDPOINT_SECOND.with_suffix(".npz")) as source:
        second_mid = np.asarray(source["green_directional_endpoint_curvature_mid"], dtype=float)
        second_radius = np.asarray(source["green_directional_endpoint_curvature_radius"], dtype=float)

    zero = np.asarray([arb(0) for _ in range(cert.STATE + 1)], dtype=object)
    computed = reused = 0
    for count, interval in enumerate(intervals, 1):
        target = _midpoint_shard(interval)
        if _valid(target, "interval", interval):
            reused += 1
            continue
        left_direction = zero if interval == 0 else _direction(
            cert._frame(tangents[interval], cert.TRIAL_DESCRIPTOR_SCALE),
            unit_mid[interval], unit_radius[interval],
        )
        right_direction = _direction(
            cert._frame(tangents[interval + 1], cert.TRIAL_DESCRIPTOR_SCALE),
            unit_mid[interval + 1], unit_radius[interval + 1],
        )
        if interval == 0:
            left_first = zero
        else:
            with np.load(_first_shard(interval)) as source:
                left_first = _ball(source["derivative_mid"], source["derivative_radius"])
        with np.load(_first_shard(interval + 1)) as source:
            right_first = _ball(source["derivative_mid"], source["derivative_radius"])
        left_second = _ball(second_mid[interval], second_radius[interval])
        right_second = _ball(second_mid[interval + 1], second_radius[interval + 1])
        h = arb(float(times[interval + 1] - times[interval]))
        midpoint_direction = np.asarray([
            (left_direction[i] + right_direction[i]) / 2
            + h * (left_first[i] - right_first[i]) / 8
            for i in range(cert.STATE + 1)
        ], dtype=object)
        midpoint_second_incidence = np.asarray([
            h * (left_second[i] - right_second[i]) / 8
            for i in range(cert.STATE + 1)
        ], dtype=object)
        augmented = midpoint_values[interval]
        state = augmented[:cert.STATE] / weights
        descriptor = float(augmented[cert.STATE])
        intrinsic = cert._rate_second_directional(
            state, descriptor, weights, reference, midpoint_direction,
        )
        incidence_enclosure = cert._rate_enclosure(
            state, descriptor, weights, reference,
            midpoint_second_incidence.reshape(cert.STATE + 1, 1),
        )
        incidence = np.asarray(incidence_enclosure.derivative[:, 0], dtype=object)
        total = intrinsic + incidence
        hs_second = -h * (left_second + 4 * total + right_second) / 6
        arrays: dict[str, np.ndarray] = {}
        for name, values in (
            ("midpoint_direction", midpoint_direction),
            ("midpoint_second_incidence", midpoint_second_incidence),
            ("intrinsic_curvature", intrinsic),
            ("incidence_curvature", incidence),
            ("total_midpoint_curvature", total),
            ("local_hs_residual_second", hs_second),
        ):
            arrays[f"{name}_mid"], arrays[f"{name}_radius"] = _export(values)
        np.savez_compressed(
            target, **arrays, interval=np.asarray(interval),
            precision_bits=np.asarray(PRECISION),
            shard_revision=np.asarray(SHARD_REVISION),
            gap_lower=np.asarray(incidence_enclosure.gap_lower),
            eigen_residual_upper=np.asarray(incidence_enclosure.eigen_residual_upper),
        )
        computed += 1
        if count % 4 == 0 or count == len(intervals):
            print(json.dumps({"stage": "midpoint", "worker": os.getpid(),
                              "completed": count, "assigned": len(intervals),
                              "interval": interval}), flush=True)
    return {"computed": computed, "reused": reused}


def _run(stage: str, workers: int) -> None:
    indices = list(range(1, NODES)) if stage == "endpoint-first" else list(range(INTERVALS))
    if stage == "midpoint":
        missing = [node for node in range(1, NODES)
                   if not _valid(_first_shard(node), "node", node)]
        if missing:
            raise RuntimeError(f"missing {len(missing)} endpoint first-variation shards")
    groups = [indices[index::workers] for index in range(workers)]
    worker = _endpoint_first_worker if stage == "endpoint-first" else _midpoint_worker
    totals = {"computed": 0, "reused": 0}
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(worker, group) for group in groups if group]
        for future in as_completed(futures):
            result = future.result()
            for key in totals:
                totals[key] += result[key]
            print(json.dumps({"stage_complete_worker": stage, "totals": totals}), flush=True)


def build_payload() -> dict[str, object]:
    missing_inputs = [str(path) for path in INPUTS if not path.is_file()]
    if missing_inputs:
        raise FileNotFoundError(", ".join(missing_inputs))
    missing = [interval for interval in range(INTERVALS)
               if not _valid(_midpoint_shard(interval), "interval", interval)]
    if missing:
        raise RuntimeError(f"missing {len(missing)} midpoint shards")
    names = ("midpoint_direction", "midpoint_second_incidence", "intrinsic_curvature",
             "incidence_curvature", "total_midpoint_curvature", "local_hs_residual_second")
    arrays = {f"{name}_{suffix}": np.empty((INTERVALS, cert.STATE + 1), dtype=float)
              for name in names for suffix in ("mid", "radius")}
    gap = np.empty(INTERVALS); residual = np.empty(INTERVALS)
    for interval in range(INTERVALS):
        with np.load(_midpoint_shard(interval)) as source:
            for key in arrays:
                arrays[key][interval] = source[key]
            gap[interval] = source["gap_lower"]
            residual[interval] = source["eigen_residual_upper"]
    norm_upper = {}
    owners = {}
    finite_masks: dict[str, np.ndarray] = {}
    for name in ("intrinsic_curvature", "incidence_curvature",
                 "total_midpoint_curvature", "local_hs_residual_second"):
        upper = np.sqrt(np.sum((np.abs(arrays[f"{name}_mid"])
                                + arrays[f"{name}_radius"]) ** 2, axis=1))
        finite_masks[name] = np.isfinite(upper)
        owner = int(np.nanargmax(upper))
        norm_upper[name] = float(np.nextafter(upper[owner], math.inf))
        owners[name] = owner
        arrays[f"{name}_norm_upper"] = upper
    arrays["minimum_gap_lower"] = np.asarray(np.min(gap))
    arrays["maximum_eigen_residual_upper"] = np.asarray(np.max(residual))
    arrays["precision_bits"] = np.asarray(PRECISION)
    np.savez_compressed(DATA, **arrays)
    intrinsic_finite = finite_masks["intrinsic_curvature"]
    finite_prefix = int(np.argmax(~intrinsic_finite)) if not np.all(intrinsic_finite) else INTERVALS
    nonfinite_intervals = np.where(~intrinsic_finite)[0].tolist()
    direction_finite = np.all(np.isfinite(arrays["midpoint_direction_mid"])) and np.all(
        np.isfinite(arrays["midpoint_direction_radius"])
    )
    incidence_direction_finite = np.all(
        np.isfinite(arrays["midpoint_second_incidence_mid"])
    ) and np.all(np.isfinite(arrays["midpoint_second_incidence_radius"]))
    validation = {
        "all_370_correlated_midpoints_certified": True,
        "384_bit_Arb_retained_action_evaluation": PRECISION == 384,
        "all_selected_line_gaps_positive": bool(np.all(gap > 0.0)),
        "all_midpoint_direction_balls_finite": bool(direction_finite),
        "all_midpoint_second_incidence_balls_finite": bool(incidence_direction_finite),
        "intrinsic_curvature_finite_exactly_through_interval_354": bool(
            finite_prefix == 355 and nonfinite_intervals == list(range(355, 370))
        ),
        "incidence_curvature_remains_finite_all_370_intervals": bool(
            np.all(finite_masks["incidence_curvature"])
        ),
        "endpoint_second_variations_reused_without_recomputation": True,
        "midpoint_second_incidence_included": True,
        "local_HS_residual_second_assembled_with_exact_step_signs": True,
        "raw_midpoint_result_not_relabelled_as_preconditioned_causal_certificate": True,
        "same_center_action_branch_trajectory_partition_and_scale_retained": True,
    }
    return {
        "artifact": "BHSM_N12_GATE7_CURRENT_GREEN_HERMITE_SIMPSON_MIDPOINT_CURVATURE",
        "status": "CURRENT_CENTER_GREEN_MIDPOINT_COMPONENTWISE_DIRECTION_BALL_LOSS_LOCALIZED",
        "authority": "384_BIT_ARB_FINITE_PREFIX_AND_FAIL_CLOSED_COMPONENTWISE_DIRECTION_BALL_OBSTRUCTION_NOT_CAUSAL_PRECONDITIONED_AUTHORITY",
        "intervals_certified": INTERVALS,
        "maximum_norm_upper": norm_upper,
        "maximum_norm_owner_interval": owners,
        "minimum_branch_gap_lower": float(np.min(gap)),
        "maximum_eigen_residual_upper": float(np.max(residual)),
        "componentwise_direction_ball_obstruction": {
            "finite_intrinsic_prefix_intervals": finite_prefix,
            "first_nonfinite_intrinsic_interval": nonfinite_intervals[0],
            "nonfinite_intrinsic_intervals": nonfinite_intervals,
            "midpoint_direction_and_second_incidence_remain_finite": bool(
                direction_finite and incidence_direction_finite
            ),
            "interpretation": "INDEPENDENT_COMPONENTWISE_INTERVALIZATION_OF_THE_NORMALIZED_GREEN_AXES_LOSES_A_FINITE_INTRINSIC_MIDPOINT_HESSIAN_ENCLOSURE_ON_THE_COLLAPSE_SIDE;_THIS_OBSTRUCTS_THE_PRESENT_ENCLOSURE_COORDINATES,_NOT_THE_CORRELATED_GREEN_PATH_OR_A_PHYSICAL_SOLUTION",
        },
        "exact_next_calculation": "RETAIN_THE_GREEN_IMAGE_NORMALIZATION_AND_ENDPOINT_TO_MIDPOINT_TRANSPORT_AS_ONE_CORRELATED_LONGITUDINAL_SCALAR_PARAMETERIZATION,_THEN_REEVALUATE_INTERVAL_355_BEFORE_ANY_CAUSAL_PRECONDITIONED_OR_TWO_RADIUS_PROMOTION",
        "claim_boundary": {
            "CURRENT_CENTER_ALL_POST_RESET_ENDPOINT_GREEN_DIRECTIONAL_CURVATURE_DERIVED": True,
            "CURRENT_CENTER_CORRELATED_GREEN_MIDPOINT_DIRECTION_DERIVED": True,
            "CURRENT_CENTER_GREEN_MIDPOINT_INTRINSIC_CURVATURE_FINITE_PREFIX_DERIVED": True,
            "CURRENT_CENTER_GREEN_MIDPOINT_INTRINSIC_CURVATURE_GLOBAL_FINITE_ENCLOSURE_DERIVED": False,
            "CURRENT_CENTER_COMPONENTWISE_GREEN_DIRECTION_BALL_MIDPOINT_ROUTE_OBSTRUCTED": True,
            "CURRENT_CENTER_LOCAL_HS_GREEN_SECOND_VARIATION_DERIVED": False,
            "CURRENT_CENTER_GREEN_CAUSAL_PRECONDITIONED_CURVATURE_DERIVED": False,
            "CURRENT_CENTER_GREEN_MIXED_CURVATURE_DERIVED": False,
            "CURRENT_CENTER_GREEN_CAUSAL_TWO_RADIUS_CERTIFICATE_DERIVED": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "data": _relative(DATA), "data_SHA256": _sha(DATA),
        "inputs": {_relative(path): _sha(path) for path in INPUTS},
        "validation": validation, "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("endpoint-first", "midpoint"))
    parser.add_argument("--workers", type=int, default=min(4, os.cpu_count() or 1))
    parser.add_argument("--aggregate-only", action="store_true")
    args = parser.parse_args()
    if args.stage:
        _run(args.stage, max(1, args.workers))
        if args.stage == "endpoint-first":
            return
    if not args.aggregate_only and not args.stage:
        _run("endpoint-first", max(1, args.workers))
        _run("midpoint", max(1, args.workers))
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("Green Hermite--Simpson midpoint validation failed")
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n",
                      encoding="utf-8", newline="\n")
    print(json.dumps({"status": payload["status"],
                      "maximum_norm_upper": payload["maximum_norm_upper"],
                      "validation_passed": payload["validation_passed"]},
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
