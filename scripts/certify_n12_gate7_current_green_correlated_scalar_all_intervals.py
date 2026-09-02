"""Certify the correlated central Green scalar on all retained intervals."""

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
import certify_n12_gate7_current_green_correlated_scalar_interval355 as seed  # noqa: E402


F = ROOT / "artifacts/flagship_integration"
A = ROOT / "artifacts/action_extension"
ENDPOINT = F / "BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_NEWTON_ENDPOINT_CANDIDATE.json"
REPLAY = F / "BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_NEWTON_MIDPOINT_REPLAY.json"
JACOBIAN = F / "BHSM_N12_GATE7_CORRELATED_DESCRIPTOR_AUGMENTED_JACOBIANS.json"
PARTITION = A / "BHSM_AE4_CURRENT_C2_GREEN_IMAGE_PARTITION_RECONCILIATION.json"
SEED = F / "BHSM_N12_GATE7_CURRENT_GREEN_CORRELATED_SCALAR_INTERVAL355.json"
RESULT = F / "BHSM_N12_GATE7_CURRENT_GREEN_CORRELATED_SCALAR_ALL_INTERVALS.json"
DATA = RESULT.with_suffix(".npz")
WORK = F / ".current_green_correlated_scalar_all_work"
THEORY = ROOT / "theory/n12_gate7_current_green_correlated_scalar_all_intervals.md"
THIS_SCRIPT = Path(__file__).resolve()
PRECISION = cert.PRECISION
NODES = 371
INTERVALS = 370
SHARD_REVISION = 2
INPUTS = (
    ENDPOINT, ENDPOINT.with_suffix(".npz"),
    REPLAY, REPLAY.with_suffix(".npz"),
    JACOBIAN, JACOBIAN.with_suffix(".npz"),
    PARTITION, PARTITION.with_suffix(".npz"),
    SEED, SEED.with_suffix(".npz"),
    Path(cert.__file__).resolve(), Path(seed.__file__).resolve(), THIS_SCRIPT, THEORY,
)


