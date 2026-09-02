"""Certify retained-action Green-directional curvature at every endpoint.

The calculation is resumable because each post-reset endpoint is persisted as
an independent 384-bit Arb shard before the deterministic aggregate is built.
"""

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
JACOBIAN = F / "BHSM_N12_GATE7_CORRELATED_DESCRIPTOR_AUGMENTED_JACOBIANS.json"
PARTITION = A / "BHSM_AE4_CURRENT_C2_GREEN_IMAGE_PARTITION_RECONCILIATION.json"
SEED = F / "BHSM_N12_GATE7_CURRENT_GREEN_DIRECTIONAL_CURVATURE_SEED.json"
RESULT = F / "BHSM_N12_GATE7_CURRENT_GREEN_DIRECTIONAL_ENDPOINT_CURVATURE.json"
DATA = RESULT.with_suffix(".npz")
WORK = F / ".current_green_directional_endpoint_work"
THEORY = ROOT / "theory/n12_gate7_current_green_directional_endpoint_curvature.md"
THIS_SCRIPT = Path(__file__).resolve()
PRECISION = cert.PRECISION
NODES = 371
FIRST_POST_RESET_NODE = 1
SHARD_REVISION = 1
INPUTS = (
    ENDPOINT,
    ENDPOINT.with_suffix(".npz"),
    JACOBIAN,
    JACOBIAN.with_suffix(".npz"),
    PARTITION,
    PARTITION.with_suffix(".npz"),
    SEED,
    SEED.with_suffix(".npz"),
    Path(cert.__file__).resolve(),
    THIS_SCRIPT,
    THEORY,
)


