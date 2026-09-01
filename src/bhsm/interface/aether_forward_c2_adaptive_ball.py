"""Derived radius allocation for translated C2 descriptor proof balls."""

from __future__ import annotations

import math
from typing import Any, Callable

import numpy as np

from bhsm.interface.aether_forward_c2_descriptor_cover import (
    admissible_root_radius,
)


def translated_ball_bounds_with_share(
    *,
    center_path: float,
    tube: float,
    local_radius_share: float,
    pf: dict[str, float],
    launch_ball: dict[str, Any],
    line: dict[str, float],
    parent_radius: float,
    root_state: np.ndarray,
    weights: np.ndarray,
    coefficient_enclosure: Callable[..., dict[str, Any]],
) -> dict[str, Any]:
    """Return the original translated-ball bounds with a supplied allocation.

    If ``A`` is the admissible root radius, the incoming center path and tube
    use ``c+r`` and the unallocated radius is ``m=A-c-r``.  The local proof
    radius is ``rho* m`` with ``0<rho<1``.  Thus the total root-relative
    radius is strictly below ``A``.  No physical equation depends on ``rho``.
    """

    share = float(local_radius_share)
    if not math.isfinite(share) or not 0.0 < share < 1.0:
        raise ValueError("strict local-radius allocation share in (0,1) required")
    roots = admissible_root_radius(
        pf=pf,
        launch_ball=launch_ball,
        line=line,
        parent_radius=parent_radius,
    )
    center_plus_tube = float(center_path) + float(tube)
    remaining = roots["admissible_radius"] - center_plus_tube
    if not remaining > 0.0:
        raise ValueError("positive unallocated root radius required")
    local_radius = share * remaining
    total_radius = center_plus_tube + local_radius
    hard_inverse = 1.0 / float(line["eigenline_gap_lower"])
    hard_D3 = (
        float(pf["hard_D3_center"])
        + float(pf["D4_full_hard_hard_upper"]) * total_radius
    )
    self_consistency = hard_inverse * hard_D3 * total_radius
    rhs_derivative = (
        float(pf["rhs_raw_derivative_center"])
        + float(pf["rhs_raw_second_derivative_upper"]) * total_radius
    )
    b_lipschitz = float(pf["structured_b_psi_Lipschitz_upper"])
    b_upper = float(launch_ball["b_psi_interval"][1]) + b_lipschitz * total_radius
    projector_derivative = 2.0 * float(
        line["weighted_selected_to_complement_first_variation_on_ball"]
    )
    center_hard = float(pf["center_hard_rate_raw_norm"])
    if not self_consistency < 1.0:
        hard_jacobi_raw = math.inf
    else:
        hard_jacobi_raw = hard_inverse * (
            rhs_derivative + hard_D3 * center_hard
            + projector_derivative * b_upper
        ) / (1.0 - self_consistency)
    maximum_reduced_weight = float(np.max(weights[37:]))
    hard_rate_action = maximum_reduced_weight * (
        center_hard + hard_jacobi_raw * total_radius
    )
    lambda_lipschitz = float(line["selected_eigenvalue_first_derivative_bound"])
    R_upper = lambda_lipschitz * hard_rate_action
    c_lipschitz = float(launch_ball["c_psi_Lipschitz_upper"])
    c_interval = (
        float(launch_ball["c_psi_interval"][0]) - c_lipschitz * total_radius,
        float(launch_ball["c_psi_interval"][1]) + c_lipschitz * total_radius,
    )
    b_interval = (
        float(launch_ball["b_psi_interval"][0]) - b_lipschitz * total_radius,
        b_upper,
    )
    lambda_upper = lambda_lipschitz * total_radius
    Delta = (
        c_interval[0] * b_interval[0] - lambda_upper * R_upper,
        c_interval[1] * b_interval[1] + lambda_upper * R_upper,
    )
    coefficient = coefficient_enclosure(root_state, weights, total_radius)
    return {
        **roots,
        "center_path_upper": float(center_path),
        "endpoint_tube_radius": float(tube),
        "center_path_plus_tube_offset": center_plus_tube,
        "unallocated_root_radius_before_share": remaining,
        "local_radius_share": share,
        "derived_local_radius": local_radius,
        "total_root_relative_radius": total_radius,
        "hard_self_consistency": self_consistency,
        "hard_rate_action_upper": hard_rate_action,
        "R_upper": R_upper,
        "c_psi_interval": list(c_interval),
        "b_psi_interval": list(b_interval),
        "Delta_interval": list(Delta),
        "log_R4_interval": coefficient["root_log_R4_interval"],
        "lapse_interval": coefficient["root_lapse_interval"],
        "D_tau_log_R4_interval": coefficient["root_D_tau_log_R4_interval"],
    }


