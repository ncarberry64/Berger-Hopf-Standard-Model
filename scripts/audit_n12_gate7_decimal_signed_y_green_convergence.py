"""Replay Decimal Gauss-6/8 signed sources through one retained Green map."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

import numpy as np
from scipy.sparse.linalg import expm_multiply


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
SOURCE = BASE / "BHSM_N12_GATE7_DECIMAL_SIGNED_SOURCE_QUADRATURE_AUDIT.npz"
CENTER = BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.npz"
JACOBIAN = BASE / "BHSM_N12_C2_STOP_QUARTER_STEP_FINE_HYBRID_GRAPH_JACOBIAN_RECONNAISSANCE.npz"
TANGENT = BASE / "BHSM_N12_C2_STOP_QUARTER_STEP_PHYSICAL_TANGENT_TRANSFER_RECONNAISSANCE.npz"
Z2 = BASE / "BHSM_N12_GATE7_SELECTED_CONE_INTERNAL_RESPONSE_Z2.json"
RESULT = Path(os.environ.get(
    "BHSM_N12_GATE7_DECIMAL_GREEN_RESULT",
    str(BASE / "BHSM_N12_GATE7_DECIMAL_SIGNED_Y_GREEN_CONVERGENCE_AUDIT.json"),
))
if not RESULT.is_absolute():
    RESULT = ROOT / RESULT
DATA_RESULT = RESULT.with_suffix(".npz")


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _jacobian_at(time: float, times: np.ndarray, values: np.ndarray) -> np.ndarray:
    index = min(max(
        int(np.searchsorted(times, time, side="right") - 1), 0,
    ), times.size - 2)
    unit = (time - times[index]) / (times[index + 1] - times[index])
    return (1.0 - unit) * values[index] + unit * values[index + 1]


def _propagate(
    value: np.ndarray, left: float, right: float, maximum_step: float,
    jacobian_times: np.ndarray, jacobians: np.ndarray,
    slopes: np.ndarray, commutators: np.ndarray, magnus_order: int,
) -> np.ndarray:
    if right <= left:
        return value.copy()
    count = max(1, int(np.ceil((right - left) / maximum_step)))
    step = (right - left) / count
    result = value.copy()
    for substep in range(count):
        midpoint = left + (substep + 0.5) * step
        interval = min(max(
            int(np.searchsorted(jacobian_times, midpoint, side="right") - 1), 0,
        ), jacobian_times.size - 2)
        exponent = step * _jacobian_at(midpoint, jacobian_times, jacobians)
        if magnus_order >= 4:
            exponent = exponent - step**3 * commutators[interval] / 12.0
        if magnus_order >= 6:
            midpoint_generator = _jacobian_at(
                midpoint, jacobian_times, jacobians,
            )
            slope = slopes[interval]
            first = midpoint_generator @ slope - slope @ midpoint_generator
            second = midpoint_generator @ first - first @ midpoint_generator
            third = midpoint_generator @ second - second @ midpoint_generator
            slope_nested = slope @ first - first @ slope
            exponent = exponent + step**5 * (
                third / 720.0 - slope_nested / 240.0
            )
        result = expm_multiply(
            exponent, result,
        )
    return result


def _profile(
    *, order: int, sample_intervals: np.ndarray, sample_orders: np.ndarray,
    sample_indices: np.ndarray, residuals: np.ndarray, fine_times: np.ndarray,
    stop_fraction: float, macro_times: np.ndarray, tangents: np.ndarray,
    jacobian_times: np.ndarray, jacobians: np.ndarray, substeps: int,
    slopes: np.ndarray, commutators: np.ndarray, magnus_order: int,
) -> np.ndarray:
    nodes, weights = np.polynomial.legendre.leggauss(order)
    units = 0.5 * (nodes + 1.0)
    step = float(fine_times[1] - fine_times[0])
    maximum_step = step / substeps
    correction = np.zeros(98)
    profile = [correction.copy()]
    next_macro = 1
    interval_count = 370
    for interval in range(interval_count):
        mask = (sample_intervals == interval) & (sample_orders == order)
        local_indices = sample_indices[mask]
        local_residuals = residuals[mask]
        permutation = np.argsort(local_indices)
        local_residuals = local_residuals[permutation]
        if local_residuals.shape != (order, 98):
            raise RuntimeError("complete ordered Gauss source required")
        right_fraction = stop_fraction if interval == interval_count - 1 else 1.0
        duration = step * right_fraction
        left = float(fine_times[interval])
        right = left + duration
        source = np.zeros(98)
        for unit, weight, residual in zip(units, weights, local_residuals, strict=True):
            node_time = left + right_fraction * float(unit) * step
            source -= 0.5 * duration * float(weight) * _propagate(
                residual, node_time, right, maximum_step,
                jacobian_times, jacobians, slopes, commutators, magnus_order,
            )
        correction = _propagate(
            correction, left, right, maximum_step, jacobian_times, jacobians,
            slopes, commutators, magnus_order,
        ) + source
        if (
            next_macro < macro_times.size
            and abs(right - float(macro_times[next_macro])) < 1.0e-9
        ):
            target = tangents[next_macro]
            correction = target @ (target.T @ correction)
            next_macro += 1
        profile.append(correction.copy())
    if next_macro != macro_times.size:
        raise RuntimeError("fine grid did not land on every retained macro seam")
    return np.asarray(profile)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--propagator-substeps", type=int, default=16)
    parser.add_argument("--magnus-order", type=int, choices=(2, 4, 6), default=2)
    args = parser.parse_args()
    if args.propagator_substeps < 1:
        raise ValueError("positive propagator substep count required")
    with np.load(SOURCE) as data:
        sample_intervals = np.asarray(data["sample_intervals"], dtype=int)
        sample_orders = np.asarray(data["sample_orders"], dtype=int)
        sample_indices = np.asarray(data["sample_indices"], dtype=int)
        residuals = np.asarray(data["state_rate_residuals"], dtype=float)
    with np.load(CENTER) as data:
        fine_times = np.asarray(data["fine_grid_action_lengths"], dtype=float)
        macro_times = np.asarray(data["action_lengths"], dtype=float)
        stop_fraction = float(data["stop_dense_fraction"][0])
    with np.load(JACOBIAN) as data:
        jacobian_times = np.asarray(data["action_lengths"], dtype=float)
        jacobians = np.asarray(data["graph_Jacobian_action"], dtype=float)
    with np.load(TANGENT) as data:
        tangents = np.asarray(data["physical_tangent_action"], dtype=float)
    slopes = np.diff(jacobians, axis=0) / np.diff(jacobian_times)[:, None, None]
    commutators = np.asarray([
        jacobians[index] @ slopes[index] - slopes[index] @ jacobians[index]
        for index in range(slopes.shape[0])
    ])
    profiles = {
        order: _profile(
            order=order,
            sample_intervals=sample_intervals,
            sample_orders=sample_orders,
            sample_indices=sample_indices,
            residuals=residuals,
            fine_times=fine_times,
            stop_fraction=stop_fraction,
            macro_times=macro_times,
            tangents=tangents,
            jacobian_times=jacobian_times,
            jacobians=jacobians,
            substeps=args.propagator_substeps,
            slopes=slopes,
            commutators=commutators,
            magnus_order=args.magnus_order,
        )
        for order in (6, 8)
    }
    difference = np.linalg.norm(profiles[8] - profiles[6], axis=1)
    owner = int(np.argmax(difference))
    halo = float(json.loads(Z2.read_text(encoding="utf-8"))[
        "domain"
    ]["candidate_nonlinear_action_radius"])
    maximum = float(difference[owner])
    np.savez_compressed(
        DATA_RESULT,
        fine_action_lengths=np.concatenate((
            fine_times[:370],
            [fine_times[369] + stop_fraction * (fine_times[370] - fine_times[369])],
        )),
        Gauss6_correction_profile=profiles[6],
        Gauss8_correction_profile=profiles[8],
        cross_order_profile_increment=difference,
    )
    validation = {
        "same_retained_PROP_substeps_for_both_orders": True,
        "same_macro_tangent_projection_for_both_orders": True,
        "signed_sources_propagated_before_norm": True,
        "complete_371_node_profiles_compared": difference.shape == (371,),
        "maximum_Gauss6_to8_profile_increment_below_candidate_halo": maximum < halo,
        "not_relabelled_as_interval_propagator_authority": True,
    }
    payload = {
        "artifact": (
            "BHSM_N12_GATE7_DECIMAL_SIGNED_Y_GREEN_CONVERGENCE_AUDIT"
            if args.propagator_substeps == 16 and args.magnus_order == 2 else
            f"BHSM_N12_GATE7_DECIMAL_SIGNED_Y_GREEN_MAGNUS{args.magnus_order}_"
            f"PROP{args.propagator_substeps}_AUDIT"
        ),
        "authority": "NUMERICAL_CORRELATION_PRESERVING_GREEN_CROSS_ORDER_AUDIT_NOT_INTERVAL_AUTHORITY",
        "identity": {
            "source_sign": "MINUS_DEFECT",
            "source_orders": [6, 8],
            "propagator_substeps_per_quarter_cell": args.propagator_substeps,
            "Magnus_order": args.magnus_order,
            "affine_generator_commutator_coefficient": (
                "-h^3*[A_mid,A_prime]/12" if args.magnus_order >= 4 else None
            ),
            "affine_generator_fifth_order_coefficient": (
                "h^5*([A,[A,[A,B]]]/720-[B,[A,B]]/240)"
                if args.magnus_order >= 6 else None
            ),
            "constraint_handling": "PROJECT_ONLY_AT_RETAINED_MACRO_SEAMS",
        },
        "summary": {
            "candidate_nonlinear_action_radius": halo,
            "maximum_signed_correction_profile_increment_2_norm": maximum,
            "profile_increment_owner_fine_node": owner,
            "candidate_halo_utilization": maximum / halo,
            "terminal_signed_correction_increment_2_norm": float(difference[-1]),
        },
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path)
            for path in (SOURCE, CENTER, JACOBIAN, TANGENT, Z2)
        },
        "data": DATA_RESULT.relative_to(ROOT).as_posix(),
        "claim_boundary": {
            "signed_Y_numerical_cross_order_convergence": (
                "VALIDATED" if maximum < halo else "OPEN"
            ),
            "outward_interval_Y_and_Z1": "OPEN",
            "Gate7": "ACTIVE",
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
