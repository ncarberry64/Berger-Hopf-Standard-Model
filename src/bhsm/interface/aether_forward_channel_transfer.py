"""Fixed-channel transfer systems for the maximal-forward source operator.

The retained round spatial blocks are homogeneous in the physical boundary
radius.  Their eigenspaces are therefore fixed along a history; only
``x(tau)=log(R4(tau))`` changes.  This module exposes the exact two-dimensional
channel generators and their log-radius jets without selecting a history,
endpoint, spectral-to-momentum map, or source profile.
"""

from __future__ import annotations

from collections.abc import Callable
import math
from typing import Any

import numpy as np
from scipy.integrate import solve_ivp


def scalar_channel_transfer_generator(
    spatial_eigenvalue_at_unit_radius: float,
    log_radius: float,
    spectral_parameter: complex,
) -> np.ndarray:
    """Return the first-order transfer generator for ``-u''+c/R4^2 u=z u``."""

    c = float(spatial_eigenvalue_at_unit_radius)
    x = float(log_radius)
    z = complex(spectral_parameter)
    if not math.isfinite(c) or c < 0.0 or not math.isfinite(x):
        raise ValueError("finite nonnegative channel and finite log radius required")
    potential = c * math.exp(-2.0 * x)
    return np.asarray([[0.0, 1.0], [potential - z, 0.0]], dtype=complex)


def scalar_channel_log_radius_jets(
    spatial_eigenvalue_at_unit_radius: float,
    log_radius: float,
    spectral_parameter: complex,
    left_direction: float,
    right_direction: float,
    mixed_second_direction: float = 0.0,
) -> dict[str, np.ndarray]:
    """Return base, first-left, first-right, and mixed log-radius jets."""

    base = scalar_channel_transfer_generator(
        spatial_eigenvalue_at_unit_radius, log_radius, spectral_parameter
    )
    c = float(spatial_eigenvalue_at_unit_radius)
    potential = c * math.exp(-2.0 * float(log_radius))
    h = float(left_direction)
    k = float(right_direction)
    ell = float(mixed_second_direction)
    if not math.isfinite(h) or not math.isfinite(k) or not math.isfinite(ell):
        raise ValueError("finite log-radius directions required")

    def lower_left(value: float) -> np.ndarray:
        return np.asarray([[0.0, 0.0], [value, 0.0]], dtype=complex)

    return {
        "base": base,
        "first_left": lower_left(-2.0 * h * potential),
        "first_right": lower_left(-2.0 * k * potential),
        "mixed_second": lower_left((4.0 * h * k - 2.0 * ell) * potential),
    }


def product_dirac_channel_transfer_generator(
    dirac_eigenvalue_at_unit_radius: float,
    log_radius: float,
    spectral_parameter: complex,
    *,
    chirality: int = 1,
) -> np.ndarray:
    """Return the transfer generator for one product-Dirac squared channel.

    With ``A=d/dtau+s`` and ``v=A u``, the equation ``A^* A u=z u`` is
    ``(u,v)'=[[-s,1],[-z,s]](u,v)``.  The other squared block is obtained by
    changing the chirality sign.
    """

    eigenvalue = float(dirac_eigenvalue_at_unit_radius)
    x = float(log_radius)
    z = complex(spectral_parameter)
    sign = int(chirality)
    if (
        not math.isfinite(eigenvalue)
        or not math.isfinite(x)
        or sign not in (-1, 1)
    ):
        raise ValueError("finite Dirac channel and chirality +/-1 required")
    s = sign * eigenvalue * math.exp(-x)
    return np.asarray([[-s, 1.0], [-z, s]], dtype=complex)


