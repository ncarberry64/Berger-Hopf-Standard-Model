"""Inverse-free helpers for translated C2 signed-descriptor flow boxes."""

from __future__ import annotations

import math
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (
    exact_full_action_jet_at_state,
)
from bhsm.interface.aether_sobolev_metric_soft_mode_lift_v16_07 import (
    spectral_frequencies,
)


QDIM = 37


def metric_data() -> tuple[np.ndarray, np.ndarray, float, float]:
    frequencies = spectral_frequencies(12)
    q_weights = np.sqrt(1.0 + frequencies["coordinates"] ** 2)
    reduced_weights = np.concatenate((
        np.ones(QDIM), np.sqrt(1.0 + frequencies["multipliers"] ** 2),
    ))
    return (
        q_weights,
        reduced_weights,
        float(np.max(q_weights)),
        float(np.max(reduced_weights)),
    )


def admissible_root_radius(
    *, pf: dict[str, float], launch_ball: dict[str, Any],
    line: dict[str, float], parent_radius: float,
) -> dict[str, float]:
    hard_inverse = 1.0 / float(line["eigenline_gap_lower"])
    d3 = float(pf["hard_D3_center"])
    d4 = float(pf["D4_full_hard_hard_upper"])
    hard_radius = (-d3 + math.sqrt(d3**2 + 2.0 * d4 / hard_inverse)) / (
        2.0 * d4
    )
    c_radius = (
        0.5 * float(launch_ball["c_psi_interval"][0])
        / float(launch_ball["c_psi_Lipschitz_upper"])
    )
    return {
        "hard_self_consistency_radius": hard_radius,
        "c_sign_radius": c_radius,
        "parent_action_radius": parent_radius,
        "admissible_radius": min(hard_radius, c_radius, parent_radius),
    }


