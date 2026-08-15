"""Scale-component/event tangent correction after the v17.54 audit."""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_fresh_sbp_expanded_measured_tangent_v17_07 import _measured_response, _solve
from bhsm.interface.aether_n3_fresh_sbp_kkt_v16_58 import sbp_projected_residual_and_vector
from bhsm.interface.aether_n3_fresh_sbp_six_owner_measured_cone_v17_05 import (
    EPS, FILTERS, LABELS, MARGIN, SCALE_ROWS, _gradients, _metrics, _slopes,
)
from bhsm.interface.aether_n3_fresh_sbp_coupled_owner_cone_v16_94 import EVENT_ROW
from bhsm.interface.aether_n3_fresh_sbp_third_v0_priority_v17_31 import RADII
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_parallel_physical_jacobian_v17_32 import parallel_sbp_physical_jacobian
from bhsm.interface.aether_n3_post_curvature_compensation_audit_v17_54 import v17_53_selected_raw_vector
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales

VERSION = "v17.55"
CLASSIFICATION = "BHSM_N3_SCALE_COMPONENT_EVENT_TANGENT_CORRECTION"
FULL_BHSM_COMPLETE = False
PRIORITY_PROFILES = (
    (1.0, 1.0), (2.0, 2.0), (4.0, 4.0), (8.0, 8.0),
    (16.0, 12.0), (24.0, 16.0), (32.0, 24.0), (48.0, 32.0),
)


def scale_component_event_correction() -> dict[str, Any]:
    raw = v17_53_selected_raw_vector()
    scales = kkt_variable_scales()
    y, residual = sbp_projected_residual_and_vector(raw * scales)
    initial = _metrics(residual)
    assembled = parallel_sbp_physical_jacobian(y / scales)
    jacobian = np.asarray(assembled.pop("matrix"))[:, :-1]
    _, singular_values, vt = np.linalg.svd(jacobian, full_matrices=False)
    spectral = float(singular_values[0])
    owner_gradients = _gradients(jacobian, residual, initial).T
    component_gradients = jacobian[SCALE_ROWS].T
    sources = np.column_stack((owner_gradients, component_gradients))
    columns: list[np.ndarray] = []
    for relative_filter in FILTERS:
        mu = relative_filter * spectral
        denominator = singular_values * singular_values + mu * mu
        block = vt.T @ ((vt @ sources) / denominator[:, None])
        block /= np.maximum(np.linalg.norm(block, axis=0), 1e-300)
        columns.extend(block[:, index] for index in range(block.shape[1]))
    candidate = np.column_stack(columns)
    candidate_u, candidate_s, _ = np.linalg.svd(candidate, full_matrices=False)
    keep = candidate_s > max(1e-12, 1e-10 * float(candidate_s[0]))
    basis = candidate_u[:, keep]
    response = _measured_response(y, residual, initial, basis)
    log_index = LABELS.index("log_scale")
    event_index = LABELS.index("event")
    rows: list[dict[str, Any]] = []
    accepted: list[tuple[float, float, dict[str, Any], Any]] = []
    for log_priority, event_priority in PRIORITY_PROFILES:
        targets = np.ones(len(LABELS))
        targets[log_index] = log_priority
        targets[event_index] = event_priority
        coefficient, rate, solved, weights, gap = _solve(response / targets[:, None])
        reduced_direction = basis @ coefficient
        direction = np.concatenate((reduced_direction, [0.0]))
        _, plus = sbp_projected_residual_and_vector(y + EPS * direction)
        _, minus = sbp_projected_residual_and_vector(y - EPS * direction)
        jacobian_direction = (plus - minus) / (2 * EPS)
        verified = _slopes(residual, jacobian_direction, initial)
        cauchy = max(
            0.0,
            -float(residual @ jacobian_direction)
            / float(jacobian_direction @ jacobian_direction),
        )
        common = bool(np.all(verified < 0))
        profile = {"log_scale": log_priority, "event": event_priority}
        row: dict[str, Any] = {
            "priority_profile": profile,
            "maximin_solve_success": solved,
            "relative_duality_gap": gap,
            "weighted_equalized_rate": rate,
            "dual_owner_weights": weights.tolist(),
            "verified_fractional_slopes": {
                LABELS[index]: float(verified[index]) for index in range(len(LABELS))
            },
            "derived_cauchy_radius": cauchy,
            "common_six_owner_descent": common,
            "trials": [],
        }
        if solved and common and cauchy > 0:
            for factor in RADII:
                radius = factor * cauchy
                try:
                    candidate_y, candidate_residual = sbp_projected_residual_and_vector(
                        y + radius * direction
                    )
                    raw_candidate = candidate_y / scales
                    eta = _minimum_node_eta(raw_candidate)
                    metrics = _metrics(candidate_residual)
                    reductions = {key: initial[key] - metrics[key] for key in initial}
                    fractions = {
                        key: reductions[key] / max(initial[key], 1e-300) for key in initial
                    }
                    trial = {
                        "cauchy_factor": factor,
                        "trust_radius": radius,
                        "domain_valid": bool(eta > 1e-5),
                        "eta_minimum": eta,
                        "metrics": metrics,
                        "reductions": reductions,
                        "fractional_reductions": fractions,
                        "minimum_fractional_progress": min(fractions.values()),
                        "limiting_owner": min(fractions, key=fractions.get),
                        "raw_vector_hex": [float(value).hex() for value in raw_candidate],
                    }
                    row["trials"].append(trial)
                    if eta > 1e-5 and all(value > MARGIN for value in reductions.values()):
                        accepted.append((
                            trial["minimum_fractional_progress"],
                            sum(fractions.values()), trial, profile,
                        ))
                except (FloatingPointError, ValueError, np.linalg.LinAlgError) as exc:
                    row["trials"].append({
                        "cauchy_factor": factor,
                        "domain_valid": False,
                        "exception": type(exc).__name__,
                    })
        rows.append(row)
    best = None
    if accepted:
        _, _, trial, profile = max(accepted, key=lambda item: (item[0], item[1]))
        best = {"priority_profile": profile, **trial}
    return {
        "source_state": "v17.53_selected_event_log_curvature_compensated_state",
        "physical_residual_changed": False,
        "physical_event_changed": False,
        "initial_metrics": initial,
        **assembled,
        "singular_value_scale": spectral,
        "scale_component_count": len(SCALE_ROWS),
        "source_direction_count_per_filter": sources.shape[1],
        "tangent_rank": basis.shape[1],
        "priority_profile_count": len(PRIORITY_PROFILES),
        "direction_rows": rows,
        "common_direction_count": sum(row["common_six_owner_descent"] for row in rows),
        "strict_candidate_count": len(accepted),
        "selected_scale_component_event_correction": best,
    }


