"""Soft-branch and contraction audit after the v17.70 physical promotion."""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_exact_radial_schur_lift_v15_83 import exact_action_jet_at_state
from bhsm.interface.aether_n3_exact_local_jet_sbp_covector_v17_61 import (
    exact_local_jet_sbp_projected_residual_and_vector,
)
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_fresh_sbp_six_owner_measured_cone_v17_05 import _metrics
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales, unpack_reduced
from bhsm.interface.aether_n3_sbp_redirect_audit_v16_57 import trapezoid_sbp_difference

VERSION = "v17.71"
CLASSIFICATION = "BHSM_N3_POST_PERIOD_LOG_BRACKET_SOFT_CONTRACTION_AUDIT"
FULL_BHSM_COMPLETE = False
TOLERANCE = 1e-6


def v17_70_selected_raw_vector() -> np.ndarray:
    payload = json.loads(Path(
        "artifacts/BHSM_aether_n3_period_log_direction_bracket_v17_70.json"
    ).read_text(encoding="utf-8"))["period_log_direction_bracket"]
    values = payload["selected_period_log_bracket"]["raw_vector_hex"]
    raw = np.asarray([float.fromhex(value) for value in values])
    if raw.shape != (376,):
        raise ValueError("v17.70 selected vector has wrong dimension")
    return raw


def post_period_log_bracket_audit() -> dict[str, Any]:
    payload = json.loads(Path(
        "artifacts/BHSM_aether_n3_period_log_direction_bracket_v17_70.json"
    ).read_text(encoding="utf-8"))["period_log_direction_bracket"]
    selected = payload["selected_period_log_bracket"]
    raw = v17_70_selected_raw_vector()
    _, residual = exact_local_jet_sbp_projected_residual_and_vector(raw * kkt_variable_scales())
    metrics = _metrics(residual)
    unpacked = unpack_reduced(raw)
    coordinates = np.asarray(unpacked["coordinates"])
    multipliers = np.asarray(unpacked["multipliers"])
    velocity = trapezoid_sbp_difference() @ coordinates / float(unpacked["period"])
    hessian = exact_action_jet_at_state(
        3, coordinates[-1], velocity[-1], multipliers[-1], points=44
    ).hessian
    eigenvalues, eigenvectors = np.linalg.eigh(hessian)
    soft = eigenvectors[:, 6]
    contraction: dict[str, dict[str, float | int]] = {}
    for owner, fraction in selected["fractional_reductions"].items():
        ratio = 1.0 - float(fraction)
        passes = (
            math.ceil(math.log(TOLERANCE / metrics[owner]) / math.log(ratio))
            if 0.0 < ratio < 1.0 and metrics[owner] > TOLERANCE else 0
        )
        contraction[owner] = {
            "ratio_per_pass": ratio,
            "constant_rate_projected_additional_passes": passes,
        }
    bottleneck = max(
        contraction,
        key=lambda owner: contraction[owner]["constant_rate_projected_additional_passes"],
    )
    return {
        "source_state": "v17.70_selected_period_log_bracket_state",
        "metrics": metrics,
        "terminal_soft_mode": {
            "eigenvalue": float(eigenvalues[6]),
            "scaled_event_value": float(eigenvalues[6] / 1e-3),
            "gap_below": float(eigenvalues[6] - eigenvalues[5]),
            "gap_above": float(eigenvalues[7] - eigenvalues[6]),
            "eigenvector_norm": float(np.linalg.norm(soft)),
            "eigenpair_residual_norm": float(np.linalg.norm(hessian @ soft - eigenvalues[6] * soft)),
        },
        "eta_minimum_provenance": selected["eta_minimum"],
        "contraction_by_owner": contraction,
        "extrapolation_bottleneck": bottleneck,
        "projected_additional_passes": contraction[bottleneck]["constant_rate_projected_additional_passes"],
        "classification_scope": "EMPIRICAL_ADEQUACY_NOT_MATHEMATICAL_NO_GO",
    }


def completion_payload() -> dict[str, Any]:
    result = post_period_log_bracket_audit()
    metrics = result["metrics"]
    soft = result["terminal_soft_mode"]
    validation = {
        "v17_70_residual_reproduced": math.isclose(
            metrics["complete"], 0.832005956495502, rel_tol=0, abs_tol=2e-8
        ),
        "v17_70_event_reproduced": math.isclose(
            metrics["event"], 0.083861003953294, rel_tol=0, abs_tol=2e-8
        ),
        "event_matches_soft_spectrum": math.isclose(
            metrics["event"], abs(soft["scaled_event_value"]), rel_tol=0, abs_tol=2e-8
        ),
        "soft_vector_normalized": math.isclose(
            soft["eigenvector_norm"], 1.0, rel_tol=0, abs_tol=2e-12
        ),
        "soft_eigenpair_resolved": soft["eigenpair_residual_norm"] < 1e-9,
        "soft_branch_isolated": min(soft["gap_below"], soft["gap_above"]) > 1e-4,
        "eta_domain_preserved": result["eta_minimum_provenance"] > 1e-5,
        "constant_rate_still_inadequate": result["projected_additional_passes"] > 1000,
        "no_no_go_claimed": result["classification_scope"] == "EMPIRICAL_ADEQUACY_NOT_MATHEMATICAL_NO_GO",
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_aether_n3_post_period_log_bracket_audit_v17_71",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": False,
        "post_period_log_bracket_audit": result,
        "status": "RECLASSIFIED" if passed else "INVALIDATED",
        "real_physical_property_explained": "ISOLATED_SOFT_BRANCH_AFTER_THE_PERIOD_LOG_COMMON_DESCENT_PROMOTION",
        "dependency_advanced": "CONTINUE_FROM_THE_VALIDATED_V17_70_PHYSICAL_STATE",
        "active_calculation": "RECOMPUTE_THE_MEASURED_OWNER_DIRECTION_AT_V17_70",
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_post_period_log_bracket_audit_v17_71.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "TOLERANCE",
    "v17_70_selected_raw_vector", "post_period_log_bracket_audit", "completion_payload", "materialize",
]
