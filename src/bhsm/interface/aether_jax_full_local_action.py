"""JAX realization of the unchanged 96-point N12 retained local action.

This optional evaluator is acceleration and cross-check machinery.  The
authoritative action remains :mod:`aether_n3_exact_full_local_action_jet_v17_60`.
No coefficient, quadrature rule, boundary term, or state convention differs.
"""

from __future__ import annotations

from functools import lru_cache

import jax

jax.config.update("jax_enable_x64", True)
import jax.numpy as jnp
import numpy as np

from bhsm.interface.aether_m4_standard_model_zeta_backreaction_v15_51 import (
    standard_model_casimir_coefficient,
)
from bhsm.interface.aether_post_cut_nonround_lorentzian_cap_v15_48 import (
    HOPF_ORBIT_VOLUME,
    RADIUS0,
)
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import dimensions


ORDER = 12
POINTS = 96


def _constants(order: int = ORDER, points: int = POINTS) -> dict[str, jax.Array]:
    dims = dimensions(order)
    qdim = dims["coordinates"]
    mdim = dims["multipliers"]
    nodes, quadrature = np.polynomial.legendre.leggauss(points)
    chi = (nodes + 1.0) * np.pi / 8.0
    quadrature = quadrature * np.pi / 8.0
    ks = np.arange(1, order + 1, dtype=float)
    js = np.arange(order, dtype=float)
    cos_k = np.cos(4.0 * np.outer(ks, chi))
    sin_k = np.sin(4.0 * np.outer(ks, chi))
    cos_j = np.cos(4.0 * np.outer(js, chi))
    sin_j = np.sin(4.0 * np.outer(js, chi))
    window = np.sin(2.0 * chi) ** 2
    window_prime = 2.0 * np.sin(4.0 * chi)

    lc = np.zeros((points, qdim))
    la = np.zeros((points, qdim))
    lb = np.zeros((points, qdim))
    lc[:, 0] = la[:, 0] = lb[:, 0] = 1.0
    lc[:, 1:1 + order] = cos_k.T
    la[:, 1:1 + order] = cos_k.T
    lb[:, 1:1 + order] = cos_k.T
    lc[:, 1 + order:1 + 2 * order] = (window * cos_j).T
    la[:, 1 + 2 * order:1 + 3 * order] = (window * cos_j).T
    lb[:, 1 + 2 * order:1 + 3 * order] = -(window * cos_j).T

    lapse = np.zeros((points, mdim))
    lapse_prime = np.zeros((points, mdim))
    shift = np.zeros((points, mdim))
    shift_prime = np.zeros((points, mdim))
    lapse[:, :order] = cos_k.T
    lapse_prime[:, :order] = (-4.0 * ks[:, None] * sin_k).T
    shift[:, order:2 * order] = (np.sin(4.0 * chi) * cos_j).T
    shift_prime[:, order:2 * order] = (
        4.0 * np.cos(4.0 * chi) * cos_j
        + np.sin(4.0 * chi) * (-4.0 * js[:, None] * sin_j)
    ).T
    sigma = -0.5 + 2.0 * chi / np.pi - np.sin(4.0 * chi) / (2.0 * np.pi)
    localization = 1.0 - 4.0 * sigma**2
    return {
        name: jnp.asarray(value)
        for name, value in {
            "chi": chi,
            "quadrature": quadrature,
            "ks": ks,
            "js": js,
            "cos_k": cos_k,
            "sin_k": sin_k,
            "cos_j": cos_j,
            "sin_j": sin_j,
            "window": window,
            "window_prime": window_prime,
            "lc": lc,
            "la": la,
            "lb": lb,
            "lapse": lapse,
            "lapse_prime": lapse_prime,
            "shift": shift,
            "shift_prime": shift_prime,
            "localization": localization,
        }.items()
    }


_C = _constants()
_DIMS = dimensions(ORDER)
QDIM = _DIMS["coordinates"]
MDIM = _DIMS["multipliers"]
STATE_DIMENSION = 2 * QDIM + MDIM


