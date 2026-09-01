"""Audit the retained fine DOP853 dense stop-center polynomials.

The high-order center stores SciPy's seventh-order DOP853 dense coefficients
for every fixed half-action substep.  This script evaluates those same
polynomials and their exact polynomial derivatives at Gauss nodes, then
compares them with the retained normalized cancelled BHSM field.  It is a
global center residual audit, not an interval enclosure.
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
if os.environ.get("BHSM_N12_USE_JAX", "0") == "1":
    from bhsm.interface.aether_jax_forward_c2_exact_fixed_s_field import (  # noqa: E402
        exact_cancelled_euler_dirac_field_action,
    )


BASE = ROOT / "artifacts" / "flagship_integration"
CENTER_DATA = Path(os.environ.get(
    "BHSM_N12_STOP_CENTER_DATA",
    str(BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_HALF_STEP_CENTER_RECONNAISSANCE.npz"),
))
RESULT = Path(os.environ.get(
    "BHSM_N12_STOP_DENSE_RESIDUAL_RESULT",
    str(BASE / "BHSM_N12_C2_STOP_DOP853_DENSE_RESIDUAL_RECONNAISSANCE.json"),
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


def _sample(task: tuple) -> tuple[dict[str, float | int], np.ndarray]:
    (
        interval, sample, fraction, left, coefficients, step,
        weights, reference,
    ) = task
    augmented = np.asarray(_dense(left, coefficients, fraction), dtype=float)
    derivative = np.imag(_dense(
        left, coefficients, fraction + 1j * COMPLEX_STEP,
    )) / COMPLEX_STEP / step
    descriptor = float(augmented[-1])
    if descriptor < -1.0e-18:
        raise RuntimeError("stored dense path left the positive-s domain")
    descriptor = max(descriptor, 0.0)
    field = exact_cancelled_euler_dirac_field_action(
        state=augmented[:-1] / weights,
        weights=weights,
        reference=reference,
        signed_descriptor=descriptor,
    )
    cancelled = np.asarray(field["cancelled_field_action"], dtype=float)
    norm = float(np.linalg.norm(cancelled))
    exact = np.concatenate((cancelled / norm, [float(field["Delta"]) / norm]))
    residual = derivative - exact
    return ({
        "interval": interval,
        "sample": sample,
        "fraction": float(fraction),
        "descriptor": descriptor,
        "state_rate_residual_2_norm": float(np.linalg.norm(residual[:-1])),
        "state_rate_residual_infinity_norm": float(
            np.max(np.abs(residual[:-1]))
        ),
        "descriptor_rate_residual": float(residual[-1]),
        "augmented_rate_residual_2_norm": float(np.linalg.norm(residual)),
        "selected_branch": int(field["selected_branch"]),
        "selected_eigenline_gap": float(field["selected_eigenline_gap"]),
        "b_psi": float(field["b_psi"]),
        "Delta": float(field["Delta"]),
        "cancelled_field_action_norm": norm,
    }, residual)


def build_payload(*, workers: int, samples_per_interval: int) -> dict[str, object]:
    with np.load(CENTER_DATA) as source:
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)
        grid_times = np.asarray(source["fine_grid_action_lengths"], dtype=float)
        grid_values = np.asarray(
            source["fine_grid_augmented_action_values"], dtype=float,
        )
        coefficients = np.asarray(
            source["fine_grid_DOP853_dense_coefficients"], dtype=float,
        )
        bracket_index = int(source["stop_bracket_fine_grid_index"][0])
        stop_fraction = float(source["stop_dense_fraction"][0])
    step = float(grid_times[1] - grid_times[0])
    nodes, _ = np.polynomial.legendre.leggauss(samples_per_interval)
    unit_fractions = 0.5 * (nodes + 1.0)
    tasks = []
    for interval in range(bracket_index + 1):
        right_fraction = stop_fraction if interval == bracket_index else 1.0
        for sample, unit in enumerate(unit_fractions):
            tasks.append((
                interval, sample, float(right_fraction * unit),
                grid_values[interval], coefficients[interval], step,
                weights, reference,
            ))
    with ProcessPoolExecutor(max_workers=workers) as executor:
        sampled = list(executor.map(_sample, tasks, chunksize=1))
    rows = [item[0] for item in sampled]
    residual_vectors = np.asarray([item[1] for item in sampled])
    rate_owner = max(rows, key=lambda row: row["augmented_rate_residual_2_norm"])
    descriptor_owner = max(rows, key=lambda row: abs(row["descriptor_rate_residual"]))
    gap_owner = min(rows, key=lambda row: row["selected_eigenline_gap"])
    b_owner = min(rows, key=lambda row: row["b_psi"])
    s_owner = min(rows, key=lambda row: row["descriptor"])
    branches = sorted({int(row["selected_branch"]) for row in rows})
    np.savez_compressed(
        DATA_RESULT,
        interval=np.asarray([row["interval"] for row in rows]),
        fraction=np.asarray([row["fraction"] for row in rows]),
        state_rate_residual_2_norm=np.asarray([
            row["state_rate_residual_2_norm"] for row in rows
        ]),
        descriptor_rate_residual=np.asarray([
            row["descriptor_rate_residual"] for row in rows
        ]),
        selected_eigenline_gap=np.asarray([
            row["selected_eigenline_gap"] for row in rows
        ]),
        b_psi=np.asarray([row["b_psi"] for row in rows]),
        Delta=np.asarray([row["Delta"] for row in rows]),
        augmented_rate_residual=residual_vectors,
    )
    summary = {
        "fine_intervals_through_stop": bracket_index + 1,
        "fixed_action_step": step,
        "stop_interval_fraction": stop_fraction,
        "Gauss_samples_per_interval": samples_per_interval,
        "exact_field_samples": len(rows),
        "selected_branches_seen": branches,
        "maximum_augmented_rate_residual_2_norm": rate_owner[
            "augmented_rate_residual_2_norm"
        ],
        "maximum_rate_residual_owner": rate_owner,
        "maximum_absolute_descriptor_rate_residual": abs(
            descriptor_owner["descriptor_rate_residual"]
        ),
        "maximum_descriptor_rate_residual_owner": descriptor_owner,
        "minimum_selected_eigenline_gap": gap_owner["selected_eigenline_gap"],
        "minimum_selected_eigenline_gap_owner": gap_owner,
        "minimum_b_psi": b_owner["b_psi"],
        "minimum_b_psi_owner": b_owner,
        "minimum_interior_descriptor": s_owner["descriptor"],
        "minimum_interior_descriptor_owner": s_owner,
        "minimum_Delta": min(row["Delta"] for row in rows),
        "maximum_Delta": max(row["Delta"] for row in rows),
    }
    return {
        "artifact": "BHSM_N12_C2_STOP_DOP853_DENSE_RESIDUAL_RECONNAISSANCE",
        "authority": "GLOBAL_DENSE_CENTER_SAMPLES_ONLY_NOT_INTERVAL_AUTHORITY",
        "construction": {
            "center": CENTER_DATA.relative_to(ROOT).as_posix(),
            "dense_interpolant": "STORED_NATIVE_DOP853_SEVENTH_ORDER_POLYNOMIAL",
            "derivative": "EXACT_COMPLEX_DERIVATIVE_OF_THE_STORED_POLYNOMIAL",
            "field": "RETAINED_NORMALIZED_CANCELLED_BHSM_EULER_DIRAC_FIELD",
        },
        "summary": summary,
        "data": DATA_RESULT.relative_to(ROOT).as_posix(),
        "validation_passed": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=min(12, os.cpu_count() or 1))
    parser.add_argument("--samples-per-interval", type=int, default=3)
    args = parser.parse_args()
    payload = build_payload(
        workers=args.workers, samples_per_interval=args.samples_per_interval,
    )
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