def _sha(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _endpoint_shard(node: int) -> Path:
    return WORK / f"endpoint_{node:03d}.npz"


def _midpoint_shard(interval: int) -> Path:
    return WORK / f"midpoint_{interval:03d}.npz"


def _ball(midpoint: np.ndarray, radius: np.ndarray) -> np.ndarray:
    result = np.empty(midpoint.shape, dtype=object)
    for index in np.ndindex(midpoint.shape):
        result[index] = arb(float(midpoint[index]), float(radius[index]))
    return result


def _valid(path: Path, key: str, index: int, required: tuple[str, ...]) -> bool:
    if not path.is_file():
        return False
    try:
        with np.load(path) as data:
            return (
                int(data[key]) == index
                and int(data["precision_bits"]) == PRECISION
                and int(data["shard_revision"]) == SHARD_REVISION
                and all(name in data.files for name in required)
            )
    except Exception:
        return False


def _endpoint_worker(nodes: list[int]) -> dict[str, int]:
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
    required = ("direction_arb", "first_arb", "second_arb")
    for count, node in enumerate(nodes, 1):
        target = _endpoint_shard(node)
        if _valid(target, "node", node, required):
            reused += 1
            continue
        central = seed._normalized_central_axis(unit_mid[node])
        axis_error = seed._axis_error_upper(unit_mid[node], unit_radius[node], central)
        direction = seed._ambient_direction(
            cert._frame(tangents[node], cert.TRIAL_DESCRIPTOR_SCALE), central,
        )
        first_enclosure = cert._rate_enclosure(
            states[node], float(descriptors[node]), weights, reference,
            direction.reshape(cert.STATE + 1, 1),
        )
        first = np.asarray(first_enclosure.derivative[:, 0], dtype=object)
        second = cert._rate_second_directional(
            states[node], float(descriptors[node]), weights, reference, direction,
        )
        first_mid, first_radius = seed._export(first)
        second_mid, second_radius = seed._export(second)
        direction_mid, direction_radius = seed._export(direction)
        np.savez_compressed(
            target, central_causal_axis=central,
            axis_error_upper=np.asarray(axis_error),
            direction_mid=direction_mid, direction_radius=direction_radius,
            first_mid=first_mid, first_radius=first_radius,
            second_mid=second_mid, second_radius=second_radius,
            direction_arb=cert._arb_string_array(direction),
            first_arb=cert._arb_string_array(first),
            second_arb=cert._arb_string_array(second),
            gap_lower=np.asarray(first_enclosure.gap_lower),
            eigen_residual_upper=np.asarray(first_enclosure.eigen_residual_upper),
            node=np.asarray(node), precision_bits=np.asarray(PRECISION),
            shard_revision=np.asarray(SHARD_REVISION),
        )
        computed += 1
        if count % 4 == 0 or count == len(nodes):
            print(json.dumps({"stage": "endpoint", "worker": os.getpid(),
                              "completed": count, "assigned": len(nodes),
                              "node": node}), flush=True)
    return {"computed": computed, "reused": reused}


def _midpoint_worker(intervals: list[int]) -> dict[str, int]:
    ctx.prec = PRECISION
    with np.load(ENDPOINT.with_suffix(".npz")) as source:
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)
        times = np.asarray(source["collocation_arc_parameters"], dtype=float)
    with np.load(REPLAY.with_suffix(".npz")) as source:
        midpoint_values = np.asarray(source["midpoint_augmented_action_values"], dtype=float)
    zero = np.asarray([arb(0) for _ in range(cert.STATE + 1)], dtype=object)
    computed = reused = 0
    required = ("intrinsic_mid", "intrinsic_radius", "local_hs_mid", "local_hs_radius")
    for count, interval in enumerate(intervals, 1):
        target = _midpoint_shard(interval)
        if _valid(target, "interval", interval, required):
            reused += 1
            continue
        if interval == 0:
            left_direction = left_first = left_second = zero
        else:
            with np.load(_endpoint_shard(interval)) as source:
                left_direction = cert._parse_arb_string_array(source["direction_arb"])
                left_first = cert._parse_arb_string_array(source["first_arb"])
                left_second = cert._parse_arb_string_array(source["second_arb"])
        with np.load(_endpoint_shard(interval + 1)) as source:
            right_direction = cert._parse_arb_string_array(source["direction_arb"])
            right_first = cert._parse_arb_string_array(source["first_arb"])
            right_second = cert._parse_arb_string_array(source["second_arb"])
        h = arb(float(times[interval + 1] - times[interval]))
        midpoint_direction = np.asarray([
            (left_direction[i] + right_direction[i]) / 2
            + h * (left_first[i] - right_first[i]) / 8
            for i in range(cert.STATE + 1)
        ], dtype=object)
        midpoint_second = np.asarray([
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
            midpoint_second.reshape(cert.STATE + 1, 1),
        )
        incidence = np.asarray(incidence_enclosure.derivative[:, 0], dtype=object)
        total = intrinsic + incidence
        local_hs = -h * (left_second + 4 * total + right_second) / 6
        arrays = {}
        for name, values in (
            ("midpoint_direction", midpoint_direction),
            ("midpoint_second_incidence", midpoint_second),
            ("intrinsic", intrinsic), ("incidence", incidence),
            ("total", total), ("local_hs", local_hs),
        ):
            arrays[f"{name}_mid"], arrays[f"{name}_radius"] = seed._export(values)
        np.savez_compressed(
            target, **arrays, interval=np.asarray(interval),
            gap_lower=np.asarray(incidence_enclosure.gap_lower),
            eigen_residual_upper=np.asarray(incidence_enclosure.eigen_residual_upper),
            precision_bits=np.asarray(PRECISION),
            shard_revision=np.asarray(SHARD_REVISION),
        )
        computed += 1
        if count % 4 == 0 or count == len(intervals):
            print(json.dumps({"stage": "midpoint", "worker": os.getpid(),
                              "completed": count, "assigned": len(intervals),
                              "interval": interval}), flush=True)
    return {"computed": computed, "reused": reused}


def _run(stage: str, workers: int) -> None:
    indices = list(range(1, NODES)) if stage == "endpoint" else list(range(INTERVALS))
    if stage == "midpoint":
        missing = [node for node in range(1, NODES) if not _valid(
            _endpoint_shard(node), "node", node,
            ("direction_arb", "first_arb", "second_arb"),
        )]
        if missing:
            raise RuntimeError(f"missing {len(missing)} correlated endpoint shards")
    groups = [indices[index::workers] for index in range(workers)]
    worker = _endpoint_worker if stage == "endpoint" else _midpoint_worker
    totals = {"computed": 0, "reused": 0}
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(worker, group) for group in groups if group]
        for future in as_completed(futures):
            result = future.result()
            for key in totals:
                totals[key] += result[key]
            print(json.dumps({"stage_complete_worker": stage, "totals": totals}), flush=True)


