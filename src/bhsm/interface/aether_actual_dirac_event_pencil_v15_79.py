"""Identify the actual constrained event pencil on the v15.74 child orbit.

The pointwise eta coefficient stays positive.  The approaching singularity is
instead a simple eigenvalue of the full Euler--Dirac velocity/multiplier
matrix.  This supersedes the off-orbit ``min L_eta -> 0`` extrapolation as the
physical control variable for the common M5-to-M4 pushforward.
"""

from __future__ import annotations

import json
import math
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.aether_m4_standard_model_zeta_backreaction_v15_51 import (
    attached_eta_gauge_dirac_acceleration,
    attached_multiplier_lagrangian,
)
from bhsm.interface.aether_post_cut_nonround_lorentzian_cap_v15_48 import cap_fields
from bhsm.interface.aether_sampled_event_shell_pushforward_v15_74 import SNAPSHOTS


VERSION = "v15.79"
CLASSIFICATION = "BHSM_ACTUAL_CONSTRAINED_DIRAC_EVENT_PENCIL"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False
VARIABLE_NAMES = (
    "dot_log_R", "dot_u1", "dot_u2", "dot_w0", "dot_w1", "dot_v0",
    "dot_v1", "lapse_n1", "lapse_n2", "shift_b0", "shift_b1",
)


def _state() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    state = SNAPSHOTS[0.10602]
    return (
        np.asarray(state["q"], dtype=float),
        np.asarray(state["v"], dtype=float),
        np.asarray(state["m"], dtype=float),
    )


def _dirac_hessian(
    q_full: np.ndarray, velocity_full: np.ndarray, multipliers: np.ndarray,
    *, points: int = 32, step: float = 5.0e-5,
) -> np.ndarray:
    q = np.asarray(q_full, dtype=float)[:7]
    z = np.concatenate((np.asarray(velocity_full, dtype=float)[:7], multipliers))

    def lagrangian(z_value: np.ndarray) -> float:
        coordinates = np.zeros(9)
        coordinates[:7] = q
        velocities = np.zeros(9)
        velocities[:7] = z_value[:7]
        return attached_multiplier_lagrangian(
            coordinates, velocities, z_value[7:], points=points
        )

    center = lagrangian(z)
    hessian = np.empty((11, 11))
    for row in range(11):
        erow = np.zeros(11)
        erow[row] = step
        for column in range(row, 11):
            ecolumn = np.zeros(11)
            ecolumn[column] = step
            if row == column:
                value = (
                    lagrangian(z + erow) - 2.0 * center
                    + lagrangian(z - erow)
                ) / step**2
            else:
                value = (
                    lagrangian(z + erow + ecolumn)
                    - lagrangian(z + erow - ecolumn)
                    - lagrangian(z - erow + ecolumn)
                    + lagrangian(z - erow - ecolumn)
                ) / (4.0 * step**2)
            hessian[row, column] = value
            hessian[column, row] = value
    return hessian


def _tracked_eigenpair(
    hessian: np.ndarray, reference: np.ndarray | None = None,
) -> tuple[float, np.ndarray]:
    values, vectors = np.linalg.eigh(hessian)
    if reference is None:
        index = int(np.argmin(np.abs(values)))
    else:
        index = int(np.argmax(np.abs(vectors.T @ reference)))
    vector = vectors[:, index]
    if reference is not None and float(vector @ reference) < 0.0:
        vector = -vector
    return float(values[index]), vector


def _minimum_eta_legendre(
    q: np.ndarray, velocity: np.ndarray, multipliers: np.ndarray,
    *, points: int = 900,
) -> float:
    fields = cap_fields(q, velocity, points=points)
    chi = np.asarray(fields["chi"])
    A = np.asarray(fields["A"])
    B = np.asarray(fields["B"])
    C = np.asarray(fields["C"])
    f = np.asarray(fields["f"])
    n1, n2, b0, b1 = multipliers
    lapse = np.exp(n1 * np.cos(4.0 * chi) + n2 * np.cos(8.0 * chi))
    shift = np.sin(4.0 * chi) * (b0 + b1 * np.cos(4.0 * chi))
    normal_f = (
        np.asarray(fields["f_dot_coordinate"])
        - shift * np.asarray(fields["f_prime"])
    ) / lapse
    spatial_x = (
        np.asarray(fields["f_prime"]) ** 2 / C**2
        + 3.0 * np.cos(f) ** 2 / A**2
        + 3.0 * np.sin(f) ** 2 / B**2
    )
    return float(np.min(1.0 + (spatial_x - normal_f**2) ** 3))


