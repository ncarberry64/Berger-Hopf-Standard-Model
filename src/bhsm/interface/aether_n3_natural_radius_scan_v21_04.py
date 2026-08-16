"""Scan the unresolved interval between BHSM plateau and medium trust radii."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_curvature_transport_proposal_v21_00 import v21_00_selected_raw_vector
from bhsm.interface.aether_n3_dual_metric_range_space_proposal_v20_91 import (
    _physical_history_radii, dual_metric_range_space_proposal,
)
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales


VERSION = "v21.04"
CLASSIFICATION = "BHSM_N3_ACTION_OWNED_NATURAL_TRUST_RADIUS_INTERVAL_SCAN"
FULL_BHSM_COMPLETE = False
POINTS = 17


def v21_04_selected_raw_vector() -> np.ndarray:
    payload = json.loads(Path(
        "artifacts/BHSM_N3_NATURAL_RADIUS_SCAN_V21_04.json"
    ).read_text(encoding="utf-8"))["natural_radius_scan"]
    if not payload["promotion"]["promoted"]:
        raise ValueError("v21.04 has no physically promoted state")
    return np.asarray([
        float.fromhex(value) for value in payload["exact_search"]["best"]["raw_vector_hex"]
    ])


def completion_payload() -> dict[str, Any]:
    audit = json.loads(Path(
        "artifacts/BHSM_N3_CURVATURE_SINGULAR_SUBSPACE_REFRESH_V21_01.json"
    ).read_text(encoding="utf-8"))["curvature_singular_subspace_refresh"]
    action = audit["bhsm_owned_action_coordinate_radii"]
    physical = _physical_history_radii(kkt_variable_scales())
    action_endpoints = np.asarray([
        float(action["PLATEAU_DESCENT"]), float(action["MEDIUM_DESCENT"])
    ])
    physical_endpoints = np.asarray([
        float(physical["PLATEAU_DESCENT"]), float(physical["MEDIUM_DESCENT"])
    ])
    schedule = []
    for index, fraction in enumerate(np.linspace(0.0, 1.0, POINTS)):
        schedule.append({
            "label": f"PLATEAU_TO_MEDIUM_{index:02d}",
            "physical_radius": float(np.exp(
                (1.0 - fraction) * np.log(physical_endpoints[0])
                + fraction * np.log(physical_endpoints[1])
            )),
            "action_radius": float(np.exp(
                (1.0 - fraction) * np.log(action_endpoints[0])
                + fraction * np.log(action_endpoints[1])
            )),
        })
    result = dual_metric_range_space_proposal(
        v21_00_selected_raw_vector(),
        source_label="v21.00",
        curvature_artifact="artifacts/BHSM_N3_CURVATURE_SINGULAR_SUBSPACE_REFRESH_V21_01.json",
        curvature_key="curvature_singular_subspace_refresh",
        radius_schedule_override=schedule,
    )
    best = result["exact_search"]["best"]
    validation = {
        "source_v21_00_reproduced": abs(
            result["source"]["exact_rayleigh_f376_l2"] - 0.782778933037026
        ) < 5.0e-12,
        "only_owned_endpoint_interpolation": result["dual_metric_model"][
            "radius_schedule_interpolated_only_if_explicitly_overridden"
        ] and len(schedule) == POINTS,
        "both_signs_all_points": result["exact_search"]["trial_count"] == 2 * POINTS,
        "exact_rows_decide": result["exact_search"]["original_unweighted_376_rows_authoritative"],
        "candidate_reduces_merit": best is None or best["exact_reduction"] > 0.0,
        "promotion_requires_child": not result["promotion"]["promoted"] or result["promotion"]["child"]["all_pass"],
        "same_physics": not result["physical_equations_changed"]
        and not result["event_definition_changed"]
        and not result["acceptance_gate_changed"],
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N3_NATURAL_RADIUS_SCAN_V21_04",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "natural_radius_scan": result,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_N3_NATURAL_RADIUS_SCAN_V21_04.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "v21_04_selected_raw_vector",
    "completion_payload", "materialize",
]
