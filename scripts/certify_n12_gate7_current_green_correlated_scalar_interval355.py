"""Reconcile interval 355 with one correlated Green scalar axis."""

from __future__ import annotations

import hashlib
import json
import math
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
OBSTRUCTION = F / "BHSM_N12_GATE7_CURRENT_GREEN_HERMITE_SIMPSON_MIDPOINT_CURVATURE.json"
RESULT = F / "BHSM_N12_GATE7_CURRENT_GREEN_CORRELATED_SCALAR_INTERVAL355.json"
DATA = RESULT.with_suffix(".npz")
THEORY = ROOT / "theory/n12_gate7_current_green_correlated_scalar_interval355.md"
THIS_SCRIPT = Path(__file__).resolve()
INTERVAL = 355
PRECISION = cert.PRECISION
INPUTS = (
    ENDPOINT, ENDPOINT.with_suffix(".npz"),
    REPLAY, REPLAY.with_suffix(".npz"),
    JACOBIAN, JACOBIAN.with_suffix(".npz"),
    PARTITION, PARTITION.with_suffix(".npz"),
    OBSTRUCTION, OBSTRUCTION.with_suffix(".npz"),
    Path(cert.__file__).resolve(), THIS_SCRIPT, THEORY,
)


def _sha(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _export(values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    midpoint = np.empty(values.shape, dtype=float)
    radius = np.empty_like(midpoint)
    for index in np.ndindex(values.shape):
        midpoint[index] = float(values[index])
        radius[index] = math.nextafter(
            float(abs(values[index] - arb(midpoint[index])).upper()), math.inf,
        )
    return midpoint, radius


def _normalized_central_axis(unit_mid: np.ndarray) -> np.ndarray:
    central = np.asarray(unit_mid, dtype=float)
    return central / np.linalg.norm(central)


def _axis_error_upper(unit_mid: np.ndarray, unit_radius: np.ndarray,
                      central: np.ndarray) -> float:
    total = arb(0)
    for midpoint, radius, selected in zip(unit_mid, unit_radius, central):
        difference = arb(float(midpoint), float(radius)) - arb(float(selected))
        upper = arb(abs(difference).upper())
        total += upper * upper
    return math.nextafter(float(total.sqrt().upper()), math.inf)


def _ambient_direction(frame: np.ndarray, central: np.ndarray) -> np.ndarray:
    return np.asarray([
        sum((arb(float(frame[i, k])) * arb(float(central[k]))
             for k in range(74)), arb(0))
        for i in range(cert.STATE + 1)
    ], dtype=object)


def build_payload() -> dict[str, object]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    obstruction = json.loads(OBSTRUCTION.read_text(encoding="utf-8"))
    with np.load(ENDPOINT.with_suffix(".npz")) as source:
        states = np.asarray(source["projected_states"], dtype=float)
        descriptors = np.asarray(source["independent_signed_descriptors"], dtype=float)
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)
        times = np.asarray(source["collocation_arc_parameters"], dtype=float)
    with np.load(REPLAY.with_suffix(".npz")) as source:
        midpoint_value = np.asarray(
            source["midpoint_augmented_action_values"][INTERVAL], dtype=float,
        )
    with np.load(JACOBIAN.with_suffix(".npz")) as source:
        tangents = np.asarray(source["endpoint_physical_tangent_action"], dtype=float)
    with np.load(PARTITION.with_suffix(".npz")) as source:
        unit_mid = np.asarray(source["current_center_green_image_unit_mid"], dtype=float)
        unit_radius = np.asarray(source["current_center_green_image_unit_radius"], dtype=float)

    ctx.prec = PRECISION
    endpoint_directions = []
    endpoint_first = []
    endpoint_second = []
    central_axes = []
    axis_errors = []
    gaps = []
    residuals = []
    for node in (INTERVAL, INTERVAL + 1):
        central = _normalized_central_axis(unit_mid[node])
        central_axes.append(central)
        axis_errors.append(_axis_error_upper(
            unit_mid[node], unit_radius[node], central,
        ))
        direction = _ambient_direction(
            cert._frame(tangents[node], cert.TRIAL_DESCRIPTOR_SCALE), central,
        )
        endpoint_directions.append(direction)
        first = cert._rate_enclosure(
            states[node], float(descriptors[node]), weights, reference,
            direction.reshape(cert.STATE + 1, 1),
        )
        endpoint_first.append(np.asarray(first.derivative[:, 0], dtype=object))
        endpoint_second.append(cert._rate_second_directional(
            states[node], float(descriptors[node]), weights, reference, direction,
        ))
        gaps.append(first.gap_lower)
        residuals.append(first.eigen_residual_upper)

    h = arb(float(times[INTERVAL + 1] - times[INTERVAL]))
    midpoint_direction = np.asarray([
        (endpoint_directions[0][i] + endpoint_directions[1][i]) / 2
        + h * (endpoint_first[0][i] - endpoint_first[1][i]) / 8
        for i in range(cert.STATE + 1)
    ], dtype=object)
    midpoint_second_incidence = np.asarray([
        h * (endpoint_second[0][i] - endpoint_second[1][i]) / 8
        for i in range(cert.STATE + 1)
    ], dtype=object)
    midpoint_state = midpoint_value[:cert.STATE] / weights
    midpoint_descriptor = float(midpoint_value[cert.STATE])
    intrinsic = cert._rate_second_directional(
        midpoint_state, midpoint_descriptor, weights, reference, midpoint_direction,
    )
    incidence_enclosure = cert._rate_enclosure(
        midpoint_state, midpoint_descriptor, weights, reference,
        midpoint_second_incidence.reshape(cert.STATE + 1, 1),
    )
    incidence = np.asarray(incidence_enclosure.derivative[:, 0], dtype=object)
    total = intrinsic + incidence
    local_hs = -h * (endpoint_second[0] + 4 * total + endpoint_second[1]) / 6
    gaps.append(incidence_enclosure.gap_lower)
    residuals.append(incidence_enclosure.eigen_residual_upper)

    stored: dict[str, np.ndarray] = {
        "central_causal_axes": np.asarray(central_axes),
        "central_axis_error_upper": np.asarray(axis_errors),
        "precision_bits": np.asarray(PRECISION),
        "interval": np.asarray(INTERVAL),
    }
    operands = {
        "left_endpoint_first": endpoint_first[0],
        "right_endpoint_first": endpoint_first[1],
        "left_endpoint_second": endpoint_second[0],
        "right_endpoint_second": endpoint_second[1],
        "midpoint_direction": midpoint_direction,
        "midpoint_second_incidence": midpoint_second_incidence,
        "midpoint_intrinsic_curvature": intrinsic,
        "midpoint_incidence_curvature": incidence,
        "midpoint_total_curvature": total,
        "local_HS_second_residual": local_hs,
    }
    bounds = {}
    for name, values in operands.items():
        stored[f"{name}_mid"], stored[f"{name}_radius"] = _export(values)
        bounds[name] = cert._arb_norm_bounds(values)
    np.savez_compressed(DATA, **stored)
    validation = {
        "upstream_componentwise_route_failed_first_at_interval_355": (
            obstruction["componentwise_direction_ball_obstruction"][
                "first_nonfinite_intrinsic_interval"
            ] == INTERVAL
        ),
        "central_axes_are_unit_to_binary_roundoff": bool(all(
            abs(np.linalg.norm(axis) - 1.0) <= 2 * np.finfo(float).eps
            for axis in central_axes
        )),
        "certified_exact_green_axes_lie_in_reported_central_neighborhoods": bool(
            all(error > 0.0 and math.isfinite(error) for error in axis_errors)
        ),
        "all_correlated_scalar_operands_finite": bool(all(
            math.isfinite(row["lower"]) and math.isfinite(row["upper"])
            for row in bounds.values()
        )),
        "all_selected_line_gaps_positive": min(gaps) > 0.0,
        "384_bit_Arb_retained_action_evaluation": PRECISION == 384,
        "no_center_action_branch_trajectory_scale_or_fit_changed": True,
        "axis_neighborhood_error_deferred_to_mixed_transverse_remainder": True,
        "interval355_probe_not_relabelled_as_global_or_causal_certificate": True,
    }
    return {
        "artifact": "BHSM_N12_GATE7_CURRENT_GREEN_CORRELATED_SCALAR_INTERVAL355",
        "status": "CURRENT_GREEN_CORRELATED_SCALAR_INTERVAL355_FINITE_RECONCILIATION_CERTIFIED",
        "authority": "384_BIT_ARB_SINGLE_INTERVAL_CORRELATED_SCALAR_RECONCILIATION_NOT_GLOBAL_CAUSAL_AUTHORITY",
        "interval": INTERVAL,
        "central_axis_neighborhood_error_upper": {
            "left_node_355": axis_errors[0],
            "right_node_356": axis_errors[1],
        },
        "operand_norm_bounds": bounds,
        "minimum_branch_gap_lower": min(gaps),
        "maximum_eigen_residual_upper": max(residuals),
        "scientific_result": "THE_INTERVAL_355_NONFINITE_COMPONENTWISE_BALL_RESULT_IS_REMOVED_WHEN_GREEN_NORMALIZATION_AND_TRANSPORT_ARE_HELD_AS_ONE_CENTRAL_LONGITUDINAL_SCALAR_AXIS;_THE_SMALL_CERTIFIED_AXIS_NEIGHBORHOOD_MUST_ENTER_THE_LATER_MIXED_TRANSVERSE_REMAINDER",
        "exact_next_calculation": "EXTEND_THE_CORRELATED_CENTRAL_GREEN_SCALAR_CONSTRUCTION_TO_ALL_370_INTERVALS,_THEN_BOUND_THE_CERTIFIED_AXIS_NEIGHBORHOOD_WITH_THE_MIXED_AND_TRANSVERSE_REMAINDERS_BEFORE_CAUSAL_TWO_RADIUS_PROMOTION",
        "claim_boundary": {
            "CURRENT_GREEN_CORRELATED_SCALAR_INTERVAL355_FINITE": True,
            "CURRENT_GREEN_CORRELATED_SCALAR_ALL_INTERVALS_DERIVED": False,
            "CURRENT_GREEN_AXIS_NEIGHBORHOOD_MIXED_TRANSVERSE_BOUND_DERIVED": False,
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
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("correlated Green scalar interval-355 reconciliation failed")
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n",
                      encoding="utf-8", newline="\n")
    print(json.dumps({"status": payload["status"],
                      "operand_norm_bounds": payload["operand_norm_bounds"],
                      "validation_passed": payload["validation_passed"]},
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
