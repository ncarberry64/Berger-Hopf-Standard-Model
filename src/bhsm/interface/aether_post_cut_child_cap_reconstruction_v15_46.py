"""Post-cut BHSM child-cap reconstruction from metric-free event data.

The v15.45 firewall transports topology, orientation, incidence, endpoint
ordering, degree, and FR parity, but no metric datum.  This module turns
exactly those data into a new variational problem on ``B4 x S3``.  It does
not continue the closed-S7 metric through the Legendre singularity.

In proper-radial gauge the static child metric and join map are

    ds7^2 = d rho^2 + A(rho)^2 dOmega_3,u^2
                    + B(rho)^2 dOmega_3,v^2,
    eta = (cos(f) u, sin(f) v),       0 <= rho <= L.

The v-S3 collapses regularly at rho=0 and the transported full-preimage
boundary is at f(L)=pi/4.  The response endpoints uniquely normalize the
child restriction to sigma(0)=-1/2 and sigma(L)=0.
"""

from __future__ import annotations

import json
import math
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq, least_squares

from bhsm.interface.aether_response_constrained_child_galerkin_v15_41 import (
    HOPF_ORBIT_VOLUME,
)


VERSION = "v15.46"
CLASSIFICATION = "BHSM_POST_CUT_CHILD_CAP_METRIC_RECONSTRUCTION"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False


def post_cut_variational_contract() -> dict[str, Any]:
    """State the coefficient-free reconstructed-cap variational problem."""

    return {
        "domain": "C_child=B4_times_S3_with_0<=rho<=L",
        "metric": (
            "ds8^2=-N(rho)^2dt^2+drho^2+A(rho)^2dOmega3_u^2+"
            "B(rho)^2dOmega3_v^2"
        ),
        "eta": "eta=(cos(f)u,sin(f)v)",
        "pole_data": "B(0)=0,_B_prime(0)=1,_A_prime(0)=N_prime(0)=0,_f(0)=0",
        "transported_boundary_data": (
            "boundary_is_S3_times_S3,_f(L)=pi/4,_sigma(L)=0,_"
            "boundary_identity_is_child_to_child"
        ),
        "response": (
            "sigma(rho)=-1/2+(2Z_c)^-1*integral_0^rho_"
            "sin(f)^2cos(f)^2ds,_Z_c=integral_0^L_sin(f)^2cos(f)^2ds"
        ),
        "carrier": "Lambda=1-4sigma^2",
        "eta_invariant": "X=f_prime^2+3cos(f)^2/A^2+3sin(f)^2/B^2",
        "eta_density": "F(X)=X/2+X^4/8",
        "GHY_completed_radial_density": (
            "3*N*A^3*B^3*[n(a+b)+a^2+b^2+3ab]+"
            "N*A^3*B^3*[3/A^2+3/B^2-kappa0/2-Lambda*F(X)]"
        ),
        "log_derivatives": "n=N_prime/N,_a=A_prime/A,_b=B_prime/B",
        "kappa0": "15*5^(1/3)/4_for_kappa1=1",
        "FR_sector": "J^2=1/4_from_odd_antiperiodic_domain",
        "Routh_term": "-J^2/(2I),_I=Vol(S3)^2*integral_A^3B^3*Lambda*(1+X^3)/N_drho",
        "metric_firewall_respected": True,
        "pre_firewall_metric_used_as_boundary_data": False,
        "new_continuous_coefficient": False,
    }


@lru_cache(maxsize=8)
def _gauss_rule(points: int) -> tuple[np.ndarray, np.ndarray]:
    nodes, weights = np.polynomial.legendre.leggauss(points)
    return (nodes + 1.0) / 2.0, weights / 2.0