def translated_ball_bounds(
    *, center_path: float, tube: float, pf: dict[str, float],
    launch_ball: dict[str, Any], line: dict[str, float],
    parent_radius: float, root_state: np.ndarray, weights: np.ndarray,
    coefficient_enclosure: Any,
) -> dict[str, Any]:
    roots = admissible_root_radius(
        pf=pf, launch_ball=launch_ball, line=line,
        parent_radius=parent_radius,
    )
    center_plus_tube = center_path + tube
    local_radius = 0.5 * (roots["admissible_radius"] - center_plus_tube)
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
    hard_Jacobi_raw = hard_inverse * (
        rhs_derivative + hard_D3 * center_hard
        + projector_derivative * b_upper
    ) / (1.0 - self_consistency)
    maximum_reduced_weight = float(np.max(weights[37:]))
    hard_rate_action = maximum_reduced_weight * (
        center_hard + hard_Jacobi_raw * total_radius
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
        "center_path_upper": center_path,
        "endpoint_tube_radius": tube,
        "center_path_plus_tube_offset": center_plus_tube,
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


def translated_generator(
    *, ball: dict[str, Any], pf: dict[str, float],
    launch_ball: dict[str, Any], line: dict[str, float],
    root_state: np.ndarray,
) -> dict[str, float]:
    q_weights, _, maximum_q_weight, maximum_reduced_weight = metric_data()
    total_radius = float(ball["total_root_relative_radius"])
    hard_inverse = 1.0 / float(line["eigenline_gap_lower"])
    hard_D3 = (
        float(pf["hard_D3_center"])
        + float(pf["D4_full_hard_hard_upper"]) * total_radius
    )
    denominator = 1.0 - hard_inverse * hard_D3 * total_radius
    rhs_derivative = (
        float(pf["rhs_raw_derivative_center"])
        + float(pf["rhs_raw_second_derivative_upper"]) * total_radius
    )
    projector_derivative = 2.0 * float(
        line["weighted_selected_to_complement_first_variation_on_ball"]
    )
    b_upper = max(abs(value) for value in ball["b_psi_interval"])
    center_hard = float(pf["center_hard_rate_raw_norm"])
    hard_Jacobi_raw = hard_inverse * (
        rhs_derivative + hard_D3 * center_hard
        + projector_derivative * b_upper
    ) / denominator
    hard_rate_raw = center_hard + hard_Jacobi_raw * total_radius
    hard_rate_action = maximum_reduced_weight * hard_rate_raw
    hard_Jacobi_action = maximum_reduced_weight * hard_Jacobi_raw
    lambda_lipschitz = float(line["selected_eigenvalue_first_derivative_bound"])
    lambda_hessian = float(line["selected_eigenvalue_raw_Hessian_bound"])
    lambda_upper = lambda_lipschitz * total_radius
    coupling = (
        float(pf["coupling_center"])
        + float(pf["D4_full_selected_hard_upper"]) * total_radius
    )
    structured_b = (
        rhs_derivative
        + (coupling + lambda_upper * projector_derivative) * hard_rate_raw
    )
    root_configuration = q_weights * root_state[QDIM:2 * QDIM]
    configuration_upper = (
        float(np.linalg.norm(root_configuration))
        + maximum_q_weight * total_radius
    )
    hard_flow = math.hypot(configuration_upper, hard_rate_action)
    remainder = lambda_lipschitz * hard_flow
    hard_flow_Jacobi = math.hypot(maximum_q_weight, hard_Jacobi_action)
    remainder_lipschitz = (
        lambda_hessian * hard_flow
        + lambda_lipschitz * hard_flow_Jacobi
    )
    c_upper = max(abs(value) for value in ball["c_psi_interval"])
    c_lipschitz = float(launch_ball["c_psi_Lipschitz_upper"])
    Delta_lipschitz = (
        b_upper * c_lipschitz + c_upper * structured_b
        + lambda_lipschitz * remainder
        + lambda_upper * remainder_lipschitz
    )
    selected_action_upper = (
        maximum_reduced_weight
        + maximum_reduced_weight
        * float(line["weighted_selected_to_complement_first_variation_on_ball"])
        * total_radius
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
        + lambda_upper * hard_Jacobi_action
    )
    Delta_lower = float(ball["Delta_interval"][0])
    speed = numerator / Delta_lower
    Jacobi = (
        numerator_lipschitz / Delta_lower
        + numerator * Delta_lipschitz / Delta_lower**2
    )
    return {
        "hard_self_consistency_denominator_lower": denominator,
        "hard_rate_action_upper": hard_rate_action,
        "hard_Jacobi_action_upper": hard_Jacobi_action,
        "structured_b_psi_Lipschitz_upper": structured_b,
        "hard_remainder_upper": remainder,
        "hard_remainder_Lipschitz_upper": remainder_lipschitz,
        "Delta_action_derivative_upper": Delta_lipschitz,
        "regularized_speed_upper": speed,
        "pole_free_regularized_Jacobi_upper": Jacobi,
    }


def proof_center_field(
    *, center: np.ndarray, weights: np.ndarray, reference: np.ndarray,
    signed_s: float, ball: dict[str, Any], generator: dict[str, float],
) -> dict[str, Any]:
    q_weights, reduced_weights, _, _ = metric_data()
    jet = exact_full_action_jet_at_state(
        12, center[:QDIM], center[QDIM:2 * QDIM], center[2 * QDIM:], points=96,
    )
    gradient = np.asarray(jet.gradient, dtype=float) / weights
    hessian_action = (
        np.asarray(jet.hessian, dtype=float)
        / weights[:, None] / weights[None, :]
    )
    raw_D = np.asarray(jet.hessian, dtype=float)[QDIM:, QDIM:]
    values, vectors = np.linalg.eigh(raw_D)
    selected = int(np.argmax(np.abs(vectors.T @ reference)))
    psi = vectors[:, selected]
    if float(psi @ reference) < 0.0:
        psi = -psi
    complement = np.delete(vectors, selected, axis=1)
    hard_values = np.delete(values, selected)
    configuration = q_weights * center[QDIM:2 * QDIM]
    mixed_vq = hessian_action[QDIM:QDIM + QDIM, :QDIM]
    mixed_mq = hessian_action[2 * QDIM:, :QDIM]
    rhs_action = np.concatenate((
        q_weights * gradient[:QDIM] - mixed_vq @ configuration,
        -mixed_mq @ configuration,
    ))
    rhs_raw = reduced_weights * rhs_action
    b_center = float(psi @ rhs_raw)
    hard_center = complement @ ((complement.T @ rhs_raw) / hard_values)
    c_lower, c_upper = (float(value) for value in ball["c_psi_interval"])
    c_midpoint = 0.5 * (c_lower + c_upper)
    c_halfwidth = 0.5 * (c_upper - c_lower)
    nominal_Delta = c_midpoint * b_center
    numerator = np.concatenate((
        signed_s * configuration,
        (b_center * psi + signed_s * hard_center) * reduced_weights,
    ))
    field = numerator / nominal_Delta
    mismatch = (
        float(np.linalg.norm(numerator))
        * (
            abs(b_center) * c_halfwidth
            + signed_s * float(generator["hard_remainder_upper"])
        )
        / (float(ball["Delta_interval"][0]) * nominal_Delta)
    )
    return {
        "selected_branch": selected,
        "b_psi_center": b_center,
        "c_psi_midpoint": c_midpoint,
        "nominal_Delta": nominal_Delta,
        "field_action": field,
        "field_action_norm": float(np.linalg.norm(field)),
        "field_mismatch_upper": mismatch,
    }
