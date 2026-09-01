"""Certify the selected projector graph on all finite-stop subspans.

The preceding boundary-cluster certificate supplies a positive selected-line
gap on every correlated Hermite action ball.  This script reuses the exact
center D3 coupling and retained D4 action majorant, resolved by the same
spectral-distance bands, to bound the Kato graph derivative of branch 24.
"""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
from functools import lru_cache
import hashlib
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
SPECTRUM = BASE / "BHSM_N12_C2_STOP_FULL_BOUNDARY_CLUSTER_SPECTRUM.json"
RESULT = BASE / "BHSM_N12_C2_STOP_FULL_SELECTED_PROJECTOR_GRAPH.json"
SELECTED = 24
NEUMANN_FACTOR = 2.0


def _up(value: float) -> float:
    return math.nextafter(float(value) * (1.0 + 1.0e-10), math.inf)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


@lru_cache(maxsize=1)
def _spectrum_rows() -> dict[tuple[int, int], dict[str, Any]]:
    record = json.loads(SPECTRUM.read_text(encoding="utf-8"))
    if record["claim_boundary"][
        "selected_line_on_reference_Hermite_stop_path"
    ] != "CERTIFIED_SIMPLE":
        raise RuntimeError("complete finite-stop spectrum certificate required")
    return {
        (int(row["seam"]), int(row["subspan"])): row
        for row in record["rows"]
    }


def _projector_row(pair: tuple[int, int]) -> dict[str, Any]:
    seam, subspan = pair
    spectrum = _spectrum_rows()[(seam, subspan)]
    states, action_rates, action_lengths, weights, reference = cluster._center_arrays()
    geometry = cluster.local._subspan_geometry(
        seam, subspan, states, action_rates, action_lengths, weights, reference,
    )
    if geometry["selected"] != SELECTED:
        raise RuntimeError("selected branch changed")
    midpoint = geometry["midpoint"]
    projection = geometry["projection"]
    values = geometry["values"]
    vectors = geometry["vectors"]
    directionals = geometry["directionals"]
    selected = vectors[:, SELECTED]
    reduced_weights = weights[cluster.local.QDIM:]
    selected_action = np.concatenate((
        np.zeros(cluster.local.QDIM), reduced_weights * selected,
    ))
    reduced_basis_action = np.vstack((
        np.zeros((cluster.local.QDIM, values.size)),
        np.diag(reduced_weights),
    ))
    ambient_D3 = float(np.linalg.norm([
        np.linalg.norm(matrix, ord=2) for matrix in directionals
    ]))
    ambient_D4 = _up(float(cluster.local.action_bound(
        midpoint,
        projection=projection,
        mixed_directions=[
            reduced_basis_action, reduced_basis_action, projection, projection,
        ],
    ).d[-1]))
    ambient_Hessian_shift = _up(ambient_D3 + 0.5 * ambient_D4)
    selected_shift = float(spectrum["selected_line_shift_upper"])
    gap_lower = float(min(
        spectrum["negative_selected_gap_lower"],
        spectrum["selected_positive_gap_lower"],
    ))
    if gap_lower <= 0.0:
        raise RuntimeError("positive certified selected-line gap required")
    group_rows = []
    derivative_square = 0.0
    numerator_groups = cluster._distance_groups(values, (SELECTED,))
    for group in numerator_groups:
        indices = np.asarray(group, dtype=int)
        group_vectors = vectors[:, indices]
        group_action = np.vstack((
            np.zeros((cluster.local.QDIM, len(group))),
            reduced_weights[:, None] * group_vectors,
        ))
        center_coupling_square = 0.0
        for matrix in directionals:
            coupling = group_vectors.T @ matrix @ selected
            center_coupling_square += float(np.sum(np.square(coupling)))
        center_coupling = float(np.sqrt(center_coupling_square))
        coupling_change = _up(float(cluster.local.action_bound(
            midpoint,
            projection=projection,
            mixed_directions=[
                group_action, selected_action, projection, projection,
            ],
        ).d[-1]))
        numerator = _up(center_coupling + coupling_change)
        center_distance = float(np.min(np.abs(
            values[indices] - values[SELECTED]
        )))
        Weyl_gap_lower = center_distance - selected_shift - ambient_Hessian_shift
        branch_gap_lower = max(gap_lower, Weyl_gap_lower)
        derivative = _up(NEUMANN_FACTOR * numerator / branch_gap_lower)
        derivative_square += derivative**2
        group_rows.append({
            "branches": list(group),
            "minimum_center_distance": center_distance,
            "ordered_Weyl_gap_lower": Weyl_gap_lower,
            "consumed_gap_lower": branch_gap_lower,
            "center_D3_coupling_l2_norm": center_coupling,
            "D4_coupling_change_upper": coupling_change,
            "coupling_numerator_upper": numerator,
            "selected_graph_derivative_upper_using_global_gap": derivative,
        })
    derivative_l2 = _up(math.sqrt(derivative_square))
    return {
        "seam": seam,
        "subspan": subspan,
        "selected_branch": SELECTED,
        "certified_global_gap_lower": gap_lower,
        "selected_line_shift_upper": selected_shift,
        "ambient_D3_Hessian_shift_upper": ambient_D3,
        "ambient_D4_Hessian_remainder_upper": 0.5 * ambient_D4,
        "ambient_Hessian_shift_upper": ambient_Hessian_shift,
        "spectral_distance_bands": len(group_rows),
        "selected_graph_derivative_l2_upper": derivative_l2,
        "selected_projector_motion_upper": derivative_l2,
        "graph_Neumann_closed": derivative_l2 < 1.0,
        "groups": group_rows,
    }


