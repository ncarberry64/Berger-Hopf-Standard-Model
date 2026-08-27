"""Probe the Kato clusters that actually isolate the Gate-7 selected line.

The ordered reduced Hessian has the selected line at branch 24.  A near
degeneracy internal to hard branches 26--27 must not be treated as a physical
line denominator.  The invariant boundary groups are therefore branch 23,
branch 24, and the positive hard cluster 25--27.  This script applies the
retained first-chord mixed-action majorant to those three groups on one of the
existing 64 Hermite subspans.
"""

from __future__ import annotations

import argparse
from functools import lru_cache
import json
import os
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_n12_c2_stop_local_termwise_spectrum as local  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
CENTER_DATA = Path(os.environ.get(
    "BHSM_N12_STOP_CENTER_DATA",
    str(BASE / "BHSM_N12_C2_STOP_MULTIPLE_SHOOTING_CENTER.npz"),
))
GROUPS = ((23,), (24,), (25, 26, 27))
DISTANCE_BAND_RATIO = 4.0


@lru_cache(maxsize=1)
def _center_arrays() -> tuple[np.ndarray, ...]:
    with np.load(CENTER_DATA) as source:
        return (
            np.asarray(source["centers"], dtype=float),
            np.asarray(source["action_rates"], dtype=float),
            np.asarray(source["action_lengths"], dtype=float),
            np.asarray(source["state_weights"], dtype=float),
            np.asarray(source["branch_reference"], dtype=float),
        )


def _cluster_bound(
    branches: tuple[int, ...],
    coupling_groups: tuple[tuple[int, ...], ...],
    geometry: dict[str, Any],
    weights: np.ndarray,
) -> dict[str, Any]:
    midpoint = geometry["midpoint"]
    projection = geometry["projection"]
    values = geometry["values"]
    vectors = geometry["vectors"]
    directionals = geometry["directionals"]
    indices = np.asarray(branches, dtype=int)
    outside_indices = np.asarray([
        index for index in range(values.size) if index not in branches
    ], dtype=int)
    cluster = vectors[:, indices]
    reduced_weights = weights[local.QDIM:]
    cluster_action = np.vstack((
        np.zeros((local.QDIM, len(branches))),
        reduced_weights[:, None] * cluster,
    ))
    diagonal_fourth = float(local.action_bound(
        midpoint,
        projection=projection,
        mixed_directions=[
            cluster_action, cluster_action, projection, projection,
        ],
    ).d[-1])
    external_gap = float(min(
        abs(values[inside] - values[outside_index])
        for inside in indices for outside_index in outside_indices
    ))
    diagonal_slopes = []
    for matrix in directionals:
        diagonal_slopes.append(float(np.linalg.norm(
            cluster.T @ matrix @ cluster, ord=2,
        )))
    slope_norm = float(np.linalg.norm(diagonal_slopes))
    assigned = {index for group in coupling_groups for index in group}
    if assigned != set(int(index) for index in outside_indices):
        expected = set(int(index) for index in outside_indices)
        raise RuntimeError(
            "coupling groups must partition the cluster complement: "
            f"missing={sorted(expected - assigned)}, extra={sorted(assigned - expected)}"
        )
    coupling_rows = []
    coupling_amplitude_square = 0.0
    for group in coupling_groups:
        group_indices = np.asarray(group, dtype=int)
        group_vectors = vectors[:, group_indices]
        group_action = np.vstack((
            np.zeros((local.QDIM, len(group))),
            reduced_weights[:, None] * group_vectors,
        ))
        group_fourth = float(local.action_bound(
            midpoint,
            projection=projection,
            mixed_directions=[
                group_action, cluster_action, projection, projection,
            ],
        ).d[-1])
        pair_denominators = 0.5 * np.abs(
            values[group_indices, None] - values[indices][None, :]
        )
        group_energy = 0.0
        for matrix in directionals:
            coupling = group_vectors.T @ matrix @ cluster
            group_energy += float(np.sum(np.square(coupling) / pair_denominators))
        group_denominator = float(np.min(pair_denominators))
        group_amplitude_square = float(
            (np.sqrt(group_energy) + group_fourth / np.sqrt(group_denominator)) ** 2
        )
        coupling_amplitude_square += group_amplitude_square
        coupling_rows.append({
            "branches": list(group),
            "minimum_half_denominator": group_denominator,
            "D3_weighted_energy_upper": group_energy,
            "D4_coupling_upper": group_fourth,
            "Kato_amplitude_square_upper": group_amplitude_square,
        })
    curvature = float(
        diagonal_fourth
        + 2.0 * coupling_amplitude_square
    )
    shift = slope_norm + 0.5 * curvature
    return {
        "branches": list(branches),
        "external_center_gap": external_gap,
        "diagonal_D3_slope_norm": slope_norm,
        "diagonal_D4_upper": diagonal_fourth,
        "coupling_groups": coupling_rows,
        "Kato_cluster_curvature_upper": curvature,
        "cluster_spectral_shift_upper": shift,
        "quarter_gap_bootstrap_closed": shift < 0.25 * external_gap,
    }


def _distance_groups(
    values: np.ndarray, branches: tuple[int, ...], ratio: float = DISTANCE_BAND_RATIO,
) -> tuple[tuple[int, ...], ...]:
    """Partition the complement by comparable Sylvester denominators."""
    inside = np.asarray(branches, dtype=int)
    remaining = {
        index: float(np.min(np.abs(values[index] - values[inside])))
        for index in range(values.size) if index not in branches
    }
    groups = []
    while remaining:
        minimum = min(remaining.values())
        cutoff = ratio * minimum
        group = tuple(sorted(
            index for index, distance in remaining.items() if distance <= cutoff
        ))
        groups.append(group)
        for index in group:
            del remaining[index]
    return tuple(groups)


def probe(seam: int, subspan: int) -> dict[str, Any]:
    states, action_rates, action_lengths, weights, reference = _center_arrays()
    geometry = local._subspan_geometry(
        seam, subspan, states, action_rates, action_lengths, weights, reference,
    )
    values = geometry["values"]
    rows = [
        _cluster_bound(
            (23,), _distance_groups(values, (23,)), geometry, weights,
        ),
        _cluster_bound(
            (24,), _distance_groups(values, (24,)), geometry, weights,
        ),
        _cluster_bound(
            (25, 26, 27), _distance_groups(values, (25, 26, 27)), geometry, weights,
        ),
    ]
    selected = next(row for row in rows if row["branches"] == [24])
    negative = next(row for row in rows if row["branches"] == [23])
    positive = next(row for row in rows if row["branches"] == [25, 26, 27])
    negative_margin = float(
        values[24] - values[23]
        - selected["cluster_spectral_shift_upper"]
        - negative["cluster_spectral_shift_upper"]
    )
    positive_margin = float(
        values[25] - values[24]
        - selected["cluster_spectral_shift_upper"]
        - positive["cluster_spectral_shift_upper"]
    )
    return {
        "seam": seam,
        "subspan": subspan,
        "selected_branch": geometry["selected"],
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--seam", type=int, default=45)
    parser.add_argument("--subspan", type=int, default=32)
    arguments = parser.parse_args()
    print(json.dumps(probe(arguments.seam, arguments.subspan), indent=2))


if __name__ == "__main__":
    main()