def _action(state: jax.Array) -> jax.Array:
    q = state[:QDIM]
    velocity = state[QDIM:2 * QDIM]
    multipliers = state[2 * QDIM:]
    chi = _C["chi"]
    cos_k = _C["cos_k"]
    sin_k = _C["sin_k"]
    cos_j = _C["cos_j"]
    sin_j = _C["sin_j"]
    window = _C["window"]
    window_prime = _C["window_prime"]

    u_coeff = q[1:1 + ORDER]
    w_coeff = q[1 + ORDER:1 + 2 * ORDER]
    b_coeff = q[1 + 2 * ORDER:1 + 3 * ORDER]
    radius = RADIUS0 * jnp.exp(q[0])
    u = cos_k.T @ u_coeff
    up = (-4.0 * _C["ks"][:, None] * sin_k).T @ u_coeff
    w = window * (cos_j.T @ w_coeff)
    b = window * (cos_j.T @ b_coeff)
    wp_basis = window_prime * cos_j + window * (
        -4.0 * _C["js"][:, None] * sin_j
    )
    wp = wp_basis.T @ w_coeff
    bp_shape = wp_basis.T @ b_coeff
    cosine = jnp.cos(chi)
    sine = jnp.sin(chi)
    C = radius * jnp.exp(u + w)
    A = radius * jnp.exp(u + b) * cosine
    B = radius * jnp.exp(u - b) * sine
    cp = up + wp
    ap = up + bp_shape - jnp.tan(chi)
    bp = up - bp_shape + 1.0 / jnp.tan(chi)

    volume = C * A**3 * B**3
    spatial_volume = A**3 * B**3
    lc = _C["lc"] @ velocity
    la = _C["la"] @ velocity
    lb = _C["lb"] @ velocity
    log_n = _C["lapse"] @ multipliers
    n_prime = _C["lapse_prime"] @ multipliers
    beta = _C["shift"] @ multipliers
    beta_prime = _C["shift_prime"] @ multipliers
    lapse = jnp.exp(log_n)
    hc = (lc - beta * cp - beta_prime) / lapse
    ha = (la - beta * ap) / lapse
    hb = (lb - beta * bp) / lapse
    adm = hc**2 + 3.0 * ha**2 + 3.0 * hb**2 - (hc + 3.0 * ha + 3.0 * hb) ** 2
    f_normal = -beta / lapse
    x_spatial = 1.0 / C**2 + 3.0 * cosine**2 / A**2 + 3.0 * sine**2 / B**2
    x_eta = x_spatial - f_normal**2
    eta_legendre = 1.0 + x_eta**3
    fixed_gravity = ap**2 + bp**2 + 3.0 * ap * bp
    spatial_gravity = (
        3.0 * spatial_volume / C * lapse
        * (n_prime * (ap + bp) + fixed_gravity)
    )
    algebraic = lapse * volume * (
        3.0 / A**2 + 3.0 / B**2
        - 0.5 * (15.0 * 5.0 ** (1.0 / 3.0) / 4.0)
        - _C["localization"] * (0.5 * x_eta + 0.125 * x_eta**4)
        + 0.5 * adm
    )
    bulk = jnp.sum(_C["quadrature"] * (spatial_gravity + algebraic))
    inertia = jnp.sum(
        _C["quadrature"] * volume * _C["localization"] * eta_legendre / lapse
    )
    action = bulk - 0.25 / (2.0 * HOPF_ORBIT_VOLUME**2 * inertia)

    signs_k = (-1.0) ** jnp.arange(1, ORDER + 1)
    signs_j = (-1.0) ** jnp.arange(ORDER)
    u_boundary = signs_k @ u_coeff
    b_boundary = signs_j @ b_coeff
    A_boundary = radius * jnp.exp(u_boundary + b_boundary) / jnp.sqrt(2.0)
    B_boundary = radius * jnp.exp(u_boundary - b_boundary) / jnp.sqrt(2.0)
    radius4 = A_boundary * B_boundary / jnp.sqrt(A_boundary**2 + B_boundary**2)
    boundary_log_n = signs_k @ multipliers[:ORDER]
    return (
        action
        - standard_model_casimir_coefficient() * jnp.exp(boundary_log_n) / radius4
    )


action_value = jax.jit(_action)
action_gradient = jax.jit(jax.grad(_action))
action_hessian = jax.jit(jax.hessian(_action))


@jax.jit
def action_value_gradient_hessian(state: jax.Array) -> tuple[jax.Array, ...]:
    return action_value(state), action_gradient(state), action_hessian(state)


@jax.jit
def action_hessian_directional(
    state: jax.Array, direction: jax.Array,
) -> tuple[jax.Array, jax.Array]:
    return jax.jvp(action_hessian, (state,), (direction,))


@jax.jit
def action_third_tensor(state: jax.Array) -> jax.Array:
    return jax.jacfwd(action_hessian)(state)


def numpy_value_gradient_hessian(state: np.ndarray) -> tuple[float, np.ndarray, np.ndarray]:
    value, gradient, hessian = action_value_gradient_hessian(jnp.asarray(state))
    return float(value), np.asarray(gradient), np.asarray(hessian)


__all__ = [
    "ORDER",
    "POINTS",
    "QDIM",
    "MDIM",
    "STATE_DIMENSION",
    "action_gradient",
    "action_hessian",
    "action_hessian_directional",
    "action_third_tensor",
    "action_value",
    "action_value_gradient_hessian",
    "numpy_value_gradient_hessian",
]
