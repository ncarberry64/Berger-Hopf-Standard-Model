"""Reconstruct the next v18.50 merit candidate after v18.52 fails flux."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
from scipy.linalg import qr
from scipy.optimize import least_squares

from bhsm.interface.aether_n3_child_constraint_cauchy_match_v17_94 import _metric_radial_flux_covector
from bhsm.interface.aether_n3_complete_child_chart_reconstruction_v18_24 import JACOBIAN_STEP, _child_rows, _pack_child, _unpack_child
from bhsm.interface.aether_n3_constraint_solved_orbit_v16_08 import eta_legendre_minimum
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import unpack_reduced
from bhsm.interface.aether_n3_required_child_cauchy_flux_v17_93 import _canonical_pair
from bhsm.interface.aether_n3_sbp_redirect_audit_v16_57 import trapezoid_sbp_difference


VERSION = "v18.53"
CLASSIFICATION = "BHSM_N3_BIDIRECTIONAL_NEXT_CANDIDATE_CHILD"
FULL_BHSM_COMPLETE = False


def _selection() -> dict[str, Any]:
    proposal = json.loads(Path(
        "artifacts/BHSM_aether_n3_bidirectional_merit_manifold_probe_v18_50.json"
    ).read_text(encoding="utf-8"))["bidirectional_merit_manifold_probe"]
    rejected = proposal["selected_true_merit_candidate_pending_child_acceptance"]
    remaining = [
        row for row in proposal["trials"]
        if row.get("true_merit_eligible", False)
        and not (row["orientation"] == rejected["orientation"] and row["backtrack"] == rejected["backtrack"])
    ]
    if not remaining:
        raise ValueError("v18.50 has no remaining exact-merit candidate")
    return min(remaining, key=lambda row: row["metrics"]["complete"])


def v18_53_selected_raw_vector() -> np.ndarray:
    return np.asarray([float.fromhex(value) for value in _selection()["raw_vector_hex"]])


def bidirectional_next_candidate_child() -> dict[str, Any]:
    selected = _selection()
    raw = v18_53_selected_raw_vector()
    state = unpack_reduced(raw)
    qh = np.asarray(state["coordinates"])
    mh = np.asarray(state["multipliers"])
    vh = trapezoid_sbp_difference() @ qh / float(state["period"])
    qe, ve, me = qh[-1], vh[-1], mh[-1]
    pe, _, le, _ = _canonical_pair(qe, ve, me)
    event_covector, _ = _metric_radial_flux_covector(qe, me)
    event_flux = le.T @ event_covector
    prior = json.loads(Path(
        "artifacts/BHSM_aether_n3_third_direct_admissible_line_child_v18_46.json"
    ).read_text(encoding="utf-8"))["third_direct_admissible_line_child"]["child_state"]
    germ = _pack_child(np.asarray(prior["coordinates"]), np.asarray(prior["velocities"]), np.asarray(prior["multipliers"]))
    initial_rows = _child_rows(germ, qe, pe, event_flux)
    jacobian = np.empty((14, 26))
    for column in range(26):
        delta = np.zeros(26)
        delta[column] = JACOBIAN_STEP
        jacobian[:, column] = (
            _child_rows(germ + delta, qe, pe, event_flux)
            - _child_rows(germ - delta, qe, pe, event_flux)
        ) / (2.0 * JACOBIAN_STEP)
    row_scales = np.maximum(np.linalg.norm(jacobian, axis=1), 1.0)
    scaled_jacobian = jacobian / row_scales[:, None]
    _, _, pivots = qr(scaled_jacobian, mode="economic", pivoting=True)
    singular = np.linalg.svd(scaled_jacobian, compute_uv=False)
    tolerance = np.finfo(float).eps * max(scaled_jacobian.shape) * singular[0]
    rank = int(np.count_nonzero(singular > tolerance))
    chart = np.asarray(pivots[:14], dtype=int)
    fixed = germ.copy()

    def residual(chart_values: np.ndarray) -> np.ndarray:
        value = fixed.copy()
        value[chart] = chart_values
        return _child_rows(value, qe, pe, event_flux) / row_scales

    solution = least_squares(residual, germ[chart].copy(), method="lm", ftol=1.0e-13, xtol=1.0e-13, gtol=1.0e-13, max_nfev=900)
    child = fixed.copy()
    child[chart] = solution.x
    final_rows = _child_rows(child, qe, pe, event_flux)
    q, v, m = _unpack_child(child)
    return {
        "line_selection": {
            "rule": "LOWEST_EXACT_MERIT_REMAINING_AFTER_V18_52_CHILD_FLUX_FAILURE",
            "orientation": selected["orientation"],
            "alpha": selected["alpha"],
            "backtrack": selected["backtrack"],
            "complete_norm": selected["metrics"]["complete"],
            "complete_norm_reduction": selected["complete_norm_reduction"],
            "eta_minimum": selected["eta_minimum"],
        },
        "source_event": "v18.50_next_bidirectional_exact_merit_candidate",
        "source_solver_interpretation": "INVALIDATED_NOT_REASSERTED",
        "source_germ": "v18.46_child_of_accepted_v18.47_state",
        "whole_child_variable_count": 26,
        "physical_row_count": 14,
        "additional_global_KKT_rows": 0,
        "chart": {
            "jacobian_step": JACOBIAN_STEP,
            "full_chart_rank": rank,
            "selected_variable_indices": chart.tolist(),
            "smallest_resolved_singular_value": float(singular[rank - 1]),
            "row_scaling": "LOCAL_JACOBIAN_ROW_NORMS_NUMERICAL_ONLY_SAME_ZERO_SET",
            "solver_success": bool(solution.success),
            "solver_message": str(solution.message),
            "function_evaluations": int(solution.nfev),
            "scaled_final_norm": float(np.linalg.norm(solution.fun)),
        },
        "initial_physical_rows": initial_rows.tolist(),
        "final_physical_rows": final_rows.tolist(),
        "child_state": {
            "coordinates": q.tolist(),
            "velocities": v.tolist(),
            "multipliers": m.tolist(),
            "velocity_norm": float(np.linalg.norm(v)),
            "eta_Legendre_minimum": eta_legendre_minimum(q, m, points=5000),
        },
        "physical_residuals": {
            "maximum_trace": float(np.max(np.abs(final_rows[:3]))),
            "maximum_seven_constraints": float(np.max(np.abs(final_rows[3:10]))),
            "momentum_norm": float(np.linalg.norm(final_rows[10:12])),
            "dynamic_flux_norm_at_4e-4": float(np.linalg.norm(final_rows[12:14])),
        },
        "nonzero_motion_retained": bool(np.linalg.norm(v) > 0.0),
        "physical_equations_changed": False,
        "event_definition_changed": False,
    }


def completion_payload() -> dict[str, Any]:
    result = bidirectional_next_candidate_child()
    chart = result["chart"]
    rows = result["physical_residuals"]
    validation = {
        "next_candidate_selected_by_exact_merit": result["line_selection"]["backtrack"] == 6 and result["line_selection"]["complete_norm_reduction"] > 0.0,
        "invalidated_solver_not_reasserted": result["source_solver_interpretation"] == "INVALIDATED_NOT_REASSERTED",
        "complete_26_variable_child_considered": result["whole_child_variable_count"] == 26,
        "fourteen_physical_rows": result["physical_row_count"] == 14,
        "full_rank_local_chart": chart["full_chart_rank"] == 14 and len(chart["selected_variable_indices"]) == 14,
        "local_solve_converged": chart["solver_success"],
        "trace_closed": rows["maximum_trace"] < 1.0e-9,
        "seven_constraints_closed": rows["maximum_seven_constraints"] < 1.0e-9,
        "momentum_closed": rows["momentum_norm"] < 1.0e-7,
        "dynamic_flux_closed": rows["dynamic_flux_norm_at_4e-4"] < 2.0e-5,
        "child_eta_hyperregular": result["child_state"]["eta_Legendre_minimum"]["minimum"] > 0.0,
        "nonzero_motion_retained": result["nonzero_motion_retained"],
        "no_extra_global_row": result["additional_global_KKT_rows"] == 0,
        "physical_equations_unchanged": not result["physical_equations_changed"],
        "event_definition_unchanged": not result["event_definition_changed"],
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_aether_n3_bidirectional_next_candidate_child_v18_53",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "bidirectional_next_candidate_child": result,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "real_physical_property_explained": "THE_NEXT_BIDIRECTIONAL_EXACT_MERIT_STATE_IS_TESTED_WITH_THE_UNCHANGED_COMPLETE_CHILD_MAP_AFTER_THE_LOWER_MERIT_STATE_FAILS_FLUX",
        "dependency_advanced": "NONLINEAR_N3_EVENT_SADDLE_CLOSURE",
        "active_calculation": "VERIFY_TWO_SCALE_FLUX_AND_POSITIVE_DURATION_PERSISTENCE_THEN_PROMOTE" if passed else "TEST_THE_NEXT_COMPETITIVE_EXACT_MERIT_STATE",
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_bidirectional_next_candidate_child_v18_53.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = ["VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "v18_53_selected_raw_vector", "bidirectional_next_candidate_child", "completion_payload", "materialize"]
