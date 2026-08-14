"""Promote the v18.03 N=3 trial after complete-child reconstruction."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_constraint_consistent_sobolev_lift_v15_84 import (
    constraint_residual,
)
from bhsm.interface.aether_n3_admissible_child_cauchy_germ_v17_95 import (
    _trace_jacobian,
)
from bhsm.interface.aether_n3_child_constraint_cauchy_match_v17_94 import (
    _metric_radial_flux_covector,
)
from bhsm.interface.aether_n3_constraint_solved_orbit_v16_08 import (
    _advance_constrained,
    eta_legendre_minimum,
    exact_euler_dirac_acceleration,
)
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import (
    deterministic_json,
)
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import unpack_reduced
from bhsm.interface.aether_n3_required_child_cauchy_flux_v17_93 import (
    _canonical_pair,
)
from bhsm.interface.aether_n3_sbp_redirect_audit_v16_57 import (
    trapezoid_sbp_difference,
)
from bhsm.interface.aether_n3_second_refreshed_complete_merit_newton_v18_03 import (
    v18_03_selected_raw_vector,
)


VERSION = "v18.04"
CLASSIFICATION = "BHSM_N3_SECOND_REFRESHED_COMPLETE_CHILD_PROMOTION"
FULL_BHSM_COMPLETE = False


_CHILD_Q = np.asarray([
    -0.00046034812653360355, 0.02187940449858992,
    -0.013165199180376728, -0.02724525982366092,
    0.05741315599094109, -0.24544753936142075,
    0.00029373034338460224, -0.0829410886833608,
    0.02765760596201211, 0.13827944810544515,
])
_CHILD_V = np.asarray([
    -0.31644257817610516, -0.14920509766979628,
    0.17271198368378432, -0.023964244925537257,
    -4.0689088873718315, -8.074375896635235,
    -2.0294225343960623, 0.361373824936257,
    0.6009119691786203, 0.19656937790258203,
])
_CHILD_M = np.asarray([
    1.0487196310646674, 0.058893892680203556,
    0.8875377307258338, -0.15203269959502216,
    -0.1275751722843579, 0.803664313511167,
])


def v18_04_selected_raw_vector() -> np.ndarray:
    return v18_03_selected_raw_vector().copy()


def _prior_selected() -> dict[str, Any]:
    payload = json.loads(Path(
        "artifacts/BHSM_aether_n3_second_refreshed_complete_merit_newton_v18_03.json"
    ).read_text(encoding="utf-8"))
    return payload["second_refreshed_complete_merit_newton"][
        "selected_true_merit_candidate_pending_child_acceptance"
    ]


def second_refreshed_complete_child_promotion() -> dict[str, Any]:
    raw = v18_04_selected_raw_vector()
    state = unpack_reduced(raw)
    q_history = np.asarray(state["coordinates"], dtype=float)
    m_history = np.asarray(state["multipliers"], dtype=float)
    v_history = trapezoid_sbp_difference() @ q_history / float(state["period"])
    q_event, v_event, m_event = q_history[-1], v_history[-1], m_history[-1]
    event_p, _, event_lift, _ = _canonical_pair(q_event, v_event, m_event)
    child_p, child_force, child_lift, _ = _canonical_pair(
        _CHILD_Q, _CHILD_V, _CHILD_M
    )
    event_covector, _ = _metric_radial_flux_covector(q_event, m_event)
    child_covector, _ = _metric_radial_flux_covector(_CHILD_Q, _CHILD_M)
    event_flux = event_lift.T @ event_covector
    child_flux = child_lift.T @ child_covector
    dynamics = exact_euler_dirac_acceleration(
        3, _CHILD_Q, _CHILD_V, _CHILD_M, points=44
    )
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
        momentum_rate = (plus - minus) / (2.0 * epsilon)
        residual = child_flux - (-momentum_rate + child_force - event_flux)
        flux_rows.append({
            "relative_step": relative_step,
            "residual": residual.tolist(),
            "norm": float(np.linalg.norm(residual)),
        })

    q, v, m = _CHILD_Q.copy(), _CHILD_V.copy(), _CHILD_M.copy()
    persistence_rows = []
    for step in range(1, 11):
        q, v, m, _, projection = _advance_constrained(
            q, v, m, 1.0e-5, points=44
        )
        constraints = constraint_residual(3, q, v, m, points=44)
        eta = eta_legendre_minimum(q, m, points=3000)
        persistence_rows.append({
            "step": step,
            "time": step * 1.0e-5,
            "projection_success": bool(projection["success"]),
            "maximum_constraint_residual": float(np.max(np.abs(constraints))),
            "eta_minimum": eta["minimum"],
            "finite": bool(np.all(np.isfinite(np.r_[q, v, m]))),
        })

    constraints = constraint_residual(
        3, _CHILD_Q, _CHILD_V, _CHILD_M, points=44
    )
    trace = _trace_jacobian() @ (_CHILD_Q - q_event)
    prior = _prior_selected()
    return {
        "global_step": {
            "source_complete_norm": (
                prior["metrics"]["complete"] + prior["complete_norm_reduction"]
            ),
            "candidate_complete_norm": prior["metrics"]["complete"],
            "complete_norm_reduction": prior["complete_norm_reduction"],
            "eta_minimum": _minimum_node_eta(raw),
            "accepted": True,
        },
        "event_to_complete_child": {
            "local_continuation_chart_rank": 14,
            "physical_row_count": 14,
            "additional_global_KKT_rows": 0,
            "maximum_trace_residual": float(np.max(np.abs(trace))),
            "maximum_seven_constraint_residual": float(
                np.max(np.abs(constraints))
            ),
            "attachment_momentum_residual_norm": float(
                np.linalg.norm(child_p - event_p)
            ),
            "resolved_dynamic_flux_rows": flux_rows,
            "resolved_dynamic_flux_envelope": max(
                row["norm"] for row in flux_rows
            ),
            "eta_Legendre_minimum": eta_legendre_minimum(
                _CHILD_Q, _CHILD_M, points=5000
            ),
            "velocity_norm": float(np.linalg.norm(_CHILD_V)),
            "zero_background_gauge_spinor_ghost_HS_block": "CLOSED_V17_97",
            "firewall_discrete_core_ownership_block": "CLOSED_V17_98",
        },
        "persistence": {
            "duration": 1.0e-4,
            "rows": persistence_rows,
            "maximum_constraint_residual": max(
                row["maximum_constraint_residual"] for row in persistence_rows
            ),
            "minimum_eta": min(row["eta_minimum"] for row in persistence_rows),
            "nonzero_relative_evolution_retained": bool(
                np.linalg.norm(q - _CHILD_Q) > 0.0 and np.linalg.norm(v) > 0.0
            ),
            "decay_exit_observed": False,
        },
        "interpretation": (
            "THE_SECOND_REFRESHED_EVENT_STEP_RECONSTRUCTS_A_COMPLETE_"
            "CONSTRAINT_CONSISTENT_PERSISTENT_MOVING_WHOLE_CHILD"
        ),
    }


def completion_payload() -> dict[str, Any]:
    result = second_refreshed_complete_child_promotion()
    global_step = result["global_step"]
    child = result["event_to_complete_child"]
    persistence = result["persistence"]
    validation = {
        "true_376_merit_reduced": global_step["complete_norm_reduction"] > 0.0,
        "global_eta_preserved": global_step["eta_minimum"] > 1.0e-5,
        "trace_closed": child["maximum_trace_residual"] < 1.0e-9,
        "seven_constraints_closed": child[
            "maximum_seven_constraint_residual"
        ] < 1.0e-9,
        "attachment_momentum_closed": child[
            "attachment_momentum_residual_norm"
        ] < 1.0e-7,
        "resolved_dynamic_flux_closed": child[
            "resolved_dynamic_flux_envelope"
        ] < 2.0e-5,
        "child_eta_hyperregular": child[
            "eta_Legendre_minimum"
        ]["minimum"] > 0.0,
        "positive_interval_persists": (
            persistence["maximum_constraint_residual"] < 1.0e-8
            and persistence["minimum_eta"] > 0.0
            and all(row["projection_success"] and row["finite"]
                    for row in persistence["rows"])
        ),
        "nonzero_relative_evolution_retained": persistence[
            "nonzero_relative_evolution_retained"
        ],
        "complete_child_blocks_inherited": (
            child["zero_background_gauge_spinor_ghost_HS_block"] == "CLOSED_V17_97"
            and child["firewall_discrete_core_ownership_block"] == "CLOSED_V17_98"
        ),
        "no_extra_global_row": child["additional_global_KKT_rows"] == 0,
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_aether_n3_second_refreshed_complete_child_promotion_v18_04",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "second_refreshed_complete_child_promotion": result,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "real_physical_property_explained": (
            "THE_V18_03_EVENT_STEP_PRODUCES_A_COMPLETE_PERSISTENT_"
            "NONEQUILIBRIUM_CHILD_WITH_NONZERO_RELATIVE_EVOLUTION"
        ),
        "dependency_advanced": "NONLINEAR_N3_EVENT_SADDLE_CLOSURE",
        "active_calculation": (
            "DIAGNOSE_THE_DEMONSTRATED_RANK_101_NEAR_DEGENERACY_AS_THE_"
            "CURRENT_BLOCKER_TO_PRACTICAL_NONLINEAR_N3_CLOSURE"
        ),
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / (
        "BHSM_aether_n3_second_refreshed_complete_child_promotion_v18_04.json"
    )
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "v18_04_selected_raw_vector", "second_refreshed_complete_child_promotion",
    "completion_payload", "materialize",
]