def product_dirac_channel_log_radius_jets(
    dirac_eigenvalue_at_unit_radius: float,
    log_radius: float,
    spectral_parameter: complex,
    left_direction: float,
    right_direction: float,
    *,
    chirality: int = 1,
    mixed_second_direction: float = 0.0,
) -> dict[str, np.ndarray]:
    """Return exact log-radius jets of a product-Dirac channel generator."""

    base = product_dirac_channel_transfer_generator(
        dirac_eigenvalue_at_unit_radius,
        log_radius,
        spectral_parameter,
        chirality=chirality,
    )
    s = (
        int(chirality)
        * float(dirac_eigenvalue_at_unit_radius)
        * math.exp(-float(log_radius))
    )
    h = float(left_direction)
    k = float(right_direction)
    ell = float(mixed_second_direction)
    if not math.isfinite(h) or not math.isfinite(k) or not math.isfinite(ell):
        raise ValueError("finite log-radius directions required")

    def diagonal(value: float) -> np.ndarray:
        return np.asarray([[value, 0.0], [0.0, -value]], dtype=complex)

    return {
        "base": base,
        "first_left": diagonal(h * s),
        "first_right": diagonal(k * s),
        "mixed_second": diagonal((ell - h * k) * s),
    }


def transfer_variation_rhs(
    generator_jets: dict[str, np.ndarray],
    transfer_jets: dict[str, np.ndarray],
) -> dict[str, np.ndarray]:
    """Return the base, tangent, and mixed-second transfer derivatives.

    For ``T'=G T`` and two action directions ``h,k``, this is the exact
    triangular variational system

    ``T_h'=G T_h+G_h T`` and
    ``T_hk'=G T_hk+G_h T_k+G_k T_h+G_hk T``.

    The birth frame is action independent when the initial data are
    ``T=I`` and all three variation matrices are zero.  Endpoint/domain
    variations are instead carried by the terminal-admittance jets below.
    """

    keys = ("base", "first_left", "first_right", "mixed_second")

    def checked(record: dict[str, np.ndarray], key: str) -> np.ndarray:
        value = np.asarray(record[key], dtype=complex)
        if value.shape != (2, 2) or not np.all(np.isfinite(value)):
            raise ValueError(f"finite 2x2 matrix required for {key}")
        return value

    if not all(key in generator_jets and key in transfer_jets for key in keys):
        raise KeyError("base, first_left, first_right, and mixed_second required")
    g, gh, gk, ghk = (checked(generator_jets, key) for key in keys)
    t, th, tk, thk = (checked(transfer_jets, key) for key in keys)
    return {
        "base": g @ t,
        "first_left": g @ th + gh @ t,
        "first_right": g @ tk + gk @ t,
        "mixed_second": g @ thk + gh @ tk + gk @ th + ghk @ t,
    }


def proper_duration_scaled_generator_jets(
    generator_jets: dict[str, np.ndarray],
    proper_duration_jets: dict[str, float],
) -> dict[str, np.ndarray]:
    """Pull a proper-time generator back to the fixed interval ``[0,1]``.

    If ``tau=T(xi)*s``, the normalized generator is ``T G``.  This exact
    product jet is what carries moving physical endpoint duration into the
    Calderon derivative while leaving the endpoint labels fixed.
    """

    keys = ("base", "first_left", "first_right", "mixed_second")
    if not all(key in generator_jets and key in proper_duration_jets for key in keys):
        raise KeyError("base, first_left, first_right, and mixed_second required")
    g, gh, gk, ghk = (
        np.asarray(generator_jets[key], dtype=complex) for key in keys
    )
    if any(value.shape != (2, 2) for value in (g, gh, gk, ghk)) or any(
        not np.all(np.isfinite(value)) for value in (g, gh, gk, ghk)
    ):
        raise ValueError("finite 2x2 generator jets required")
    duration, duration_h, duration_k, duration_hk = (
        float(proper_duration_jets[key]) for key in keys
    )
    if not all(
        math.isfinite(value)
        for value in (duration, duration_h, duration_k, duration_hk)
    ) or duration <= 0.0:
        raise ValueError("finite duration jets with positive base required")
    return {
        "base": duration * g,
        "first_left": duration_h * g + duration * gh,
        "first_right": duration_k * g + duration * gk,
        "mixed_second": (
            duration_hk * g
            + duration_h * gk
            + duration_k * gh
            + duration * ghk
        ),
    }


