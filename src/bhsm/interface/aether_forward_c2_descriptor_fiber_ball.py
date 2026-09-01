"""Fixed-descriptor C2 balls preserving the exact birth-limit cancellation."""

from __future__ import annotations

import math
from typing import Any, Callable

import numpy as np

from bhsm.interface.aether_forward_c2_descriptor_cover import metric_data


def _fiber_bounds(
    *, radius: float, descriptor_upper: float, pf: dict[str, float],
    launch: dict[str, Any], line: dict[str, float],
    center_c: tuple[float, float], center_b: tuple[float, float],
    center_selected_action_norm: float, center_state: np.ndarray,
    weights: np.ndarray, coefficient_bounds: dict[str, Any],
) -> dict[str, Any]:
    q_weights, _, maximum_q_weight, maximum_reduced_weight = metric_data()
    hard_inverse = 1.0 / float(line["eigenline_gap_lower"])
    hard_D3 = float(pf["hard_D3_center"]) + float(
        pf["D4_full_hard_hard_upper"]
    ) * radius
    hard_self = hard_inverse * hard_D3 * radius
    hard_denominator = 1.0 - hard_self
    rhs_derivative = float(pf["rhs_raw_derivative_center"]) + float(
        pf["rhs_raw_second_derivative_upper"]
    ) * radius
    projector_derivative = 2.0 * float(
        line["weighted_selected_to_complement_first_variation_on_ball"]
    )
    center_hard = float(pf["center_hard_rate_raw_norm"])
    coupling = float(pf["coupling_center"]) + float(
        pf["D4_full_selected_hard_upper"]
    ) * radius
    b_center_upper = max(abs(value) for value in center_b)
    if hard_denominator <= 0.0:
        hard_jacobi_raw = hard_rate_raw = structured_b = math.inf
        b_fixed_denominator = -math.inf
    else:
        H = hard_inverse / hard_denominator
        C = coupling + descriptor_upper * projector_derivative
        feedback = radius**2 * C * H * projector_derivative
        b_fixed_denominator = 1.0 - feedback
        affine = b_center_upper + radius * (
            rhs_derivative + C * (
                center_hard
                + radius * H * (rhs_derivative + hard_D3 * center_hard)
            )
        )
        b_upper_seed = (
            affine / b_fixed_denominator if b_fixed_denominator > 0.0 else math.inf
        )
        hard_jacobi_raw = hard_inverse * (
            rhs_derivative + hard_D3 * center_hard
            + projector_derivative * b_upper_seed
        ) / hard_denominator
        hard_rate_raw = center_hard + hard_jacobi_raw * radius
        structured_b = rhs_derivative + C * hard_rate_raw

    c_lipschitz = float(launch["c_psi_Lipschitz_upper"])
    c_interval = (
        float(center_c[0]) - c_lipschitz * radius,
        float(center_c[1]) + c_lipschitz * radius,
    )
    b_interval = (
        float(center_b[0]) - structured_b * radius,
        float(center_b[1]) + structured_b * radius,
    )
    lambda_lipschitz = float(line["selected_eigenvalue_first_derivative_bound"])
    lambda_hessian = float(line["selected_eigenvalue_raw_Hessian_bound"])
    hard_rate_action = maximum_reduced_weight * hard_rate_raw
    hard_jacobi_action = maximum_reduced_weight * hard_jacobi_raw
    configuration = q_weights * center_state[37:74]
    configuration_upper = float(np.linalg.norm(configuration)) + maximum_q_weight * radius
    full_hard_flow = math.hypot(configuration_upper, hard_rate_action)
    full_hard_jacobi = math.hypot(maximum_q_weight, hard_jacobi_action)
    remainder = lambda_lipschitz * full_hard_flow
    remainder_lipschitz = (
        lambda_hessian * full_hard_flow + lambda_lipschitz * full_hard_jacobi
    )
    c_upper = max(abs(value) for value in c_interval)
    b_upper = max(abs(value) for value in b_interval)
    delta_interval = (
        c_interval[0] * b_interval[0] - descriptor_upper * remainder,
        c_interval[1] * b_interval[1] + descriptor_upper * remainder,
    )
    delta_lipschitz = (
        b_upper * c_lipschitz + c_upper * structured_b
        + lambda_lipschitz * remainder
        + descriptor_upper * remainder_lipschitz
    )
    line_lipschitz_action = maximum_reduced_weight * float(
        line["weighted_selected_to_complement_first_variation_on_ball"]
    )
    selected_action_upper = (
        float(center_selected_action_norm) + line_lipschitz_action * radius
    )

    c_lower = c_interval[0]
    delta_lower = delta_interval[0]
    if c_lower <= 0.0 or delta_lower <= 0.0:
        speed = jacobi = correction_norm = correction_jacobi = math.inf
    else:
        # Exact cancellation:
        # F_s = Psi/c + s*(c*V_hard-R*Psi)/(c*Delta).
        correction_numerator = (
            c_upper * full_hard_flow + remainder * selected_action_upper
        )
        correction_numerator_lipschitz = (
            c_lipschitz * full_hard_flow
            + c_upper * full_hard_jacobi
            + remainder_lipschitz * selected_action_upper
            + remainder * line_lipschitz_action
        )
        correction_denominator_lower = c_lower * delta_lower
        correction_denominator_lipschitz = (
            c_lipschitz * max(abs(value) for value in delta_interval)
            + c_upper * delta_lipschitz
        )
        correction_norm = correction_numerator / correction_denominator_lower
        correction_jacobi = (
            correction_numerator_lipschitz / correction_denominator_lower
            + correction_numerator * correction_denominator_lipschitz
            / correction_denominator_lower**2
        )
        birth_speed = selected_action_upper / c_lower
        birth_jacobi = (
            line_lipschitz_action / c_lower
            + selected_action_upper * c_lipschitz / c_lower**2
        )
        speed = birth_speed + descriptor_upper * correction_norm
        jacobi = birth_jacobi + descriptor_upper * correction_jacobi

    coefficient = coefficient_bounds
    return {
        "total_root_relative_radius": radius,
        "descriptor_fiber_lambda_upper": descriptor_upper,
        "hard_self_consistency": hard_self,
        "hard_self_consistency_denominator_lower": hard_denominator,
        "b_fixed_point_denominator_lower": b_fixed_denominator,
        "hard_rate_action_upper": hard_rate_action,
        "hard_Jacobi_action_upper": hard_jacobi_action,
        "structured_b_psi_Lipschitz_upper": structured_b,
        "hard_remainder_upper": remainder,
        "hard_remainder_Lipschitz_upper": remainder_lipschitz,
        "Delta_action_derivative_upper": delta_lipschitz,
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
        0.0 < float(ball["hard_self_consistency"]) < 1.0
        and float(ball["b_fixed_point_denominator_lower"]) > 0.0
        and float(ball["c_psi_interval"][0]) > 0.0
        and float(ball["b_psi_interval"][0]) > 0.0
        and float(ball["Delta_interval"][0]) > 0.0
        and float(ball["lapse_interval"][0]) > 0.0
        and float(ball["D_tau_log_R4_interval"][0]) > 0.0
        and math.isfinite(float(ball["pole_free_regularized_Jacobi_upper"]))
    )


