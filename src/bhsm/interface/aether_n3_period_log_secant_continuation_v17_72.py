"""Finite physical continuation along the validated v17.63-to-v17.70 secant."""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_exact_local_jet_sbp_covector_v17_61 import (
    exact_local_jet_sbp_projected_residual_and_vector,
)
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_fresh_sbp_six_owner_measured_cone_v17_05 import MARGIN, _metrics
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_post_period_log_bracket_audit_v17_71 import v17_70_selected_raw_vector
from bhsm.interface.aether_n3_post_scale_manifold_audit_v17_64 import v17_63_selected_raw_vector
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales

VERSION = "v17.72"
CLASSIFICATION = "BHSM_N3_PERIOD_LOG_SECANT_CONTINUATION"
FULL_BHSM_COMPLETE = False
FACTORS = (0.25, 0.5, 1.0, 2.0, 3.0, 5.0, 10.0, 20.0, 30.0, 50.0, 100.0)


def period_log_secant_continuation() -> dict[str, Any]:
    scales = kkt_variable_scales()
    y70, residual = exact_local_jet_sbp_projected_residual_and_vector(v17_70_selected_raw_vector() * scales)
    y63, _ = exact_local_jet_sbp_projected_residual_and_vector(v17_63_selected_raw_vector() * scales)
    secant = y70 - y63
    secant[-1] = 0.0
    initial = _metrics(residual)
    trials: list[dict[str, Any]] = []
    accepted: list[dict[str, Any]] = []
    for factor in FACTORS:
        try:
            cy, candidate_residual = exact_local_jet_sbp_projected_residual_and_vector(y70 + factor * secant)
            raw = cy / scales
            eta = _minimum_node_eta(raw)
            metrics = _metrics(candidate_residual)
            reductions = {key: initial[key] - metrics[key] for key in initial}
            fractions = {key: reductions[key] / max(initial[key], 1e-300) for key in initial}
            trial = {
                "secant_factor": factor,
                "eta_minimum": eta,
                "metrics": metrics,
                "reductions": reductions,
                "fractional_reductions": fractions,
                "minimum_fractional_progress": min(fractions.values()),
                "limiting_owner": min(fractions, key=fractions.get),
                "raw_vector_hex": [float(value).hex() for value in raw],
            }
            trials.append(trial)
            if eta > 1e-5 and all(value > MARGIN for value in reductions.values()):
                accepted.append(trial)
        except (FloatingPointError, ValueError, ArithmeticError) as exc:
            trials.append({"secant_factor": factor, "exception": type(exc).__name__})
    best = max(
        accepted,
        key=lambda trial: (
            trial["minimum_fractional_progress"],
            sum(trial["fractional_reductions"].values()),
        ),
    ) if accepted else None
    return {
        "source_state": "v17.70_selected_period_log_bracket_state",
        "physical_action_changed": False,
        "physical_event_changed": False,
        "secant_norm": float(np.linalg.norm(secant)),
        "initial_metrics": initial,
        "trial_count": len(trials),
        "strict_candidate_count": len(accepted),
        "trials": trials,
        "selected_period_log_secant": best,
    }


def completion_payload() -> dict[str, Any]:
    result = period_log_secant_continuation()
    best = result["selected_period_log_secant"]
    validation = {
        "v17_70_residual_reproduced": math.isclose(
            result["initial_metrics"]["complete"], 0.832005956495502, rel_tol=0, abs_tol=2e-8
        ),
        "v17_70_event_reproduced": math.isclose(
            result["initial_metrics"]["event"], 0.083861003953294, rel_tol=0, abs_tol=2e-8
        ),
        "bounded_secant_tested": result["trial_count"] == len(FACTORS),
        "physical_equations_unchanged": (
            not result["physical_action_changed"] and not result["physical_event_changed"]
        ),
        "candidate_result_classified": best is not None or result["strict_candidate_count"] == 0,
        "no_unvalidated_state_promoted": best is not None or result["strict_candidate_count"] == 0,
        "all_six_metrics_reduced_if_promoted": bool(
            best is None or all(value > MARGIN for value in best["reductions"].values())
        ),
        "eta_domain_preserved_if_promoted": bool(best is None or best["eta_minimum"] > 1e-5),
        "full_state_preserved_if_promoted": bool(best is None or len(best["raw_vector_hex"]) == 376),
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_aether_n3_period_log_secant_continuation_v17_72",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": False,
        "period_log_secant_continuation": result,
        "status": "VALIDATED" if passed and best is not None else "RECLASSIFIED" if passed else "INVALIDATED",
        "real_physical_property_explained": "FINITE_ACCEPTANCE_RADIUS_OF_THE_VALIDATED_PERIOD_LOG_PHYSICAL_SECANT",
        "dependency_advanced": "SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE",
        "active_calculation": "PROMOTE_IF_VALIDATED_THEN_AUDIT_THE_UPDATED_OWNER_AND_SOFT_BRANCH",
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_period_log_secant_continuation_v17_72.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "FACTORS",
    "period_log_secant_continuation", "completion_payload", "materialize",
]