def integrate_transfer_jets(
    generator_jet_builder: Callable[[float], dict[str, np.ndarray]],
    proper_time_interval: tuple[float, float],
    *,
    relative_tolerance: float = 2.0e-11,
    absolute_tolerance: float = 2.0e-13,
    maximum_step: float | None = None,
) -> dict[str, Any]:
    """Integrate the fundamental transfer and two geometry directions.

    ``generator_jet_builder(tau)`` supplies the action-owned base, left,
    right, and mixed generator jets.  The birth frame is the identity and is
    independent of geometry.  This realizes the triangular first-jet system
    without inverting a kinetic, Dirac, or transfer block.

    The interval must have strictly positive proper duration.  Its two ends
    remain boundary traces; this routine imposes no endpoint load or boundary
    condition.
    """

    start, stop = (float(value) for value in proper_time_interval)
    rtol = float(relative_tolerance)
    atol = float(absolute_tolerance)
    if (
        not math.isfinite(start)
        or not math.isfinite(stop)
        or stop <= start
        or not math.isfinite(rtol)
        or not math.isfinite(atol)
        or rtol <= 0.0
        or atol <= 0.0
    ):
        raise ValueError(
            "a finite positive proper-time interval and tolerances are required"
        )
    if maximum_step is None:
        max_step = np.inf
    else:
        max_step = float(maximum_step)
        if not math.isfinite(max_step) or max_step <= 0.0:
            raise ValueError("maximum_step must be positive and finite")

    keys = ("base", "first_left", "first_right", "mixed_second")
    initial = {
        "base": np.eye(2, dtype=complex),
        "first_left": np.zeros((2, 2), dtype=complex),
        "first_right": np.zeros((2, 2), dtype=complex),
        "mixed_second": np.zeros((2, 2), dtype=complex),
    }

    def pack(record: dict[str, np.ndarray]) -> np.ndarray:
        return np.concatenate(
            [np.asarray(record[key], dtype=complex).ravel() for key in keys]
        )

    def unpack(vector: np.ndarray) -> dict[str, np.ndarray]:
        return {
            key: np.asarray(vector[4 * index : 4 * (index + 1)]).reshape(2, 2)
            for index, key in enumerate(keys)
        }

    def rhs(tau: float, vector: np.ndarray) -> np.ndarray:
        generator = generator_jet_builder(float(tau))
        return pack(transfer_variation_rhs(generator, unpack(vector)))

    solution = solve_ivp(
        rhs,
        (start, stop),
        pack(initial),
        method="DOP853",
        rtol=rtol,
        atol=atol,
        max_step=max_step,
    )
    if not solution.success or not np.all(np.isfinite(solution.y[:, -1])):
        raise RuntimeError(f"transfer jet integration failed: {solution.message}")
    transfer = unpack(solution.y[:, -1])
    determinant = np.linalg.det(transfer["base"])
    return {
        **transfer,
        "proper_time_interval": (start, stop),
        "proper_duration": stop - start,
        "function_evaluations": int(solution.nfev),
        "accepted_steps": int(len(solution.t) - 1),
        "base_determinant": determinant,
        "base_Wronskian_residual": float(abs(determinant - 1.0)),
        "explicit_matrix_inverse_formed": False,
        "endpoint_condition_imposed": False,
    }


