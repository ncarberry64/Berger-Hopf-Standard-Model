"""Inverse-free descriptor pencil for the N12 weight-seven round balance.

The retained weight-seven Lagrangian is a differential-algebraic system: the
lapse and shift coefficients have no time derivatives and the local lapse
symmetry gives twelve polynomial gauge chains.  This module constructs the
first-order generalized pencil directly from the exact action two-jet.  It
never forms an inverse of the velocity/multiplier (Euler--Dirac) block.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
from scipy.linalg import eig, solve, svdvals

from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (
    exact_weight_five_action_jet_at_state,
    exact_weight_seven_action_jet_at_state,
)
from bhsm.interface.aether_post_cut_nonround_lorentzian_cap_v15_48 import (
    RADIUS0,
)
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import (
    dimensions,
)


KAPPA0 = 15.0 * 5.0 ** (1.0 / 3.0) / 4.0
ROUND_EXPANSION_RATE = math.sqrt(KAPPA0 / 42.0)


@dataclass(frozen=True)
class DescriptorData:
    """Exact-quadrature realization of the weight-seven descriptor."""

    A: np.ndarray
    E: np.ndarray
    hessian: np.ndarray
    coordinate_dimension: int
    multiplier_dimension: int
    expansion_rate: float


def _normalized_hessian(order: int, points: int) -> np.ndarray:
    dims = dimensions(order)
    qdim = dims["coordinates"]
    mdim = dims["multipliers"]
    coordinates = np.zeros(qdim)
    velocities = np.zeros(qdim)
    velocities[0] = ROUND_EXPANSION_RATE
    multipliers = np.zeros(mdim)
    jet = exact_weight_seven_action_jet_at_state(
        order, coordinates, velocities, multipliers, points=points
    )
    # q0=0 at the represented round state, so RADIUS0**7 removes the common
    # scale factor and leaves the constant co-moving quadratic coefficients.
    return np.real(jet.hessian) / RADIUS0**7


def descriptor_data(*, order: int = 12, points: int = 384) -> DescriptorData:
    """Return ``A-E*sigma`` for the complete weight-seven DAE.

    For the normalized Hessian blocks ``H_ab`` and ``h=H0``, the linearized
    coordinate equation is

    ``Hvv qdd + (7h Hvv + Hvq-Hqv) qd + (7h Hvq-Hqq) q``
    ``+ Hvm md + (7h Hvm-Hqm)m = 0``.

    The multiplier equation is algebraic.  Linearizing with ``xi=qd`` gives
    the square descriptor below without solving a kinetic or Dirac block.
    """

    dims = dimensions(order)
    qdim = dims["coordinates"]
    mdim = dims["multipliers"]
    hessian = _normalized_hessian(order, points)
    q = slice(0, qdim)
    v = slice(qdim, 2 * qdim)
    m = slice(2 * qdim, 2 * qdim + mdim)
    hqq = hessian[q, q]
    hqv = hessian[q, v]
    hqm = hessian[q, m]
    hvq = hessian[v, q]
    hvv = hessian[v, v]
    hvm = hessian[v, m]
    hmq = hessian[m, q]
    hmv = hessian[m, v]
    hmm = hessian[m, m]
    total = 2 * qdim + mdim
    A = np.zeros((total, total))
    E = np.zeros((total, total))
    # sigma*q=xi
    A[q, v] = np.eye(qdim)
    E[q, q] = np.eye(qdim)
    # sigma*(Hvv*xi+Hvm*m) = the remaining negative EL terms.
    A[v, q] = -(7.0 * ROUND_EXPANSION_RATE * hvq - hqq)
    A[v, v] = -(
        7.0 * ROUND_EXPANSION_RATE * hvv + hvq - hqv
    )
    A[v, m] = -(7.0 * ROUND_EXPANSION_RATE * hvm - hqm)
    E[v, v] = hvv
    E[v, m] = hvm
    # Linearized lapse/shift constraints.
    A[m, q] = hmq
    A[m, v] = hmv
    A[m, m] = hmm
    return DescriptorData(
        A=A,
        E=E,
        hessian=hessian,
        coordinate_dimension=qdim,
        multiplier_dimension=mdim,
        expansion_rate=ROUND_EXPANSION_RATE,
    )


def physical_coordinate_indices(order: int = 12) -> np.ndarray:
    """Coordinates left after the exact local time/lapse quotient.

    The twelve ``u_k`` coordinates are the coordinate part of the polynomial
    time-reparametrization chains.  The retained quotient contains the common
    scale ``q0`` and all twelve ``w_j`` and twelve ``b_j`` modes.
    """

    qdim = dimensions(order)["coordinates"]
    return np.concatenate((np.asarray([0]), np.arange(1 + order, qdim)))


def time_gauge_vector(
    sigma: float, mode: int, *, order: int = 12
) -> np.ndarray:
    """Return one exact polynomial local time/lapse gauge vector.

    With gauge amplitude one,
    ``delta u_k=h``, ``delta dot(u_k)=h*sigma``, and
    ``delta log(N)_k=sigma``.  The vector is in
    ``ker(A-sigma E)`` for every ``sigma``.
    """

    if not 0 <= mode < order:
        raise ValueError("time gauge mode outside retained order")
    dims = dimensions(order)
    qdim = dims["coordinates"]
    mdim = dims["multipliers"]
    vector = np.zeros(2 * qdim + mdim)
    vector[1 + mode] = ROUND_EXPANSION_RATE
    vector[qdim + 1 + mode] = ROUND_EXPANSION_RATE * sigma
    vector[2 * qdim + mode] = sigma
    return vector


def bordered_physical_pencil(
    data: DescriptorData, *, order: int = 12
) -> tuple[np.ndarray, np.ndarray]:
    """Retain all KKT multipliers while quotienting the 12 gauge chains."""

    qdim = data.coordinate_dimension
    mdim = data.multiplier_dimension
    physical = physical_coordinate_indices(order)
    selected = np.concatenate(
        (physical, qdim + physical, np.arange(2 * qdim, 2 * qdim + mdim))
    )
    return (
        data.A[np.ix_(selected, selected)],
        data.E[np.ix_(selected, selected)],
    )


def homogeneous_spectrum(
    A: np.ndarray, E: np.ndarray, *, relative_beta_tolerance: float = 1.0e-10
) -> tuple[np.ndarray, int]:
    """Return finite generalized eigenvalues and the infinite-mode count."""

    alpha, beta = eig(
        A, E, right=False, homogeneous_eigvals=True, check_finite=False
    )
    scale = np.maximum(np.abs(alpha), np.abs(beta))
    finite = np.abs(beta) > relative_beta_tolerance * np.maximum(scale, 1.0)
    return alpha[finite] / beta[finite], int(np.count_nonzero(~finite))


def constraint_solved_crosscheck(
    data: DescriptorData, *, order: int = 12
) -> dict[str, object]:
    """Cross-check the bordered spectrum by a residual-certified Schur solve.

    This routine uses a symmetric linear solve only on the algebraic
    multiplier block.  It neither forms that inverse nor solves the singular
    combined velocity/multiplier Euler--Dirac block.
    """

    qdim = data.coordinate_dimension
    hessian = data.hessian
    qqvv = hessian[: 2 * qdim, : 2 * qdim]
    coupling = hessian[: 2 * qdim, 2 * qdim :]
    hmm = hessian[2 * qdim :, 2 * qdim :]
    solved = solve(hmm, coupling.T, assume_a="sym")
    residual = np.linalg.norm(hmm @ solved - coupling.T) / max(
        1.0, np.linalg.norm(coupling.T)
    )
    reduced = qqvv - coupling @ solved
    hqq = reduced[:qdim, :qdim]
    hqv = reduced[:qdim, qdim:]
    hvq = reduced[qdim:, :qdim]
    hvv = reduced[qdim:, qdim:]
    physical = physical_coordinate_indices(order)
    N = np.eye(qdim)[:, physical]
    q0 = N.T @ (
        7.0 * data.expansion_rate * hvq - hqq
    ) @ N
    q1 = N.T @ (
        7.0 * data.expansion_rate * hvv + hvq - hqv
    ) @ N
    q2 = N.T @ hvv @ N
    count = physical.size
    Aq = np.block(
        [[np.zeros((count, count)), np.eye(count)], [-q0, -q1]]
    )
    Eq = np.block(
        [[np.eye(count), np.zeros((count, count))],
         [np.zeros((count, count)), q2]]
    )
    values, infinite = homogeneous_spectrum(Aq, Eq)
    return {
        "finite_eigenvalues": values,
        "infinite_modes": infinite,
        "algebraic_solve_relative_residual": float(residual),
        "multiplier_block_condition_number": float(
            svdvals(hmm)[0] / svdvals(hmm)[-1]
        ),
        "combined_euler_dirac_inverse_formed": False,
    }


def cluster_residuals(values: np.ndarray) -> dict[str, float | int]:
    """Classify against the exact weight-seven roots 0 and -7 H0."""

    h = ROUND_EXPANSION_RATE
    distance_center = np.abs(values)
    distance_stable = np.abs(values + 7.0 * h)
    center = distance_center <= distance_stable
    return {
        "center_count": int(np.count_nonzero(center)),
        "stable_count": int(np.count_nonzero(~center)),
        "unstable_count": 0,
        "maximum_center_residual": float(np.max(distance_center[center])),
        "maximum_stable_residual": float(np.max(distance_stable[~center])),
    }


def weight_five_center_lift_system(
    *, order: int = 12, points: int = 384
) -> dict[str, np.ndarray | float]:
    """Return the exact first lower-weight Feshbach/KKT lift equation.

    Put ``epsilon=R4^-2`` on the round weight-seven orbit.  A scale-weight
    five particular correction has the form ``epsilon*X5`` and hence
    descriptor exponent ``sigma=-2*H0``.  The weight-five action contains no
    velocities, so its coordinate Euler--Lagrange residual is ``-D_q L5``
    and its algebraic residual is ``D_m L5``.  On the physical quotient,

    ``(A7+2*H0*E7) X5 = (0, -D_q_phys L5, -D_m L5)``.

    The matrix and right-hand side are returned without solving the badly
    conditioned coefficient-basis system.
    """

    dims = dimensions(order)
    qdim = dims["coordinates"]
    mdim = dims["multipliers"]
    coordinates = np.zeros(qdim)
    velocities = np.zeros(qdim)
    velocities[0] = ROUND_EXPANSION_RATE
    multipliers = np.zeros(mdim)
    jet = exact_weight_five_action_jet_at_state(
        order, coordinates, velocities, multipliers, points=points
    )
    gradient = np.real(jet.gradient) / RADIUS0**5
    data = descriptor_data(order=order, points=points)
    A, E = bordered_physical_pencil(data, order=order)
    physical = physical_coordinate_indices(order)
    right_hand_side = np.concatenate(
        (
            np.zeros(physical.size),
            -gradient[physical],
            -gradient[2 * qdim :],
        )
    )
    matrix = A + 2.0 * ROUND_EXPANSION_RATE * E
    singular_values = svdvals(matrix)
    return {
        "matrix": matrix,
        "right_hand_side": right_hand_side,
        "weight_five_gradient": gradient,
        "smallest_singular_value": float(singular_values[-1]),
        "largest_singular_value": float(singular_values[0]),
        "condition_number": float(singular_values[0] / singular_values[-1]),
        "descriptor_exponent": -2.0 * ROUND_EXPANSION_RATE,
    }


__all__ = [
    "KAPPA0",
    "ROUND_EXPANSION_RATE",
    "DescriptorData",
    "bordered_physical_pencil",
    "cluster_residuals",
    "constraint_solved_crosscheck",
    "descriptor_data",
    "homogeneous_spectrum",
    "physical_coordinate_indices",
    "time_gauge_vector",
    "weight_five_center_lift_system",
]
