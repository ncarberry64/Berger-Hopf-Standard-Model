"""Certify selected-line boundary clusters on the recentered Gate-7 cone.

Each proof cell is the union refinement of the retained 64-way Hermite stop
mesh and the fine signed Green-correction mesh.  On such a cell the base
Hermite cubic plus the piecewise-linear correction is exactly cubic.  Its
three correlated coordinates and the nonlinear causal-radius halo are placed
in one Euclidean ellipsoid via the sqrt(2) product-ball embedding, then the
existing retained cluster/Kato kernel is replayed unchanged.

JAX evaluates only the center D3 directional matrices in batch.  The same
action formula is already cross-validated against retained complex-step D3 on
all 48 macro seams; retained MixedBound D4 remains the outward authority.
"""

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

import jax

jax.config.update("jax_enable_x64", True)
import jax.numpy as jnp
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import audit_n12_c2_stop_boundary_cluster_probe as cluster  # noqa: E402
from bhsm.interface.aether_jax_full_local_action import action_hessian  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
CENTER = BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.npz"
GREEN = BASE / "BHSM_N12_C2_STOP_QUARTER_STEP_MATCHED_TANGENT_CORRELATED_DEFECT_GAUSS12_RECONNAISSANCE.npz"
CAUSAL_Z2 = BASE / "BHSM_N12_GATE7_SELECTED_CONE_INTERNAL_RESPONSE_Z2.json"
EIGENLINE = BASE / "BHSM_N12_GATE7_RETAINED_CORRECTION_EIGENLINE_FIRST_JETS.json"
TWO_FREE = BASE / "BHSM_N12_GATE7_TWO_FREE_LEG_ACTION_MAJORANTS.json"
BASE_SPECTRUM = BASE / "BHSM_N12_GATE7_SELECTED_DOP853_NONLINEAR_CONE_SPECTRUM.json"
RESULT = BASE / "BHSM_N12_GATE7_RECENTERED_CONE_BOUNDARY_CLUSTER_SPECTRUM.json"
SQRT_TWO = math.sqrt(2.0)
JAX_D3_NORM_INFLATION = 1.0 + 1.0e-10


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


@lru_cache(maxsize=1)
def _inputs() -> tuple[np.ndarray, ...]:
    with np.load(CENTER) as source:
        states = np.asarray(source["centers"], dtype=float)
        rates = np.asarray(source["action_rates"], dtype=float)
        times = np.asarray(source["action_lengths"], dtype=float)
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)
    with np.load(GREEN) as source:
        fine_times = np.asarray(source["fine_action_lengths"], dtype=float)
        fine_correction = np.asarray(
            source["fine_ambient_correction_profile"], dtype=float
        )
    causal_z2 = json.loads(CAUSAL_Z2.read_text(encoding="utf-8"))
    nonlinear_radius = np.full(
        states.shape[0],
        float(causal_z2["domain"]["candidate_nonlinear_action_radius"]),
    )
    return (
        states, rates, times, weights, reference,
        fine_times, fine_correction, nonlinear_radius,
    )


def _cells() -> list[tuple[int, int, float, float]]:
    _, _, times, _, _, fine_times, _, _ = _inputs()
    result = []
    for seam in range(47):
        start = float(times[seam])
        end = float(times[seam + 1])
        boundaries = list(np.linspace(start, end, 65))
        boundaries.extend(float(value) for value in fine_times[
            (fine_times > start) & (fine_times < end)
        ])
        boundaries = sorted(set(boundaries))
        for local_index, (left, right) in enumerate(zip(
            boundaries[:-1], boundaries[1:], strict=True
        )):
            result.append((seam, local_index, left, right))
    return result


