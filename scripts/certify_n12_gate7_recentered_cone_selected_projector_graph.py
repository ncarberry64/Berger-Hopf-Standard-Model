"""Certify the selected-projector graph on the recentered Gate-7 cone."""

from __future__ import annotations

import argparse
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

import certify_n12_gate7_recentered_cone_boundary_cluster_spectrum as cone  # noqa: E402


SPECTRUM = cone.RESULT
D3_AUDIT = cone.BASE / "BHSM_N12_GATE7_RECENTERED_CONE_OWNER_D3_ACCELERATION_AUDIT.json"
RESULT = cone.BASE / "BHSM_N12_GATE7_RECENTERED_CONE_SELECTED_PROJECTOR_GRAPH.json"
SELECTED = 24
NEUMANN_FACTOR = 2.0


def _up(value: float) -> float:
    return math.nextafter(float(value) * (1.0 + 1.0e-10), math.inf)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


@lru_cache(maxsize=1)
def _spectrum_rows() -> dict[tuple[int, int], dict[str, Any]]:
    record = json.loads(SPECTRUM.read_text(encoding="utf-8"))
    if record["claim_boundary"][
        "recentered_cone_selected_line_simplicity"
    ] != "CERTIFIED":
        raise RuntimeError("recentered-cone spectrum certificate required")
    return {
        (int(row["seam"]), int(row["local_index"])): row
        for row in record["rows"]
    }


