"""Reference Branch R1 background integrator.

Units: H0 = M_Pl = 1.
The script solves the cubic-Galileon + linear-potential background on closed FLRW,
shoots V0 so E(a=1)=1, and prints a deterministic JSON summary.
"""
from __future__ import annotations
import json
import math
from dataclasses import dataclass, asdict
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

OMEGA_M0 = 0.31
OMEGA_R0 = 9.0e-5
OMEGA_K0 = -0.018
KCURV = -OMEGA_K0
LAMBDA = 1.0
Q = 3.0
Z_INITIAL = 100.0
A_INITIAL = 1.0 / (1.0 + Z_INITIAL)
N_INITIAL = math.log(A_INITIAL)

@dataclass(frozen=True)
class Params:
    omega_m0: float = OMEGA_M0
    omega_r0: float = OMEGA_R0
    omega_k0: float = OMEGA_K0
    lam: float = LAMBDA
    q: float = Q
    z_initial: float = Z_INITIAL

def _initial_state(v0: float):
    phi = 0.0
    E = math.sqrt(
        OMEGA_M0*A_INITIAL**-3
        + OMEGA_R0*A_INITIAL**-4
        + OMEGA_K0*A_INITIAL**-2
        + v0/3.0
    )
    for _ in range(100):
        J = 2.0*Q/(9.0*E)
        A = 6.0*E/LAMBDA
        v = (-1.0 + math.sqrt(1.0 + 4.0*A*J))/(2.0*A)
        rho_t = 0.5*v*v + v0 + 6.0*E*v**3/LAMBDA
        E_new = math.sqrt(
            OMEGA_M0*A_INITIAL**-3
            + OMEGA_R0*A_INITIAL**-4
            + rho_t/3.0
            - KCURV*A_INITIAL**-2
        )
        if abs(E_new-E) < 1e-15*E:
            E = E_new
            break
        E = E_new
    return np.array([phi, v, E], dtype=float)

def rhs(N: float, y: np.ndarray) -> np.ndarray:
    phi, v, E = y
    a = math.exp(N)
    rho_m = 3.0*OMEGA_M0*a**-3
    rho_r = 3.0*OMEGA_R0*a**-4
    J = v + 6.0*E*v*v/LAMBDA

    A11 = 1.0 + 12.0*E*v/LAMBDA
    A12 = 6.0*v*v/LAMBDA
    b1 = Q - 3.0*E*J

    A21 = 2.0*v*v/LAMBDA
    A22 = -2.0
    b2 = (
        rho_m + (4.0/3.0)*rho_r + v*v
        + 6.0*E*v**3/LAMBDA
        - 2.0*KCURV*a**-2
    )
    det = A11*A22 - A12*A21
    if abs(det) < 1e-14:
        raise RuntimeError("Background derivative matrix became singular.")

    dot_v = (b1*A22 - A12*b2)/det
    dot_E = (A11*b2 - b1*A21)/det
    return np.array([v/E, dot_v/E, dot_E/E], dtype=float)

def integrate(v0: float):
    return solve_ivp(
        rhs, (N_INITIAL, 0.0), _initial_state(v0),
        method="DOP853", rtol=2e-13, atol=1e-15,
        dense_output=True, max_step=0.005,
    )

def shoot_v0() -> float:
    def target(v0):
        return float(integrate(v0).y[2, -1] - 1.0)
    return brentq(target, 2.3, 2.5, xtol=1e-13)

def diagnostics(sol, v0: float, z: float):
    N = math.log(1.0/(1.0+z))
    phi, v, E = [float(x) for x in sol.sol(N)]
    a = math.exp(N)
    dphi_dN, dv_dN, dE_dN = rhs(N, np.array([phi, v, E]))
    dot_v = dv_dN*E
    alpha_b = 2.0*v**3/(E*LAMBDA)
    x = v/E
    alpha_k = x*x + 6.0*alpha_b
    dkin = alpha_k + 1.5*alpha_b**2
    V = v0 - Q*phi
    rho_t = 0.5*v*v + V + 6.0*E*v**3/LAMBDA
    p_t = 0.5*v*v - V - 2.0*v*v*dot_v/LAMBDA
    omega_t = rho_t/(3.0*E*E)
    w_t = p_t/rho_t

    rho_m = 3.0*OMEGA_M0*a**-3
    rho_r = 3.0*OMEGA_R0*a**-4
    friedmann = (E*E + KCURV*a**-2) - (rho_m+rho_r+rho_t)/3.0
    residual = abs(friedmann)/(3.0*E*E)

    return {
        "z": z, "E": E, "alpha_B": alpha_b, "D_kin": dkin,
        "Omega_T": omega_t, "w_T": w_t, "friedmann_residual": residual,
    }

def main():
    v0 = shoot_v0()
    sol = integrate(v0)
    zs = [10.0, 3.0, 2.1, 1.5, 1.0, 0.8, 0.5, 0.3, 0.0]
    rows = [diagnostics(sol, v0, z) for z in zs]
    payload = {
        "model": "R1",
        "params": asdict(Params()),
        "V0_over_Mpl2H02": v0,
        "rows": rows,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