def fresh_center_descriptor_fiber_ball(
    *, incoming_tube: float, parent_radius: float, descriptor_upper: float,
    pf: dict[str, float], launch: dict[str, Any], line: dict[str, float],
    center_c: tuple[float, float], center_b: tuple[float, float],
    center_selected_action_norm: float, center_state: np.ndarray,
    weights: np.ndarray, coefficient_enclosure: Callable[..., dict[str, Any]],
    bisection_steps: int = 80,
) -> dict[str, Any]:
    tube = float(incoming_tube)
    upper = float(parent_radius)
    if not 0.0 < tube < upper:
        raise ArithmeticError("incoming fiber tube must lie inside parent ball")
    coefficient = coefficient_enclosure(center_state, weights, upper)

    def build(radius: float) -> dict[str, Any]:
        return _fiber_bounds(
            radius=radius, descriptor_upper=descriptor_upper, pf=pf,
            launch=launch, line=line, center_c=center_c, center_b=center_b,
            center_selected_action_norm=center_selected_action_norm,
            center_state=center_state, weights=weights,
            coefficient_bounds=coefficient,
        )

    lower_probe = math.nextafter(tube, upper)
    if not _feasible(build(lower_probe)):
        raise ArithmeticError("descriptor-fiber inequalities fail at incoming tube")
    upper_probe = math.nextafter(upper, 0.0)
    if _feasible(build(upper_probe)):
        feasible_upper = upper_probe
    else:
        feasible = lower_probe
        infeasible = upper_probe
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
        raise ArithmeticError("derived descriptor-fiber midpoint ball is not feasible")
    return {
        **ball,
        "incoming_endpoint_tube_radius": tube,
        "joint_feasibility_upper_radius": feasible_upper,
        "selected_midpoint_radius": selected,
        "incoming_tube_slack": selected - tube,
        "feasibility_slack": feasible_upper - selected,
        "exact_fixed_s_cancellation_used": True,
    }


__all__ = ["fresh_center_descriptor_fiber_ball"]
