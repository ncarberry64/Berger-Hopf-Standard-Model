"""C2 fixed-descriptor balls using the already certified uniform hard gap."""

from __future__ import annotations

import math
from typing import Any, Callable

import numpy as np

from bhsm.interface.aether_forward_c2_descriptor_cover import metric_data


def _bounds(
    *, radius: float, base_path: float, descriptor_upper: float,
    pf: dict[str, float], line: dict[str, float], birth: dict[str, Any],
    center_state: np.ndarray, center_b: float, center_hard_raw_norm: float,
    center_selected_action_norm: float, weights: np.ndarray,
    coefficient_bounds: dict[str, Any],
) -> dict[str, Any]:
    q_weights, _, maximum_q_weight, maximum_reduced_weight = metric_data()
    total_radius = base_path + radius
    hard_inverse = 1.0 / float(line["eigenline_gap_lower"])
    hard_d3 = (
        float(pf["hard_D3_center"])
        + float(pf["D4_full_hard_hard_upper"]) * total_radius
    )
    rhs_derivative = (
        float(pf["rhs_raw_derivative_center"])
        + float(pf["rhs_raw_second_derivative_upper"]) * total_radius
    )
    coupling = (
        float(pf["coupling_center"])
        + float(pf["D4_full_selected_hard_upper"]) * total_radius
    )
    projector_derivative = 2.0 * float(
        line["weighted_selected_to_complement_first_variation_on_ball"]
    )
    linear_rate = hard_inverse * hard_d3
    exponent = linear_rate * radius
    if exponent >= 700.0:
        hard_rate_raw = hard_jacobi_raw = structured_b = math.inf
    else:
        exponential = math.exp(exponent)
        b_seed = abs(center_b) + rhs_derivative * radius
        for _ in range(32):
            affine = hard_inverse * (rhs_derivative + projector_derivative * b_seed)
            hard_rate_raw = (
                center_hard_raw_norm * exponential
                + affine * math.expm1(exponent) / linear_rate
                if linear_rate > 0.0 else
                center_hard_raw_norm + affine * radius
            )
            structured_b = (
                rhs_derivative
                + (coupling + descriptor_upper * projector_derivative) * hard_rate_raw
            )
            updated = abs(center_b) + structured_b * radius
            if updated <= b_seed * (1.0 + 1.0e-12):
                b_seed = max(b_seed, updated)
                break
            b_seed = updated
        else:
            hard_rate_raw = hard_jacobi_raw = structured_b = math.inf
        if math.isfinite(hard_rate_raw):
            affine = hard_inverse * (rhs_derivative + projector_derivative * b_seed)
            hard_jacobi_raw = linear_rate * hard_rate_raw + affine

    hard_rate_action = maximum_reduced_weight * hard_rate_raw
    hard_jacobi_action = maximum_reduced_weight * hard_jacobi_raw
    b_interval = (
        center_b - structured_b * radius,
        center_b + structured_b * radius,
    )
    cubic = birth["moving_cubic"]
    c0 = float(cubic["center_value"])
    c1 = float(cubic["center_complete_first_derivative_upper"])
    c2 = float(cubic["second_derivative_upper"])
    c_interval = (
        c0 - c1 * total_radius - 0.5 * c2 * total_radius**2,
        c0 + c1 * total_radius + 0.5 * c2 * total_radius**2,
    )
    c_derivative = c1 + c2 * total_radius
    lambda_one = float(line["selected_eigenvalue_first_derivative_bound"])
    lambda_two = float(line["selected_eigenvalue_raw_Hessian_bound"])
    configuration = q_weights * center_state[37:74]
    configuration_upper = float(np.linalg.norm(configuration)) + maximum_q_weight * radius
    full_hard_flow = math.hypot(configuration_upper, hard_rate_action)
    full_hard_jacobi = math.hypot(maximum_q_weight, hard_jacobi_action)
    remainder = lambda_one * full_hard_flow
    remainder_jacobi = lambda_two * full_hard_flow + lambda_one * full_hard_jacobi
    c_upper = max(abs(value) for value in c_interval)
    b_upper = max(abs(value) for value in b_interval)
    delta_interval = (
        c_interval[0] * b_interval[0] - descriptor_upper * remainder,
        c_interval[1] * b_interval[1] + descriptor_upper * remainder,
    )
    delta_derivative = (
        b_upper * c_derivative + c_upper * structured_b
        + lambda_one * remainder + descriptor_upper * remainder_jacobi
    )
    p1 = float(birth["selected_line"]["first_variation_coefficient_upper"])
    p2 = float(birth["selected_line"]["complete_second_variation_coefficient_upper"])
    selected_action_upper = (
        center_selected_action_norm + maximum_reduced_weight * p1 * radius
        + 0.5 * maximum_reduced_weight * p2 * radius**2
    )
    selected_action_derivative = maximum_reduced_weight * (p1 + p2 * radius)
    c_lower = c_interval[0]
    delta_lower = delta_interval[0]
    if c_lower <= 0.0 or delta_lower <= 0.0:
        correction_norm = correction_jacobi = speed = jacobi = math.inf
    else:
        numerator = c_upper * full_hard_flow + remainder * selected_action_upper
        numerator_derivative = (
            c_derivative * full_hard_flow + c_upper * full_hard_jacobi
            + remainder_jacobi * selected_action_upper
            + remainder * selected_action_derivative
        )
        denominator = c_lower * delta_lower
        denominator_derivative = (
            c_derivative * max(abs(value) for value in delta_interval)
            + c_upper * delta_derivative
        )
        correction_norm = numerator / denominator
        correction_jacobi = (
            numerator_derivative / denominator
            + numerator * denominator_derivative / denominator**2
        )
        speed = selected_action_upper / c_lower + descriptor_upper * correction_norm
        jacobi = (
            float(birth["birth_limit_generator"]["full_action_ball_operator_norm_upper"])
            + descriptor_upper * correction_jacobi
        )
    coefficient = coefficient_bounds
    return {
        "total_root_relative_radius": radius,
        "matrix_center_total_radius": total_radius,
        "descriptor_fiber_lambda_upper": descriptor_upper,
        "uniform_hard_gap_lower": float(line["eigenline_gap_lower"]),
        "covariant_hard_Gronwall_exponent_upper": exponent,
        "hard_rate_action_upper": hard_rate_action,
        "hard_Jacobi_action_upper": hard_jacobi_action,
        "structured_b_psi_Lipschitz_upper": structured_b,
        "hard_remainder_upper": remainder,
        "hard_remainder_Lipschitz_upper": remainder_jacobi,
        "Delta_action_derivative_upper": delta_derivative,
        "selected_action_norm_upper": selected_action_upper,
        "fiber_cancellation_correction_norm_upper": correction_norm,
        "fiber_cancellation_correction_Jacobi_upper": correction_jacobi,
        "regularized_speed_upper": speed,
        "pole_free_regularized_Jacobi_upper": jacobi,
        "c_psi_interval": list(c_interval),
        "b_psi_interval": list(b_interval),
        "Delta_interval": list(delta_interval),
        "log_R4_interval": coefficient["root_log_R4_interval"],
        "lapse_interval": coefficient["root_lapse_interval"],
        "D_tau_log_R4_interval": coefficient["root_D_tau_log_R4_interval"],
    }


