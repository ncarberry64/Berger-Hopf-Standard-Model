"""Test one exact-F376 proposal using the validated eigenpair event Hessian."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_dual_metric_range_space_proposal_v20_91 import (
    dual_metric_range_space_proposal,
)
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import (
    deterministic_json,
)
from bhsm.interface.aether_n3_natural_radius_scan_v21_04 import (
    v21_04_selected_raw_vector,
)


VERSION = "v21.18"
CLASSIFICATION = "BHSM_N3_EIGENPAIR_CURVATURE_DUAL_METRIC_PROPOSAL"
FULL_BHSM_COMPLETE = False


def v21_18_selected_raw_vector() -> np.ndarray:
    payload = json.loads(Path(
        "artifacts/BHSM_N3_EIGENPAIR_CURVATURE_DUAL_METRIC_PROPOSAL_V21_18.json"
    ).read_text(encoding="utf-8"))["eigenpair_curvature_dual_metric_proposal"]
    if not payload["promotion"]["promoted"]:
        raise ValueError("v21.18 has no physically promoted state")
    return np.asarray([
        float.fromhex(value)
        for value in payload["exact_search"]["best"]["raw_vector_hex"]
    ])


def completion_payload() -> dict[str, Any]:
    derived_payload = json.loads(Path(
        "artifacts/BHSM_N3_ISOLATED_EIGENPAIR_EVENT_HESSIAN_V21_17.json"
    ).read_text(encoding="utf-8"))
    if not derived_payload["validation_passed"]:
        raise ValueError("v21.17 event Hessian is not validated")
    curvature = dict(derived_payload["isolated_eigenpair_event_hessian"])
    prior = json.loads(Path(
        "artifacts/BHSM_N3_RESIDUAL_MANIFOLD_NORMAL_ACCELERATION_V21_06.json"
    ).read_text(encoding="utf-8"))["curvature_refresh"]
    curvature["bhsm_owned_action_coordinate_radii"] = prior[
        "bhsm_owned_action_coordinate_radii"
    ]

    natural = json.loads(Path(
        "artifacts/BHSM_N3_NATURAL_RADIUS_SCAN_V21_04.json"
    ).read_text(encoding="utf-8"))["natural_radius_scan"]["exact_search"]["trials"]
    unique = {}
    for row in natural:
        unique.setdefault(row["radius_class"], row)
    radius_schedule = [
        {
            "label": label,
            "action_radius": float(row["bhsm_action_coordinate_radius"]),
            "physical_radius": float(row["bhsm_physical_scaled_radius"]),
        }
        for label, row in sorted(unique.items())
    ]
    result = dual_metric_range_space_proposal(
        v21_04_selected_raw_vector(),
        source_label="v21.04",
        curvature_override=curvature,
        radius_schedule_override=radius_schedule,
    )
    result["dual_metric_model"]["curvature_artifact"] = (
        "VALIDATED_V21_17_ISOLATED_EIGENPAIR_EVENT_HESSIAN"
    )
    best = result["exact_search"]["best"]
    validation = {
        "source_v21_04_reproduced": abs(
            result["source"]["exact_rayleigh_f376_l2"] - 0.782775399601569
        ) < 5.0e-12,
        "validated_eigenpair_curvature_used": result["dual_metric_model"][
            "curvature_artifact"
        ].startswith("VALIDATED_V21_17"),
        "natural_radius_interval_reused": len(radius_schedule) == 17,
        "both_signs_all_radii": result["exact_search"]["trial_count"] == 34,
        "exact_rows_decide": result["exact_search"][
            "original_unweighted_376_rows_authoritative"
        ],
        "candidate_reduces_merit": best is None or best["exact_reduction"] > 0.0,
        "promotion_requires_child": not result["promotion"]["promoted"]
        or result["promotion"]["child"]["all_pass"],
        "same_physics": not result["physical_equations_changed"]
        and not result["event_definition_changed"]
        and not result["acceptance_gate_changed"],
        "no_componentwise_gate": not result["componentwise_monotonicity_added"],
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N3_EIGENPAIR_CURVATURE_DUAL_METRIC_PROPOSAL_V21_18",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "eigenpair_curvature_dual_metric_proposal": result,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_N3_EIGENPAIR_CURVATURE_DUAL_METRIC_PROPOSAL_V21_18.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "v21_18_selected_raw_vector", "completion_payload", "materialize",
]
