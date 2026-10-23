from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Callable

import numpy as np


@dataclass(frozen=True)
class OpticalStateIndex:
    zeta: int = 0
    kappa: int = 1
    p_kappa: int = 2
    gamma1: int = 3
    p_gamma1: int = 4
    gamma2: int = 5
    p_gamma2: int = 6


IDX = OpticalStateIndex()
STATE_DIM = 7
SOURCE_DIM = 4


def S_K(chi: float, K: float) -> float:
    if K > 0.0:
        root = math.sqrt(K)
        return math.sin(root * chi) / root
    if K < 0.0:
        root = math.sqrt(-K)
        return math.sinh(root * chi) / root
    return chi


def C_K(chi: float, K: float) -> float:
    if K > 0.0:
        return math.cos(math.sqrt(K) * chi)
    if K < 0.0:
        return math.cosh(math.sqrt(-K) * chi)
    return 1.0


def H_K(chi: float, K: float) -> float:
    s = S_K(chi, K)
    if abs(s) < 1.0e-15:
        raise ValueError("H_K is singular at S_K(chi)=0")
    return C_K(chi, K) / s


def drift_matrix(chi: float, K: float) -> np.ndarray:
    h = H_K(chi, K)
    A = np.zeros((STATE_DIM, STATE_DIM), dtype=float)

    A[IDX.kappa, IDX.p_kappa] = 1.0
    A[IDX.p_kappa, IDX.p_kappa] = -2.0 * h

    A[IDX.gamma1, IDX.p_gamma1] = 1.0
    A[IDX.p_gamma1, IDX.p_gamma1] = -2.0 * h

    A[IDX.gamma2, IDX.p_gamma2] = 1.0
    A[IDX.p_gamma2, IDX.p_gamma2] = -2.0 * h

    return A


def source_matrix() -> np.ndarray:
    B = np.zeros((STATE_DIM, SOURCE_DIM), dtype=float)
    B[IDX.zeta, 0] = 1.0
    B[IDX.p_kappa, 1] = 1.0
    B[IDX.p_gamma1, 2] = 1.0
    B[IDX.p_gamma2, 3] = 1.0
    return B


B_OPT = source_matrix()


def optical_rhs(
    chi: float,
    y: np.ndarray,
    K: float,
    source: np.ndarray,
) -> np.ndarray:
    y = np.asarray(y, dtype=float)
    s = np.asarray(source, dtype=float)
    if y.shape != (STATE_DIM,):
        raise ValueError(f"expected y shape {(STATE_DIM,)}, got {y.shape}")
    if s.shape != (SOURCE_DIM,):
        raise ValueError(f"expected source shape {(SOURCE_DIM,)}, got {s.shape}")
    return drift_matrix(chi, K) @ y + B_OPT @ s


def covariance_rhs(
    chi: float,
    covariance: np.ndarray,
    K: float,
    q_opt: np.ndarray,
) -> np.ndarray:
    C = np.asarray(covariance, dtype=float)
    Q = np.asarray(q_opt, dtype=float)
    if C.shape != (STATE_DIM, STATE_DIM):
        raise ValueError("covariance must be 7x7")
    if Q.shape != (SOURCE_DIM, SOURCE_DIM):
        raise ValueError("q_opt must be 4x4")

    A = drift_matrix(chi, K)
    return A @ C + C @ A.T + B_OPT @ Q @ B_OPT.T


def jacobi_background_residual(
    chi: float,
    K: float,
) -> float:
    """Analytic residual of S_K'' + K S_K = 0."""
    # S_K'' = -K S_K for all constant K branches.
    return -K * S_K(chi, K) + K * S_K(chi, K)


def optical_tidal_components(delta_t: np.ndarray) -> np.ndarray:
    """Map a symmetric 2x2 optical-tidal perturbation to (F,G1,G2)."""
    t = np.asarray(delta_t, dtype=float)
    if t.shape != (2, 2):
        raise ValueError("delta_t must be 2x2")
    if not np.allclose(t, t.T, rtol=0.0, atol=1e-14):
        raise ValueError("delta_t must be symmetric")
    F = -0.5 * (t[0, 0] + t[1, 1])
    G1 = -0.5 * (t[0, 0] - t[1, 1])
    G2 = -t[0, 1]
    return np.array([F, G1, G2], dtype=float)


def fixed_affine_fractional_distance(
    zeta_gamma: float,
    kappa: float,
) -> float:
    """First-order delta ln D_L at fixed physical source endpoint."""
    return 2.0 * float(zeta_gamma) - float(kappa)


def rk4_step(
    chi: float,
    y: np.ndarray,
    h: float,
    K: float,
    source_fn: Callable[[float], np.ndarray],
) -> np.ndarray:
    y = np.asarray(y, dtype=float)
    k1 = optical_rhs(chi, y, K, source_fn(chi))
    k2 = optical_rhs(
        chi + 0.5 * h,
        y + 0.5 * h * k1,
        K,
        source_fn(chi + 0.5 * h),
    )
    k3 = optical_rhs(
        chi + 0.5 * h,
        y + 0.5 * h * k2,
        K,
        source_fn(chi + 0.5 * h),
    )
    k4 = optical_rhs(
        chi + h,
        y + h * k3,
        K,
        source_fn(chi + h),
    )
    return y + (h / 6.0) * (k1 + 2*k2 + 2*k3 + k4)
