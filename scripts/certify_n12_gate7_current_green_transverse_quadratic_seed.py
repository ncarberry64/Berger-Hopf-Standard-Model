"""Certify current-center transverse quadratic seeds at decisive nodes."""

from __future__ import annotations

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
ENDPOINT = F / "BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_NEWTON_ENDPOINT_CANDIDATE.json"
JACOBIAN = F / "BHSM_N12_GATE7_CORRELATED_DESCRIPTOR_AUGMENTED_JACOBIANS.json"
MIXED = F / "BHSM_N12_GATE7_CURRENT_GREEN_MIXED_TRANSVERSE_SEED.json"
RESULT = F / "BHSM_N12_GATE7_CURRENT_GREEN_TRANSVERSE_QUADRATIC_SEED.json"
DATA = RESULT.with_suffix(".npz")
WORK = F / ".current_green_transverse_quadratic_seed_work"
THEORY = ROOT / "theory/n12_gate7_current_green_transverse_quadratic_seed.md"
THIS_SCRIPT = Path(__file__).resolve()
PRECISION = 512
SEED_NODES = (1, 355, 356, 370)
DIRECTION_NAMES = (
    "PROJECTED_COARSE_COORDINATE_61",
    "MIXED_MAP_LEADING_RIGHT_SINGULAR_DIRECTION",
)
SHARD_REVISION = 1
INPUTS = (
    ENDPOINT, ENDPOINT.with_suffix(".npz"),
    JACOBIAN, JACOBIAN.with_suffix(".npz"),
    MIXED, MIXED.with_suffix(".npz"),
    Path(cert.__file__).resolve(), THIS_SCRIPT, THEORY,
)