def two_boundary_weyl_from_transfer_jets(
    transfer_jets: dict[str, np.ndarray],
    *,
    chart_tolerance: float = 1.0e-14,
) -> dict[str, Any]:
    """Return the compact two-boundary Weyl matrix and its exact jets.

    For ``(u_1,p_1)^T=T(u_0,p_0)^T`` and outward conormals
    ``(-p_0,p_1)``, the endpoint response is

    ``M=[[a/b,-1/b],[c-da/b,d/b]]``.

    Both endpoint values ``(u_0,u_1)`` are free boundary variables.  Thus the
    construction is the two-sided Calderon graph on the regular ``b != 0``
    chart, not a terminal boundary condition.  The same formula applies to a
    scalar channel with ``p=u'`` and a factorized product-Dirac channel with
    ``p=A u``.
    """

    keys = ("base", "first_left", "first_right", "mixed_second")
    if not all(key in transfer_jets for key in keys):
        raise KeyError("base, first_left, first_right, and mixed_second required")
    matrices = {
        key: np.asarray(transfer_jets[key], dtype=complex) for key in keys
    }
    if any(value.shape != (2, 2) for value in matrices.values()) or any(
        not np.all(np.isfinite(value)) for value in matrices.values()
    ):
        raise ValueError("finite 2x2 transfer jets required")
    tolerance = float(chart_tolerance)
    if not math.isfinite(tolerance) or tolerance <= 0.0:
        raise ValueError("chart_tolerance must be positive and finite")

    def entry(row: int, column: int) -> tuple[complex, complex, complex, complex]:
        return tuple(  # type: ignore[return-value]
            matrices[key][row, column] for key in keys
        )

    def add(
        left: tuple[complex, complex, complex, complex],
        right: tuple[complex, complex, complex, complex],
    ) -> tuple[complex, complex, complex, complex]:
        return tuple(  # type: ignore[return-value]
            a + b for a, b in zip(left, right, strict=True)
        )

    def scale(
        value: tuple[complex, complex, complex, complex], coefficient: complex
    ) -> tuple[complex, complex, complex, complex]:
        return tuple(coefficient * item for item in value)  # type: ignore[return-value]

    def multiply(
        left: tuple[complex, complex, complex, complex],
        right: tuple[complex, complex, complex, complex],
    ) -> tuple[complex, complex, complex, complex]:
        a, ah, ak, ahk = left
        b, bh, bk, bhk = right
        return (
            a * b,
            ah * b + a * bh,
            ak * b + a * bk,
            ahk * b + ah * bk + ak * bh + a * bhk,
        )

    def reciprocal(
        value: tuple[complex, complex, complex, complex]
    ) -> tuple[complex, complex, complex, complex]:
        b, bh, bk, bhk = value
        if abs(b) <= tolerance:
            raise ZeroDivisionError(
                "two-boundary Weyl chart has singular transfer b block"
            )
        inverse = 1.0 / b
        return (
            inverse,
            -bh * inverse**2,
            -bk * inverse**2,
            2.0 * bh * bk * inverse**3 - bhk * inverse**2,
        )

    a, b, c, d = entry(0, 0), entry(0, 1), entry(1, 0), entry(1, 1)
    inverse_b = reciprocal(b)
    a_over_b = multiply(a, inverse_b)
    d_over_b = multiply(d, inverse_b)
    lower_left = add(c, scale(multiply(d, a_over_b), -1.0))
    upper_right = scale(inverse_b, -1.0)
    determinant = add(multiply(a, d), scale(multiply(b, c), -1.0))

    output: dict[str, Any] = {}
    for index, key in enumerate(keys):
        output[key] = np.asarray(
            [
                [a_over_b[index], upper_right[index]],
                [lower_left[index], d_over_b[index]],
            ],
            dtype=complex,
        )
    output.update(
        {
            "transfer_determinant_jets": {
                key: determinant[index] for index, key in enumerate(keys)
            },
            "transfer_b": b[0],
            "chart_margin": float(abs(b[0])),
            "base_Wronskian_residual": float(abs(determinant[0] - 1.0)),
            "base_Hermitian_residual": float(
                np.linalg.norm(output["base"] - output["base"].conj().T)
            ),
            "first_left_Hermitian_residual": float(
                np.linalg.norm(
                    output["first_left"] - output["first_left"].conj().T
                )
            ),
            "first_right_Hermitian_residual": float(
                np.linalg.norm(
                    output["first_right"] - output["first_right"].conj().T
                )
            ),
            "mixed_second_Hermitian_residual": float(
                np.linalg.norm(
                    output["mixed_second"]
                    - output["mixed_second"].conj().T
                )
            ),
            "endpoint_partition": ("birth", "new_event"),
            "outward_conormal_orientation": ("minus_birth", "plus_new_event"),
            "endpoint_condition_imposed": False,
            "explicit_matrix_inverse_formed": False,
        }
    )
    return output


