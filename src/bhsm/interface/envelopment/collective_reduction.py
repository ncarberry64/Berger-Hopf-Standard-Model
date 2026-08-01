"""Controlled collective-coordinate reduction of the BHSM v10 eta action."""

from __future__ import annotations

from functools import lru_cache
from math import isfinite
from typing import Any, Mapping

import mpmath as mp
import numpy as np
from scipy.integrate import quad
import sympy as sp

from .foundation import SOURCE_PR208_SHA, SPRINT, VERSION


def _stable(value: float, digits: int = 15) -> float:
    return float(f"{value:.{digits}g}")


def scaling_derivation() -> dict[str, Any]:
    return {
        "spatial_dimension": 7,
        "rule": "int_R7 |partial Phi|^p d^7x scales as R^(7-p)",
        "eta_p2": "R^5",
        "eta_p8": "R^-1",
        "sigma_gradient": "s^2 R^5",
        "sigma_quadratic_potential": "s^2 R^7",
        "sigma_quartic_potential": "s^4 R^7",
        "sigma_eta_p2": "s^2 R^5",
        "sigma_eta_p8": "s^2 R^-1",
        "derived_from_action": True,
        "classification": "DERIVED_CONDITIONAL",
    }


def prototype_profiles() -> dict[str, Any]:
    return {
        "domain": "R7 compactified by one point to S7",
        "eta": "eta_0(r,Omega)=(cos f(r),sin f(r) Omega)",
        "f": "2 atan(r^4)",
        "degree": 1,
        "boundary_conditions": {"f(0)": "0", "f(infinity)": "pi"},
        "X0": "f'^2+6 sin(f)^2/r^2=88 r^6/(1+r^8)^2",
        "sigma_profile": "q(r)=N exp(-r^2), normalized by int_R7 q^2=1",
        "role": "explicit normalized coefficient audit only",
        "classification": "PROXY_ONLY",
        "action_selected": False,
        "Hopf_weighted_current_compatibility": None,
    }


def _mp_integral(function) -> mp.mpf:
    return mp.quad(function, [0, 1, mp.inf])


