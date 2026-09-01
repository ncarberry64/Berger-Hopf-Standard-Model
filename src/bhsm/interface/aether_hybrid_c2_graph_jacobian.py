"""Retained-center/JAX-third-tensor C2 graph Jacobian accelerator.

The base action gradient and Hessian are evaluated by the retained 96-point
Jet.  Only their state derivative is supplied by the separately
cross-validated JAX third tensor.  This module is predictor/reconnaissance
machinery until its assembled graph Jacobian is compared with the retained
98-direction complex-step construction.
"""

from __future__ import annotations

import jax.numpy as jnp
import numpy as np

from bhsm.interface.aether_forward_c2_descriptor_cover import metric_data
from bhsm.interface.aether_jax_full_local_action import action_third_tensor
from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (
    exact_full_action_jet_at_state,
)


QDIM = 37


def graph_jacobian_action(
    state: np.ndarray,
    weights: np.ndarray,
    reference: np.ndarray,
    signed_descriptor: float,
    *,
    include_fixed_descriptor_decomposition: bool = False,
    cancelled_field_action: np.ndarray | None = None,
) -> dict[str, object]:
    y = np.asarray(state, dtype=float)
    w = np.asarray(weights, dtype=float)
    ref = np.asarray(reference, dtype=float)
    s = float(signed_descriptor)
    q_weights, reduced_weights, _, _ = metric_data()
    jet = exact_full_action_jet_at_state(
        12, y[:QDIM], y[QDIM:2 * QDIM], y[2 * QDIM:], points=96,
    )
    gradient_raw = np.asarray(jet.gradient, dtype=float)
    hessian_raw = np.asarray(jet.hessian, dtype=float)
    reduced_hessian = hessian_raw[QDIM:, QDIM:]
    values, vectors = np.linalg.eigh(reduced_hessian)
    selected = int(np.argmax(np.abs(vectors.T @ ref)))
    psi = vectors[:, selected]
    if float(psi @ ref) < 0.0:
        psi = -psi
    hard_indices = np.asarray([i for i in range(values.size) if i != selected])
    complement = vectors[:, hard_indices]
    hard_values = values[hard_indices]
    eigenvalue = float(values[selected])
    denominators = hard_values - eigenvalue
    K = np.block([
        [reduced_hessian - eigenvalue * np.eye(values.size), psi[:, None]],
        [psi[None, :], np.zeros((1, 1))],
    ])
    hessian_action = hessian_raw / w[:, None] / w[None, :]
    gradient_action = gradient_raw / w
    configuration = q_weights * y[QDIM:2 * QDIM]
    rhs = reduced_weights * (
        np.concatenate((
            q_weights * gradient_action[:QDIM],
            np.zeros(reduced_weights.size - QDIM),
        )) - hessian_action[QDIM:, :QDIM] @ configuration
    )
    response = np.linalg.solve(K, np.concatenate((rhs, np.zeros(1))))
    hard = response[:-1]
    b_psi = float(response[-1])

    third = np.asarray(action_third_tensor(jnp.asarray(y)), dtype=float)
    # Enforce the exact permutation symmetries of an action third derivative.
    third = sum(
        np.transpose(third, axes)
        for axes in (
            (0, 1, 2), (0, 2, 1), (1, 0, 2),
            (1, 2, 0), (2, 0, 1), (2, 1, 0),
        )
    ) / 6.0
    total = y.size
    lambda_first = np.empty(total)
    psi_first = np.empty((psi.size, total))
    response_first = np.empty((response.size, total))
    for column in range(total):
        reduced_first = third[QDIM:, QDIM:, column] / w[column]
        slope = float(psi @ reduced_first @ psi)
        lambda_first[column] = slope
        coupling = complement.T @ reduced_first @ psi
        dpsi = complement @ (coupling / (eigenvalue - hard_values))
        psi_first[:, column] = dpsi

        dgradient_raw = hessian_raw[:, column] / w[column]
        dgradient_action = dgradient_raw / w
        dhessian_action = (
            third[:, :, column] / w[column]
            / w[:, None] / w[None, :]
        )
        dconfiguration = np.zeros(QDIM)
        if QDIM <= column < 2 * QDIM:
            local = column - QDIM
            dconfiguration[local] = q_weights[local] / w[column]
        drhs = reduced_weights * (
            np.concatenate((
                q_weights * dgradient_action[:QDIM],
                np.zeros(reduced_weights.size - QDIM),
            ))
            - dhessian_action[QDIM:, :QDIM] @ configuration
            - hessian_action[QDIM:, :QDIM] @ dconfiguration
        )
        dK = np.block([
            [reduced_first - slope * np.eye(values.size), dpsi[:, None]],
            [dpsi[None, :], np.zeros((1, 1))],
        ])
        response_first[:, column] = np.linalg.solve(
            K, np.concatenate((drhs, np.zeros(1))) - dK @ response,
        )

    configuration_first = np.zeros((QDIM, total))
    configuration_first[:, QDIM:2 * QDIM] = np.diag(
        q_weights / w[QDIM:2 * QDIM]
    )
    hard_first = response_first[:-1]
    b_first = response_first[-1]
    G = np.concatenate((
        s * configuration,
        reduced_weights * (b_psi * psi + s * hard),
    ))
    G_first = np.vstack((
        s * configuration_first + np.outer(configuration, lambda_first),
        reduced_weights[:, None] * (
            np.outer(psi, b_first)
            + b_psi * psi_first
            + np.outer(hard, lambda_first)
            + s * hard_first
        ),
    ))
    predictor_norm = float(np.linalg.norm(G))
    normalization_field = (
        G if cancelled_field_action is None
        else np.asarray(cancelled_field_action, dtype=float)
    )
    if normalization_field.shape != (total,):
        raise ValueError("cancelled_field_action must have shape (98,)")
    norm = float(np.linalg.norm(normalization_field))
    if not np.isfinite(norm) or norm <= 0.0:
        raise ValueError("cancelled_field_action must have positive finite norm")
    flow = normalization_field / norm
    jacobian = (np.eye(total) - np.outer(flow, flow)) @ G_first / norm
    result = {
        "selected_branch": selected,
        "selected_eigenline_gap": float(np.min(np.abs(denominators))),
        "b_psi": b_psi,
        "cancelled_field_action_norm": norm,
        "predictor_cancelled_field_action_norm": predictor_norm,
        "descriptor_gradient_action": lambda_first,
        "graph_Jacobian_action": jacobian,
        "third_tensor_realization": "SYMMETRIZED_JAX_PREDICTOR",
    }
    if include_fixed_descriptor_decomposition:
        descriptor_numerator_partial = np.concatenate((
            configuration,
            reduced_weights * hard,
        ))
        fixed_descriptor_numerator_first = (
            G_first - np.outer(descriptor_numerator_partial, lambda_first)
        )
        descriptor_column = (
            np.eye(total) - np.outer(flow, flow)
        ) @ descriptor_numerator_partial / norm
        result.update({
            "fixed_descriptor_state_Jacobian_action": (
                jacobian - np.outer(descriptor_column, lambda_first)
            ),
            "state_rate_descriptor_column": descriptor_column,
            "cancelled_norm_state_gradient_action": (
                flow @ fixed_descriptor_numerator_first
            ),
            "cancelled_norm_descriptor_derivative": float(
                flow @ descriptor_numerator_partial
            ),
        })
    return result


__all__ = ["graph_jacobian_action"]
