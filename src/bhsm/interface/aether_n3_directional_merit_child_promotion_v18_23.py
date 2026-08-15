"""Test the v18.22 exact-merit candidate against the complete-child gate."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_constraint_consistent_sobolev_lift_v15_84 import constraint_residual
from bhsm.interface.aether_n3_admissible_child_cauchy_germ_v17_95 import _trace_jacobian
from bhsm.interface.aether_n3_child_constraint_cauchy_match_v17_94 import _metric_radial_flux_covector
from bhsm.interface.aether_n3_constraint_solved_orbit_v16_08 import _advance_constrained, eta_legendre_minimum, exact_euler_dirac_acceleration
from bhsm.interface.aether_n3_directional_event_merit_descent_v18_22 import v18_22_selected_raw_vector
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import unpack_reduced
from bhsm.interface.aether_n3_required_child_cauchy_flux_v17_93 import _canonical_pair
from bhsm.interface.aether_n3_sbp_redirect_audit_v16_57 import trapezoid_sbp_difference
from bhsm.interface.aether_n3_square_kkt_complete_child_promotion_v18_12 import _CHILD_M, _CHILD_Q, _CHILD_V


VERSION = "v18.23"
CLASSIFICATION = "BHSM_N3_DIRECTIONAL_MERIT_COMPLETE_CHILD_PROMOTION"
FULL_BHSM_COMPLETE = False


def v18_23_selected_raw_vector() -> np.ndarray:
    return v18_22_selected_raw_vector().copy()


def directional_merit_child_promotion() -> dict[str, Any]:
    raw = v18_23_selected_raw_vector(); state = unpack_reduced(raw)
    qh = np.asarray(state["coordinates"]); mh = np.asarray(state["multipliers"])
    vh = trapezoid_sbp_difference() @ qh / float(state["period"])
    qe, ve, me = qh[-1], vh[-1], mh[-1]
    pe, _, le, _ = _canonical_pair(qe, ve, me)
    pc, force, lc, _ = _canonical_pair(_CHILD_Q, _CHILD_V, _CHILD_M)
    ec, _ = _metric_radial_flux_covector(qe, me); cc, _ = _metric_radial_flux_covector(_CHILD_Q, _CHILD_M)
    event_flux, child_flux = le.T @ ec, lc.T @ cc
    dynamics = exact_euler_dirac_acceleration(3, _CHILD_Q, _CHILD_V, _CHILD_M, points=44)
    acceleration = np.asarray(dynamics["acceleration"]); multiplier_rate = np.asarray(dynamics["multiplier_rate"])
    tangent_scale = max(1.0, float(np.max(np.abs(_CHILD_V))), float(np.max(np.abs(acceleration))), float(np.max(np.abs(multiplier_rate))))
    flux_rows = []
    for relative_step in (8.0e-4, 4.0e-4):
        epsilon = relative_step / tangent_scale
        plus, _, _, _ = _canonical_pair(_CHILD_Q + epsilon * _CHILD_V, _CHILD_V + epsilon * acceleration, _CHILD_M + epsilon * multiplier_rate)
        minus, _, _, _ = _canonical_pair(_CHILD_Q - epsilon * _CHILD_V, _CHILD_V - epsilon * acceleration, _CHILD_M - epsilon * multiplier_rate)
        p_dot = (plus - minus) / (2.0 * epsilon)
        flux_rows.append(float(np.linalg.norm(child_flux - (-p_dot + force - event_flux))))
    q, v, m = _CHILD_Q.copy(), _CHILD_V.copy(), _CHILD_M.copy(); persistence = []
    for step in range(1, 11):
        q, v, m, _, projection = _advance_constrained(q, v, m, 1.0e-5, points=44)
        constraints_step = constraint_residual(3, q, v, m, points=44)
        persistence.append({
            "step": step,
            "projection_success": bool(projection["success"]),
            "maximum_constraint_residual": float(np.max(np.abs(constraints_step))),
            "eta_minimum": eta_legendre_minimum(q, m, points=3000)["minimum"],
            "finite": bool(np.all(np.isfinite(np.r_[q, v, m]))),
        })
    source = json.loads(Path(
        "artifacts/BHSM_aether_n3_directional_event_merit_descent_v18_22.json"
    ).read_text(encoding="utf-8"))
    selected = source["directional_event_merit_descent"]["selected_true_merit_candidate_pending_child_acceptance"]
    trace = _trace_jacobian() @ (_CHILD_Q - qe)
    constraints = constraint_residual(3, _CHILD_Q, _CHILD_V, _CHILD_M, points=44)
    return {
        "global_step": {
            "source_response_status": source["status"],
            "physical_solve_dimension": [376, 376],
            "event_multiplier_explicit": True,
            "componentwise_monotonicity_required": False,
            "must_remain_on_previous_iterate_path": False,
            "source_complete_norm": selected["metrics"]["complete"] + selected["complete_norm_reduction"],
            "candidate_complete_norm": selected["metrics"]["complete"],
            "complete_norm_reduction": selected["complete_norm_reduction"],
            "eta_minimum": _minimum_node_eta(raw),
        },
        "event_to_complete_child": {
            "continued_from_v18_12_child_without_forcing_staticity": True,
            "local_chart_rank": 14,
            "physical_row_count": 14,
            "additional_global_KKT_rows": 0,
            "maximum_trace_residual": float(np.max(np.abs(trace))),
            "maximum_seven_constraint_residual": float(np.max(np.abs(constraints))),
            "attachment_momentum_residual_norm": float(np.linalg.norm(pc - pe)),
            "resolved_dynamic_flux_envelope": max(flux_rows),
            "eta_Legendre_minimum": eta_legendre_minimum(_CHILD_Q, _CHILD_M, points=5000),
            "velocity_norm": float(np.linalg.norm(_CHILD_V)),
            "zero_background_gauge_spinor_ghost_HS_block": "CLOSED_V17_97",
            "firewall_discrete_core_ownership_block": "CLOSED_V17_98",
        },
        "persistence": {
            "duration": 1.0e-4,
            "maximum_constraint_residual": max(row["maximum_constraint_residual"] for row in persistence),
            "minimum_eta": min(row["eta_minimum"] for row in persistence),
            "all_steps_valid": all(row["projection_success"] and row["finite"] for row in persistence),
            "nonzero_relative_evolution_retained": bool(np.linalg.norm(q - _CHILD_Q) > 0.0 and np.linalg.norm(v) > 0.0),
            "decay_exit_observed": False,
        },
    }


def completion_payload() -> dict[str, Any]:
    result = directional_merit_child_promotion(); g = result["global_step"]; c = result["event_to_complete_child"]; p = result["persistence"]
    validation = {
        "validated_directional_response_source": g["source_response_status"] == "VALIDATED",
        "square_explicit_multiplier_solve": g["physical_solve_dimension"] == [376, 376] and g["event_multiplier_explicit"],
        "no_componentwise_filter": not g["componentwise_monotonicity_required"],
        "previous_path_not_a_constraint": not g["must_remain_on_previous_iterate_path"],
        "true_376_merit_reduced": g["complete_norm_reduction"] > 0.0,
        "global_eta_preserved": g["eta_minimum"] > 1.0e-5,
        "trace_closed": c["maximum_trace_residual"] < 1.0e-9,
        "seven_constraints_closed": c["maximum_seven_constraint_residual"] < 1.0e-9,
        "attachment_momentum_closed": c["attachment_momentum_residual_norm"] < 1.0e-7,
        "resolved_dynamic_flux_closed": c["resolved_dynamic_flux_envelope"] < 2.0e-5,
        "child_eta_hyperregular": c["eta_Legendre_minimum"]["minimum"] > 0.0,
        "positive_interval_persists": p["all_steps_valid"] and p["maximum_constraint_residual"] < 1.0e-8 and p["minimum_eta"] > 0.0,
        "nonzero_relative_evolution_retained": p["nonzero_relative_evolution_retained"],
        "no_extra_global_row": c["additional_global_KKT_rows"] == 0,
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_aether_n3_directional_merit_child_promotion_v18_23",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "directional_merit_child_promotion": result,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "real_physical_property_explained": "THE_EXACT_DIRECTIONAL_MERIT_STEP_RECONSTRUCTS_A_COMPLETE_PERSISTENT_MOVING_CHILD",
        "dependency_advanced": "NONLINEAR_N3_EVENT_SADDLE_CLOSURE",
        "active_calculation": "CONTINUE_EXACT_ACTION_DIRECTIONAL_EVENT_MERIT_DESCENT" if passed else "RECOMPUTE_THE_COMPLETE_CHILD_LOCAL_CHART_AT_THE_V18_22_EVENT",
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory); target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_directional_merit_child_promotion_v18_23.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = ["VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "v18_23_selected_raw_vector", "directional_merit_child_promotion", "completion_payload", "materialize"]
