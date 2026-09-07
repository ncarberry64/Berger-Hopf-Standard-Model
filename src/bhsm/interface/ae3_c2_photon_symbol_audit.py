"""Audit finite-mode DtN ratios without changing the retained AE3 action.

The continuous spatial spectral parameter is a diagnostic extension of n**2,
not a new physical mode. Numerical witnesses use the explicitly stated finite
pole cutoff and leading-Frobenius Robin condition; they are not ball enclosures.
"""
from __future__ import annotations

import math

import numpy as np
from scipy.integrate import quad, solve_ivp

def stable_weight_and_log_derivative(rho: float) -> tuple[float, float]:
    """Evaluate the same Lambda=1-4*sigma**2 without cancellation at the pole."""
    if not math.isfinite(rho) or not 0 < rho <= math.pi/2:
        raise ValueError("require 0<rho<=pi/2")
    x = 2*rho
    if x < 0.1:
        # delta=sigma+1/2=(x-sin(x))/(2*pi); terms through x**17.
        difference = math.fsum((-1)**(k+1)*x**(2*k+1)/math.factorial(2*k+1)
                               for k in range(1, 9))
    else:
        difference = x-math.sin(x)
    delta = difference/(2*math.pi)
    delta_prime = 2*math.sin(rho)**2/math.pi
    return (4*delta*(1-delta),
            delta_prime*(1-2*delta)/(delta*(1-delta)))


def spectral_solution(spatial_eigenvalue: float = 4.0, q_squared: float = 0.0,
                      *, epsilon: float = 1.0e-3, rtol: float = 1.0e-11):
    """Integrate the logarithmic derivative and both parameter sensitivities.

    With y=u'/u, evolve y, d_s y, d_q2 y and log(u). This removes arbitrary
    amplitude underflow at higher modes. The same singular endpoint exponent
    alpha=(-3+sqrt(9+4s))/2 sets the finite-cutoff Robin data.
    """
    s, q2 = float(spatial_eigenvalue), float(q_squared)
    if (not all(math.isfinite(v) for v in (s, q2, epsilon, rtol))
            or s <= 0 or q2 > s or not 0 < epsilon <= 0.05
            or not 0 < rtol <= 1.0e-4):
        raise ValueError("require s>0, q_squared<=s and finite positive cutoff/tolerance")
    root = math.sqrt(9.0 + 4.0*s)
    alpha = 2.0*s/(3.0 + root)

    def equation(rho, state):
        y, ys, yq, _ = state
        a = 1.0/math.tan(rho) + stable_weight_and_log_derivative(rho)[1]
        c = 1.0/math.sin(rho)**2
        return (-a*y + s*c - q2 - y*y,
                c - (a + 2*y)*ys, -1 - (a + 2*y)*yq, y)

    result = solve_ivp(
        equation, (epsilon, math.pi/2),
        (alpha/epsilon, 1.0/(root*epsilon), 0.0, 0.0),
        method="DOP853", rtol=rtol, atol=rtol*0.01,
        max_step=0.002, dense_output=True,
    )
    if not result.success or not np.all(np.isfinite(result.y)):
        raise ArithmeticError("spectral sensitivity integration failed")
    return result


def spectral_dtn(spatial_eigenvalue: float = 4.0, q_squared: float = 0.0,
                 *, epsilon: float = 1.0e-3) -> float:
    return float(spectral_solution(spatial_eigenvalue, q_squared,
                                   epsilon=epsilon).y[0, -1])


def spectral_witness(level: int = 2, *, epsilon: float = 1.0e-3) -> dict:
    """Compare static quotient, spectral slope and independent energy integrals."""
    if isinstance(level, bool) or int(level) != level or level < 2:
        raise ValueError("physical coexact level must be an integer >=2")
    s = float(level*level)
    sol = spectral_solution(s, epsilon=epsilon)
    n0, ns, nq, log_end = map(float, sol.y[:, -1])

    def integral(kind):
        def integrand(rho):
            y, _, _, log_u = sol.sol(rho)
            u2 = math.exp(2*(float(log_u)-log_end))
            w = stable_weight_and_log_derivative(rho)[0]
            if kind == "electric":
                return w*math.sin(rho)*u2
            if kind == "magnetic":
                return w/math.sin(rho)*u2
            return w*math.sin(rho)*float(y)**2*u2
        return quad(integrand, epsilon, math.pi/2,
                    epsabs=1.0e-11, epsrel=1.0e-11, limit=300)[0]

    electric, magnetic, radial = (integral(k) for k in
                                   ("electric", "magnetic", "radial"))
    root = math.sqrt(9 + 4*s)
    alpha = 2*s/(3 + root)
    boundary = stable_weight_and_log_derivative(epsilon)[0]*math.sin(epsilon)*math.exp(-2*log_end)
    robin_energy = boundary*alpha/epsilon
    robin_slope = boundary/(root*epsilon)
    h = 1.0e-3
    ns_fd = (spectral_dtn(s+h, epsilon=epsilon) -
             spectral_dtn(s-h, epsilon=epsilon))/(2*h)
    nq_fd = (spectral_dtn(s, h, epsilon=epsilon) -
             spectral_dtn(s, -h, epsilon=epsilon))/(2*h)
    return {
        "level": int(level), "spatial_eigenvalue": s, "pole_cutoff": epsilon,
        "N_static": n0, "dN_d_spatial_eigenvalue": ns, "minus_dN_d_q_squared": -nq,
        "static_quotient": n0/s,
        "complete_mode_ratio": s*(-nq)/n0,
        "derivative_ratio": (-nq)/ns,
        "electric_integral": electric, "magnetic_integral": magnetic,
        "radial_gradient_integral": radial,
        "finite_cutoff_Robin_energy": robin_energy,
        "finite_cutoff_Robin_spatial_derivative": robin_slope,
        "static_energy_residual": abs(n0 - (radial + s*magnetic + robin_energy)),
        "spectral_envelope_residual": abs(ns - (magnetic + robin_slope)),
        "frequency_envelope_residual": abs(-nq - electric),
        "spatial_centered_difference_residual": abs(ns - ns_fd),
        "frequency_centered_difference_residual": abs(nq - nq_fd),
        "static_quotient_minus_spatial_derivative": n0/s - ns,
        "N_over_level": n0/level,
    }


def flat_half_space_control(spatial_eigenvalue: float = 4.0) -> dict:
    """Analytic N(s,q2)=sqrt(s-q2), on the spacelike/decaying branch.

    This control tests the diagnostic logic; it is not substituted into BHSM.
    """
    s = float(spatial_eigenvalue)
    if not math.isfinite(s) or s <= 0:
        raise ValueError("finite positive spatial eigenvalue required")
    n0 = math.sqrt(s)
    slope = 1.0/(2*n0)
    return {"N_static": n0, "minus_dN_d_q_squared": slope,
            "dN_d_spatial_eigenvalue": slope,
            "complete_mode_ratio": 0.5, "derivative_ratio": 1.0,
            "depends_only_on_s_minus_q_squared": True,
            "exact_local_second_order_Maxwell_kernel": False,
            "BHSM_replacement": False}
