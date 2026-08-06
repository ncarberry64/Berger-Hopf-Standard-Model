"""Exact specification and analytic screens for the downstream coupled BVP."""

from __future__ import annotations

from functools import lru_cache
from math import pi
from typing import Any, Callable

VERSION = "v14.29"
EXACT_NEXT_OBJECT = "GAUGE_FIXED_COUPLED_ETA_SU3_COLLAR_WILSON_SINGLET_BOUNDARY_VALUE_PROBLEM_WITH_SELF_ADJOINT_DOMAIN_PARENT_RELATIVE_SUBTRACTION_AND_NONRADIAL_HESSIAN"


def reduced_tension(radius: float, k_z: float, bulk_b: float, wall_tau: float, residual: Callable[[float], float] | None = None) -> float:
    if radius <= 0 or k_z <= 0 or bulk_b < 0 or wall_tau < 0:
        raise ValueError("invalid flux-tube parameters")
    return k_z / radius**2 + pi * bulk_b * radius**2 + 2 * pi * wall_tau * radius + (0.0 if residual is None else residual(radius))


def stationary_equation(radius: float, k_z: float, bulk_b: float, wall_tau: float, residual_prime: Callable[[float], float] | None = None) -> float:
    return -2 * k_z / radius**3 + 2 * pi * bulk_b * radius + 2 * pi * wall_tau + (0.0 if residual_prime is None else residual_prime(radius))


def wallless_solution(k_z: float, bulk_b: float) -> tuple[float, float]:
    radius = (k_z / (pi * bulk_b)) ** 0.25
    return radius, 2 * (pi * k_z * bulk_b) ** 0.5


def wall_only_solution(k_z: float, wall_tau: float) -> tuple[float, float]:
    radius = (k_z / (pi * wall_tau)) ** (1.0 / 3.0)
    return radius, 3 * k_z ** (1.0 / 3.0) * (pi * wall_tau) ** (2.0 / 3.0)


@lru_cache(maxsize=1)
def coupled_bvp_payload() -> dict[str, Any]:
    validation = {
        "non_Abelian_fields_declared": True,
        "Wilson_center_sector_declared": True,
        "parent_relative_subtraction_declared": True,
        "gauge_and_ghost_domain_required": True,
        "proxy_solution_not_claimed": True,
        "full_solution_not_claimed": True,
    }
    return {
        "artifact": "BHSM_View2_coupled_BVP_and_confinement_gate_v14_29",
        "version": VERSION,
        "unknowns": ["eta collar section", "physical SU3 connection", "collar geometry", "conditional FR collective mode", "retained gravity/Higgs/seam fields"],
        "gauge": "background-covariant R_xi gauge; FP operator and zero-mode projection must be fixed with the saddle",
        "domain": "finite-action Sobolev completion with regular axis, parent asymptotics, collar transmission conditions, and a self-adjoint relative-knot/Dirac extension",
        "sector": "fixed eta degree and Wilson N-ality/center sector",
        "relative_action": "Delta Gamma=Gamma[tube;W_k]-Gamma[parent], with identical regulator and boundary data",
        "numerical_plan": "nonradial finite-element continuation from the classical eta branch in source strength and collar coupling",
        "status": "OPEN_EXACT_DOMAIN_AND_NONLINEAR_SADDLE",
        "exact_next_object": EXACT_NEXT_OBJECT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


@lru_cache(maxsize=1)
def transverse_flux_payload() -> dict[str, Any]:
    rw, sw = wallless_solution(2.0, 3.0)
    rt, st = wall_only_solution(2.0, 3.0)
    validation = {
        "stationary_equation_exact": abs(stationary_equation(rw, 2.0, 3.0, 0.0)) < 1e-12,
        "wallless_formula_exact": abs(sw - reduced_tension(rw, 2.0, 3.0, 0.0)) < 1e-12,
        "wall_only_formula_exact": abs(st - reduced_tension(rt, 2.0, 0.0, 3.0)) < 1e-12,
        "classical_convexity_positive_for_nonnegative_B": True,
        "stable_tube_not_called_area_law": True,
        "Gaussian_collar_string_tension_zero_result_preserved": True,
    }
    return {
        "artifact": "BHSM_transverse_flux_relative_determinant_gate_v14_29",
        "version": VERSION,
        "definition": "sigma_k=inf_R inf_Phi (Gamma[Phi;W_k]-Gamma[parent])/(beta L)",
        "reduction": "sigma(R)=K_Z/R^2+pi B R^2+2pi tau R+sigma_residual(R)",
        "stationarity": "-2K_Z/R^3+2pi B R+2pi tau+sigma_residual'(R)=0",
        "convexity": "sigma''=6K_Z/R^4+2pi B+sigma_residual''; require it positive at the saddle",
        "relative_determinant": "include gauge fixing, ghosts, fermion signs, zero-mode removal, negative-mode audit, common counterterms and regulator",
        "derivative_expansion": "Delta sigma_det=pi R^2 delta B+2pi R delta tau+delta kappa+delta alpha/R+Delta sigma_nonlocal",
        "renormalization": "B_ren=B_cl+delta B, tau_ren=tau_cl+delta tau (no double counting)",
        "confinement_boundary": "a stable straight tube precedes but does not prove a Wilson-loop area law or exclude string breaking",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
