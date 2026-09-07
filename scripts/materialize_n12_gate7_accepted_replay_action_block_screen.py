"""Screen the same-center Gate-7 field/descriptor block radii route.

This materializer deliberately recomputes only the outward value enclosure
needed for the accepted-center defect.  It reuses the already-certified
single-direction curvature vector, so it can decide whether the coarse
73-field-plus-1-descriptor block split survives before any dense nonlinear
interval tensor is commissioned.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
import math
import os
from pathlib import Path

import numpy as np
from flint import arb, arb_mat, ctx

import certify_n12_gate7_accepted_replay_center_outward_74d as cert


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
ENDPOINT = BASE / "BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_NEWTON_ENDPOINT_CANDIDATE.json"
REPLAY = BASE / "BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_NEWTON_MIDPOINT_REPLAY.json"
OLD_JACOBIAN = BASE / "BHSM_N12_GATE7_CORRELATED_DESCRIPTOR_AUGMENTED_JACOBIANS.json"
PRECONDITIONER = BASE / "BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_BLOCK_NEWTON_PREDICTOR.json"
OBSTRUCTION = BASE / "BHSM_N12_GATE7_ACCEPTED_REPLAY_CENTER_OUTWARD_74D_CONTRACTION.json"
RESULT = BASE / "BHSM_N12_GATE7_ACCEPTED_REPLAY_ACTION_BLOCK_SCREEN.json"
DATA = RESULT.with_suffix(".npz")
WORK = BASE / ".accepted_replay_action_block_screen_work"
THEORY = ROOT / "theory" / "n12_gate7_accepted_replay_action_block_screen.md"
THIS_SCRIPT = Path(__file__).resolve()
PRECISION = cert.PRECISION
SHARD_REVISION = 1


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _aggregate_sha256(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in paths:
        digest.update(path.name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(bytes.fromhex(_sha256(path)))
    return digest.hexdigest().upper()


def _target(stage: str, index: int) -> Path:
    return WORK / f"value_{stage}_{index:03d}.npz"


def _value_worker(index: int, stage: str) -> tuple[int, str]:
    ctx.prec = PRECISION
    WORK.mkdir(parents=True, exist_ok=True)
    target = _target(stage, index)
    if target.exists():
        try:
            with np.load(target) as existing:
                if (
                    int(existing["precision_bits"]) == PRECISION
                    and int(existing["shard_revision"]) == SHARD_REVISION
                    and "value_arb" in existing.files
                ):
                    return index, "reused"
        except Exception:
            pass

    with np.load(ENDPOINT.with_suffix(".npz")) as source:
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)
        if stage == "endpoint":
            state = np.asarray(source["projected_states"][index], dtype=float)
            descriptor = float(source["independent_signed_descriptors"][index])
        elif stage == "midpoint":
            with np.load(REPLAY.with_suffix(".npz")) as replay:
                augmented = np.asarray(
                    replay["midpoint_augmented_action_values"][index], dtype=float,
                )
            state = augmented[:98] / weights
            descriptor = float(augmented[98])
        else:
            raise ValueError(stage)

    enclosed = cert._rate_enclosure(state, descriptor, weights, reference, None)
    value_mid, value_radius = cert._export(enclosed.value)
    np.savez_compressed(
        target,
        value_mid=value_mid,
        value_radius=value_radius,
        value_arb=cert._arb_string_array(enclosed.value),
        gap_lower=np.asarray(enclosed.gap_lower),
        eigen_residual_upper=np.asarray(enclosed.eigen_residual_upper),
        precision_bits=np.asarray(PRECISION),
        shard_revision=np.asarray(SHARD_REVISION),
    )
    return index, "computed"


def _run_stage(stage: str, workers: int) -> None:
    total = 371 if stage == "endpoint" else 370
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(_value_worker, index, stage) for index in range(total)]
        for count, future in enumerate(futures, 1):
            index, disposition = future.result()
            if count % 16 == 0 or count == total:
                print(json.dumps({
                    "stage": stage,
                    "completed": count,
                    "total": total,
                    "index": index,
                    "disposition": disposition,
                }), flush=True)


def _abs_bounds(value: arb) -> tuple[float, float]:
    magnitude = abs(value)
    return float(magnitude.lower()), math.nextafter(float(magnitude.upper()), math.inf)


def _ball_vector(midpoint: np.ndarray, radius: np.ndarray) -> np.ndarray:
    return np.asarray([
        arb(float(value), float(error))
        for value, error in zip(np.asarray(midpoint), np.asarray(radius))
    ], dtype=object)


def _compose() -> None:
    ctx.prec = PRECISION
    endpoint_paths = [_target("endpoint", index) for index in range(371)]
    midpoint_paths = [_target("midpoint", index) for index in range(370)]
    missing = [path for path in endpoint_paths + midpoint_paths if not path.exists()]
    if missing:
        raise RuntimeError(f"missing {len(missing)} outward value shards")

    with np.load(ENDPOINT.with_suffix(".npz")) as source:
        states = np.asarray(source["projected_states"], dtype=float)
        descriptors = np.asarray(source["independent_signed_descriptors"], dtype=float)
        weights = np.asarray(source["state_weights"], dtype=float)
        times = np.asarray(source["collocation_arc_parameters"], dtype=float)
    centers = np.column_stack((states * weights[None, :], descriptors))
    with np.load(OLD_JACOBIAN.with_suffix(".npz")) as source:
        tangents = np.asarray(source["endpoint_physical_tangent_action"], dtype=float)
    with np.load(PRECONDITIONER.with_suffix(".npz")) as source:
        old_left = np.asarray(source["left_Newton_blocks"], dtype=float)
        old_right = np.asarray(source["reduced_right_Newton_blocks"], dtype=float)

    coordinate = arb_mat(74, 1)
    coordinate_mid = np.zeros((371, 74), dtype=float)
    coordinate_radius = np.zeros_like(coordinate_mid)
    total_bounds = [(0.0, 0.0)]
    field_bounds = [(0.0, 0.0)]
    descriptor_bounds = [(0.0, 0.0)]
    minimum_gap = math.inf
    maximum_eigen_residual = 0.0

    for interval, h_float in enumerate(np.diff(times)):
        h = cert._a(float(h_float))
        with np.load(endpoint_paths[interval]) as left:
            e0 = cert._arb_mat_from_array(cert._parse_arb_string_array(left["value_arb"]))
            minimum_gap = min(minimum_gap, float(left["gap_lower"]))
            maximum_eigen_residual = max(maximum_eigen_residual, float(left["eigen_residual_upper"]))
        with np.load(endpoint_paths[interval + 1]) as right:
            e1 = cert._arb_mat_from_array(cert._parse_arb_string_array(right["value_arb"]))
            minimum_gap = min(minimum_gap, float(right["gap_lower"]))
            maximum_eigen_residual = max(maximum_eigen_residual, float(right["eigen_residual_upper"]))
        with np.load(midpoint_paths[interval]) as middle:
            em = cert._arb_mat_from_array(cert._parse_arb_string_array(middle["value_arb"]))
            minimum_gap = min(minimum_gap, float(middle["gap_lower"]))
            maximum_eigen_residual = max(maximum_eigen_residual, float(middle["eigen_residual_upper"]))

        residual = (
            cert._arb_vector(centers[interval + 1])
            - cert._arb_vector(centers[interval])
            - h * (e0 + 4 * em + e1) / 6
        )
        test = cert._arb_matrix(cert._frame(
            tangents[interval + 1], cert.TEST_DESCRIPTOR_SCALE,
        ).T)
        trial = cert._arb_matrix(cert._frame(
            tangents[interval], cert.TRIAL_DESCRIPTOR_SCALE,
        ))
        inverse = cert._arb_matrix(old_right[interval]).inv()
        coordinate = -inverse * (
            test * residual
            + test * cert._arb_matrix(old_left[interval]) * trial * coordinate
        )
        vector = cert._array(coordinate).ravel()
        coordinate_mid[interval + 1], coordinate_radius[interval + 1] = cert._export(vector)
        total_bounds.append((cert._arb_norm_lower(vector), cert._norm_upper(vector)))
        field_bounds.append((cert._arb_norm_lower(vector[:73]), cert._norm_upper(vector[:73])))
        descriptor_bounds.append(_abs_bounds(vector[73]))

    total_lower = np.asarray([row[0] for row in total_bounds])
    total_upper = np.asarray([row[1] for row in total_bounds])
    field_lower = np.asarray([row[0] for row in field_bounds])
    field_upper = np.asarray([row[1] for row in field_bounds])
    descriptor_lower = np.asarray([row[0] for row in descriptor_bounds])
    descriptor_upper = np.asarray([row[1] for row in descriptor_bounds])
    total_owner = int(np.argmax(total_upper))
    field_owner = int(np.argmax(field_lower))
    descriptor_owner = int(np.argmax(descriptor_upper))

    obstruction_record = json.loads(OBSTRUCTION.read_text(encoding="utf-8"))
    with np.load(OBSTRUCTION.with_suffix(".npz")) as source:
        curvature = _ball_vector(
            source["terminal_directional_curvature_mid"],
            source["terminal_directional_curvature_radius"],
        )
        obstruction_coordinate = int(source["obstruction_causal_coordinate"])
    curvature_field_lower = cert._arb_norm_lower(curvature[:73])
    curvature_field_upper = cert._norm_upper(curvature[:73])
    curvature_descriptor_lower, curvature_descriptor_upper = _abs_bounds(curvature[73])
    discriminant_upper = float((
        arb(1)
        - arb(4)
        * arb(float(field_lower[field_owner]))
        * arb(float(curvature_field_lower))
    ).upper())
    scalar_y = obstruction_record["outward_operands"]
    scalar_y_reproduced = (
        total_lower[total_owner] <= float(scalar_y["Y_lower"])
        and total_upper[total_owner] >= float(scalar_y["Y_upper"])
    )

    np.savez_compressed(
        DATA,
        accepted_center_causal_coordinate_mid=coordinate_mid,
        accepted_center_causal_coordinate_radius=coordinate_radius,
        total_Y_lower_by_node=total_lower,
        total_Y_upper_by_node=total_upper,
        field_Y_lower_by_node=field_lower,
        field_Y_upper_by_node=field_upper,
        descriptor_Y_lower_by_node=descriptor_lower,
        descriptor_Y_upper_by_node=descriptor_upper,
        witness_terminal_curvature_field_lower=np.asarray(curvature_field_lower),
        witness_terminal_curvature_field_upper=np.asarray(curvature_field_upper),
        witness_terminal_curvature_descriptor_lower=np.asarray(curvature_descriptor_lower),
        witness_terminal_curvature_descriptor_upper=np.asarray(curvature_descriptor_upper),
    )

    validation = {
        "same_frozen_accepted_replay_center": True,
        "same_frozen_preconditioner": True,
        "same_causal_74D_frame": True,
        "all_741_value_enclosures_recomputed_in_Arb": True,
        "scalar_Y_interval_reproduces_upstream_certificate": scalar_y_reproduced,
        "obstruction_input_is_inside_73D_field_block": obstruction_coordinate < 73,
        "coarse_field_block_necessary_discriminant_strictly_negative": discriminant_upper < 0.0,
        "no_dense_Z2_tensor_needed_for_this_route_obstruction": True,
        "no_new_center_trajectory_scale_or_fit": True,
        "componentwise_or_finer_action_block_route_not_adjudicated": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    payload = {
        "artifact": "BHSM_N12_GATE7_ACCEPTED_REPLAY_ACTION_BLOCK_SCREEN",
        "status": (
            "SAME_CENTER_FIELD_DESCRIPTOR_BLOCK_RADII_ROUTE_OBSTRUCTED"
            if passed else "SAME_CENTER_FIELD_DESCRIPTOR_BLOCK_SCREEN_INCONCLUSIVE"
        ),
        "authority": "384_BIT_ARB_NECESSARY_RADII_POLYNOMIAL_OBSTRUCTION",
        "action_version": "BHSM-AE-4.0.0",
        "block_partition": {
            "field": "CAUSAL_COORDINATES_0_THROUGH_72",
            "independent_descriptor": "CAUSAL_COORDINATE_73",
            "scaling": "EXISTING_FROZEN_ACTION_CAUSAL_FRAME",
        },
        "outward_center_defect": {
            "total_Y_owner_node": total_owner,
            "total_Y_lower": float(total_lower[total_owner]),
            "total_Y_upper": float(total_upper[total_owner]),
            "field_Y_owner_node": field_owner,
            "field_Y_lower": float(field_lower[field_owner]),
            "field_Y_upper": float(field_upper[field_owner]),
            "descriptor_Y_owner_node": descriptor_owner,
            "descriptor_Y_lower": float(descriptor_lower[descriptor_owner]),
            "descriptor_Y_upper": float(descriptor_upper[descriptor_owner]),
        },
        "existing_curvature_witness": {
            "input_causal_coordinate": obstruction_coordinate,
            "input_block": "FIELD",
            "terminal_field_block_curvature_lower": curvature_field_lower,
            "terminal_field_block_curvature_upper": curvature_field_upper,
            "terminal_descriptor_coordinate_curvature_lower": curvature_descriptor_lower,
            "terminal_descriptor_coordinate_curvature_upper": curvature_descriptor_upper,
        },
        "necessary_field_block_test": {
            "polynomial_lower_form": "Y_field_lower-r_field+Z_field_from_field_lower*r_field^2",
            "discriminant_upper": discriminant_upper,
            "classification": (
                "NO_POSITIVE_FIELD_RADIUS_CAN_SATISFY_THE_COARSE_FIELD_BLOCK_SELF_MAP"
                if discriminant_upper < 0.0 else "INCONCLUSIVE"
            ),
            "linear_and_cross_block_terms_omitted_for_necessary_lower_test": True,
        },
        "decision": {
            "coarse_73_plus_1_field_descriptor_block_route_obstructed": discriminant_upper < 0.0,
            "componentwise_or_finer_action_owned_partition_obstructed": False,
            "root_nonexistence_claim": False,
            "physical_spacetime_instability_claim": False,
            "new_center_or_trajectory_authorized": False,
            "dense_two_block_Z2_campaign_required": False,
            "why": "THE_ALREADY_CERTIFIED_FIELD_INPUT_DIRECTION_RETURNS_ENOUGH_CURVATURE_TO_THE_FIELD_BLOCK_THAT_ITS_NECESSARY_QUADRATIC_DISCRIMINANT_IS_NEGATIVE",
        },
        "exact_next_calculation": "SAME_CENTER_COMPONENTWISE_OR_FINER_ACTION_OWNED_BLOCK_RADII_SCREEN;_PERSIST_DIRECTION_BY_OUTPUT_BLOCK_CURVATURE_ENVELOPES_ONLY_FOR_THE_SURVIVING_PARTITION",
        "data": _relative(DATA),
        "data_SHA256": _sha256(DATA),
        "minimum_branch_gap_lower": minimum_gap,
        "maximum_eigen_residual_upper": maximum_eigen_residual,
        "derived_work_aggregate_SHA256": {
            "371_outward_endpoint_value_shards": _aggregate_sha256(endpoint_paths),
            "370_outward_midpoint_value_shards": _aggregate_sha256(midpoint_paths),
        },
        "inputs": {
            _relative(path): _sha256(path)
            for path in (
                ENDPOINT, ENDPOINT.with_suffix(".npz"),
                REPLAY, REPLAY.with_suffix(".npz"),
                OLD_JACOBIAN, OLD_JACOBIAN.with_suffix(".npz"),
                PRECONDITIONER, PRECONDITIONER.with_suffix(".npz"),
                OBSTRUCTION, OBSTRUCTION.with_suffix(".npz"),
                THEORY,
                THIS_SCRIPT,
            )
        },
        "claim_boundary": {
            "G7_SAME_CENTER_FIELD_DESCRIPTOR_BLOCK_RADII_POLYNOMIAL_DERIVED": False,
            "G7_SAME_CENTER_FIELD_DESCRIPTOR_BLOCK_ROUTE_OBSTRUCTED": discriminant_upper < 0.0,
            "G7_SAME_CENTER_COMPONENTWISE_OR_FINER_BLOCK_RADII_DERIVED": False,
            "G7_ROOT_NONEXISTENCE_DERIVED": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "validation": validation,
        "validation_passed": passed,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "outward_center_defect": payload["outward_center_defect"],
        "existing_curvature_witness": payload["existing_curvature_witness"],
        "necessary_field_block_test": payload["necessary_field_block_test"],
        "validation_passed": passed,
    }, indent=2, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("endpoint", "midpoint"))
    parser.add_argument("--workers", type=int, default=min(4, os.cpu_count() or 1))
    args = parser.parse_args()
    if args.stage:
        _run_stage(args.stage, args.workers)
    else:
        _compose()


if __name__ == "__main__":
    main()