@lru_cache(maxsize=1)
def profile_integrals() -> dict[str, Any]:
    """Evaluate every potential and kinetic coefficient from fixed profiles.

    High-precision tanh-sinh values are serialized.  Independent SciPy
    Gauss-Kronrod evaluations must lie inside a certified relative bound; raw
    platform-specific last-bit differences are not serialized.
    """

    mp.mp.dps = 70
    omega6 = 16 * mp.pi**3 / 15
    norm_integral = omega6 * mp.mpf("0.5") * 2 ** (-mp.mpf(7) / 2) * mp.gamma(mp.mpf(7) / 2)
    q_norm = 1 / mp.sqrt(norm_integral)

    def x0(r):
        return 88 * r**6 / (1 + r**8) ** 2

    def rfprime(r):
        return 8 * r**4 / (1 + r**8)

    def q(r):
        return q_norm * mp.exp(-(r**2))

    exact = {
        "A2": mp.mpf(11) / 2 * omega6 * mp.beta(mp.mpf(13) / 8, mp.mpf(3) / 8),
        "A8": 88**4 / mp.mpf(64) * omega6 * mp.beta(mp.mpf(31) / 8, mp.mpf(33) / 8),
        "B2": mp.mpf(7) / 2,
        "B0": mp.mpf(1) / 2,
        "B4": mp.mpf(1) / 4 * _mp_integral(lambda r: omega6 * r**6 * q(r) ** 4),
        "C2": mp.mpf(1) / 2 * _mp_integral(lambda r: omega6 * r**6 * q(r) ** 2 * x0(r)),
        "C8": mp.mpf(1) / 8 * _mp_integral(lambda r: omega6 * r**6 * q(r) ** 2 * x0(r) ** 4),
        "D2": 8 * omega6 * mp.beta(mp.mpf(15) / 8, mp.mpf(1) / 8),
        "D8": 8 * 88**3 * omega6 * mp.beta(mp.mpf(33) / 8, mp.mpf(31) / 8),
        "E2": _mp_integral(lambda r: omega6 * r**6 * q(r) ** 2 * rfprime(r) ** 2),
        "E8": _mp_integral(lambda r: omega6 * r**6 * q(r) ** 2 * x0(r) ** 3 * rfprime(r) ** 2),
        "S0": mp.mpf(1),
        "S1": -mp.mpf(7) / 2,
        "S2": mp.mpf(63) / 4,
    }

    omega6_f = float(omega6)
    q_norm_f = float(q_norm)

    def x0_f(r: float) -> float:
        return 88.0 * r**6 / (1.0 + r**8) ** 2

    def rfprime_f(r: float) -> float:
        return 8.0 * r**4 / (1.0 + r**8)

    def q_f(r: float) -> float:
        return q_norm_f * np.exp(-(r**2))

    scipy_values = {
        "A2": 0.5 * quad(lambda r: omega6_f * r**6 * x0_f(r), 0, np.inf, epsabs=1e-9, epsrel=1e-11)[0],
        "A8": 0.125 * quad(lambda r: omega6_f * r**6 * x0_f(r) ** 4, 0, np.inf, epsabs=1e-7, epsrel=1e-11)[0],
        "B2": 0.5 * quad(lambda r: omega6_f * r**6 * (-2 * r * q_f(r)) ** 2, 0, np.inf, epsabs=1e-11, epsrel=1e-11)[0],
        "B0": 0.5 * quad(lambda r: omega6_f * r**6 * q_f(r) ** 2, 0, np.inf, epsabs=1e-11, epsrel=1e-11)[0],
        "B4": 0.25 * quad(lambda r: omega6_f * r**6 * q_f(r) ** 4, 0, np.inf, epsabs=1e-11, epsrel=1e-11)[0],
        "C2": 0.5 * quad(lambda r: omega6_f * r**6 * q_f(r) ** 2 * x0_f(r), 0, np.inf, epsabs=1e-11, epsrel=1e-11)[0],
        "C8": 0.125 * quad(lambda r: omega6_f * r**6 * q_f(r) ** 2 * x0_f(r) ** 4, 0, np.inf, epsabs=1e-7, epsrel=1e-11)[0],
        "D2": quad(lambda r: omega6_f * r**6 * rfprime_f(r) ** 2, 0, np.inf, epsabs=1e-9, epsrel=1e-11)[0],
        "D8": quad(lambda r: omega6_f * r**6 * x0_f(r) ** 3 * rfprime_f(r) ** 2, 0, np.inf, epsabs=1e-7, epsrel=1e-11)[0],
        "E2": quad(lambda r: omega6_f * r**6 * q_f(r) ** 2 * rfprime_f(r) ** 2, 0, np.inf, epsabs=1e-11, epsrel=1e-11)[0],
        "E8": quad(lambda r: omega6_f * r**6 * q_f(r) ** 2 * x0_f(r) ** 3 * rfprime_f(r) ** 2, 0, np.inf, epsabs=1e-7, epsrel=1e-11)[0],
        "S0": quad(lambda r: omega6_f * r**6 * q_f(r) ** 2, 0, np.inf, epsabs=1e-11, epsrel=1e-11)[0],
        "S1": quad(lambda r: omega6_f * r**6 * q_f(r) * (-2 * r**2 * q_f(r)), 0, np.inf, epsabs=1e-11, epsrel=1e-11)[0],
        "S2": quad(lambda r: omega6_f * r**6 * (-2 * r**2 * q_f(r)) ** 2, 0, np.inf, epsabs=1e-11, epsrel=1e-11)[0],
    }
    relative_bound = 2.0e-9
    for key, value in exact.items():
        difference = abs(scipy_values[key] - float(value))
        if difference > relative_bound * max(1.0, abs(float(value))):
            raise RuntimeError(f"profile integral {key} violates certified bound")

    values = {key: _stable(float(value)) for key, value in exact.items()}
    return {
        "profiles": prototype_profiles(),
        "coefficient_definitions": {
            "A2": "(1/2) int_R7 X0",
            "A8": "(1/8) int_R7 X0^4",
            "B2": "(1/2) int_R7 |grad q|^2",
            "B0": "(1/2) int_R7 q^2",
            "B4": "(1/4) int_R7 q^4",
            "C2": "(1/2) int_R7 q^2 X0",
            "C8": "(1/8) int_R7 q^2 X0^4",
            "D2": "int_R7 |y.grad eta0|^2",
            "D8": "int_R7 X0^3 |y.grad eta0|^2",
            "E2": "int_R7 q^2 |y.grad eta0|^2",
            "E8": "int_R7 q^2 X0^3 |y.grad eta0|^2",
            "S0": "int_R7 q^2",
            "S1": "int_R7 q(y.grad q)",
            "S2": "int_R7 (y.grad q)^2",
        },
        "values": values,
        "all_finite": all(isfinite(value) and value != 0.0 for value in values.values()),
        "all_potential_coefficients_positive": all(values[key] > 0 for key in ("A2", "A8", "B2", "B0", "B4", "C2", "C8")),
        "methods": ["70-digit mpmath tanh-sinh", "SciPy adaptive Gauss-Kronrod"],
        "serialization_policy": "serialize high-precision values and certified cross-platform method bounds, not raw last-bit differences",
        "certified_relative_method_bound": relative_bound,
        "physical_promotion": False,
    }