def _sha(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _shard(node: int, direction_index: int) -> Path:
    return WORK / f"node_{node:03d}_direction_{direction_index}.npz"


def _valid(path: Path, node: int, direction_index: int) -> bool:
    if not path.is_file():
        return False
    try:
        with np.load(path) as source:
            return (
                int(source["node"]) == node
                and int(source["direction_index"]) == direction_index
                and int(source["precision_bits"]) == PRECISION
                and int(source["shard_revision"]) == SHARD_REVISION
                and source["quadratic_arb"].shape == (cert.STATE + 1,)
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


def _coordinate_directions() -> tuple[np.ndarray, np.ndarray]:
    with np.load(MIXED.with_suffix(".npz")) as source:
        axes = np.asarray(source["central_green_axis_coordinate"], dtype=float)
        projectors = np.asarray(
            source["transverse_projector_coordinate"], dtype=float,
        )
        mixed = np.asarray(source["mixed_green_transverse_mid"], dtype=float)
    directions = np.empty((len(SEED_NODES), len(DIRECTION_NAMES), 74))
    for owner in range(len(SEED_NODES)):
        coarse = projectors[owner, :, 61]
        coarse /= np.linalg.norm(coarse)
        _, _, right = np.linalg.svd(mixed[owner], full_matrices=False)
        leading = projectors[owner] @ right[0]
        leading /= np.linalg.norm(leading)
        directions[owner, 0] = coarse
        directions[owner, 1] = leading
    return directions, axes


def _worker(node: int) -> dict[str, int]:
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
    coordinate_directions, _ = _coordinate_directions()
    owner = SEED_NODES.index(node)
    frame = cert._frame(tangents[node], cert.TRIAL_DESCRIPTOR_SCALE)
    jets = cert._arb_action_jets(states[node])
    original_action_jets = cert._arb_action_jets
    cert._arb_action_jets = lambda _state: jets
    computed = reused = 0
    for direction_index, coordinate in enumerate(coordinate_directions[owner]):
        target = _shard(node, direction_index)
        if _valid(target, node, direction_index):
            reused += 1
            continue
        direction = frame @ coordinate
        quadratic = cert._rate_second_directional(
            states[node], float(descriptors[node]), weights, reference,
            direction,
        )
        midpoint, radius = _export(quadratic)
        np.savez_compressed(
            target,
            coordinate_direction=coordinate,
            augmented_action_direction=direction,
            quadratic_mid=midpoint,
            quadratic_radius=radius,
            quadratic_arb=cert._arb_string_array(quadratic),
            norm_lower=np.asarray(cert._arb_norm_bounds(quadratic)["lower"]),
            norm_upper=np.asarray(cert._arb_norm_bounds(quadratic)["upper"]),
            node=np.asarray(node), direction_index=np.asarray(direction_index),
            precision_bits=np.asarray(PRECISION),
            shard_revision=np.asarray(SHARD_REVISION),
        )
        computed += 1
        print(json.dumps({
            "worker": os.getpid(), "node": node,
            "direction": DIRECTION_NAMES[direction_index],
        }), flush=True)
    cert._arb_action_jets = original_action_jets
    return {"computed": computed, "reused": reused}


def run_workers() -> None:
    totals = {"computed": 0, "reused": 0}
    with ProcessPoolExecutor(max_workers=len(SEED_NODES)) as executor:
        futures = [executor.submit(_worker, node) for node in SEED_NODES]
        for future in as_completed(futures):
            result = future.result()
            for key in totals:
                totals[key] += result[key]
            print(json.dumps({"transverse_seed_progress": totals}), flush=True)


def build_payload() -> dict[str, object]:
    missing_inputs = [str(path) for path in INPUTS if not path.is_file()]
    if missing_inputs:
        raise FileNotFoundError(", ".join(missing_inputs))
    missing = [
        (node, direction_index)
        for node in SEED_NODES
        for direction_index in range(len(DIRECTION_NAMES))
        if not _valid(_shard(node, direction_index), node, direction_index)
    ]
    if missing:
        raise RuntimeError(f"missing transverse quadratic seed shards: {missing}")

    coordinate_directions, axes = _coordinate_directions()
    quadratic_mid = np.empty((len(SEED_NODES), len(DIRECTION_NAMES), 99))
    quadratic_radius = np.empty_like(quadratic_mid)
    rows = []
    for owner, node in enumerate(SEED_NODES):
        for direction_index, name in enumerate(DIRECTION_NAMES):
            with np.load(_shard(node, direction_index)) as source:
                quadratic_mid[owner, direction_index] = source["quadratic_mid"]
                quadratic_radius[owner, direction_index] = source[
                    "quadratic_radius"
                ]
                rows.append({
                    "node": node,
                    "direction": name,
                    "coordinate_norm_residual": float(abs(
                        np.linalg.norm(coordinate_directions[owner, direction_index])
                        - 1.0
                    )),
                    "axis_orthogonality_residual": float(abs(
                        axes[owner] @ coordinate_directions[
                            owner, direction_index
                        ]
                    )),
                    "quadratic_rate_curvature_norm_lower": float(
                        source["norm_lower"]
                    ),
                    "quadratic_rate_curvature_norm_upper": float(
                        source["norm_upper"]
                    ),
                    "maximum_component_radius": float(np.max(
                        source["quadratic_radius"]
                    )),
                })
    np.savez_compressed(
        DATA,
        seed_nodes=np.asarray(SEED_NODES),
        direction_names=np.asarray(DIRECTION_NAMES),
        transverse_coordinate_directions=coordinate_directions,
        transverse_quadratic_mid=quadratic_mid,
        transverse_quadratic_radius=quadratic_radius,
        precision_bits=np.asarray(PRECISION),
    )
    validation = {
        "both_action_selected_transverse_directions_evaluated_at_four_nodes": len(rows) == 8,
        "512_bit_Arb_retained_action_second_rate_derivatives": PRECISION == 512,
        "all_direction_norm_residuals_below_1e_minus_12": all(
            row["coordinate_norm_residual"] < 1.0e-12 for row in rows
        ),
        "all_axis_orthogonality_residuals_below_1e_minus_12": all(
            row["axis_orthogonality_residual"] < 1.0e-12 for row in rows
        ),
        "all_quadratic_rate_curvature_bounds_finite_and_ordered": all(
            math.isfinite(row["quadratic_rate_curvature_norm_lower"])
            and math.isfinite(row["quadratic_rate_curvature_norm_upper"])
            and row["quadratic_rate_curvature_norm_lower"]
            <= row["quadratic_rate_curvature_norm_upper"]
            for row in rows
        ),
        "same_current_center_action_branch_frame_partition_and_scale_retained": True,
        "sampled_direction_seed_not_relabelled_as_full_transverse_operator_bound": True,
    }
    owner = max(rows, key=lambda row: row[
        "quadratic_rate_curvature_norm_upper"
    ])
    return {
        "artifact": "BHSM_N12_GATE7_CURRENT_GREEN_TRANSVERSE_QUADRATIC_SEED",
        "status": "CURRENT_GREEN_TRANSVERSE_TRANSVERSE_DECISIVE_DIRECTION_SEED_DERIVED",
        "authority": "512_BIT_ARB_RETAINED_ACTION_DIRECTIONAL_SEED_NOT_FULL_TRANSVERSE_OPERATOR_OR_TWO_RADIUS_AUTHORITY",
        "rows": rows,
        "maximum_seed_transverse_quadratic_norm_upper": owner[
            "quadratic_rate_curvature_norm_upper"
        ],
        "maximum_seed_transverse_quadratic_owner": {
            "node": owner["node"], "direction": owner["direction"],
        },
        "exact_next_calculation": "DERIVE_THE_FULL_CURRENT_TRANSVERSE_QUADRATIC_OPERATOR_MAJORANT_AROUND_THE_FOUR_VALIDATED_DIRECTIONS_AND_EXTEND_THE_MIXED_MAP_TO_ALL_ENDPOINTS_AND_MIDPOINTS_BEFORE_CAUSAL_TWO_RADIUS_COMPOSITION",
        "claim_boundary": {
            "CURRENT_GREEN_TRANSVERSE_TRANSVERSE_DECISIVE_DIRECTION_SEED_DERIVED": True,
            "CURRENT_GREEN_TRANSVERSE_TRANSVERSE_FULL_OPERATOR_BOUND_DERIVED": False,
            "CURRENT_GREEN_MIXED_TRANSVERSE_ALL_NODES_DERIVED": False,
            "CURRENT_GREEN_AXIS_NEIGHBORHOOD_MIXED_TRANSVERSE_BOUND_DERIVED": False,
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
    if not all(
        _valid(_shard(node, direction_index), node, direction_index)
        for node in SEED_NODES
        for direction_index in range(len(DIRECTION_NAMES))
    ):
        run_workers()
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("current transverse quadratic seed validation failed")
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "maximum_seed_transverse_quadratic_norm_upper": payload[
            "maximum_seed_transverse_quadratic_norm_upper"
        ],
        "maximum_seed_transverse_quadratic_owner": payload[
            "maximum_seed_transverse_quadratic_owner"
        ],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
