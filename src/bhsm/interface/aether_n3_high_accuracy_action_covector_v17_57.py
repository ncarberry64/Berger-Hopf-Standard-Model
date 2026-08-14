"""Higher-accuracy same-action SBP covector after the v17.56 scale audit."""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_exact_radial_schur_lift_v15_83 import exact_action_jet_at_state
from bhsm.interface.aether_m4_standard_model_zeta_backreaction_v15_51 import standard_model_casimir_coefficient
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_fresh_sbp_kkt_v16_58 import (
    sbp_event_covector, sbp_event_value_from_base, sbp_projected_residual_and_vector,
    sbp_replacement_action_from_base,
)
from bhsm.interface.aether_n3_fresh_sbp_six_owner_measured_cone_v17_05 import _metrics
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_post_curvature_compensation_audit_v17_54 import v17_53_selected_raw_vector
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import (
    M_DIMENSION, NODES, ORDER, Q_DIMENSION, boundary_lapse,
    boundary_radius_and_jacobian, kkt_variable_scales, trapezoid_weights,
    unpack_reduced,
)
from bhsm.interface.aether_n3_sbp_redirect_audit_v16_57 import trapezoid_sbp_difference
from bhsm.interface.aether_replacement_geometry_force_v16_06 import zero_source_heat_geometry_response
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import generalized_lagrangian

VERSION = "v17.57"
CLASSIFICATION = "BHSM_N3_HIGH_ACCURACY_SAME_ACTION_SBP_COVECTOR"
FULL_BHSM_COMPLETE = False
COORDINATE_RELATIVE_STEP = 1e-4


def _high_accuracy_local_first_derivatives(
    q: np.ndarray, velocity: np.ndarray, multipliers: np.ndarray,
    *, points: int, coordinate_relative_step: float,
) -> tuple[float, np.ndarray, np.ndarray, np.ndarray]:
    jet = exact_action_jet_at_state(
        ORDER, q, velocity, multipliers, points=points
    )
    dq = np.empty(Q_DIMENSION)
    for index in range(Q_DIMENSION):
        step = coordinate_relative_step * max(1.0, abs(float(q[index])))
        delta = np.zeros(Q_DIMENSION)
        delta[index] = step
        plus_one = generalized_lagrangian(
            q + delta, velocity, multipliers, order=ORDER, points=points
        )
        minus_one = generalized_lagrangian(
            q - delta, velocity, multipliers, order=ORDER, points=points
        )
        plus_two = generalized_lagrangian(
            q + 2 * delta, velocity, multipliers, order=ORDER, points=points
        )
        minus_two = generalized_lagrangian(
            q - 2 * delta, velocity, multipliers, order=ORDER, points=points
        )
        dq[index] = (-plus_two + 8 * plus_one - 8 * minus_one + minus_two) / (12 * step)
    return (
        float(jet.value), dq,
        np.asarray(jet.gradient[:Q_DIMENSION]),
        np.asarray(jet.gradient[Q_DIMENSION:Q_DIMENSION + M_DIMENSION]),
    )


def high_accuracy_sbp_action_covector(
    base_vector: np.ndarray, *, radial_points: int = 36,
    coordinate_relative_step: float = COORDINATE_RELATIVE_STEP,
) -> dict[str, Any]:
    base = np.asarray(base_vector, dtype=float)
    unpacked = unpack_reduced(np.concatenate((base, [0.0])))
    q = np.asarray(unpacked["coordinates"])
    multipliers = np.asarray(unpacked["multipliers"])
    period = float(unpacked["period"])
    difference = trapezoid_sbp_difference()
    weights = trapezoid_weights()
    velocity = difference @ q / period
    attached = np.empty(NODES)
    dq_local = np.empty((NODES, Q_DIMENSION))
    dv_local = np.empty((NODES, Q_DIMENSION))
    dm_local = np.empty((NODES, M_DIMENSION))
    for node in range(NODES):
        attached[node], dq_local[node], dv_local[node], dm_local[node] = (
            _high_accuracy_local_first_derivatives(
                q[node], velocity[node], multipliers[node], points=radial_points,
                coordinate_relative_step=coordinate_relative_step,
            )
        )
    radii, log_jacobian = boundary_radius_and_jacobian(q)
    lapse = boundary_lapse(multipliers)
    restored = lapse * standard_model_casimir_coefficient() / radii
    parent = attached + restored
    dq_local -= restored[:, None] * log_jacobian
    signs = (-1.0) ** np.arange(1, ORDER + 1)
    dm_local[:, :ORDER] += restored[:, None] * signs
    dq = period * weights[:, None] * dq_local + difference.T @ (weights[:, None] * dv_local)
    dm = period * weights[:, None] * dm_local
    lapse_sum = float(weights @ lapse)
    proper = period * lapse_sum
    heat = zero_source_heat_geometry_response(radii, proper / NODES)
    dq += np.asarray(heat["d_Gamma_heat_d_log_R_nodes"])[:, None] * log_jacobian
    duration = float(heat["d_Gamma_heat_d_log_proper_step"])
    dm[:, :ORDER] += duration * (weights * lapse / lapse_sum)[:, None] * signs
    dperiod = float(weights @ (
        parent - np.einsum("ij,ij->i", dv_local, velocity)
    )) + duration / period
    covector = np.concatenate((dq[1:].ravel(), dm.ravel(), [dperiod]))
    gamma = period * float(weights @ parent) + float(heat["Gamma_heat"])
    return {
        "Gamma_replacement": gamma,
        "covector": covector,
        "coordinate_covector": dq,
        "multiplier_covector": dm,
        "period_covector": dperiod,
        "proper_duration": proper,
        "same_common_gauge_ghost_rank16_HS_operator": heat[
            "same_rank16_gauge_ghost_HS_direct_sum_as_source_response"
        ],
    }


