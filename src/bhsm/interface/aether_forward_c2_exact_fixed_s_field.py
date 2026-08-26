"""Exact-center evaluator for the desingularized C2 fixed-s action flow."""

from __future__ import annotations

import numpy as np

from bhsm.interface.aether_forward_c2_descriptor_cover import metric_data
from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (
    exact_full_action_jet_at_state,
)


QDIM = 37
STATE_DIMENSION = 98
COMPLEX_STEP = 1.0e-20


def _jet(state: np.ndarray):
    return exact_full_action_jet_at_state(
        12,
        state[:QDIM],
        state[QDIM : 2 * QDIM],
        state[2 * QDIM :],
        points=96,
    )


def _selected_line(
    reduced_hessian: np.ndarray, reference: np.ndarray
) -> tuple[int, float, np.ndarray, np.ndarray, np.ndarray]:
    values, vectors = np.linalg.eigh(reduced_hessian)
    selected = int(np.argmax(np.abs(vectors.T @ reference)))
    psi = vectors[:, selected]
    if float(psi @ reference) < 0.0:
        psi = -psi
    complement = np.delete(vectors, selected, axis=1)
    hard_values = np.delete(values, selected)
    return selected, float(values[selected]), psi, complement, hard_values


def _eigenvalue_directional_derivative(
    state: np.ndarray, psi: np.ndarray, action_direction: np.ndarray,
    weights: np.ndarray,
) -> float:
    raw_direction = np.asarray(action_direction, dtype=float) / weights
    shifted = np.asarray(state, dtype=complex) + 1j * COMPLEX_STEP * raw_direction
    reduced = np.asarray(_jet(shifted).hessian)[QDIM:, QDIM:]
    return float(np.imag(psi @ reduced @ psi) / COMPLEX_STEP)


def exact_fixed_s_field_action(
    *, state: np.ndarray, weights: np.ndarray, reference: np.ndarray,
    signed_descriptor: float,
) -> dict[str, object]:
    """Evaluate the exact cancellation-preserving fixed-s field at one state.

    Only the uniformly invertible selected-line complement is solved.  The
    singular full Euler--Dirac block is never inverted.
    """

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
    # A fixed-s orbit is restricted to the descriptor fiber lambda(Y)=s.
    # Keep the supplied descriptor in the cancellation formula so callers can
    # enclose a nearby fiber without replacing it by a binary64 eigenvalue.
    jet = _jet(y)
    gradient_action = np.asarray(jet.gradient, dtype=float) / w
    hessian_raw = np.asarray(jet.hessian, dtype=float)
    hessian_action = hessian_raw / w[:, None] / w[None, :]
    reduced_raw = hessian_raw[QDIM:, QDIM:]
    selected, eigenvalue, psi, complement, hard_values = _selected_line(
        reduced_raw, ref
    )
    q_weights, reduced_weights, _, _ = metric_data()
    configuration = q_weights * y[QDIM : 2 * QDIM]
    mixed_vq = hessian_action[QDIM : QDIM + QDIM, :QDIM]
    mixed_mq = hessian_action[2 * QDIM :, :QDIM]
    rhs_action = np.concatenate((
        q_weights * gradient_action[:QDIM] - mixed_vq @ configuration,
        -mixed_mq @ configuration,
    ))
    rhs_raw = reduced_weights * rhs_action
    b_psi = float(psi @ rhs_raw)
    hard_raw = complement @ (
        (complement.T @ rhs_raw) / (hard_values - eigenvalue)
    )
    psi_action = np.concatenate((np.zeros(QDIM), reduced_weights * psi))
    full_hard_action = np.concatenate((
        configuration,
        reduced_weights * hard_raw,
    ))
    c_psi = _eigenvalue_directional_derivative(
        y, psi, psi_action, w
    )
    remainder = _eigenvalue_directional_derivative(
        y, psi, full_hard_action, w
    )
    delta = c_psi * b_psi + s * remainder
    numerator = np.concatenate((
        s * configuration,
        reduced_weights * (b_psi * psi + s * hard_raw),
    ))
    if not delta > 0.0:
        raise ArithmeticError("fixed-s denominator is not positive")
    field = numerator / delta
    return {
        "field_action": field,
        "selected_branch": selected,
        "selected_eigenvalue": eigenvalue,
        "b_psi": b_psi,
        "c_psi": c_psi,
        "R_Dlambda_Vhard": remainder,
        "Delta": delta,
        "Dlambda_field": (
            c_psi * b_psi + s * remainder
        ) / delta,
        "explicit_full_Euler_Dirac_inverse_formed": False,
    }