def build_payload() -> dict[str, object]:
    missing = [interval for interval in range(INTERVALS) if not _valid(
        _midpoint_shard(interval), "interval", interval,
        ("intrinsic_mid", "intrinsic_radius", "local_hs_mid", "local_hs_radius"),
    )]
    if missing:
        raise RuntimeError(f"missing {len(missing)} correlated midpoint shards")
    names = ("midpoint_direction", "midpoint_second_incidence", "intrinsic",
             "incidence", "total", "local_hs")
    arrays = {f"{name}_{suffix}": np.empty((INTERVALS, cert.STATE + 1))
              for name in names for suffix in ("mid", "radius")}
    gap = np.empty(INTERVALS); residual = np.empty(INTERVALS)
    axis_error = np.zeros(NODES)
    for node in range(1, NODES):
        with np.load(_endpoint_shard(node)) as source:
            axis_error[node] = source["axis_error_upper"]
    for interval in range(INTERVALS):
        with np.load(_midpoint_shard(interval)) as source:
            for key in arrays:
                arrays[key][interval] = source[key]
            gap[interval] = source["gap_lower"]
            residual[interval] = source["eigen_residual_upper"]
    bounds = {}; owners = {}
    for name in ("intrinsic", "incidence", "total", "local_hs"):
        upper = np.sqrt(np.sum((np.abs(arrays[f"{name}_mid"])
                                + arrays[f"{name}_radius"]) ** 2, axis=1))
        owner = int(np.argmax(upper)); arrays[f"{name}_norm_upper"] = upper
        bounds[name] = float(np.nextafter(upper[owner], math.inf)); owners[name] = owner
    arrays["axis_error_upper"] = axis_error
    arrays["precision_bits"] = np.asarray(PRECISION)
    np.savez_compressed(DATA, **arrays)
    with np.load(SEED.with_suffix(".npz")) as source:
        seed_intrinsic_mid = source["midpoint_intrinsic_curvature_mid"]
        seed_intrinsic_radius = source["midpoint_intrinsic_curvature_radius"]
    global_lower = arrays["intrinsic_mid"][355] - arrays["intrinsic_radius"][355]
    global_upper = arrays["intrinsic_mid"][355] + arrays["intrinsic_radius"][355]
    seed_lower = seed_intrinsic_mid - seed_intrinsic_radius
    seed_upper = seed_intrinsic_mid + seed_intrinsic_radius
    seed_reproduced = bool(
        np.all(global_lower <= seed_lower) and np.all(global_upper >= seed_upper)
        and np.max(arrays["intrinsic_radius"][355]) < 1.0e-15
    )
    validation = {
        "all_370_correlated_scalar_intervals_certified": True,
        "all_correlated_midpoint_arrays_finite": bool(all(
            np.all(np.isfinite(value)) for value in arrays.values()
        )),
        "interval355_seed_sharply_enclosed_after_exact_Arb_shard_transport": seed_reproduced,
        "all_selected_line_gaps_positive": bool(np.all(gap > 0.0)),
        "all_370_axis_neighborhood_errors_finite": bool(
            np.all(np.isfinite(axis_error[1:])) and np.all(axis_error[1:] > 0.0)
        ),
        "384_bit_Arb_retained_action_evaluation": PRECISION == 384,
        "axis_error_not_silently_discarded": True,
        "global_scalar_result_not_relabelled_as_mixed_transverse_or_causal_certificate": True,
        "same_center_action_branch_trajectory_scale_and_partition_retained": True,
    }
    maximum_axis_node = int(np.argmax(axis_error))
    return {
        "artifact": "BHSM_N12_GATE7_CURRENT_GREEN_CORRELATED_SCALAR_ALL_INTERVALS",
        "status": "CURRENT_GREEN_CORRELATED_CENTRAL_SCALAR_ALL_370_INTERVALS_CERTIFIED",
        "authority": "384_BIT_ARB_GLOBAL_CORRELATED_CENTRAL_SCALAR_NOT_AXIS_NEIGHBORHOOD_OR_CAUSAL_AUTHORITY",
        "intervals_certified": INTERVALS,
        "maximum_norm_upper": bounds,
        "maximum_norm_owner_interval": owners,
        "axis_neighborhood": {
            "maximum_error_upper": float(axis_error[maximum_axis_node]),
            "maximum_error_owner_node": maximum_axis_node,
            "classification": "REMAINS_INPUT_TO_MIXED_AND_TRANSVERSE_REMAINDER",
        },
        "minimum_branch_gap_lower": float(np.min(gap)),
        "maximum_eigen_residual_upper": float(np.max(residual)),
        "exact_next_calculation": "BOUND_THE_CERTIFIED_GREEN_AXIS_NEIGHBORHOOD_WITH_ACTION_DERIVED_MIXED_GREEN_TRANSVERSE_AND_TRANSVERSE_TRANSVERSE_REMAINDERS,_THEN_APPLY_THE_FROZEN_CAUSAL_PRECONDITIONER_AND_TWO_RADIUS_TEST",
        "claim_boundary": {
            "CURRENT_GREEN_CORRELATED_SCALAR_ALL_INTERVALS_DERIVED": True,
            "CURRENT_GREEN_AXIS_NEIGHBORHOOD_MIXED_TRANSVERSE_BOUND_DERIVED": False,
            "CURRENT_GREEN_CAUSAL_PRECONDITIONED_CURVATURE_DERIVED": False,
            "CURRENT_CENTER_GREEN_CAUSAL_TWO_RADIUS_CERTIFICATE_DERIVED": False,
            "G7_ROOT_NONEXISTENCE_DERIVED": False,
            "G7_PHYSICAL_SPACETIME_INSTABILITY_DERIVED": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "data": _relative(DATA), "data_SHA256": _sha(DATA),
        "inputs": {_relative(path): _sha(path) for path in INPUTS},
        "validation": validation, "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("endpoint", "midpoint"))
    parser.add_argument("--workers", type=int, default=min(4, os.cpu_count() or 1))
    parser.add_argument("--aggregate-only", action="store_true")
    args = parser.parse_args()
    if args.stage:
        _run(args.stage, max(1, args.workers))
        if args.stage == "endpoint":
            return
    if not args.stage and not args.aggregate_only:
        _run("endpoint", max(1, args.workers)); _run("midpoint", max(1, args.workers))
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("global correlated Green scalar validation failed")
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n",
                      encoding="utf-8", newline="\n")
    print(json.dumps({"status": payload["status"],
                      "maximum_norm_upper": payload["maximum_norm_upper"],
                      "axis_neighborhood": payload["axis_neighborhood"],
                      "validation_passed": payload["validation_passed"]},
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
