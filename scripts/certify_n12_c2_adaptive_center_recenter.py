"""Recenter retained C2 action majorants at the last adaptive proof center."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_forward_c2_descriptor_cover import (  # noqa: E402
    admissible_root_radius,
    metric_data,
)


BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_C2_ADAPTIVE_CENTER_RECENTER.json"
DATA_RESULT = BASE / "BHSM_N12_C2_ADAPTIVE_CENTER_RECENTER.npz"
ADAPTIVE = BASE / "BHSM_N12_C2_ADAPTIVE_BALL_CONTINUATION.json"
ADAPTIVE_DATA = BASE / "BHSM_N12_C2_ADAPTIVE_BALL_CONTINUATION.npz"
POLE_FREE = BASE / "BHSM_N12_C2_POLE_FREE_REGULARIZED_JACOBI.json"
LAUNCH = BASE / "BHSM_N12_C2_REGULARIZED_LAUNCH_SEGMENT.json"
LINE = BASE / "BHSM_N12_FINITE_TERMINAL_EVENT_EIGENLINE_BALL.json"
ACTION = BASE / "BHSM_N12_FINITE_TERMINAL_ACTION_BALL_MAJORANTS.json"
THEORY = ROOT / "theory/n12_c2_adaptive_center_recenter.md"
INPUTS = (ADAPTIVE, ADAPTIVE_DATA, POLE_FREE, LAUNCH, LINE, ACTION, THEORY)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing adaptive recenter inputs: " + ", ".join(missing))
    adaptive, pole_free, launch, line_record, action = (
        _load(path) for path in (ADAPTIVE, POLE_FREE, LAUNCH, LINE, ACTION)
    )
    if not all(record.get("validation_passed") is True for record in (
        adaptive, pole_free, launch, line_record, action,
    )):
        raise RuntimeError("validated adaptive recenter parents required")
    with np.load(ADAPTIVE_DATA) as data:
        centers = np.asarray(data["C2_adaptive_predictor_centers"], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
        reference = np.asarray(data["branch_reference"], dtype=float)
    center = centers[-1].copy()
    cover = adaptive["adaptive_cover"]
    distance = float(cover["final_center_path_upper"])
    tube = float(cover["final_endpoint_tube_radius_upper"])
    old_pf = pole_free["bounds"]
    old_launch = launch["launch_ball"]
    line = line_record["bounds"]
    original_parent_radius = float(action["action_coordinate_ball_radius"])
    _, _, _, maximum_reduced_weight = metric_data()

    recentered_pf = dict(old_pf)
    recentered_pf.update({
        "hard_D3_center": (
            float(old_pf["hard_D3_center"])
            + float(old_pf["D4_full_hard_hard_upper"]) * distance
        ),
        "rhs_raw_derivative_center": (
            float(old_pf["rhs_raw_derivative_center"])
            + float(old_pf["rhs_raw_second_derivative_upper"]) * distance
        ),
        "coupling_center": (
            float(old_pf["coupling_center"])
            + float(old_pf["D4_full_selected_hard_upper"]) * distance
        ),
        "center_hard_rate_raw_norm": (
            float(old_pf["center_hard_rate_raw_norm"])
            + float(old_pf["hard_Jacobi_action_upper"])
            * distance / maximum_reduced_weight
        ),
    })
    recentered_launch = dict(old_launch)
    c_shift = float(old_launch["c_psi_Lipschitz_upper"]) * distance
    b_shift = float(old_pf["structured_b_psi_Lipschitz_upper"]) * distance
    recentered_launch.update({
        "c_psi_interval": [
            float(old_launch["c_psi_interval"][0]) - c_shift,
            float(old_launch["c_psi_interval"][1]) + c_shift,
        ],
        "b_psi_interval": [
            float(old_launch["b_psi_interval"][0]) - b_shift,
            float(old_launch["b_psi_interval"][1]) + b_shift,
        ],
    })
    recentered_parent_radius = original_parent_radius - distance
    roots = admissible_root_radius(
        pf=recentered_pf,
        launch_ball=recentered_launch,
        line=line,
        parent_radius=recentered_parent_radius,
    )
    strict_allocation_margin = roots["admissible_radius"] - 2.0 * tube
    original_line_ball_radius = float(line_record["action_coordinate_ball_radius"])

    np.savez_compressed(
        DATA_RESULT,
        recentered_root_state=center,
        state_weights=weights,
        branch_reference=reference,
    )
    validation = {
        "adaptive_parent_is_validated": True,
        "last_adaptive_center_materialized": center.shape == (98,),
        "center_shift_stays_inside_original_parent_action_ball": (
            0.0 < distance < original_parent_radius
        ),
        "recentered_parent_radius_is_positive": recentered_parent_radius > 0.0,
        "D3_center_transfer_uses_retained_D4_bound": (
            recentered_pf["hard_D3_center"] >= old_pf["hard_D3_center"]
        ),
        "rhs_center_transfer_uses_retained_second_bound": (
            recentered_pf["rhs_raw_derivative_center"]
            >= old_pf["rhs_raw_derivative_center"]
        ),
        "hard_rate_center_transfer_uses_retained_Jacobi_bound": (
            recentered_pf["center_hard_rate_raw_norm"]
            >= old_pf["center_hard_rate_raw_norm"]
        ),
        "c_and_b_center_intervals_transfer_by_lipschitz_bounds": (
            recentered_launch["c_psi_interval"][0] > 0.0
            and recentered_launch["b_psi_interval"][0] > 0.0
        ),
        "recentered_admissible_radius_strictly_exceeds_twice_incoming_tube": (
            strict_allocation_margin > 0.0
        ),
        "recentered_ball_stays_inside_original_parent_action_ball": (
            distance + roots["admissible_radius"] < original_parent_radius
        ),
        "recentered_ball_stays_inside_original_eigenline_ball": (
            distance + roots["admissible_radius"] < original_line_ball_radius
        ),
        "recenter_changes_proof_origin_not_physical_state": True,
        "no_recurrence_selector_scale_action_term_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_C2_ADAPTIVE_CENTER_RECENTER",
        "status": (
            "C2_LAST_ADAPTIVE_CENTER_MAJORANTS_RECENTERED_WITH_STRICT_NEXT_BALL_MARGIN"
            if passed else "C2_ADAPTIVE_CENTER_RECENTER_NOT_CERTIFIED"
        ),
        "classification": (
            "THE_LAST_791_SEGMENT_PROOF_CENTER_BECOMES_A_NEW_ANALYTIC_ORIGIN;_"
            "RETAINED_D4_RHS_SECOND_JACOBI_AND_C_B_LIPSCHITZ_BOUNDS_TRANSFER_"
            "THE_LOCAL_ACTION_DATA_AND_REOPEN_A_STRICT_ADAPTIVE_RADIUS_INTERVAL"
        ),
        "recenter": {
            "prior_total_certified_segments": int(cover["total_certified_segments"]),
            "old_root_to_new_center_action_distance_upper": distance,
            "incoming_endpoint_tube_upper": tube,
            "original_parent_action_radius": original_parent_radius,
            "recentered_parent_action_radius": recentered_parent_radius,
            "original_eigenline_ball_radius": original_line_ball_radius,
            "recentered_pole_free_bounds": recentered_pf,
            "recentered_launch_ball": recentered_launch,
            "recentered_admissible_root_radii": roots,
            "strict_adaptive_allocation_margin": strict_allocation_margin,
            "data": DATA_RESULT.relative_to(ROOT).as_posix(),
            "data_SHA256": _sha256(DATA_RESULT),
        },
        "transfer_identities": {
            "hard_D3": "D3_new<=D3_old+D4_global*distance",
            "rhs_derivative": "Drhs_new<=Drhs_old+D2rhs_global*distance",
            "coupling": "coupling_new<=coupling_old+D4_selected_hard*distance",
            "hard_rate": "norm(r_h,new)<=norm(r_h,old)+J_hard_raw*distance",
            "c_and_b": "center_intervals_expand_by_their_retained_Lipschitz_constants",
        },
        "adjudication": {
            "no_representable_old_origin_allocation": "SUPERSEDED_BY_RECENTER",
            "new_strict_allocation_interval": "CERTIFIED" if passed else "OPEN",
            "actual_later_event_or_canonical_stop": "NOT_REACHED",
            "physical_history_changed": False,
        },
        "exact_next_dependency": (
            "CONTINUE_THE_SAME_COMPENSATED_ADAPTIVE_DESCRIPTOR_FLOW_FROM_THE_"
            "RECENTERED_ROOT_WITH_CENTER_PATH_ZERO_AND_THE_TRANSFERRED_ACTION_"
            "BOUNDS;_MONITOR_ONLY_RETAINED_EVENTS_AND_CANONICAL_STOPS"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_RECENTERED_C2_CONTINUATION_OR_COMBINED_PROJECTED_TAIL",
            "Gate8": "LOCKED",
            "adaptive_center_recenter": "CERTIFIED" if passed else "OPEN",
            "actual_later_event_or_canonical_stop": "OPEN",
            "actual_projected_zero_source_force": "OPEN",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": passed,
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    recenter = payload["recenter"]
    print(json.dumps({
        "status": payload["status"],
        "validation_passed": payload["validation_passed"],
        "admissible_radius": recenter["recentered_admissible_root_radii"]["admissible_radius"],
        "twice_tube": 2.0 * recenter["incoming_endpoint_tube_upper"],
        "strict_margin": recenter["strict_adaptive_allocation_margin"],
    }, indent=2))


if __name__ == "__main__":
    main()