def _feasible(ball: dict[str, Any]) -> bool:
    return bool(
        float(ball["uniform_hard_gap_lower"]) > 0.0
        and math.isfinite(float(ball["hard_Jacobi_action_upper"]))
        and float(ball["c_psi_interval"][0]) > 0.0
        and float(ball["b_psi_interval"][0]) > 0.0
        and float(ball["Delta_interval"][0]) > 0.0
        and float(ball["lapse_interval"][0]) > 0.0
        and float(ball["D_tau_log_R4_interval"][0]) > 0.0
        and math.isfinite(float(ball["pole_free_regularized_Jacobi_upper"]))
    )


def uniform_gap_descriptor_fiber_ball(
    *, incoming_tube: float, parent_radius: float, base_path: float,
    descriptor_upper: float, pf: dict[str, float], line: dict[str, float],
    birth: dict[str, Any], center_state: np.ndarray, center_b: float,
    center_hard_raw_norm: float, center_selected_action_norm: float,
    weights: np.ndarray, coefficient_enclosure: Callable[..., dict[str, Any]],
    bisection_steps: int = 80,
) -> dict[str, Any]:
    tube = float(incoming_tube)
    upper = float(parent_radius)
    if not 0.0 < tube < upper:
        raise ArithmeticError("incoming uniform-gap tube must lie inside parent ball")
    coefficient = coefficient_enclosure(center_state, weights, upper)

    def build(radius: float) -> dict[str, Any]:
        return _bounds(
            radius=radius, base_path=base_path, descriptor_upper=descriptor_upper,
            pf=pf, line=line, birth=birth, center_state=center_state,
            center_b=center_b, center_hard_raw_norm=center_hard_raw_norm,
            center_selected_action_norm=center_selected_action_norm,
            weights=weights, coefficient_bounds=coefficient,
        )

    lower = math.nextafter(tube, upper)
    if not _feasible(build(lower)):
        raise ArithmeticError("uniform-gap inequalities fail at incoming tube")
    upper_probe = math.nextafter(upper, 0.0)
    if _feasible(build(upper_probe)):
        feasible_upper = upper_probe
    else:
        feasible, infeasible = lower, upper_probe
        for _ in range(bisection_steps):
            midpoint = 0.5 * (feasible + infeasible)
            if midpoint in (feasible, infeasible):
                break
            if _feasible(build(midpoint)):
                feasible = midpoint
            else:
                infeasible = midpoint
        feasible_upper = feasible
    selected = 0.5 * (tube + feasible_upper)
    ball = build(selected)
    if not tube < selected < feasible_upper or not _feasible(ball):
        raise ArithmeticError("derived uniform-gap midpoint ball is not feasible")
    return {
        **ball,
        "incoming_endpoint_tube_radius": tube,
        "joint_feasibility_upper_radius": feasible_upper,
        "selected_midpoint_radius": selected,
        "incoming_tube_slack": selected - tube,
        "feasibility_slack": feasible_upper - selected,
        "uniform_gap_used_once": True,
        "redundant_center_Neumann_denominator_used": False,
    }


__all__ = ["uniform_gap_descriptor_fiber_ball"]
