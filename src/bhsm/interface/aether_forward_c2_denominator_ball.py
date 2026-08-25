"""Fresh-center C2 proof balls using the exact hard denominator condition."""

from __future__ import annotations

import math
from typing import Any, Callable

import numpy as np

from bhsm.interface.aether_forward_c2_descriptor_cover import metric_data


def _centered_bounds(
    *, radius: float, pf: dict[str, float], launch: dict[str, Any],
    line: dict[str, float], center_c: tuple[float, float], center_b: tuple[float, float],
    center_lambda: float, center_state: np.ndarray, weights: np.ndarray,
    coefficient_bounds: dict[str, Any],
) -> dict[str, Any]:
    """Evaluate all retained local inequalities on a fresh-centered ball."""

    q_weights, _, maximum_q_weight, maximum_reduced_weight = metric_data()
    hard_inverse = 1.0 / float(line["eigenline_gap_lower"])
    hard_D3 = (
        float(pf["hard_D3_center"])
        + float(pf["D4_full_hard_hard_upper"]) * radius
    )
    self_consistency = hard_inverse * hard_D3 * radius
    denominator = 1.0 - self_consistency
    rhs_derivative = (
        float(pf["rhs_raw_derivative_center"])
        + float(pf["rhs_raw_second_derivative_upper"]) * radius
    )
    projector_derivative = 2.0 * float(
        line["weighted_selected_to_complement_first_variation_on_ball"]
    )
    center_hard = float(pf["center_hard_rate_raw_norm"])
    lambda_lipschitz = float(line["selected_eigenvalue_first_derivative_bound"])
    lambda_upper = center_lambda + lambda_lipschitz * radius
    coupling = (
        float(pf["coupling_center"])
        + float(pf["D4_full_selected_hard_upper"]) * radius
    )
    b_center_upper = max(abs(value) for value in center_b)
    if denominator <= 0.0:
        hard_jacobi_raw = math.inf
        hard_rate_raw = math.inf
        structured_b = math.inf
        b_fixed_point_denominator = -math.inf
    else:
        # Close the scalar monotone feedback exactly.  The hard Jacobi bound
        # depends on the ball supremum of b, while the b Lipschitz bound
        # depends on that hard Jacobi bound.  Both dependencies are affine.
        H = hard_inverse / denominator
        C = coupling + lambda_upper * projector_derivative
        b_feedback = radius**2 * C * H * projector_derivative
        b_fixed_point_denominator = 1.0 - b_feedback
        b_affine = b_center_upper + radius * (
            rhs_derivative
            + C * (
                center_hard
                + radius * H * (rhs_derivative + hard_D3 * center_hard)
            )
        )
        b_seed_upper = (
            b_affine / b_fixed_point_denominator
            if b_fixed_point_denominator > 0.0 else math.inf
        )
        hard_jacobi_raw = hard_inverse * (
            rhs_derivative + hard_D3 * center_hard
            + projector_derivative * b_seed_upper
        ) / denominator
        hard_rate_raw = center_hard + hard_jacobi_raw * radius
        structured_b = (
            rhs_derivative
            + (coupling + lambda_upper * projector_derivative) * hard_rate_raw
        )
    c_lipschitz = float(launch["c_psi_Lipschitz_upper"])
    c_interval = (
        float(center_c[0]) - c_lipschitz * radius,
        float(center_c[1]) + c_lipschitz * radius,
    )
    b_interval = (
        float(center_b[0]) - structured_b * radius,
        float(center_b[1]) + structured_b * radius,
    )
    hard_rate_action = maximum_reduced_weight * hard_rate_raw
    lambda_hessian = float(line["selected_eigenvalue_raw_Hessian_bound"])
    configuration_center = q_weights * center_state[37:74]
    configuration_upper = (
        float(np.linalg.norm(configuration_center)) + maximum_q_weight * radius
    )
    hard_flow = math.hypot(configuration_upper, hard_rate_action)
    remainder = lambda_lipschitz * hard_flow
    hard_jacobi_action = maximum_reduced_weight * hard_jacobi_raw
    hard_flow_jacobi = math.hypot(maximum_q_weight, hard_jacobi_action)
    remainder_lipschitz = (
        lambda_hessian * hard_flow + lambda_lipschitz * hard_flow_jacobi
    )
    c_upper = max(abs(value) for value in c_interval)
    b_upper = max(abs(value) for value in b_interval)
    delta_interval = (
        c_interval[0] * b_interval[0] - lambda_upper * remainder,
        c_interval[1] * b_interval[1] + lambda_upper * remainder,
    )
    delta_lipschitz = (
        b_upper * c_lipschitz + c_upper * structured_b
        + lambda_lipschitz * remainder + lambda_upper * remainder_lipschitz
    )
    selected_action_upper = maximum_reduced_weight * (
        1.0
        + float(line["weighted_selected_to_complement_first_variation_on_ball"])
        * radius
    )
    numerator = math.hypot(
        lambda_upper * configuration_upper,
        b_upper * selected_action_upper + lambda_upper * hard_rate_action,
    )
    numerator_lipschitz = (
        lambda_lipschitz * configuration_upper
        + lambda_upper * maximum_q_weight
        + structured_b * selected_action_upper
        + b_upper * maximum_reduced_weight
        * float(line["weighted_selected_to_complement_first_variation_on_ball"])
        + lambda_lipschitz * hard_rate_action
        + lambda_upper * hard_jacobi_action
    )
    delta_lower = delta_interval[0]
    if delta_lower <= 0.0:
        speed = math.inf
        jacobi = math.inf
    else:
        speed = numerator / delta_lower
        jacobi = (
            numerator_lipschitz / delta_lower
            + numerator * delta_lipschitz / delta_lower**2
        )
    coefficient = coefficient_bounds
    return {
        "total_root_relative_radius": radius,
        "hard_self_consistency": self_consistency,
        "hard_self_consistency_denominator_lower": denominator,
        "b_fixed_point_denominator_lower": b_fixed_point_denominator,
        "hard_rate_action_upper": hard_rate_action,
        "hard_Jacobi_action_upper": hard_jacobi_action,
        "structured_b_psi_Lipschitz_upper": structured_b,
        "hard_remainder_upper": remainder,
        "hard_remainder_Lipschitz_upper": remainder_lipschitz,
        "Delta_action_derivative_upper": delta_lipschitz,
        "regularized_speed_upper": speed,
        "pole_free_regularized_Jacobi_upper": jacobi,
        "center_lambda_absolute_upper": center_lambda,
        "lambda_absolute_upper": lambda_upper,
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


def fresh_center_denominator_ball(
    *, incoming_tube: float, parent_radius: float, pf: dict[str, float],
    launch: dict[str, Any], line: dict[str, float],
    center_c: tuple[float, float], center_b: tuple[float, float],
    center_lambda: float, center_state: np.ndarray, weights: np.ndarray,
    coefficient_enclosure: Callable[..., dict[str, Any]],
    bisection_steps: int = 80,
) -> dict[str, Any]:
    """Derive a ball between the incoming tube and exact feasibility loss.

    The old one-half hard self-consistency and one-half c-sign reserves were
    sufficient proof conveniences.  The actual inverse-free estimates only
    require the hard denominator, c, b, Delta, lapse, and radius rate to stay
    strictly positive.  Their joint feasibility endpoint is derived here by
    bisection; its midpoint with the incoming tube is a proof coordinate, not
    a physical parameter.
    """

    tube = float(incoming_tube)
    upper = float(parent_radius)
    if not 0.0 < tube < upper:
        raise ArithmeticError("incoming tube must lie inside the parent ball")
    # These coefficient signs are already extremely remote from zero.  Cache
    # one enclosure on the complete parent ball rather than recomputing the
    # same monotone statement at every radius-bisection probe.
    coefficient_bounds = coefficient_enclosure(center_state, weights, upper)

    def build(radius: float) -> dict[str, Any]:
        return _centered_bounds(
            radius=radius, pf=pf, launch=launch, line=line,
            center_c=center_c, center_b=center_b, center_lambda=center_lambda,
            center_state=center_state, weights=weights,
            coefficient_bounds=coefficient_bounds,
        )

    tube_probe = math.nextafter(tube, upper)
    if not _feasible(build(tube_probe)):
        raise ArithmeticError("fresh-centered inequalities fail at incoming tube")
    upper_probe = math.nextafter(upper, 0.0)
    if _feasible(build(upper_probe)):
        feasible_upper = upper_probe
    else:
        feasible = tube_probe
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
    if not tube < selected < feasible_upper:
        selected = math.nextafter(tube, feasible_upper)
    ball = build(selected)
    if not _feasible(ball):
        raise ArithmeticError("derived midpoint ball is not feasible")
    return {
        **ball,
        "incoming_endpoint_tube_radius": tube,
        "joint_feasibility_upper_radius": feasible_upper,
        "selected_midpoint_radius": selected,
        "incoming_tube_slack": selected - tube,
        "feasibility_slack": feasible_upper - selected,
        "bisection_steps": bisection_steps,
        "hard_half_margin_imposed": False,
        "c_half_margin_imposed": False,
    }


__all__ = ["fresh_center_denominator_ball"]
