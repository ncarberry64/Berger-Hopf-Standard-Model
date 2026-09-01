"""Exact two-jet evaluation of the retained cancelled C2 flow.

The standard diagnostic evaluator obtains ``c_psi`` and ``R`` from two
separate Hessian directional jets and forms ``Delta=c_psi*b_psi+s*R``.  By
linearity of ``D lambda`` this module evaluates the identical quantity with
one directional jet along the already assembled cancelled numerator.  It is
an algebraic acceleration only; no action or flow is changed.
"""

from __future__ import annotations

import os

import numpy as np

from bhsm.interface.aether_forward_c2_descriptor_cover import metric_data
from bhsm.interface.aether_forward_c2_exact_fixed_s_field import (
    QDIM,
    STATE_DIMENSION,
    _eigenvalue_directional_derivative,
    _jet,
    _selected_line,
)


def exact_cancelled_euler_dirac_field_action(
    *, state: np.ndarray, weights: np.ndarray, reference: np.ndarray,
    signed_descriptor: float,
) -> dict[str, object]:
    y = np.asarray(state, dtype=float)
    w = np.asarray(weights, dtype=float)
    ref = np.asarray(reference, dtype=float)
    s = float(signed_descriptor)
    if (
        y.shape != (STATE_DIMENSION,)
        or w.shape != (STATE_DIMENSION,)
        or ref.shape != (STATE_DIMENSION - QDIM,)
        or not np.all(np.isfinite(y))
        or not np.all(np.isfinite(w))
        or np.any(w <= 0.0)
        or not np.all(np.isfinite(ref))
        or not np.isfinite(s)
        or s < 0.0
    ):
        raise ValueError("finite N12 state, weights, line reference, and s>=0 required")
    jet = _jet(y)
    gradient_action = np.asarray(jet.gradient, dtype=float) / w
    hessian_raw = np.asarray(jet.hessian, dtype=float)
    hessian_action = hessian_raw / w[:, None] / w[None, :]
    reduced_raw = hessian_raw[QDIM:, QDIM:]
    selected, eigenvalue, psi, complement, hard_values = _selected_line(
        reduced_raw, ref,
    )
    q_weights, reduced_weights, _, _ = metric_data()
    configuration = q_weights * y[QDIM:2 * QDIM]
    rhs_action = np.concatenate((
        q_weights * gradient_action[:QDIM],
        np.zeros(reduced_weights.size - QDIM),
    )) - hessian_action[QDIM:, :QDIM] @ configuration
    rhs_raw = reduced_weights * rhs_action
    b_psi = float(psi @ rhs_raw)
    hard_raw = complement @ (
        (complement.T @ rhs_raw) / (hard_values - eigenvalue)
    )
    numerator = np.concatenate((
        s * configuration,
        reduced_weights * (b_psi * psi + s * hard_raw),
    ))
    if os.environ.get("BHSM_N12_FAST_DELTA_JAX", "0") == "1":
        import jax.numpy as jnp

        from bhsm.interface.aether_jax_full_local_action import (
            action_hessian_directional,
        )

        _, directional = action_hessian_directional(
            jnp.asarray(y), jnp.asarray(numerator / w),
        )
        directional = np.asarray(directional)
        directional = 0.5 * (directional + directional.T)
        delta = float(psi @ directional[QDIM:, QDIM:] @ psi)
    else:
        delta = _eigenvalue_directional_derivative(y, psi, numerator, w)
    return {
        "cancelled_field_action": numerator,
        "selected_branch": selected,
        "signed_descriptor": s,
        "numeric_selected_eigenvalue_not_used_as_descriptor": eigenvalue,
        "selected_eigenline_gap": float(np.min(np.abs(hard_values - eigenvalue))),
        "b_psi": b_psi,
        "Delta": delta,
        "Dlambda_cancelled_field": delta,
        "explicit_full_Euler_Dirac_inverse_formed": False,
        "Delta_divided_out": False,
        "combined_directional_Delta_identity_used": True,
        "JAX_Delta_predictor_only": (
            os.environ.get("BHSM_N12_FAST_DELTA_JAX", "0") == "1"
        ),
    }


__all__ = ["exact_cancelled_euler_dirac_field_action"]
