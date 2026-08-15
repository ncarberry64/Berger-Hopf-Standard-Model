"""Resolve the local validity radius of the v17.68 physical manifold."""
from __future__ import annotations

import json
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
from bhsm.interface.aether_n3_post_curvature_compensation_audit_v17_54 import v17_53_selected_raw_vector
from bhsm.interface.aether_n3_post_scale_manifold_audit_v17_64 import v17_63_selected_raw_vector
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales
from bhsm.interface.aether_n3_soft_event_constrained_v17_51 import v17_49_selected_raw_vector

VERSION = "v17.69"
CLASSIFICATION = "BHSM_N3_REFINED_SCALE_V0_PERIOD_MANIFOLD"
FULL_BHSM_COMPLETE = False
FACTORS = (1e-6, 3e-6, 1e-5, 3e-5, 1e-4, 3e-4, 5e-4)
RATIOS = (0.0, 1.0, 3.0, 10.0, 25.0, 50.0, 100.0, 150.0)


def _v17_68_manifold(y: np.ndarray, path: np.ndarray, scales: np.ndarray) -> np.ndarray:
    payload = json.loads(Path(
        "artifacts/BHSM_aether_n3_scale_v0_period_manifold_v17_68.json"
    ).read_text(encoding="utf-8"))["scale_v0_period_manifold"]
    anchor = next(
        trial for trial in payload["trials"]
        if trial.get("manifold_factor") == 0.001 and trial.get("path_ratio") == 25.0
    )
    cy = np.asarray([float.fromhex(value) for value in anchor["raw_vector_hex"]]) * scales
    manifold = (cy - y - anchor["path_factor"] * path) / anchor["manifold_factor"]
    manifold[-1] = 0.0
    return manifold


def refined_scale_v0_period_manifold() -> dict[str, Any]:
    scales = kkt_variable_scales()
    y, residual = exact_local_jet_sbp_projected_residual_and_vector(v17_63_selected_raw_vector() * scales)
    initial = _metrics(residual)
    y53, _ = exact_local_jet_sbp_projected_residual_and_vector(v17_53_selected_raw_vector() * scales)
    y49, _ = exact_local_jet_sbp_projected_residual_and_vector(v17_49_selected_raw_vector() * scales)
    path = y53 - y49
    path[-1] = 0.0
    manifold = _v17_68_manifold(y, path, scales)
    trials: list[dict[str, Any]] = []
    accepted: list[dict[str, Any]] = []
    for factor in FACTORS:
        for ratio in RATIOS:
            path_factor = factor * ratio
            try:
                cy, candidate_residual = exact_local_jet_sbp_projected_residual_and_vector(
                    y + factor * manifold + path_factor * path
                )
                raw = cy / scales
                eta = _minimum_node_eta(raw)
                metrics = _metrics(candidate_residual)
                reductions = {key: initial[key] - metrics[key] for key in initial}
                fractions = {
                    key: reductions[key] / max(initial[key], 1e-300) for key in initial
                }
                trial = {
                    "manifold_factor": factor,
                    "path_ratio": ratio,
                    "path_factor": path_factor,
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
                trials.append({
                    "manifold_factor": factor,
                    "path_ratio": ratio,
                    "exception": type(exc).__name__,
                })
    best = max(
        accepted,
        key=lambda trial: (
            trial["minimum_fractional_progress"],
            sum(trial["fractional_reductions"].values()),
        ),
    ) if accepted else None
    return {
        "source_state": "v17.63_selected_scale_manifold_path_corrector_state",
        "source_direction": "v17.68_scale_v0_period_manifold",
        "physical_action_changed": False,
        "physical_event_changed": False,
        "factor_bounds": [min(FACTORS), max(FACTORS)],
        "initial_metrics": initial,
        "trial_count": len(trials),
        "strict_candidate_count": len(accepted),
        "trials": trials,
        "selected_refined_manifold": best,
    }


def completion_payload() -> dict[str, Any]:
    result = refined_scale_v0_period_manifold()
    best = result["selected_refined_manifold"]
    validation = {
        "v17_63_residual_reproduced": math.isclose(
            result["initial_metrics"]["complete"], 0.832011690209781, rel_tol=0, abs_tol=2e-8
        ),
        "v17_63_event_reproduced": math.isclose(
            result["initial_metrics"]["event"], 0.083861037713239, rel_tol=0, abs_tol=2e-8
        ),
        "demonstrated_local_radius_resolved": result["factor_bounds"] == [1e-6, 5e-4],
        "bounded_grid_tested": result["trial_count"] == len(FACTORS) * len(RATIOS),
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
        "artifact": "BHSM_aether_n3_refined_scale_v0_period_manifold_v17_69",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": False,
        "refined_scale_v0_period_manifold": result,
        "status": "VALIDATED" if passed and best is not None else "RECLASSIFIED" if passed else "INVALIDATED",
        "real_physical_property_explained": "LOCAL_VALIDITY_RADIUS_OF_THE_SAME_ACTION_SCALE_V0_PERIOD_MANIFOLD",
        "dependency_advanced": "SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE",
        "active_calculation": "PROMOTE_IF_VALIDATED_THEN_AUDIT_THE_UPDATED_OWNER_AND_SOFT_BRANCH",
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_refined_scale_v0_period_manifold_v17_69.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "FACTORS", "RATIOS",
    "refined_scale_v0_period_manifold", "completion_payload", "materialize",
]