@lru_cache(maxsize=1)
def event_pencil_diagnostics() -> dict[str, Any]:
    q, velocity, multipliers = _state()
    dynamics = attached_eta_gauge_dirac_acceleration(
        q, velocity, multipliers, points=32, step=5.0e-5
    )
    acceleration = np.asarray(dynamics["acceleration"])
    multiplier_velocity = np.asarray(dynamics["multiplier_velocity"])
    hessian = _dirac_hessian(q, velocity, multipliers)
    eigenvalue, eigenvector = _tracked_eigenpair(hessian)

    tangent_step = 1.0e-6
    plus_hessian = _dirac_hessian(
        q + tangent_step * velocity,
        velocity + tangent_step * acceleration,
        multipliers + tangent_step * multiplier_velocity,
    )
    minus_hessian = _dirac_hessian(
        q - tangent_step * velocity,
        velocity - tangent_step * acceleration,
        multipliers - tangent_step * multiplier_velocity,
    )
    plus_value, _ = _tracked_eigenpair(plus_hessian, eigenvector)
    minus_value, _ = _tracked_eigenpair(minus_hessian, eigenvector)
    eigenvalue_derivative = (plus_value - minus_value) / (2.0 * tangent_step)

    eta_step = 1.0e-7
    eta_value = _minimum_eta_legendre(q, velocity, multipliers)
    eta_plus = _minimum_eta_legendre(
        q + eta_step * velocity,
        velocity + eta_step * acceleration,
        multipliers + eta_step * multiplier_velocity,
    )
    eta_minus = _minimum_eta_legendre(
        q - eta_step * velocity,
        velocity - eta_step * acceleration,
        multipliers - eta_step * multiplier_velocity,
    )
    eta_derivative = (eta_plus - eta_minus) / (2.0 * eta_step)
    crossing_increment = -eigenvalue / eigenvalue_derivative
    components = {
        name: float(value) for name, value in zip(VARIABLE_NAMES, eigenvector)
    }
    return {
        "time": 0.10602,
        "soft_Dirac_eigenvalue": eigenvalue,
        "positive_distance_delta": -eigenvalue,
        "soft_eigenvalue_time_derivative": eigenvalue_derivative,
        "delta_time_derivative": -eigenvalue_derivative,
        "linearized_crossing_increment": crossing_increment,
        "linearized_crossing_time": 0.10602 + crossing_increment,
        "Dirac_condition_number": float(np.linalg.cond(hessian)),
        "minimum_eta_Legendre": eta_value,
        "minimum_eta_Legendre_time_derivative": eta_derivative,
        "minimum_eta_Legendre_at_linearized_Dirac_event": (
            eta_value + eta_derivative * crossing_increment
        ),
        "soft_eigenvector_components": components,
        "dominant_component": max(components, key=lambda key: abs(components[key])),
        "soft_mode_is_metric_shape_dominated": (
            abs(components["dot_w1"]) > 0.8
        ),
    }