def scalar_compact_history_weyl_jets(
    spatial_eigenvalue_at_unit_radius: float,
    spectral_parameter: complex,
    log_radius_jets: Callable[[float], dict[str, float]],
    proper_duration_jets: dict[str, float],
    **integration_options: Any,
) -> dict[str, Any]:
    """Evaluate ``M_C`` and its jets on a supplied scalar BHSM history.

    The history is parameterized by normalized proper time ``s in [0,1]``.
    Both its log-radius jet and its physical-duration jet are supplied by the
    action flow/Jacobi family.  No endpoint condition is added.
    """

    keys = ("base", "first_left", "first_right", "mixed_second")

    def builder(normalized_time: float) -> dict[str, np.ndarray]:
        radius = log_radius_jets(float(normalized_time))
        if not all(key in radius for key in keys):
            raise KeyError("all four log-radius jet fields are required")
        generator = scalar_channel_log_radius_jets(
            spatial_eigenvalue_at_unit_radius,
            float(radius["base"]),
            spectral_parameter,
            float(radius["first_left"]),
            float(radius["first_right"]),
            float(radius["mixed_second"]),
        )
        return proper_duration_scaled_generator_jets(
            generator, proper_duration_jets
        )

    transfer = integrate_transfer_jets(
        builder, (0.0, 1.0), **integration_options
    )
    return {
        "transfer": transfer,
        "weyl": two_boundary_weyl_from_transfer_jets(transfer),
        "proper_duration_jets": {
            key: float(proper_duration_jets[key]) for key in keys
        },
        "channel": "scalar",
        "endpoint_condition_imposed": False,
    }


def product_dirac_compact_history_weyl_jets(
    dirac_eigenvalue_at_unit_radius: float,
    spectral_parameter: complex,
    log_radius_jets: Callable[[float], dict[str, float]],
    proper_duration_jets: dict[str, float],
    *,
    chirality: int = 1,
    **integration_options: Any,
) -> dict[str, Any]:
    """Evaluate the factorized product-Dirac compact Weyl history jet."""

    keys = ("base", "first_left", "first_right", "mixed_second")

    def builder(normalized_time: float) -> dict[str, np.ndarray]:
        radius = log_radius_jets(float(normalized_time))
        if not all(key in radius for key in keys):
            raise KeyError("all four log-radius jet fields are required")
        generator = product_dirac_channel_log_radius_jets(
            dirac_eigenvalue_at_unit_radius,
            float(radius["base"]),
            spectral_parameter,
            float(radius["first_left"]),
            float(radius["first_right"]),
            chirality=chirality,
            mixed_second_direction=float(radius["mixed_second"]),
        )
        return proper_duration_scaled_generator_jets(
            generator, proper_duration_jets
        )

    transfer = integrate_transfer_jets(
        builder, (0.0, 1.0), **integration_options
    )
    return {
        "transfer": transfer,
        "weyl": two_boundary_weyl_from_transfer_jets(transfer),
        "proper_duration_jets": {
            key: float(proper_duration_jets[key]) for key in keys
        },
        "channel": "product_Dirac",
        "chirality": int(chirality),
        "endpoint_condition_imposed": False,
    }