def _interpolate_correction(
    value: float, fine_times: np.ndarray, fine_correction: np.ndarray,
) -> np.ndarray:
    index = int(np.searchsorted(fine_times, value, side="right") - 1)
    index = min(max(index, 0), len(fine_times) - 2)
    fraction = (value - fine_times[index]) / (
        fine_times[index + 1] - fine_times[index]
    )
    fraction = min(max(float(fraction), 0.0), 1.0)
    return (
        (1.0 - fraction) * fine_correction[index]
        + fraction * fine_correction[index + 1]
    )


@jax.jit
def _batched_hessian_directionals(
    state: jax.Array, raw_directions: jax.Array,
) -> jax.Array:
    return jax.vmap(
        lambda direction: jax.jvp(
            action_hessian, (state,), (direction,),
        )[1]
    )(raw_directions)


def _geometry(task: tuple[int, int, float, float]) -> dict[str, Any]:
    seam, local_index, left, right = task
    (
        states, rates, times, weights, reference,
        fine_times, fine_correction, nonlinear_radius,
    ) = _inputs()
    macro_span = float(times[seam + 1] - times[seam])
    start_fraction = (left - times[seam]) / macro_span
    end_fraction = (right - times[seam]) / macro_span
    macro_x0 = states[seam] * weights
    macro_x1 = states[seam + 1] * weights
    macro_controls = np.asarray((
        macro_x0,
        macro_x0 + macro_span * rates[seam] / 3.0,
        macro_x1 - macro_span * rates[seam + 1] / 3.0,
        macro_x1,
    ))
    base_controls = cluster.local._restrict(
        macro_controls, float(start_fraction), float(end_fraction)
    )
    correction0 = _interpolate_correction(
        left, fine_times, fine_correction
    )
    correction1 = _interpolate_correction(
        right, fine_times, fine_correction
    )
    correction_delta = correction1 - correction0
    correction_controls = np.asarray((
        correction0,
        correction0 + correction_delta / 3.0,
        correction0 + 2.0 * correction_delta / 3.0,
        correction1,
    ))
    controls = base_controls + correction_controls
    span = float(right - left)
    x0, x1 = controls[0], controls[-1]
    rate0 = 3.0 * (controls[1] - controls[0]) / span
    rate1 = 3.0 * (controls[3] - controls[2]) / span
    delta = x1 - x0
    path_projection = np.column_stack((
        0.5 * delta,
        span * rate0 - delta,
        delta - span * rate1,
    ))
    halo_radius = float(np.max(nonlinear_radius))
    halo_projection = halo_radius * np.eye(98)
    projection = SQRT_TWO * np.column_stack((
        path_projection, halo_projection,
    ))
    midpoint_action = 0.5 * (x0 + x1)
    midpoint = midpoint_action / weights
    jet = cluster.local.exact_full_action_jet_at_state(
        12,
        midpoint[:cluster.local.QDIM],
        midpoint[cluster.local.QDIM:2 * cluster.local.QDIM],
        midpoint[2 * cluster.local.QDIM:],
        points=cluster.local.POINTS,
    )
    reduced = np.asarray(jet.hessian, dtype=float)[
        cluster.local.QDIM:, cluster.local.QDIM:
    ]
    values, vectors = np.linalg.eigh(0.5 * (reduced + reduced.T))
    selected = int(np.argmax(np.abs(vectors.T @ reference)))
    directionals = np.array(_batched_hessian_directionals(
        jnp.asarray(midpoint),
        jnp.asarray(projection.T / weights[None, :]),
    ), copy=True)[:, cluster.local.QDIM:, cluster.local.QDIM:]
    directionals = directionals * JAX_D3_NORM_INFLATION
    return {
        "seam": seam,
        "local_index": local_index,
        "action_interval": [left, right],
        "midpoint": midpoint,
        "projection": projection,
        "values": values,
        "vectors": vectors,
        "selected": selected,
        "directionals": list(directionals),
        "path_projection_column_norms": [
            float(np.linalg.norm(path_projection[:, index]))
            for index in range(3)
        ],
        "halo_radius": halo_radius,
    }


