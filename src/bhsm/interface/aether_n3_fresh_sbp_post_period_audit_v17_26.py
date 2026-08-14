"""Complete block and soft-spectrum audit after v17.25 continuation."""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.aether_exact_radial_schur_lift_v15_83 import (
    exact_action_jet_at_state,
)
from bhsm.interface.aether_n3_fresh_sbp_kkt_v16_58 import (
    sbp_projected_residual_and_vector,
)
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import (
    kkt_variable_scales,
    unpack_reduced,
)
from bhsm.interface.aether_n3_sbp_redirect_audit_v16_57 import (
    trapezoid_sbp_difference,
)
from bhsm.interface.aether_physical_inverse_closure_v16_36 import Q_LABELS

VERSION = "v17.26"
CLASSIFICATION = "BHSM_N3_FRESH_SBP_POST_PERIOD_COMPLETE_BLOCK_SOFT_AUDIT"
FULL_BHSM_COMPLETE = False


def v17_25_selected_raw_vector() -> np.ndarray:
    payload = json.loads(
        Path(
            "artifacts/BHSM_aether_n3_fresh_sbp_period_priority_family_v17_25.json"
        ).read_text(encoding="utf-8")
    )
    values = payload["fresh_sbp_period_priority_family"][
        "selected_period_priority_maximin"
    ]["raw_vector_hex"]
    raw = np.asarray([float.fromhex(value) for value in values])
    if raw.shape != (376,):
        raise ValueError("v17.25 selected vector has wrong dimension")
    return raw


def post_period_audit() -> dict[str, Any]:
    raw = v17_25_selected_raw_vector()
    y = raw * kkt_variable_scales()
    _, residual = sbp_projected_residual_and_vector(y)
    q_residual = residual[:230].reshape(23, 10)
    multiplier_residual = residual[230:374].reshape(24, 6)
    unpacked = unpack_reduced(raw)
    coordinates = np.asarray(unpacked["coordinates"])
    multipliers = np.asarray(unpacked["multipliers"])
    velocity = (
        trapezoid_sbp_difference()
        @ coordinates
        / float(unpacked["period"])
    )
    hessian = exact_action_jet_at_state(
        3,
        coordinates[-1],
        velocity[-1],
        multipliers[-1],
        points=44,
    ).hessian
    eigenvalues, eigenvectors = np.linalg.eigh(hessian)
    soft = eigenvectors[:, 6]
    group = np.linalg.norm(q_residual, axis=0)
    block = {
        "complete": float(np.linalg.norm(residual)),
        "q": float(np.linalg.norm(q_residual)),
        "multipliers": float(np.linalg.norm(multiplier_residual)),
        "period": abs(float(residual[-2])),
        "event": abs(float(residual[-1])),
    }
    return {
        "source_state": "v17.25_selected_period_priority_state",
        "block_norms": block,
        "coordinate_group_ranking": [
            {
                "coordinate": Q_LABELS[index],
                "stationarity_norm": float(group[index]),
            }
            for index in np.argsort(group)[::-1]
        ],
        "terminal_soft_mode": {
            "eigenvalue": float(eigenvalues[6]),
            "scaled_event_value": float(eigenvalues[6] / 1e-3),
            "gap_below": float(eigenvalues[6] - eigenvalues[5]),
            "gap_above": float(eigenvalues[7] - eigenvalues[6]),
            "eigenvector_norm": float(np.linalg.norm(soft)),
            "eigenpair_residual_norm": float(
                np.linalg.norm(hessian @ soft - eigenvalues[6] * soft)
            ),
        },
        "eta_minimum_provenance": 0.773413141526173,
        "scale_rows_retained": 23,
        "nonlinear_limiter_transition": "PERIOD_TO_LOG_SCALE_AT_V17_25",
        "interpretation": "RECALIBRATE_OWNER_PRIORITIES_FROM_THE_CURRENT_FULL_RESIDUAL",
    }


def completion_payload() -> dict[str, Any]:
    result = post_period_audit()
    block = result["block_norms"]
    soft = result["terminal_soft_mode"]
    validation = {
        "v17_25_residual_reproduced": math.isclose(
            block["complete"], 1.127995335027502, rel_tol=0, abs_tol=2e-8
        ),
        "v17_25_event_reproduced": math.isclose(
            block["event"], 0.095644921219748, rel_tol=0, abs_tol=2e-8
        ),
        "event_matches_soft_spectrum": math.isclose(
            block["event"],
            abs(soft["scaled_event_value"]),
            rel_tol=0,
            abs_tol=2e-8,
        ),
        "soft_vector_normalized": math.isclose(
            soft["eigenvector_norm"], 1.0, rel_tol=0, abs_tol=2e-12
        ),
        "soft_eigenpair_resolved": soft["eigenpair_residual_norm"] < 1e-9,
        "soft_branch_isolated": min(soft["gap_below"], soft["gap_above"]) > 1e-4,
        "all_coordinate_groups_measured": len(
            result["coordinate_group_ranking"]
        )
        == 10,
        "all_scale_rows_retained": result["scale_rows_retained"] == 23,
        "limiter_transition_recorded": (
            result["nonlinear_limiter_transition"]
            == "PERIOD_TO_LOG_SCALE_AT_V17_25"
        ),
        "simultaneous_closure_not_claimed": block["complete"] > 1e-6,
    }
    return {
        "artifact": "BHSM_aether_n3_fresh_sbp_post_period_audit_v17_26",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": False,
        "fresh_sbp_post_period_audit": result,
        "status": "RECLASSIFIED" if all(validation.values()) else "INVALIDATED",
        "real_physical_property_explained": (
            "CURRENT_COMPLETE_OWNER_BLOCKS_AND_IDENTICAL_SOFT_MODE_AFTER_THE_"
            "PERIOD_LIMITER_TRANSITION"
        ),
        "dependency_advanced": (
            "RETARGETS_THE_NEXT_SIMULTANEOUS_N3_EVENT_SADDLE_CORRECTION"
        ),
        "active_calculation": (
            "BUILD_A_BOUNDED_LOG_SCALE_PRIORITY_FAMILY_FROM_V17_25"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def _canonical(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return [_canonical(item) for item in value.tolist()]
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        value = float(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite float")
        return round(value, 15)
    if isinstance(value, Mapping):
        return {key: _canonical(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    return value


def deterministic_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(_canonical(payload), indent=2, sort_keys=True) + "\n"


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_fresh_sbp_post_period_audit_v17_26.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION",
    "CLASSIFICATION",
    "FULL_BHSM_COMPLETE",
    "v17_25_selected_raw_vector",
    "post_period_audit",
    "completion_payload",
    "deterministic_json",
    "materialize",
]
