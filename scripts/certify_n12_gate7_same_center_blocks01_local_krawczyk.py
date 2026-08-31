"""Certify the accepted Gate-7 curvature-owner blocks by local Krawczyk.

The proof center is the single frozen-preconditioner Newton correction of the
accepted replay center on nodes 1 and 2.  Its containment in the previously
certified correlated branch-24 domain is checked before any interval solve.
The physical action, trajectory, causal frames, branch, mesh, and parameters
are unchanged; the recenter is only an equivalent local proof coordinate.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np
from flint import arb, arb_mat, ctx


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import certify_n12_gate7_accepted_replay_center_outward_74d as accepted  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
SPECTRAL = BASE / "BHSM_N12_GATE7_SAME_CENTER_BLOCKS01_CORRELATED_SPECTRAL_DOMAIN.json"
RESULT = BASE / "BHSM_N12_GATE7_SAME_CENTER_BLOCKS01_LOCAL_KRAWCZYK.json"
THIS_SCRIPT = Path(__file__).resolve()
RECENTER_RADIUS_RESERVE_FACTOR = 1.25
TRANSVERSE_RESERVE_FRACTION = 0.01
WORK = BASE / ".same_center_blocks01_local_krawczyk_work"


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load_arb_array(path: Path, key: str) -> np.ndarray:
    with np.load(path) as source:
        return accepted._parse_arb_string_array(source[key])


def _arb_array(matrix: arb_mat) -> np.ndarray:
    return accepted._array(matrix)


def _arb_mat(values: np.ndarray) -> arb_mat:
    return accepted._arb_mat_from_array(np.asarray(values, dtype=object))


def _midpoint_array(values: np.ndarray) -> np.ndarray:
    array = np.asarray(values, dtype=object)
    result = np.empty(array.shape, dtype=float)
    for index in np.ndindex(array.shape):
        result[index] = float(array[index])
    return result


def _frobenius_upper(matrix: arb_mat) -> float:
    return accepted._norm_upper(_arb_array(matrix).ravel())


def _vector_pair_norm_upper(left: arb_mat, right: arb_mat) -> float:
    total = arb(0)
    for vector in (left, right):
        for index in range(vector.nrows()):
            total += vector[index, 0] ** 2
    return math.nextafter(float(total.sqrt().upper()), math.inf)


def _contains_zero(matrix: arb_mat) -> int:
    return sum(
        not matrix[i, j].contains(0)
        for i in range(matrix.nrows())
        for j in range(matrix.ncols())
    )


def _initial_newton_coordinates(
    centers: np.ndarray,
    times: np.ndarray,
    tangents: np.ndarray,
    old_left: np.ndarray,
    old_right: np.ndarray,
) -> list[arb_mat]:
    coordinate = arb_mat(74, 1)
    coordinates = [arb_mat(74, 1)]
    for interval in range(2):
        h = accepted._a(float(times[interval + 1] - times[interval]))
        test = accepted._arb_matrix(accepted._frame(
            tangents[interval + 1], accepted.TEST_DESCRIPTOR_SCALE,
        ).T)
        trial = accepted._arb_matrix(accepted._frame(
            tangents[interval], accepted.TRIAL_DESCRIPTOR_SCALE,
        ))
        inverse = accepted._arb_matrix(old_right[interval]).inv()
        e0 = _arb_mat(_load_arb_array(
            accepted.WORK / f"endpoint_{interval:03d}.npz", "value_arb",
        ))
        e1 = _arb_mat(_load_arb_array(
            accepted.WORK / f"endpoint_{interval + 1:03d}.npz", "value_arb",
        ))
        em = _arb_mat(_load_arb_array(
            accepted.WORK / f"midpoint_{interval:03d}.npz", "value_arb",
        ))
        residual = (
            accepted._arb_vector(centers[interval + 1])
            - accepted._arb_vector(centers[interval])
            - h * (e0 + 4 * em + e1) / 6
        )
        coordinate = -inverse * (
            test * residual
            + test * accepted._arb_matrix(old_left[interval]) * trial * coordinate
        )
        coordinates.append(coordinate)
    return coordinates


def _point_rate(
    augmented_action: np.ndarray,
    directions: np.ndarray,
    weights: np.ndarray,
    reference: np.ndarray,
) -> accepted.RateEnclosure:
    return accepted._rate_enclosure(
        augmented_action[:98] / weights,
        float(augmented_action[98]),
        weights,
        reference,
        directions,
    )


def _cached_point_rate(
    label: str,
    augmented_action: np.ndarray,
    directions: np.ndarray,
    weights: np.ndarray,
    reference: np.ndarray,
) -> accepted.RateEnclosure:
    """Reuse an exact point evaluation only for identical binary inputs."""
    WORK.mkdir(parents=True, exist_ok=True)
    target = WORK / f"{label}.npz"
    center = np.asarray(augmented_action, dtype=float)
    direction_mid = _midpoint_array(np.asarray(directions, dtype=object))
    digest = hashlib.sha256()
    digest.update(center.tobytes())
    digest.update(direction_mid.tobytes())
    signature = digest.hexdigest().upper()
    if target.is_file():
        with np.load(target) as source:
            if str(source["signature"]) == signature:
                return accepted.RateEnclosure(
                    accepted._parse_arb_string_array(source["value_arb"]),
                    accepted._parse_arb_string_array(source["derivative_arb"]),
                    float(source["gap_lower"]),
                    float(source["eigen_residual_upper"]),
                    None,
                )
    result = _point_rate(
        augmented_action, directions, weights, reference,
    )
    np.savez_compressed(
        target,
        signature=np.asarray(signature),
        value_arb=accepted._arb_string_array(result.value),
        derivative_arb=accepted._arb_string_array(result.derivative),
        gap_lower=np.asarray(result.gap_lower),
        eigen_residual_upper=np.asarray(result.eigen_residual_upper),
        precision_bits=np.asarray(accepted.PRECISION),
    )
    return result


def _midpoint_center_and_directions(
    left_center: np.ndarray,
    right_center: np.ndarray,
    left_rate: accepted.RateEnclosure,
    right_rate: accepted.RateEnclosure,
    left_frame: np.ndarray,
    right_frame: np.ndarray,
    h: arb,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    left_value = np.asarray(left_rate.value, dtype=object)
    right_value = np.asarray(right_rate.value, dtype=object)
    exact_center = np.asarray([
        accepted._a(0.5 * (left_center[i] + right_center[i]))
        + h * (left_value[i] - right_value[i]) / 8
        for i in range(99)
    ], dtype=object)
    binary_center = _midpoint_array(exact_center)
    center_rounding = np.asarray([
        accepted._center_radius(exact_center[i] - accepted._a(binary_center[i]))[1]
        for i in range(99)
    ], dtype=float)
    left_direction = np.empty((99, 74), dtype=object)
    right_direction = np.empty_like(left_direction)
    for i in range(99):
        for k in range(74):
            left_direction[i, k] = (
                accepted._a(0.5 * left_frame[i, k])
                + h * left_rate.derivative[i, k] / 8
            )
            right_direction[i, k] = (
                accepted._a(0.5 * right_frame[i, k])
                - h * right_rate.derivative[i, k] / 8
            )
    return binary_center, center_rounding, left_direction, right_direction


def _tube_rate(
    center: np.ndarray,
    center_rounding: np.ndarray,
    directions: np.ndarray,
    coordinate_radii: np.ndarray,
    weights: np.ndarray,
    reference: np.ndarray,
) -> accepted.RateEnclosure:
    directions = np.asarray(directions, dtype=object)
    coordinate_radii = np.asarray(coordinate_radii, dtype=float)
    if directions.shape[1] != coordinate_radii.size:
        raise ValueError("direction/radius dimensions differ")
    augmented_radius = np.asarray(center_rounding, dtype=float).copy()
    for row in range(directions.shape[0]):
        total = arb(0)
        for column in range(directions.shape[1]):
            total += abs(directions[row, column]) * accepted._a(
                float(coordinate_radii[column])
            )
        augmented_radius[row] = math.nextafter(
            augmented_radius[row] + float(total.upper()), math.inf,
        )
    print(json.dumps({
        "tube_maximum_augmented_action_radius": float(np.max(augmented_radius)),
        "tube_maximum_raw_state_radius": float(np.max(
            augmented_radius[:98] / weights
        )),
        "tube_descriptor_radius": float(augmented_radius[98]),
    }), flush=True)
    state_ball = np.asarray([
        arb(
            float(center[index] / weights[index]),
            float(augmented_radius[index] / weights[index]),
        )
        for index in range(98)
    ], dtype=object)
    descriptor_ball = arb(float(center[98]), float(augmented_radius[98]))
    return accepted._rate_enclosure(
        state_ball, descriptor_ball, weights, reference, directions,
    )


def _cached_tube_rate(
    label: str,
    center: np.ndarray,
    center_rounding: np.ndarray,
    directions: np.ndarray,
    coordinate_radii: np.ndarray,
    weights: np.ndarray,
    reference: np.ndarray,
) -> accepted.RateEnclosure:
    WORK.mkdir(parents=True, exist_ok=True)
    target = WORK / f"{label}.npz"
    digest = hashlib.sha256()
    digest.update(np.asarray(center, dtype=float).tobytes())
    digest.update(np.asarray(center_rounding, dtype=float).tobytes())
    digest.update(np.asarray(coordinate_radii, dtype=float).tobytes())
    direction_array = np.asarray(directions, dtype=object)
    for value in direction_array.ravel():
        digest.update(
            (value.str(140) if isinstance(value, arb) else float(value).hex())
            .encode("ascii")
        )
        digest.update(b"\0")
    signature = digest.hexdigest().upper()
    if target.is_file():
        with np.load(target) as source:
            if str(source["signature"]) == signature:
                result = accepted.RateEnclosure(
                    accepted._parse_arb_string_array(source["value_arb"]),
                    accepted._parse_arb_string_array(source["derivative_arb"]),
                    float(source["gap_lower"]),
                    float(source["eigen_residual_upper"]),
                    None,
                )
                _require_finite_rate(result, label)
                return result
    result = _tube_rate(
        center, center_rounding, directions, coordinate_radii,
        weights, reference,
    )
    _require_finite_rate(result, label)
    np.savez_compressed(
        target,
        signature=np.asarray(signature),
        value_arb=accepted._arb_string_array(result.value),
        derivative_arb=accepted._arb_string_array(result.derivative),
        gap_lower=np.asarray(result.gap_lower),
        eigen_residual_upper=np.asarray(result.eigen_residual_upper),
        precision_bits=np.asarray(accepted.PRECISION),
    )
    return result


def _require_finite_rate(
    result: accepted.RateEnclosure, label: str,
) -> None:
    values = np.asarray(result.value, dtype=object).ravel()
    derivatives = np.asarray(result.derivative, dtype=object).ravel()
    if not all(value.is_finite() for value in (*values, *derivatives)):
        raise ArithmeticError(
            f"{label}: interval rate/value enclosure became indeterminate"
        )


def _scaled_infinity_upper(matrix: arb_mat, radii: np.ndarray) -> float:
    radii = np.asarray(radii, dtype=float)
    maximum = 0.0
    for row in range(matrix.nrows()):
        total = arb(0)
        for column in range(matrix.ncols()):
            total += abs(matrix[row, column]) * accepted._a(
                float(radii[column])
            )
        value = math.nextafter(
            float(total.upper()) / float(radii[row]), math.inf,
        )
        maximum = max(maximum, value)
    return maximum


def _componentwise_krawczyk(
    correction: arb_mat, error: arb_mat, radii: np.ndarray,
) -> tuple[float, float, int]:
    maximum_ratio = 0.0
    minimum_margin = math.inf
    failures = 0
    for row in range(error.nrows()):
        image = arb(0)
        for column in range(error.ncols()):
            image += abs(error[row, column]) * accepted._a(
                float(radii[column])
            )
        total = abs(correction[row, 0]) + image
        upper = math.nextafter(float(total.upper()), math.inf)
        ratio = math.nextafter(upper / float(radii[row]), math.inf)
        margin = math.nextafter(float(radii[row]) - upper, -math.inf)
        maximum_ratio = max(maximum_ratio, ratio)
        minimum_margin = min(minimum_margin, margin)
        failures += margin <= 0.0
    return maximum_ratio, minimum_margin, failures


def _local_blocks(
    *,
    endpoint_rates: list[accepted.RateEnclosure],
    midpoint_rates: list[accepted.RateEnclosure],
    centers: np.ndarray,
    times: np.ndarray,
    tangents: np.ndarray,
    old_left: np.ndarray,
    old_right: np.ndarray,
) -> tuple[arb_mat, arb_mat, arb_mat]:
    residual_coordinates: list[arb_mat] = []
    c_values: list[arb_mat] = []
    dl_values: list[arb_mat] = []
    dr_values: list[arb_mat] = []
    prior = arb_mat(74, 1)
    for interval in range(2):
        h = accepted._a(float(times[interval + 1] - times[interval]))
        test = accepted._arb_matrix(accepted._frame(
            tangents[interval + 1], accepted.TEST_DESCRIPTOR_SCALE,
        ).T)
        trial_left = accepted._arb_matrix(accepted._frame(
            tangents[interval], accepted.TRIAL_DESCRIPTOR_SCALE,
        ))
        trial_right = accepted._arb_matrix(accepted._frame(
            tangents[interval + 1], accepted.TRIAL_DESCRIPTOR_SCALE,
        ))
        frozen_left = accepted._arb_matrix(old_left[interval])
        frozen_right = accepted._arb_matrix(old_right[interval])
        inverse = frozen_right.inv()

        e0 = _arb_mat(np.asarray(endpoint_rates[interval].value, dtype=object))
        e1 = _arb_mat(np.asarray(endpoint_rates[interval + 1].value, dtype=object))
        em = _arb_mat(np.asarray(midpoint_rates[interval].value, dtype=object))
        residual = (
            accepted._arb_vector(centers[interval + 1])
            - accepted._arb_vector(centers[interval])
            - h * (e0 + 4 * em + e1) / 6
        )
        prior = -inverse * (
            test * residual + test * frozen_left * trial_left * prior
        )
        residual_coordinates.append(prior)

        midpoint_derivative = np.asarray(
            midpoint_rates[interval].derivative, dtype=object,
        )
        if interval == 0 and midpoint_derivative.shape[1] == 74:
            midpoint_left = arb_mat(99, 74)
            midpoint_right = _arb_mat(midpoint_derivative)
        else:
            midpoint_left = _arb_mat(midpoint_derivative[:, :74])
            midpoint_right = _arb_mat(midpoint_derivative[:, 74:])
        endpoint_left = _arb_mat(np.asarray(
            endpoint_rates[interval].derivative, dtype=object,
        ))
        endpoint_right = _arb_mat(np.asarray(
            endpoint_rates[interval + 1].derivative, dtype=object,
        ))
        new_left = -trial_left - h * (endpoint_left + 4 * midpoint_left) / 6
        new_right = trial_right - h * (4 * midpoint_right + endpoint_right) / 6
        frozen_left_reduced = test * frozen_left * trial_left
        c_values.append(inverse * frozen_left_reduced)
        dl_values.append(inverse * (frozen_left_reduced - test * new_left))
        dr_values.append(inverse * (frozen_right - test * new_right))

    error = arb_mat(148, 148)
    for i in range(74):
        for j in range(74):
            error[i, j] = dr_values[0][i, j]
            error[74 + i, j] = (
                -c_values[1] * dr_values[0] + dl_values[1]
            )[i, j]
            error[74 + i, 74 + j] = dr_values[1][i, j]
    correction = arb_mat(148, 1)
    for i in range(74):
        correction[i, 0] = residual_coordinates[0][i, 0]
        correction[74 + i, 0] = residual_coordinates[1][i, 0]
    return correction, error, c_values[1]


def main() -> None:
    ctx.prec = accepted.PRECISION
    spectral = json.loads(SPECTRAL.read_text(encoding="utf-8"))
    if spectral.get("validation_passed") is not True:
        raise RuntimeError("certified correlated blocks 0--1 domain required")
    required = [
        SPECTRAL,
        accepted.ENDPOINT,
        accepted.ENDPOINT.with_suffix(".npz"),
        accepted.OLD_JACOBIAN,
        accepted.OLD_JACOBIAN.with_suffix(".npz"),
        accepted.PRECONDITIONER,
        accepted.PRECONDITIONER.with_suffix(".npz"),
    ] + [
        accepted.WORK / f"endpoint_{index:03d}.npz" for index in range(3)
    ] + [
        accepted.WORK / f"midpoint_{index:03d}.npz" for index in range(2)
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"missing {len(missing)} local proof inputs")

    with np.load(accepted.ENDPOINT.with_suffix(".npz")) as source:
        states = np.asarray(source["projected_states"], dtype=float)
        descriptors = np.asarray(
            source["independent_signed_descriptors"], dtype=float,
        )
        weights = np.asarray(source["state_weights"], dtype=float)
        times = np.asarray(source["collocation_arc_parameters"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)
    original_centers = np.column_stack((states * weights[None, :], descriptors))
    with np.load(accepted.OLD_JACOBIAN.with_suffix(".npz")) as source:
        tangents = np.asarray(
            source["endpoint_physical_tangent_action"], dtype=float,
        )
    with np.load(accepted.PRECONDITIONER.with_suffix(".npz")) as source:
        old_left = np.asarray(source["left_Newton_blocks"], dtype=float)
        old_right = np.asarray(
            source["reduced_right_Newton_blocks"], dtype=float,
        )
    frames = [
        accepted._frame(tangents[index], accepted.TRIAL_DESCRIPTOR_SCALE)
        for index in range(3)
    ]

    initial = _initial_newton_coordinates(
        original_centers, times, tangents, old_left, old_right,
    )
    initial_mid = [
        np.asarray([float(value[i, 0]) for i in range(74)], dtype=float)
        for value in initial
    ]
    recentered = original_centers[:3].copy()
    for index in (1, 2):
        recentered[index] += frames[index] @ initial_mid[index]
    displacement_pair_upper = _vector_pair_norm_upper(initial[1], initial[2])
    spectral_radius = float(spectral["local_domain"]["action_coordinate_radius"])
    if not displacement_pair_upper < spectral_radius:
        raise ArithmeticError("proof recenter leaves certified spectral domain")

    endpoint_center_rates: list[accepted.RateEnclosure] = []
    endpoint_center_rates.append(accepted.RateEnclosure(
        _load_arb_array(accepted.WORK / "endpoint_000.npz", "value_arb"),
        _load_arb_array(accepted.WORK / "endpoint_000.npz", "derivative_arb"),
        float(np.load(accepted.WORK / "endpoint_000.npz")["gap_lower"]),
        float(np.load(accepted.WORK / "endpoint_000.npz")["eigen_residual_upper"]),
        None,
    ))
    for index in (1, 2):
        print(json.dumps({"stage": "center_endpoint", "index": index}), flush=True)
        endpoint_center_rates.append(_cached_point_rate(
            f"center_endpoint_{index}",
            recentered[index], frames[index], weights, reference,
        ))

    midpoint_centers: list[np.ndarray] = []
    midpoint_rounding: list[np.ndarray] = []
    midpoint_left_directions: list[np.ndarray] = []
    midpoint_right_directions: list[np.ndarray] = []
    midpoint_center_rates: list[accepted.RateEnclosure] = []
    for interval in range(2):
        h = accepted._a(float(times[interval + 1] - times[interval]))
        center, rounding, left_direction, right_direction = (
            _midpoint_center_and_directions(
                recentered[interval], recentered[interval + 1],
                endpoint_center_rates[interval],
                endpoint_center_rates[interval + 1],
                frames[interval], frames[interval + 1], h,
            )
        )
        midpoint_centers.append(center)
        midpoint_rounding.append(rounding)
        midpoint_left_directions.append(left_direction)
        midpoint_right_directions.append(right_direction)
        active = right_direction if interval == 0 else np.column_stack((
            left_direction, right_direction,
        ))
        print(json.dumps({"stage": "center_midpoint", "index": interval}), flush=True)
        midpoint_center_rates.append(_cached_point_rate(
            f"center_midpoint_{interval}",
            center, active, weights, reference,
        ))

    center_correction, center_error, _ = _local_blocks(
        endpoint_rates=endpoint_center_rates,
        midpoint_rates=midpoint_center_rates,
        centers=recentered,
        times=times,
        tangents=tangents,
        old_left=old_left,
        old_right=old_right,
    )
    outward_y = accepted._vector_norm_upper(center_correction)
    correction_mid = np.asarray([
        float(center_correction[index, 0]) for index in range(148)
    ], dtype=float)
    maximum_component = float(np.max(np.abs(correction_mid)))
    transverse_floor = math.nextafter(
        TRANSVERSE_RESERVE_FRACTION * maximum_component / math.sqrt(148.0),
        math.inf,
    )
    coordinate_radii = np.nextafter(
        RECENTER_RADIUS_RESERVE_FACTOR * np.abs(correction_mid)
        + transverse_floor,
        math.inf,
    )
    proof_radius = math.nextafter(
        float(np.linalg.norm(coordinate_radii)), math.inf,
    )
    if not displacement_pair_upper + proof_radius < spectral_radius:
        raise ArithmeticError("root-containing proof ball leaves spectral domain")

    endpoint_tube_rates = [endpoint_center_rates[0]]
    midpoint_tube_rates: list[accepted.RateEnclosure] = []
    current_stage = "tube_endpoint_1"
    try:
        for index in (1, 2):
            current_stage = f"tube_endpoint_{index}"
            print(json.dumps({
                "stage": "tube_endpoint", "index": index,
                "maximum_coordinate_radius": float(np.max(
                    coordinate_radii[(index - 1) * 74:index * 74]
                )),
            }), flush=True)
            endpoint_tube_rates.append(_cached_tube_rate(
                current_stage,
                recentered[index], np.zeros(99), frames[index],
                coordinate_radii[(index - 1) * 74:index * 74],
                weights, reference,
            ))

        for interval in range(2):
            current_stage = f"tube_midpoint_{interval}"
            h = accepted._a(float(times[interval + 1] - times[interval]))
            left_direction = np.empty((99, 74), dtype=object)
            right_direction = np.empty_like(left_direction)
            for i in range(99):
                for k in range(74):
                    left_direction[i, k] = (
                        accepted._a(0.5 * frames[interval][i, k])
                        + h * endpoint_tube_rates[interval].derivative[i, k] / 8
                    )
                    right_direction[i, k] = (
                        accepted._a(0.5 * frames[interval + 1][i, k])
                        - h * endpoint_tube_rates[interval + 1].derivative[i, k] / 8
                    )
            active = right_direction if interval == 0 else np.column_stack((
                left_direction, right_direction,
            ))
            active_radii = (
                coordinate_radii[:74] if interval == 0 else coordinate_radii
            )
            print(json.dumps({
                "stage": "tube_midpoint", "index": interval,
                "maximum_coordinate_radius": float(np.max(active_radii)),
            }), flush=True)
            midpoint_tube_rates.append(_cached_tube_rate(
                current_stage,
                midpoint_centers[interval], midpoint_rounding[interval], active,
                active_radii, weights, reference,
            ))
    except (ArithmeticError, ZeroDivisionError) as exc:
        validation = {
            "same_action_center_branch_mesh_and_physics": True,
            "proof_recenter_strictly_inside_prior_correlated_spectral_domain": (
                displacement_pair_upper < spectral_radius
            ),
            "complete_root_containing_ball_inside_prior_spectral_domain": (
                displacement_pair_upper + proof_radius < spectral_radius
            ),
            "corrected_center_residual_is_finite": math.isfinite(outward_y),
            "direct_componentwise_interval_rate_enclosure_rejected": True,
            "indeterminate_interval_output_not_used_as_authority": True,
            "no_local_Z1_or_Z2_promoted": True,
            "no_root_nonexistence_or_physical_instability_inference": True,
        }
        payload = {
            "artifact": "BHSM_N12_GATE7_SAME_CENTER_BLOCKS01_LOCAL_KRAWCZYK",
            "owner": "SAME_CENTER_LOCAL_FORMATION_VIABILITY_CERTIFICATE",
            "result": (
                "LOCAL_OWNER_NOT_CERTIFIED__"
                "CORRELATED_CANCELLED_RATE_TAYLOR_MODEL_REQUIRED"
            ),
            "directive_terminal_classification": (
                "B_LOCAL_OWNER_FAILS_TO_CERTIFY"
            ),
            "requested_B_curvature_label_not_claimed": True,
            "segment": {
                "block_intervals": [0, 1],
                "endpoint_nodes": [0, 1, 2],
                "action_interval": [float(times[0]), float(times[2])],
                "proof_recenter_classification": (
                    "EQUIVALENT_PROOF_COORDINATE_TRANSFORMATION"
                ),
                "accepted_to_recentered_two_node_displacement_upper": (
                    displacement_pair_upper
                ),
                "prior_correlated_spectral_radius": spectral_radius,
                "root_containing_anisotropic_proof_radius": proof_radius,
                "anisotropic_transverse_floor": transverse_floor,
                "minimum_coordinate_radius": float(np.min(coordinate_radii)),
                "maximum_coordinate_radius": float(np.max(coordinate_radii)),
                "spectral_containment_margin": (
                    spectral_radius - displacement_pair_upper - proof_radius
                ),
            },
            "finite_center_evidence": {
                "corrected_center_local_Y_Euclidean_upper": outward_y,
                "prior_two_block_Newton_coordinate_norm_upper": float(
                    spectral["local_domain"][
                        "two_block_Newton_coordinate_norm_upper"
                    ]
                ),
                "residual_reduction_factor_lower": math.nextafter(
                    float(spectral["local_domain"][
                        "two_block_Newton_coordinate_norm_upper"
                    ]) / outward_y,
                    -math.inf,
                ),
            },
            "failed_enclosure": {
                "stage": current_stage,
                "exception_type": type(exc).__name__,
                "message": str(exc),
                "isotropic_root_containing_box": (
                    "REJECTED_BY_INTERVAL_EIGENLINE_RECIPROCAL"
                ),
                "anisotropic_root_containing_box": (
                    "REJECTED_AS_INDETERMINATE_NONFINITE_OUTPUT"
                ),
                "scientific_interpretation": (
                    "The direct componentwise state box loses correlated "
                    "cancelled-field and normalized-rate dependency."
                ),
            },
            "outward_operands": {
                "local_Y_Euclidean_upper": outward_y,
                "local_Z1": None,
                "local_Z2": None,
                "Krawczyk_self_map": None,
            },
            "exact_missing_operand": (
                "A correlation-preserving cancelled-rate Taylor/affine "
                "enclosure, or equivalent branchwise Kato-Schur rate-"
                "Jacobian variation, on this same corrected center."
            ),
            "claim_boundary": {
                "correlated_branch24_spectral_domain_blocks01": "CERTIFIED",
                "blocks01_local_root": "OPEN",
                "local_Z1_Z2_Krawczyk_inequality": "NOT_CERTIFIED",
                "root_nonexistence_claim": False,
                "physical_instability_claim": False,
                "Gate7": "OPEN",
                "FULL_BHSM_COMPLETE": False,
            },
            "provenance_SHA256": {
                str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path)
                for path in required
            },
            "validation": validation,
            "validation_passed": all(validation.values()),
            "FULL_BHSM_COMPLETE": False,
        }
        RESULT.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        print(json.dumps(payload, indent=2, sort_keys=True))
        return

    _, tube_error, _ = _local_blocks(
        endpoint_rates=endpoint_tube_rates,
        midpoint_rates=midpoint_tube_rates,
        centers=recentered,
        times=times,
        tangents=tangents,
        old_left=old_left,
        old_right=old_right,
    )
    variation = tube_error - center_error
    center_inclusion_failures = _contains_zero(variation)
    outward_z1 = _scaled_infinity_upper(center_error, coordinate_radii)
    derivative_variation = _scaled_infinity_upper(
        variation, coordinate_radii,
    )
    outward_z2 = math.nextafter(derivative_variation / proof_radius, math.inf)
    tube_error_upper = _scaled_infinity_upper(tube_error, coordinate_radii)
    scaled_y = math.nextafter(max(
        float(abs(center_correction[index, 0]).upper())
        * proof_radius / float(coordinate_radii[index])
        for index in range(148)
    ), math.inf)
    direct_self_map = math.nextafter(
        scaled_y + tube_error_upper * proof_radius, math.inf,
    )
    polynomial_self_map = math.nextafter(
        scaled_y + outward_z1 * proof_radius
        + outward_z2 * proof_radius**2,
        math.inf,
    )
    conservative_contraction = math.nextafter(
        outward_z1 + 2.0 * outward_z2 * proof_radius, math.inf,
    )
    minimum_gap = min(
        rate.gap_lower
        for rate in (*endpoint_tube_rates, *midpoint_tube_rates)
    )
    maximum_eigen_residual = max(
        rate.eigen_residual_upper
        for rate in (*endpoint_tube_rates, *midpoint_tube_rates)
    )
    minimum_descriptor = math.inf
    for index in (1, 2):
        descriptor_radius = math.nextafter(float(
            np.abs(frames[index][98])
            @ coordinate_radii[(index - 1) * 74:index * 74]
        ), math.inf)
        minimum_descriptor = min(
            minimum_descriptor,
            float(recentered[index, 98]) - descriptor_radius,
        )
    component_self_map_ratio, minimum_component_margin, component_failures = (
        _componentwise_krawczyk(
            center_correction, tube_error, coordinate_radii,
        )
    )
    validation = {
        "same_action_center_branch_mesh_and_physics": True,
        "proof_recenter_strictly_inside_prior_correlated_spectral_domain": (
            displacement_pair_upper < spectral_radius
        ),
        "complete_root_containing_ball_inside_prior_spectral_domain": (
            displacement_pair_upper + proof_radius < spectral_radius
        ),
        "all_interval_derivatives_contain_center_derivatives": (
            center_inclusion_failures == 0
        ),
        "selected_branch_uniformly_simple_on_local_ball": minimum_gap > 0.0,
        "descriptor_orientation_positive": minimum_descriptor > 0.0,
        "direct_Krawczyk_strict_self_map": (
            direct_self_map < proof_radius and component_failures == 0
        ),
        "radii_polynomial_strict_self_map": polynomial_self_map < proof_radius,
        "conservative_radii_contraction": conservative_contraction < 1.0,
        "causal_endpoint_order_preserved": bool(np.all(np.diff(times[:3]) > 0.0)),
        "no_root_nonexistence_or_physical_instability_inference": True,
    }
    passed = all(validation.values())
    payload = {
        "artifact": "BHSM_N12_GATE7_SAME_CENTER_BLOCKS01_LOCAL_KRAWCZYK",
        "owner": "SAME_CENTER_LOCAL_FORMATION_VIABILITY_CERTIFICATE",
        "result": (
            "LOCAL_CURVATURE_OWNER_BLOCKS01_CERTIFIED"
            if passed else "LOCAL_CURVATURE_OWNER_BLOCKS01_NOT_CERTIFIED"
        ),
        "segment": {
            "block_intervals": [0, 1],
            "endpoint_nodes": [0, 1, 2],
            "action_interval": [float(times[0]), float(times[2])],
            "proof_recenter_classification": (
                "EQUIVALENT_PROOF_COORDINATE_TRANSFORMATION"
            ),
            "accepted_to_recentered_two_node_displacement_upper": (
                displacement_pair_upper
            ),
            "prior_correlated_spectral_radius": spectral_radius,
            "local_proof_radius": proof_radius,
            "anisotropic_transverse_floor": transverse_floor,
            "minimum_coordinate_radius": float(np.min(coordinate_radii)),
            "maximum_coordinate_radius": float(np.max(coordinate_radii)),
            "spectral_containment_margin": (
                spectral_radius - displacement_pair_upper - proof_radius
            ),
        },
        "outward_operands": {
            "local_Y": outward_y,
            "local_Y_scaled_infinity": scaled_y,
            "local_Y_Euclidean_upper": outward_y,
            "local_Z1_scaled_infinity_upper": outward_z1,
            "local_Z2_fixed_radius_scaled_infinity_upper": outward_z2,
            "complete_interval_Krawczyk_derivative_scaled_infinity_upper": tube_error_upper,
            "derivative_variation_scaled_infinity_upper": derivative_variation,
            "direct_self_map_upper": direct_self_map,
            "radii_polynomial_self_map_upper": polynomial_self_map,
            "conservative_contraction_upper": conservative_contraction,
            "componentwise_self_map_maximum_ratio": component_self_map_ratio,
            "minimum_componentwise_self_map_margin": minimum_component_margin,
            "componentwise_self_map_failures": component_failures,
            "minimum_branch_gap_lower": minimum_gap,
            "maximum_eigen_residual_upper": maximum_eigen_residual,
            "minimum_descriptor_lower": minimum_descriptor,
            "center_inclusion_failures": center_inclusion_failures,
        },
        "relationship_to_global_obstruction": {
            "previous_global_Z2_lower": 3376470.2602736303,
            "previous_global_classification": (
                "PROOF_COORDINATE_CURVATURE_AMPLIFICATION"
            ),
            "complete_causal_transport_to_terminal_used_here": False,
            "same_local_physical_equations_used": True,
        },
        "claim_boundary": {
            "blocks01_local_root": "CERTIFIED" if passed else "OPEN",
            "node2_to_next_segment_handoff": "OPEN",
            "complete_formation_corridor_local_chain": "OPEN",
            "Gate7": "OPEN",
            "FULL_BHSM_COMPLETE": False,
        },
        "provenance_SHA256": {
            str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path)
            for path in required
        },
        "validation": validation,
        "validation_passed": passed,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({
        "result": payload["result"],
        "segment": payload["segment"],
        "outward_operands": payload["outward_operands"],
        "validation": validation,
        "validation_passed": passed,
        "artifact": str(RESULT),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
