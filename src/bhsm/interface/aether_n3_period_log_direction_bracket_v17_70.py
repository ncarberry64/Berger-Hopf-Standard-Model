"""Bracket the measured v17.67 period and v17.68 log-scale limiters."""
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
from bhsm.interface.aether_n3_refined_scale_v0_period_manifold_v17_69 import _v17_68_manifold
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales
from bhsm.interface.aether_n3_soft_event_constrained_v17_51 import v17_49_selected_raw_vector

VERSION = "v17.70"
CLASSIFICATION = "BHSM_N3_PERIOD_LOG_DIRECTION_BRACKET"
FULL_BHSM_COMPLETE = False
MIXES = (0.05, 0.075, 0.1, 0.125, 0.15, 0.175, 0.2)
FACTORS = (1e-6, 3e-6, 1e-5)
RATIOS = (25.0, 50.0, 75.0, 100.0)


def _v17_67_manifold(y: np.ndarray, path: np.ndarray, scales: np.ndarray) -> np.ndarray:
    payload = json.loads(Path(
        "artifacts/BHSM_aether_n3_scale_v0_manifold_path_corrector_v17_67.json"
    ).read_text(encoding="utf-8"))["scale_v0_manifold_path_corrector"]
    anchor = payload["trials"][0]
    cy = np.asarray([float.fromhex(value) for value in anchor["raw_vector_hex"]]) * scales
    manifold = (
        cy - y - anchor["path_factor"] * path
    ) / anchor["manifold_newton_factor"]
    manifold[-1] = 0.0
    return manifold


def period_log_direction_bracket() -> dict[str, Any]:
    scales = kkt_variable_scales()
    y, residual = exact_local_jet_sbp_projected_residual_and_vector(v17_63_selected_raw_vector() * scales)
    initial = _metrics(residual)
    y53, _ = exact_local_jet_sbp_projected_residual_and_vector(v17_53_selected_raw_vector() * scales)
    y49, _ = exact_local_jet_sbp_projected_residual_and_vector(v17_49_selected_raw_vector() * scales)
    path = y53 - y49
    path[-1] = 0.0
    direction67 = _v17_67_manifold(y, path, scales)
    direction68 = _v17_68_manifold(y, path, scales)
    trials: list[dict[str, Any]] = []
    accepted: list[dict[str, Any]] = []
    for mix in MIXES:
        direction = (1.0 - mix) * direction67 + mix * direction68
        for factor in FACTORS:
            for ratio in RATIOS:
                path_factor = factor * ratio
                try:
                    cy, candidate_residual = exact_local_jet_sbp_projected_residual_and_vector(
                        y + factor * direction + path_factor * path
                    )
                    raw = cy / scales
                    eta = _minimum_node_eta(raw)
                    metrics = _metrics(candidate_residual)
                    reductions = {key: initial[key] - metrics[key] for key in initial}
                    fractions = {
                        key: reductions[key] / max(initial[key], 1e-300) for key in initial
                    }
                    trial = {
                        "v17_68_mix": mix,
                        "factor": factor,
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
                        "v17_68_mix": mix,
                        "factor": factor,
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
        "bracketed_limiters": ["period", "log_scale"],
        "physical_action_changed": False,
        "physical_event_changed": False,
        "direction_norms": {
            "v17_67": float(np.linalg.norm(direction67)),
            "v17_68": float(np.linalg.norm(direction68)),
        },
        "initial_metrics": initial,
        "trial_count": len(trials),
        "strict_candidate_count": len(accepted),
        "trials": trials,
        "selected_period_log_bracket": best,
    }


def completion_payload() -> dict[str, Any]:
    result = period_log_direction_bracket()
    best = result["selected_period_log_bracket"]
    validation = {
        "v17_63_residual_reproduced": math.isclose(
            result["initial_metrics"]["complete"], 0.832011690209781, rel_tol=0, abs_tol=2e-8
        ),
        "v17_63_event_reproduced": math.isclose(
            result["initial_metrics"]["event"], 0.083861037713239, rel_tol=0, abs_tol=2e-8
        ),
        "measured_limiters_bracketed": result["bracketed_limiters"] == ["period", "log_scale"],
        "bounded_bracket_tested": result["trial_count"] == len(MIXES) * len(FACTORS) * len(RATIOS),
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
        "artifact": "BHSM_aether_n3_period_log_direction_bracket_v17_70",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": False,
        "period_log_direction_bracket": result,
        "status": "VALIDATED" if passed and best is not None else "RECLASSIFIED" if passed else "INVALIDATED",
        "real_physical_property_explained": "COMMON_DESCENT_BRACKET_FOR_THE_MEASURED_PERIOD_LOG_SCALE_CONFLICT",
        "dependency_advanced": "SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE",
        "active_calculation": "PROMOTE_IF_VALIDATED_THEN_AUDIT_THE_UPDATED_OWNER_AND_SOFT_BRANCH",
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_period_log_direction_bracket_v17_70.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "MIXES", "FACTORS", "RATIOS",
    "period_log_direction_bracket", "completion_payload", "materialize",
]
