"""Derive the ordered-event Hessian from the isolated eigenpair response.

The physical event is unchanged: lambda_6 of the terminal Euler--Dirac
Hessian.  This module differentiates that simple eigenpair explicitly and
then applies the exact terminal SBP/period pullback.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_action_curvature_square_kkt_proposal_v18_16 import (
    _action_curvature_transform,
)
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import (
    deterministic_json,
)
from bhsm.interface.aether_n3_natural_radius_scan_v21_04 import (
    v21_04_selected_raw_vector,
)
from bhsm.interface.aether_n3_rayleigh_event_covector_v20_80 import (
    _event_hessian,
    _terminal_data,
    rayleigh_sbp_event_covector,
    rayleigh_square_physical_residual,
)
from bhsm.interface.aether_n3_refreshed_dual_metric_continuation_v20_99 import (
    v20_99_selected_raw_vector,
)
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import (
    M_DIMENSION,
    NODES,
    Q_DIMENSION,
    event_gradient_indices,
    kkt_variable_scales,
)
from bhsm.interface.aether_n3_residual_manifold_normal_acceleration_v21_06 import (
    _current_square_response,
)
from bhsm.interface.aether_n3_terminal_derivative_owner_audit_v21_09 import (
    _components,
)


VERSION = "v21.17"
CLASSIFICATION = "BHSM_N3_ISOLATED_EIGENPAIR_ORDERED_EVENT_HESSIAN"
FULL_BHSM_COMPLETE = False
FIRST_DERIVATIVE_RELATIVE_STEP = 1.0e-4
SECOND_DERIVATIVE_RELATIVE_STEPS = (3.0e-4, 1.0e-3, 3.0e-3)
EXACT_RESPONSE_STEP = 1.0e-5


def _local_eigenpair_hessian(
    local: np.ndarray, *, second_relative_step: float,
) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    """Return grad(lambda_6), Hess(lambda_6), and an eigenpair audit."""
    center = np.asarray(local, dtype=float)
    matrix = _event_hessian(center)
    eigenvalues, eigenvectors = np.linalg.eigh(matrix)
    selected = 6
    eigenvalue = float(eigenvalues[selected])
    vector = eigenvectors[:, selected]
    if not (eigenvalues[5] < eigenvalue < eigenvalues[7]):
        raise ValueError("ordered event eigenvalue is not isolated")

    first_steps = FIRST_DERIVATIVE_RELATIVE_STEP * np.maximum(1.0, np.abs(center))
    second_steps = second_relative_step * np.maximum(1.0, np.abs(center))

    first_derivatives = np.empty((center.size, matrix.shape[0], matrix.shape[1]))
    for index, step in enumerate(first_steps):
        delta = np.zeros_like(center)
        delta[index] = step
        first_derivatives[index] = (
            -_event_hessian(center + 2.0 * delta)
            + 8.0 * _event_hessian(center + delta)
            - 8.0 * _event_hessian(center - delta)
            + _event_hessian(center - 2.0 * delta)
        ) / (12.0 * step)

    gradient = np.einsum("a,iab,b->i", vector, first_derivatives, vector)

    # Fixed-central-mode contraction of D^2 H.  Keeping the eigenvector fixed
    # here prevents double counting; its response is added analytically below.
    def projected_hessian(value: np.ndarray) -> float:
        return float(vector @ _event_hessian(value) @ vector)

    fixed_mode = np.empty((center.size, center.size))
    central_value = projected_hessian(center)
    for left, step in enumerate(second_steps):
        delta = np.zeros_like(center)
        delta[left] = step
        fixed_mode[left, left] = (
            -projected_hessian(center + 2.0 * delta)
            + 16.0 * projected_hessian(center + delta)
            - 30.0 * central_value
            + 16.0 * projected_hessian(center - delta)
            - projected_hessian(center - 2.0 * delta)
        ) / (12.0 * step**2)
    for left in range(center.size):
        left_delta = np.zeros_like(center)
        left_delta[left] = second_steps[left]
        for right in range(left + 1, center.size):
            right_delta = np.zeros_like(center)
            right_delta[right] = second_steps[right]
            mixed = (
                projected_hessian(center + left_delta + right_delta)
                - projected_hessian(center + left_delta - right_delta)
                - projected_hessian(center - left_delta + right_delta)
                + projected_hessian(center - left_delta - right_delta)
            ) / (4.0 * second_steps[left] * second_steps[right])
            fixed_mode[left, right] = mixed
            fixed_mode[right, left] = mixed

    couplings = np.einsum(
        "ka,iab,b->ki", eigenvectors.T, first_derivatives, vector
    )
    denominators = eigenvalue - eigenvalues
    mask = np.arange(eigenvalues.size) != selected
    eigenvector_response = 2.0 * (
        couplings[mask].T
        @ ((1.0 / denominators[mask])[:, None] * couplings[mask])
    )
    hessian = fixed_mode + eigenvector_response
    hessian = 0.5 * (hessian + hessian.T)
    return gradient, hessian, {
        "ordered_index": selected,
        "eigenvalue": eigenvalue,
        "lower_gap": float(eigenvalue - eigenvalues[5]),
        "upper_gap": float(eigenvalues[7] - eigenvalue),
        "eigenpair_residual_l2": float(
            np.linalg.norm(matrix @ vector - eigenvalue * vector)
        ),
        "first_derivative_relative_step": FIRST_DERIVATIVE_RELATIVE_STEP,
        "second_derivative_relative_step": second_relative_step,
        "fixed_mode_second_derivative_l2": float(np.linalg.norm(fixed_mode)),
        "eigenvector_response_l2": float(np.linalg.norm(eigenvector_response)),
        "local_event_hessian_l2": float(np.linalg.norm(hessian)),
        "local_event_hessian_symmetry_residual": float(
            np.linalg.norm(hessian - hessian.T) / max(np.linalg.norm(hessian), 1.0)
        ),
    }


def _terminal_pullback(
    gradient: np.ndarray, local_hessian: np.ndarray, raw: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Pull the local event gradient/Hessian to the 37-row raw support."""
    support = np.asarray(event_gradient_indices(), dtype=int)
    _, _, period, difference, local = _terminal_data(raw[:-1])
    terminal_velocity = local[Q_DIMENSION:2 * Q_DIMENSION]
    pullback = np.zeros((2 * Q_DIMENSION + M_DIMENSION, support.size))

    previous = Q_DIMENSION
    terminal = 2 * Q_DIMENSION
    multiplier = 3 * Q_DIMENSION
    period_position = support.size - 1
    pullback[:Q_DIMENSION, terminal:terminal + Q_DIMENSION] = np.eye(Q_DIMENSION)
    pullback[Q_DIMENSION:2 * Q_DIMENSION, previous:previous + Q_DIMENSION] = (
        difference[-1, NODES - 2] / period * np.eye(Q_DIMENSION)
    )
    pullback[Q_DIMENSION:2 * Q_DIMENSION, terminal:terminal + Q_DIMENSION] = (
        difference[-1, NODES - 1] / period * np.eye(Q_DIMENSION)
    )
    pullback[2 * Q_DIMENSION:, multiplier:multiplier + M_DIMENSION] = np.eye(M_DIMENSION)
    pullback[Q_DIMENSION:2 * Q_DIMENSION, period_position] = -terminal_velocity / period

    support_gradient = pullback.T @ gradient
    support_hessian = pullback.T @ local_hessian @ pullback
    velocity_gradient = gradient[Q_DIMENSION:2 * Q_DIMENSION]
    for coordinate in range(Q_DIMENSION):
        previous_position = previous + coordinate
        terminal_position = terminal + coordinate
        support_hessian[previous_position, period_position] += (
            -difference[-1, NODES - 2] / period**2 * velocity_gradient[coordinate]
        )
        support_hessian[period_position, previous_position] = support_hessian[
            previous_position, period_position
        ]
        support_hessian[terminal_position, period_position] += (
            -difference[-1, NODES - 1] / period**2 * velocity_gradient[coordinate]
        )
        support_hessian[period_position, terminal_position] = support_hessian[
            terminal_position, period_position
        ]
    support_hessian[period_position, period_position] += float(
        2.0 * velocity_gradient @ terminal_velocity / period**2
    )
    return support, support_gradient, support_hessian


