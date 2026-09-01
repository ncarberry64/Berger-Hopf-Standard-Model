"""JAX predictor for the scalar row of the augmented fixed-descriptor flow.

The retained exact field remains nonlinear replay authority.  This module uses
the separately cross-validated JAX action solely to differentiate the normalized
descriptor rate, whose state derivative contains the action fourth derivative.
"""

from __future__ import annotations

import jax
import jax.numpy as jnp
import numpy as np

from bhsm.interface.aether_forward_c2_descriptor_cover import metric_data
from bhsm.interface.aether_jax_full_local_action import (
    action_value_gradient_hessian,
    action_third_tensor,
)


QDIM = 37
STATE_DIMENSION = 98
SELECTED_BRANCH = 24
_Q_WEIGHTS, _REDUCED_WEIGHTS, _, _ = metric_data()
Q_WEIGHTS = jnp.asarray(_Q_WEIGHTS)
REDUCED_WEIGHTS = jnp.asarray(_REDUCED_WEIGHTS)


def _normalized_descriptor_rate_action(
    augmented_action: jax.Array,
    weights: jax.Array,
    reference: jax.Array,
) -> jax.Array:
    state = augmented_action[:STATE_DIMENSION] / weights
    descriptor = augmented_action[STATE_DIMENSION]
    _, gradient_raw, hessian_raw = action_value_gradient_hessian(state)
    hessian_raw = 0.5 * (hessian_raw + hessian_raw.T)
    gradient_action = gradient_raw / weights
    hessian_action = hessian_raw / weights[:, None] / weights[None, :]
    reduced = hessian_raw[QDIM:, QDIM:]
    values, vectors = jnp.linalg.eigh(reduced)
    psi = vectors[:, SELECTED_BRANCH]
    orientation = jnp.where(jnp.dot(psi, reference) >= 0.0, 1.0, -1.0)
    psi = orientation * psi
    hard_indices = jnp.concatenate((
        jnp.arange(SELECTED_BRANCH),
        jnp.arange(SELECTED_BRANCH + 1, reduced.shape[0]),
    ))
    complement = vectors[:, hard_indices]
    eigenvalue = values[SELECTED_BRANCH]
    hard_values = values[hard_indices]
    configuration = Q_WEIGHTS * state[QDIM:2 * QDIM]
    rhs_action = jnp.concatenate((
        Q_WEIGHTS * gradient_action[:QDIM]
        - hessian_action[QDIM:2 * QDIM, :QDIM] @ configuration,
        -hessian_action[2 * QDIM:, :QDIM] @ configuration,
    ))
    rhs_raw = REDUCED_WEIGHTS * rhs_action
    b_psi = jnp.dot(psi, rhs_raw)
    hard_raw = complement @ (
        (complement.T @ rhs_raw) / (hard_values - eigenvalue)
    )
    psi_action = jnp.concatenate((jnp.zeros(QDIM), REDUCED_WEIGHTS * psi))
    full_hard_action = jnp.concatenate((
        configuration,
        REDUCED_WEIGHTS * hard_raw,
    ))
    third = action_third_tensor(state)

    def slope(action_direction: jax.Array) -> jax.Array:
        raw_direction = action_direction / weights
        reduced_directional = jnp.einsum(
            "ijk,k->ij", third[QDIM:, QDIM:, :], raw_direction,
        )
        return jnp.einsum("i,ij,j->", psi, reduced_directional, psi)

    c_psi = slope(psi_action)
    remainder = slope(full_hard_action)
    delta = c_psi * b_psi + descriptor * remainder
    numerator = jnp.concatenate((
        descriptor * configuration,
        REDUCED_WEIGHTS * (b_psi * psi + descriptor * hard_raw),
    ))
    return delta / jnp.linalg.norm(numerator)


_VALUE_AND_GRAD = jax.jit(jax.value_and_grad(
    _normalized_descriptor_rate_action, argnums=0,
))


def descriptor_rate_and_gradient_action(
    *, state: np.ndarray, signed_descriptor: float,
    weights: np.ndarray, reference: np.ndarray,
) -> tuple[float, np.ndarray]:
    augmented = np.concatenate((
        np.asarray(state, dtype=float) * np.asarray(weights, dtype=float),
        [float(signed_descriptor)],
    ))
    value, gradient = _VALUE_AND_GRAD(
        jnp.asarray(augmented), jnp.asarray(weights), jnp.asarray(reference),
    )
    return float(value), np.asarray(gradient, dtype=float)


__all__ = ["descriptor_rate_and_gradient_action"]