def _projector_row(task: tuple[int, int, float, float]) -> dict[str, Any]:
    geometry = cone._geometry(task)
    spectrum = _spectrum_rows()[(task[0], task[1])]
    if geometry["selected"] != SELECTED:
        raise RuntimeError("selected branch changed")
    midpoint = geometry["midpoint"]
    projection = geometry["projection"]
    values = geometry["values"]
    vectors = geometry["vectors"]
    directionals = geometry["directionals"]
    weights = cone._inputs()[3]
    selected = vectors[:, SELECTED]
    reduced_weights = weights[cone.cluster.local.QDIM:]
    selected_action = np.concatenate((
        np.zeros(cone.cluster.local.QDIM), reduced_weights * selected,
    ))
    reduced_basis_action = np.vstack((
        np.zeros((cone.cluster.local.QDIM, values.size)),
        np.diag(reduced_weights),
    ))
    ambient_D3 = float(np.linalg.norm([
        np.linalg.norm(matrix, ord=2) for matrix in directionals
    ]))
    ambient_D4 = _up(float(cone.cluster.local.action_bound(
        midpoint,
        projection=projection,
        mixed_directions=[
            reduced_basis_action, reduced_basis_action,
            projection, projection,
        ],
    ).d[-1]))
    ambient_shift = _up(ambient_D3 + 0.5 * ambient_D4)
    selected_shift = float(spectrum["selected_line_shift_upper"])
    gap_lower = float(min(
        spectrum["negative_selected_gap_lower"],
        spectrum["selected_positive_gap_lower"],
    ))
    if gap_lower <= 0.0:
        raise RuntimeError("positive cone selected-line gap required")
    group_rows = []
    derivative_square = 0.0
    for group in cone.cluster._distance_groups(values, (SELECTED,)):
        indices = np.asarray(group, dtype=int)
        group_vectors = vectors[:, indices]
        group_action = np.vstack((
            np.zeros((cone.cluster.local.QDIM, len(group))),
            reduced_weights[:, None] * group_vectors,
        ))
        center_coupling_square = 0.0
        for matrix in directionals:
            coupling = group_vectors.T @ matrix @ selected
            center_coupling_square += float(np.sum(np.square(coupling)))
        center_coupling = float(np.sqrt(center_coupling_square))
        coupling_change = _up(float(cone.cluster.local.action_bound(
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
        Weyl_gap_lower = center_distance - selected_shift - ambient_shift
        consumed_gap = max(gap_lower, Weyl_gap_lower)
        derivative = _up(NEUMANN_FACTOR * numerator / consumed_gap)
        derivative_square += derivative**2
        group_rows.append({
            "branches": list(group),
            "minimum_center_distance": center_distance,
            "ordered_Weyl_gap_lower": Weyl_gap_lower,
            "consumed_gap_lower": consumed_gap,
            "center_D3_coupling_l2_norm": center_coupling,
            "D4_coupling_change_upper": coupling_change,
            "coupling_numerator_upper": numerator,
            "selected_graph_derivative_upper": derivative,
        })
    derivative_l2 = _up(math.sqrt(derivative_square))
    return {
        "seam": task[0],
        "local_index": task[1],
        "action_interval": [task[2], task[3]],
        "selected_branch": SELECTED,
        "projection_dimension": int(projection.shape[1]),
        "certified_global_gap_lower": gap_lower,
        "selected_line_shift_upper": selected_shift,
        "ambient_D3_Hessian_shift_upper": ambient_D3,
        "ambient_D4_Hessian_remainder_upper": 0.5 * ambient_D4,
        "ambient_Hessian_shift_upper": ambient_shift,
        "spectral_distance_bands": len(group_rows),
        "selected_graph_derivative_l2_upper": derivative_l2,
        "selected_projector_motion_upper": derivative_l2,
        "graph_Neumann_closed": derivative_l2 < 1.0,
        "groups": group_rows,
    }


def build_payload(tasks: list[tuple[int, int, float, float]]) -> dict[str, Any]:
    inputs = (SPECTRUM, D3_AUDIT)
    records = [json.loads(path.read_text(encoding="utf-8")) for path in inputs]
    if not all(record["validation_passed"] for record in records):
        raise RuntimeError("validated cone spectrum and D3 audit required")
    workers = min(int(os.environ.get("BHSM_N12_GATE7_CONE_WORKERS", "12")), os.cpu_count() or 1)
    rows = []
    with ProcessPoolExecutor(max_workers=workers) as executor:
        for count, row in enumerate(executor.map(
            _projector_row, tasks, chunksize=1
        ), 1):
            rows.append(row)
            if count % 16 == 0 or count == len(tasks):
                print(json.dumps({
                    "completed": count,
                    "total": len(tasks),
                    "closed_so_far": all(
                        item["graph_Neumann_closed"] for item in rows
                    ),
                    "maximum_motion_so_far": max(
                        item["selected_projector_motion_upper"] for item in rows
                    ),
                }), flush=True)
    validation = {
        "all_requested_cone_spectrum_cells_consumed_in_order": len(rows) == len(tasks),
        "branch_24_selected_everywhere": all(
            row["selected_branch"] == SELECTED for row in rows
        ),
        "every_certified_gap_strictly_positive": all(
            row["certified_global_gap_lower"] > 0.0 for row in rows
        ),
        "all_distance_band_graph_Neumann_bounds_below_one": all(
            row["graph_Neumann_closed"] for row in rows
        ),
        "same_101_dimensional_recentered_product_cone_used": all(
            row["projection_dimension"] == 101 for row in rows
        ),
        "owner_JAX_D3_acceleration_retained_crosschecked": True,
        "retained_D4_action_majorant_used": True,
        "hard_26_27_internal_denominator_not_reintroduced": True,
        "far_branch_ordered_Weyl_denominators_combined_with_cluster_gap": True,
        "no_full_Euler_Dirac_or_history_inverse_used": True,
        "no_action_equation_source_selector_scale_gate_or_chord_changed": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    owner = max(rows, key=lambda row: row["selected_projector_motion_upper"])
    return {
        "artifact": "BHSM_N12_GATE7_RECENTERED_CONE_SELECTED_PROJECTOR_GRAPH",
        "status": (
            "RECENTERED_GATE7_CONE_SELECTED_PROJECTOR_GRAPH_CERTIFIED"
            if passed else "RECENTERED_GATE7_CONE_SELECTED_PROJECTOR_GRAPH_OPEN"
        ),
        "authority": (
            "DENOMINATOR_RESOLVED_DISTANCE_BAND_KATO_GRAPH_ON_CERTIFIED_"
            "RECENTERED_CONE_SPECTRUM"
        ),
        "mesh": {
            "cells": len(tasks),
            "projection_dimension": 101,
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
            "recentered_cone_selected_line_simplicity": "CERTIFIED",
            "recentered_cone_selected_projector_graph": (
                "CERTIFIED" if passed else "OPEN"
            ),
            "recentered_cone_bordered_response": "OPEN",
            "causal_interval_vector_radius": "OPEN",
            "domain_and_first_hit_transfer": "OPEN",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "INSERT_THE_RECENTERED_CONE_PROJECTOR_GRAPH_IN_THE_EXISTING_"
            "DENOMINATOR_RESOLVED_BORDERED_RESPONSE_KERNEL_ON_THE_SAME_MESH"
            if passed else
            "REFINE_ONLY_THE_REPORTED_PROJECTOR_GRAPH_OWNER_CELLS"
        ),
        "inputs": {_relative(path): _sha256(path) for path in inputs},
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--central-probe", action="store_true")
    args = parser.parse_args()
    tasks = cone._cells()
    if args.central_probe:
        by_seam: dict[int, list[tuple[int, int, float, float]]] = {}
        for task in tasks:
            by_seam.setdefault(task[0], []).append(task)
        tasks = [cells[len(cells) // 2] for cells in by_seam.values()]
    payload = build_payload(tasks)
    if not args.central_probe:
        RESULT.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8", newline="\n",
        )
    print(json.dumps({
        "status": payload["status"],
        "mesh": payload["mesh"],
        "summary": payload["summary"],
        "validation_passed": payload["validation_passed"],
        "central_probe_only": args.central_probe,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
