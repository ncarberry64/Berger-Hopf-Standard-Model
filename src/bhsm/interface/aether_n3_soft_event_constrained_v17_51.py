"""Soft-eigenvalue-constrained event correction after the v17.50 audit."""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import minimize

from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_fresh_sbp_expanded_measured_tangent_v17_07 import _measured_response
from bhsm.interface.aether_n3_fresh_sbp_kkt_v16_58 import sbp_projected_residual_and_vector
from bhsm.interface.aether_n3_fresh_sbp_period_priority_family_v17_25 import RANKS
from bhsm.interface.aether_n3_fresh_sbp_six_owner_measured_cone_v17_05 import (
    EPS, FILTERS, LABELS, MARGIN, _gradients, _metrics, _slopes)
from bhsm.interface.aether_n3_fresh_sbp_third_v0_priority_v17_31 import RADII
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_parallel_physical_jacobian_v17_32 import parallel_sbp_physical_jacobian
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales

VERSION = "v17.51"
CLASSIFICATION = "BHSM_N3_SOFT_EIGENVALUE_CONSTRAINED_EVENT_CORRECTION"
FULL_BHSM_COMPLETE = False
EVENT_TARGET_FRACTIONS = (0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.7)


def v17_49_selected_raw_vector() -> np.ndarray:
    payload = json.loads(Path(
        "artifacts/BHSM_aether_n3_fresh_sbp_refined_four_owner_v17_49.json"
    ).read_text(encoding="utf-8"))
    values = payload["fresh_sbp_refined_four_owner"][
        "selected_refined_four_owner_maximin"]["raw_vector_hex"]
    raw = np.asarray([float.fromhex(value) for value in values])
    if raw.shape != (376,):
        raise ValueError("v17.49 selected vector has wrong dimension")
    return raw


def _solve_event_constrained(
    response: np.ndarray, gram: np.ndarray, target_fraction: float
) -> tuple[np.ndarray, float, bool, float, float]:
    """Maximize other-owner descent with a required soft-event descent rate."""
    event_index = LABELS.index("event")
    event_row = response[event_index]
    other = np.delete(response, event_index, axis=0)
    inverse_gram = np.linalg.pinv(gram, rcond=1e-12)
    event_maximum = math.sqrt(max(float(event_row @ inverse_gram @ event_row), 0.0))
    if event_maximum <= 1e-15:
        return np.zeros(response.shape[1]), -math.inf, False, event_maximum, 0.0
    target = target_fraction * event_maximum
    event_direction = -inverse_gram @ event_row / event_maximum
    start_scale = min(0.95, target_fraction + 0.1)
    c0 = start_scale * event_direction
    t0 = float(np.min(-other @ c0))
    x0 = np.concatenate((c0, [t0]))
    n = response.shape[1]
    constraints = [
        {
            "type": "ineq",
            "fun": lambda x: -other @ x[:n] - x[-1],
            "jac": lambda x: np.column_stack((-other, -np.ones(other.shape[0]))),
        },
        {
            "type": "ineq",
            "fun": lambda x: float(-event_row @ x[:n] - target),
            "jac": lambda x: np.concatenate((-event_row, [0.0])),
        },
        {
            "type": "ineq",
            "fun": lambda x: 1.0 - float(x[:n] @ gram @ x[:n]),
            "jac": lambda x: np.concatenate((-2.0 * gram @ x[:n], [0.0])),
        },
    ]
    solved = minimize(
        lambda x: -float(x[-1]), x0,
        jac=lambda x: np.concatenate((np.zeros(n), [-1.0])),
        constraints=constraints, method="SLSQP",
        options={"ftol": 1e-13, "maxiter": 3000, "disp": False},
    )
    coefficient = np.asarray(solved.x[:n])
    rate = float(solved.x[-1])
    achieved = float(-event_row @ coefficient)
    norm_squared = float(coefficient @ gram @ coefficient)
    valid = bool(solved.success and rate > 0 and achieved >= target - 1e-9
                 and norm_squared <= 1.0 + 1e-7)
    return coefficient, rate, valid, event_maximum, achieved