def scalar_compact_weyl_terminal_germ(
    spatial_eigenvalue_at_unit_radius: float,
    terminal_log_radius: float,
    spectral_parameter: float,
) -> dict[str, np.ndarray | float]:
    """Return the exact ``T -> 0+`` scalar Weyl Laurent coefficients.

    With ``L=[[1,-1],[-1,1]]`` and
    ``A=[[1/3,1/6],[1/6,1/3]]``, a smooth terminal coefficient has

    ``M_C=T^-1 L+T*(c exp(-2x_E)-z) A+O(T^2)``.

    The fixed-duration physical common-scale derivative is the derivative of
    this germ under ``D x_E=1``.
    """

    c = float(spatial_eigenvalue_at_unit_radius)
    x = float(terminal_log_radius)
    z = float(spectral_parameter)
    if not math.isfinite(c) or c < 0.0 or not math.isfinite(x) or not math.isfinite(z):
        raise ValueError("finite nonnegative channel and finite terminal data required")
    potential = c * math.exp(-2.0 * x)
    q = potential - z
    leading = np.asarray([[1.0, -1.0], [-1.0, 1.0]])
    first = np.asarray([[1.0 / 3.0, 1.0 / 6.0], [1.0 / 6.0, 1.0 / 3.0]])
    return {
        "inverse_duration": leading,
        "duration": q * first,
        "common_scale_constant": np.zeros((2, 2)),
        "common_scale_duration": -2.0 * potential * first,
        "potential_at_terminal": potential,
        "shifted_potential_at_terminal": q,
    }


def product_dirac_compact_weyl_terminal_germ(
    dirac_eigenvalue_at_unit_radius: float,
    terminal_log_radius: float,
    terminal_proper_log_radius_rate: float,
    spectral_parameter: float,
    *,
    chirality: int = 1,
) -> dict[str, np.ndarray | float]:
    """Return product-Dirac terminal Laurent and common-scale coefficients."""

    eigenvalue = float(dirac_eigenvalue_at_unit_radius)
    x = float(terminal_log_radius)
    rate = float(terminal_proper_log_radius_rate)
    z = float(spectral_parameter)
    sign = int(chirality)
    if not all(math.isfinite(value) for value in (eigenvalue, x, rate, z)) or sign not in (-1, 1):
        raise ValueError("finite terminal data and chirality +/-1 required")
    s = sign * eigenvalue * math.exp(-x)
    s_dot = -s * rate
    q = s**2 - z
    leading = np.asarray([[1.0, -1.0], [-1.0, 1.0]])
    constant = np.asarray([[-s, 0.0], [0.0, s]])
    duration = np.asarray(
        [
            [(q + 2.0 * s_dot) / 3.0, (q - s_dot) / 6.0],
            [(q - s_dot) / 6.0, (q - s_dot) / 3.0],
        ]
    )
    common_constant = np.asarray([[s, 0.0], [0.0, -s]])
    common_duration = np.asarray(
        [
            [(-2.0 * s**2 - 2.0 * s_dot) / 3.0, (-2.0 * s**2 + s_dot) / 6.0],
            [(-2.0 * s**2 + s_dot) / 6.0, (-2.0 * s**2 + s_dot) / 3.0],
        ]
    )
    return {
        "inverse_duration": leading,
        "constant": constant,
        "duration": duration,
        "common_scale_constant": common_constant,
        "common_scale_duration": common_duration,
        "superpotential_at_terminal": s,
        "proper_superpotential_rate_at_terminal": s_dot,
        "shifted_squared_superpotential_at_terminal": q,
    }


