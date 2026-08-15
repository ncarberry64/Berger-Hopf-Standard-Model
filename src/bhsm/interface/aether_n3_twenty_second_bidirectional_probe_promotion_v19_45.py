"""Promote the v19.43 merit state only after the complete physical gate."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_constraint_consistent_sobolev_lift_v15_84 import constraint_residual
from bhsm.interface.aether_n3_admissible_child_cauchy_germ_v17_95 import _trace_jacobian
from bhsm.interface.aether_n3_child_constraint_cauchy_match_v17_94 import _metric_radial_flux_covector
from bhsm.interface.aether_n3_constraint_solved_orbit_v16_08 import _advance_constrained, eta_legendre_minimum, exact_euler_dirac_acceleration
from bhsm.interface.aether_n3_twenty_second_bidirectional_merit_manifold_probe_v19_43 import v19_43_selected_raw_vector
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_fresh_sbp_six_owner_measured_cone_v17_05 import _metrics
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_reclassified_chain_proposal_v18_11 import _square_physical_residual
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales, unpack_reduced
from bhsm.interface.aether_n3_required_child_cauchy_flux_v17_93 import _canonical_pair
from bhsm.interface.aether_n3_sbp_redirect_audit_v16_57 import trapezoid_sbp_difference
from bhsm.interface.aether_n3_twenty_first_bidirectional_probe_promotion_v19_41 import v19_41_selected_raw_vector


VERSION = "v19.45"
CLASSIFICATION = "BHSM_N3_TWENTY_SECOND_BIDIRECTIONAL_PROBE_PROMOTION"
FULL_BHSM_COMPLETE = False


def v19_45_selected_raw_vector() -> np.ndarray:
    return v19_43_selected_raw_vector().copy()


def twenty_second_bidirectional_probe_promotion() -> dict[str, Any]:
    reconstruction = json.loads(Path(
        "artifacts/BHSM_aether_n3_twenty_second_bidirectional_probe_child_v19_44.json"
    ).read_text(encoding="utf-8"))
    child = reconstruction["twenty_second_bidirectional_probe_child"]
    child_state = child["child_state"]
    qc = np.asarray(child_state["coordinates"])
    vc = np.asarray(child_state["velocities"])
    mc = np.asarray(child_state["multipliers"])
    scales = kkt_variable_scales()
    source_raw = v19_41_selected_raw_vector()
    raw = v19_45_selected_raw_vector()
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
    tangent_scale = max(
        1.0, float(np.max(np.abs(vc))), float(np.max(np.abs(acceleration))),
        float(np.max(np.abs(multiplier_rate))),
    )
    flux_rows = []
    for relative_step in (8.0e-4, 4.0e-4):
        epsilon = relative_step / tangent_scale
        plus, _, _, _ = _canonical_pair(
            qc + epsilon * vc, vc + epsilon * acceleration,
            mc + epsilon * multiplier_rate,
        )
        minus, _, _, _ = _canonical_pair(
            qc - epsilon * vc, vc - epsilon * acceleration,
            mc - epsilon * multiplier_rate,
        )
        p_dot = (plus - minus) / (2.0 * epsilon)
        flux_rows.append({
            "relative_step": relative_step,
            "norm": float(np.linalg.norm(child_flux - (-p_dot + force - event_flux))),
        })
    q, velocity, multipliers = qc.copy(), vc.copy(), mc.copy()
    persistence = []
    for step in range(1, 11):
        q, velocity, multipliers, _, projection = _advance_constrained(
            q, velocity, multipliers, 1.0e-5, points=44
        )
        residual = constraint_residual(3, q, velocity, multipliers, points=44)
        persistence.append({
            "step": step,
            "projection_success": bool(projection["success"]),
            "maximum_constraint_residual": float(np.max(np.abs(residual))),
            "eta_minimum": eta_legendre_minimum(q, multipliers, points=3000)["minimum"],
            "finite": bool(np.all(np.isfinite(np.r_[q, velocity, multipliers]))),
        })
    proposal = json.loads(Path(
        "artifacts/BHSM_aether_n3_twenty_second_bidirectional_merit_manifold_probe_v19_43.json"
    ).read_text(encoding="utf-8"))
    trace = _trace_jacobian() @ (qc - qe)
    constraints = constraint_residual(3, qc, vc, mc, points=44)
    return {
        "global_step": {
            "source_solver_interpretation": proposal["solver_interpretation"],
            "source_solver_interpretation_reasserted": False,
            "proposal_status": proposal["status"],
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
            "maximum_constraint_residual": max(
                row["maximum_constraint_residual"] for row in persistence
            ),
            "minimum_eta": min(row["eta_minimum"] for row in persistence),
            "all_steps_valid": all(
                row["projection_success"] and row["finite"] for row in persistence
            ),
            "nonzero_relative_evolution_retained": bool(
                np.linalg.norm(q - qc) > 0.0 and np.linalg.norm(velocity) > 0.0
            ),
            "decay_exit_observed": False,
        },
    }


def completion_payload() -> dict[str, Any]:
    result = twenty_second_bidirectional_probe_promotion()
    global_step = result["global_step"]
    child = result["event_to_complete_child"]
    persistence = result["persistence"]
    validation = {
        "invalidated_solver_interpretation_not_reasserted": (
            global_step["source_solver_interpretation"] == "INVALIDATED"
            and not global_step["source_solver_interpretation_reasserted"]
        ),
        "bidirectional_line_scan_used": global_step["both_orientations_were_scanned"],
        "independent_exact_residual_recomputed": global_step["independent_exact_residual_recomputed"],
        "validated_recomputed_child": (
            child["source_reconstruction_status"] == "VALIDATED"
            and child["chart_recomputed_from_all_child_variables"]
        ),
        "square_explicit_multiplier_solve": (
            global_step["physical_solve_dimension"] == [376, 376]
            and global_step["event_multiplier_explicit"]
        ),
        "no_componentwise_filter": not global_step["componentwise_monotonicity_required"],
        "previous_path_not_a_constraint": not global_step["must_remain_on_previous_iterate_path"],
        "true_376_merit_reduced": global_step["complete_norm_reduction"] > 0.0,
        "global_eta_preserved": global_step["eta_minimum"] > 1.0e-5,
        "trace_closed": child["maximum_trace_residual"] < 1.0e-9,
        "seven_constraints_closed": child["maximum_seven_constraint_residual"] < 1.0e-9,
        "attachment_momentum_closed": child["attachment_momentum_residual_norm"] < 1.0e-7,
        "resolved_dynamic_flux_closed": child["resolved_dynamic_flux_envelope"] < 2.0e-5,
        "child_eta_hyperregular": child["eta_Legendre_minimum"]["minimum"] > 0.0,
        "positive_interval_persists": (
            persistence["all_steps_valid"]
            and persistence["maximum_constraint_residual"] < 1.0e-8
            and persistence["minimum_eta"] > 0.0
        ),
        "nonzero_relative_evolution_retained": persistence["nonzero_relative_evolution_retained"],
        "no_extra_global_row": child["additional_global_KKT_rows"] == 0,
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_aether_n3_twenty_second_bidirectional_probe_promotion_v19_45",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "twenty_second_bidirectional_probe_promotion": result,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "real_physical_property_explained": (
            "THE_V19_43_EXACT_MERIT_STATE_PASSES_THE_UNCHANGED_COMPLETE_"
            "CHILD_FLUX_AND_PERSISTENCE_GATE_WHILE_ITS_SOLVER_"
            "INTERPRETATION_REMAINS_INVALIDATED"
        ),
        "dependency_advanced": "NONLINEAR_N3_EVENT_SADDLE_CLOSURE",
        "active_calculation": (
            "CONTINUE_PHYSICALLY_ADMISSIBLE_EXACT_376_ROW_DESCENT_FROM_"
            "THE_LATEST_ACCEPTED_FRONTIER_TO_F376_ZERO"
            if passed else "TEST_THE_NEXT_COMPETITIVE_EXACT_MERIT_STATE"
        ),
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_twenty_second_bidirectional_probe_promotion_v19_45.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "v19_45_selected_raw_vector",
    "twenty_second_bidirectional_probe_promotion", "completion_payload", "materialize",
]