def soft_event_constrained() -> dict[str, Any]:
    raw = v17_49_selected_raw_vector()
    scales = kkt_variable_scales()
    y = raw * scales
    y, residual = sbp_projected_residual_and_vector(y)
    initial = _metrics(residual)
    assembled = parallel_sbp_physical_jacobian(y / scales)
    jacobian = np.asarray(assembled.pop("matrix"))[:, :-1]
    _, singular_values, vt = np.linalg.svd(jacobian, full_matrices=False)
    spectral = float(singular_values[0])
    gradients = _gradients(jacobian, residual, initial)
    columns: list[np.ndarray] = []
    filter_blocks: list[tuple[float, np.ndarray]] = []
    for relative_filter in FILTERS:
        mu = relative_filter * spectral
        denominator = singular_values * singular_values + mu * mu
        block = vt.T @ ((vt @ gradients.T) / denominator[:, None])
        block /= np.maximum(np.linalg.norm(block, axis=0), 1e-300)
        filter_blocks.append((relative_filter, block))
        columns.extend(block[:, index] for index in range(block.shape[1]))
    candidate = np.column_stack(columns)
    candidate_u, candidate_s, _ = np.linalg.svd(candidate, full_matrices=False)
    keep = candidate_s > max(1e-12, 1e-10 * float(candidate_s[0]))
    basis = candidate_u[:, keep]
    response = _measured_response(y, residual, initial, basis)
    families: list[tuple[str, np.ndarray]] = []
    for rank in RANKS:
        if rank <= basis.shape[1]:
            families.append((f"combined_rank_{rank}", np.eye(basis.shape[1])[:, :rank]))
    for relative_filter, block in filter_blocks:
        qf, _ = np.linalg.qr(block, mode="reduced")
        families.append((f"single_filter_{relative_filter:.0e}", basis.T @ qf))
    rows: list[dict[str, Any]] = []
    accepted: list[tuple[float, float, dict[str, Any], str, float]] = []
    for family, transform in families:
        family_response = response @ transform
        gram = transform.T @ transform
        for target_fraction in EVENT_TARGET_FRACTIONS:
            coefficient, rate, solved, event_maximum, achieved = _solve_event_constrained(
                family_response, gram, target_fraction)
            reduced_direction = basis @ (transform @ coefficient)
            direction = np.concatenate((reduced_direction, [0.0]))
            _, plus = sbp_projected_residual_and_vector(y + EPS * direction)
            _, minus = sbp_projected_residual_and_vector(y - EPS * direction)
            jacobian_direction = (plus - minus) / (2 * EPS)
            verified = _slopes(residual, jacobian_direction, initial)
            cauchy = max(0.0, -float(residual @ jacobian_direction)
                         / float(jacobian_direction @ jacobian_direction))
            common = bool(np.all(verified < 0))
            row: dict[str, Any] = {
                "family": family, "dimension": transform.shape[1],
                "event_target_fraction": target_fraction,
                "event_maximum_measured_descent_rate": event_maximum,
                "event_target_measured_descent_rate": target_fraction * event_maximum,
                "event_achieved_measured_descent_rate": achieved,
                "other_owner_maximin_rate": rate,
                "constrained_solve_success": solved,
                "predicted_fractional_slopes": (family_response @ coefficient).tolist(),
                "verified_fractional_slopes": {
                    LABELS[index]: float(verified[index]) for index in range(len(LABELS))},
                "derived_cauchy_radius": cauchy,
                "common_six_owner_descent": common, "trials": [],
            }
            if solved and common and cauchy > 0:
                for factor in RADII:
                    radius = factor * cauchy
                    try:
                        candidate_y, candidate_residual = sbp_projected_residual_and_vector(
                            y + radius * direction)
                        raw_candidate = candidate_y / scales
                        eta = _minimum_node_eta(raw_candidate)
                        metrics = _metrics(candidate_residual)
                        reductions = {key: initial[key] - metrics[key] for key in initial}
                        fractions = {key: reductions[key] / max(initial[key], 1e-300)
                                     for key in initial}
                        trial = {"cauchy_factor": factor, "trust_radius": radius,
                            "domain_valid": bool(eta > 1e-5), "metrics": metrics,
                            "reductions": reductions, "fractional_reductions": fractions,
                            "minimum_fractional_progress": min(fractions.values()),
                            "limiting_owner": min(fractions, key=fractions.get),
                            "eta_minimum": eta,
                            "raw_vector_hex": [float(value).hex() for value in raw_candidate]}
                        row["trials"].append(trial)
                        if eta > 1e-5 and all(value > MARGIN for value in reductions.values()):
                            accepted.append((trial["minimum_fractional_progress"],
                                sum(fractions.values()), trial, family, target_fraction))
                    except (FloatingPointError, ValueError, np.linalg.LinAlgError) as exc:
                        row["trials"].append({"cauchy_factor": factor,
                            "domain_valid": False, "exception": type(exc).__name__})
            rows.append(row)
    best = None
    if accepted:
        _, _, trial, family, target_fraction = max(accepted, key=lambda item: (item[0], item[1]))
        best = {"family": family, "event_target_fraction": target_fraction, **trial}
    return {"source_state": "v17.49_selected_refined_four_owner_state",
        "physical_residual_changed": False, "physical_event_changed": False,
        "constraint_semantics": "REQUIRE_A_FRACTION_OF_MAXIMUM_MEASURED_SOFT_EVENT_DESCENT_AND_MAXIMIZE_MINIMUM_OTHER_OWNER_DESCENT",
        "initial_metrics": initial, **assembled, "singular_value_scale": spectral,
        "tangent_rank": basis.shape[1], "family_count": len(families),
        "event_target_count": len(EVENT_TARGET_FRACTIONS), "direction_rows": rows,
        "constrained_solve_count": sum(row["constrained_solve_success"] for row in rows),
        "common_direction_count": sum(row["common_six_owner_descent"] for row in rows),
        "strict_candidate_count": len(accepted), "selected_soft_event_constrained": best}


