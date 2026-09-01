"""Audit one correlated Newton correction of the global DOP853 center.

The signed Green correction is added to the stored center at every fine node.
On each fine interval a cubic correction matches those endpoint corrections
and makes the corrected polynomial derivative equal the retained field at
both endpoints.  Exact retained fields at interior Gauss nodes then measure
whether the global Newton correction has reduced the center defect.

This is a numerical Newton-center audit, not an interval Krawczyk proof.
"""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
import argparse
import json
import os
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_forward_c2_exact_fixed_s_field import (  # noqa: E402
    exact_cancelled_euler_dirac_field_action,
)
if os.environ.get("BHSM_N12_USE_FAST_DELTA", "0") == "1":
    from bhsm.interface.aether_forward_c2_fast_cancelled_field import (  # noqa: E402
        exact_cancelled_euler_dirac_field_action,
    )


BASE = ROOT / "artifacts" / "flagship_integration"
CENTER_DATA = Path(os.environ.get(
    "BHSM_N12_STOP_CENTER_DATA",
    str(BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_HALF_STEP_CENTER_RECONNAISSANCE.npz"),
))
CORRECTION_DATA = Path(os.environ.get(
    "BHSM_N12_STOP_CORRELATED_DEFECT_DATA",
    str(BASE / "BHSM_N12_C2_STOP_FINE_JACOBIAN_CORRELATED_DEFECT_GAUSS12_RECONNAISSANCE.npz"),
))
RESULT = Path(os.environ.get(
    "BHSM_N12_STOP_NEWTON_RESIDUAL_RESULT",
    str(BASE / "BHSM_N12_C2_STOP_NEWTON_CORRECTED_DENSE_RESIDUAL_RECONNAISSANCE.json"),
))
DATA_RESULT = RESULT.with_suffix(".npz")
COMPLEX_STEP = 1.0e-30


def _dense(
    left: np.ndarray, coefficients: np.ndarray, fraction: complex | float,
) -> np.ndarray:
    dtype = complex if np.iscomplexobj(fraction) else float
    value = np.zeros(left.shape, dtype=dtype)
    for index, coefficient in enumerate(reversed(coefficients)):
        value += coefficient
        value *= fraction if index % 2 == 0 else 1.0 - fraction
    return value + left


def _dense_rate(
    left: np.ndarray, coefficients: np.ndarray, fraction: float, step: float,
) -> np.ndarray:
    return np.imag(_dense(
        left, coefficients, fraction + 1j * COMPLEX_STEP,
    )) / COMPLEX_STEP / step


def _hermite(
    left: np.ndarray, right: np.ndarray,
    left_rate: np.ndarray, right_rate: np.ndarray,
    fraction: float, duration: float,
) -> tuple[np.ndarray, np.ndarray]:
    u = float(fraction)
    value = (
        (2*u**3 - 3*u**2 + 1) * left
        + (u**3 - 2*u**2 + u) * duration * left_rate
        + (-2*u**3 + 3*u**2) * right
        + (u**3 - u**2) * duration * right_rate
    )
    rate = (
        (6*u**2 - 6*u) * left
        + (3*u**2 - 4*u + 1) * duration * left_rate
        + (-6*u**2 + 6*u) * right
        + (3*u**2 - 2*u) * duration * right_rate
    ) / duration
    return value, rate


def _field(task: tuple[int, np.ndarray, np.ndarray, np.ndarray]) -> tuple:
    index, augmented, weights, reference = task
    descriptor = max(float(augmented[-1]), 0.0)
    field = exact_cancelled_euler_dirac_field_action(
        state=augmented[:-1] / weights,
        weights=weights,
        reference=reference,
        signed_descriptor=descriptor,
    )
    cancelled = np.asarray(field["cancelled_field_action"], dtype=float)
    norm = float(np.linalg.norm(cancelled))
    rate = np.concatenate((cancelled / norm, [float(field["Delta"]) / norm]))
    return index, rate, field


def _sample(task: tuple) -> tuple[dict[str, float | int], np.ndarray]:
    (
        interval, sample, unit, right_fraction, left, dense_coefficients,
        fixed_step, correction_endpoints, correction_rates, weights, reference,
    ) = task
    original_fraction = float(right_fraction * unit)
    original = np.asarray(_dense(left, dense_coefficients, original_fraction), dtype=float)
    original_rate = _dense_rate(
        left, dense_coefficients, original_fraction, fixed_step,
    )
    duration = fixed_step * right_fraction
    correction, correction_rate = _hermite(
        correction_endpoints[0], correction_endpoints[1],
        correction_rates[0], correction_rates[1], unit, duration,
    )
    augmented = original + correction
    path_rate = original_rate + correction_rate
    if augmented[-1] < -1.0e-16:
        raise RuntimeError("Newton-corrected center left the positive-s domain")
    augmented[-1] = max(augmented[-1], 0.0)
    _, exact_rate, field = _field((0, augmented, weights, reference))
    residual = path_rate - exact_rate
    return ({
        "interval": interval,
        "sample": sample,
        "fraction": original_fraction,
        "descriptor": float(augmented[-1]),
        "state_rate_residual_2_norm": float(np.linalg.norm(residual[:-1])),
        "descriptor_rate_residual": float(residual[-1]),
        "augmented_rate_residual_2_norm": float(np.linalg.norm(residual)),
        "selected_branch": int(field["selected_branch"]),
        "selected_eigenline_gap": float(field["selected_eigenline_gap"]),
        "b_psi": float(field["b_psi"]),
        "Delta": float(field["Delta"]),
    }, residual)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=min(12, os.cpu_count() or 1))
    parser.add_argument("--samples-per-interval", type=int, default=3)
    args = parser.parse_args()
    with np.load(CENTER_DATA) as source:
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)
        fine_times = np.asarray(source["fine_grid_action_lengths"], dtype=float)
        fine_values = np.asarray(source["fine_grid_augmented_action_values"], dtype=float)
        dense_coefficients = np.asarray(source["fine_grid_DOP853_dense_coefficients"], dtype=float)
        bracket = int(source["stop_bracket_fine_grid_index"][0])
        stop_fraction = float(source["stop_dense_fraction"][0])
        stop_augmented = np.concatenate((
            np.asarray(source["centers"][-1], dtype=float) * weights,
            [float(source["signed_descriptors"][-1])],
        ))
    with np.load(CORRECTION_DATA) as source:
        correction_times = np.asarray(source["fine_action_lengths"], dtype=float)
        state_correction = np.asarray(source["fine_ambient_correction_profile"], dtype=float)
        descriptor_correction = np.asarray(source["fine_descriptor_correction_profile"], dtype=float)
    correction = np.column_stack((state_correction, descriptor_correction))
    endpoint_times = np.concatenate((fine_times[:bracket + 1], [correction_times[-1]]))
    original_endpoints = np.vstack((fine_values[:bracket + 1], stop_augmented))
    if not np.allclose(endpoint_times, correction_times, atol=1.0e-12, rtol=0.0):
        raise RuntimeError("correction and center fine grids do not match")
    corrected_endpoints = original_endpoints + correction
    endpoint_tasks = [
        (index, value, weights, reference)
        for index, value in enumerate(corrected_endpoints)
    ]
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        endpoint_fields = list(executor.map(_field, endpoint_tasks, chunksize=1))
    endpoint_fields.sort(key=lambda item: item[0])
    corrected_rates = np.asarray([item[1] for item in endpoint_fields])
    original_rates = []
    for index in range(bracket + 2):
        if index == 0:
            original_rates.append(_dense_rate(
                fine_values[0], dense_coefficients[0], 0.0,
                float(fine_times[1] - fine_times[0]),
            ))
        elif index <= bracket:
            original_rates.append(_dense_rate(
                fine_values[index - 1], dense_coefficients[index - 1], 1.0,
                float(fine_times[1] - fine_times[0]),
            ))
        else:
            original_rates.append(_dense_rate(
                fine_values[bracket], dense_coefficients[bracket], stop_fraction,
                float(fine_times[1] - fine_times[0]),
            ))
    original_rates = np.asarray(original_rates)
    correction_rates = corrected_rates - original_rates

    nodes, _ = np.polynomial.legendre.leggauss(args.samples_per_interval)
    units = 0.5 * (nodes + 1.0)
    fixed_step = float(fine_times[1] - fine_times[0])
    tasks = []
    for interval in range(bracket + 1):
        right_fraction = stop_fraction if interval == bracket else 1.0
        for sample, unit in enumerate(units):
            tasks.append((
                interval, sample, float(unit), right_fraction,
                fine_values[interval], dense_coefficients[interval], fixed_step,
                correction[interval:interval + 2],
                correction_rates[interval:interval + 2], weights, reference,
            ))
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        sampled = list(executor.map(_sample, tasks, chunksize=1))
    rows = [item[0] for item in sampled]
    residuals = np.asarray([item[1] for item in sampled])
    owner = max(rows, key=lambda row: row["augmented_rate_residual_2_norm"])
    descriptor_owner = max(rows, key=lambda row: abs(row["descriptor_rate_residual"]))
    np.savez_compressed(
        DATA_RESULT,
        action_lengths=endpoint_times,
        corrected_augmented_endpoints=corrected_endpoints,
        corrected_endpoint_rates=corrected_rates,
        correction_endpoint_rates=correction_rates,
        interval=np.asarray([row["interval"] for row in rows]),
        fraction=np.asarray([row["fraction"] for row in rows]),
        augmented_rate_residual=residuals,
    )
    summary = {
        "fine_intervals": bracket + 1,
        "Gauss_samples_per_interval": args.samples_per_interval,
        "maximum_input_correction_2_norm": float(np.max(np.linalg.norm(correction, axis=1))),
        "maximum_augmented_rate_residual_2_norm": owner["augmented_rate_residual_2_norm"],
        "maximum_rate_residual_owner": owner,
        "maximum_absolute_descriptor_rate_residual": abs(descriptor_owner["descriptor_rate_residual"]),
        "minimum_selected_eigenline_gap": min(row["selected_eigenline_gap"] for row in rows),
        "minimum_b_psi": min(row["b_psi"] for row in rows),
        "selected_branches_seen": sorted({int(row["selected_branch"]) for row in rows}),
    }
    payload = {
        "artifact": "BHSM_N12_C2_STOP_NEWTON_CORRECTED_DENSE_RESIDUAL_RECONNAISSANCE",
        "authority": "GLOBAL_NEWTON_CENTER_SAMPLES_ONLY_NOT_INTERVAL_AUTHORITY",
        "construction": {
            "base_center": CENTER_DATA.relative_to(ROOT).as_posix(),
            "correlated_correction": CORRECTION_DATA.relative_to(ROOT).as_posix(),
            "correction_interpolant": "FINE_ENDPOINT_CUBIC_HERMITE",
            "endpoint_rates": "RETAINED_FIELD_AT_CORRECTED_ENDPOINTS",
            "interior_field": "RETAINED_NORMALIZED_CANCELLED_BHSM_FIELD",
        },
        "summary": summary,
        "data": DATA_RESULT.relative_to(ROOT).as_posix(),
        "validation_passed": False,
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