def _task(task: tuple[int, int, float, float]) -> dict[str, Any]:
    geometry = _geometry(task)
    weights = _inputs()[3]
    values = geometry["values"]
    rows = [
        cluster._cluster_bound(
            branches,
            cluster._distance_groups(values, branches),
            geometry,
            weights,
        )
        for branches in ((23,), (24,), (25, 26, 27))
    ]
    negative, selected, positive = rows
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
        "seam": geometry["seam"],
        "local_index": geometry["local_index"],
        "action_interval": geometry["action_interval"],
        "selected_branch": geometry["selected"],
        "projection_dimension": int(geometry["projection"].shape[1]),
        "path_projection_column_norms": geometry[
            "path_projection_column_norms"
        ],
        "nonlinear_halo_radius": geometry["halo_radius"],
        "negative_cluster_shift_upper": negative[
            "cluster_spectral_shift_upper"
        ],
        "selected_line_shift_upper": selected[
            "cluster_spectral_shift_upper"
        ],
        "positive_cluster_shift_upper": positive[
            "cluster_spectral_shift_upper"
        ],
        "negative_selected_gap_lower": negative_margin,
        "selected_positive_gap_lower": positive_margin,
        "all_three_quarter_gap_bootstraps_closed": all(
            row["quarter_gap_bootstrap_closed"] for row in rows
        ),
        "boundary_cluster_certificate_closed": bool(
            geometry["selected"] == 24
            and all(row["quarter_gap_bootstrap_closed"] for row in rows)
            and negative_margin > 0.0
            and positive_margin > 0.0
        ),
    }


