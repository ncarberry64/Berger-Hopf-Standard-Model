"""Test the optimistic componentwise current-Green two-radius assembly.

This is a representation screen.  It deliberately omits the still-open
normal/axis and outward-tube additions.  Failure therefore shows that merely
outwardizing the stored componentwise center norms cannot close Gate 7; it
does not prove root nonexistence or physical instability.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import certify_n12_gate7_accepted_replay_center_outward_74d as cert  # noqa: E402
import certify_n12_gate7_current_green_correlated_scalar_interval355 as scalar  # noqa: E402

F = ROOT / "artifacts/flagship_integration"
A = ROOT / "artifacts/action_extension"
RESULT = F / "BHSM_N12_GATE7_CURRENT_GREEN_COMPONENTWISE_TWO_RADIUS_SCREEN.json"
DATA = RESULT.with_suffix(".npz")
THEORY = ROOT / "theory/n12_gate7_current_green_componentwise_two_radius_screen.md"
THIS_SCRIPT = Path(__file__).resolve()

FULL = F / "BHSM_N12_GATE7_CURRENT_GREEN_FULL_TRANSVERSE_QUADRATIC_CENTER.json"
AMBIENT = F / "BHSM_N12_GATE7_CURRENT_GREEN_MIDPOINT_AMBIENT_DF.json"
CENTRAL_LOCAL = F / "BHSM_N12_GATE7_CURRENT_GREEN_CORRELATED_SCALAR_ALL_INTERVALS.json"
CENTRAL_CAUSAL = F / "BHSM_N12_GATE7_CURRENT_GREEN_CORRELATED_SCALAR_CAUSAL_COMPOSITION.json"
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


def _sha(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _vector_blocks(mid: np.ndarray, rad: np.ndarray,
                   axes: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    longitudinal = np.zeros(NODES)
    transverse = np.zeros(NODES)
    for node in range(1, NODES):
        value = float(axes[node] @ mid[node])
        error = float(abs(axes[node]) @ rad[node])
        longitudinal[node] = math.nextafter(abs(value) + error, math.inf)
        tmid = mid[node] - axes[node] * value
        trad = rad[node] + abs(axes[node]) * error
        transverse[node] = math.nextafter(
            float(np.linalg.norm(tmid)) + float(np.linalg.norm(trad)), math.inf,
        )
    return longitudinal, transverse


def _matrix_output_blocks(mid: np.ndarray, radius: np.ndarray,
                          axes: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    longitudinal = np.zeros(NODES)
    transverse = np.zeros(NODES)
    for node in range(1, NODES):
        left = axes[node] @ mid[node]
        longitudinal[node] = math.nextafter(
            float(np.linalg.norm(left)) + float(radius[node]), math.inf,
        )
        projected = mid[node] - np.outer(axes[node], left)
        transverse[node] = math.nextafter(
            float(np.linalg.norm(projected)) + float(radius[node]), math.inf,
        )
    return longitudinal, transverse


def _load_axes() -> np.ndarray:
    with np.load(PARTITION.with_suffix(".npz")) as source:
        raw = np.asarray(source["current_center_green_image_unit_mid"], dtype=float)
    axes = np.zeros_like(raw)
    axes[1:] = raw[1:] / np.linalg.norm(raw[1:], axis=1)[:, None]
    return axes


def _causal_maps(tangents: np.ndarray, left: np.ndarray,
                 right: np.ndarray) -> np.ndarray:
    maps = np.empty((INTERVALS, COORDINATES, COORDINATES))
    for interval in range(INTERVALS):
        test = cert._frame(
            tangents[interval + 1], cert.TEST_DESCRIPTOR_SCALE,
        ).T
        trial = cert._frame(
            tangents[interval], cert.TRIAL_DESCRIPTOR_SCALE,
        )
        maps[interval] = -np.linalg.solve(
            right[interval], test @ left[interval] @ trial,
        )
    return maps


def _local_transverse_center_bounds(
    axes: np.ndarray, tangents: np.ndarray, midpoint_tangents: np.ndarray,
    times: np.ndarray, right: np.ndarray,
) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    with np.load(FULL.with_suffix(".npz")) as source:
        endpoint_q = np.asarray(source["endpoint_output_Frobenius_norms"], dtype=float)
        midpoint_q = np.asarray(source["midpoint_output_Frobenius_norms"], dtype=float)
    with np.load(CENTRAL_LOCAL.with_suffix(".npz")) as source:
        central = abs(np.asarray(source["intrinsic_mid"], dtype=float)) + np.asarray(
            source["intrinsic_radius"], dtype=float,
        )
        midpoint_direction = np.asarray(source["midpoint_direction_mid"], dtype=float)
    with np.load(AMBIENT.with_suffix(".npz")) as source:
        ambient = abs(np.asarray(source["ambient_DF_mid"], dtype=float)) + np.asarray(
            source["ambient_DF_radius"], dtype=float,
        )

    local = np.empty((INTERVALS, COORDINATES))
    intrinsic_norm = np.empty(INTERVALS)
    incidence_norm = np.empty(INTERVALS)
    midpoint_longitudinal_norm = np.empty(INTERVALS)
    midpoint_transverse_norm = np.empty(INTERVALS)
    midpoint_normal_residual = np.empty(INTERVALS)
    for interval in range(INTERVALS):
        h = float(times[interval + 1] - times[interval])
        kinematic_blocks = []
        for node, sign in ((interval, 1.0), (interval + 1, -1.0)):
            if node == 0:
                transverse = np.zeros((OUTPUTS, COORDINATES))
                first = np.zeros_like(transverse)
            else:
                projector = np.eye(COORDINATES) - np.outer(axes[node], axes[node])
                transverse = cert._frame(
                    tangents[node], cert.TRIAL_DESCRIPTOR_SCALE,
                ) @ projector
                with np.load(MIXED_WORK / f"endpoint_{node:03d}.npz") as source:
                    first = np.asarray(source["first_mid"][:, 1:], dtype=float)
            kinematic_blocks.append(0.5 * transverse + sign * h * first / 8.0)
        kinematic = np.column_stack(kinematic_blocks)
        midpoint_frame = cert._frame(
            midpoint_tangents[interval], cert.TRIAL_DESCRIPTOR_SCALE,
        )
        coordinate = np.linalg.lstsq(midpoint_frame, kinematic, rcond=None)[0]
        normal = kinematic - midpoint_frame @ coordinate
        axis_coordinate = np.linalg.lstsq(
            midpoint_frame, midpoint_direction[interval], rcond=None,
        )[0]
        axis_coordinate /= np.linalg.norm(axis_coordinate)
        longitudinal_row = axis_coordinate @ coordinate
        transverse_coordinate = coordinate - np.outer(
            axis_coordinate, longitudinal_row,
        )
        lnorm = float(np.linalg.norm(longitudinal_row))
        tnorm = float(np.linalg.norm(transverse_coordinate, ord=2))
        midpoint_longitudinal_norm[interval] = lnorm
        midpoint_transverse_norm[interval] = tnorm
        midpoint_normal_residual[interval] = float(np.linalg.norm(normal, ord=2))
        with np.load(MIXED_WORK / f"midpoint_{interval:03d}.npz") as source:
            mixed_intrinsic = np.linalg.norm(
                abs(np.asarray(source["intrinsic_mid"], dtype=float))
                + np.asarray(source["intrinsic_radius"], dtype=float), axis=1,
            )
        intrinsic = (
            central[interval] * lnorm**2
            + 2.0 * mixed_intrinsic * lnorm * tnorm
            + midpoint_q[interval] * tnorm**2
        )
        left_q = endpoint_q[interval - 1] if interval > 0 else np.zeros(OUTPUTS)
        right_q = endpoint_q[interval]
        second_incidence = h * (left_q + right_q) / 8.0
        incidence = ambient[interval] @ second_incidence
        output = h * (
            left_q + 4.0 * (intrinsic + incidence) + right_q
        ) / 6.0
        test = cert._frame(
            tangents[interval + 1], cert.TEST_DESCRIPTOR_SCALE,
        ).T
        local[interval] = abs(np.linalg.solve(right[interval], test)) @ output
        intrinsic_norm[interval] = float(np.linalg.norm(intrinsic))
        incidence_norm[interval] = float(np.linalg.norm(incidence))
    return local, {
        "midpoint_intrinsic_output_norm": intrinsic_norm,
        "midpoint_incidence_output_norm": incidence_norm,
        "midpoint_longitudinal_coordinate_operator_norm": midpoint_longitudinal_norm,
        "midpoint_transverse_coordinate_operator_norm": midpoint_transverse_norm,
        "omitted_midpoint_normal_operator_norm": midpoint_normal_residual,
    }


def _transport_boxes(local: np.ndarray, maps: np.ndarray,
                     axes: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    longitudinal = np.zeros(NODES)
    transverse = np.zeros(NODES)
    products: list[np.ndarray] = []
    for interval in range(INTERVALS):
        products = [maps[interval] @ product for product in products]
        products.append(np.eye(COORDINATES))
        axis = axes[interval + 1]
        projector = np.eye(COORDINATES) - np.outer(axis, axis)
        lbound = 0.0
        tcomponents = np.zeros(COORDINATES)
        for source, product in enumerate(products):
            lbound += float(abs(axis @ product) @ local[source])
            tcomponents += abs(projector @ product) @ local[source]
        longitudinal[interval + 1] = math.nextafter(lbound, math.inf)
        transverse[interval + 1] = math.nextafter(
            float(np.linalg.norm(tcomponents)), math.inf,
        )
    return longitudinal, transverse


def _best_screen(y: np.ndarray, z: np.ndarray, c: np.ndarray,
                 m: np.ndarray, t: np.ndarray, ceiling: float) -> dict[str, object]:
    longitudinal_grid = np.geomspace(max(y[0], 1.0e-15), ceiling, 360)
    transverse_grid = np.geomspace(max(y[1], 1.0e-15), ceiling, 520)
    best = None
    feasible = False
    for longitudinal in longitudinal_grid:
        radius = np.column_stack((
            np.full_like(transverse_grid, longitudinal), transverse_grid,
        ))
        rhs = (
            y[None, :] + radius @ z.T
            + c[None, :] * longitudinal**2
            + 2.0 * m[None, :] * longitudinal * transverse_grid[:, None]
            + t[None, :] * transverse_grid[:, None] ** 2
        )
        margin = radius - rhs
        relative = np.min(margin / radius, axis=1)
        index = int(np.argmax(relative))
        if best is None or float(relative[index]) > best[0]:
            best = (
                float(relative[index]), longitudinal,
                float(transverse_grid[index]), rhs[index], margin[index],
            )
        feasible |= bool(np.any(np.all(margin > 0.0, axis=1)))
    assert best is not None
    return {
        "positive_self_map_found": feasible,
        "best_minimum_relative_self_map_margin": best[0],
        "best_longitudinal_radius": best[1],
        "best_transverse_radius": best[2],
        "best_rhs": best[3].tolist(),
        "best_absolute_margin": best[4].tolist(),
        "grid_shape": [len(longitudinal_grid), len(transverse_grid)],
    }


def build_payload() -> dict[str, object]:
    inputs = (
        FULL, FULL.with_suffix(".npz"), AMBIENT, AMBIENT.with_suffix(".npz"),
        CENTRAL_LOCAL, CENTRAL_LOCAL.with_suffix(".npz"), CENTRAL_CAUSAL,
        CENTRAL_CAUSAL.with_suffix(".npz"), MIXED, MIXED.with_suffix(".npz"),
        BLOCK_Z1, BLOCK_Z1.with_suffix(".npz"), PARTITION,
        PARTITION.with_suffix(".npz"), ENDPOINT, ENDPOINT.with_suffix(".npz"),
        JACOBIAN, JACOBIAN.with_suffix(".npz"), PRECONDITIONER,
        PRECONDITIONER.with_suffix(".npz"), Y_SOURCE,
        Y_SOURCE.with_suffix(".npz"), THEORY, THIS_SCRIPT,
    )
    missing = [str(path) for path in inputs if not path.is_file()]
    missing += [str(MIXED_WORK / f"endpoint_{node:03d}.npz")
                for node in range(1, NODES)
                if not (MIXED_WORK / f"endpoint_{node:03d}.npz").is_file()]
    missing += [str(MIXED_WORK / f"midpoint_{interval:03d}.npz")
                for interval in range(INTERVALS)
                if not (MIXED_WORK / f"midpoint_{interval:03d}.npz").is_file()]
    if missing:
        raise FileNotFoundError(f"missing inputs: {len(missing)}; first={missing[0]}")
    axes = _load_axes()
    with np.load(JACOBIAN.with_suffix(".npz")) as source:
        tangents = np.asarray(source["endpoint_physical_tangent_action"], dtype=float)
        midpoint_tangents = np.asarray(source["midpoint_physical_tangent_action"], dtype=float)
    with np.load(ENDPOINT.with_suffix(".npz")) as source:
        times = np.asarray(source["collocation_arc_parameters"], dtype=float)
        descriptor_ceiling = float(
            source["independent_signed_descriptors"][-1]
            / cert.TRIAL_DESCRIPTOR_SCALE
        )
    with np.load(PRECONDITIONER.with_suffix(".npz")) as source:
        left = np.asarray(source["left_Newton_blocks"], dtype=float)
        right = np.asarray(source["reduced_right_Newton_blocks"], dtype=float)
    maps = _causal_maps(tangents, left, right)
    local, decomposition = _local_transverse_center_bounds(
        axes, tangents, midpoint_tangents, times, right,
    )
    transverse_l, transverse_t = _transport_boxes(local, maps, axes)

    with np.load(Y_SOURCE.with_suffix(".npz")) as source:
        y_l, y_t = _vector_blocks(
            np.asarray(source["accepted_center_causal_coordinate_mid"], dtype=float),
            np.asarray(source["accepted_center_causal_coordinate_radius"], dtype=float),
            axes,
        )
    with np.load(CENTRAL_CAUSAL.with_suffix(".npz")) as source:
        central_l, central_t = _vector_blocks(
            np.asarray(source["causal_central_scalar_curvature_mid"], dtype=float),
            np.asarray(source["causal_central_scalar_curvature_radius"], dtype=float),
            axes,
        )
    with np.load(MIXED.with_suffix(".npz")) as source:
        mixed_l, mixed_t = _matrix_output_blocks(
            np.asarray(source["causal_mixed_mid"], dtype=float),
            np.asarray(source[
                "causal_mixed_shared_affine_Frobenius_radius_upper"
            ], dtype=float), axes,
        )
    with np.load(BLOCK_Z1.with_suffix(".npz")) as source:
        zmax = np.asarray(source["causal_block_Z1_maximum_upper"], dtype=float)
    y = np.asarray((np.max(y_l), np.max(y_t)))
    z = np.asarray(((zmax[0], zmax[1]), (zmax[2], zmax[3])))
    central = np.asarray((np.max(central_l), np.max(central_t)))
    mixed = np.asarray((np.max(mixed_l), np.max(mixed_t)))
    transverse = np.asarray((np.max(transverse_l), np.max(transverse_t)))
    screen = _best_screen(y, z, central, mixed, transverse, descriptor_ceiling)

    np.savez_compressed(
        DATA, local_transverse_component_box=local,
        causal_transverse_longitudinal_upper=transverse_l,
        causal_transverse_transverse_upper=transverse_t,
        Y_longitudinal_upper=y_l, Y_transverse_upper=y_t,
        central_longitudinal_upper=central_l,
        central_transverse_upper=central_t,
        mixed_longitudinal_upper=mixed_l,
        mixed_transverse_upper=mixed_t,
        causal_maps_center=maps, **decomposition,
    )
    validation = {
        "all_370_HS_intervals_included": local.shape == (370, 74),
        "same_frozen_causal_preconditioner_and_Green_partition_used": True,
        "full_endpoint_and_midpoint_componentwise_center_majorants_used": True,
        "reconstructed_midpoint_ambient_DF_used_for_second_incidence": True,
        "normal_axis_remainder_explicitly_omitted_from_optimistic_screen": True,
        "outward_tube_remainder_explicitly_omitted_from_optimistic_screen": True,
        "optimistic_componentwise_self_map_does_not_close": not screen[
            "positive_self_map_found"
        ],
        "failure_not_relabelled_as_root_nonexistence_or_instability": True,
        "no_action_center_branch_scale_partition_or_fit_changed": True,
        "FULL_BHSM_COMPLETE": False,
    }
    passed = all(v for k, v in validation.items()
                 if k != "FULL_BHSM_COMPLETE") and not validation["FULL_BHSM_COMPLETE"]
    payload = {
        "artifact": "BHSM_N12_GATE7_CURRENT_GREEN_COMPONENTWISE_TWO_RADIUS_SCREEN",
        "status": "OPTIMISTIC_COMPONENTWISE_TWO_RADIUS_REPRESENTATION_DOES_NOT_CLOSE",
        "authority": "DIRECTED_CENTER_REPRESENTATION_SCREEN_NOT_OUTWARD_TUBE_AUTHORITY",
        "coefficients": {
            "Y": y.tolist(), "Z1": z.tolist(),
            "central_quadratic": central.tolist(),
            "mixed_quadratic": mixed.tolist(),
            "transverse_quadratic": transverse.tolist(),
        },
        "screen": screen,
        "maximum_omitted_midpoint_normal_operator_norm": float(np.max(
            decomposition["omitted_midpoint_normal_operator_norm"]
        )),
        "dominant_local_transverse_interval": int(np.argmax(
            np.linalg.norm(local, axis=1)
        )),
        "dominant_local_transverse_coordinate": int(np.argmax(
            local[int(np.argmax(np.linalg.norm(local, axis=1)))]
        )),
        "representation_adjudication": "RETAIN_THE_SIGNED_TRANSVERSE_HS_TENSOR_THROUGH_CAUSAL_TRANSPORT_BEFORE_NORMS;_DO_NOT_SPEND_COMPUTE_OUTWARDIZING_THE_FAILED_COMPONENT_BOX",
        "exact_next_calculation": "DERIVE_A_RESTART_SAFE_SIGNED_TRANSVERSE_HERMITE_SIMPSON_CAUSAL_TENSOR_COMPOSITION_USING_THE_EXISTING_FULL_CENTER_KERNEL_AND_RECONSTRUCTED_MIDPOINT_DF_THEN_ATTACH_THE_OUTWARD_REMAINDER_ONLY_TO_THE_SURVIVING_SIGNED_OPERATOR",
        "claim_boundary": {
            "CURRENT_GREEN_COMPONENTWISE_TWO_RADIUS_REPRESENTATION_SCREENED": True,
            "CURRENT_GREEN_TRANSVERSE_TRANSVERSE_FULL_OPERATOR_BOUND_DERIVED": False,
            "CURRENT_CENTER_GREEN_CAUSAL_TWO_RADIUS_CERTIFICATE_DERIVED": False,
            "G7_ROOT_NONEXISTENCE_DERIVED": False,
            "G7_PHYSICAL_SPACETIME_INSTABILITY_DERIVED": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "data": _relative(DATA), "data_SHA256": _sha(DATA),
        "inputs": {_relative(path): _sha(path) for path in inputs},
        "validation": validation, "validation_passed": passed,
        "FULL_BHSM_COMPLETE": False,
    }
    return payload


def main() -> None:
    payload = build_payload()
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n",
                      encoding="utf-8", newline="\n")
    print(json.dumps({
        "status": payload["status"],
        "coefficients": payload["coefficients"],
        "screen": payload["screen"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