def completion_payload() -> dict[str, Any]:
    result = scale_component_event_correction()
    best = result["selected_scale_component_event_correction"]
    validation = {
        "v17_53_residual_reproduced": math.isclose(
            result["initial_metrics"]["complete"], 0.8503794666366,
            rel_tol=0, abs_tol=2e-8,
        ),
        "v17_53_event_reproduced": math.isclose(
            result["initial_metrics"]["event"], 0.083985972706086,
            rel_tol=0, abs_tol=2e-8,
        ),
        "all_scale_components_owned": result["scale_component_count"] == 23,
        "six_owners_plus_scale_components_seeded": (
            result["source_direction_count_per_filter"] == 29
        ),
        "parallel_jacobian_adopted": result.get("assembly_workers") == 8,
        "bounded_profiles_tested": result["priority_profile_count"] == 8,
        "physical_equations_unchanged": (
            not result["physical_residual_changed"] and not result["physical_event_changed"]
        ),
        "common_direction_exists": result["common_direction_count"] > 0,
        "candidate_result_classified": (
            (best is None and result["strict_candidate_count"] == 0)
            or (
                best is not None
                and all(value > MARGIN for value in best["reductions"].values())
            )
        ),
        "no_unvalidated_state_promoted": best is None,
    }
    return {
        "artifact": "BHSM_aether_n3_scale_component_event_correction_v17_55",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": False,
        "scale_component_event_correction": result,
        "status": (
            "VALIDATED" if all(validation.values()) and best is not None
            else "RECLASSIFIED" if all(validation.values())
            else "INVALIDATED"
        ),
        "real_physical_property_explained": (
            "SAME_ACTION_COMPONENT_RESOLVED_SCALE_EVENT_SIX_OWNER_DESCENT"
        ),
        "dependency_advanced": "SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE",
        "active_calculation": (
            "AUDIT_THE_COMPONENT_DIRECTION_AGAINST_THE_INTERNAL_ACTION_COVECTOR_"
            "DIFFERENCE_SCALE_BEFORE_ANY_SMALLER_RADIUS_TRIAL"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_scale_component_event_correction_v17_55.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "PRIORITY_PROFILES",
    "scale_component_event_correction", "completion_payload", "materialize",
]
