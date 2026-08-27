"""Test the established termwise Kato spectrum proof on stop-path seams.

The local cubic Hermite curve lies in an exact three-coordinate action
ellipsoid.  This script evaluates raw-event D3 slopes and the retained D4
diagonal/coupling majorants branch by branch, following the already-certified
first-chord construction.  Representative seams are audited before the same
kernel is expanded to all 47 seams.
"""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import types
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
os.environ["BHSM_N12_CERTIFICATE_BALL"] = "1.0"

from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (  # noqa: E402
    exact_full_action_jet_at_state,
)


def _load_committed_majorant_module():
    relative = "scripts/derive_n12_action_ball_majorants.py"
    try:
        source = subprocess.check_output(
            ["git", "show", f"HEAD:{relative}"], cwd=ROOT
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        source = (ROOT / relative).read_bytes()
    module = types.ModuleType("bhsm_committed_action_majorants")
    module.__file__ = str(ROOT / relative)
    sys.modules[module.__name__] = module
    exec(compile(source, module.__file__, "exec"), module.__dict__)
    return module, hashlib.sha256(source.replace(b"\r\n", b"\n")).hexdigest().upper()


_MAJORANT, COMMITTED_MAJORANT_SHA256 = _load_committed_majorant_module()
action_bound = _MAJORANT.action_bound

BASE = ROOT / "artifacts" / "flagship_integration"
CENTER = BASE / "BHSM_N12_C2_STOP_MULTIPLE_SHOOTING_CENTER.json"
CENTER_DATA = CENTER.with_suffix(".npz")
KATO = BASE / "BHSM_N12_C2_STOP_KATO_RATE_PROFILE.json"
RESULT = BASE / "BHSM_N12_C2_STOP_LOCAL_TERMWISE_SPECTRUM.json"
QDIM = 37
POINTS = 96
COMPLEX_STEP = 1.0e-20
SEAMS = tuple(range(47))
SUBDIVISIONS = 64


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _branch_bound(args: tuple[Any, ...]) -> dict[str, Any]:
    (
        branch, midpoint, projection, values, vectors, directionals, weights,
    ) = args
    vector = vectors[:, branch]
    mask = np.arange(values.size) != branch
    complement = vectors[:, mask]
    reduced_weights = weights[QDIM:]
    vector_action = np.concatenate((np.zeros(QDIM), reduced_weights * vector))
    complement_action = np.vstack((
        np.zeros((QDIM, values.size - 1)),
        reduced_weights[:, None] * complement,
    ))
    diagonal_fourth = float(action_bound(
        midpoint,
        projection=projection,
        mixed_directions=[
            vector_action, vector_action, projection, projection,
        ],
    ).d[-1])
    coupling_fourth = float(action_bound(
        midpoint,
        projection=projection,
        mixed_directions=[
            vector_action, complement_action, projection, projection,
        ],
    ).d[-1])
    slopes = np.asarray([
        float(vector @ matrix @ vector) for matrix in directionals
    ])
    coupling = np.asarray([
        complement.T @ matrix @ vector for matrix in directionals
    ]).T
    gaps = np.abs(values[branch] - values[mask])
    denominator_lower = 0.5 * gaps
    weighted_center = float(np.sum(
        np.sum(coupling**2, axis=1) / denominator_lower
    ))
    curvature = float(
        diagonal_fourth
        + 2.0 * (
            math.sqrt(weighted_center)
            + coupling_fourth / math.sqrt(float(np.min(denominator_lower)))
        ) ** 2
    )
    shift = float(np.linalg.norm(slopes) + 0.5 * curvature)
    return {
        "branch": int(branch),
        "center_eigenvalue": float(values[branch]),
        "center_minimum_gap": float(np.min(gaps)),
        "three_coordinate_slope_norm": float(np.linalg.norm(slopes)),
        "diagonal_D4_upper": diagonal_fourth,
        "coupling_D4_upper": coupling_fourth,
        "Kato_curvature_upper": curvature,
        "total_branch_shift_upper": shift,
        "half_gap_bootstrap": shift < 0.25 * float(np.min(gaps)),
    }


def _split(control: np.ndarray, t: float) -> tuple[np.ndarray, np.ndarray]:
    levels = [np.asarray(control, dtype=float)]
    while levels[-1].shape[0] > 1:
        prior = levels[-1]
        levels.append((1.0 - t) * prior[:-1] + t * prior[1:])
    return (
        np.asarray([level[0] for level in levels]),
        np.asarray([level[-1] for level in levels[::-1]]),
    )


def _restrict(control: np.ndarray, start: float, end: float) -> np.ndarray:
    left, _ = _split(control, end)
    if start == 0.0:
        return left
    return _split(left, start / end)[1]


def _subspan_geometry(
    seam: int,
    subspan: int,
    states: np.ndarray,
    action_rates: np.ndarray,
    action_lengths: np.ndarray,
    weights: np.ndarray,
    reference: np.ndarray,
) -> dict[str, Any]:
    if not 0 <= subspan < SUBDIVISIONS:
        raise ValueError("subspan must lie in the existing 64-part mesh")
    h = float(action_lengths[seam + 1] - action_lengths[seam])
    macro_x0 = states[seam] * weights
    macro_x1 = states[seam + 1] * weights
    macro_controls = np.asarray((
        macro_x0,
        macro_x0 + h * action_rates[seam] / 3.0,
        macro_x1 - h * action_rates[seam + 1] / 3.0,
        macro_x1,
    ))
    controls = _restrict(
        macro_controls,
        subspan / SUBDIVISIONS,
        (subspan + 1) / SUBDIVISIONS,
    )
    local_h = h / SUBDIVISIONS
    x0 = controls[0]
    x1 = controls[-1]
    rate0 = 3.0 * (controls[1] - controls[0]) / local_h
    rate1 = 3.0 * (controls[3] - controls[2]) / local_h
    delta = x1 - x0
    projection = np.column_stack((
        0.5 * delta,
        local_h * rate0 - delta,
        delta - local_h * rate1,
    ))
    midpoint_action = 0.5 * (x0 + x1)
    midpoint = midpoint_action / weights
    jet = exact_full_action_jet_at_state(
        12,
        midpoint[:QDIM], midpoint[QDIM:2 * QDIM], midpoint[2 * QDIM:],
        points=POINTS,
    )
    hessian = np.asarray(jet.hessian, dtype=float)[QDIM:, QDIM:]
    values, vectors = np.linalg.eigh(hessian)
    selected = int(np.argmax(np.abs(vectors.T @ reference)))
    directionals = []
    for column in range(projection.shape[1]):
        shifted = np.asarray(midpoint, dtype=complex) + (
            1j * COMPLEX_STEP * projection[:, column] / weights
        )
        shifted_jet = exact_full_action_jet_at_state(
            12,
            shifted[:QDIM], shifted[QDIM:2 * QDIM], shifted[2 * QDIM:],
            points=POINTS,
        )
        directionals.append(
            np.imag(np.asarray(shifted_jet.hessian)[QDIM:, QDIM:])
            / COMPLEX_STEP
        )
    return {
        "local_h": local_h,
        "midpoint": midpoint,
        "projection": projection,
        "values": values,
        "vectors": vectors,
        "selected": selected,
        "directionals": directionals,
    }


def _seam_payload(
    seam: int,
    states: np.ndarray,
    action_rates: np.ndarray,
    action_lengths: np.ndarray,
    weights: np.ndarray,
    reference: np.ndarray,
    *,
    subspan: int | None = None,
    parallel_branches: bool = True,
) -> dict[str, Any]:
    if subspan is None:
        subspan = SUBDIVISIONS // 2
    geometry = _subspan_geometry(
        seam, subspan, states, action_rates, action_lengths, weights, reference,
    )
    local_h = geometry["local_h"]
    midpoint = geometry["midpoint"]
    projection = geometry["projection"]
    values = geometry["values"]
    vectors = geometry["vectors"]
    selected = geometry["selected"]
    directionals = geometry["directionals"]
    branch_arguments = [
        (
            branch, midpoint, projection, values, vectors,
            directionals, weights,
        )
        for branch in range(values.size)
    ]
    if parallel_branches:
        workers = min(4, os.cpu_count() or 1)
        with ProcessPoolExecutor(max_workers=workers) as executor:
            rows = list(executor.map(_branch_bound, branch_arguments))
    else:
        rows = [_branch_bound(arguments) for arguments in branch_arguments]
    selected_shift = rows[selected]["total_branch_shift_upper"]
    pair_margins = []
    for branch, row in enumerate(rows):
        if branch == selected:
            continue
        center_gap = abs(float(values[selected] - values[branch]))
        pair_margins.append(
            center_gap - selected_shift - row["total_branch_shift_upper"]
        )
    return {
        "seam": seam,
        "subdivisions": SUBDIVISIONS,
        "tested_subspan": subspan,
        "action_interval": [
            float(action_lengths[seam] + subspan * local_h),
            float(action_lengths[seam] + (subspan + 1) * local_h),
        ],
        "selected_branch": selected,
        "projection_column_norms": [
            float(np.linalg.norm(projection[:, column]))
            for column in range(projection.shape[1])
        ],
        "selected_center_gap": float(np.min(np.abs(
            np.delete(values, selected) - values[selected]
        ))),
        "selected_branch_shift_upper": selected_shift,
        "minimum_selected_to_hard_gap_lower": float(min(pair_margins)),
        "selected_denominator_bootstrap_closed": min(pair_margins) > 0.0,
        "branch_rows": rows,
    }


def build_payload() -> dict[str, Any]:
    center = json.loads(CENTER.read_text(encoding="utf-8"))
    kato = json.loads(KATO.read_text(encoding="utf-8"))
    if center["claim_boundary"]["exact_node_and_midpoint_fields_evaluated"] is not True:
        raise RuntimeError("finite stop center required")
    if kato["claim_boundary"]["exact_center_D3_Kato_rates"] != "ASSEMBLED":
        raise RuntimeError("exact center Kato profile required")
    with np.load(CENTER_DATA) as source:
        states = np.asarray(source["centers"], dtype=float)
        action_rates = np.asarray(source["action_rates"], dtype=float)
        action_lengths = np.asarray(source["action_lengths"], dtype=float)
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)
    seams = []
    for seam in SEAMS:
        print(f"evaluating seam {seam} termwise Kato bounds", flush=True)
        result = _seam_payload(
            seam, states, action_rates, action_lengths, weights, reference
        )
        seams.append(result)
        print(json.dumps({
            "seam": seam,
            "selected_branch": result["selected_branch"],
            "selected_center_gap": result["selected_center_gap"],
            "selected_branch_shift_upper": result["selected_branch_shift_upper"],
            "minimum_selected_to_hard_gap_lower": result[
                "minimum_selected_to_hard_gap_lower"
            ],
            "selected_denominator_bootstrap_closed": result[
                "selected_denominator_bootstrap_closed"
            ],
        }), flush=True)
    every = all(row["selected_denominator_bootstrap_closed"] for row in seams)
    return {
        "artifact": "BHSM_N12_C2_STOP_LOCAL_TERMWISE_SPECTRUM",
        "status": (
            "CENTRAL_1_OF_64_SUBSPAN_TERMWISE_KATO_DENOMINATORS_"
            "CLOSE_ON_ALL_47_MACRO_SEAMS"
            if every else
            "CENTRAL_SUBSPAN_TERMWISE_KATO_DENOMINATOR_REFINEMENT_REQUIRED"
        ),
        "method": (
            "EXACT_THREE_COORDINATE_HERMITE_ELLIPSOID_WITH_RAW_EVENT_D3_"
            "SLOPES_AND_RETAINED_D4_DIAGONAL_COUPLING_KATO_CURVATURE"
        ),
        "tested_seams": list(SEAMS),
        "subdivisions_per_macro_seam": SUBDIVISIONS,
        "seams": seams,
        "summary": {
            "every_central_subspan_on_all_47_macro_seams_closed": every,
            "minimum_selected_to_hard_gap_lower": min(
                row["minimum_selected_to_hard_gap_lower"] for row in seams
            ),
            "maximum_selected_branch_shift_upper": max(
                row["selected_branch_shift_upper"] for row in seams
            ),
        },
        "provenance": {
            "majorant_source": "CLEAN_COMMITTED_HEAD_BLOB_EXECUTED_IN_ISOLATED_MODULE",
            "committed_majorant_SHA256": COMMITTED_MAJORANT_SHA256,
            "protected_worktree_extensions_used": False,
        },
        "claim_boundary": {
            "central_1_of_64_subspan_on_all_47_macro_seams": (
                "CERTIFIED" if every else "OPEN"
            ),
            "all_3008_stop_path_subspans": "OPEN",
            "all_47_complete_macro_seams": "OPEN",
            "branchwise_selected_projector_graph": "OPEN",
            "Green_Hermite_shadowing": "OPEN",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "EXTEND_THE_SAME_LOCAL_TERMWISE_KATO_KERNEL_TO_ALL_64_SUBSPANS_"
            "OF_EACH_MACRO_SEAM_THEN_INSERT_THE_CERTIFIED_DENOMINATORS_IN_"
            "THE_BRANCHWISE_SELECTED_PROJECTOR_AND_BORDERED_HARD_RESPONSE_GRAPHS"
            if every else
            "REFINE_ONLY_THE_NONCLOSING_SEAM_OR_PROMOTE_ITS_NEAREST_TWO_LINE_CLUSTER"
        ),
        "inputs": {
            CENTER.relative_to(ROOT).as_posix(): _sha256(CENTER),
            CENTER_DATA.relative_to(ROOT).as_posix(): _sha256(CENTER_DATA),
            KATO.relative_to(ROOT).as_posix(): _sha256(KATO),
        },
        "validation_passed": every,
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
        "exact_next_dependency": payload["exact_next_dependency"],
        "validation_passed": payload["validation_passed"],
    }, indent=2))


if __name__ == "__main__":
    main()