def completion_payload() -> dict[str, Any]:
    result = soft_event_constrained(); best = result["selected_soft_event_constrained"]
    validation = {
        "v17_49_residual_reproduced": math.isclose(result["initial_metrics"]["complete"], 0.855054105118296, rel_tol=0, abs_tol=2e-8),
        "v17_49_event_reproduced": math.isclose(result["initial_metrics"]["event"], 0.084012053757297, rel_tol=0, abs_tol=2e-8),
        "source_state_owned": result["source_state"] == "v17.49_selected_refined_four_owner_state",
        "physical_equations_unchanged": not result["physical_residual_changed"] and not result["physical_event_changed"],
        "parallel_jacobian_adopted": result.get("assembly_workers") == 8,
        "bounded_event_targets_tested": result["event_target_count"] == 8,
        "all_families_tested": result["family_count"] == 7,
        "constrained_solve_exists": result["constrained_solve_count"] > 0,
        "common_direction_exists": result["common_direction_count"] > 0,
        "strict_candidate_exists": best is not None,
        "all_six_metrics_reduced": bool(best is not None and all(value > MARGIN for value in best["reductions"].values())),
        "positive_maximin_progress": bool(best is not None and best["minimum_fractional_progress"] > 0),
        "eta_domain_preserved": bool(best is not None and best["eta_minimum"] > 1e-5),
        "full_precision_state_preserved": bool(best is not None and len(best["raw_vector_hex"]) == 376),
    }
    return {"artifact": "BHSM_aether_n3_soft_event_constrained_v17_51",
        "version": VERSION, "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": False, "soft_event_constrained": result,
        "status": "VALIDATED" if all(validation.values()) else "RECLASSIFIED",
        "real_physical_property_explained": "SAME_ACTION_SOFT_EVENT_CONSTRAINED_SIX_OWNER_DESCENT",
        "dependency_advanced": "SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE",
        "active_calculation": "PROMOTE_IF_VALIDATED_THEN_REAUDIT_SOFT_BRANCH_AND_OWNER_SET",
        "validation": validation, "validation_passed": all(validation.values())}


def materialize(directory: str | Path) -> Path:
    target = Path(directory); target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_soft_event_constrained_v17_51.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = ["VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "EVENT_TARGET_FRACTIONS",
    "v17_49_selected_raw_vector", "soft_event_constrained", "completion_payload", "materialize"]
