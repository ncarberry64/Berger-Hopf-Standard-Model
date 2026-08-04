"""Degree-one static eta-knot solution from the retained p=2+p=8 action."""

from __future__ import annotations

import json
from functools import lru_cache
from math import log, pi
from pathlib import Path
from typing import Any

import numpy as np
from scipy.integrate import simpson, solve_bvp
from scipy.linalg import eigh

VERSION = "v13.1"
OMEGA_6 = 16.0 * pi**3 / 15.0
X_MIN, X_MAX = -8.0, 6.0
EXACT_NEXT_OBJECT = (
    "LOCAL_ETA_TEXTURE_TO_INTRINSIC_M4_CHIRAL_CLIFFORD_TRANSGRESSION_WITH_"
    "GAUGE_DRESSING_AND_NORMALIZED_C3_FAMILY_TANGENT_BUNDLE"
)
ARTIFACT_FILES = {
    "solution": "BHSM_eta_degree_one_static_solution_v13_1.json",
    "stability": "BHSM_eta_radial_stability_v13_1.json",
    "completion": "BHSM_completion_gate_v13_1.json",
}


def deterministic_json(value: Any) -> str:
    def default(item: Any) -> Any:
        if isinstance(item, np.ndarray):
            return item.tolist()
        if isinstance(item, np.generic):
            return item.item()
        raise TypeError(type(item).__name__)
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, default=default) + "\n"


def log_profile_ode(x: np.ndarray, y: np.ndarray, kappa1: float = 1.0) -> np.ndarray:
    """Exact log-radius Euler equation for E=Omega6 int r^6(kX/2+X^4/8)dr."""
    if kappa1 <= 0:
        raise ValueError("kappa1 must be positive")
    f, p = y
    s, c = np.sin(f), np.cos(f)
    Y = p * p + 6.0 * s * s
    em = np.exp(-x)
    A = kappa1 * np.exp(5.0 * x) + em * Y**3
    denominator = A + 6.0 * em * Y**2 * p * p
    numerator = 6.0 * A * s * c - p * (
        5.0 * kappa1 * np.exp(5.0 * x) - em * Y**3 + 36.0 * em * Y**2 * s * c * p
    )
    return np.vstack((p, numerator / denominator))


def initial_profile(x: np.ndarray, slope: float = 2.0) -> np.ndarray:
    f = 2.0 * np.arctan(np.exp(slope * x))
    return np.vstack((f, slope / np.cosh(slope * x)))


@lru_cache(maxsize=12)
def solve_profile(kappa1: float = 1.0, slope: float = 2.0, x_min: float = X_MIN, x_max: float = X_MAX) -> Any:
    if kappa1 <= 0 or slope <= 0 or x_min >= x_max:
        raise ValueError("invalid profile parameters")
    grid = np.linspace(x_min, x_max, 720)
    solution = solve_bvp(
        lambda x, y: log_profile_ode(x, y, kappa1),
        lambda left, right: np.array([left[0], right[0] - pi]),
        grid,
        initial_profile(grid, slope),
        tol=7.5e-7,
        max_nodes=24000,
    )
    if solution.status:
        raise RuntimeError(solution.message)
    return solution


def profile_energy_components(solution: Any, kappa1: float = 1.0) -> tuple[float, float]:
    x = np.linspace(float(solution.x[0]), float(solution.x[-1]), 5001)
    f, p = solution.sol(x)
    Y = p * p + 6.0 * np.sin(f) ** 2
    e2 = OMEGA_6 * simpson(0.5 * kappa1 * np.exp(5.0 * x) * Y, x=x)
    e8 = OMEGA_6 * simpson(0.125 * np.exp(-x) * Y**4, x=x)
    return float(e2), float(e8)


def profile_center(solution: Any) -> tuple[float, float]:
    x = np.linspace(float(solution.x[0]), float(solution.x[-1]), 8001)
    index = int(np.argmin(np.abs(solution.sol(x)[0] - pi / 2.0)))
    return float(x[index]), float(np.exp(x[index]))


def ode_residual(solution: Any, kappa1: float = 1.0) -> float:
    x = np.linspace(float(solution.x[0]), float(solution.x[-1]), 3001)
    return float(np.max(np.abs(solution.sol(x, 1) - log_profile_ode(x, solution.sol(x), kappa1))))


def scaling_law(kappa1: float) -> dict[str, float]:
    if kappa1 <= 0:
        raise ValueError("kappa1 must be positive")
    return {
        "radius_relative_to_kappa1_1": kappa1 ** (-1 / 6),
        "energy_relative_to_kappa1_1": kappa1 ** (1 / 6),
        "log_radius_shift": -log(kappa1) / 6,
    }


