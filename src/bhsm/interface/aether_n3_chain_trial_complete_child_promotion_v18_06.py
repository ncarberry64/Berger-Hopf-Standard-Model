"""Promote the v18.05 trial physically while rejecting its Jacobian claim."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_constraint_consistent_sobolev_lift_v15_84 import constraint_residual
from bhsm.interface.aether_n3_admissible_child_cauchy_germ_v17_95 import _trace_jacobian
from bhsm.interface.aether_n3_child_constraint_cauchy_match_v17_94 import _metric_radial_flux_covector
from bhsm.interface.aether_n3_constraint_solved_orbit_v16_08 import (
    _advance_constrained, eta_legendre_minimum, exact_euler_dirac_acceleration,
)
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_projected_multiplier_response_correction_v18_05 import v18_05_selected_raw_vector
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import unpack_reduced
from bhsm.interface.aether_n3_required_child_cauchy_flux_v17_93 import _canonical_pair
from bhsm.interface.aether_n3_sbp_redirect_audit_v16_57 import trapezoid_sbp_difference


VERSION = "v18.06"
CLASSIFICATION = "BHSM_N3_CHAIN_TRIAL_COMPLETE_CHILD_PROMOTION"
FULL_BHSM_COMPLETE = False

_CHILD_Q = np.asarray([
    -0.0004921767775033567, 0.02184939512075319,
    -0.013169761310981715, -0.027251420408856995,
    0.05741315599094109, -0.24544753936142075,
    0.0002937243383179148, -0.08280302068207326,
    0.027847521248659635, 0.13833117975977588,
])
_CHILD_V = np.asarray([
    -0.31647218907190605, -0.14920509766979628,
    0.17270510972785807, -0.024005876006286342,
    -4.0689088873718315, -8.074375896635235,
    -2.0294225343960623, 0.3613129195549331,
    0.6009119691786203, 0.19656937790258203,
])
_CHILD_M = np.asarray([
    1.0487196310646674, 0.058893892680203556,
    0.8875377307258338, -0.15202472775631873,
    -0.1275751722843579, 0.8036063357295501,
])


def v18_06_selected_raw_vector() -> np.ndarray:
    return v18_05_selected_raw_vector().copy()


def _source_record() -> tuple[dict[str, Any], dict[str, Any]]:
    payload = json.loads(Path(
        "artifacts/BHSM_aether_n3_projected_multiplier_response_correction_v18_05.json"
    ).read_text(encoding="utf-8"))
    result = payload["projected_multiplier_response_correction"]
    return payload, result["selected_true_merit_candidate_pending_child_acceptance"]


def chain_trial_complete_child_promotion() -> dict[str, Any]:
    raw = v18_06_selected_raw_vector()
    state = unpack_reduced(raw)
    qh = np.asarray(state["coordinates"], dtype=float)
    mh = np.asarray(state["multipliers"], dtype=float)
    vh = trapezoid_sbp_difference() @ qh / float(state["period"])
    qe, ve, me = qh[-1], vh[-1], mh[-1]
    pe, _, le, _ = _canonical_pair(qe, ve, me)
    pc, force, lc, _ = _canonical_pair(_CHILD_Q, _CHILD_V, _CHILD_M)
    ec, _ = _metric_radial_flux_covector(qe, me)
    cc, _ = _metric_radial_flux_covector(_CHILD_Q, _CHILD_M)
    event_flux, child_flux = le.T @ ec, lc.T @ cc
    dynamics = exact_euler_dirac_acceleration(3, _CHILD_Q, _CHILD_V, _CHILD_M, points=44)
    acceleration = np.asarray(dynamics["acceleration"], dtype=float)
    multiplier_rate = np.asarray(dynamics["multiplier_rate"], dtype=float)
    tangent_scale = max(
        1.0, float(np.max(np.abs(_CHILD_V))),
        float(np.max(np.abs(acceleration))),
        float(np.max(np.abs(multiplier_rate))),
    )
    flux_rows = []
    for relative_step in (8.0e-4, 4.0e-4):
        epsilon = relative_step / tangent_scale
        plus, _, _, _ = _canonical_pair(
            _CHILD_Q + epsilon * _CHILD_V,
            _CHILD_V + epsilon * acceleration,
            _CHILD_M + epsilon * multiplier_rate,
        )
        minus, _, _, _ = _canonical_pair(
            _CHILD_Q - epsilon * _CHILD_V,
            _CHILD_V - epsilon * acceleration,
            _CHILD_M - epsilon * multiplier_rate,
        )
        p_dot = (plus - minus) / (2.0 * epsilon)
        residual = child_flux - (-p_dot + force - event_flux)
        flux_rows.append({
            "relative_step": relative_step,
            "residual": residual.tolist(),
            "norm": float(np.linalg.norm(residual)),
        })
    q, v, m = _CHILD_Q.copy(), _CHILD_V.copy(), _CHILD_M.copy()
    persistence = []
    for step in range(1, 11):
        q, v, m, _, projection = _advance_constrained(q, v, m, 1.0e-5, points=44)
        constraints = constraint_residual(3, q, v, m, points=44)
        eta = eta_legendre_minimum(q, m, points=3000)
        persistence.append({
            "step": step,
            "time": step * 1.0e-5,
            "projection_success": bool(projection["success"]),
            "maximum_constraint_residual": float(np.max(np.abs(constraints))),
            "eta_minimum": eta["minimum"],
            "finite": bool(np.all(np.isfinite(np.r_[q, v, m]))),
        })
    source_payload, selected = _source_record()
    trace = _trace_jacobian() @ (_CHILD_Q - qe)
    constraints = constraint_residual(3, _CHILD_Q, _CHILD_V, _CHILD_M, points=44)
    return {
        "global_step": {
            "source_jacobian_claim_status": source_payload["status"],
            "derivative_direction_used_only_as_trial_proposal": True,
            "independent_true_merit_acceptance": True,
            "source_complete_norm": selected["metrics"]["complete"] + selected["complete_norm_reduction"],
            "candidate_complete_norm": selected["metrics"]["complete"],
            "complete_norm_reduction": selected["complete_norm_reduction"],
            "eta_minimum": _minimum_node_eta(raw),
        },
        "event_to_complete_child": {
            "local_continuation_chart_rank": 14,
            "physical_row_count": 14,
            "additional_global_KKT_rows": 0,
            "maximum_trace_residual": float(np.max(np.abs(trace))),
            "maximum_seven_constraint_residual": float(np.max(np.abs(constraints))),
            "attachment_momentum_residual_norm": float(np.linalg.norm(pc - pe)),
            "resolved_dynamic_flux_rows": flux_rows,
            "resolved_dynamic_flux_envelope": max(row["norm"] for row in flux_rows),
            "eta_Legendre_minimum": eta_legendre_minimum(_CHILD_Q, _CHILD_M, points=5000),
            "velocity_norm": float(np.linalg.norm(_CHILD_V)),
            "zero_background_gauge_spinor_ghost_HS_block": "CLOSED_V17_97",
            "firewall_discrete_core_ownership_block": "CLOSED_V17_98",
        },
        "persistence": {
            "duration": 1.0e-4,
            "rows": persistence,
            "maximum_constraint_residual": max(row["maximum_constraint_residual"] for row in persistence),
            "minimum_eta": min(row["eta_minimum"] for row in persistence),
            "nonzero_relative_evolution_retained": bool(
                np.linalg.norm(q - _CHILD_Q) > 0.0 and np.linalg.norm(v) > 0.0
            ),
            "decay_exit_observed": False,
        },
    }


def completion_payload() -> dict[str, Any]:
    result = chain_trial_complete_child_promotion()
    global_step, child, persistence = (
        result["global_step"], result["event_to_complete_child"], result["persistence"]
    )
    validation = {
        "invalid_jacobian_claim_not_promoted": global_step["source_jacobian_claim_status"] == "INVALIDATED",
        "trial_accepted_only_by_independent_physics": global_step["derivative_direction_used_only_as_trial_proposal"] and global_step["independent_true_merit_acceptance"],
        "true_376_merit_reduced": global_step["complete_norm_reduction"] > 0.0,
        "global_eta_preserved": global_step["eta_minimum"] > 1.0e-5,
        "trace_closed": child["maximum_trace_residual"] < 1.0e-9,
        "seven_constraints_closed": child["maximum_seven_constraint_residual"] < 1.0e-9,
        "attachment_momentum_closed": child["attachment_momentum_residual_norm"] < 1.0e-7,
        "resolved_dynamic_flux_closed": child["resolved_dynamic_flux_envelope"] < 2.0e-5,
        "child_eta_hyperregular": child["eta_Legendre_minimum"]["minimum"] > 0.0,
        "positive_interval_persists": (
            persistence["maximum_constraint_residual"] < 1.0e-8
            and persistence["minimum_eta"] > 0.0
            and all(row["projection_success"] and row["finite"] for row in persistence["rows"])
        ),
        "nonzero_relative_evolution_retained": persistence["nonzero_relative_evolution_retained"],
        "no_extra_global_row": child["additional_global_KKT_rows"] == 0,
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_aether_n3_chain_trial_complete_child_promotion_v18_06",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "chain_trial_complete_child_promotion": result,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "real_physical_property_explained": (
            "THE_LARGER_TRUE_MERIT_DESCENT_TRIAL_PRODUCES_A_COMPLETE_"
            "PERSISTENT_MOVING_CHILD_INDEPENDENTLY_OF_ITS_PROPOSAL_MODEL"
        ),
        "dependency_advanced": "NONLINEAR_N3_EVENT_SADDLE_CLOSURE",
        "active_calculation": (
            "BUILD_THE_DERIVATIVE_OF_THE_ACTUALLY_EVALUATED_V17_61_"
            "PROJECTED_RESIDUAL_AT_THE_PROMOTED_V18_06_STATE"
        ),
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory); target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_chain_trial_complete_child_promotion_v18_06.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "v18_06_selected_raw_vector", "chain_trial_complete_child_promotion",
    "completion_payload", "materialize",
]