def _flow_ball_feasible(ball: dict[str, Any], tube: float) -> bool:
    return bool(
        float(ball["derived_local_radius"]) > float(tube)
        and float(ball["hard_self_consistency"]) < 0.5
        and float(ball["c_psi_interval"][0]) > 0.0
        and float(ball["b_psi_interval"][0]) > 0.0
        and float(ball["Delta_interval"][0]) > 0.0
        and float(ball["lapse_interval"][0]) > 0.0
        and float(ball["D_tau_log_R4_interval"][0]) > 0.0
    )


def derived_adaptive_ball(
    *,
    center_path: float,
    tube: float,
    pf: dict[str, float],
    launch_ball: dict[str, Any],
    line: dict[str, float],
    parent_radius: float,
    root_state: np.ndarray,
    weights: np.ndarray,
    coefficient_enclosure: Callable[..., dict[str, Any]],
    bisection_steps: int = 64,
) -> dict[str, Any]:
    """Derive a strict midpoint allocation between necessity and feasibility.

    ``rho_min=tube/(A-center_path-tube)`` is the exact lower allocation needed
    for the next local ball to contain the incoming tube.  The upper endpoint
    is the supremum retained by monotone action-majorant checks.  The selected
    share is their midpoint, so it is derived and carries strict slack at both
    boundaries.
    """

    if bisection_steps < 16:
        raise ValueError("at least sixteen allocation bisections required")
    roots = admissible_root_radius(
        pf=pf,
        launch_ball=launch_ball,
        line=line,
        parent_radius=parent_radius,
    )
    remaining = roots["admissible_radius"] - float(center_path) - float(tube)
    if not remaining > float(tube) > 0.0:
        raise ArithmeticError("no local-radius allocation can contain the incoming tube")
    lower = float(tube) / remaining
    def build(share: float) -> dict[str, Any]:
        return translated_ball_bounds_with_share(
            center_path=center_path,
            tube=tube,
            local_radius_share=share,
            pf=pf,
            launch_ball=launch_ball,
            line=line,
            parent_radius=parent_radius,
            root_state=root_state,
            weights=weights,
            coefficient_enclosure=coefficient_enclosure,
        )

    lower_probe = lower
    lower_ball: dict[str, Any] | None = None
    for _ in range(1024):
        lower_probe = math.nextafter(lower_probe, 1.0)
        if not lower_probe < 1.0:
            break
        candidate = build(lower_probe)
        if float(candidate["derived_local_radius"]) > float(tube):
            lower_ball = candidate
            break
    if lower_ball is None:
        raise ArithmeticError(
            "no representable allocation strictly contains the incoming tube"
        )
    if not _flow_ball_feasible(lower_ball, tube):
        raise ArithmeticError("retained margins fail immediately above allocation necessity")
    upper_probe = math.nextafter(1.0, 0.0)
    upper_ball = build(upper_probe)
    if _flow_ball_feasible(upper_ball, tube):
        feasible_upper = upper_probe
    else:
        feasible = lower_probe
        infeasible = upper_probe
        for _ in range(bisection_steps):
            midpoint = 0.5 * (feasible + infeasible)
            if midpoint in (feasible, infeasible):
                break
            if _flow_ball_feasible(build(midpoint), tube):
                feasible = midpoint
            else:
                infeasible = midpoint
        feasible_upper = feasible
    selected = 0.5 * (lower + feasible_upper)
    if not lower < selected < feasible_upper:
        selected = math.nextafter(lower, feasible_upper)
    if not lower < selected < feasible_upper:
        raise ArithmeticError(
            "no representable allocation lies strictly inside the derived interval"
        )
    ball = build(selected)
    if not _flow_ball_feasible(ball, tube):
        selected = math.nextafter(feasible_upper, lower)
        if not lower < selected < feasible_upper:
            raise ArithmeticError(
                "no representable strict allocation retains all margins"
            )
        ball = build(selected)
        if not _flow_ball_feasible(ball, tube):
            raise ArithmeticError(
                "representable interior allocation failed retained margins"
            )
    return {
        **ball,
        "allocation_lower_necessity": lower,
        "allocation_feasible_upper": feasible_upper,
        "allocation_selected_midpoint": selected,
        "allocation_lower_slack": selected - lower,
        "allocation_upper_slack": feasible_upper - selected,
        "allocation_bisection_steps": bisection_steps,
    }


__all__ = [
    "derived_adaptive_ball",
    "translated_ball_bounds_with_share",
]
