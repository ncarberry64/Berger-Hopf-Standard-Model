# Exact gravity-scalar closed-Horndeski kernel for the first physical mode.
#
# Specialization of Akama & Kobayashi, Phys. Rev. D 99, 043522 (2019),
# to the manuscript cubic-Galileon/KGB model:
#   G2 = X - V(T)
#   G3 = 2 X / Lambda^3
#   G4 = M_Pl^2 / 2
#   G5 = 0
#
# Units used by the repository: H0 = M_Pl = 1.
# Manuscript n=2 corresponds to literature closed-universe N=3,
# so k^2 = K(N^2-1) = 8K.
#
# Scope: pure gravity+scalar constraint kernel. Matter/radiation
# perturbations and the extra reduced topographic response remain separate.
from __future__ import annotations

import json
import math
from typing import Dict

import numpy as np

import background

MPL2 = 1.0


def alpha_quantities(v: float, E: float) -> Dict[str, float]:
    alpha_b = 2.0 * v**3 / (E * background.LAMBDA)
    alpha_k = (v / E) ** 2 + 6.0 * alpha_b
    dkin = alpha_k + 1.5 * alpha_b**2
    return {"alpha_B": alpha_b, "alpha_K": alpha_k, "D_kin": dkin}


def theta_sigma(v: float, E: float) -> tuple[float, float]:
    theta = E - v**3 / background.LAMBDA
    sigma = (
        0.5 * v**2
        + 12.0 * E * v**3 / background.LAMBDA
        - 3.0 * E**2
    )
    return theta, sigma


def r_ratio(v: float, E: float) -> float:
    theta, sigma = theta_sigma(v, E)
    return sigma / theta**2


def akama_factor_n2(v: float, E: float) -> float:
    r = r_ratio(v, E)
    return 5.0 / (8.0 + r)


def gs_n2(v: float, E: float) -> float:
    r = r_ratio(v, E)
    return 5.0 * (r + 3.0) / (r + 8.0)


def gs_n2_from_dkin(v: float, E: float) -> float:
    q = alpha_quantities(v, E)
    u = 1.0 - 0.5 * q["alpha_B"]
    return 5.0 * q["D_kin"] / (q["D_kin"] + 10.0 * u * u)


def constraint_solution_n2(
    a: float,
    v: float,
    E: float,
    zeta: float,
    zeta_dot: float,
) -> tuple[float, float]:
    theta, _ = theta_sigma(v, E)
    r = r_ratio(v, E)
    kappa = background.KCURV / (a * a)
    denom = r + 8.0

    delta_n = (
        5.0 / (theta * denom)
        * (zeta_dot - (kappa / theta) * zeta)
    )
    chi = (
        -(r + 3.0) / (kappa * denom) * zeta_dot
        - 5.0 / (theta * denom) * zeta
    )
    return delta_n, chi


def constraint_residuals_n2(
    a: float,
    v: float,
    E: float,
    zeta: float,
    zeta_dot: float,
) -> tuple[float, float]:
    delta_n, chi = constraint_solution_n2(a, v, E, zeta, zeta_dot)
    theta, sigma = theta_sigma(v, E)
    kappa = background.KCURV / (a * a)

    c1 = (
        sigma * delta_n
        + 8.0 * theta * kappa * chi
        + 3.0 * theta * zeta_dot
        + 5.0 * kappa * zeta
    )
    c2 = theta * delta_n - zeta_dot - kappa * chi
    return c1, c2


def formal_fs_n2_gravity_sector(N: float, y: np.ndarray) -> float:
    # Exact pure gravity+scalar Horndeski expression evaluated on the R1
    # background. This is not yet the complete matter+radiation stability
    # matrix.
    _, v, E = [float(x) for x in y]
    a = math.exp(N)
    _, dv_dN, dE_dN = background.rhs(N, np.asarray(y, dtype=float))

    theta, sigma = theta_sigma(v, E)
    dtheta_dN = dE_dN - 3.0 * v * v * dv_dN / background.LAMBDA

    dsigma_dN = (
        v * dv_dN
        + 12.0 / background.LAMBDA
        * (dE_dN * v**3 + 3.0 * E * v * v * dv_dN)
        - 6.0 * E * dE_dN
    )

    r = sigma / theta**2
    dr_dN = dsigma_dN / theta**2 - 2.0 * sigma * dtheta_dN / theta**3

    A = 5.0 / (8.0 + r)
    dA_dN = -5.0 * dr_dN / (8.0 + r) ** 2

    derivative_term = E / theta * (
        dA_dN + A - A * dtheta_dN / theta
    )
    curvature_term = A * background.KCURV / (
        a * a * theta * theta
    )
    return derivative_term - 1.0 + curvature_term


def diagnostics(sol, z: float) -> dict:
    N = math.log(1.0 / (1.0 + z))
    y = np.asarray(sol.sol(N), dtype=float)
    _, v, E = [float(x) for x in y]
    a = math.exp(N)
    alpha = alpha_quantities(v, E)
    theta, sigma = theta_sigma(v, E)
    r = sigma / theta**2

    return {
        "z": z,
        "theta": theta,
        "r": r,
        "D_kin": alpha["D_kin"],
        "G_S_n2": gs_n2(v, E),
        "G_S_n2_alpha_identity": gs_n2_from_dkin(v, E),
        "F_S_n2_gravity_sector_only": formal_fs_n2_gravity_sector(N, y),
        "kappa": background.KCURV / (a * a),
    }


def main() -> None:
    v0 = background.shoot_v0()
    sol = background.integrate(v0)
    zs = [10.0, 3.0, 2.1, 1.5, 1.0, 0.8, 0.5, 0.3, 0.0]
    payload = {
        "model": "R1",
        "scope": "pure gravity+scalar closed-Horndeski n=2 kernel",
        "matter_perturbations_included": False,
        "topographic_reduced_response_included": False,
        "rows": [diagnostics(sol, z) for z in zs],
    }
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