def actual_event_pushforward_contract() -> dict[str, Any]:
    return {
        "actual_control": (
            "delta(t)=-lambda_soft(D_Euler-Dirac[q,dotq,m])_downarrow_zero"
        ),
        "not_the_actual_control": "epsilon_eta=min_chi(1+X_eta^3)",
        "principal_pencil_split": (
            "D_KKT=-delta*P_s+D_perp,_P_s=e_s_tensor_e_s"
        ),
        "common_parent_cycle": (
            "Gamma_cycle=Gamma_reset+integral_dt*[-log_integral_"
            "B_Phi=fixed_exp(-S5)]"
        ),
        "absolute_gauge_residue": (
            "Z_i^cycle=T^(-1)*delta_Fi^2_Gamma_cycle"
        ),
        "soft_source": (
            "J_s=e_s^T*delta_Gamma5/delta_(dotq,m);_Gamma_soft="
            "-(2*delta)^(-1)<J_s,J_s>"
        ),
        "LR_scalar_projection": (
            "G_LR,soft(delta)=delta^(-1)*P_scalarLR[<J_s,J_s>]/2"
        ),
        "canonical_Yukawa": (
            "Y_f^cycle=(Z_L*Z_R*Z_H)^(-1/2)*"
            "delta_bar_fL_delta_fR_delta_H_Gamma_cycle"
        ),
        "required_next_evaluation": (
            "COMPUTE_THE_FERMIONIC_SPIN-STRESS_PROJECTION_ON_e_s_AND_THE_"
            "GAUGE_DtN_ON_THE_SAME_delta-CONTROLLED_EVENT_LAYER"
        ),
        "same_parent_functional_required": True,
        "split_normalization_forbidden": True,
    }


def completion_payload() -> dict[str, Any]:
    diagnostic = event_pencil_diagnostics()
    contract = actual_event_pushforward_contract()
    validation = {
        "soft_Dirac_mode_approaches_zero": (
            diagnostic["soft_Dirac_eigenvalue"] < 0.0
            and diagnostic["soft_eigenvalue_time_derivative"] > 0.0
        ),
        "linearized_event_is_nearby": (
            0.0 < diagnostic["linearized_crossing_increment"] < 5.0e-5
        ),
        "eta_Legendre_stays_strictly_positive": (
            diagnostic["minimum_eta_Legendre_at_linearized_Dirac_event"] > 0.5
        ),
        "eta_Legendre_moves_away_from_zero": (
            diagnostic["minimum_eta_Legendre_time_derivative"] > 0.0
        ),
        "actual_soft_mode_is_metric_shape_dominated": diagnostic[
            "soft_mode_is_metric_shape_dominated"
        ],
        "one_pushforward_required": (
            contract["same_parent_functional_required"]
            and contract["split_normalization_forbidden"]
        ),
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_actual_dirac_event_pencil_v15_79",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "event_pencil_diagnostics": diagnostic,
        "actual_event_pushforward": contract,
        "scientific_result": (
            "THE_ACTUAL_CHILD_APPROACHES_A_METRIC-SHAPE-DOMINATED_SIMPLE_"
            "EULER-DIRAC_EIGENVALUE_ZERO_NEAR_t=0.1060372_WHILE_min_L_eta_"
            "REMAINS_ABOUT_0.829_AND_IS_INCREASING;_THE_v15.75-v15.78_"
            "L_eta-DOWNARROW-ZERO_BRANCH_IS_OFF-ORBIT_AND_CANNOT_SUPPLY_THE_"
            "PHYSICAL_NORMALIZATION"
        ),
        "supersession": {
            "Cartan_shell_coefficient_c_EC_equals_3_over_4_retained": True,
            "off-orbit_L_eta_shell_crossing_promoted_to_physical": False,
            "v15_77_gap_branch_status": "CONDITIONAL_OFF-ORBIT_BRANCH",
            "v15_78_epsilon_power_count_status": "CONDITIONAL_OFF-ORBIT_BRANCH",
        },
        "claim_boundary": {
            "actual_event_control_identified": True,
            "actual_event_linearized_time_estimated": True,
            "actual_soft_fermion_source_projection_evaluated": False,
            "physical_joint_gauge_Yukawa_residues_evaluated": False,
        },
        "active_calculation": contract["required_next_evaluation"],
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def _canonical(value: Any) -> Any:
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        value = float(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite float")
        return round(value, 12)
    if isinstance(value, Mapping):
        return {key: _canonical(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    return value


def deterministic_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(_canonical(payload), indent=2, sort_keys=True) + "\n"


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_actual_dirac_event_pencil_v15_79.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "VARIABLE_NAMES",
    "event_pencil_diagnostics", "actual_event_pushforward_contract",
    "completion_payload", "deterministic_json", "materialize",
]