def completion_payload() -> dict[str, Any]:
    raw = v21_04_selected_raw_vector()
    scales = kkt_variable_scales()
    y = raw * scales
    residual = rayleigh_square_physical_residual(y)
    source_norm = float(np.linalg.norm(residual))
    local = _terminal_data(raw[:-1])[-1]

    local_results = []
    scaled_blocks = []
    scaled_gradients = []
    support = None
    for relative_step in SECOND_DERIVATIVE_RELATIVE_STEPS:
        gradient, local_hessian, eigenpair = _local_eigenpair_hessian(
            local, second_relative_step=relative_step
        )
        support, support_gradient, raw_block = _terminal_pullback(
            gradient, local_hessian, raw
        )
        support_scales = scales[:-1][support]
        scaled_gradient = support_gradient / support_scales / scales[-1]
        scaled_block = (
            raw_block / support_scales[:, None] / support_scales[None, :] / scales[-1]
        )
        scaled_gradients.append(scaled_gradient)
        scaled_blocks.append(scaled_block)
        local_results.append(eigenpair)

    assert support is not None
    selected = 1
    block = scaled_blocks[selected]
    event_gradient = rayleigh_sbp_event_covector(raw[:-1]) / scales[:-1] / scales[-1]
    derived_gradient = np.zeros(375)
    derived_gradient[support] = scaled_gradients[selected]
    gradient_relative = float(
        np.linalg.norm(derived_gradient - event_gradient)
        / max(np.linalg.norm(event_gradient), 1.0)
    )

    prior = json.loads(Path(
        "artifacts/BHSM_N3_RESIDUAL_MANIFOLD_NORMAL_ACCELERATION_V21_06.json"
    ).read_text(encoding="utf-8"))["curvature_refresh"]
    old_matrix = _current_square_response(raw, prior)
    transform, transform_audit = _action_curvature_transform(raw)
    gradient_x = transform.T @ old_matrix.T @ residual
    current_direction = transform @ (-gradient_x / np.linalg.norm(gradient_x))
    terminal_scale_v = np.zeros(376)
    owner_coordinates = {0, 7, 8, 9}
    for index in support[:3 * Q_DIMENSION]:
        if int(index) % Q_DIMENSION in owner_coordinates:
            terminal_scale_v[int(index)] = current_direction[int(index)]
    terminal_scale_v[-1] = current_direction[-1]
    directions = {
        "negative_current_merit_gradient": current_direction,
        "terminal_scale_v_owner_projection": terminal_scale_v,
        "exact_physical_residual": residual,
        "latest_accepted_secant": (raw - v20_99_selected_raw_vector()) * scales,
    }

    full_event_hessian = np.zeros((375, 375))
    full_event_hessian[np.ix_(support, support)] = block
    direction_checks = []
    for name, direction in directions.items():
        direction = np.asarray(direction, dtype=float)
        norm = float(np.linalg.norm(direction))
        unit = direction / norm
        exact_responses = []
        for factor in (0.5, 1.0, 2.0):
            step = factor * EXACT_RESPONSE_STEP
            _, plus = _components(y + step * unit, scales)
            _, minus = _components(y - step * unit, scales)
            exact_responses.append(norm * (plus - minus) / (2.0 * step))
        exact = exact_responses[1]
        predicted = np.empty(376)
        predicted[:-1] = (
            y[-1] * (full_event_hessian @ direction[:-1])
            + direction[-1] * event_gradient
        )
        predicted[-1] = float(event_gradient @ direction[:-1])
        denominator = max(float(np.linalg.norm(exact)), 1.0)
        step_actions = [
            float(np.linalg.norm((candidate - block) @ direction[support]))
            / max(float(np.linalg.norm(block @ direction[support])), 1.0)
            for candidate in scaled_blocks
        ]
        exact_stable = bool(
            np.linalg.norm(exact_responses[0] - exact) / denominator < 1.0e-2
            and np.linalg.norm(exact_responses[2] - exact) / denominator < 1.0e-2
        )
        direction_checks.append({
            "direction": name,
            "exact_response_l2": float(np.linalg.norm(exact)),
            "derived_response_l2": float(np.linalg.norm(predicted)),
            "derived_vs_exact_relative": float(
                np.linalg.norm(predicted - exact) / denominator
            ),
            "exact_half_vs_reference_relative": float(
                np.linalg.norm(exact_responses[0] - exact) / denominator
            ),
            "exact_double_vs_reference_relative": float(
                np.linalg.norm(exact_responses[2] - exact) / denominator
            ),
            "exact_reference_step_stable": exact_stable,
            "relative_block_action_difference_by_second_step": step_actions,
        })

    stable_checks = [
        row for row in direction_checks if row["exact_reference_step_stable"]
    ]
    max_exact_mismatch = max(
        row["derived_vs_exact_relative"] for row in stable_checks
    )
    max_step_instability = max(
        max(row["relative_block_action_difference_by_second_step"])
        for row in direction_checks
    )
    result = {
        "source_frontier": {"version": "v21.04", "exact_rayleigh_f376_l2": source_norm},
        "derivation": {
            "formula": "vT_Hij_v+2_SUM_k_ne_6[(ukT_Hi_v)(ukT_Hj_v)/(lambda6-lambdak)]",
            "isolated_eigenvector_response_included": True,
            "terminal_SBP_and_period_second_pullback_included": True,
            "local_step_audits": local_results,
            "selected_second_derivative_relative_step": SECOND_DERIVATIVE_RELATIVE_STEPS[selected],
            "scaled_gradient_vs_validated_rayleigh_covector_relative": gradient_relative,
            "maximum_directional_block_step_instability": max_step_instability,
        },
        "event_curvature_support_indices": support.tolist(),
        "event_curvature_symmetric_block": block.tolist(),
        "directional_validation": direction_checks,
        "stable_direction_count": len(stable_checks),
        "maximum_stable_derived_vs_exact_event_response_relative": max_exact_mismatch,
        "coordinate_map": transform_audit,
        "classification": (
            "ISOLATED_EIGENPAIR_EVENT_HESSIAN_VALIDATED"
            if gradient_relative < 1.0e-6
            and max_step_instability < 2.0e-2
            and len(stable_checks) >= 3
            and max_exact_mismatch < 1.0e-2
            else "ISOLATED_EIGENPAIR_EVENT_HESSIAN_INVALIDATED"
        ),
        "physical_equations_changed": False,
        "event_definition_changed": False,
        "acceptance_gate_changed": False,
    }
    validation = {
        "source_v21_04_reproduced": abs(source_norm - 0.782775399601569) < 5.0e-12,
        "ordered_branch_isolated": min(
            local_results[selected]["lower_gap"], local_results[selected]["upper_gap"]
        ) > 0.0,
        "eigenpair_resolved": local_results[selected]["eigenpair_residual_l2"] < 1.0e-9,
        "complete_event_support": support.size == 37,
        "gradient_reproduces_validated_covector": gradient_relative < 1.0e-6,
        "directional_block_step_stable": max_step_instability < 2.0e-2,
        "three_stable_exact_directional_references": len(stable_checks) >= 3,
        "matches_stable_exact_event_responses": max_exact_mismatch < 1.0e-2,
        "same_physics": not result["physical_equations_changed"]
        and not result["event_definition_changed"]
        and not result["acceptance_gate_changed"],
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N3_ISOLATED_EIGENPAIR_EVENT_HESSIAN_V21_17",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "isolated_eigenpair_event_hessian": result,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_N3_ISOLATED_EIGENPAIR_EVENT_HESSIAN_V21_17.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "_local_eigenpair_hessian", "_terminal_pullback", "completion_payload", "materialize",
]