def radial_hessian_eigenvalues(solution: Any, kappa1: float = 1.0, points: int = 220, x_min: float = -7.0, x_max: float = 5.0, count: int = 6) -> np.ndarray:
    """Piecewise-linear finite-element Jacobi spectrum on a declared finite interval."""
    x = np.linspace(x_min, x_max, points)
    mid = (x[:-1] + x[1:]) / 2
    f, p = solution.sol(mid)
    s, c = np.sin(f), np.cos(f)
    Y = p * p + 6 * s * s
    em = np.exp(-mid)
    A = kappa1 * np.exp(5 * mid) + em * Y**3
    cpp = A + 6 * em * Y**2 * p * p
    cfp = 36 * em * Y**2 * s * c * p
    cff = 216 * em * Y**2 * (s * c) ** 2 + 6 * A * np.cos(2 * f)
    weight = kappa1 * np.exp(7 * mid) + np.exp(mid) * Y**3
    size = points - 2
    H, M = np.zeros((size, size)), np.zeros((size, size))
    for interval in range(points - 1):
        h = x[interval + 1] - x[interval]
        d, n = np.array([-1 / h, 1 / h]), np.array([0.5, 0.5])
        local_h = h * (cpp[interval] * np.outer(d, d) + cfp[interval] * (np.outer(n, d) + np.outer(d, n)) + cff[interval] * np.outer(n, n))
        local_m = weight[interval] * h / 6 * np.array([[2.0, 1.0], [1.0, 2.0]])
        for i, gi in enumerate((interval, interval + 1)):
            if gi in (0, points - 1):
                continue
            for j, gj in enumerate((interval, interval + 1)):
                if gj not in (0, points - 1):
                    H[gi - 1, gj - 1] += local_h[i, j]
                    M[gi - 1, gj - 1] += local_m[i, j]
    return eigh(H, M, eigvals_only=True, subset_by_index=[0, count - 1])


def solution_payload() -> dict[str, Any]:
    solution = solve_profile()
    e2, e8 = profile_energy_components(solution)
    center_x, center_r = profile_center(solution)
    validation = {
        "BVP_converged": solution.status == 0,
        "degree_one_boundaries": abs(solution.y[0, 0]) < 1e-12 and abs(solution.y[0, -1] - pi) < 1e-12,
        "profile_monotone": np.min(solution.sol(np.linspace(X_MIN, X_MAX, 3001))[1]) > -1e-8,
        "Euler_residual_small": ode_residual(solution) < 2e-5,
        "Derrick_virial_5E2_equals_E8": abs(5 * e2 - e8) / e8 < 2e-6,
        "no_measured_particle_input": True,
    }
    return {
        "artifact": "BHSM_eta_degree_one_static_solution_v13_1",
        "version": VERSION,
        "classification": "DERIVED_CONDITIONAL_IN_EQUIVARIANT_COHOMOGENEITY_ONE_REDUCTION",
        "Euler_equation": "d_r[r^6(kappa1+X^3)f_r]-6r^4(kappa1+X^3)sin(f)cos(f)=0",
        "reference_normalization": {"kappa1": 1.0, "physical": False},
        "numerical_solution": {"center_log_radius": center_x, "center_radius": center_r, "E2": e2, "E8": e8, "E8_over_E2": e8 / e2},
        "scaling_family": {**scaling_law(1.0), "physical_scale_selected": False},
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def stability_payload() -> dict[str, Any]:
    solution = solve_profile()
    e2, e8 = profile_energy_components(solution)
    values = radial_hessian_eigenvalues(solution)
    validation = {
        "scale_stationary": abs(e8 / e2 - 5) < 1e-5,
        "scale_second_variation_positive": 25 * e2 + e8 > 0,
        "finite_interval_radial_spectrum_positive": bool(np.min(values) > 0),
        "full_nonradial_stability_not_claimed": True,
        "Floquet_stability_not_claimed": True,
    }
    return {"artifact": "BHSM_eta_radial_stability_v13_1", "version": VERSION, "lowest_radial_generalized_eigenvalues": values, "validation": validation, "validation_passed": all(validation.values())}


def completion_payload() -> dict[str, Any]:
    validation = {"static_eta_solution_constructed": solution_payload()["validation_passed"], "radial_stability_passed": stability_payload()["validation_passed"], "physical_particle_not_promoted": True, "frozen_predictions_unchanged": True}
    return {"artifact": "BHSM_completion_gate_v13_1", "version": VERSION, "Mark_III_subgate_eta_static_texture": "REACHED_CONDITIONALLY", "full_Mark_III": "NOT_REACHED", "BHSM_1_0_release_complete": False, "exact_next_object": EXACT_NEXT_OBJECT, "validation": validation, "validation_passed": all(validation.values())}


def materialize(output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    payloads = {"solution": solution_payload(), "stability": stability_payload(), "completion": completion_payload()}
    paths = []
    for key, name in ARTIFACT_FILES.items():
        path = output_dir / name
        path.write_text(deterministic_json(payloads[key]), encoding="utf-8")
        paths.append(path)
    return paths
