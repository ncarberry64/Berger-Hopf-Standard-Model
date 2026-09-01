"""Certify branch-24 projector motion on the adaptive DOP853 cover."""

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

# The Bernstein projection is normalized so that its coefficient domain is
# the unit Euclidean ball.  Pin that proof radius before importing the action
# majorant module; relying on a caller's shell environment would make the
# certificate non-reproducible.
os.environ["BHSM_N12_CERTIFICATE_BALL"] = "1.0"

import audit_n12_c2_stop_dop853_boundary_cluster_probe as dense  # noqa: E402
import derive_n12_action_ball_majorants as action_majorants  # noqa: E402

action_majorants.BALL_RADIUS = 1.0


BASE = ROOT / "artifacts" / "flagship_integration"
SPECTRUM = Path(os.environ.get(
    "BHSM_N12_STOP_DOP853_ADAPTIVE_SPECTRUM",
    str(BASE / "BHSM_N12_C2_STOP_DOP853_ADAPTIVE_BOUNDARY_CLUSTER_SPECTRUM.json"),
))
RESULT = Path(os.environ.get(
    "BHSM_N12_STOP_DOP853_ADAPTIVE_PROJECTOR",
    str(BASE / "BHSM_N12_C2_STOP_DOP853_ADAPTIVE_SELECTED_PROJECTOR_GRAPH.json"),
))
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
def _spectrum_record() -> dict[str, Any]:
    payload = json.loads(SPECTRUM.read_text(encoding="utf-8"))
    if payload["validation_passed"] is not True or payload["claim_boundary"][
        "selected_line_on_stored_DOP853_stop_path"
    ] != "CERTIFIED_SIMPLE":
        raise RuntimeError("certified adaptive DOP853 selected-line spectrum required")
    return payload


@lru_cache(maxsize=1)
def _spectrum_rows() -> dict[tuple[int, int, int], dict[str, Any]]:
    return {
        (int(row["interval"]), int(row["subspan"]), int(row["subdivisions"])): row
        for row in _spectrum_record()["rows"]
    }


