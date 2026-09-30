"""Numerical heat-action cotangents on an explicitly supplied C2 form core.

The generalized stiffness/mass pencil and its derivatives come from the
existing descriptor assembler. This evaluates that finite form core; a
future-domain or angular completion is not supplied by this routine.
"""
from __future__ import annotations

import math
from typing import Any

import numpy as np
from scipy.linalg import eigh
from scipy.special import exp1, logsumexp

from bhsm.interface.aether_forward_c2_finite_core_descriptor import assemble_finite_core_descriptor


def _dense(diagonal: np.ndarray, off: np.ndarray) -> np.ndarray:
    return np.diag(diagonal) + np.diag(off, 1) + np.diag(off, -1)


def _log_e1(value: float) -> float:
    if value <= 50.0:
        return math.log(float(exp1(value)))
    # exp(value) E1(value) has an alternating asymptotic expansion. At
    # value>50 the first thirty terms resolve the binary64 precision.
    term = 1.0
    series = 1.0
    for order in range(1, 31):
        term *= -order / value
        series += term
    return -value - math.log(value) + math.log(series)


def _restore_scaled(common_log: float, scaled: np.ndarray) -> np.ndarray:
    """Restore each component, even when the common seed underflows."""
    result = np.zeros_like(scaled)
    nonzero = scaled != 0.0
    result[nonzero] = np.sign(scaled[nonzero]) * np.exp(common_log + np.log(np.abs(scaled[nonzero])))
    return result


def finite_core_heat_coefficient_cotangent(
    *, log_radii: np.ndarray, proper_durations: np.ndarray,
    channel: str, unit_channel_value: float, chirality: int = 1,
    heat_length: float = 1.0,
) -> dict[str, Any]:
    """Return D_x Gamma and D_h Gamma, retaining very small forces in logs.

For M-normalized eigenvectors v_i, the generalized first variation is
  D Gamma = sum_i exp(-ell^2 lambda_i)/(2 lambda_i)
                    * v_i^T (D K - lambda_i D M) v_i.
Element quadratic forms avoid cancellation in the temporal stiffness.
Scaled cotangents retain their common log factor when binary64 underflows.
"""
    if not math.isfinite(heat_length) or heat_length <= 0:
        raise ValueError("a finite positive inherited heat length is required")
    x = np.asarray(log_radii, dtype=float)
    h = np.asarray(proper_durations, dtype=float)
    pencil = assemble_finite_core_descriptor(log_radii=x, proper_durations=h,
        channel=channel, unit_channel_value=unit_channel_value, chirality=chirality)
    stiffness = _dense(pencil["K_diagonal"], pencil["K_off_diagonal"])
    mass = _dense(pencil["M_diagonal"], pencil["M_off_diagonal"])
    eigenvalues, vectors = eigh(stiffness, mass)
    if not np.all(np.isfinite(eigenvalues)) or eigenvalues[0] <= 0:
        raise ValueError("positive finite generalized spectrum required")
    log_seed = -heat_length**2 * eigenvalues - np.log(2.0 * eigenvalues)
    common_log = float(log_seed[0])
    scaled_seed = np.exp(log_seed - common_log)
    padded = np.vstack((vectors, np.zeros((1, vectors.shape[1]))))
    scaled_x = np.zeros(x.size)
    scaled_h = np.zeros(h.size)
    rayleigh = np.zeros(eigenvalues.size)
    for index, duration in enumerate(h):
        left, right = padded[index], padded[index + 1]
        mass_density = (left * left + left * right + right * right) / 3.0
        difference_squared = (left - right) ** 2
        if channel == "scalar":
            potential = float(pencil["element_coefficient"][index])
            contact = np.zeros_like(left)
        else:
            coefficient = float(pencil["element_coefficient"][index])
            potential = coefficient * coefficient
            contact = coefficient * (right * right - left * left)
        radius_mid_variation = -2.0 * potential * duration * mass_density - contact
        duration_variation = (-difference_squared / duration**2
                             + (potential - eigenvalues) * mass_density)
        radius = float(scaled_seed @ radius_mid_variation)
        scaled_x[index:index + 2] += 0.5 * radius
        scaled_h[index] = float(scaled_seed @ duration_variation)
        rayleigh += difference_squared / duration + potential * duration * mass_density + contact
    radius_force = _restore_scaled(common_log, scaled_x)
    duration_force = _restore_scaled(common_log, scaled_h)
    gamma_logs = np.asarray([_log_e1(float(heat_length**2 * value)) for value in eigenvalues])
    log_abs_gamma = float(logsumexp(gamma_logs) - math.log(2.0))
    value = -math.exp(log_abs_gamma)
    common_scale = float(scaled_x.sum() + scaled_h @ h)
    expected_common_scale = float(-2.0 * (eigenvalues @ scaled_seed))
    return {
        "channel": channel, "chirality": chirality if channel == "product_Dirac" else None,
        "unit_channel_value": float(unit_channel_value), "heat_length": heat_length,
        "dimension": int(pencil["dimension"]), "Gamma_heat": value,
        "log_absolute_Gamma_heat": log_abs_gamma,
        "D_log_R4_Gamma_heat": radius_force,
        "D_proper_duration_Gamma_heat": duration_force,
        "cotangent_common_log_factor": common_log,
        "scaled_D_log_R4_Gamma_heat": scaled_x,
        "scaled_D_proper_duration_Gamma_heat": scaled_h,
        "minimum_generalized_eigenvalue": float(eigenvalues[0]),
        "cotangent_common_factor_underflows_binary64": math.exp(common_log) == 0.0,
        "binary64_cotangent_underflow": bool(np.any((scaled_x != 0) & (radius_force == 0))
                                              or np.any((scaled_h != 0) & (duration_force == 0))),
        "moving_mass_derivative_included": True,
        "numerical_residuals": {
            "mass_frame_orthogonality": float(np.linalg.norm(vectors.T @ mass @ vectors - np.eye(len(eigenvalues)), 2)),
            "maximum_Rayleigh_eigenvalue_relative_difference": float(np.max(np.abs(rayleigh - eigenvalues) / eigenvalues)),
            "scaled_common_scale_Ward_relative": abs(common_scale - expected_common_scale) / max(abs(expected_common_scale), np.finfo(float).tiny),
        },
        "domain": "EXISTING_BIRTH_RETAINED_FAR_CORE_DIRICHLET_FORM_CORE",
        "scope": "ONE_SUPPLIED_CHANNEL;_FAR_CORE_IS_AN_ARTIFICIAL_TRUNCATION;_NOT_FULL_FUTURE_CHILD_ACTION",
    }


__all__ = ["finite_core_heat_coefficient_cotangent"]