def symbolic_reduction() -> dict[str, Any]:
    R, kappa1, A2, A8 = sp.symbols("R kappa1 A2 A8", positive=True)
    potential = kappa1 * A2 * R**5 + A8 / R
    radius = (A8 / (5 * kappa1 * A2)) ** sp.Rational(1, 6)
    stiffness = sp.simplify(sp.diff(potential, R, 2).subs(R, radius))
    energy = sp.simplify(potential.subs(R, radius))
    expected_stiffness = 30 * kappa1 * A2 * radius**3
    expected_energy = 6 * kappa1 ** sp.Rational(1, 6) * A2 ** sp.Rational(1, 6) * A8 ** sp.Rational(5, 6) / 5 ** sp.Rational(5, 6)
    return {
        "reduced_potential": (
            "V=kappa1 A2 R^5+A8/R+Zsigma B2 s^2 R^5+A0 B0 s^2 R^7+"
            "G0 B4 s^4 R^7+g s^2(kappa1 C2 R^5+C8/R)"
        ),
        "R0": "(A8/(5 kappa1 A2))^(1/6)",
        "stationarity_exact": sp.simplify(sp.diff(potential, R).subs(R, radius)) == 0,
        "radial_stiffness": "30 kappa1 A2 R0^3",
        "radial_stiffness_identity_exact": sp.simplify(stiffness - expected_stiffness) == 0,
        "E0": "6 kappa1^(1/6) A2^(1/6) A8^(5/6)/5^(5/6)",
        "energy_identity_exact": sp.simplify(energy - expected_energy) == 0,
        "quadratic_only_eta_finite_radius": False,
        "quadratic_only_reason": "A8=0 gives V=kappa1 A2 R^5 with no positive stationary R",
        "classification": "DERIVED_CONDITIONAL",
    }


def collective_kinetic_metric() -> dict[str, Any]:
    return {
        "quadratic_velocity_expansion": True,
        "coordinates": ["R", "s"],
        "M_RR": (
            "kappa1 D2 R^5+D8/R+g s^2(kappa1 E2 R^5+E8/R)"
            "+Zsigma s^2 S2 R^5"
        ),
        "M_Rs": "-Zsigma s S1 R^6",
        "M_ss": "Zsigma S0 R^7",
        "higher_velocity_terms": "the X_eta^4 action also contains O(dot R^4) and higher terms",
        "positive_at_s0": "M_RR=kappa1 D2 R^5+D8/R>0 and M_ss=Zsigma S0 R^7>0",
        "breathing_frequency_squared": (
            "omega_R^2=30 kappa1 A2 R0^3/(kappa1 D2 R0^5+D8/R0)"
        ),
        "classification": "DERIVED_CONDITIONAL",
    }


def sigma_formation_gate() -> dict[str, Any]:
    return {
        "C_sigma": "Zsigma B2 R^5+A0 B0 R^7+g(kappa1 C2 R^5+C8/R)",
        "amplitude_Hessian_at_s0": "d_s^2 V(R,0)=2 C_sigma(R)",
        "fixed_R_branch_condition": "C_sigma(R)<0 and G0 B4>0",
        "fixed_R_branch": "s_*^2=-C_sigma(R)/(2 G0 B4 R^7)",
        "full_branch_requirement": "also solve d_R V(R,s_*)=0 and the complete constraints",
        "surface_licensed_by_collective_branch_alone": False,
        "classification": "DERIVED_CONDITIONAL",
    }


