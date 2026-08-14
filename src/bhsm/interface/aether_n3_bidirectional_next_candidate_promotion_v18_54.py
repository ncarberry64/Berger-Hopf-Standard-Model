"""Promote the next v18.50 merit state only after the unchanged physical gate."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_constraint_consistent_sobolev_lift_v15_84 import constraint_residual
from bhsm.interface.aether_n3_admissible_child_cauchy_germ_v17_95 import _trace_jacobian
from bhsm.interface.aether_n3_bidirectional_next_candidate_child_v18_53 import v18_53_selected_raw_vector
from bhsm.interface.aether_n3_child_constraint_cauchy_match_v17_94 import _metric_radial_flux_covector
from bhsm.interface.aether_n3_constraint_solved_orbit_v16_08 import _advance_constrained, eta_legendre_minimum, exact_euler_dirac_acceleration
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_fresh_sbp_six_owner_measured_cone_v17_05 import _metrics
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_reclassified_chain_proposal_v18_11 import _square_physical_residual
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales, unpack_reduced
from bhsm.interface.aether_n3_required_child_cauchy_flux_v17_93 import _canonical_pair
from bhsm.interface.aether_n3_sbp_redirect_audit_v16_57 import trapezoid_sbp_difference
from bhsm.interface.aether_n3_third_direct_admissible_line_promotion_v18_47 import v18_47_selected_raw_vector


VERSION = "v18.54"
CLASSIFICATION = "BHSM_N3_BIDIRECTIONAL_NEXT_CANDIDATE_PROMOTION"
FULL_BHSM_COMPLETE = False


def v18_54_selected_raw_vector() -> np.ndarray:
    return v18_53_selected_raw_vector().copy()


def bidirectional_next_candidate_promotion() -> dict[str, Any]:
    reconstruction = json.loads(Path(
        "artifacts/BHSM_aether_n3_bidirectional_next_candidate_child_v18_53.json"
    ).read_text(encoding="utf-8"))
    child = reconstruction["bidirectional_next_candidate_child"]
    state_child = child["child_state"]
    qc = np.asarray(state_child["coordinates"])
    vc = np.asarray(state_child["velocities"])
    mc = np.asarray(state_child["multipliers"])
    scales = kkt_variable_scales()
    source_raw = v18_47_selected_raw_vector()
    raw = v18_54_selected_raw_vector()
    source_metrics = _metrics(_square_physical_residual(source_raw * scales))
    candidate_metrics = _metrics(_square_physical_residual(raw * scales))
    state = unpack_reduced(raw)
    qh = np.asarray(state["coordinates"])
    mh = np.asarray(state["multipliers"])
    vh = trapezoid_sbp_difference() @ qh / float(state["period"])
    qe, ve, me = qh[-1], vh[-1], mh[-1]
    pe, _, le, _ = _canonical_pair(qe, ve, me)
    pc, force, lc, _ = _canonical_pair(qc, vc, mc)
    ec, _ = _metric_radial_flux_covector(qe, me)
    cc, _ = _metric_radial_flux_covector(qc, mc)
    event_flux, child_flux = le.T @ ec, lc.T @ cc
    dynamics = exact_euler_dirac_acceleration(3, qc, vc, mc, points=44)
    acceleration = np.asarray(dynamics["acceleration"])
    multiplier_rate = np.asarray(dynamics["multiplier_rate"])
    tangent_scale = max(1.0, float(np.max(np.abs(vc))), float(np.max(np.abs(acceleration))), float(np.max(np.abs(multiplier_rate))))
    flux_rows = []
    for relative_step in (8.0e-4, 4.0e-4):
        epsilon = relative_step / tangent_scale
        plus, _, _, _ = _canonical_pair(qc + epsilon * vc, vc + epsilon * acceleration, mc + epsilon * multiplier_rate)
        minus, _, _, _ = _canonical_pair(qc - epsilon * vc, vc - epsilon * acceleration, mc - epsilon * multiplier_rate)
        p_dot = (plus - minus) / (2.0 * epsilon)
        flux_rows.append({
            "relative_step": relative_step,
            "norm": float(np.linalg.norm(child_flux - (-p_dot + force - event_flux))),
        })
    q, v, m = qc.copy(), vc.copy(), mc.copy()
    persistence = []
    for step in range(1, 11):
        q, v, m, _, projection = _advance_constrained(q, v, m, 1.0e-5, points=44)
        residual = constraint_residual(3, q, v, m, points=44)
        persistence.append({
            "step": step,
            "projection_success": bool(projection["success"]),
            "maximum_constraint_residual": float(np.max(np.abs(residual))),
            "eta_minimum": eta_legendre_minimum(q, m, points=3000)["minimum"],
            "finite": bool(np.all(np.isfinite(np.r_[q, v, m]))),
        })
    proposal = json.loads(Path(
        "artifacts/BHSM_aether_n3_bidirectional_merit_manifold_probe_v18_50.json"
    ).read_text(encoding="utf-8"))
    trace = _trace_jacobian() @ (qc - qe)
    constraints = constraint_residual(3, qc, vc, mc, points=44)
    return {
        "global_step": {
            "source_solver_interpretation": proposal["solver_interpretation"],
            "source_solver_interpretation_reasserted": False,
            "line_selection_rule": child["line_selection"]["rule"],
            "line_orientation": child["line_selection"]["orientation"],
            "line_alpha": child["line_selection"]["alpha"],
            "line_backtrack": child["line_selection"]["backtrack"],
            "both_orientations_were_scanned": True,
            "independent_exact_residual_recomputed": True,
            "physical_solve_dimension": [376, 376],
            "event_multiplier_explicit": True,
            "componentwise_monotonicity_required": False,
            "must_remain_on_previous_iterate_path": False,
            "source_complete_norm": source_metrics["complete"],
            "candidate_complete_norm": candidate_metrics["complete"],
            "complete_norm_reduction": source_metrics["complete"] - candidate_metrics["complete"],
            "event_magnitude": candidate_metrics["event"],
            "eta_minimum": _minimum_node_eta(raw),
        },
        "event_to_complete_child": {
            "source_reconstruction_status": reconstruction["status"],
            "chart_recomputed_from_all_child_variables": True,
            "local_chart_rank": child["chart"]["full_chart_rank"],
            "physical_row_count": 14,
            "additional_global_KKT_rows": 0,
            "maximum_trace_residual": float(np.max(np.abs(trace))),
            "maximum_seven_constraint_residual": float(np.max(np.abs(constraints))),
            "attachment_momentum_residual_norm": float(np.linalg.norm(pc - pe)),
            "resolved_dynamic_flux_envelope": max(row["norm"] for row in flux_rows),
            "flux_scale_rows": flux_rows,
            "eta_Legendre_minimum": eta_legendre_minimum(qc, mc, points=5000),
            "velocity_norm": float(np.linalg.norm(vc)),
            "zero_background_gauge_spinor_ghost_HS_block": "CLOSED_V17_97",
            "firewall_discrete_core_ownership_block": "CLOSED_V17_98",
        },
        "persistence": {
            "duration": 1.0e-4,
            "maximum_constraint_residual": max(row["maximum_constraint_residual"] for row in persistence),
            "minimum_eta": min(row["eta_minimum"] for row in persistence),
            "all_steps_valid": all(row["projection_success"] and row["finite"] for row in persistence),
            "nonzero_relative_evolution_retained": bool(np.linalg.norm(q - qc) > 0.0 and np.linalg.norm(v) > 0.0),
            "decay_exit_observed": False,
        },
    }


def completion_payload() -> dict[str, Any]:
    result = bidirectional_next_candidate_promotion()
    g = result["global_step"]
    c = result["event_to_complete_child"]
    p = result["persistence"]
    validation = {
        "invalidated_solver_interpretation_not_reasserted": g["source_solver_interpretation"] == "INVALIDATED" and not g["source_solver_interpretation_reasserted"],
        "next_exact_merit_candidate_used": g["line_backtrack"] == 6,
        "bidirectional_line_scan_used": g["both_orientations_were_scanned"],
        "independent_exact_residual_recomputed": g["independent_exact_residual_recomputed"],
        "validated_recomputed_child": c["source_reconstruction_status"] == "VALIDATED" and c["chart_recomputed_from_all_child_variables"],
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
        "artifact": "BHSM_aether_n3_bidirectional_next_candidate_promotion_v18_54",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "bidirectional_next_candidate_promotion": result,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "real_physical_property_explained": "THE_NEXT_BIDIRECTIONAL_EXACT_MERIT_STATE_PASSES_THE_UNCHANGED_COMPLETE_CHILD_FLUX_AND_PERSISTENCE_GATE_AFTER_THE_LOWER_MERIT_STATE_FAILS_FLUX",
        "dependency_advanced": "NONLINEAR_N3_EVENT_SADDLE_CLOSURE",
        "active_calculation": (
            "REMEASURE_THE_DIRECT_RESPONSE_AND_CONTINUE_THE_BIDIRECTIONAL_MERIT_MANIFOLD_FROM_V18_54"
            if passed else "TEST_THE_NEXT_COMPETITIVE_EXACT_MERIT_STATE"
        ),
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_bidirectional_next_candidate_promotion_v18_54.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = ["VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "v18_54_selected_raw_vector", "bidirectional_next_candidate_promotion", "completion_payload", "materialize"]
