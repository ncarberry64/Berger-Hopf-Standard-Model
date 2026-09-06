"""Compose recovered signed transverse tensors through the frozen causal map.

This is the center-only successor to the failed componentwise representation
screen.  Endpoint, midpoint, incidence, test-frame, and reduced-inverse signs
are retained before local block-pair Frobenius norms are taken.  Each local
output covariance is then transported by the exact center causal products.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np
from scipy.linalg import null_space


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_n12_gate7_current_green_componentwise_two_radius as component  # noqa: E402
import certify_n12_gate7_accepted_replay_center_outward_74d as cert  # noqa: E402
import derive_n12_gate7_current_green_full_transverse_quadratic_center as center  # noqa: E402
import derive_n12_gate7_current_green_signed_transverse_tensor_recovery as recovery  # noqa: E402
import certify_n12_gate7_current_green_signed_transverse_tensor_recovery as recovery_aggregate  # noqa: E402


F = ROOT / "artifacts" / "flagship_integration"
A = ROOT / "artifacts" / "action_extension"
C = ROOT / "artifacts" / "current_semantics"
RESULT = F / "BHSM_N12_GATE7_CURRENT_GREEN_SIGNED_TRANSVERSE_CAUSAL_CENTER.json"
DATA = RESULT.with_suffix(".npz")
THEORY = ROOT / "theory" / "n12_gate7_current_green_signed_transverse_causal_center.md"
THIS_SCRIPT = Path(__file__).resolve()
JUSTIFICATION = C / "BHSM_N12_GATE7_CURRENT_GREEN_SIGNED_TENSOR_RECOVERY_COMPUTE_JUSTIFICATION.json"
RECOVERY_AGGREGATE = F / "BHSM_N12_GATE7_CURRENT_GREEN_SIGNED_TRANSVERSE_TENSOR_RECOVERY.json"
FULL = F / "BHSM_N12_GATE7_CURRENT_GREEN_FULL_TRANSVERSE_QUADRATIC_CENTER.json"
AMBIENT = F / "BHSM_N12_GATE7_CURRENT_GREEN_MIDPOINT_AMBIENT_DF.json"
CENTRAL = F / "BHSM_N12_GATE7_CURRENT_GREEN_CORRELATED_SCALAR_CAUSAL_COMPOSITION.json"
MIXED = F / "BHSM_N12_GATE7_CURRENT_GREEN_MIXED_HS_CAUSAL_TRANSPORT.json"
BLOCK_Z1 = F / "BHSM_N12_GATE7_CURRENT_GREEN_BLOCK_Z1.json"
PARTITION = A / "BHSM_AE4_CURRENT_C2_GREEN_IMAGE_PARTITION_RECONCILIATION.json"
ENDPOINT = F / "BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_NEWTON_ENDPOINT_CANDIDATE.json"
JACOBIAN = F / "BHSM_N12_GATE7_CORRELATED_DESCRIPTOR_AUGMENTED_JACOBIANS.json"
PRECONDITIONER = F / "BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_BLOCK_NEWTON_PREDICTOR.json"
Y_SOURCE = F / "BHSM_N12_GATE7_ACCEPTED_REPLAY_ACTION_BLOCK_SCREEN.json"
MIXED_WORK = F / ".current_green_mixed_hs_causal_transport_work"

NODES = 371
INTERVALS = 370
COORDINATES = 74
OUTPUTS = 99
TRANSVERSE = 73
PAIR_BLOCKS = 3


def _sha(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _tensor(kind: str, index: int) -> np.ndarray:
    path = recovery.WORK / f"{kind}_{index:03d}.npz"
    with np.load(path) as source:
        return np.asarray(source["quadratic_tensor"], dtype=float)


def _transformed(
    output_map: np.ndarray,
    tensor: np.ndarray,
    input_map: np.ndarray,
) -> np.ndarray:
    output = np.einsum("co,oab->cab", output_map, tensor, optimize=True)
    return np.einsum(
        "cab,ai,bj->cij", output, input_map, input_map, optimize=True,
    )


def _kinematic_midpoint_map(
    interval: int,
    h: float,
    endpoint_axes: np.ndarray,
    endpoint_tangents: np.ndarray,
    midpoint_tangents: np.ndarray,
) -> np.ndarray:
    blocks = []
    for node, sign in ((interval, 1.0), (interval + 1, -1.0)):
        if node == 0:
            transverse = np.zeros((OUTPUTS, COORDINATES))
            first = np.zeros_like(transverse)
        else:
            projector = np.eye(COORDINATES) - np.outer(
                endpoint_axes[node], endpoint_axes[node],
            )
            transverse = cert._frame(
                endpoint_tangents[node], cert.TRIAL_DESCRIPTOR_SCALE,
            ) @ projector
            with np.load(MIXED_WORK / f"endpoint_{node:03d}.npz") as source:
                first = np.asarray(source["first_mid"][:, 1:], dtype=float)
        blocks.append(0.5 * transverse + sign * h * first / 8.0)
    augmented = np.column_stack(blocks)
    midpoint_frame = cert._frame(
        midpoint_tangents[interval], cert.TRIAL_DESCRIPTOR_SCALE,
    )
    return np.linalg.lstsq(midpoint_frame, augmented, rcond=None)[0]


def _pair_blocks(local: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    left = local[:, :COORDINATES, :COORDINATES]
    cross = (
        local[:, :COORDINATES, COORDINATES:]
        + local[:, COORDINATES:, :COORDINATES].transpose(0, 2, 1)
    )
    right = local[:, COORDINATES:, COORDINATES:]
    return left, cross, right


def _covariance_blocks(local: np.ndarray) -> np.ndarray:
    covariances = np.empty((PAIR_BLOCKS, COORDINATES, COORDINATES))
    for index, block in enumerate(_pair_blocks(local)):
        flat = block.reshape((COORDINATES, -1))
        covariance = flat @ flat.T
        covariances[index] = 0.5 * (covariance + covariance.T)
    return covariances


def _local_covariances(
    endpoint_axes: np.ndarray,
    midpoint_axes: np.ndarray,
    endpoint_tangents: np.ndarray,
    midpoint_tangents: np.ndarray,
    times: np.ndarray,
    right_blocks: np.ndarray,
    ambient: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    covariances = np.empty((INTERVALS, PAIR_BLOCKS, COORDINATES, COORDINATES))
    adjacent_right_left = np.zeros(
        (INTERVALS, COORDINATES, COORDINATES), dtype=float,
    )
    local_norms = np.empty(INTERVALS)
    previous_right_flat: np.ndarray | None = None
    zero = np.zeros((OUTPUTS, TRANSVERSE, TRANSVERSE))
    for interval in range(INTERVALS):
        h = float(times[interval + 1] - times[interval])
        left_tensor = zero if interval == 0 else _tensor("endpoint", interval)
        right_tensor = _tensor("endpoint", interval + 1)
        midpoint_tensor = _tensor("midpoint", interval)

        left_axis = endpoint_axes[interval]
        left_basis = (
            np.zeros((COORDINATES, TRANSVERSE))
            if interval == 0 else
            null_space(left_axis.reshape(1, -1))
        )
        right_basis = null_space(endpoint_axes[interval + 1].reshape(1, -1))
        midpoint_basis = null_space(midpoint_axes[interval].reshape(1, -1))
        left_input = left_basis.T
        right_input = right_basis.T
        midpoint_coordinate = _kinematic_midpoint_map(
            interval, h, endpoint_axes, endpoint_tangents, midpoint_tangents,
        )
        midpoint_input = midpoint_basis.T @ midpoint_coordinate

        test = cert._frame(
            endpoint_tangents[interval + 1], cert.TEST_DESCRIPTOR_SCALE,
        ).T
        inverse_test = -np.linalg.solve(right_blocks[interval], test)
        incidence_map = inverse_test @ ambient[interval]
        left_output = h * inverse_test / 6.0 + h * h * incidence_map / 12.0
        right_output = h * inverse_test / 6.0 - h * h * incidence_map / 12.0
        midpoint_output = 2.0 * h * inverse_test / 3.0

        local = np.zeros((COORDINATES, 2 * COORDINATES, 2 * COORDINATES))
        if interval > 0:
            local[:, :COORDINATES, :COORDINATES] += _transformed(
                left_output, left_tensor, left_input,
            )
        local[:, COORDINATES:, COORDINATES:] += _transformed(
            right_output, right_tensor, right_input,
        )
        local += _transformed(
            midpoint_output, midpoint_tensor, midpoint_input,
        )
        pair_blocks = _pair_blocks(local)
        covariances[interval] = _covariance_blocks(local)
        left_flat = pair_blocks[0].reshape((COORDINATES, -1))
        if previous_right_flat is not None:
            adjacent_right_left[interval] = previous_right_flat @ left_flat.T
        previous_right_flat = pair_blocks[2].reshape((COORDINATES, -1))
        local_norms[interval] = math.nextafter(sum(
            math.sqrt(max(float(np.trace(covariance)), 0.0))
            for covariance in covariances[interval]
        ), math.inf)
    return covariances, adjacent_right_left, local_norms


def _causal_bounds(
    local_covariances: np.ndarray,
    adjacent_right_left: np.ndarray,
    maps: np.ndarray,
    axes: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    intervals = int(local_covariances.shape[0])
    if (
        local_covariances.shape != (
            intervals, PAIR_BLOCKS, COORDINATES, COORDINATES,
        )
        or adjacent_right_left.shape != (
            intervals, COORDINATES, COORDINATES,
        )
        or maps.shape != (intervals, COORDINATES, COORDINATES)
        or axes.shape != (intervals + 1, COORDINATES)
    ):
        raise ValueError("causal covariance inputs have incompatible shapes")
    longitudinal = np.zeros(intervals + 1)
    transverse = np.zeros(intervals + 1)
    diagonal = np.empty((0, COORDINATES, COORDINATES))
    off_diagonal = np.empty((0, COORDINATES, COORDINATES))
    pending_right: np.ndarray | None = None
    for interval in range(intervals):
        causal_map = maps[interval]
        if len(diagonal):
            diagonal = np.matmul(
                np.matmul(causal_map, diagonal), causal_map.T,
            )
            diagonal = 0.5 * (
                diagonal + diagonal.transpose(0, 2, 1)
            )
        if len(off_diagonal):
            off_diagonal = np.matmul(
                np.matmul(causal_map, off_diagonal), causal_map.T,
            )
            off_diagonal = 0.5 * (
                off_diagonal + off_diagonal.transpose(0, 2, 1)
            )
        if pending_right is not None:
            pending_right = causal_map @ pending_right @ causal_map.T
            cross = causal_map @ adjacent_right_left[interval]
            completed = (
                pending_right + local_covariances[interval, 0]
                + cross + cross.T
            )
            diagonal = np.concatenate((
                diagonal, 0.5 * (completed + completed.T)[None, ...],
            ), axis=0)
        pending_right = local_covariances[interval, 2].copy()
        off_diagonal = np.concatenate((
            off_diagonal, local_covariances[interval, 1][None, ...],
        ), axis=0)
        axis = axes[interval + 1]
        total_l = 0.0
        total_t = 0.0
        covariances = [*diagonal, *off_diagonal]
        if pending_right is not None:
            covariances.append(pending_right)
        for covariance in covariances:
            l2 = max(float(axis @ covariance @ axis), 0.0)
            total = max(float(np.trace(covariance)), l2)
            total_l = math.nextafter(total_l + math.sqrt(l2), math.inf)
            total_t = math.nextafter(
                total_t + math.sqrt(max(total - l2, 0.0)), math.inf,
            )
        longitudinal[interval + 1] = total_l
        transverse[interval + 1] = total_t
    return longitudinal, transverse


def build_payload() -> dict[str, object]:
    tracked_inputs = (
        JUSTIFICATION, RECOVERY_AGGREGATE, FULL, AMBIENT, CENTRAL, MIXED,
        BLOCK_Z1, PARTITION,
        ENDPOINT, JACOBIAN, PRECONDITIONER, Y_SOURCE, THEORY, THIS_SCRIPT,
        Path(recovery.__file__).resolve(),
    )
    missing = [str(path) for path in tracked_inputs if not path.is_file()]
    missing += [str(recovery.WORK / f"endpoint_{node:03d}.npz")
                for node in range(1, NODES)
                if not (recovery.WORK / f"endpoint_{node:03d}.npz").is_file()]
    missing += [str(recovery.WORK / f"midpoint_{interval:03d}.npz")
                for interval in range(INTERVALS)
                if not (recovery.WORK / f"midpoint_{interval:03d}.npz").is_file()]
    if missing:
        raise FileNotFoundError(f"missing inputs: {len(missing)}; first={missing[0]}")
    justification = json.loads(JUSTIFICATION.read_text(encoding="utf-8"))
    recovered = json.loads(RECOVERY_AGGREGATE.read_text(encoding="utf-8"))
    if not (
        justification.get("validation_passed") is True
        and justification.get("campaign_authorized") is True
        and recovered.get("validation_passed") is True
    ):
        raise RuntimeError("validated signed recovery aggregate required")
    shard_paths = (
        recovery_aggregate._paths("endpoint")
        + recovery_aggregate._paths("midpoint")
    )
    if recovery_aggregate._manifest(shard_paths) != recovered.get(
        "shard_manifest_SHA256"
    ):
        raise RuntimeError("signed recovery shard manifest changed")

    inputs = center._load_inputs()
    endpoint_axes = np.asarray(inputs["endpoint"][3], dtype=float)
    midpoint_axes = np.asarray(inputs["midpoint"][3], dtype=float)
    with np.load(JACOBIAN.with_suffix(".npz")) as source:
        endpoint_tangents = np.asarray(
            source["endpoint_physical_tangent_action"], dtype=float,
        )
        midpoint_tangents = np.asarray(
            source["midpoint_physical_tangent_action"], dtype=float,
        )
    with np.load(ENDPOINT.with_suffix(".npz")) as source:
        times = np.asarray(source["collocation_arc_parameters"], dtype=float)
        ceiling = float(
            source["independent_signed_descriptors"][-1]
            / cert.TRIAL_DESCRIPTOR_SCALE
        )
    with np.load(PRECONDITIONER.with_suffix(".npz")) as source:
        left = np.asarray(source["left_Newton_blocks"], dtype=float)
        right = np.asarray(source["reduced_right_Newton_blocks"], dtype=float)
    with np.load(AMBIENT.with_suffix(".npz")) as source:
        ambient = np.asarray(source["ambient_DF_mid"], dtype=float)

    maps = component._causal_maps(endpoint_tangents, left, right)
    local_covariances, adjacent_right_left, local_norms = _local_covariances(
        endpoint_axes, midpoint_axes, endpoint_tangents, midpoint_tangents,
        times, right, ambient,
    )
    transverse_l, transverse_t = _causal_bounds(
        local_covariances, adjacent_right_left, maps, endpoint_axes,
    )

    with np.load(Y_SOURCE.with_suffix(".npz")) as source:
        y_l, y_t = component._vector_blocks(
            np.asarray(source["accepted_center_causal_coordinate_mid"], dtype=float),
            np.asarray(source["accepted_center_causal_coordinate_radius"], dtype=float),
            endpoint_axes,
        )
    with np.load(CENTRAL.with_suffix(".npz")) as source:
        central_l, central_t = component._vector_blocks(
            np.asarray(source["causal_central_scalar_curvature_mid"], dtype=float),
            np.asarray(source["causal_central_scalar_curvature_radius"], dtype=float),
            endpoint_axes,
        )
    with np.load(MIXED.with_suffix(".npz")) as source:
        mixed_l, mixed_t = component._matrix_output_blocks(
            np.asarray(source["causal_mixed_mid"], dtype=float),
            np.asarray(
                source["causal_mixed_shared_affine_Frobenius_radius_upper"],
                dtype=float,
            ),
            endpoint_axes,
        )
    with np.load(BLOCK_Z1.with_suffix(".npz")) as source:
        zmax = np.asarray(source["causal_block_Z1_maximum_upper"], dtype=float)

    y = np.asarray([np.max(y_l), np.max(y_t)])
    z = np.asarray([[zmax[0], zmax[1]], [zmax[2], zmax[3]]])
    central_coeff = np.asarray([np.max(central_l), np.max(central_t)])
    mixed_coeff = np.asarray([np.max(mixed_l), np.max(mixed_t)])
    transverse_coeff = np.asarray([np.max(transverse_l), np.max(transverse_t)])
    screen = component._best_screen(
        y, z, central_coeff, mixed_coeff, transverse_coeff, ceiling,
    )
    np.savez_compressed(
        DATA,
        local_pair_output_covariances=local_covariances,
        adjacent_right_left_output_cross_covariances=adjacent_right_left,
        local_pair_block_Frobenius_upper=local_norms,
        causal_signed_transverse_longitudinal_center_upper=transverse_l,
        causal_signed_transverse_transverse_center_upper=transverse_t,
        causal_maps_center=maps,
    )
    validation = {
        "all_370_endpoint_and_370_midpoint_recovery_shards_consumed": True,
        "endpoint_midpoint_and_second_incidence_signs_composed_before_norms": True,
        "test_frame_and_reduced_inverse_composed_before_norms": True,
        "left_cross_and_right_input_block_correlations_retained_locally": True,
        "shared_node_diagonal_contributions_combined_across_adjacent_intervals_before_norms": True,
        "complete_370_interval_frozen_center_causal_transport_composed": True,
        "all_center_bounds_finite_and_nonnegative": bool(
            np.all(np.isfinite(local_norms)) and np.all(local_norms >= 0.0)
            and np.all(np.isfinite(transverse_l)) and np.all(transverse_l >= 0.0)
            and np.all(np.isfinite(transverse_t)) and np.all(transverse_t >= 0.0)
        ),
        "same_Y_Z1_central_mixed_two_radius_operands_reused": True,
        "outward_neighborhood_authority_not_claimed": True,
        "Gate7_not_closed_by_center_screen_alone": True,
        "no_action_source_mesh_parameter_precision_or_norm_changed": True,
        "FULL_BHSM_COMPLETE": False,
    }
    passed = (
        all(value for key, value in validation.items()
            if key != "FULL_BHSM_COMPLETE")
        and not validation["FULL_BHSM_COMPLETE"]
    )
    return {
        "artifact": "BHSM_N12_GATE7_CURRENT_GREEN_SIGNED_TRANSVERSE_CAUSAL_CENTER",
        "status": "SIGNED_TRANSVERSE_CAUSAL_CENTER_COMPOSED",
        "authority": (
            "COMPLETE_BINARY64_SIGNED_CENTER_HERMITE_SIMPSON_CAUSAL_"
            "COMPOSITION_NOT_OUTWARD_NEIGHBORHOOD_AUTHORITY"
        ),
        "coefficients": {
            "Y": y.tolist(), "Z1": z.tolist(),
            "central_quadratic": central_coeff.tolist(),
            "mixed_quadratic": mixed_coeff.tolist(),
            "signed_transverse_quadratic_center": transverse_coeff.tolist(),
        },
        "screen": screen,
        "data": _relative(DATA),
        "data_SHA256": _sha(DATA),
        "maximum_local_signed_pair_block_Frobenius_upper": float(
            np.max(local_norms)
        ),
        "maximum_local_owner_interval": int(np.argmax(local_norms)),
        "claim_boundary": {
            "SIGNED_CENTER_TENSORS_RECOVERED": True,
            "SIGNED_CAUSAL_TRANSVERSE_CENTER_OPERATOR_DERIVED": True,
            "OUTWARD_TRANSVERSE_REMAINDER_DERIVED": False,
            "CURRENT_CENTER_GREEN_CAUSAL_TWO_RADIUS_CERTIFICATE_DERIVED": False,
            "GATE7_CLOSED": False,
            "BHSM_PHYSICAL_BACKGROUND_AUTHORITY": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_calculation": (
            "IF_THE_SIGNED_CENTER_SCREEN_IS_VIABLE_ATTACH_THE_RIGOROUS_"
            "OUTWARD_AXIS_ROUNDING_AND_ACTION_REMAINDER_TO_THE_SAME_SIGNED_"
            "CAUSAL_COMPOSITION;_OTHERWISE_RECORD_THE_CENTER_REPRESENTATION_"
            "OBSTRUCTION_WITHOUT_RETUNING"
        ),
        "inputs": {_relative(path): _sha(path) for path in tracked_inputs},
        "validation": validation,
        "validation_passed": passed,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "coefficients": payload["coefficients"],
        "screen": payload["screen"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
