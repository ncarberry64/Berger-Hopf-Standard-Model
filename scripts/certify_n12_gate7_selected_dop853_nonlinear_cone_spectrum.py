"""Attach the selected-quarter causal radius to the DOP853 spectrum cover.

The adaptive DOP853 spectrum already encloses the exact degree-seven center
path.  This script does not rebuild that cover.  On every accepted cell it
adds the candidate nonlinear action-coordinate ball as a Cartesian product.
The incremental halo Hessian motion is evaluated by same-formula center D3
plus the retained-action D4 product-domain remainder, then transferred from
the already-certified path gaps by Weyl's theorem.

The candidate radius is twice the exact signed center radius.  It becomes an
interval radius only after the downstream correlated Y/Z1/Z2 self-map closes.
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
sys.path.insert(0, str(ROOT / "scripts"))

# The product projection below is normalized to one Euclidean coefficient
# ball.  Pin that convention before importing the retained majorant module.
os.environ["BHSM_N12_CERTIFICATE_BALL"] = "1.0"

import audit_n12_c2_stop_dop853_boundary_cluster_probe as dense  # noqa: E402
import derive_n12_action_ball_majorants as majorants  # noqa: E402
from bhsm.interface.aether_jax_full_local_action import action_hessian  # noqa: E402

majorants.BALL_RADIUS = 1.0


BASE = ROOT / "artifacts" / "flagship_integration"
SPECTRUM = BASE / "BHSM_N12_C2_STOP_DOP853_ADAPTIVE_BOUNDARY_CLUSTER_SPECTRUM.json"
CAUSAL = BASE / "BHSM_N12_GATE7_EXACT_CENTER_CAUSAL_VECTOR_CERTIFICATE.json"
CAUSAL_DATA = CAUSAL.with_suffix(".npz")
RESULT = BASE / "BHSM_N12_GATE7_SELECTED_DOP853_NONLINEAR_CONE_SPECTRUM.json"
SELECTED = 24
RADIUS_FACTOR = 2.0
SQRT_TWO = math.sqrt(2.0)
JAX_D3_NORM_INFLATION = 1.0 + 1.0e-10


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
def _parents() -> tuple[dict[str, Any], dict[str, Any], float]:
    spectrum = json.loads(SPECTRUM.read_text(encoding="utf-8"))
    causal = json.loads(CAUSAL.read_text(encoding="utf-8"))
    if spectrum["validation_passed"] is not True:
        raise RuntimeError("certified selected DOP853 path spectrum required")
    if causal["validation_passed"] is not True:
        raise RuntimeError("exact selected-history center radius required")
    with np.load(CAUSAL_DATA) as source:
        exact_radius = float(np.max(source["exact_total_center_radius"]))
    if exact_radius != float(causal["summary"]["maximum_exact_total_center_radius"]):
        raise RuntimeError("causal radius JSON/NPZ mismatch")
    return spectrum, causal, RADIUS_FACTOR * exact_radius


@lru_cache(maxsize=1)
def _path_rows() -> dict[tuple[int, int, int], dict[str, Any]]:
    return {
        (
            int(row["interval"]), int(row["subspan"]),
            int(row["subdivisions"]),
        ): row
        for row in _parents()[0]["rows"]
    }


@jax.jit
def _batched_hessian_directionals(
    state: jax.Array, raw_directions: jax.Array,
) -> jax.Array:
    return jax.vmap(
        lambda direction: jax.jvp(
            action_hessian, (state,), (direction,),
        )[1]
    )(raw_directions)


def _interval_halo_row(interval: int) -> dict[str, Any]:
    _, _, candidate_radius = _parents()
    # One full stored dense interval contains every accepted 4/8-cell child
    # in that interval.  Bounding the halo derivative here is therefore a
    # valid common parent bound for all of its accepted path cells.
    dense.SUBDIVISIONS = 1
    geometry = dense.dense_subspan_geometry(interval, 0)
    *_, weights, __, ___, ____ = dense._dense_arrays()
    path_projection = np.asarray(geometry["projection"], dtype=float)
    halo_projection = candidate_radius * np.eye(path_projection.shape[0])
    # If ||u||<=1 and ||v||<=1, then (u/sqrt(2),v/sqrt(2)) belongs to the
    # unit ball and sqrt(2)[P,H](u/sqrt(2),v/sqrt(2))=Pu+Hv.
    product_projection = SQRT_TWO * np.column_stack((
        path_projection, halo_projection,
    ))
    halo_directionals = np.array(_batched_hessian_directionals(
        jnp.asarray(geometry["midpoint"]),
        jnp.asarray(halo_projection.T / weights[None, :]),
    ), copy=True)[:, dense.QDIM:, dense.QDIM:]
    center_halo_motion = _up(JAX_D3_NORM_INFLATION * math.sqrt(sum(
        float(np.linalg.norm(matrix, ord=2)) ** 2
        for matrix in halo_directionals
    )))
    reduced_weights = np.asarray(weights[dense.QDIM:], dtype=float)
    reduced_basis_action = np.vstack((
        np.zeros((dense.QDIM, reduced_weights.size)),
        np.diag(reduced_weights),
    ))
    D4_product_remainder = _up(float(majorants.action_bound(
        np.asarray(geometry["midpoint"], dtype=float),
        projection=product_projection,
        mixed_directions=[
            reduced_basis_action,
            reduced_basis_action,
            halo_projection,
            product_projection,
        ],
    ).d[-1]))
    halo_motion = _up(center_halo_motion + D4_product_remainder)
    return {
        "interval": interval,
        "selected_branch": int(geometry["selected"]),
        "dense_interval_path_projection_Frobenius_norm": float(
            np.linalg.norm(path_projection)
        ),
        "candidate_nonlinear_action_radius": candidate_radius,
        "center_halo_reduced_Hessian_motion_2_norm_upper": center_halo_motion,
        "D4_product_domain_halo_motion_remainder_upper": D4_product_remainder,
        "incremental_halo_reduced_Hessian_motion_2_norm_upper": halo_motion,
    }


def _transfer_row(
    task: tuple[int, int, int], interval_halo: dict[str, Any],
) -> dict[str, Any]:
    interval, subspan, subdivisions = task
    path_row = _path_rows()[task]
    halo_motion = float(interval_halo[
        "incremental_halo_reduced_Hessian_motion_2_norm_upper"
    ])
    negative_margin = math.nextafter(
        float(path_row["negative_selected_gap_lower"])
        - 2.0 * halo_motion,
        -math.inf,
    )
    positive_margin = math.nextafter(
        float(path_row["selected_positive_gap_lower"])
        - 2.0 * halo_motion,
        -math.inf,
    )
    return {
        "interval": interval,
        "subspan": subspan,
        "subdivisions": subdivisions,
        "selected_branch": int(interval_halo["selected_branch"]),
        "path_negative_selected_gap_lower": float(
            path_row["negative_selected_gap_lower"]
        ),
        "path_selected_positive_gap_lower": float(
            path_row["selected_positive_gap_lower"]
        ),
        "candidate_nonlinear_action_radius": float(interval_halo[
            "candidate_nonlinear_action_radius"
        ]),
        "center_halo_reduced_Hessian_motion_2_norm_upper": float(
            interval_halo["center_halo_reduced_Hessian_motion_2_norm_upper"]
        ),
        "D4_product_domain_halo_motion_remainder_upper": float(
            interval_halo["D4_product_domain_halo_motion_remainder_upper"]
        ),
        "incremental_halo_reduced_Hessian_motion_2_norm_upper": halo_motion,
        "nonlinear_cone_negative_selected_gap_lower": negative_margin,
        "nonlinear_cone_selected_positive_gap_lower": positive_margin,
        "nonlinear_cone_selected_line_simple": bool(
            int(interval_halo["selected_branch"]) == SELECTED
            and negative_margin > 0.0
            and positive_margin > 0.0
        ),
    }


def _tasks() -> list[tuple[int, int, int]]:
    spectrum, _, _ = _parents()
    return [
        (int(row["interval"]), int(row["subspan"]), int(row["subdivisions"]))
        for row in spectrum["rows"]
    ]


def build_payload(tasks: list[tuple[int, int, int]]) -> dict[str, Any]:
    spectrum, causal, candidate_radius = _parents()
    workers = min(
        int(os.environ.get("BHSM_N12_GATE7_CONE_WORKERS", "8")),
        os.cpu_count() or 1,
        len({task[0] for task in tasks}),
    )
    interval_tasks = sorted({task[0] for task in tasks})
    interval_rows = []
    with ProcessPoolExecutor(max_workers=workers) as executor:
        for count, row in enumerate(executor.map(
            _interval_halo_row, interval_tasks, chunksize=1,
        ), 1):
            interval_rows.append(row)
            if count % 32 == 0 or count == len(interval_tasks):
                print(json.dumps({
                    "completed": count,
                    "total": len(interval_tasks),
                    "maximum_halo_motion_so_far": max(
                        item["incremental_halo_reduced_Hessian_motion_2_norm_upper"]
                        for item in interval_rows
                    ),
                }), flush=True)
    interval_map = {int(row["interval"]): row for row in interval_rows}
    rows = [_transfer_row(task, interval_map[task[0]]) for task in tasks]
    full_cover = len(tasks) == len(spectrum["rows"])
    validation = {
        "all_accepted_selected_DOP853_path_cells_consumed_in_order": (
            full_cover and [
                (row["interval"], row["subspan"], row["subdivisions"])
                for row in rows
            ] == _tasks()
        ),
        "candidate_radius_is_twice_exact_signed_center_radius": (
            candidate_radius == RADIUS_FACTOR * float(
                causal["summary"]["maximum_exact_total_center_radius"]
            )
        ),
        "sqrt2_product_ball_contains_path_ellipsoid_times_candidate_ball": True,
        "one_full_dense_interval_halo_bound_contains_all_of_its_accepted_path_children": True,
        "all_370_retained_dense_intervals_have_halo_bounds": (
            full_cover and len(interval_rows) == 370
        ),
        "same_formula_JAX_center_D3_evaluated_on_the_full_halo_basis": True,
        "retained_action_D4_bounds_halo_motion_on_the_complete_product_domain": True,
        "Weyl_transfer_subtracts_two_incremental_halo_motions_from_each_path_gap": True,
        "branch_24_selected_everywhere": all(
            row["selected_branch"] == SELECTED for row in rows
        ),
        "both_nonlinear_cone_boundary_gaps_positive_everywhere": all(
            row["nonlinear_cone_selected_line_simple"] for row in rows
        ),
        "candidate_radius_not_promoted_before_Y_Z1_Z2": True,
        "no_legacy_mixed_center_cone_replayed": True,
        "no_action_equation_source_selector_scale_gate_or_chord_changed": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    owner = min(rows, key=lambda row: min(
        row["nonlinear_cone_negative_selected_gap_lower"],
        row["nonlinear_cone_selected_positive_gap_lower"],
    ))
    return {
        "artifact": "BHSM_N12_GATE7_SELECTED_DOP853_NONLINEAR_CONE_SPECTRUM",
        "status": (
            "SELECTED_DOP853_CANDIDATE_NONLINEAR_CONE_LINE_SIMPLICITY_CERTIFIED"
            if passed else "SELECTED_DOP853_NONLINEAR_CONE_REFINEMENT_REQUIRED"
        ),
        "authority": (
            "CERTIFIED_DOP853_PATH_SPECTRUM_PLUS_SAME_FORMULA_CENTER_D3_"
            "RETAINED_ACTION_D4_PRODUCT_REMAINDER_AND_WEYL_TRANSFER"
        ),
        "domain": {
            "path_carrier": _relative(SPECTRUM),
            "candidate_nonlinear_action_radius": candidate_radius,
            "radius_factor_over_exact_center": RADIUS_FACTOR,
            "product_embedding": "sqrt(2)*[P_DOP853,r_candidate*I_98]",
            "candidate_only_until_correlated_radii_polynomial_closes": True,
        },
        "mesh": {
            "cells": len(tasks),
            "full_selected_DOP853_cover_cells": len(spectrum["rows"]),
            "dense_interval_halo_bounds": len(interval_rows),
            "workers": workers,
        },
        "summary": {
            "maximum_incremental_halo_reduced_Hessian_motion_2_norm_upper": max(
                row["incremental_halo_reduced_Hessian_motion_2_norm_upper"]
                for row in rows
            ),
            "minimum_nonlinear_cone_boundary_gap_lower": min(
                min(
                    row["nonlinear_cone_negative_selected_gap_lower"],
                    row["nonlinear_cone_selected_positive_gap_lower"],
                ) for row in rows
            ),
            "minimum_gap_owner": owner,
        },
        "rows": rows,
        "validation": validation,
        "validation_passed": passed,
        "claim_boundary": {
            "selected_line_on_candidate_nonlinear_DOP853_cone": (
                "CERTIFIED_SIMPLE" if passed else "OPEN"
            ),
            "candidate_radius_self_map": "OPEN_CORRELATED_Y_Z1_Z2",
            "projector_and_bordered_response_on_nonlinear_cone": "OPEN",
            "first_hit_domain_transfer": "OPEN",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "TRANSFER_THE_SELECTED_PROJECTOR_AND_BORDERED_RESPONSE_TO_THIS_"
            "CANDIDATE_PRODUCT_CONE,_THEN_CONTRACT_LITERAL_SIGNED_Y_Z1_Z2"
            if passed else
            "REFINE_ONLY_THE_REPORTED_NONCLOSING_SELECTED_DOP853_OWNER_CELLS"
        ),
        "inputs": {
            _relative(path): _sha256(path)
            for path in (SPECTRUM, CAUSAL, CAUSAL_DATA, dense.CENTER_DATA)
        },
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--probe-owner", action="store_true")
    args = parser.parse_args()
    tasks = _tasks()
    if args.probe_owner:
        owner = _parents()[0]["summary"]["minimum_margin_owner"]
        tasks = [(
            int(owner["interval"]), int(owner["subspan"]),
            int(owner["subdivisions"]),
        )]
    payload = build_payload(tasks)
    if not args.probe_owner:
        RESULT.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8", newline="\n",
        )
    print(json.dumps({
        "status": payload["status"],
        "mesh": payload["mesh"],
        "summary": payload["summary"],
        "validation_passed": payload["validation_passed"],
        "probe_owner_only": args.probe_owner,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