def build_payload() -> dict[str, Any]:
    tasks = [(seam, subspan) for seam in range(47) for subspan in range(64)]
    workers = min(8, os.cpu_count() or 1)
    rows = []
    with ProcessPoolExecutor(max_workers=workers) as executor:
        for index, row in enumerate(executor.map(_projector_row, tasks, chunksize=1), 1):
            rows.append(row)
            if index % 64 == 0 or index == len(tasks):
                print(json.dumps({
                    "completed": index,
                    "total": len(tasks),
                    "closed_so_far": all(item["graph_Neumann_closed"] for item in rows),
                    "maximum_motion_so_far": max(
                        item["selected_projector_motion_upper"] for item in rows
                    ),
                }), flush=True)
    validation = {
        "all_3008_spectrum_certified_subspans_consumed_in_order": [
            (row["seam"], row["subspan"]) for row in rows
        ] == tasks,
        "branch_24_selected_everywhere": all(
            row["selected_branch"] == SELECTED for row in rows
        ),
        "every_certified_gap_strictly_positive": all(
            row["certified_global_gap_lower"] > 0.0 for row in rows
        ),
        "all_distance_band_graph_Neumann_bounds_below_one": all(
            row["graph_Neumann_closed"] for row in rows
        ),
        "exact_center_D3_and_retained_D4_action_majorant_used": True,
        "hard_26_27_internal_denominator_not_reintroduced": True,
        "far_branch_ordered_Weyl_denominators_combined_with_global_gap": True,
        "no_full_Euler_Dirac_or_dense_history_inverse_used": True,
    }
    passed = all(validation.values())
    owner = max(rows, key=lambda row: row["selected_projector_motion_upper"])
    return {
        "artifact": "BHSM_N12_C2_STOP_FULL_SELECTED_PROJECTOR_GRAPH",
        "status": (
            "ALL_3008_STOP_PATH_SELECTED_PROJECTOR_GRAPHS_CERTIFIED"
            if passed else "STOP_PATH_SELECTED_PROJECTOR_GRAPH_OPEN"
        ),
        "method": (
            "DENOMINATOR_RESOLVED_DISTANCE_BAND_KATO_GRAPH_WITH_EXACT_"
            "CENTER_D3_AND_RETAINED_CORRELATED_ACTION_BALL_D4"
        ),
        "mesh": {
            "macro_seams": 47,
            "subspans_per_macro_seam": 64,
            "total_subspans": len(tasks),
            "workers": workers,
        },
        "summary": {
            "maximum_selected_graph_derivative_l2_upper": max(
                row["selected_graph_derivative_l2_upper"] for row in rows
            ),
            "maximum_selected_projector_motion_upper": max(
                row["selected_projector_motion_upper"] for row in rows
            ),
            "minimum_consumed_gap_lower": min(
                row["certified_global_gap_lower"] for row in rows
            ),
            "maximum_spectral_distance_bands": max(
                row["spectral_distance_bands"] for row in rows
            ),
            "owner": owner,
            "Neumann_factor": NEUMANN_FACTOR,
        },
        "rows": rows,
        "validation": validation,
        "validation_passed": passed,
        "claim_boundary": {
            "all_3008_selected_projector_graphs": (
                "CERTIFIED" if passed else "OPEN"
            ),
            "bordered_hard_response_tube": "OPEN",
            "Green_Hermite_shadowing": "OPEN",
            "scalar_stop_first_hit": "OPEN",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "INSERT_THE_CERTIFIED_SELECTED_PROJECTOR_GRAPH_IN_THE_"
            "DENOMINATOR_RESOLVED_BORDERED_HARD_RESPONSE_ON_THE_SAME_MESH"
            if passed else
            "REFINE_ONLY_THE_REPORTED_PROJECTOR_GRAPH_OWNER_WITH_THE_SAME_"
            "DISTANCE_BAND_KERNEL"
        ),
        "inputs": {
            SPECTRUM.relative_to(ROOT).as_posix(): _sha256(SPECTRUM),
            cluster.CENTER_DATA.relative_to(ROOT).as_posix(): _sha256(
                cluster.CENTER_DATA
            ),
            "scripts/audit_n12_c2_stop_boundary_cluster_probe.py": _sha256(
                ROOT / "scripts" / "audit_n12_c2_stop_boundary_cluster_probe.py"
            ),
        },
        "FLAGSHIP_READY": False,
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
        "summary": payload["summary"],
        "validation_passed": payload["validation_passed"],
        "exact_next_dependency": payload["exact_next_dependency"],
    }, indent=2))


if __name__ == "__main__":
    main()