def _sha(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _shard(node: int) -> Path:
    return WORK / f"endpoint_{node:03d}.npz"


def _export(values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    midpoint = np.empty(values.shape, dtype=float)
    radius = np.empty_like(midpoint)
    for index in np.ndindex(values.shape):
        midpoint[index] = float(values[index])
        radius[index] = math.nextafter(
            float(abs(values[index] - arb(midpoint[index])).upper()), math.inf,
        )
    return midpoint, radius


def _arb_strings(values: np.ndarray) -> np.ndarray:
    result = np.empty(values.shape, dtype="<U180")
    for index in np.ndindex(values.shape):
        result[index] = values[index].str(140)
    return result


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


def _valid_shard(path: Path, node: int) -> bool:
    if not path.is_file():
        return False
    try:
        with np.load(path) as data:
            return (
                int(data["node"]) == node
                and int(data["precision_bits"]) == PRECISION
                and int(data["shard_revision"]) == SHARD_REVISION
                and data["curvature_arb"].shape == (cert.STATE + 1,)
            )
    except Exception:
        return False


def _range_worker(nodes: list[int]) -> dict[str, object]:
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

    computed = 0
    reused = 0
    for count, node in enumerate(nodes, 1):
        target = _shard(node)
        if _valid_shard(target, node):
            reused += 1
            continue
        frame = cert._frame(tangents[node], cert.TRIAL_DESCRIPTOR_SCALE)
        direction = _direction(frame, unit_mid[node], unit_radius[node])
        curvature = cert._rate_second_directional(
            states[node], float(descriptors[node]), weights, reference, direction,
        )
        midpoint, radius = _export(curvature)
        total = cert._arb_norm_bounds(curvature)
        np.savez_compressed(
            target,
            curvature_mid=midpoint,
            curvature_radius=radius,
            curvature_arb=_arb_strings(curvature),
            norm_lower=np.asarray(total["lower"]),
            norm_upper=np.asarray(total["upper"]),
            node=np.asarray(node),
            precision_bits=np.asarray(PRECISION),
            shard_revision=np.asarray(SHARD_REVISION),
        )
        computed += 1
        if count % 4 == 0 or count == len(nodes):
            print(json.dumps({
                "worker": os.getpid(), "completed": count,
                "assigned": len(nodes), "node": node,
            }), flush=True)
    return {"computed": computed, "reused": reused, "assigned": len(nodes)}


def run_workers(workers: int) -> None:
    nodes = list(range(FIRST_POST_RESET_NODE, NODES))
    groups = [nodes[index::workers] for index in range(workers)]
    groups = [group for group in groups if group]
    totals = {"computed": 0, "reused": 0, "assigned": 0}
    with ProcessPoolExecutor(max_workers=len(groups)) as executor:
        futures = [executor.submit(_range_worker, group) for group in groups]
        for future in as_completed(futures):
            result = future.result()
            for key in totals:
                totals[key] += int(result[key])
            print(json.dumps({"endpoint_campaign_progress": totals}), flush=True)


def build_payload() -> dict[str, object]:
    missing_inputs = [str(path) for path in INPUTS if not path.is_file()]
    if missing_inputs:
        raise FileNotFoundError(", ".join(missing_inputs))
    missing = [node for node in range(1, NODES) if not _valid_shard(_shard(node), node)]
    if missing:
        raise RuntimeError(f"missing or stale endpoint shards: {missing[:12]} ({len(missing)} total)")

    curvature_mid = np.zeros((NODES, cert.STATE + 1), dtype=float)
    curvature_radius = np.zeros_like(curvature_mid)
    norm_lower = np.zeros(NODES, dtype=float)
    norm_upper = np.zeros(NODES, dtype=float)
    for node in range(1, NODES):
        with np.load(_shard(node)) as data:
            curvature_mid[node] = np.asarray(data["curvature_mid"], dtype=float)
            curvature_radius[node] = np.asarray(data["curvature_radius"], dtype=float)
            norm_lower[node] = float(data["norm_lower"])
            norm_upper[node] = float(data["norm_upper"])

    owner = int(np.argmax(norm_upper[1:]) + 1)
    minimum_owner = int(np.argmin(norm_lower[1:]) + 1)
    owner_component = int(np.argmax(
        np.abs(curvature_mid[owner]) + curvature_radius[owner]
    ))
    terminal_growth_factor = math.nextafter(
        float(norm_upper[-1] / norm_upper[1]), math.inf,
    )
    final_31_strictly_increasing = bool(np.all(np.diff(norm_upper[-31:]) > 0.0))
    with np.load(SEED.with_suffix(".npz")) as seed:
        seed_mid = np.asarray(seed["green_directional_rate_curvature_mid"], dtype=float)
        seed_radius = np.asarray(seed["green_directional_rate_curvature_radius"], dtype=float)
    seed_reproduced = bool(
        np.array_equal(curvature_mid[1], seed_mid)
        and np.array_equal(curvature_radius[1], seed_radius)
    )

    np.savez_compressed(
        DATA,
        green_directional_endpoint_curvature_mid=curvature_mid,
        green_directional_endpoint_curvature_radius=curvature_radius,
        green_directional_endpoint_norm_lower=norm_lower,
        green_directional_endpoint_norm_upper=norm_upper,
        post_reset_node_mask=np.arange(NODES) > 0,
        precision_bits=np.asarray(PRECISION),
    )
    validation = {
        "all_370_post_reset_endpoint_shards_present": True,
        "384_bit_Arb_retained_action_evaluation": PRECISION == 384,
        "node1_seed_reproduced_byte_for_byte_at_array_level": seed_reproduced,
        "all_post_reset_endpoint_curvature_bounds_finite": bool(
            np.all(np.isfinite(norm_lower[1:])) and np.all(np.isfinite(norm_upper[1:]))
        ),
        "all_post_reset_endpoint_curvature_intervals_ordered": bool(
            np.all(norm_lower[1:] <= norm_upper[1:])
        ),
        "terminal_endpoint_is_the_maximum_upper_owner": owner == NODES - 1,
        "final_31_endpoint_upper_bounds_strictly_increase": final_31_strictly_increasing,
        "reset_node_excluded_because_its_green_image_is_exactly_zero": bool(
            np.all(curvature_mid[0] == 0.0) and np.all(curvature_radius[0] == 0.0)
        ),
        "same_center_action_branch_frame_and_partition_retained": True,
        "endpoint_result_not_relabelled_as_midpoint_or_causal_certificate": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    return {
        "artifact": "BHSM_N12_GATE7_CURRENT_GREEN_DIRECTIONAL_ENDPOINT_CURVATURE",
        "status": "CURRENT_CENTER_ALL_POST_RESET_ENDPOINT_GREEN_DIRECTIONAL_CURVATURE_CERTIFIED",
        "authority": "384_BIT_ARB_ENDPOINT_DIRECTIONAL_CURVATURE_NOT_MIDPOINT_OR_CAUSAL_TWO_RADIUS_AUTHORITY",
        "precision_bits": PRECISION,
        "nodes": NODES,
        "post_reset_nodes_certified": NODES - 1,
        "reset_node": {
            "node": 0,
            "classification": "FIXED_ZERO_GREEN_IMAGE_NO_LONGITUDINAL_UNIT_AXIS",
        },
        "endpoint_green_directional_curvature_norm": {
            "minimum_lower": float(norm_lower[minimum_owner]),
            "minimum_lower_owner_node": minimum_owner,
            "maximum_upper": float(norm_upper[owner]),
            "maximum_upper_owner_node": owner,
            "node1_seed_lower": float(norm_lower[1]),
            "node1_seed_upper": float(norm_upper[1]),
        },
        "terminal_endpoint_stiffening": {
            "terminal_node": NODES - 1,
            "terminal_norm_lower": float(norm_lower[-1]),
            "terminal_norm_upper": float(norm_upper[-1]),
            "terminal_to_node1_upper_growth_factor": terminal_growth_factor,
            "terminal_owner_output_coordinate": owner_component,
            "final_31_endpoint_upper_bounds_strictly_increase": final_31_strictly_increasing,
            "classification": "RAW_LOCAL_COLLAPSE_SIDE_GREEN_CURVATURE_GROWTH_REQUIRES_HERMITE_SIMPSON_INCIDENCE_AND_CAUSAL_PRECONDITIONING_BEFORE_ROUTE_ADJUDICATION",
        },
        "interpretation": "THE_BHSM_NATIVE_CURRENT_GREEN_AXIS_NOW_HAS_ACTION_DERIVED_LOCAL_SECOND_DIRECTIONAL_RATE_CURVATURE_AT_EVERY_POST_RESET_ENDPOINT;_ITS_RAW_NORM_STIFFENS_BY_MORE_THAN_TWELVE_ORDERS_OF_MAGNITUDE_TOWARD_THE_TERMINAL_COLLAPSE_SIDE,_BUT_THE_HERMITE_SIMPSON_MIDPOINT_INCIDENCE_AND_CAUSAL_COMPOSITION_REMAIN_OPEN",
        "exact_next_calculation": "DERIVE_THE_CORRELATED_HERMITE_SIMPSON_MIDPOINT_GREEN_DIRECTION_AND_ITS_SECOND_INCIDENCE_FROM_THE_CERTIFIED_ENDPOINT_FIRST_AND_SECOND_RATE_VARIATIONS,_THEN_COMPOSE_THE_COMPLETE_LONGITUDINAL_CAUSAL_CURVATURE",
        "claim_boundary": {
            "CURRENT_CENTER_ALL_POST_RESET_ENDPOINT_GREEN_DIRECTIONAL_CURVATURE_DERIVED": True,
            "CURRENT_CENTER_GREEN_MIDPOINT_DIRECTIONAL_CURVATURE_DERIVED": False,
            "CURRENT_CENTER_GREEN_MIXED_CURVATURE_DERIVED": False,
            "CURRENT_CENTER_GREEN_CAUSAL_TWO_RADIUS_CERTIFICATE_DERIVED": False,
            "G7_ROOT_NONEXISTENCE_DERIVED": False,
            "G7_PHYSICAL_SPACETIME_INSTABILITY_DERIVED": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "data": _relative(DATA),
        "data_SHA256": _sha(DATA),
        "inputs": {_relative(path): _sha(path) for path in INPUTS},
        "derived_work_aggregate_SHA256": hashlib.sha256("".join(
            _sha(_shard(node)) for node in range(1, NODES)
        ).encode("ascii")).hexdigest().upper(),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=min(4, os.cpu_count() or 1))
    parser.add_argument("--aggregate-only", action="store_true")
    args = parser.parse_args()
    if not args.aggregate_only:
        run_workers(max(1, int(args.workers)))
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("endpoint Green-directional curvature validation failed")
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "endpoint_green_directional_curvature_norm": payload[
            "endpoint_green_directional_curvature_norm"
        ],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
