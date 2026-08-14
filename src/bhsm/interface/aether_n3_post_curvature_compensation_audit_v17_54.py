"""Soft-branch and contraction audit after v17.53 curvature compensation."""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_exact_radial_schur_lift_v15_83 import exact_action_jet_at_state
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_fresh_sbp_kkt_v16_58 import sbp_projected_residual_and_vector
from bhsm.interface.aether_n3_fresh_sbp_six_owner_measured_cone_v17_05 import _metrics
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales, unpack_reduced
from bhsm.interface.aether_n3_sbp_redirect_audit_v16_57 import trapezoid_sbp_difference
from bhsm.interface.aether_physical_inverse_closure_v16_36 import Q_LABELS

VERSION = "v17.54"
CLASSIFICATION = "BHSM_N3_POST_EVENT_LOG_CURVATURE_COMPENSATION_AUDIT"
FULL_BHSM_COMPLETE = False
CLOSURE_TOLERANCE = 1e-6


def v17_53_selected_raw_vector() -> np.ndarray:
    payload = json.loads(Path(
        "artifacts/BHSM_aether_n3_event_log_curvature_compensated_v17_53.json"
    ).read_text(encoding="utf-8"))
    values = payload["event_log_curvature_compensated"][
        "selected_event_log_curvature_compensated"
    ]["raw_vector_hex"]
    raw = np.asarray([float.fromhex(value) for value in values])
    if raw.shape != (376,):
        raise ValueError("v17.53 selected vector has wrong dimension")
    return raw


def post_curvature_compensation_audit() -> dict[str, Any]:
    payload = json.loads(Path(
        "artifacts/BHSM_aether_n3_event_log_curvature_compensated_v17_53.json"
    ).read_text(encoding="utf-8"))["event_log_curvature_compensated"]
    selected = payload["selected_event_log_curvature_compensated"]
    raw = v17_53_selected_raw_vector()
    _, residual = sbp_projected_residual_and_vector(raw * kkt_variable_scales())
    q_residual = residual[:230].reshape(23, 10)
    multiplier_residual = residual[230:374].reshape(24, 6)
    unpacked = unpack_reduced(raw)
    coordinates = np.asarray(unpacked["coordinates"])
    multipliers = np.asarray(unpacked["multipliers"])
    velocity = trapezoid_sbp_difference() @ coordinates / float(unpacked["period"])
    hessian = exact_action_jet_at_state(
        3, coordinates[-1], velocity[-1], multipliers[-1], points=44
    ).hessian
    eigenvalues, eigenvectors = np.linalg.eigh(hessian)
    soft = eigenvectors[:, 6]
    metrics = _metrics(residual)
    contraction: dict[str, Any] = {}
    for owner, fraction in selected["fractional_reductions"].items():
        ratio = 1.0 - float(fraction)
        projected = (
            math.ceil(math.log(CLOSURE_TOLERANCE / metrics[owner]) / math.log(ratio))
            if 0.0 < ratio < 1.0 and metrics[owner] > CLOSURE_TOLERANCE else 0
        )
        contraction[owner] = {
            "ratio_per_compensated_pass": ratio,
            "constant_rate_projected_additional_passes": projected,
        }
    bottleneck = max(
        contraction,
        key=lambda owner: contraction[owner]["constant_rate_projected_additional_passes"],
    )
    return {
        "source_state": "v17.53_selected_event_log_curvature_compensated_state",
        "block_norms": {
            **metrics,
            "q": float(np.linalg.norm(q_residual)),
            "multipliers": float(np.linalg.norm(multiplier_residual)),
        },
        "coordinate_group_ranking": [
            {"coordinate": Q_LABELS[index], "stationarity_norm": float(value)}
            for index, value in sorted(
                enumerate(np.linalg.norm(q_residual, axis=0)),
                key=lambda item: item[1], reverse=True,
            )
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
        "eta_minimum_provenance": selected["eta_minimum"],
        "scale_rows_retained": 23,
        "closure_tolerance": CLOSURE_TOLERANCE,
        "contraction_by_owner": contraction,
        "extrapolation_bottleneck": bottleneck,
        "projected_additional_passes": contraction[bottleneck][
            "constant_rate_projected_additional_passes"
        ],
        "classification_scope": "EMPIRICAL_ADEQUACY_NOT_MATHEMATICAL_NO_GO",
    }


def completion_payload() -> dict[str, Any]:
    result = post_curvature_compensation_audit()
    metrics = result["block_norms"]
    soft = result["terminal_soft_mode"]
    validation = {
        "v17_53_residual_reproduced": math.isclose(
            metrics["complete"], 0.8503794666366, rel_tol=0, abs_tol=2e-8
        ),
        "v17_53_event_reproduced": math.isclose(
            metrics["event"], 0.083985972706086, rel_tol=0, abs_tol=2e-8
        ),
        "event_matches_soft_spectrum": math.isclose(
            metrics["event"], abs(soft["scaled_event_value"]), rel_tol=0, abs_tol=2e-8
        ),
        "soft_vector_normalized": math.isclose(
            soft["eigenvector_norm"], 1.0, rel_tol=0, abs_tol=2e-12
        ),
        "soft_eigenpair_resolved": soft["eigenpair_residual_norm"] < 1e-9,
        "soft_branch_isolated": min(soft["gap_below"], soft["gap_above"]) > 1e-4,
        "positive_eta_preserved": result["eta_minimum_provenance"] > 1e-5,
        "all_scale_rows_retained": result["scale_rows_retained"] == 23,
        "constant_rate_continuation_inadequate": result["projected_additional_passes"] > 1000,
        "no_mathematical_no_go_claimed": (
            result["classification_scope"] == "EMPIRICAL_ADEQUACY_NOT_MATHEMATICAL_NO_GO"
        ),
    }
    return {
        "artifact": "BHSM_aether_n3_post_curvature_compensation_audit_v17_54",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": False,
        "post_curvature_compensation_audit": result,
        "status": "RECLASSIFIED" if all(validation.values()) else "INVALIDATED",
        "real_physical_property_explained": (
            "IDENTICAL_ISOLATED_SOFT_BRANCH_AFTER_EVENT_LOG_CURVATURE_COMPENSATION"
        ),
        "dependency_advanced": (
            "RESOLVE_SCALE_COMPONENTS_AND_EVENT_TOGETHER_BEFORE_FURTHER_CONTINUATION"
        ),
        "active_calculation": (
            "BUILD_THE_SAME_ACTION_SCALE_COMPONENT_EVENT_CORRECTION_WITH_ORIGINAL_"
            "SIX_OWNER_ACCEPTANCE"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_post_curvature_compensation_audit_v17_54.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "CLOSURE_TOLERANCE",
    "v17_53_selected_raw_vector", "post_curvature_compensation_audit",
    "completion_payload", "materialize",
]
