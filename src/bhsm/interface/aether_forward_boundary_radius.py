"""Action-coordinate projection to the physical forward M4 radius."""

from __future__ import annotations

import math

import numpy as np

from bhsm.interface.aether_diagonal_sp1_m4_attachment_v15_50 import RADIUS0


def _coordinate_dimension(order: int) -> int:
    n = int(order)
    if n < 1:
        raise ValueError("positive Galerkin order required")
    return 3 * n + 1


def _checked_vector(value: np.ndarray, size: int, name: str) -> np.ndarray:
    vector = np.asarray(value, dtype=float)
    if vector.shape != (size,) or not np.all(np.isfinite(vector)):
        raise ValueError(f"finite {name} vector of length {size} required")
    return vector


def _log_cosh(value: float) -> float:
    absolute = abs(float(value))
    return absolute + math.log1p(math.exp(-2.0 * absolute)) - math.log(2.0)


def boundary_log_radius(order: int, coordinates: np.ndarray) -> float:
    """Return ``x=log R4`` in the retained N-independent attachment chart.

    ``q_W=q0+u_L-(1/2)log(cosh(2 v_L))`` is the exact action attachment
    coordinate.  The physical round M4 reference radius is ``RADIUS0/2``.
    """

    n = int(order)
    q = _checked_vector(coordinates, _coordinate_dimension(n), "coordinate")
    signs_k = (-1.0) ** np.arange(1, n + 1)
    signs_j = (-1.0) ** np.arange(n)
    u_boundary = float(q[1 : 1 + n] @ signs_k)
    v_boundary = float(q[1 + 2 * n : 1 + 3 * n] @ signs_j)
    return (
        math.log(RADIUS0 / 2.0)
        + float(q[0])
        + u_boundary
        - 0.5 * _log_cosh(2.0 * v_boundary)
    )


def boundary_log_radius_jets(
    order: int,
    coordinates: np.ndarray,
    left_direction: np.ndarray,
    right_direction: np.ndarray,
    mixed_second_direction: np.ndarray | None = None,
) -> dict[str, float | np.ndarray]:
    """Return exact base, first, and mixed-second action-coordinate jets."""

    n = int(order)
    size = _coordinate_dimension(n)
    q = _checked_vector(coordinates, size, "coordinate")
    h = _checked_vector(left_direction, size, "left direction")
    k = _checked_vector(right_direction, size, "right direction")
    ell = (
        np.zeros(size)
        if mixed_second_direction is None
        else _checked_vector(mixed_second_direction, size, "mixed direction")
    )
    signs_k = (-1.0) ** np.arange(1, n + 1)
    signs_j = (-1.0) ** np.arange(n)
    v_slice = slice(1 + 2 * n, 1 + 3 * n)
    v_boundary = float(q[v_slice] @ signs_j)
    tangent = math.tanh(2.0 * v_boundary)
    gradient = np.zeros(size)
    gradient[0] = 1.0
    gradient[1 : 1 + n] = signs_k
    gradient[v_slice] = -tangent * signs_j
    v_h = float(h[v_slice] @ signs_j)
    v_k = float(k[v_slice] @ signs_j)
    curvature = -2.0 * (1.0 - tangent**2) * v_h * v_k
    return {
        "base": boundary_log_radius(n, q),
        "first_left": float(gradient @ h),
        "first_right": float(gradient @ k),
        "mixed_second": float(gradient @ ell + curvature),
        "gradient": gradient,
        "boundary_v": v_boundary,
    }


def boundary_log_lapse(order: int, multipliers: np.ndarray) -> float:
    """Return the action-owned boundary log lapse."""

    n = int(order)
    m = _checked_vector(multipliers, 2 * n, "multiplier")
    signs_k = (-1.0) ** np.arange(1, n + 1)
    return float(m[:n] @ signs_k)


def proper_time_log_radius_rate(
    order: int,
    coordinates: np.ndarray,
    coordinate_velocity: np.ndarray,
    multipliers: np.ndarray,
) -> float:
    """Return ``d x/d tau=(D_q x . qdot)/N_boundary``."""

    size = _coordinate_dimension(order)
    velocity = _checked_vector(coordinate_velocity, size, "coordinate velocity")
    jets = boundary_log_radius_jets(
        order, coordinates, velocity, np.zeros(size)
    )
    lapse = math.exp(boundary_log_lapse(order, multipliers))
    return float(jets["first_left"]) / lapse


def normalized_incoming_log_radius_quadratic_germ(
    normalized_times: np.ndarray,
    *,
    terminal_log_radius: float,
    terminal_proper_rate_interval: tuple[float, float],
    duration_quadratic_coefficient_interval: tuple[float, float],
) -> dict[str, np.ndarray | float | str | bool]:
    """Return the inverse-free normalized short-history coefficient germ.

    If a regular incoming history reaches its fixed terminal event with
    proper-radius rate ``v_E`` and its action amplitude obeys
    ``T(lambda_0)=a lambda_0^2+o(lambda_0^2)``, continuity of the retained
    flow gives, uniformly for ``s in [0,1]``,

    ``x(s,lambda_0)=x_E-(1-s)*a*v_E*lambda_0^2+o(lambda_0^2)``.

    Only certified positive intervals for ``a`` and ``v_E`` are used.  No
    Euler--Dirac block, acceleration, or history member is solved for.
    """

    times = np.asarray(normalized_times, dtype=float)
    x_terminal = float(terminal_log_radius)
    rate_lower, rate_upper = (
        float(value) for value in terminal_proper_rate_interval
    )
    time_lower, time_upper = (
        float(value) for value in duration_quadratic_coefficient_interval
    )
    if (
        times.ndim != 1
        or not np.all(np.isfinite(times))
        or np.any(times < 0.0)
        or np.any(times > 1.0)
        or not math.isfinite(x_terminal)
        or not (0.0 < rate_lower <= rate_upper)
        or not (0.0 < time_lower <= time_upper)
    ):
        raise ValueError("finite normalized times and positive ordered intervals required")
    factor = 1.0 - times
    product_lower = time_lower * rate_lower
    product_upper = time_upper * rate_upper
    log_radius_coefficient_interval = np.column_stack((
        -factor * product_upper,
        -factor * product_lower,
    ))
    scalar_relative_potential_coefficient_interval = np.column_stack((
        2.0 * factor * product_lower,
        2.0 * factor * product_upper,
    ))
    dirac_relative_superpotential_coefficient_interval = np.column_stack((
        factor * product_lower,
        factor * product_upper,
    ))
    return {
        "normalized_times": times,
        "terminal_log_radius": x_terminal,
        "duration_rate_product_interval": np.asarray(
            (product_lower, product_upper)
        ),
        "log_radius_lambda0_squared_coefficient_interval": (
            log_radius_coefficient_interval
        ),
        "scalar_relative_potential_lambda0_squared_coefficient_interval": (
            scalar_relative_potential_coefficient_interval
        ),
        "dirac_relative_superpotential_lambda0_squared_coefficient_interval": (
            dirac_relative_superpotential_coefficient_interval
        ),
        "uniform_asymptotic": (
            "x(s,lambda_0)=x_E-(1-s)*a*v_E*lambda_0^2+o(lambda_0^2)"
        ),
        "explicit_Euler_Dirac_inverse_formed": False,
        "acceleration_required": False,
    }


__all__ = [
    "boundary_log_radius",
    "boundary_log_radius_jets",
    "boundary_log_lapse",
    "proper_time_log_radius_rate",
    "normalized_incoming_log_radius_quadratic_germ",
]