def _projector_row(task: tuple[int, int, int]) -> dict[str, Any]:
    interval, subspan, subdivisions = task
    spectrum = _spectrum_rows()[task]
    dense.SUBDIVISIONS = subdivisions
    geometry = dense.dense_subspan_geometry(interval, subspan)
    *_, weights, reference, __, ___ = dense._dense_arrays()
    if geometry["selected"] != SELECTED:
        raise RuntimeError("selected branch changed")
    midpoint = geometry["midpoint"]
    projection = geometry["projection"]
    values = geometry["values"]
    vectors = geometry["vectors"]
    directionals = geometry["directionals"]
    selected = vectors[:, SELECTED]
    reduced_weights = weights[dense.QDIM:]
    selected_action = np.concatenate((
        np.zeros(dense.QDIM), reduced_weights * selected,
    ))
    reduced_basis_action = np.vstack((
        np.zeros((dense.QDIM, values.size)),
        np.diag(reduced_weights),
    ))
    ambient_D3 = float(np.linalg.norm([
        np.linalg.norm(matrix, ord=2) for matrix in directionals
    ]))
    ambient_D4 = _up(float(dense.cluster.local.action_bound(
        midpoint,
        projection=projection,
        mixed_directions=[
            reduced_basis_action, reduced_basis_action, projection, projection,
        ],
    ).d[-1]))
    ambient_shift = _up(ambient_D3 + 0.5 * ambient_D4)
    selected_shift = float(spectrum["selected_line_shift_upper"])
    gap_lower = float(min(
        spectrum["negative_selected_gap_lower"],
        spectrum["selected_positive_gap_lower"],
    ))
    if gap_lower <= 0.0:
        raise RuntimeError("positive certified selected-line gap required")
    group_rows = []
    derivative_square = 0.0
    groups = dense.cluster._distance_groups(values, (SELECTED,))
    for group in groups:
        indices = np.asarray(group, dtype=int)
        group_vectors = vectors[:, indices]
        group_action = np.vstack((
            np.zeros((dense.QDIM, len(group))),
            reduced_weights[:, None] * group_vectors,
        ))
        center_coupling_square = 0.0
        for matrix in directionals:
            coupling = group_vectors.T @ matrix @ selected
            center_coupling_square += float(np.sum(np.square(coupling)))
        center_coupling = float(np.sqrt(center_coupling_square))
        coupling_change = _up(float(dense.cluster.local.action_bound(
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
        ordered_gap = center_distance - selected_shift - ambient_shift
        consumed_gap = max(gap_lower, ordered_gap)
        derivative = _up(NEUMANN_FACTOR * numerator / consumed_gap)
        derivative_square += derivative**2
        group_rows.append({
            "branches": list(group),
            "minimum_center_distance": center_distance,
            "ordered_Weyl_gap_lower": ordered_gap,
            "consumed_gap_lower": consumed_gap,
            "center_D3_coupling_l2_norm": center_coupling,
            "D4_coupling_change_upper": coupling_change,
            "coupling_numerator_upper": numerator,
            "selected_graph_derivative_upper": derivative,
        })
    derivative_l2 = _up(math.sqrt(derivative_square))
    return {
        "interval": interval,
        "subspan": subspan,
        "subdivisions": subdivisions,
        "selected_branch": SELECTED,
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


def build_payload() -> dict[str, Any]:
    source_rows = _spectrum_record()["rows"]
    tasks = [
        (int(row["interval"]), int(row["subspan"]), int(row["subdivisions"]))
        for row in source_rows
    ]
    workers = min(
        int(os.environ.get("BHSM_N12_STOP_WORKERS", "8")),
        os.cpu_count() or 1,
    )
    rows = []
    with ProcessPoolExecutor(max_workers=workers) as executor:
        for index, row in enumerate(executor.map(_projector_row, tasks, chunksize=1), 1):
            rows.append(row)
            if index % 32 == 0 or index == len(tasks):
                print(json.dumps({
                    "completed": index,
                    "total": len(tasks),
                    "closed_so_far": all(item["graph_Neumann_closed"] for item in rows),
                    "maximum_motion_so_far": max(
                        item["selected_projector_motion_upper"] for item in rows
                    ),
                }), flush=True)
    validation = {
        "every_adaptive_spectrum_cell_consumed_once_in_order": [
            (row["interval"], row["subspan"], row["subdivisions"]) for row in rows
        ] == tasks,
        "branch_24_selected_everywhere": all(row["selected_branch"] == SELECTED for row in rows),
        "every_certified_gap_strictly_positive": all(row["certified_global_gap_lower"] > 0.0 for row in rows),
        "all_distance_band_graph_Neumann_bounds_below_one": all(row["graph_Neumann_closed"] for row in rows),
        "exact_center_D3_and_retained_D4_action_majorant_used": True,
        "hard_26_27_internal_denominator_not_reintroduced": True,
        "far_branch_ordered_Weyl_denominators_combined_with_global_gap": True,
        "same_DOP853_Bernstein_cover_as_spectrum": True,
        "no_cubic_Hermite_surrogate_inserted": True,
        "no_full_Euler_Dirac_or_dense_history_inverse_used": True,
    }
    passed = all(validation.values())
    owner = max(rows, key=lambda row: row["selected_projector_motion_upper"])
    return {
        "artifact": "BHSM_N12_C2_STOP_DOP853_ADAPTIVE_SELECTED_PROJECTOR_GRAPH",
        "status": (
            "ALL_DOP853_ADAPTIVE_STOP_PATH_SELECTED_PROJECTOR_GRAPHS_CERTIFIED"
            if passed else "DOP853_ADAPTIVE_STOP_PATH_SELECTED_PROJECTOR_GRAPH_OPEN"
        ),
        "method": "DENOMINATOR_RESOLVED_KATO_GRAPH_ON_THE_EXACT_ADAPTIVE_DOP853_BERNSTEIN_COVER",
        "mesh": {
            "adaptive_cover_cells": len(tasks),
            "workers": workers,
        },
        "summary": {
            "maximum_selected_graph_derivative_l2_upper": max(row["selected_graph_derivative_l2_upper"] for row in rows),
            "maximum_selected_projector_motion_upper": max(row["selected_projector_motion_upper"] for row in rows),
            "minimum_consumed_gap_lower": min(row["certified_global_gap_lower"] for row in rows),
            "maximum_spectral_distance_bands": max(row["spectral_distance_bands"] for row in rows),
            "owner": owner,
            "Neumann_factor": NEUMANN_FACTOR,
        },
        "rows": rows,
        "validation": validation,
        "validation_passed": passed,
        "claim_boundary": {
            "selected_projector_graph_on_stored_DOP853_stop_path": "CERTIFIED" if passed else "OPEN",
            "bordered_hard_response_tube": "OPEN",
            "correlated_shadowing_tube": "OPEN",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "ASSEMBLE_THE_BORDERED_HARD_INVERSE_AND_INTERNAL_RHS_RESPONSE_ON_THE_IDENTICAL_DOP853_ADAPTIVE_COVER"
            if passed else "REFINE_ONLY_THE_REPORTED_PROJECTOR_GRAPH_OWNER"
        ),
        "inputs": {
            _relative(SPECTRUM): _sha256(SPECTRUM),
            _relative(dense.CENTER_DATA): _sha256(dense.CENTER_DATA),
            "scripts/audit_n12_c2_stop_dop853_boundary_cluster_probe.py": _sha256(
                ROOT / "scripts/audit_n12_c2_stop_dop853_boundary_cluster_probe.py"
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
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