def exact_cancelled_euler_dirac_field_action(
    *, state: np.ndarray, weights: np.ndarray, reference: np.ndarray,
) -> dict[str, object]:
    """Evaluate the denominator-free selected-line Euler--Dirac field.

    The field is ``G_theta=Delta*F_s`` with the signed descriptor set to the
    action-owned simple eigenvalue ``lambda(Y)``.  It therefore remains
    regular at a zero of ``Delta=Dlambda[G_theta]`` and changes only the
    parametrization while ``lambda>0``.  It does not continue through the
    Euler--Dirac singularity ``lambda=0``.
    """

    y = np.asarray(state, dtype=float)
    w = np.asarray(weights, dtype=float)
    ref = np.asarray(reference, dtype=float)
    if (
        y.shape != (STATE_DIMENSION,)
        or w.shape != (STATE_DIMENSION,)
        or ref.shape != (STATE_DIMENSION - QDIM,)
        or not np.all(np.isfinite(y))
        or not np.all(np.isfinite(w))
        or np.any(w <= 0.0)
        or not np.all(np.isfinite(ref))
    ):
        raise ValueError("finite N12 state, weights, and line reference required")
    jet = _jet(y)
    gradient_action = np.asarray(jet.gradient, dtype=float) / w
    hessian_raw = np.asarray(jet.hessian, dtype=float)
    hessian_action = hessian_raw / w[:, None] / w[None, :]
    reduced_raw = hessian_raw[QDIM:, QDIM:]
    selected, eigenvalue, psi, complement, hard_values = _selected_line(
        reduced_raw, ref
    )
    q_weights, reduced_weights, _, _ = metric_data()
    configuration = q_weights * y[QDIM : 2 * QDIM]
    mixed_vq = hessian_action[QDIM : QDIM + QDIM, :QDIM]
    mixed_mq = hessian_action[2 * QDIM :, :QDIM]
    rhs_action = np.concatenate((
        q_weights * gradient_action[:QDIM] - mixed_vq @ configuration,
        -mixed_mq @ configuration,
    ))
    rhs_raw = reduced_weights * rhs_action
    b_psi = float(psi @ rhs_raw)
    hard_raw = complement @ (
        (complement.T @ rhs_raw) / (hard_values - eigenvalue)
    )
    psi_action = np.concatenate((np.zeros(QDIM), reduced_weights * psi))
    full_hard_action = np.concatenate((
        configuration,
        reduced_weights * hard_raw,
    ))
    c_psi = _eigenvalue_directional_derivative(
        y, psi, psi_action, w
    )
    remainder = _eigenvalue_directional_derivative(
        y, psi, full_hard_action, w
    )
    delta = c_psi * b_psi + eigenvalue * remainder
    numerator = np.concatenate((
        eigenvalue * configuration,
        reduced_weights * (b_psi * psi + eigenvalue * hard_raw),
    ))
    hard_gap = float(np.min(np.abs(hard_values - eigenvalue)))
    return {
        "cancelled_field_action": numerator,
        "selected_branch": selected,
        "selected_eigenvalue": eigenvalue,
        "selected_eigenline_gap": hard_gap,
        "b_psi": b_psi,
        "c_psi": c_psi,
        "R_Dlambda_Vhard": remainder,
        "Delta": delta,
        "Dlambda_cancelled_field": delta,
        "explicit_full_Euler_Dirac_inverse_formed": False,
        "Delta_divided_out": False,
    }


__all__ = [
    "exact_cancelled_euler_dirac_field_action",
    "exact_fixed_s_field_action",
]
