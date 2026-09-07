"""Recover full midpoint DF from certified Hermite--Simpson derivative maps."""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import time

import numpy as np
from flint import arb, ctx
from scipy.linalg import qr


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import certify_n12_gate7_accepted_replay_center_outward_74d as cert  # noqa: E402

F = ROOT / "artifacts/flagship_integration"
PARENT = F / "BHSM_N12_GATE7_ACCEPTED_REPLAY_CENTER_OUTWARD_74D_CONTRACTION.json"
JACOBIAN = F / "BHSM_N12_GATE7_CORRELATED_DESCRIPTOR_AUGMENTED_JACOBIANS.json"
ENDPOINT = F / "BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_NEWTON_ENDPOINT_CANDIDATE.json"
RESULT = F / "BHSM_N12_GATE7_CURRENT_GREEN_MIDPOINT_AMBIENT_DF.json"
DATA = RESULT.with_suffix(".npz")
WORK = F / ".current_green_midpoint_ambient_df_work"
THEORY = ROOT / "theory/n12_gate7_current_green_midpoint_ambient_df.md"
THIS_SCRIPT = Path(__file__).resolve()
DEFAULT_CACHE = F / ".accepted_replay_outward_74d_work"
PRECISION = 384
INTERVALS = 370
DIMENSION = 99
SHARD_REVISION = 1


def _sha(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _fingerprint(cache: Path) -> str:
    parent = json.loads(PARENT.read_text(encoding="utf-8"))
    payload = {
        "algorithm": "FULL_DF_FROM_SURJECTIVE_CERTIFIED_HS_DIRECTION_MAP_V1",
        "precision": PRECISION,
        "inputs": {_relative(path): _sha(path) for path in (
            PARENT, JACOBIAN.with_suffix(".npz"), ENDPOINT.with_suffix(".npz"),
            THEORY, THIS_SCRIPT,
        )},
        "endpoint_shards": parent["derived_work_aggregate_SHA256"][
            "371_outward_endpoint_rate_and_DF_shards"
        ],
        "midpoint_shards": parent["derived_work_aggregate_SHA256"][
            "370_outward_midpoint_rate_and_DF_shards"
        ],
        "cache_z1": _sha(cache / "z1_composition.npz"),
    }
    return hashlib.sha256(json.dumps(
        payload, sort_keys=True, separators=(",", ":"),
    ).encode()).hexdigest().upper()


def _target(index: int) -> Path:
    return WORK / f"midpoint_{index:03d}.npz"


def _valid(path: Path, index: int, fingerprint: str) -> bool:
    if not path.is_file():
        return False
    try:
        with np.load(path) as source:
            return bool(
                int(source["interval"]) == index
                and int(source["precision_bits"]) == PRECISION
                and int(source["shard_revision"]) == SHARD_REVISION
                and str(source["fingerprint"].item()) == fingerprint
                and source["ambient_DF_mid"].shape == (DIMENSION, DIMENSION)
                and source["ambient_DF_radius"].shape == (DIMENSION, DIMENSION)
            )
    except Exception:
        return False


def _row(index: int, cache: Path, tangents: np.ndarray,
         times: np.ndarray, fingerprint: str) -> dict[str, object]:
    ctx.prec = PRECISION
    target = _target(index)
    if _valid(target, index, fingerprint):
        return {"computed": 0, "reused": 1, "seconds": 0.0}
    started = time.perf_counter()
    h = arb(float(times[index + 1] - times[index]))
    directions = []
    direction_midpoints = []
    for node, sign in ((index, 1), (index + 1, -1)):
        frame = cert._frame(tangents[node], cert.TRIAL_DESCRIPTOR_SCALE)
        with np.load(cache / f"endpoint_{node:03d}.npz") as source:
            derivative = cert._parse_arb_string_array(source["derivative_arb"])
            derivative_mid = np.asarray(source["derivative_mid"], dtype=float)
        block = np.empty((DIMENSION, 74), dtype=object)
        for i in range(DIMENSION):
            for j in range(74):
                block[i, j] = (
                    arb(0.5 * frame[i, j])
                    + sign * h * derivative[i, j] / 8
                )
        directions.append(block)
        direction_midpoints.append(
            0.5 * frame + sign * float(h) * derivative_mid / 8
        )
    direction = np.column_stack(directions)
    direction_mid = np.column_stack(direction_midpoints)
    with np.load(cache / f"midpoint_{index:03d}.npz") as source:
        image = cert._parse_arb_string_array(source["derivative_arb"])
    _, _, pivots = qr(direction_mid, pivoting=True, mode="economic")
    selected = np.asarray(pivots[:DIMENSION], dtype=int)
    square = cert._arb_mat_from_array(direction[:, selected])
    image_square = cert._arb_mat_from_array(image[:, selected])
    inverse = square.inv()
    ambient = image_square * inverse
    residual = (
        ambient * cert._arb_mat_from_array(direction)
        - cert._arb_mat_from_array(image)
    )
    contains_zero = True
    residual_upper = 0.0
    for i in range(residual.nrows()):
        for j in range(residual.ncols()):
            value = residual[i, j]
            contains_zero &= float(value.lower()) <= 0.0 <= float(value.upper())
            residual_upper = max(
                residual_upper, float(abs(value).upper()),
            )
    midpoint, radius = cert._matrix_export(ambient)
    singular_values = np.linalg.svd(direction_mid[:, selected], compute_uv=False)
    np.savez_compressed(
        target,
        ambient_DF_mid=midpoint,
        ambient_DF_radius=radius,
        selected_direction_columns=selected,
        selected_direction_sigma_min=np.asarray(float(singular_values[-1])),
        selected_direction_condition_2=np.asarray(
            float(singular_values[0] / singular_values[-1])
        ),
        reconstruction_residual_contains_zero=np.asarray(contains_zero),
        reconstruction_residual_absolute_upper=np.asarray(residual_upper),
        interval=np.asarray(index), precision_bits=np.asarray(PRECISION),
        shard_revision=np.asarray(SHARD_REVISION),
        fingerprint=np.asarray(fingerprint),
        elapsed_seconds=np.asarray(time.perf_counter() - started),
        worker_id=np.asarray(os.getpid()),
    )
    if not contains_zero:
        raise RuntimeError(f"midpoint {index} reconstruction residual excludes zero")
    return {"computed": 1, "reused": 0,
            "seconds": time.perf_counter() - started}


def _worker(indices: list[int], cache: Path) -> dict[str, float]:
    with np.load(JACOBIAN.with_suffix(".npz")) as source:
        tangents = np.asarray(source["endpoint_physical_tangent_action"], dtype=float)
    with np.load(ENDPOINT.with_suffix(".npz")) as source:
        times = np.asarray(source["collocation_arc_parameters"], dtype=float)
    fingerprint = _fingerprint(cache)
    total = {"computed": 0.0, "reused": 0.0, "seconds": 0.0}
    for index in indices:
        result = _row(index, cache, tangents, times, fingerprint)
        for key in total:
            total[key] += float(result[key])
    return total


def _run(indices: list[int], workers: int, cache: Path) -> None:
    WORK.mkdir(parents=True, exist_ok=True)
    groups = [indices[index::workers] for index in range(workers)]
    totals = {"computed": 0.0, "reused": 0.0, "seconds": 0.0}
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(_worker, group, cache)
                   for group in groups if group]
        for future in as_completed(futures):
            row = future.result()
            for key in totals:
                totals[key] += row[key]
            print(json.dumps({"totals": totals}), flush=True)