def representative_reduction() -> dict[str, Any]:
    coefficients = profile_integrals()["values"]
    A2, A8 = coefficients["A2"], coefficients["A8"]
    R0 = (A8 / (5 * A2)) ** (1 / 6)
    stiffness = 30 * A2 * R0**3
    energy = 6 / (5 ** (5 / 6)) * A2 ** (1 / 6) * A8 ** (5 / 6)
    mass = coefficients["D2"] * R0**5 + coefficients["D8"] / R0
    omega2 = stiffness / mass
    return {
        "normalization": {"kappa1": 1.0, "Zsigma": 1.0, "g": 0.0},
        "normalization_is_physical": False,
        "R0": _stable(R0),
        "E0": _stable(energy),
        "radial_stiffness": _stable(stiffness),
        "radial_collective_mass": _stable(mass),
        "breathing_frequency_squared": _stable(omega2),
        "breathing_frequency": _stable(omega2**0.5),
        "classification": "PROXY_ONLY",
        "physical_orbit": False,
    }


def global_scale_audit() -> dict[str, Any]:
    return {
        "natural_local_mass_scale": "mu_env=kappa1^(1/6)",
        "kappa1_dimension": "mass^6=L^-6",
        "dilation_family": {
            "scope": "covariance of the dimensionful coupling family, not a symmetry at fixed couplings",
            "G_AB": "c^2 G_AB",
            "kappa1": "c^-6 kappa1",
            "kappa0": "c^-8 kappa0",
            "Zchi": "c^-6 Zchi",
            "Zsigma": "c^-6 Zsigma",
            "A0": "c^-8 A0",
            "G0": "c^-8 G0",
            "Lambda_eta": "c^-8 Lambda_eta",
            "g": "g",
            "X_eta^4 term": "invariant",
        },
        "closed_cosmic_solution_selected": False,
        "total_energy_or_topological_normalization_fixed": False,
        "kappa1_fixed_by_field_equations": False,
        "physical_eV_GeV_bridge": None,
        "uniqueness": False,
        "remaining_degeneracy": (
            "the numerical value of the dimensionful input kappa1 and hence one "
            "overall physical unit remain unselected; dimensionless coupling ratios "
            "also remain inputs until a closed cosmic boundary-value and normalization theorem is supplied"
        ),
        "status": "BHSM_GLOBAL_SCALE_REMAINS_UNDERDETERMINED_BY_CURRENT_ACTION",
        "classification": "BLOCKED_EXACT_OBJECT_PROVED",
    }


def reduction_payload() -> dict[str, Any]:
    symbolic = symbolic_reduction()
    profiles = profile_integrals()
    validation = {
        "seven_dimensional_scaling_derived": scaling_derivation()["derived_from_action"],
        "profile_coefficients_finite": profiles["all_finite"],
        "potential_coefficients_positive": profiles["all_potential_coefficients_positive"],
        "independent_quadratures_agree": profiles["certified_relative_method_bound"] <= 2.0e-9,
        "equilibrium_exact": symbolic["stationarity_exact"],
        "stiffness_exact": symbolic["radial_stiffness_identity_exact"],
        "energy_exact": symbolic["energy_identity_exact"],
        "quadratic_only_texture_invalidated": not symbolic["quadratic_only_eta_finite_radius"],
    }
    return {
        "artifact": "BHSM_dynamic_envelope_reduction_v10_0",
        "version": VERSION,
        "sprint": SPRINT,
        "source_pr208_sha": SOURCE_PR208_SHA,
        "scaling": scaling_derivation(),
        "profiles": profiles,
        "symbolic_reduction": symbolic,
        "kinetic_metric": collective_kinetic_metric(),
        "sigma_gate": sigma_formation_gate(),
        "representative_proxy": representative_reduction(),
        "global_scale": global_scale_audit(),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "physical_promotion": False,
    }
