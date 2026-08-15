"""Admissible event-to-child Cauchy germ and scalar flux solvability map."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_constraint_consistent_sobolev_lift_v15_84 import (
    constraint_residual,
)
from bhsm.interface.aether_n3_child_constraint_cauchy_match_v17_94 import (
    _metric_radial_flux_covector,
)
from bhsm.interface.aether_n3_constraint_solved_orbit_v16_08 import (
    eta_legendre_minimum,
    exact_euler_dirac_acceleration,
)
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import (
    deterministic_json,
)
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import (
    ORDER,
    unpack_reduced,
)
from bhsm.interface.aether_n3_required_child_cauchy_flux_v17_93 import (
    _canonical_pair,
)
from bhsm.interface.aether_n3_sbp_redirect_audit_v16_57 import (
    trapezoid_sbp_difference,
)
from bhsm.interface.aether_n3_scale_corrected_period_log_continuation_v17_76 import (
    v17_75_selected_raw_vector,
)


VERSION = "v17.95"
CLASSIFICATION = "BHSM_N3_ADMISSIBLE_COMPLETE_CHILD_CAUCHY_GERM"
FULL_BHSM_COMPLETE = False


# Deterministic v17.94 fixed-trace branch: minimum scaled displacement from
# the seven-constraint projection, with all twelve equality rows closed and
# eta hyperregularity enforced on the reconstruction path.
_CHILD_Q = np.asarray([
    0.0589599228401462, 0.07483823195009148,
    -0.00878492166777709, -0.01640354789963538,
    0.06724888111677679, -0.24562467601305474,
    -0.00971913304707981, -0.03983251424774494,
    0.02038950043391137, 0.08790277310437979,
])
_CHILD_V = np.asarray([
    -0.27802208163338116, -0.11169295481811201,
    0.20144982237825232, 0.0053871402192639225,
    -3.434866373880723, -8.625551897962744,
    -1.856228828303112, 0.2519191710389299,
    0.8542095906171905, 0.3497309877373612,
])
_CHILD_M = np.asarray([
    1.7353909545811126, 0.19454963573775455,
    1.179501484989852, -0.13835062879087084,
    -0.09199531227288563, 0.7498546947058955,
])


def _trace_jacobian() -> np.ndarray:
    signs_k = (-1.0) ** np.arange(1, ORDER + 1)
    signs_j = (-1.0) ** np.arange(ORDER)
    trace = np.zeros((3, _CHILD_Q.size))
    trace[:, 0] = 1.0
    trace[:, 1:1 + ORDER] = signs_k
    trace[0, 1 + ORDER:1 + 2 * ORDER] = signs_j
    trace[1, 1 + 2 * ORDER:1 + 3 * ORDER] = signs_j
    trace[2, 1 + 2 * ORDER:1 + 3 * ORDER] = -signs_j
    return trace


def admissible_child_cauchy_germ() -> dict[str, Any]:
    state = unpack_reduced(v17_75_selected_raw_vector())
    q_history = np.asarray(state["coordinates"], dtype=float)
    multiplier_history = np.asarray(state["multipliers"], dtype=float)
    velocity_history = (
        trapezoid_sbp_difference() @ q_history / float(state["period"])
    )
    q_event = q_history[-1]
    velocity_event = velocity_history[-1]
    multipliers_event = multiplier_history[-1]

    momentum_event, _, q_lift_event, _ = _canonical_pair(
        q_event, velocity_event, multipliers_event
    )
    momentum_child, force_child, q_lift_child, _ = _canonical_pair(
        _CHILD_Q, _CHILD_V, _CHILD_M
    )
    trace_residual = _trace_jacobian() @ (_CHILD_Q - q_event)
    constraints = constraint_residual(
        ORDER, _CHILD_Q, _CHILD_V, _CHILD_M, points=44
    )
    momentum_residual = momentum_child - momentum_event
    eta_margin = eta_legendre_minimum(_CHILD_Q, _CHILD_M, points=5000)

    dynamics = exact_euler_dirac_acceleration(
        ORDER, _CHILD_Q, _CHILD_V, _CHILD_M, points=44
    )
    acceleration = np.asarray(dynamics["acceleration"], dtype=float)
    multiplier_rate = np.asarray(dynamics["multiplier_rate"], dtype=float)
    tangent_scale = max(
        1.0,
        float(np.max(np.abs(_CHILD_V))),
        float(np.max(np.abs(acceleration))),
        float(np.max(np.abs(multiplier_rate))),
    )

    def momentum_rate(relative_step: float) -> np.ndarray:
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
        return (plus - minus) / (2.0 * epsilon)

    # The initially used 2e-6 relative step is algebraically valid but too
    # small to differentiate this map again in the coupled boundary solve.
    # The 8e-4/4e-4 pair is in the resolved central-difference plateau.
    rate_coarse = momentum_rate(8.0e-4)
    rate = momentum_rate(4.0e-4)
    rate_refinement = float(
        np.linalg.norm(rate - rate_coarse) / max(1.0, np.linalg.norm(rate))
    )

    event_covector, event_raw_flux = _metric_radial_flux_covector(
        q_event, multipliers_event
    )
    child_covector, child_raw_flux = _metric_radial_flux_covector(
        _CHILD_Q, _CHILD_M
    )
    event_flux = q_lift_event.T @ event_covector
    actual_child_flux = q_lift_child.T @ child_covector
    required_child_flux = -rate + force_child - event_flux
    flux_residual = actual_child_flux - required_child_flux

    return {
        "source_event": "v17.75_selected_fine_period_log_mix_state",
        "selection_rule": (
            "MINIMUM_SCALED_DISPLACEMENT_BRANCH_FROM_THE_FIXED_TRACE_SEVEN_"
            "CONSTRAINT_PROJECTION_SUBJECT_TO_THREE_Gamma0_ROWS_SEVEN_"
            "LOCAL_CONSTRAINTS_TWO_CANONICAL_MOMENTUM_ROWS_AND_POSITIVE_"
            "ETA_LEGENDRE_MARGIN"
        ),
        "child_Cauchy_germ": {
            "coordinates": _CHILD_Q.tolist(),
            "velocities": _CHILD_V.tolist(),
            "multipliers": _CHILD_M.tolist(),
            "trace_order": ["log_C", "log_A", "log_B"],
            "trace_residual": trace_residual.tolist(),
            "maximum_trace_residual": float(np.max(np.abs(trace_residual))),
            "constraint_order": [
                "lapse_1", "lapse_2", "lapse_3",
                "shift_0", "shift_1", "shift_2", "Hamiltonian_energy",
            ],
            "constraint_residual": constraints.tolist(),
            "maximum_constraint_residual": float(np.max(np.abs(constraints))),
            "event_attachment_momentum": momentum_event.tolist(),
            "child_attachment_momentum": momentum_child.tolist(),
            "momentum_residual": momentum_residual.tolist(),
            "momentum_residual_norm": float(np.linalg.norm(momentum_residual)),
            "eta_Legendre_minimum": eta_margin,
            "nonzero_velocity_norm": float(np.linalg.norm(_CHILD_V)),
        },
        "child_relative_evolution": {
            "acceleration": acceleration.tolist(),
            "multiplier_rate": multiplier_rate.tolist(),
            "Dirac_condition_number": float(
                dynamics["Dirac_condition_number"]
            ),
            "attachment_momentum_rate": rate.tolist(),
            "momentum_rate_relative_step": 4.0e-4 / tangent_scale,
            "momentum_rate_refinement_relative_difference": rate_refinement,
            "finite_nonzero_evolution_is_defect": False,
        },
        "F_child_scalar": {
            "row_order": [
                "trace_log_C", "trace_log_A", "trace_log_B",
                "six_lapse_shift_plus_energy_constraints",
                "momentum_q_W", "momentum_x_D",
                "dynamic_flux_q_W", "dynamic_flux_x_D",
            ],
            "event_projected_flux": event_flux.tolist(),
            "event_raw_metric_flux": event_raw_flux,
            "actual_child_projected_flux": actual_child_flux.tolist(),
            "actual_child_raw_metric_flux": child_raw_flux,
            "child_instantaneous_force": force_child.tolist(),
            "required_child_projected_flux": required_child_flux.tolist(),
            "dynamic_flux_residual": flux_residual.tolist(),
            "dynamic_flux_residual_norm": float(np.linalg.norm(flux_residual)),
            "scalar_map_evaluable": True,
            "scalar_map_closed_at_current_event": bool(
                np.linalg.norm(flux_residual) < 1.0e-7
            ),
            "v17_93_pre_event_tangent_target_promotable": False,
            "why_v17_93_is_reclassified": (
                "ITS_MOMENTUM_RATE_WAS_TAKEN_ALONG_A_TERMINAL_LOCAL_STATE_"
                "THAT_DID_NOT_SATISFY_THE_SEVEN_CHILD_CONSTRAINTS"
            ),
        },
        "complete_child_status": {
            "admissible_scalar_Cauchy_germ_reconstructed": True,
            "scalar_dynamic_flux_match_closed": bool(
                np.linalg.norm(flux_residual) < 1.0e-7
            ),
            "event_core_pregeometric_generator_block": "OPEN",
            "gauge_spinor_ghost_Calderon_projector": "OPEN",
            "persistent_interval_evolved": False,
            "complete_F_child_closed": False,
        },
    }


def completion_payload() -> dict[str, Any]:
    result = admissible_child_cauchy_germ()
    germ = result["child_Cauchy_germ"]
    evolution = result["child_relative_evolution"]
    scalar = result["F_child_scalar"]
    complete = result["complete_child_status"]
    validation = {
        "three_event_traces_matched": germ["maximum_trace_residual"] < 1.0e-10,
        "seven_constraints_closed": germ["maximum_constraint_residual"] < 5.0e-10,
        "two_momenta_matched": germ["momentum_residual_norm"] < 1.0e-9,
        "eta_hyperregular": germ["eta_Legendre_minimum"]["minimum"] > 0.0,
        "nonzero_motion_retained": germ["nonzero_velocity_norm"] > 1.0,
        "relative_evolution_finite": bool(np.all(np.isfinite(
            evolution["acceleration"] + evolution["multiplier_rate"]
        ))),
        "momentum_rate_refined": evolution[
            "momentum_rate_refinement_relative_difference"
        ] < 2.0e-8,
        "scalar_flux_map_evaluated": scalar["scalar_map_evaluable"],
        "open_flux_not_promoted": (
            not scalar["scalar_map_closed_at_current_event"]
            and scalar["dynamic_flux_residual_norm"] > 1.0
        ),
        "complete_child_not_prematurely_claimed": not complete[
            "complete_F_child_closed"
        ],
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_aether_n3_admissible_child_cauchy_germ_v17_95",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "admissible_child_cauchy_germ": result,
        "status": "RECLASSIFIED" if passed else "INVALIDATED",
        "real_physical_property_explained": (
            "THE_EVENT_HAS_AN_ETA_HYPERREGULAR_CONSTRAINT_AND_MOMENTUM_"
            "CONSISTENT_MOVING_CHILD_GERM_BUT_NOT_YET_A_FLUX_BALANCED_CHILD"
        ),
        "dependency_advanced": (
            "CLOSES_THE_EVENT_TO_ADMISSIBLE_CHILD_CAUCHY_RECONSTRUCTION_"
            "AND_EVALUATES_ITS_OWN_DYNAMIC_SCALAR_F_child_RESIDUAL"
        ),
        "active_calculation": (
            "SOLVE_THE_DYNAMIC_SCALAR_FLUX_ROW_ON_THE_ADMISSIBLE_CHILD_"
            "RECONSTRUCTION_THEN_CLOSE_THE_CORE_AND_GAUGE_SPINOR_GHOST_BLOCKS"
        ),
        "direct_N3_solve_authorized_next": False,
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_admissible_child_cauchy_germ_v17_95.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "admissible_child_cauchy_germ", "completion_payload", "materialize",
]
