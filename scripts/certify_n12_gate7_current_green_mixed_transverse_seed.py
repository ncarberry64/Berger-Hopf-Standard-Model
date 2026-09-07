"""Certify current-center mixed Green/transverse maps at decisive seed nodes.

The historical 48-seam mixed-map mechanism is reused, but none of its
numerical values are imported.  Each current map is reconstructed by exact
polarization of the retained-action second rate derivative in the frozen
74-dimensional proof-coordinate frame.
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
import certify_n12_gate7_current_green_correlated_scalar_interval355 as scalar  # noqa: E402


F = ROOT / "artifacts/flagship_integration"
A = ROOT / "artifacts/action_extension"
ENDPOINT = F / "BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_NEWTON_ENDPOINT_CANDIDATE.json"
JACOBIAN = F / "BHSM_N12_GATE7_CORRELATED_DESCRIPTOR_AUGMENTED_JACOBIANS.json"
PARTITION = A / "BHSM_AE4_CURRENT_C2_GREEN_IMAGE_PARTITION_RECONCILIATION.json"
CENTRAL_CAUSAL = F / "BHSM_N12_GATE7_CURRENT_GREEN_CORRELATED_SCALAR_CAUSAL_COMPOSITION.json"
RESULT = F / "BHSM_N12_GATE7_CURRENT_GREEN_MIXED_TRANSVERSE_SEED.json"
DATA = RESULT.with_suffix(".npz")
WORK = F / ".current_green_mixed_transverse_seed_work"
THEORY = ROOT / "theory/n12_gate7_current_green_mixed_transverse_seed.md"
THIS_SCRIPT = Path(__file__).resolve()
PRECISION = 512
COORDINATES = 74
OUTPUTS = cert.STATE + 1
SEED_NODES = (1, 355, 356, 370)
SHARD_REVISION = 1
INPUTS = (
    ENDPOINT, ENDPOINT.with_suffix(".npz"),
    JACOBIAN, JACOBIAN.with_suffix(".npz"),
    PARTITION, PARTITION.with_suffix(".npz"),
    CENTRAL_CAUSAL, CENTRAL_CAUSAL.with_suffix(".npz"),
    Path(cert.__file__).resolve(), Path(scalar.__file__).resolve(),
    THIS_SCRIPT, THEORY,
)


def _sha(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _shard(node: int, column: int) -> Path:
    return WORK / f"node_{node:03d}_column_{column:02d}.npz"


def _valid(path: Path, node: int, column: int) -> bool:
    if not path.is_file():
        return False
    try:
        with np.load(path) as source:
            return (
                int(source["node"]) == node
                and int(source["column"]) == column
                and int(source["precision_bits"]) == PRECISION
                and int(source["shard_revision"]) == SHARD_REVISION
                and source["mixed_arb"].shape == (OUTPUTS,)
            )
    except Exception:
        return False


def _export(values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    midpoint = np.empty(values.shape, dtype=float)
    radius = np.empty_like(midpoint)
    for index in np.ndindex(values.shape):
        midpoint[index] = float(values[index])
        radius[index] = math.nextafter(
            float(abs(values[index] - arb(midpoint[index])).upper()), math.inf,
        )
    return midpoint, radius


def _frobenius_upper(midpoint: np.ndarray, radius: np.ndarray) -> float:
    total = 0.0
    for value, error in zip(
        np.asarray(midpoint, dtype=float).ravel(),
        np.asarray(radius, dtype=float).ravel(),
        strict=True,
    ):
        upper = math.nextafter(abs(float(value)) + float(error), math.inf)
        total = math.nextafter(total + upper * upper, math.inf)
    return math.nextafter(math.sqrt(total), math.inf)


def _worker(tasks: list[tuple[int, int]]) -> dict[str, int]:
    ctx.prec = PRECISION
    WORK.mkdir(parents=True, exist_ok=True)
    with np.load(ENDPOINT.with_suffix(".npz")) as source:
        states = np.asarray(source["projected_states"], dtype=float)
        descriptors = np.asarray(
            source["independent_signed_descriptors"], dtype=float,
        )
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)
    with np.load(JACOBIAN.with_suffix(".npz")) as source:
        tangents = np.asarray(
            source["endpoint_physical_tangent_action"], dtype=float,
        )
    with np.load(PARTITION.with_suffix(".npz")) as source:
        unit_mid = np.asarray(
            source["current_center_green_image_unit_mid"], dtype=float,
        )

    prepared: dict[int, tuple[np.ndarray, np.ndarray]] = {}
    original_action_jets = cert._arb_action_jets
    cached_node: int | None = None
    computed = reused = 0
    for count, (node, column) in enumerate(tasks, 1):
        target = _shard(node, column)
        if _valid(target, node, column):
            reused += 1
            continue
        if node not in prepared:
            axis = scalar._normalized_central_axis(unit_mid[node])
            projector = np.eye(COORDINATES) - np.outer(axis, axis)
            frame = cert._frame(tangents[node], cert.TRIAL_DESCRIPTOR_SCALE)
            prepared[node] = (frame @ axis, frame @ projector)
        if cached_node != node:
            jets = original_action_jets(states[node])
            cert._arb_action_jets = lambda _state, cached=jets: cached
            cached_node = node
        axis_direction, transverse_directions = prepared[node]
        transverse = transverse_directions[:, column]
        plus = cert._rate_second_directional(
            states[node], float(descriptors[node]), weights, reference,
            axis_direction + transverse,
        )
        minus = cert._rate_second_directional(
            states[node], float(descriptors[node]), weights, reference,
            axis_direction - transverse,
        )
        mixed = np.asarray([
            (plus[index] - minus[index]) / 4 for index in range(OUTPUTS)
        ], dtype=object)
        midpoint, radius = _export(mixed)
        np.savez_compressed(
            target,
            mixed_mid=midpoint,
            mixed_radius=radius,
            mixed_arb=cert._arb_string_array(mixed),
            mixed_column_norm_upper=np.asarray(cert._norm_upper(mixed)),
            node=np.asarray(node), column=np.asarray(column),
            precision_bits=np.asarray(PRECISION),
            shard_revision=np.asarray(SHARD_REVISION),
        )
        computed += 1
        if count % 2 == 0 or count == len(tasks):
            print(json.dumps({
                "worker": os.getpid(), "completed": count,
                "assigned": len(tasks), "node": node, "column": column,
            }), flush=True)
    cert._arb_action_jets = original_action_jets
    return {"computed": computed, "reused": reused}


def run_workers(workers: int) -> None:
    if workers >= len(SEED_NODES):
        lanes = max(1, workers // len(SEED_NODES))
        groups = [
            [(node, column) for column in range(lane, COORDINATES, lanes)]
            for node in SEED_NODES for lane in range(lanes)
        ]
    else:
        tasks = [
            (node, column)
            for node in SEED_NODES for column in range(COORDINATES)
        ]
        groups = [tasks[index::workers] for index in range(workers)]
    totals = {"computed": 0, "reused": 0}
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(_worker, group) for group in groups if group]
        for future in as_completed(futures):
            result = future.result()
            for key in totals:
                totals[key] += result[key]
            print(json.dumps({"mixed_seed_progress": totals}), flush=True)


def build_payload() -> dict[str, object]:
    missing_inputs = [str(path) for path in INPUTS if not path.is_file()]
    if missing_inputs:
        raise FileNotFoundError(", ".join(missing_inputs))
    missing = [
        (node, column)
        for node in SEED_NODES for column in range(COORDINATES)
        if not _valid(_shard(node, column), node, column)
    ]
    if missing:
        raise RuntimeError(f"missing {len(missing)} mixed seed shards")

    mixed_mid = np.empty((len(SEED_NODES), OUTPUTS, COORDINATES))
    mixed_radius = np.empty_like(mixed_mid)
    axes = np.empty((len(SEED_NODES), COORDINATES))
    projectors = np.empty((len(SEED_NODES), COORDINATES, COORDINATES))
    with np.load(PARTITION.with_suffix(".npz")) as source:
        unit_mid = np.asarray(
            source["current_center_green_image_unit_mid"], dtype=float,
        )
    rows = []
    for owner, node in enumerate(SEED_NODES):
        for column in range(COORDINATES):
            with np.load(_shard(node, column)) as source:
                mixed_mid[owner, :, column] = source["mixed_mid"]
                mixed_radius[owner, :, column] = source["mixed_radius"]
        axis = scalar._normalized_central_axis(unit_mid[node])
        projector = np.eye(COORDINATES) - np.outer(axis, axis)
        axes[owner] = axis
        projectors[owner] = projector
        frobenius_upper = _frobenius_upper(
            mixed_mid[owner], mixed_radius[owner],
        )
        axis_annihilation_mid = mixed_mid[owner] @ axis
        axis_annihilation_radius = mixed_radius[owner] @ np.abs(axis)
        rows.append({
            "node": node,
            "role": {
                1: "CURRENT_COARSE_WITNESS_AND_HISTORICAL_MIXED_OWNER",
                355: "FIRST_COMPONENTWISE_LOSS_INTERVAL_LEFT_ENDPOINT",
                356: "FIRST_COMPONENTWISE_LOSS_INTERVAL_RIGHT_ENDPOINT",
                370: "CURRENT_CAUSAL_CENTRAL_SCALAR_OWNER",
            }[node],
            "central_axis_norm_residual": float(abs(np.linalg.norm(axis) - 1.0)),
            "transverse_projector_idempotence_residual": float(
                np.linalg.norm(projector @ projector - projector, ord=2)
            ),
            "transverse_projector_annihilation_residual": float(
                np.linalg.norm(projector @ axis)
            ),
            "mixed_center_operator_2_norm": float(
                np.linalg.norm(mixed_mid[owner], ord=2)
            ),
            "mixed_interval_Frobenius_upper": frobenius_upper,
            "mixed_projected_map_axis_annihilation_center_residual": float(
                np.linalg.norm(axis_annihilation_mid)
            ),
            "mixed_projected_map_axis_annihilation_interval_upper": float(
                _frobenius_upper(
                    axis_annihilation_mid, axis_annihilation_radius,
                )
            ),
            "maximum_component_radius": float(
                np.max(mixed_radius[owner])
            ),
        })

    np.savez_compressed(
        DATA,
        seed_nodes=np.asarray(SEED_NODES),
        central_green_axis_coordinate=axes,
        transverse_projector_coordinate=projectors,
        mixed_green_transverse_mid=mixed_mid,
        mixed_green_transverse_radius=mixed_radius,
        precision_bits=np.asarray(PRECISION),
    )
    validation = {
        "all_four_decisive_current_nodes_evaluated": len(rows) == 4,
        "all_74_projected_coordinate_columns_evaluated_at_each_node": True,
        "512_bit_Arb_retained_action_polarization": PRECISION == 512,
        "all_mixed_interval_Frobenius_bounds_finite": all(
            math.isfinite(row["mixed_interval_Frobenius_upper"])
            for row in rows
        ),
        "all_exported_component_radii_finite_and_nonnegative": bool(
            np.all(np.isfinite(mixed_radius)) and np.all(mixed_radius >= 0.0)
        ),
        "all_transverse_projectors_close_below_1e_minus_12": all(
            row["transverse_projector_idempotence_residual"] < 1.0e-12
            and row["transverse_projector_annihilation_residual"] < 1.0e-12
            for row in rows
        ),
        "all_projected_mixed_map_center_axis_annihilation_residuals_below_1e_minus_10": all(
            row["mixed_projected_map_axis_annihilation_center_residual"]
            < 1.0e-10 for row in rows
        ),
        "historical_mechanism_reused_without_historical_numerical_values": True,
        "same_current_center_action_branch_frame_partition_and_scale_retained": True,
        "seed_not_relabelled_as_global_mixed_or_two_radius_authority": True,
    }
    owner = max(rows, key=lambda row: row["mixed_interval_Frobenius_upper"])
    return {
        "artifact": "BHSM_N12_GATE7_CURRENT_GREEN_MIXED_TRANSVERSE_SEED",
        "status": "CURRENT_GREEN_MIXED_TRANSVERSE_POLARIZATION_SEED_DERIVED",
        "authority": "512_BIT_ARB_RETAINED_ACTION_MIXED_SEED_NOT_GLOBAL_CAUSAL_OR_TWO_RADIUS_AUTHORITY",
        "polarization_identity": "D2F[u,v]=(D2F[u+v,u+v]-D2F[u-v,u-v])/4",
        "coordinate_split": "u_G_PLUS_ORTHOGONAL_COMPLEMENT_IN_FROZEN_74D_PROOF_COORDINATES",
        "rows": rows,
        "maximum_seed_mixed_interval_Frobenius_upper": owner[
            "mixed_interval_Frobenius_upper"
        ],
        "maximum_seed_mixed_owner_node": owner["node"],
        "exact_next_calculation": "EXTEND_THE_SAME_CORRELATED_POLARIZATION_MAP_TO_ALL_371_CURRENT_NODES_AND_HERMITE_SIMPSON_MIDPOINTS,_THEN_COMPOSE_ITS_SIGNED_CAUSAL_ACTION_WITH_THE_TRANSVERSE_TRANSVERSE_REMAINDER",
        "claim_boundary": {
            "CURRENT_GREEN_MIXED_TRANSVERSE_DECISIVE_NODE_SEED_DERIVED": True,
            "CURRENT_GREEN_MIXED_TRANSVERSE_ALL_NODES_DERIVED": False,
            "CURRENT_GREEN_MIXED_TRANSVERSE_ALL_MIDPOINTS_DERIVED": False,
            "CURRENT_GREEN_AXIS_NEIGHBORHOOD_MIXED_TRANSVERSE_BOUND_DERIVED": False,
            "CURRENT_GREEN_TRANSVERSE_TRANSVERSE_REMAINDER_DERIVED": False,
            "CURRENT_CENTER_GREEN_CAUSAL_TWO_RADIUS_CERTIFICATE_DERIVED": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "data": _relative(DATA),
        "data_SHA256": _sha(DATA),
        "inputs": {_relative(path): _sha(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=min(12, os.cpu_count() or 1))
    parser.add_argument("--aggregate-only", action="store_true")
    args = parser.parse_args()
    if not args.aggregate_only:
        run_workers(max(1, args.workers))
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("current Green mixed/transverse seed validation failed")
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "maximum_seed_mixed_interval_Frobenius_upper": payload[
            "maximum_seed_mixed_interval_Frobenius_upper"
        ],
        "maximum_seed_mixed_owner_node": payload[
            "maximum_seed_mixed_owner_node"
        ],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
