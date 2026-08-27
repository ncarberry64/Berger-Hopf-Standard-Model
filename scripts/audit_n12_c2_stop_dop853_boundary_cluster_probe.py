"""Probe selected-line Kato clusters on the actual DOP853 dense center.

The proof cell is the convex hull of the exact degree-seven Bernstein control
points of one stored DOP853 polynomial (or one de Casteljau subcell).  This
keeps the spectral enclosure on the same polynomial used by the defect and
first-hit calculations; no cubic-Hermite surrogate is inserted.
"""

from __future__ import annotations

import argparse
from functools import lru_cache
import json
import math
import os
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_n12_c2_stop_boundary_cluster_probe as cluster  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
CENTER_DATA = Path(os.environ.get(
    "BHSM_N12_STOP_CENTER_DATA",
    str(BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.npz"),
))
SUBDIVISIONS = int(os.environ.get("BHSM_N12_STOP_DOP853_SUBDIVISIONS", "4"))
QDIM = 37
COMPLEX_STEP = 1.0e-20


@lru_cache(maxsize=1)
def _dense_arrays() -> tuple[np.ndarray, ...]:
    with np.load(CENTER_DATA) as source:
        return (
            np.asarray(source["fine_grid_augmented_action_values"], dtype=float),
            np.asarray(source["fine_grid_DOP853_dense_coefficients"], dtype=float),
            np.asarray(source["fine_grid_action_lengths"], dtype=float),
            np.asarray(source["state_weights"], dtype=float),
            np.asarray(source["branch_reference"], dtype=float),
            np.asarray(source["stop_bracket_fine_grid_index"], dtype=int),
            np.asarray(source["stop_dense_fraction"], dtype=float),
        )


def mesh_shape() -> tuple[int, int]:
    *_, bracket, __ = _dense_arrays()
    return int(bracket[0]) + 1, SUBDIVISIONS


def _dense_bernstein_controls(
    left: np.ndarray, coefficients: np.ndarray,
) -> np.ndarray:
    """Convert SciPy's stored alternating DOP853 form to Bernstein form."""
    dimension = left.size
    power = [np.zeros(dimension)]
    for index, coefficient in enumerate(reversed(coefficients)):
        power[0] = power[0] + coefficient
        if index % 2 == 0:
            power = [np.zeros(dimension), *power]
        else:
            prior = power
            power = [item.copy() for item in prior] + [np.zeros(dimension)]
            for degree, item in enumerate(prior):
                power[degree + 1] -= item
    power[0] += left
    degree = len(power) - 1
    return np.asarray([
        sum(
            (math.comb(k, j) / math.comb(degree, j)) * power[j]
            for j in range(k + 1)
        )
        for k in range(degree + 1)
    ])


def _split(control: np.ndarray, fraction: float) -> tuple[np.ndarray, np.ndarray]:
    levels = [np.asarray(control, dtype=float)]
    while levels[-1].shape[0] > 1:
        prior = levels[-1]
        levels.append((1.0 - fraction) * prior[:-1] + fraction * prior[1:])
    left = np.asarray([level[0] for level in levels])
    right = np.asarray([level[-1] for level in levels[::-1]])
    return left, right


def _restrict(control: np.ndarray, start: float, end: float) -> np.ndarray:
    left, _ = _split(control, end)
    if start == 0.0:
        return left
    return _split(left, start / end)[1]


def dense_subspan_geometry(interval: int, subspan: int) -> dict[str, Any]:
    values, coefficients, times, weights, reference, bracket_raw, stop_raw = (
        _dense_arrays()
    )
    bracket = int(bracket_raw[0])
    stop_fraction = float(stop_raw[0])
    intervals, subdivisions = mesh_shape()
    if not 0 <= interval < intervals or not 0 <= subspan < subdivisions:
        raise ValueError("DOP853 cell index lies outside the retained stop path")
    controls = _dense_bernstein_controls(values[interval], coefficients[interval])
    right = stop_fraction if interval == bracket else 1.0
    controls = _restrict(controls, 0.0, right)
    controls = _restrict(
        controls, subspan / subdivisions, (subspan + 1) / subdivisions,
    )
    state_controls = controls[:, :-1]
    midpoint_action = np.mean(state_controls, axis=0)
    # Every Bernstein curve point is a convex combination B*theta.  With
    # midpoint m, x-m=(B-m)*theta and ||theta||_2<=||theta||_1=1.
    projection = (state_controls - midpoint_action).T
    midpoint = midpoint_action / weights
    jet = cluster.local.exact_full_action_jet_at_state(
        12,
        midpoint[:QDIM], midpoint[QDIM:2 * QDIM], midpoint[2 * QDIM:],
        points=cluster.local.POINTS,
    )
    hessian = np.asarray(jet.hessian, dtype=float)[QDIM:, QDIM:]
    eigenvalues, eigenvectors = np.linalg.eigh(hessian)
    selected = int(np.argmax(np.abs(eigenvectors.T @ reference)))
    directionals = []
    for column in range(projection.shape[1]):
        shifted = np.asarray(midpoint, dtype=complex) + (
            1j * COMPLEX_STEP * projection[:, column] / weights
        )
        shifted_jet = cluster.local.exact_full_action_jet_at_state(
            12,
            shifted[:QDIM], shifted[QDIM:2 * QDIM], shifted[2 * QDIM:],
            points=cluster.local.POINTS,
        )
        directionals.append(
            np.imag(np.asarray(shifted_jet.hessian)[QDIM:, QDIM:])
            / COMPLEX_STEP
        )
    duration = (times[interval + 1] - times[interval]) * right / subdivisions
    return {
        "local_h": float(duration),
        "midpoint": midpoint,
        "projection": projection,
        "values": eigenvalues,
        "vectors": eigenvectors,
        "selected": selected,
        "directionals": directionals,
        "augmented_Bernstein_controls": controls,
    }


def probe(interval: int, subspan: int) -> dict[str, Any]:
    *_, weights, __, ___, ____ = _dense_arrays()
    geometry = dense_subspan_geometry(interval, subspan)
    eigenvalues = geometry["values"]
    rows = [
        cluster._cluster_bound(
            branches, cluster._distance_groups(eigenvalues, branches),
            geometry, weights,
        )
        for branches in cluster.GROUPS
    ]
    selected = next(row for row in rows if row["branches"] == [24])
    negative = next(row for row in rows if row["branches"] == [23])
    positive = next(row for row in rows if row["branches"] == [25, 26, 27])
    negative_margin = float(
        eigenvalues[24] - eigenvalues[23]
        - selected["cluster_spectral_shift_upper"]
        - negative["cluster_spectral_shift_upper"]
    )
    positive_margin = float(
        eigenvalues[25] - eigenvalues[24]
        - selected["cluster_spectral_shift_upper"]
        - positive["cluster_spectral_shift_upper"]
    )
    return {
        "interval": interval,
        "subspan": subspan,
        "selected_branch": geometry["selected"],
        "Bernstein_control_count": int(
            geometry["augmented_Bernstein_controls"].shape[0]
        ),
        "projection_column_norms": [
            float(np.linalg.norm(geometry["projection"][:, column]))
            for column in range(geometry["projection"].shape[1])
        ],
        "clusters": rows,
        "negative_selected_gap_lower": negative_margin,
        "selected_positive_gap_lower": positive_margin,
        "boundary_cluster_certificate_closed": bool(
            geometry["selected"] == 24
            and all(row["quarter_gap_bootstrap_closed"] for row in rows)
            and negative_margin > 0.0
            and positive_margin > 0.0
        ),
    }


def main() -> None:
    intervals, subdivisions = mesh_shape()
    parser = argparse.ArgumentParser()
    parser.add_argument("--interval", type=int, default=intervals - 1)
    parser.add_argument("--subspan", type=int, default=subdivisions - 1)
    arguments = parser.parse_args()
    print(json.dumps(probe(arguments.interval, arguments.subspan), indent=2))


if __name__ == "__main__":
    main()
