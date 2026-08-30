"""Replay the retained recentered-cone spectrum on the exact-affine center.

The retained spectral/Kato kernel is imported unchanged.  This adapter swaps
only the historically incompatible Gauss-12 correction for the certified
371-node exact-affine signed-source midpoint and includes its outward Arb
radius in the nonlinear product-ball halo.  Worker tasks are defined in this
module so Windows process spawning preserves that exact-center routing.
"""

from __future__ import annotations

import argparse
from functools import lru_cache
import json
import math
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import certify_n12_gate7_recentered_cone_boundary_cluster_spectrum as cone  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
FINE = BASE / "BHSM_N12_GATE7_ARB_INTERACTION_TAYLOR26_FINE_CENTER.npz"
FINE_RECORD = FINE.with_suffix(".json")
RESULT = BASE / (
    "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_BOUNDARY_CLUSTER_SPECTRUM.json"
)
_RETAINED_TASK = cone._task


@lru_cache(maxsize=1)
def _inputs() -> tuple[np.ndarray, ...]:
    with np.load(cone.CENTER) as source:
        states = np.asarray(source["centers"], dtype=float)
        rates = np.asarray(source["action_rates"], dtype=float)
        times = np.asarray(source["action_lengths"], dtype=float)
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)
    with np.load(FINE) as source:
        fine_times = np.asarray(source["fine_action_lengths"], dtype=float)
        fine_correction = np.asarray(
            source["fine_signed_response_midpoint"], dtype=float,
        )
        fine_radius = np.asarray(
            source["fine_signed_response_Euclidean_radius"], dtype=float,
        )
    causal_z2 = json.loads(cone.CAUSAL_Z2.read_text(encoding="utf-8"))
    candidate_radius = float(
        causal_z2["domain"]["candidate_nonlinear_action_radius"]
    )
    halo = math.nextafter(
        candidate_radius + float(np.max(fine_radius)), math.inf,
    )
    nonlinear_radius = np.full(states.shape[0], halo)
    return (
        states, rates, times, weights, reference,
        fine_times, fine_correction, nonlinear_radius,
    )


def _task(task: tuple[int, int, float, float]) -> dict[str, Any]:
    return _RETAINED_TASK(task)


# These assignments are repeated when a Windows worker imports this module.
cone.GREEN = FINE
cone.RESULT = RESULT
cone._inputs = _inputs
cone._task = _task


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--central-probe", action="store_true")
    args = parser.parse_args()
    if not FINE.is_file() or not FINE_RECORD.is_file():
        raise FileNotFoundError("certified exact-affine fine center required")
    fine_record = json.loads(FINE_RECORD.read_text(encoding="utf-8"))
    if fine_record.get("validation_passed") is not True:
        raise RuntimeError("validated exact-affine fine center required")

    tasks = cone._cells()
    if args.central_probe:
        by_seam: dict[int, list[tuple[int, int, float, float]]] = {}
        for task in tasks:
            by_seam.setdefault(task[0], []).append(task)
        tasks = [cells[len(cells) // 2] for cells in by_seam.values()]
    payload = cone.build_payload(tasks)
    payload["artifact"] = (
        "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_BOUNDARY_CLUSTER_SPECTRUM"
    )
    if payload["validation_passed"]:
        payload["status"] = (
            "EXACT_AFFINE_CENTER_GATE7_CONE_SELECTED_LINE_BOUNDARY_CLUSTERS_"
            "CERTIFIED"
        )
    payload["authority"] = (
        "RETAINED_ACTION_KATO_CLUSTER_KERNEL_ON_THE_256_BIT_ARB_EXACT_AFFINE_"
        "FINE_CENTER_WITH_ITS_OUTWARD_RADIUS_INCLUDED"
    )
    payload["method"] = (
        "UNION_REFINED_CORRELATED_HERMITE_PLUS_EXACT_AFFINE_FINE_CENTER_"
        "CONTROLS_TIMES_NONLINEAR_PRODUCT_BALL_KATO_CLUSTERS"
    )
    payload["domain"].update({
        "recenter": (
            "BASE_HERMITE_HISTORY_PLUS_FINE_PIECEWISE_LINEAR_EXACT_AFFINE_CENTER"
        ),
        "center_correction": cone._relative(FINE),
        "exact_center_interval_radius_included": True,
    })
    payload["validation"].update({
        "exact_affine_fine_center_parent_validated": True,
        "exact_affine_center_Arb_radius_included_in_product_ball_halo": True,
        "historical_Gauss12_recenter_not_consumed": True,
    })
    payload["validation_passed"] = all(payload["validation"].values())
    payload["exact_next_dependency"] = (
        "REPLAY_THE_EXISTING_DISTANCE_BAND_PROJECTOR_AND_BORDERED_RESPONSE_"
        "KERNELS_ON_THIS_EXACT_AFFINE_RECENTERED_CONE_MESH"
        if payload["validation_passed"] else
        payload["exact_next_dependency"]
    )
    payload["inputs"][cone._relative(FINE_RECORD)] = cone._sha256(FINE_RECORD)
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
