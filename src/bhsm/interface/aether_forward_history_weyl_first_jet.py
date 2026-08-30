"""Vectorized first jet of the retained two-boundary channel response.

The compact Gate-7 operator depends on a history only through
``x=log(R4)`` and its physical duration.  This module propagates the base
two-by-two transfer matrix and an arbitrary finite family of geometry
directions in one triangular solve.  It imposes no endpoint condition and
forms no kinetic, Dirac, transfer, or Weyl inverse.
"""

from __future__ import annotations

import math
from typing import Any, Literal

import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import CubicSpline

from bhsm.interface.aether_forward_channel_transfer import (
    product_dirac_channel_transfer_generator,
    scalar_channel_transfer_generator,
)


Channel = Literal["scalar", "product_dirac"]


def _validated_history(
    normalized_times: np.ndarray,
    log_radius: np.ndarray,
    log_radius_first_jet: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    times = np.asarray(normalized_times, dtype=float)
    values = np.asarray(log_radius, dtype=float)
    first = np.asarray(log_radius_first_jet, dtype=float)
    if (
        times.ndim != 1
        or values.shape != times.shape
        or first.ndim != 2
        or first.shape[0] != times.size
        or times.size < 2
        or not np.all(np.isfinite(times))
        or not np.all(np.isfinite(values))
        or not np.all(np.isfinite(first))
        or not np.all(np.diff(times) > 0.0)
        or times[0] != 0.0
        or times[-1] != 1.0
    ):
        raise ValueError(
            "finite increasing [0,1] history and node-by-direction first jet required"
        )
    return times, values, first


def _generator_and_log_radius_derivative(
    *,
    channel: Channel,
    unit_channel_value: float,
    log_radius: float,
    spectral_parameter: complex,
    chirality: int,
) -> tuple[np.ndarray, np.ndarray]:
    value = float(unit_channel_value)
    x = float(log_radius)
    z = complex(spectral_parameter)
    if channel == "scalar":
        base = scalar_channel_transfer_generator(value, x, z)
        potential = value * math.exp(-2.0 * x)
        derivative = np.asarray(
            [[0.0, 0.0], [-2.0 * potential, 0.0]], dtype=complex,
        )
    elif channel == "product_dirac":
        base = product_dirac_channel_transfer_generator(
            value, x, z, chirality=chirality,
        )
        signed_mass = int(chirality) * value * math.exp(-x)
        derivative = np.asarray(
            [[signed_mass, 0.0], [0.0, -signed_mass]], dtype=complex,
        )
    else:
        raise ValueError("channel must be scalar or product_dirac")
    return base, derivative


def integrate_history_weyl_first_jet(
    *,
    normalized_times: np.ndarray,
    log_radius: np.ndarray,
    log_radius_first_jet: np.ndarray,
    proper_duration: float,
    proper_duration_first_jet: np.ndarray,
    channel: Channel,
    unit_channel_value: float,
    spectral_parameter: complex,
    chirality: int = 1,
    relative_tolerance: float = 2.0e-11,
    absolute_tolerance: float = 2.0e-13,
    maximum_step: float | None = None,
    chart_tolerance: float = 1.0e-14,
) -> dict[str, Any]:
    """Integrate ``M_C`` and all supplied first geometry directions.

    The independent variable is normalized physical time.  If ``G`` is the
    proper-time channel generator, the propagated generator is ``T*G`` and
    its direction ``h`` is ``T_h*G + T*G_x*x_h``.
    """

    times, values, first = _validated_history(
        normalized_times, log_radius, log_radius_first_jet,
    )
    duration = float(proper_duration)
    duration_first = np.asarray(proper_duration_first_jet, dtype=float)
    parameter_count = first.shape[1]
    if (
        not math.isfinite(duration)
        or duration <= 0.0
        or duration_first.shape != (parameter_count,)
        or not np.all(np.isfinite(duration_first))
        or int(chirality) not in (-1, 1)
    ):
        raise ValueError("positive duration and one finite duration jet per direction required")
    rtol = float(relative_tolerance)
    atol = float(absolute_tolerance)
    if not (math.isfinite(rtol) and rtol > 0.0 and math.isfinite(atol) and atol > 0.0):
        raise ValueError("positive finite integration tolerances required")
    max_step = np.inf if maximum_step is None else float(maximum_step)
    if not max_step > 0.0 or not math.isfinite(max_step) and maximum_step is not None:
        raise ValueError("maximum_step must be positive and finite when supplied")
    tolerance = float(chart_tolerance)
    if not math.isfinite(tolerance) or tolerance <= 0.0:
        raise ValueError("positive finite chart tolerance required")

    x_spline = CubicSpline(times, values)
    first_spline = CubicSpline(times, first, axis=0)
    def scaled_generator(
        normalized_time: float,
    ) -> tuple[np.ndarray, np.ndarray]:
        generator, generator_x = _generator_and_log_radius_derivative(
            channel=channel,
            unit_channel_value=unit_channel_value,
            log_radius=float(x_spline(normalized_time)),
            spectral_parameter=spectral_parameter,
            chirality=chirality,
        )
        scaled = duration * generator
        directions = np.asarray(first_spline(normalized_time), dtype=float)
        scaled_first = (
            duration_first[:, None, None] * generator[None, :, :]
            + duration * directions[:, None, None] * generator_x[None, :, :]
        )
        return scaled, scaled_first

    # The two Dirichlet solutions start with u=0 and therefore have a
    # singular Riccati coordinate.  Integrate only a tiny endpoint collar in
    # the regular two-vector representation, then use ratios and log
    # amplitude on the long interval.  This avoids exponentially ill-
    # conditioned fundamental matrices without adding a boundary condition.
    collar = min(1.0e-5, 0.05 * float(np.min(np.diff(times))))
    vector_initial = np.zeros((1 + parameter_count, 2), dtype=complex)
    vector_initial[0, 1] = 1.0

    def vector_rhs(normalized_time: float, packed: np.ndarray) -> np.ndarray:
        vectors = packed.reshape(1 + parameter_count, 2)
        scaled, scaled_first = scaled_generator(normalized_time)
        output = np.empty_like(vectors)
        output[0] = scaled @ vectors[0]
        output[1:] = (
            np.einsum("ab,jb->ja", scaled, vectors[1:])
            + np.einsum("jab,b->ja", scaled_first, vectors[0])
        )
        return output.ravel()

    def endpoint_collar(start: float, stop: float) -> tuple[np.ndarray, int, int]:
        solution = solve_ivp(
            vector_rhs,
            (start, stop),
            vector_initial.ravel(),
            method="DOP853",
            rtol=rtol,
            atol=atol,
            max_step=min(max_step, collar / 4.0),
        )
        if not solution.success or not np.all(np.isfinite(solution.y[:, -1])):
            raise RuntimeError(f"endpoint collar integration failed: {solution.message}")
        return (
            solution.y[:, -1].reshape(1 + parameter_count, 2),
            int(solution.nfev),
            int(len(solution.t) - 1),
        )

    def riccati_initial(vectors: np.ndarray) -> np.ndarray:
        u, v = vectors[0]
        if abs(u) <= np.finfo(float).tiny:
            raise ZeroDivisionError("Dirichlet collar did not enter the regular Riccati chart")
        result = np.empty((1 + parameter_count, 2), dtype=complex)
        result[0] = (v / u, np.log(complex(u)))
        if parameter_count:
            uh = vectors[1:, 0]
            vh = vectors[1:, 1]
            result[1:, 0] = (vh * u - v * uh) / (u * u)
            result[1:, 1] = uh / u
        return result

    def riccati_rhs(normalized_time: float, packed: np.ndarray) -> np.ndarray:
        variables = packed.reshape(1 + parameter_count, 2)
        r, _ = variables[0]
        rh = variables[1:, 0]
        scaled, scaled_first = scaled_generator(normalized_time)
        alpha, beta = scaled[0]
        gamma, delta = scaled[1]
        output = np.empty_like(variables)
        output[0, 0] = gamma + (delta - alpha) * r - beta * r * r
        output[0, 1] = alpha + beta * r
        if parameter_count:
            alpha_h = scaled_first[:, 0, 0]
            beta_h = scaled_first[:, 0, 1]
            gamma_h = scaled_first[:, 1, 0]
            delta_h = scaled_first[:, 1, 1]
            output[1:, 0] = (
                gamma_h
                + (delta_h - alpha_h) * r
                + (delta - alpha) * rh
                - beta_h * r * r
                - 2.0 * beta * r * rh
            )
            output[1:, 1] = alpha_h + beta_h * r + beta * rh
        return output.ravel()

    forward_collar, forward_nfev, forward_steps = endpoint_collar(0.0, collar)
    forward_initial = riccati_initial(forward_collar)
    forward = solve_ivp(
        riccati_rhs,
        (collar, 1.0),
        forward_initial.ravel(),
        method="DOP853",
        rtol=rtol,
        atol=atol,
        max_step=max_step,
    )
    backward_collar, backward_nfev, backward_steps = endpoint_collar(
        1.0, 1.0 - collar,
    )
    backward_initial = riccati_initial(backward_collar)
    backward = solve_ivp(
        riccati_rhs,
        (1.0 - collar, 0.0),
        backward_initial.ravel(),
        method="DOP853",
        rtol=rtol,
        atol=atol,
        max_step=max_step,
    )
    if any(
        not solution.success or not np.all(np.isfinite(solution.y[:, -1]))
        for solution in (forward, backward)
    ):
        messages = (forward.message, backward.message)
        raise RuntimeError(f"two-sided Riccati integration failed: {messages}")
    forward_final = forward.y[:, -1].reshape(1 + parameter_count, 2)
    backward_final = backward.y[:, -1].reshape(1 + parameter_count, 2)
    log_b = forward_final[0, 1]
    inverse_b = np.exp(-log_b)
    if abs(inverse_b) >= 1.0 / tolerance:
        raise ZeroDivisionError("two-boundary Weyl chart has singular transfer b block")
    m00 = -backward_final[0, 0]
    m11 = forward_final[0, 0]
    off_diagonal = -inverse_b
    weyl = np.asarray(
        [[m00, off_diagonal], [off_diagonal, m11]], dtype=complex,
    )
    weyl_first = np.empty((parameter_count, 2, 2), dtype=complex)
    if parameter_count:
        off_first = -off_diagonal * forward_final[1:, 1]
        weyl_first[:, 0, 0] = -backward_final[1:, 0]
        weyl_first[:, 0, 1] = off_first
        weyl_first[:, 1, 0] = off_first
        weyl_first[:, 1, 1] = forward_final[1:, 0]
    log_chart_margin = float(np.real(log_b))
    chart_margin = (
        math.exp(log_chart_margin)
        if log_chart_margin <= math.log(np.finfo(float).max)
        else math.inf
    )
    return {
        "weyl": weyl,
        "weyl_first_jet": weyl_first,
        "log_transfer_b": log_b,
        "log_transfer_b_first_jet": forward_final[1:, 1],
        "transfer_b_chart_log_margin": log_chart_margin,
        "off_diagonal_log_absolute": -log_chart_margin,
        "inverse_transfer_b_underflowed_in_binary64": bool(inverse_b == 0.0),
        "parameter_count": parameter_count,
        "proper_duration": duration,
        "function_evaluations": int(
            forward_nfev + backward_nfev + forward.nfev + backward.nfev
        ),
        "accepted_steps": int(
            forward_steps + backward_steps + len(forward.t) + len(backward.t) - 2
        ),
        "transfer_b_chart_margin": chart_margin,
        "Wronskian_identity_used": "c-d*a/b=-1/b",
        "weyl_Hermitian_residual": float(np.linalg.norm(weyl - weyl.conj().T)),
        "propagation_representation": "TWO_SIDED_RICCATI_PLUS_LOG_TRANSFER_B",
        "numerical_not_interval_authority": True,
        "explicit_matrix_inverse_formed": False,
        "endpoint_condition_imposed": False,
    }


__all__ = ["integrate_history_weyl_first_jet"]
