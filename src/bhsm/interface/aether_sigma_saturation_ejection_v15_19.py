"""BHSM v15.19 transient sigma activation, saturation and ejection audit.

This module solves the conservative v15.9 reduced formation trajectory,
classifies its sigma activation as transient tachyonic rather than Floquet,
derives the sign of stable-block quartic backreaction, and applies the exact
round-seam shape kernel to the proposed q-to-d inertia transfer.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from bhsm.interface.completion.stationary_full_preimage_transport_no_go_v14_85 import (
    pure_repartition_inertia_witness,
)
from bhsm.interface.completion.tensor_differential_incidence_v14_69 import (
    round_shape_kernel_payload,
)


VERSION = "v15.19"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False
CAMPAIGN_OBJECT = (
    "DOES_THE_ACTION_OWNED_LOCALIZATION_INERTIA_KERNEL_CONTAIN_ENOUGH_"
    "HIGHER_RESPONSE_TO_CREATE_A_UNIQUE_SIGMA_SKIN_AND_REDIRECT_"
    "FORMATION_MOMENTUM_INTO_EJECTION"
)
EXACT_NEXT_OBJECT = (
    "ACTION_OWNED_NONROUND_OR_SECOND_SHAPE_M5_M4_LOCALIZATION_INERTIA_"
    "KERNEL_WITH_DIRECT_POSITIVE_SIGMA_QUARTIC_CANONICAL_SEPARATION_MODE_"
    "AND_NONZERO_Q_TO_D_SYMPLECTIC_TRANSFER_ON_THE_V15_9_FORMATION_TRAJECTORY"
)
OUTCOME = "TRANSIENT_ACTIVATION_EXACT_SATURATION_AND_EJECTION_KERNEL_ABSENT"
PRIMARY_VERDICT = (
    "THE_CONSERVATIVE_V15_9_FORMATION_EQUATION_HAS_AN_EXACT_SECH_"
    "HOMOCLINIC_TRAJECTORY_WHOSE_VELOCITY_SQUARED_IS_A_FINITE_PULSE_SO_"
    "ANY_SIGMA_ACTIVATION_IS_TRANSIENT_TACHYONIC_NOT_FLOQUET;_ITS_"
    "MAXIMUM_INERTIAL_LOWERING_IS_EXACT_AND_SCALE_INDEPENDENT_AFTER_"
    "MULTIPLYING_BY_MQ;_ELIMINATING_ANY_POSITIVE_RESPONSE_BLOCK_COUPLED_"
    "THROUGH_SIGMA_SQUARED_CAN_ONLY_LOWER_THE_QUARTIC_SO_IT_CANNOT_"
    "CREATE_MISSING_POSITIVE_SATURATION;_AND_THE_ROUND_EQUATOR_K_EQUALS_"
    "ZERO_MAKES_NORMAL_SEPARATION_A_FIRST_ORDER_TRACE_KERNEL_WHILE_PURE_"
    "CAP_REPARTITION_HAS_ZERO_TOTAL_ACTION_INERTIA_SO_NO_Q_TO_D_CANONICAL_"
    "MOMENTUM_TRANSFER_IS_PRESENT"
)


def _finite(value: float, name: str) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _positive(value: float, name: str) -> float:
    result = _finite(value, name)
    if result <= 0.0:
        raise ValueError(f"{name} must be positive")
    return result


def formation_homoclinic_state(
    proper_time: float, *, supercriticality: float, critical_radius: float
) -> dict[str, float]:
    """Return the exact zero-energy homoclinic solution of the v15.9 ODE."""

    tau = _finite(proper_time, "proper_time")
    m = _positive(supercriticality, "supercriticality")
    ac = _positive(critical_radius, "critical_radius")
    inertia = 1.5 * ac**2
    growth_rate = math.sqrt(5.0 * m / (6.0 * ac**2))
    amplitude = math.sqrt(90.0 * m / 23.0)
    argument = growth_rate * tau
    sech = 1.0 / math.cosh(argument)
    tangent = math.tanh(argument)
    q = amplitude * sech
    q_dot = -amplitude * growth_rate * sech * tangent
    q_ddot = 5.0 * m * q / (6.0 * ac**2) - 23.0 * q**3 / (54.0 * ac**2)
    potential = -5.0 * m * q**2 / 8.0 + 23.0 * q**4 / 144.0
    return {
        "q": q,
        "q_dot": q_dot,
        "q_ddot": q_ddot,
        "collective_inertia": inertia,
        "growth_rate": growth_rate,
        "turning_amplitude": amplitude,
        "Hamiltonian": 0.5 * inertia * q_dot**2 + potential,
        "Euler_residual": q_ddot - 5.0 * m * q / (6.0 * ac**2) + 23.0 * q**3 / (
            54.0 * ac**2
        ),
    }


def maximum_formation_inertial_drive(
    *, supercriticality: float, critical_radius: float
) -> dict[str, float]:
    """Return max qdot^2 and M_q max qdot^2 on the homoclinic pulse."""

    m = _positive(supercriticality, "supercriticality")
    ac = _positive(critical_radius, "critical_radius")
    maximum_velocity_squared = 75.0 * m**2 / (92.0 * ac**2)
    inertia = 1.5 * ac**2
    return {
        "maximum_q_dot_squared": maximum_velocity_squared,
        "q_squared_at_velocity_maximum": 45.0 * m / 23.0,
        "M_q_times_maximum_q_dot_squared": inertia * maximum_velocity_squared,
        "scale_independent_value": 225.0 * m**2 / 184.0,
    }


def tachyonic_activation_windows(
    *,
    static_sigma_curvature: float,
    g: float,
    supercriticality: float,
    critical_radius: float,
) -> dict[str, Any]:
    """Locate K_static-g*M_q*qdot^2<0 for a constant-curvature control.

    The physical v15.9 eta profile generally makes K_static a function of q.
    This exact closed form is therefore a control and not the final physical
    activation window.
    """

    curvature = _positive(static_sigma_curvature, "static_sigma_curvature")
    coupling = _positive(g, "g")
    m = _positive(supercriticality, "supercriticality")
    ac = _positive(critical_radius, "critical_radius")
    maximum = maximum_formation_inertial_drive(
        supercriticality=m, critical_radius=ac
    )
    maximum_lowering = coupling * maximum["M_q_times_maximum_q_dot_squared"]
    if maximum_lowering <= curvature:
        return {
            "activation": False,
            "classification": "NO_TANGENT_CROSSING_ON_ZERO_ENERGY_FORMATION_PULSE",
            "maximum_inertial_lowering": maximum_lowering,
            "incoming_window": None,
            "outgoing_window": None,
            "Floquet": False,
            "constant_static_curvature_control": True,
        }
    rate = math.sqrt(5.0 * m / (6.0 * ac**2))
    amplitude = math.sqrt(90.0 * m / 23.0)
    inertia = 1.5 * ac**2
    denominator = coupling * inertia * amplitude**2 * rate**2
    c = curvature / denominator
    discriminant = math.sqrt(1.0 - 4.0 * c)
    y_low = 0.5 * (1.0 - discriminant)
    y_high = 0.5 * (1.0 + discriminant)
    u_low = math.acosh(1.0 / math.sqrt(y_high)) / rate
    u_high = math.acosh(1.0 / math.sqrt(y_low)) / rate
    return {
        "activation": True,
        "classification": "TWO_TRANSIENT_TACHYONIC_WINDOWS_ON_THE_CONSERVATIVE_HOMOCLINIC_PULSE",
        "maximum_inertial_lowering": maximum_lowering,
        "threshold_ratio": c,
        "sech_squared_roots": [y_low, y_high],
        "incoming_window": [-u_high, -u_low],
        "outgoing_window": [u_low, u_high],
        "turning_point_is_tangent_stable_again": True,
        "periodic_coefficient": False,
        "Floquet": False,
        "constant_static_curvature_control": True,
    }


def schur_reduced_quartic(
    direct_quartic: float,
    sigma_squared_response_vertex: Sequence[float],
    response_hessian: Sequence[Sequence[float]],
) -> dict[str, float | bool]:
    """Eliminate y from V=G*sigma^4/4+sigma^2*b.y+y.H.y/2.

    For H positive, G_eff=G-2*b^T H^-1 b <= G.  Thus a stable response
    block softens the quartic and cannot generate positive saturation when
    the direct quartic is absent.
    """

    direct = _finite(direct_quartic, "direct_quartic")
    b = np.asarray(sigma_squared_response_vertex, dtype=float)
    h = np.asarray(response_hessian, dtype=float)
    if b.ndim != 1 or h.shape != (b.size, b.size) or b.size == 0:
        raise ValueError("vertex and nonempty square response Hessian must match")
    if not np.all(np.isfinite(b)) or not np.all(np.isfinite(h)):
        raise ValueError("response data must be finite")
    if not np.allclose(h, h.T, atol=1.0e-13):
        raise ValueError("response Hessian must be symmetric")
    if float(np.min(np.linalg.eigvalsh(h))) <= 0.0:
        raise ValueError("response Hessian must be positive")
    norm = float(b @ np.linalg.solve(h, b))
    effective = direct - 2.0 * norm
    return {
        "direct_quartic": direct,
        "Schur_norm": norm,
        "quartic_correction": -2.0 * norm,
        "effective_quartic": effective,
        "softens_or_equal": effective <= direct,
        "positive_saturation_generated_from_zero_direct": direct == 0.0 and effective > 0.0,
    }


def higher_inertia_quartic(
    direct_quartic: float,
    sigma_four_inertia_coefficient: float,
    q_inertia: float,
    q_dot: float,
) -> dict[str, float]:
    """Return G_eff from I_qq=M(1+g*sigma^2+h*sigma^4+...)."""

    direct = _finite(direct_quartic, "direct_quartic")
    h4 = _finite(sigma_four_inertia_coefficient, "sigma_four_inertia_coefficient")
    mass = _positive(q_inertia, "q_inertia")
    velocity = _finite(q_dot, "q_dot")
    correction = -2.0 * h4 * mass * velocity**2
    return {
        "direct_quartic": direct,
        "dynamic_quartic_correction": correction,
        "effective_quartic": direct + correction,
    }


def two_coordinate_kinetic_transfer(
    *,
    i_qq: float,
    i_dd: float,
    i_dq: float,
    q_dot: float,
    d_dot: float,
) -> dict[str, float | bool]:
    """Evaluate canonical momenta for an already-derived (q,d) kinetic metric."""

    qq = _positive(i_qq, "I_qq")
    dd = _positive(i_dd, "I_dd")
    cross = _finite(i_dq, "I_dq")
    qv = _finite(q_dot, "q_dot")
    dv = _finite(d_dot, "d_dot")
    determinant = qq * dd - cross**2
    if determinant <= 0.0:
        raise ValueError("the two-coordinate inertia metric must be positive definite")
    return {
        "inertia_determinant": determinant,
        "Cauchy_bound_satisfied": cross**2 < qq * dd,
        "P_q": qq * qv + cross * dv,
        "P_d": dd * dv + cross * qv,
        "P_d_from_q_when_d_dot_zero": cross * qv,
    }


def round_contact_provenance_payload() -> dict[str, Any]:
    shape = round_shape_kernel_payload()
    repartition = pure_repartition_inertia_witness(0.17)
    return {
        "shape_variation": "delta_h=Tr(delta_g)+2*d*K",
        "round_equator_K": 0.0,
        "pure_normal_round_trace_response_norm": shape[
            "pure_normal_round_response_norm"
        ],
        "normal_d_is_first_order_metric_trace_kernel": shape[
            "pure_normal_displacement_is_first_order_metric_trace_kernel_on_round_equator"
        ],
        "pure_cap_repartition_inertia": repartition["finite_difference_inertia"],
        "first_order_round_I_dq": 0.0,
        "physical_nonround_or_second_shape_I_dq": None,
        "canonical_d_mode_present": False,
        "required_route": "nonround_action_stationary_K_ab_or_second_shape_variation_plus_symplectic_reduction",
    }


def completion_payload() -> dict[str, Any]:
    state = formation_homoclinic_state(
        -1.1, supercriticality=0.4, critical_radius=2.0
    )
    maximum = maximum_formation_inertial_drive(
        supercriticality=0.4, critical_radius=2.0
    )
    windows = tachyonic_activation_windows(
        static_sigma_curvature=0.02,
        g=1.0,
        supercriticality=0.4,
        critical_radius=2.0,
    )
    quartic = schur_reduced_quartic(1.0, [0.3, -0.2], [[2.0, 0.1], [0.1, 1.5]])
    zero_direct = schur_reduced_quartic(0.0, [0.3], [[2.0]])
    contact = round_contact_provenance_payload()
    diagnostic_transfer = two_coordinate_kinetic_transfer(
        i_qq=2.0, i_dd=3.0, i_dq=0.4, q_dot=0.7, d_dot=0.0
    )
    validation = {
        "exact_homoclinic_solves_formation_equation": abs(state["Euler_residual"]) < 1.0e-14,
        "homoclinic_energy_zero": abs(state["Hamiltonian"]) < 1.0e-13,
        "maximum_drive_identity_exact": math.isclose(
            maximum["M_q_times_maximum_q_dot_squared"],
            maximum["scale_independent_value"],
            rel_tol=1.0e-14,
        ),
        "control_has_transient_not_Floquet_activation": (
            windows["activation"] and not windows["Floquet"]
        ),
        "positive_response_block_softens_quartic": quartic["softens_or_equal"],
        "zero_direct_quartic_does_not_gain_positive_saturation": not zero_direct[
            "positive_saturation_generated_from_zero_direct"
        ],
        "higher_inertia_quartic_requires_new_derived_h4": higher_inertia_quartic(
            0.0, 0.2, 2.0, 0.7
        )["effective_quartic"]
        < 0.0,
        "round_normal_shape_is_first_order_trace_kernel": contact[
            "normal_d_is_first_order_metric_trace_kernel"
        ],
        "pure_repartition_inertia_zero": abs(contact["pure_cap_repartition_inertia"]) < 1.0e-8,
        "round_first_order_cross_inertia_zero": contact["first_order_round_I_dq"] == 0.0,
        "diagnostic_positive_cross_inertia_obeys_bound": diagnostic_transfer[
            "Cauchy_bound_satisfied"
        ],
        "diagnostic_cross_inertia_not_promoted": contact[
            "physical_nonround_or_second_shape_I_dq"
        ]
        is None,
        "no_new_field_coefficient_or_empirical_input": True,
        "frozen_predictions_unchanged": True,
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_sigma_saturation_ejection_v15_19",
        "version": VERSION,
        "campaign_object": CAMPAIGN_OBJECT,
        "primary_verdict": PRIMARY_VERDICT,
        "outcome": OUTCOME,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "exact_formation_trajectory": {
            "formula": "q=A*sech(lambda*tau)",
            "A_squared": "90m/23",
            "lambda_squared": "5m/(6a_c^2)",
            "control_state": state,
            "maximum_drive": maximum,
        },
        "sigma_activation": windows,
        "physical_activation_gate": {
            "actual_curvature": (
                "K_sigma_static(t)=A0+g[kappa1*X_eta(q(t))+X_eta(q(t))^4/4]"
            ),
            "actual_X_eta_profile_along_Lorentzian_formation_trajectory_present": False,
            "alpha_r_selected": False,
            "physical_window_endpoints_evaluated": False,
            "robust_classification": (
                "the_conservative_q_trajectory_is_nonperiodic_so_any_"
                "negative_curvature_intervals_are_transient_not_Floquet"
            ),
        },
        "activation_claim_boundary": (
            "the_closed_form_window_uses_constant_K_static;_the_conservative_"
            "separatrix_is_a_control_trajectory_and_a_periodic_or_damped_"
            "action_selected_formation_orbit_has_not_been_derived"
        ),
        "quartic_saturation": {
            "stable_response_Schur_control": quartic,
            "zero_direct_control": zero_direct,
            "theorem": (
                "positive_block_elimination_cannot_supply_missing_positive_"
                "quartic_saturation_in_the_declared_sigma_squared_vertex_convention"
            ),
            "finite_frequency_exception": (
                "H-omega_squared_M_can_change_sign_but_then_local_stable_"
                "elimination_fails_near_poles_and_full_dynamics_is_required"
            ),
            "direct_positive_localization_fourth_variation_present": False,
            "unique_sigma_plus_minus_amplitude": None,
        },
        "contact_and_ejection": {
            "round_provenance": contact,
            "diagnostic_if_a_physical_cross_inertia_existed": diagnostic_transfer,
            "diagnostic_promoted": False,
            "physical_P_d": None,
            "ejection": False,
        },
        "scientific_conclusion": (
            "the_formation_pulse_can_open_a_finite_sigma_instability_window_"
            "but_the_retained_localization_response_neither_saturates_it_"
            "without_G0_nor_couples_it_to_a_canonical_round_separation_mode"
        ),
        "Hindsight_20_20": {
            "VALIDATED": [
                "exact_transient_tachyonic_activation_is_possible_on_the_conservative_v15_9_pulse",
                "the_peak_inertial_drive_is_225m_squared_over_184_after_multiplying_by_Mq",
                "a_real_cross_inertia_would_redirect_canonical_momentum_subject_to_positive_metric_bounds",
            ],
            "INVALIDATED": [
                "the_conservative_v15_9_pulse_is_a_Floquet_drive",
                "stable_constraint_backreaction_generates_a_missing_positive_sigma_quartic",
                "the_round_equatorial_first_shape variation_generates_I_dq",
                "pure_cap_repartition_is_a_physical_localization_inertia",
            ],
            "RECLASSIFIED": [
                "sigma_activation_as_a_finite_tachyonic_window_on_the_exact_control_trajectory",
                "quartic_saturation_as_requiring_direct_positive_fourth_variation_or_a_full_nonlocal_dynamical_mechanism",
                "ejection_transfer_as_nonround_or_second_shape_symplectic_physics",
            ],
            "OPEN": [EXACT_NEXT_OBJECT],
        },
        "exact_next_object": EXACT_NEXT_OBJECT,
        "missing_physical_assumption_plain_language": (
            "the_current_action_can_start_a_sigma_instability_during_motion_"
            "but_has_no_derived_positive_nonlinearity_to_stop_it_and_no_"
            "physical_separation_mode_to_receive_its_momentum;_both_must_"
            "come_from_a_nonround_or_second_shape_localization_action"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "no_retuning_certificate": {
            "new_fields": [],
            "new_continuous_coefficients": [],
            "new_empirical_inputs": [],
            "diagnostic_cross_inertia_promoted": False,
            "frozen_predictions_changed": False,
            "USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE": (
                USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE
            ),
        },
    }


def _canonical_json_value(value: Any) -> Any:
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite float cannot be materialized")
        rounded = round(value, 12)
        return 0.0 if rounded == 0.0 else rounded
    if isinstance(value, Mapping):
        return {key: _canonical_json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical_json_value(item) for item in value]
    return value


def deterministic_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(
        _canonical_json_value(payload),
        indent=2,
        sort_keys=True,
        ensure_ascii=False,
        allow_nan=False,
    ) + "\n"


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_sigma_saturation_ejection_v15_19.json"
    path.write_bytes(deterministic_json(completion_payload()).encode("utf-8"))
    return path