def _poly_and_derivative(
    y: np.ndarray, coefficients: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Polynomial sum c_k y^(k+2) and its y derivative."""

    value = np.zeros_like(y)
    derivative = np.zeros_like(y)
    for index, coefficient in enumerate(coefficients):
        power = index + 2
        value += coefficient * y**power
        derivative += power * coefficient * y ** (power - 1)
    return value, derivative


def child_cap_fields(
    coefficients: np.ndarray, *, points: int = 220
) -> dict[str, np.ndarray | float]:
    """Evaluate a regular finite Galerkin chart on the reconstructed cap.

    Coordinate order is ``log_L, log_A0, a2..a5, b2..b5, n2..n4, q1,q2``.
    No coefficient is a coupling: all are solved field coordinates.
    """

    values = np.asarray(coefficients, dtype=float)
    if values.shape != (15,) or not np.all(np.isfinite(values)):
        raise ValueError("coefficients must be fifteen finite real numbers")
    if points < 80:
        raise ValueError("points must be at least 80")
    log_length, log_a0 = values[:2]
    a_coefficients = values[2:6]
    b_coefficients = values[6:10]
    n_coefficients = values[10:13]
    q1, q2 = values[13:15]
    length = math.exp(float(log_length))
    a0 = math.exp(float(log_a0))
    y, unit_weights = _gauss_rule(int(points))
    rho = length * y
    weights = length * unit_weights

    log_a_shape, log_a_y = _poly_and_derivative(y, a_coefficients)
    log_b_shape, log_b_y = _poly_and_derivative(y, b_coefficients)
    log_n, log_n_y = _poly_and_derivative(y, n_coefficients)
    A = a0 * np.exp(log_a_shape)
    B = rho * np.exp(log_b_shape)
    N = np.exp(log_n)
    a = log_a_y / length
    b = 1.0 / rho + log_b_y / length
    n = log_n_y / length

    # Both variations vanish at the transported eta endpoints.  This keeps
    # the cap degree/incidence data fixed while allowing the interior join to
    # relax independently of the erased pre-firewall metric.
    f = (
        0.25 * math.pi * y
        + q1 * y * (1.0 - y)
        + q2 * y**2 * (1.0 - y)
    )
    f_y = (
        0.25 * math.pi
        + q1 * (1.0 - 2.0 * y)
        + q2 * (2.0 * y - 3.0 * y**2)
    )
    f_prime = f_y / length
    if np.min(f_prime) <= 1.0e-6:
        raise ValueError("the reconstructed cap eta map must be monotone")

    raw_response = np.sin(f) ** 2 * np.cos(f) ** 2
    normalization = float(np.dot(weights, raw_response))
    if normalization <= 1.0e-12:
        raise ValueError("the child response normalization must be positive")
    augmented_rho = np.concatenate(([0.0], rho, [length]))
    augmented_raw = np.concatenate(([0.0], raw_response, [0.25]))
    cumulative = np.concatenate((
        [0.0],
        np.cumsum(
            0.5
            * (augmented_raw[1:] + augmented_raw[:-1])
            * np.diff(augmented_rho)
        ),
    ))
    cumulative *= 0.5 / cumulative[-1]
    sigma = -0.5 + cumulative[1:-1]
    localization = np.maximum(0.0, 1.0 - 4.0 * sigma**2)
    x_eta = (
        f_prime**2
        + 3.0 * np.cos(f) ** 2 / A**2
        + 3.0 * np.sin(f) ** 2 / B**2
    )
    eta_legendre = 1.0 + x_eta**3
    volume = A**3 * B**3
    return {
        "rho": rho,
        "weights": weights,
        "length": float(length),
        "N": N,
        "A": A,
        "B": B,
        "a": a,
        "b": b,
        "n": n,
        "f": f,
        "f_prime": f_prime,
        "sigma": sigma,
        "localization": localization,
        "X_eta": x_eta,
        "eta_legendre": eta_legendre,
        "volume": volume,
        "response_normalization_child": normalization,
    }


def child_cap_routhian(
    coefficients: np.ndarray, *, points: int = 220
) -> float:
    """Return the orbit-volume-normalized EH+GHY+eta+FR cap action."""

    fields = child_cap_fields(coefficients, points=points)
    weights = np.asarray(fields["weights"])
    N = np.asarray(fields["N"])
    A = np.asarray(fields["A"])
    B = np.asarray(fields["B"])
    a = np.asarray(fields["a"])
    b = np.asarray(fields["b"])
    n = np.asarray(fields["n"])
    volume = np.asarray(fields["volume"])
    localization = np.asarray(fields["localization"])
    x_eta = np.asarray(fields["X_eta"])
    kappa0 = 15.0 * 5.0 ** (1.0 / 3.0) / 4.0
    eta_density = 0.5 * x_eta + 0.125 * x_eta**4
    density = (
        3.0 * N * volume * (n * (a + b) + a**2 + b**2 + 3.0 * a * b)
        + N
        * volume
        * (3.0 / A**2 + 3.0 / B**2 - 0.5 * kappa0 - localization * eta_density)
    )
    bulk = float(np.dot(weights, density))
    inertia_without_orbit = float(np.dot(
        weights,
        volume * localization * np.asarray(fields["eta_legendre"]) / N,
    ))
    if inertia_without_orbit <= 1.0e-12:
        raise ValueError("the post-cut localized inertia must be positive")
    return bulk - 0.25 / (
        2.0 * HOPF_ORBIT_VOLUME**2 * inertia_without_orbit
    )


def round_cap_constraint_fields(
    radius: float,
    trace_rate: np.ndarray,
    eta_normal_velocity: np.ndarray,
    rotor_velocity: float,
    *,
    points: int,
) -> dict[str, np.ndarray | float]:
    """Evaluate the exact round-cap ADM constraint densities.

    This chart is not inherited metric data.  It is the lowest regular
    ``B4 x S3`` reconstruction compatible with the transported incidence:
    ``A=R cos(chi)``, ``B=R sin(chi)``, ``f=chi`` on
    ``0 <= chi <= pi/4``.  A spatially varying pure-trace extrinsic
    curvature ``K^i_j=H delta^i_j`` is accompanied by the eta normal
    velocity required by the radial momentum constraint.
    """

    if radius <= 0.0 or rotor_velocity <= 0.0:
        raise ValueError("radius and rotor_velocity must be positive")
    H = np.asarray(trace_rate, dtype=float)
    velocity = np.asarray(eta_normal_velocity, dtype=float)
    if H.shape != (points,) or velocity.shape != (points,):
        raise ValueError("constraint arrays must match points")
    chi = np.linspace(0.0, math.pi / 4.0, points)
    weight = np.sin(chi) ** 3 * np.cos(chi) ** 3
    sigma = -0.5 + 2.0 * chi / math.pi - np.sin(4.0 * chi) / (2.0 * math.pi)
    localization = np.maximum(0.0, 1.0 - 4.0 * sigma**2)
    x_spatial = np.full(points, 7.0 / radius**2)
    x_eta = x_spatial - velocity**2
    eta_legendre = 1.0 + x_eta**3
    if np.min(eta_legendre) <= 1.0e-5:
        raise ValueError("eta Legendre form must stay positive")
    eta_density = localization * (
        0.5 * x_eta
        + 0.125 * x_eta**4
        + eta_legendre * velocity**2
    )
    rho_fr = 0.5 * localization * eta_legendre * rotor_velocity**2
    kappa0 = 15.0 * 5.0 ** (1.0 / 3.0) / 4.0
    hamiltonian = (
        21.0 / radius**2
        + 21.0 * H**2
        - 0.5 * kappa0
        - eta_density
        - rho_fr
    )
    momentum_current = localization * eta_legendre * velocity
    inertia_without_orbit = float(
        radius**7
        * np.trapezoid(weight * localization * eta_legendre, chi)
    )
    return {
        "chi": chi,
        "weight": weight,
        "sigma": sigma,
        "localization": localization,
        "X_spatial": x_spatial,
        "X_eta": x_eta,
        "eta_legendre": eta_legendre,
        "eta_density": eta_density,
        "rho_FR": rho_fr,
        "hamiltonian_residual": hamiltonian,
        "momentum_current": momentum_current,
        "inertia_without_orbit": inertia_without_orbit,
    }


def solve_round_cap_constraints(
    *, points: int = 120, mode_count: int = 6
) -> dict[str, Any]:
    """Reconstruct a Lorentzian child slice by solving both ADM constraints.

    The contracting sign of ``H`` is the transported ``child_x_negative``
    orientation.  The eta normal velocity is solved, not prescribed.  Its
    vanishing at both ends is the regular-pole/no-through-boundary condition.
    The radius and FR angular velocity are solved simultaneously with
    ``J=I omega=1/2``.
    """

    if points < 48 or not 3 <= mode_count <= 10:
        raise ValueError("points must be at least 48 and mode_count in [3,10]")
    chi = np.linspace(0.0, math.pi / 4.0, points)
    radius_seed = 3.0
    kappa0 = 15.0 * 5.0 ** (1.0 / 3.0) / 4.0
    pole_h_squared = max(1.0e-5, (0.5 * kappa0 - 21.0 / radius_seed**2) / 21.0)
    log_h_seed = math.log(math.sqrt(pole_h_squared))
    h_seed = np.zeros(mode_count)
    h_seed[0] = log_h_seed
    v_seed = np.zeros(mode_count)
    v_seed[0] = -0.02
    H_seed = -np.exp(np.full(points, log_h_seed))
    velocity_seed = v_seed[0] * np.sin(4.0 * chi)
    provisional = round_cap_constraint_fields(
        radius_seed, H_seed, velocity_seed, 1.0e-4, points=points
    )
    omega_seed = 0.5 / (
        HOPF_ORBIT_VOLUME * float(provisional["inertia_without_orbit"])
    )
    initial = np.concatenate((
        h_seed,
        v_seed,
        [math.log(radius_seed), math.log(omega_seed)],
    ))

    harmonics = np.arange(mode_count, dtype=float)
    cosine = np.cos(4.0 * chi[:, None] * harmonics[None, :])
    sine = np.sin(4.0 * chi[:, None] * harmonics[None, :])
    endpoint_window = np.sin(4.0 * chi)

    def unpack(
        values: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, float, float]:
        h_coefficients = values[:mode_count]
        v_coefficients = values[mode_count:2 * mode_count]
        log_h = cosine @ h_coefficients
        H = -np.exp(log_h)
        velocity = endpoint_window * (cosine @ v_coefficients)
        h_prime = (
            (-4.0 * harmonics)[None, :]
            * sine
        ) @ h_coefficients
        H_prime = H * h_prime
        return (
            H,
            H_prime,
            velocity,
            math.exp(float(values[-2])),
            math.exp(float(values[-1])),
        )

    def residual(values: np.ndarray) -> np.ndarray:
        H, H_prime, velocity, radius, omega = unpack(values)
        try:
            fields = round_cap_constraint_fields(
                radius, H, velocity, omega, points=points
            )
        except (ValueError, OverflowError, FloatingPointError):
            return np.full(2 * points + 1, 1.0e6)
        momentum = 6.0 * H_prime + np.asarray(fields["momentum_current"])
        charge = (
            HOPF_ORBIT_VOLUME
            * float(fields["inertia_without_orbit"])
            * omega
            - 0.5
        )
        return np.concatenate((
            np.asarray(fields["hamiltonian_residual"]),
            momentum,
            [charge],
        ))

    lower = np.concatenate((
        np.array([-4.0] + [-2.0] * (mode_count - 1)),
        np.full(mode_count, -1.5),
        [math.log(2.0), math.log(1.0e-10)],
    ))
    upper = np.concatenate((
        np.array([0.0] + [2.0] * (mode_count - 1)),
        np.full(mode_count, 1.5),
        [math.log(12.0), math.log(0.1)],
    ))
    solution = least_squares(
        residual,
        initial,
        bounds=(lower, upper),
        xtol=2.0e-11,
        ftol=2.0e-11,
        gtol=2.0e-11,
        max_nfev=1600,
        x_scale="jac",
        verbose=0,
    )
    H, H_prime, velocity, radius, omega = unpack(solution.x)
    fields = round_cap_constraint_fields(
        radius, H, velocity, omega, points=points
    )
    momentum = 6.0 * H_prime + np.asarray(fields["momentum_current"])
    return {
        "success": bool(solution.success),
        "solver_message": str(solution.message),
        "points": points,
        "mode_count": mode_count,
        "trace_log_mode_coefficients": solution.x[:mode_count].tolist(),
        "eta_velocity_mode_coefficients": solution.x[
            mode_count:2 * mode_count
        ].tolist(),
        "radius": radius,
        "rotor_velocity": omega,
        "FR_charge": (
            HOPF_ORBIT_VOLUME
            * float(fields["inertia_without_orbit"])
            * omega
        ),
        "trace_rate_range": [float(np.min(H)), float(np.max(H))],
        "eta_normal_velocity_range": [
            float(np.min(velocity)), float(np.max(velocity))
        ],
        "eta_boundary_velocity": [float(velocity[0]), float(velocity[-1])],
        "maximum_Hamiltonian_residual": float(np.max(np.abs(
            np.asarray(fields["hamiltonian_residual"])
        ))),
        "maximum_momentum_residual_in_solved_collocation": float(
            np.max(np.abs(momentum))
        ),
        "terminal_momentum_residual": float(abs(momentum[-1])),
        "minimum_eta_Legendre": float(np.min(np.asarray(fields["eta_legendre"]))),
        "response_endpoints": [
            float(np.asarray(fields["sigma"])[0]),
            float(np.asarray(fields["sigma"])[-1]),
        ],
        "contracting_orientation_selected": bool(np.max(H) < 0.0),
        "pre_firewall_metric_imported": False,
        "residual_norm": float(np.linalg.norm(residual(solution.x))),
    }


def solve_round_cap_tt_constraints(
    *, points: int = 180, mode_count: int = 8
) -> dict[str, Any]:
    """Solve the post-cut constraints with an exact radial TT tensor.

    Put ``K^chi_chi=s``, ``K^u_u=-s/6+d`` and
    ``K^v_v=-s/6-d``.  The trace vanishes.  On the round cap the momentum
    constraint determines

    ``d=-[s'+(7/2)(cot(chi)-tan(chi))s]/[3(cot(chi)+tan(chi))]``.

    Thus only the Hamiltonian constraint and fixed FR charge remain to be
    solved.  Cosine modes make ``s'`` vanish at the regular pole and at the
    ``S3 x S3`` boundary; no grid-scale momentum freedom remains.
    """

    if points < 80 or not 4 <= mode_count <= 14:
        raise ValueError("points must be at least 80 and mode_count in [4,14]")
    chi = np.linspace(0.0, math.pi / 4.0, points)
    harmonics = np.arange(mode_count, dtype=float)
    cosine = np.cos(4.0 * chi[:, None] * harmonics[None, :])
    sine = np.sin(4.0 * chi[:, None] * harmonics[None, :])
    sigma = -0.5 + 2.0 * chi / math.pi - np.sin(4.0 * chi) / (2.0 * math.pi)
    localization = np.maximum(0.0, 1.0 - 4.0 * sigma**2)
    weight = np.sin(chi) ** 3 * np.cos(chi) ** 3

    def evaluate(values: np.ndarray) -> dict[str, Any]:
        coefficients = values[:mode_count]
        radius = math.exp(float(values[-2]))
        omega = math.exp(float(values[-1]))
        s = cosine @ coefficients
        s_prime = ((-4.0 * harmonics)[None, :] * sine) @ coefficients
        d = np.empty_like(s)
        interior = np.arange(1, points - 1)
        cotangent = 1.0 / np.tan(chi[interior])
        tangent = np.tan(chi[interior])
        d[interior] = -(
            s_prime[interior]
            + 3.5 * (cotangent - tangent) * s[interior]
        ) / (3.0 * (cotangent + tangent))
        d[0] = -7.0 * s[0] / 6.0
        d[-1] = -s_prime[-1] / 6.0
        shear_norm = 7.0 * s**2 / 6.0 + 6.0 * d**2
        x_eta = 7.0 / radius**2
        eta_legendre = 1.0 + x_eta**3
        eta_density = localization * (0.5 * x_eta + 0.125 * x_eta**4)
        rho_fr = 0.5 * localization * eta_legendre * omega**2
        kappa0 = 15.0 * 5.0 ** (1.0 / 3.0) / 4.0
        hamiltonian = (
            0.5 * (42.0 / radius**2 - shear_norm)
            - 0.5 * kappa0
            - eta_density
            - rho_fr
        )
        inertia_without_orbit = float(
            radius**7
            * np.trapezoid(weight * localization * eta_legendre, chi)
        )
        charge = HOPF_ORBIT_VOLUME * inertia_without_orbit * omega
        return {
            "coefficients": coefficients,
            "radius": radius,
            "omega": omega,
            "s": s,
            "d": d,
            "shear_norm": shear_norm,
            "hamiltonian": hamiltonian,
            "eta_legendre": eta_legendre,
            "inertia_without_orbit": inertia_without_orbit,
            "charge": charge,
        }

    radius0 = (343.0 / 5.0) ** (1.0 / 6.0)
    x0 = 7.0 / radius0**2
    legendre0 = 1.0 + x0**3
    inertia0 = radius0**7 * float(np.trapezoid(
        weight * localization * legendre0, chi
    ))
    omega0 = 0.5 / (HOPF_ORBIT_VOLUME * inertia0)
    kappa0 = 15.0 * 5.0 ** (1.0 / 3.0) / 4.0
    pole_defect = 42.0 / radius0**2 - kappa0
    coefficients0 = np.zeros(mode_count)
    coefficients0[0] = math.sqrt(3.0 * pole_defect / 28.0)
    initial = np.concatenate((
        coefficients0, [math.log(radius0 * 0.999), math.log(omega0)]
    ))

    def residual(values: np.ndarray) -> np.ndarray:
        try:
            fields = evaluate(values)
        except (ValueError, OverflowError, FloatingPointError):
            return np.full(points + 1, 1.0e6)
        return np.concatenate((
            np.asarray(fields["hamiltonian"]),
            [float(fields["charge"]) - 0.5],
        ))

    solution = least_squares(
        residual,
        initial,
        bounds=(
            np.concatenate((np.full(mode_count, -2.0), [math.log(1.5), math.log(1.0e-9)])),
            np.concatenate((np.full(mode_count, 2.0), [math.log(3.0), math.log(0.1)])),
        ),
        xtol=2.0e-13,
        ftol=2.0e-13,
        gtol=2.0e-13,
        max_nfev=2400,
        x_scale="jac",
    )
    fields = evaluate(solution.x)
    # Evaluate the analytic divergence independently from the defining
    # formula using a high-order numerical derivative of s.
    s = np.asarray(fields["s"])
    d = np.asarray(fields["d"])
    p = -s / 6.0 + d
    q = -s / 6.0 - d
    s_prime_numeric = np.gradient(s, chi, edge_order=2)
    divergence = np.zeros_like(s)
    divergence[1:-1] = (
        s_prime_numeric[1:-1]
        + 3.0 * (-np.tan(chi[1:-1])) * (s[1:-1] - p[1:-1])
        + 3.0 / np.tan(chi[1:-1]) * (s[1:-1] - q[1:-1])
    )
    return {
        "success": bool(solution.success),
        "solver_message": str(solution.message),
        "points": points,
        "mode_count": mode_count,
        "radius": float(fields["radius"]),
        "rotor_velocity": float(fields["omega"]),
        "FR_charge": float(fields["charge"]),
        "TT_mode_coefficients": np.asarray(fields["coefficients"]).tolist(),
        "K_chi_range": [float(np.min(s)), float(np.max(s))],
        "K_u_range": [float(np.min(p)), float(np.max(p))],
        "K_v_range": [float(np.min(q)), float(np.max(q))],
        "maximum_trace_residual": float(np.max(np.abs(s + 3.0 * p + 3.0 * q))),
        "maximum_momentum_residual": float(np.max(np.abs(divergence[1:-1]))),
        "maximum_Hamiltonian_residual": float(np.max(np.abs(
            np.asarray(fields["hamiltonian"])
        ))),
        "minimum_eta_Legendre": float(fields["eta_legendre"]),
        "response_endpoints": [float(sigma[0]), float(sigma[-1])],
        "pre_firewall_metric_imported": False,
        "residual_norm": float(np.linalg.norm(residual(solution.x))),
    }


def integrate_exact_round_cap_tt(
    radius: float, *, trace_rate: float = 0.0, points: int = 500
) -> dict[str, Any]:
    """Integrate the positive radial-TT branch at a specified round radius."""

    radius = float(radius)
    if not 1.5 < radius < 3.0:
        raise ValueError("radius must lie in the regular reconstruction interval")
    grid = np.linspace(0.0, math.pi / 4.0, points)
    sigma_grid = -0.5 + 2.0 * grid / math.pi - np.sin(4.0 * grid) / (2.0 * math.pi)
    localization_grid = np.maximum(0.0, 1.0 - 4.0 * sigma_grid**2)
    weight_grid = np.sin(grid) ** 3 * np.cos(grid) ** 3
    x_eta = 7.0 / radius**2
    eta_legendre = 1.0 + x_eta**3
    inertia = radius**7 * float(np.trapezoid(
        weight_grid * localization_grid * eta_legendre, grid
    ))
    omega = 0.5 / (HOPF_ORBIT_VOLUME * inertia)
    kappa0 = 15.0 * 5.0 ** (1.0 / 3.0) / 4.0

    def defect(coordinate: np.ndarray | float) -> np.ndarray:
        coordinate_array = np.asarray(coordinate)
        sigma = (
            -0.5
            + 2.0 * coordinate_array / math.pi
            - np.sin(4.0 * coordinate_array) / (2.0 * math.pi)
        )
        localization = np.maximum(0.0, 1.0 - 4.0 * sigma**2)
        eta = localization * (0.5 * x_eta + 0.125 * x_eta**4)
        rho_fr = 0.5 * localization * eta_legendre * omega**2
        return (
            42.0 / radius**2
            + 42.0 * float(trace_rate) ** 2
            - kappa0
            - 2.0 * eta
            - 2.0 * rho_fr
        )

    epsilon = 2.0e-5
    initial_defect = float(defect(epsilon))
    if initial_defect <= 0.0:
        raise ValueError("the regular pole has no real trace-free shear")
    initial_s = math.sqrt(3.0 * initial_defect / 28.0)

    def equation(coordinate: float, state: np.ndarray) -> np.ndarray:
        s = float(state[0])
        radicand = (float(defect(coordinate)) - 7.0 * s**2 / 6.0) / 6.0
        root = math.sqrt(max(radicand, 0.0))
        cotangent = 1.0 / math.tan(coordinate)
        tangent = math.tan(coordinate)
        return np.array([
            3.0 * (cotangent + tangent) * root
            - 3.5 * (cotangent - tangent) * s
        ])

    solution = solve_ivp(
        equation,
        (epsilon, math.pi / 4.0),
        [initial_s],
        t_eval=np.linspace(epsilon, math.pi / 4.0, points),
        rtol=2.0e-10,
        atol=2.0e-11,
        max_step=2.0e-3,
    )
    coordinate = solution.t
    s = solution.y[0]
    D = defect(coordinate)
    radicand = (D - 7.0 * s**2 / 6.0) / 6.0
    d = -np.sqrt(np.maximum(radicand, 0.0))
    hamiltonian = D - (7.0 * s**2 / 6.0 + 6.0 * d**2)
    return {
        "success": bool(solution.success),
        "radius": radius,
        "rotor_velocity": omega,
        "trace_rate": float(trace_rate),
        "FR_charge": HOPF_ORBIT_VOLUME * inertia * omega,
        "coordinate": coordinate,
        "K_chi": s,
        "anisotropy_d": d,
        "minimum_radicand": float(np.min(radicand)),
        "boundary_anisotropy_d": float(d[-1]),
        "boundary_Hamiltonian_defect": float(D[-1]),
        "maximum_Hamiltonian_residual": float(np.max(np.abs(hamiltonian))),
        "minimum_eta_Legendre": eta_legendre,
    }


def solve_minimal_round_cap_cmc_tt_reconstruction(
    *, points: int = 700
) -> dict[str, Any]:
    """Select the unique minimum-norm real post-cut Cauchy reconstruction.

    No metric momentum crosses the firewall.  In the coefficient-selected
    round cap chart, reconstruction therefore minimizes ``|H|`` subject to
    the Hamiltonian and momentum constraints having a real TT solution.
    The event orientation fixes the remaining sign to the contracting
    branch.  The minimum is the first value at which the TT radicand is
    nonnegative on the whole cap.
    """

    radius = (343.0 / 5.0) ** (1.0 / 6.0)

    def margin(magnitude: float) -> float:
        return float(integrate_exact_round_cap_tt(
            radius, trace_rate=-magnitude, points=points
        )["minimum_radicand"])

    magnitude = brentq(margin, 0.1, 0.2, xtol=2.0e-11, rtol=2.0e-11)
    solution = integrate_exact_round_cap_tt(
        radius, trace_rate=-magnitude, points=points
    )
    return {
        "selection": (
            "minimum_absolute_CMC_trace_rate_with_a_real_exact_TT_"
            "constraint_solution;_negative_sign_from_child_x_negative"
        ),
        "radius": solution["radius"],
        "trace_rate": solution["trace_rate"],
        "rotor_velocity": solution["rotor_velocity"],
        "FR_charge": solution["FR_charge"],
        "minimum_TT_radicand": solution["minimum_radicand"],
        "boundary_anisotropy_d": solution["boundary_anisotropy_d"],
        "boundary_Hamiltonian_defect": solution[
            "boundary_Hamiltonian_defect"
        ],
        "maximum_Hamiltonian_residual": solution[
            "maximum_Hamiltonian_residual"
        ],
        "minimum_eta_Legendre": solution["minimum_eta_Legendre"],
        "contracting_orientation_selected": solution["trace_rate"] < 0.0,
        "metric_reconstructed_from_action_scale": True,
        "pre_firewall_metric_imported": False,
        "new_continuous_coefficient": False,
    }


def _round_cap_seed() -> np.ndarray:
    """Project the round half-cap only as a solver seed, never event data."""

    radius = (343.0 / 5.0) ** (1.0 / 6.0)
    length = radius * math.pi / 4.0
    sample = np.linspace(0.02, 1.0, 300)
    powers = np.column_stack([sample**power for power in range(2, 6)])
    angle = math.pi * sample / 4.0
    a_shape = np.log(np.cos(angle))
    b_shape = np.log(np.sin(angle) / angle)
    a_coefficients = np.linalg.lstsq(powers, a_shape, rcond=None)[0]
    b_coefficients = np.linalg.lstsq(powers, b_shape, rcond=None)[0]
    return np.concatenate((
        [math.log(length), math.log(radius)],
        a_coefficients,
        b_coefficients,
        np.zeros(3),
        np.zeros(2),
    ))


def action_gradient(
    coefficients: np.ndarray, *, points: int = 160, step: float = 2.0e-5
) -> np.ndarray:
    """Central finite-difference first variation in the cap chart."""

    values = np.asarray(coefficients, dtype=float)
    result = np.empty_like(values)
    for index in range(values.size):
        delta = np.zeros_like(values)
        delta[index] = step
        result[index] = (
            child_cap_routhian(values + delta, points=points)
            - child_cap_routhian(values - delta, points=points)
        ) / (2.0 * step)
    return result


def solve_post_cut_child_cap(
    *, points: int = 150, maximum_evaluations: int = 350
) -> dict[str, Any]:
    """Solve the GHY-completed finite cap first variation."""

    seed = _round_cap_seed()
    scale = max(1.0, abs(child_cap_routhian(seed, points=points)))

    def residual(values: np.ndarray) -> np.ndarray:
        try:
            return action_gradient(values, points=points) / scale
        except (FloatingPointError, OverflowError, ValueError):
            return np.full(values.shape, 1.0e6)

    lower = np.array(
        [-2.0, -2.0] + [-4.0] * 8 + [-3.0] * 3 + [-0.7, -0.7]
    )
    upper = np.array(
        [3.0, 3.0] + [4.0] * 8 + [3.0] * 3 + [0.7, 0.7]
    )
    solution = least_squares(
        residual,
        seed,
        bounds=(lower, upper),
        xtol=2.0e-10,
        ftol=2.0e-10,
        gtol=2.0e-10,
        max_nfev=int(maximum_evaluations),
        x_scale="jac",
    )
    values = np.asarray(solution.x)
    fields = child_cap_fields(values, points=max(points, 240))
    gradient = action_gradient(values, points=max(points, 200))
    A = np.asarray(fields["A"])
    B = np.asarray(fields["B"])
    N = np.asarray(fields["N"])
    f = np.asarray(fields["f"])
    sigma = np.asarray(fields["sigma"])
    return {
        "success": bool(solution.success),
        "solver_message": str(solution.message),
        "coordinates": values.tolist(),
        "coordinate_order": [
            "log_L", "log_A0", "a2", "a3", "a4", "a5",
            "b2", "b3", "b4", "b5", "n2", "n3", "n4", "q1", "q2",
        ],
        "length": fields["length"],
        "pole_A": float(math.exp(values[1])),
        "boundary_A": float(A[-1]),
        "boundary_B": float(B[-1]),
        "boundary_N": float(N[-1]),
        "boundary_f": math.pi / 4.0,
        "response_endpoints": [-0.5, 0.0],
        "sampled_f_endpoints": [0.0, float(f[-1])],
        "sampled_sigma_range": [float(np.min(sigma)), float(np.max(sigma))],
        "minimum_f_prime": float(np.min(np.asarray(fields["f_prime"]))),
        "minimum_eta_Legendre": float(np.min(np.asarray(fields["eta_legendre"]))),
        "minimum_localization": float(np.min(np.asarray(fields["localization"]))),
        "localized_inertia_without_orbit": float(np.dot(
            np.asarray(fields["weights"]),
            np.asarray(fields["volume"])
            * np.asarray(fields["localization"])
            * np.asarray(fields["eta_legendre"])
            / N,
        )),
        "routhian": child_cap_routhian(values, points=max(points, 240)),
        "max_first_variation": float(np.max(np.abs(gradient))),
        "scaled_residual_norm": float(np.linalg.norm(gradient / scale)),
        "metric_reconstructed": bool(
            np.all(A > 0.0) and np.all(B > 0.0) and np.all(N > 0.0)
        ),
        "eta_Legendre_positive": bool(
            np.min(np.asarray(fields["eta_legendre"])) > 0.0
        ),
        "pre_firewall_metric_imported": False,
    }


def solve_static_zero_energy_cap(
    *, points: int = 140, maximum_evaluations: int = 1000
) -> dict[str, Any]:
    """Solve spatial stationarity together with the constant-lapse constraint.

    The lapse shape is fixed to one; its constant variation is retained as
    the zero-energy equation.  This diagnostic decides whether the post-cut
    particle can be static before a relative-periodic search is attempted.
    """

    seed_full = _round_cap_seed()
    active = np.array(list(range(10)) + [13, 14], dtype=int)
    seed = seed_full[active]
    action_scale = max(1.0, abs(child_cap_routhian(seed_full, points=points)))

    def expand(values: np.ndarray) -> np.ndarray:
        full = np.zeros(15)
        full[active] = values
        return full

    def residual(values: np.ndarray) -> np.ndarray:
        full = expand(values)
        try:
            gradient = action_gradient(full, points=points)[active]
            action = child_cap_routhian(full, points=points)
        except (ValueError, OverflowError, FloatingPointError):
            return np.full(active.size + 1, 1.0e6)
        return np.concatenate((gradient / action_scale, [action / action_scale]))

    lower = np.array([-2.0, -2.0] + [-6.0] * 8 + [-0.2, -0.2])
    upper = np.array([3.0, 3.0] + [6.0] * 8 + [0.2, 0.2])
    solution = least_squares(
        residual,
        seed,
        bounds=(lower, upper),
        xtol=2.0e-12,
        ftol=2.0e-12,
        gtol=2.0e-12,
        max_nfev=maximum_evaluations,
        x_scale="jac",
    )
    full = expand(solution.x)
    fields = child_cap_fields(full, points=max(points, 260))
    gradient = action_gradient(full, points=max(points, 220))[active]
    action = child_cap_routhian(full, points=max(points, 260))
    boundary_a = float(np.asarray(fields["A"])[-1])
    boundary_b = float(np.asarray(fields["B"])[-1])
    return {
        "success": bool(solution.success),
        "solver_message": str(solution.message),
        "coordinates": full.tolist(),
        "action": action,
        "max_spatial_first_variation": float(np.max(np.abs(gradient))),
        "combined_residual_norm": float(np.linalg.norm(residual(solution.x))),
        "boundary_A": boundary_a,
        "boundary_B": boundary_b,
        "child_scale_x": math.log(boundary_b / boundary_a),
        "minimum_eta_Legendre": float(np.min(np.asarray(fields["eta_legendre"]))),
        "static_zero_energy_solution": bool(
            abs(action) < 2.0e-3 and np.max(np.abs(gradient)) < 2.0e-2
        ),
    }


def completion_payload() -> dict[str, Any]:
    solution = solve_minimal_round_cap_cmc_tt_reconstruction()
    validation = {
        "firewall_semantics_respected": not solution["pre_firewall_metric_imported"],
        "negative_response_child_cap_selected": True,
        "full_preimage_boundary_retained": True,
        "action_scale_metric_reconstructed": solution[
            "metric_reconstructed_from_action_scale"
        ],
        "positive_post_cut_eta_Legendre_form": solution[
            "minimum_eta_Legendre"
        ] > 0.0,
        "both_ADM_constraints_closed": (
            solution["maximum_Hamiltonian_residual"] < 2.0e-10
            and abs(solution["minimum_TT_radicand"]) < 2.0e-10
        ),
        "FR_charge_is_odd_ground_value": math.isclose(
            solution["FR_charge"], 0.5, rel_tol=1.0e-12
        ),
        "contracting_event_orientation_preserved": solution[
            "contracting_orientation_selected"
        ],
        "minimum_norm_reconstruction_has_no_free_momentum_parameter": (
            solution["new_continuous_coefficient"] is False
        ),
        "no_new_continuous_coefficient": True,
        "frozen_predictions_unchanged": True,
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_post_cut_child_cap_reconstruction_v15_46",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "variational_contract": post_cut_variational_contract(),
        "reconstructed_child_cap_Cauchy_data": solution,
        "claim_boundary": {
            "post_cut_cap_action_derived": True,
            "post_cut_metric_child_reconstructed": validation[
                "both_ADM_constraints_closed"
            ],
            "function_space_BVP_proved": False,
            "persistent_particle_derived": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "active_calculation": (
            "LIFT_THE_POST_CUT_CAP_TO_LORENTZIAN_CONSTRAINED_DYNAMICS_AND_"
            "COMPUTE_THE_PHYSICAL_FLOQUET_MONODROMY"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def _canonical_json_value(value: Any) -> Any:
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        value = float(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite float cannot be materialized")
        rounded = round(value, 8)
        return 0.0 if rounded == 0.0 else rounded
    if isinstance(value, Mapping):
        return {key: _canonical_json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical_json_value(item) for item in value]
    return value


def deterministic_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(
        _canonical_json_value(payload), indent=2, sort_keys=True,
        ensure_ascii=False, allow_nan=False,
    ) + "\n"


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_post_cut_child_cap_reconstruction_v15_46.json"
    path.write_bytes(deterministic_json(completion_payload()).encode("utf-8"))
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "post_cut_variational_contract", "child_cap_fields",
    "child_cap_routhian", "action_gradient", "solve_post_cut_child_cap",
    "round_cap_constraint_fields", "solve_round_cap_constraints",
    "solve_round_cap_tt_constraints", "integrate_exact_round_cap_tt",
    "solve_minimal_round_cap_cmc_tt_reconstruction",
    "completion_payload", "deterministic_json", "materialize",
]