def backward_weyl_mobius(
    transfer_birth_to_terminal: np.ndarray,
    terminal_admittance: complex,
) -> complex:
    """Pull a scalar terminal Weyl admittance back to the birth trace."""

    transfer = np.asarray(transfer_birth_to_terminal, dtype=complex)
    if transfer.shape != (2, 2) or not np.all(np.isfinite(transfer)):
        raise ValueError("finite 2x2 transfer matrix required")
    terminal = complex(terminal_admittance)
    numerator = transfer[1, 0] - terminal * transfer[0, 0]
    denominator = terminal * transfer[0, 1] - transfer[1, 1]
    if abs(denominator) == 0.0:
        raise ZeroDivisionError("terminal graph is singular under transfer")
    return numerator / denominator


def backward_weyl_mobius_jets(
    transfer_jets: dict[str, np.ndarray],
    terminal_admittance_jets: dict[str, complex],
) -> dict[str, complex]:
    """Pull back base, tangent, and mixed-second terminal Weyl jets.

    This includes terminal/Friedrichs graph variation and therefore separates
    bulk transfer variation from endpoint/domain variation without assuming a
    terminal return.  A zero denominator is precisely the singular graph
    chart already excluded from a regular Weyl interval.
    """

    keys = ("base", "first_left", "first_right", "mixed_second")
    if not all(key in transfer_jets for key in keys) or not all(
        key in terminal_admittance_jets for key in keys
    ):
        raise KeyError("base, first_left, first_right, and mixed_second required")
    matrices = [np.asarray(transfer_jets[key], dtype=complex) for key in keys]
    if any(matrix.shape != (2, 2) for matrix in matrices) or any(
        not np.all(np.isfinite(matrix)) for matrix in matrices
    ):
        raise ValueError("finite 2x2 transfer jets required")
    mu, muh, muk, muhk = (
        complex(terminal_admittance_jets[key]) for key in keys
    )
    if not all(
        math.isfinite(value.real) and math.isfinite(value.imag)
        for value in (mu, muh, muk, muhk)
    ):
        raise ValueError("finite terminal admittance jets required")
    t, th, tk, thk = matrices

    def numerator(matrix: np.ndarray, terminal: complex) -> complex:
        return matrix[1, 0] - terminal * matrix[0, 0]

    def denominator(matrix: np.ndarray, terminal: complex) -> complex:
        return terminal * matrix[0, 1] - matrix[1, 1]

    n = numerator(t, mu)
    d = denominator(t, mu)
    if abs(d) == 0.0:
        raise ZeroDivisionError("terminal graph is singular under transfer")
    nh = numerator(th, mu) - muh * t[0, 0]
    nk = numerator(tk, mu) - muk * t[0, 0]
    nhk = (
        numerator(thk, mu)
        - muhk * t[0, 0]
        - muh * tk[0, 0]
        - muk * th[0, 0]
    )
    dh = denominator(th, mu) + muh * t[0, 1]
    dk = denominator(tk, mu) + muk * t[0, 1]
    dhk = (
        denominator(thk, mu)
        + muhk * t[0, 1]
        + muh * tk[0, 1]
        + muk * th[0, 1]
    )
    m = n / d
    mh = (nh - m * dh) / d
    mk = (nk - m * dk) / d
    mhk = (nhk - mh * dk - mk * dh - m * dhk) / d
    return {
        "base": m,
        "first_left": mh,
        "first_right": mk,
        "mixed_second": mhk,
    }


__all__ = [
    "scalar_channel_transfer_generator",
    "scalar_channel_log_radius_jets",
    "product_dirac_channel_transfer_generator",
    "product_dirac_channel_log_radius_jets",
    "transfer_variation_rhs",
    "proper_duration_scaled_generator_jets",
    "integrate_transfer_jets",
    "two_boundary_weyl_from_transfer_jets",
    "scalar_compact_history_weyl_jets",
    "product_dirac_compact_history_weyl_jets",
    "scalar_compact_weyl_terminal_germ",
    "product_dirac_compact_weyl_terminal_germ",
    "backward_weyl_mobius",
    "backward_weyl_mobius_jets",
]