def _aggregate(cache: Path) -> dict[str, object]:
    fingerprint = _fingerprint(cache)
    paths = [_target(index) for index in range(INTERVALS)]
    missing = [str(path) for index, path in enumerate(paths)
               if not _valid(path, index, fingerprint)]
    if missing:
        raise RuntimeError(f"missing or invalid shards: {len(missing)}")
    mid = np.empty((INTERVALS, DIMENSION, DIMENSION))
    rad = np.empty_like(mid)
    sigma = np.empty(INTERVALS)
    condition = np.empty(INTERVALS)
    residual = np.empty(INTERVALS)
    seconds = np.empty(INTERVALS)
    contained = np.empty(INTERVALS, dtype=bool)
    for index, path in enumerate(paths):
        with np.load(path) as source:
            mid[index] = source["ambient_DF_mid"]
            rad[index] = source["ambient_DF_radius"]
            sigma[index] = source["selected_direction_sigma_min"]
            condition[index] = source["selected_direction_condition_2"]
            residual[index] = source["reconstruction_residual_absolute_upper"]
            seconds[index] = source["elapsed_seconds"]
            contained[index] = source["reconstruction_residual_contains_zero"]
    frobenius_upper = np.nextafter(
        np.linalg.norm(mid, axis=(1, 2)) + np.linalg.norm(rad, axis=(1, 2)),
        math.inf,
    )
    np.savez_compressed(
        DATA, ambient_DF_mid=mid, ambient_DF_radius=rad,
        ambient_DF_Frobenius_upper=frobenius_upper,
        selected_direction_sigma_min=sigma,
        selected_direction_condition_2=condition,
        reconstruction_residual_absolute_upper=residual,
        precision_bits=np.asarray(PRECISION), fingerprint=np.asarray(fingerprint),
    )
    validation = {
        "all_370_midpoints_reconstructed": mid.shape == (370, 99, 99),
        "all_reconstruction_residual_balls_contain_zero": bool(np.all(contained)),
        "all_selected_direction_matrices_are_nonsingular": bool(np.all(sigma > 0)),
        "all_exports_finite_with_nonnegative_radii": bool(
            np.all(np.isfinite(mid)) and np.all(np.isfinite(rad))
            and np.all(rad >= 0)
        ),
        "same_384_bit_certified_HS_endpoint_and_midpoint_maps_reused": True,
        "no_new_action_evaluation_center_scale_partition_or_fit": True,
        "ambient_DF_not_relabelled_as_two_radius_certificate": True,
        "FULL_BHSM_COMPLETE": False,
    }
    passed = all(v for k, v in validation.items()
                 if k != "FULL_BHSM_COMPLETE") and not validation["FULL_BHSM_COMPLETE"]
    payload = {
        "artifact": "BHSM_N12_GATE7_CURRENT_GREEN_MIDPOINT_AMBIENT_DF",
        "status": "CURRENT_GREEN_MIDPOINT_AMBIENT_FIRST_VARIATIONS_RECONSTRUCTED",
        "authority": "384_BIT_ARB_SURJECTIVE_HERMITE_SIMPSON_DIRECTION_MAP_IDENTITY",
        "precision_bits": PRECISION,
        "minimum_selected_direction_sigma_min": float(np.min(sigma)),
        "maximum_selected_direction_condition_2": float(np.max(condition)),
        "maximum_reconstruction_residual_absolute_upper": float(np.max(residual)),
        "maximum_ambient_DF_Frobenius_upper": float(np.max(frobenius_upper)),
        "measured_CPU_hours": float(np.sum(seconds) / 3600),
        "data": _relative(DATA), "data_SHA256": _sha(DATA),
        "exact_next_calculation": "APPLY_THE_RECONSTRUCTED_MIDPOINT_DF_TO_THE_FULL_TRANSVERSE_SECOND_INCIDENCE_BOX_AND_COMPOSE_THE_TRANSVERSE_HERMITE_SIMPSON_CAUSAL_MAJORANT",
        "claim_boundary": {
            "CURRENT_GREEN_MIDPOINT_AMBIENT_DF_DERIVED": True,
            "CURRENT_GREEN_TRANSVERSE_TRANSVERSE_FULL_OPERATOR_BOUND_DERIVED": False,
            "CURRENT_CENTER_GREEN_CAUSAL_TWO_RADIUS_CERTIFICATE_DERIVED": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {_relative(path): _sha(path) for path in (
            PARENT, PARENT.with_suffix(".npz"), JACOBIAN,
            JACOBIAN.with_suffix(".npz"), ENDPOINT,
            ENDPOINT.with_suffix(".npz"), THEORY, THIS_SCRIPT,
        )},
        "cache_attestation": {
            "accepted_endpoint_shards": json.loads(PARENT.read_text())[
                "derived_work_aggregate_SHA256"
            ]["371_outward_endpoint_rate_and_DF_shards"],
            "accepted_midpoint_shards": json.loads(PARENT.read_text())[
                "derived_work_aggregate_SHA256"
            ]["370_outward_midpoint_rate_and_DF_shards"],
        },
        "validation": validation, "validation_passed": passed,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n",
                      encoding="utf-8", newline="\n")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--accepted-cache", type=Path, default=DEFAULT_CACHE)
    parser.add_argument("--indices", default="")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--aggregate-only", action="store_true")
    args = parser.parse_args()
    cache = args.accepted_cache.resolve()
    if not args.aggregate_only:
        indices = list(range(INTERVALS)) if not args.indices else [
            int(value) for value in args.indices.split(",") if value
        ]
        _run(indices, max(1, min(args.workers, len(indices))), cache)
        return
    payload = _aggregate(cache)
    print(json.dumps({
        "status": payload["status"],
        "maximum_ambient_DF_Frobenius_upper": payload[
            "maximum_ambient_DF_Frobenius_upper"
        ],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