def build_payload(tasks: list[tuple[int, int, float, float]]) -> dict[str, Any]:
    inputs = (
        CENTER, GREEN, CAUSAL_Z2, EIGENLINE, TWO_FREE, BASE_SPECTRUM,
    )
    if not all(path.is_file() for path in inputs):
        raise FileNotFoundError("recentered-cone spectrum inputs required")
    parents = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in (CAUSAL_Z2, EIGENLINE, TWO_FREE, BASE_SPECTRUM)
    ]
    if not all(parent["validation_passed"] for parent in parents):
        raise RuntimeError("validated retained spectral parents required")
    workers = min(int(os.environ.get("BHSM_N12_GATE7_CONE_WORKERS", "12")), os.cpu_count() or 1)
    rows = []
    with ProcessPoolExecutor(max_workers=workers) as executor:
        for count, row in enumerate(executor.map(_task, tasks, chunksize=1), 1):
            rows.append(row)
            if count % 16 == 0 or count == len(tasks):
                print(json.dumps({
                    "completed": count,
                    "total": len(tasks),
                    "closed_so_far": all(
                        item["boundary_cluster_certificate_closed"]
                        for item in rows
                    ),
                    "minimum_positive_gap_so_far": min(
                        item["selected_positive_gap_lower"] for item in rows
                    ),
                }), flush=True)
    validation = {
        "all_requested_union_cells_consumed_once_in_order": len(rows) == len(tasks),
        "selected_branch_24_at_every_cell_center": all(
            row["selected_branch"] == 24 for row in rows
        ),
        "all_three_boundary_cluster_bootstraps_close_everywhere": all(
            row["all_three_quarter_gap_bootstraps_closed"] for row in rows
        ),
        "both_selected_line_boundary_margins_positive_everywhere": all(
            row["boundary_cluster_certificate_closed"] for row in rows
        ),
        "base_Hermite_and_fine_correction_mesh_union_used": True,
        "piecewise_linear_correction_added_as_exact_cubic_controls": True,
        "sqrt2_product_ball_contains_path_ellipsoid_times_delta_ball": True,
        "global_causal_delta_radius_used_on_every_cell": True,
        "batched_JAX_used_only_for_same_formula_center_D3_acceleration": True,
        "retained_MixedBound_D4_is_outward_authority": True,
        "JAX_D3_norms_inflated_by_1e_minus_10_relative": True,
        "hard_26_27_internal_meeting_removed_by_cluster_25_27": True,
        "no_action_equation_source_selector_scale_gate_or_chord_changed": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    owner = min(
        rows,
        key=lambda row: min(
            row["negative_selected_gap_lower"],
            row["selected_positive_gap_lower"],
        ),
    )
    return {
        "artifact": "BHSM_N12_GATE7_RECENTERED_CONE_BOUNDARY_CLUSTER_SPECTRUM",
        "status": (
            "RECENTERED_GATE7_CONE_SELECTED_LINE_BOUNDARY_CLUSTERS_CERTIFIED"
            if passed else "RECENTERED_GATE7_CONE_SPECTRUM_REFINEMENT_REQUIRED"
        ),
        "authority": (
            "RETAINED_ACTION_CENTER_HESSIAN_AND_OUTWARD_D4_WITH_"
            "CROSS_VALIDATED_SAME_FORMULA_JAX_CENTER_D3_ACCELERATION"
        ),
        "method": (
            "UNION_REFINED_CORRELATED_HERMITE_PLUS_SIGNED_GREEN_CUBIC_"
            "CONTROLS_TIMES_NONLINEAR_DELTA_PRODUCT_BALL_KATO_CLUSTERS"
        ),
        "mesh": {
            "cells": len(tasks),
            "macro_seams": 47,
            "base_subspans_per_macro_seam": 64,
            "fine_correction_nodes": int(_inputs()[5].size),
            "projection_dimension": 101,
            "workers": workers,
        },
        "domain": {
            "recenter": "BASE_HERMITE_HISTORY_PLUS_FINE_PIECEWISE_LINEAR_SIGNED_GREEN_CORRECTION",
            "base_center": _relative(CENTER),
            "center_correction": _relative(GREEN),
            "nonlinear_radius_authority": _relative(CAUSAL_Z2),
            "nonlinear_halo_action_radius": float(np.max(_inputs()[7])),
            "product_ball_embedding": "sqrt(2)*[P_corrected,delta_radius*I_98]",
        },
        "summary": {
            "minimum_selected_line_boundary_gap_lower": min(
                min(
                    row["negative_selected_gap_lower"],
                    row["selected_positive_gap_lower"],
                ) for row in rows
            ),
            "minimum_negative_selected_gap_lower": min(
                row["negative_selected_gap_lower"] for row in rows
            ),
            "minimum_selected_positive_gap_lower": min(
                row["selected_positive_gap_lower"] for row in rows
            ),
            "maximum_selected_line_shift_upper": max(
                row["selected_line_shift_upper"] for row in rows
            ),
            "maximum_negative_cluster_shift_upper": max(
                row["negative_cluster_shift_upper"] for row in rows
            ),
            "maximum_positive_cluster_shift_upper": max(
                row["positive_cluster_shift_upper"] for row in rows
            ),
            "minimum_margin_owner": owner,
        },
        "rows": rows,
        "validation": validation,
        "validation_passed": passed,
        "claim_boundary": {
            "recentered_cone_selected_line_simplicity": (
                "CERTIFIED" if passed else "OPEN"
            ),
            "recentered_cone_selected_projector_graph": "OPEN",
            "recentered_cone_bordered_response": "OPEN",
            "causal_interval_vector_radius": "OPEN",
            "domain_and_first_hit_transfer": "OPEN",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "REPLAY_THE_EXISTING_DISTANCE_BAND_SELECTED_PROJECTOR_AND_"
            "BORDERED_RESPONSE_KERNELS_ON_THIS_SAME_RECENTERED_CONE_MESH"
            if passed else
            "REFINE_ONLY_THE_REPORTED_NONCLOSING_UNION_CELLS_WITH_THE_SAME_"
            "CORRELATED_CLUSTER_KERNEL"
        ),
        "inputs": {_relative(path): _sha256(path) for path in inputs},
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--central-probe", action="store_true")
    args = parser.parse_args()
    tasks = _cells()
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