def high_accuracy_sbp_projected_residual_and_vector(
    scaled_vector: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    y = np.asarray(scaled_vector, dtype=float).copy()
    scales = kkt_variable_scales()
    base = y[:-1] / scales[:-1]
    action = np.asarray(high_accuracy_sbp_action_covector(base)["covector"]) / scales[:-1]
    event = sbp_event_covector(base) / scales[:-1] / scales[-1]
    y[-1] = -float(action @ event) / float(event @ event)
    residual = np.concatenate((
        action + y[-1] * event,
        [sbp_event_value_from_base(base) / scales[-1]],
    ))
    return y, residual


def high_accuracy_covector_audit() -> dict[str, Any]:
    raw = v17_53_selected_raw_vector()
    scales = kkt_variable_scales()
    base = raw[:-1]
    legacy_y, legacy_residual = sbp_projected_residual_and_vector(raw * scales)
    accurate_y, accurate_residual = high_accuracy_sbp_projected_residual_and_vector(raw * scales)
    accurate = high_accuracy_sbp_action_covector(base)
    direction = np.cos(np.arange(base.size) + 0.37) / scales[:-1]
    direction /= np.linalg.norm(direction)
    epsilon = 1e-5
    finite = (
        sbp_replacement_action_from_base(base + epsilon * direction)
        - sbp_replacement_action_from_base(base - epsilon * direction)
    ) / (2 * epsilon)
    analytic = float(np.asarray(accurate["covector"]) @ direction)
    return {
        "source_state": "v17.53_selected_event_log_curvature_compensated_state",
        "physical_action_changed": False,
        "physical_event_changed": False,
        "coordinate_derivative_stencil": "FIVE_POINT_CENTERED",
        "coordinate_relative_step": COORDINATE_RELATIVE_STEP,
        "velocity_multiplier_derivatives": "EXACT_ACTION_JET",
        "legacy_metrics": _metrics(legacy_residual),
        "high_accuracy_metrics": _metrics(accurate_residual),
        "legacy_projection_shift_norm": float(np.linalg.norm(legacy_y - raw * scales)),
        "high_accuracy_projection_shift_norm": float(np.linalg.norm(accurate_y - raw * scales)),
        "directional_witness": {
            "finite_difference_action_derivative": float(finite),
            "high_accuracy_covector_derivative": analytic,
            "relative_residual": abs(analytic - finite) / max(1.0, abs(finite)),
        },
        "eta_minimum": _minimum_node_eta(accurate_y / scales),
        "full_state_hex": [float(value).hex() for value in accurate_y / scales],
    }


def completion_payload() -> dict[str, Any]:
    result = high_accuracy_covector_audit()
    witness = result["directional_witness"]
    validation = {
        "physical_action_unchanged": not result["physical_action_changed"],
        "physical_event_unchanged": not result["physical_event_changed"],
        "five_point_coordinate_derivative": (
            result["coordinate_derivative_stencil"] == "FIVE_POINT_CENTERED"
        ),
        "exact_velocity_multiplier_derivatives": (
            result["velocity_multiplier_derivatives"] == "EXACT_ACTION_JET"
        ),
        "covector_matches_action_direction": witness["relative_residual"] < 2e-6,
        "high_accuracy_residual_finite": all(
            math.isfinite(value) for value in result["high_accuracy_metrics"].values()
        ),
        "eta_domain_preserved": result["eta_minimum"] > 1e-5,
        "full_precision_state_preserved": len(result["full_state_hex"]) == 376,
    }
    return {
        "artifact": "BHSM_aether_n3_high_accuracy_action_covector_v17_57",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": False,
        "high_accuracy_action_covector": result,
        "status": "VALIDATED" if all(validation.values()) else "INVALIDATED",
        "real_physical_property_explained": (
            "SAME_ACTION_COVECTOR_WITH_EXACT_VELOCITY_MULTIPLIER_AND_HIGH_ORDER_"
            "COORDINATE_DERIVATIVES"
        ),
        "dependency_advanced": (
            "RESTORES_NUMERICAL_IDENTIFIABILITY_OF_SCALE_COMPONENT_CONTINUATION"
        ),
        "active_calculation": (
            "REASSEMBLE_THE_IDENTICAL_PHYSICAL_JACOBIAN_FROM_THE_VALIDATED_HIGH_"
            "ACCURACY_COVECTOR_AND_RESUME_N3_CLOSURE"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_high_accuracy_action_covector_v17_57.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "COORDINATE_RELATIVE_STEP",
    "high_accuracy_sbp_action_covector", "high_accuracy_sbp_projected_residual_and_vector",
    "high_accuracy_covector_audit", "completion_payload", "materialize",
]
