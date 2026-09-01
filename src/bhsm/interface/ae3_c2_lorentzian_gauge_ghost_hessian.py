"""Same-C2 continuous-frequency gauge/ghost Hessian and residue test.

The current AE3 localization weight is inserted in the owned parent Maxwell
form before the radial variable is eliminated.  The resulting transverse
Dirichlet-to-Neumann (DtN) operator is evaluated at continuous Lorentzian
frequency.  Its frequency derivative is compared with its spatial
coexact coefficient without adding or fitting a normalization.
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np
from scipy.integrate import quad, solve_ivp

from bhsm.interface.aether_event_weighted_unified_pushforward_v15_71 import (
    localization_weight,
)
from bhsm.interface.aether_nonabelian_coexact_vertex_v16_03 import (
    coexact_curl_basis,
)


ACTION_VERSION = "BHSM-AE-3.0.0"
CLASSIFICATION = "CURRENT_C2_LORENTZIAN_GAUGE_GHOST_FREQUENCY_HESSIAN"
LOWEST_TRANSVERSE_LEVEL = 2
_POLE_EPSILON = 1.0e-3


def _half_cap_sigma(rho: float) -> float:
    value = float(rho)
    if not 0.0 <= value <= math.pi / 2.0:
        raise ValueError("require 0<=rho<=pi/2")
    return -0.5 + value / math.pi - math.sin(2.0 * value) / (2.0 * math.pi)


def _log_weight_derivative(rho: float) -> float:
    sigma = _half_cap_sigma(rho)
    sigma_prime = (1.0 - math.cos(2.0 * rho)) / math.pi
    return -8.0 * sigma * sigma_prime / localization_weight(rho)


def _regular_exponent(level: int) -> float:
    n = int(level)
    if n < 2:
        raise ValueError("transverse level must be at least two")
    return (-3.0 + math.sqrt(9.0 + 4.0 * n * n)) / 2.0


def transverse_frequency_solution(
    level: int = LOWEST_TRANSVERSE_LEVEL,
    *,
    q_squared: float = 0.0,
    dense_output: bool = False,
) -> Any:
    """Solve the AE3-weighted radial transverse equation.

    ``q_squared=(omega*r_boundary)^2`` is continuous and is not a cycle
    eigenfrequency.  The Lorentzian sign enters as ``-q_squared`` in the
    Sturm--Liouville potential.
    """

    n = int(level)
    q2 = float(q_squared)
    if n < 2 or not math.isfinite(q2):
        raise ValueError("finite q_squared and transverse level >=2 required")
    exponent = _regular_exponent(n)

    def equation(rho: float, state: np.ndarray) -> np.ndarray:
        u, first = state
        second = -(
            1.0 / math.tan(rho) + _log_weight_derivative(rho)
        ) * first + (n * n / math.sin(rho) ** 2 - q2) * u
        return np.asarray((first, second))

    epsilon = _POLE_EPSILON
    solution = solve_ivp(
        equation,
        (epsilon, math.pi / 2.0),
        (epsilon**exponent, exponent * epsilon ** (exponent - 1.0)),
        rtol=1.0e-11,
        atol=1.0e-13,
        max_step=2.0e-3,
        dense_output=dense_output,
    )
    if not solution.success:
        raise RuntimeError(solution.message)
    return solution


def transverse_frequency_dtn(
    level: int = LOWEST_TRANSVERSE_LEVEL, *, q_squared: float = 0.0
) -> float:
    """Return the dimensionless continuous-frequency transverse DtN value."""

    solution = transverse_frequency_solution(level, q_squared=q_squared)
    return float(solution.y[1, -1] / solution.y[0, -1])


def lowest_transverse_residue_witness() -> dict[str, float | int | bool | str]:
    """Extract the omega-squared coefficient and the spatial residue.

    The static regular extension is normalized to one at the enclosure wall.
    The envelope theorem then gives ``-dN/dq^2`` as the electric integral.
    """

    level = LOWEST_TRANSVERSE_LEVEL
    solution = transverse_frequency_solution(level, dense_output=True)
    boundary_value = float(solution.y[0, -1])
    if solution.sol is None or boundary_value == 0.0:
        raise RuntimeError("dense nonzero regular extension required")

    def u(rho: float) -> float:
        return float(solution.sol(rho)[0] / boundary_value)

    def du(rho: float) -> float:
        return float(solution.sol(rho)[1] / boundary_value)

    epsilon = _POLE_EPSILON
    endpoint = math.pi / 2.0
    electric = quad(
        lambda rho: localization_weight(rho) * math.sin(rho) * u(rho) ** 2,
        epsilon,
        endpoint,
        epsabs=1.0e-11,
        epsrel=1.0e-11,
        limit=300,
    )[0]
    magnetic = quad(
        lambda rho: localization_weight(rho) * u(rho) ** 2 / math.sin(rho),
        epsilon,
        endpoint,
        epsabs=1.0e-11,
        epsrel=1.0e-11,
        limit=300,
    )[0]
    radial_gradient = quad(
        lambda rho: localization_weight(rho) * math.sin(rho) * du(rho) ** 2,
        epsilon,
        endpoint,
        epsabs=1.0e-11,
        epsrel=1.0e-11,
        limit=300,
    )[0]
    static_dtn = float(solution.y[1, -1] / boundary_value)
    static_energy = radial_gradient + level * level * magnetic
    step = 1.0e-4
    centered_derivative = (
        transverse_frequency_dtn(level, q_squared=step)
        - transverse_frequency_dtn(level, q_squared=-step)
    ) / (2.0 * step)
    temporal_to_spatial = level * level * electric / static_dtn
    return {
        "transverse_level": level,
        "v16_03_level_zero_curl_eigenvalue": 2,
        "static_dimensionless_DtN": static_dtn,
        "electric_weight_integral": electric,
        "magnetic_weight_integral": magnetic,
        "radial_gradient_integral": radial_gradient,
        "static_energy_identity_right_hand_side": static_energy,
        "d_DtN_d_q_squared_at_zero": -electric,
        "centered_difference_derivative": centered_derivative,
        "pure_electric_to_magnetic_weight_ratio": electric / magnetic,
        "temporal_to_complete_spatial_mode_residue_ratio": temporal_to_spatial,
        "one_Lorentzian_residue": temporal_to_spatial == 1.0,
        "mismatch_source": (
            "UNEQUAL_RADIAL_ELECTRIC_AND_MAGNETIC_METRIC_WEIGHTS_PLUS_THE_"
            "POSITIVE_RADIAL_GRADIENT_DTN_TERM_ON_THE_SMOOTH_BULK_TRACE_DOMAIN"
        ),
    }


def current_c2_transverse_frequency_symbol(
    *, log_radii: np.ndarray, omega: float
) -> dict[str, Any]:
    """Return the frozen-slice continuous-frequency symbol on current C2."""

    x = np.asarray(log_radii, dtype=float)
    frequency = float(omega)
    if x.ndim != 1 or x.size < 2 or not np.all(np.isfinite(x)):
        raise ValueError("finite current-C2 log-radius nodes required")
    if not math.isfinite(frequency):
        raise ValueError("finite continuous frequency required")
    radius = np.exp(0.5 * (x[:-1] + x[1:]))
    witness = lowest_transverse_residue_witness()
    n = int(witness["transverse_level"])
    n0 = float(witness["static_dimensionless_DtN"])
    i_t = float(witness["electric_weight_integral"])
    z_t_over_kf5 = radius * i_t
    z_s_over_kf5 = radius * n0 / (n * n)
    k_coexact = (n / radius) ** 2
    low_frequency = z_s_over_kf5 * k_coexact - z_t_over_kf5 * frequency**2
    return {
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "frequency_parameter": frequency,
        "frequency_domain": "CONTINUOUS_REAL_OMEGA__NOT_PERIODIC_CYCLE_MODE",
        "segment_count": int(radius.size),
        "boundary_radius": radius,
        "coexact_eigenvalue": k_coexact,
        "Z_t_over_K_F5": z_t_over_kf5,
        "Z_s_over_K_F5": z_s_over_kf5,
        "H_transverse_low_frequency_over_K_F5": low_frequency,
        "formula": "H_T/K_F5=Zs_over_KF5*K_coexact-Zt_over_KF5*omega^2+O(omega^4)",
        "residue_ratio": z_t_over_kf5 / z_s_over_kf5,
        "independent_residue_inserted": False,
    }


def constraint_ghost_frequency_block(
    *, omega: float, scalar_laplacian: float, z_temporal: float, z_spatial: float
) -> dict[str, Any]:
    """Assemble temporal/longitudinal, gauge-fixing, and ghost blocks.

    The Maxwell constraint block is written in ``(A_0,phi_L)`` coordinates.
    Its exact gauge null vector is retained before a BRST-exact gauge-fixing
    term is added.  The ghost symbol is the derivative of that gauge
    functional along the same null direction.
    """

    w = float(omega)
    lam = float(scalar_laplacian)
    zt = float(z_temporal)
    zs = float(z_spatial)
    if not all(math.isfinite(value) for value in (w, lam, zt, zs)):
        raise ValueError("finite block data required")
    if lam <= 0.0 or zt <= 0.0 or zs <= 0.0:
        raise ValueError("positive scalar eigenvalue and residues required")
    electric_row = np.asarray((1.0, 1.0j * w), dtype=complex)
    maxwell = zt * lam * np.outer(electric_row.conj(), electric_row)
    gauge_direction = np.asarray((-1.0j * w, 1.0), dtype=complex)
    gauge_functional = np.asarray((1.0j * zt * w, -zs * lam), dtype=complex)
    gauge_fixing = np.outer(gauge_functional.conj(), gauge_functional) / (
        zs * lam
    )
    ghost = complex(gauge_functional @ gauge_direction)
    return {
        "basis": ("A_0", "phi_longitudinal"),
        "Maxwell_constraint_block": maxwell,
        "gauge_null_vector": gauge_direction,
        "gauge_fixing_block_xi_one": gauge_fixing,
        "gauge_fixed_block": maxwell + gauge_fixing,
        "ghost_Faddeev_Popov_symbol": ghost,
        "expected_ghost_symbol": complex(zt * w * w - zs * lam),
        "Maxwell_Ward_residual": float(np.linalg.norm(maxwell @ gauge_direction)),
        "BRST_real_degree_weights": {
            "temporal_plus_longitudinal_bosons": 2,
            "complex_ghost": -2,
        },
        "physical_transverse_residue_changed_by_gauge_fixing": False,
    }


def gauge_ghost_hessian_claim_boundary() -> dict[str, Any]:
    return {
        "same_C2_continuous_frequency_gauge_ghost_Hessian_derived": True,
        "temporal_transverse_constraint_and_ghost_blocks_derived_together": True,
        "CURRENT_C2_LORENTZIAN_MAXWELL_RESIDUE_DERIVED": False,
        "residue_outcome": "MISMATCH_RECORDED__NOT_RENORMALIZED",
        "physical_photon_derived": False,
        "electroweak_neutral_Hessian_derived": False,
        "independent_ZA_g_gprime_alpha_or_metric_cone_inserted": False,
        "next_required_action_domain_object": (
            "THE_CONTINUOUS_FREQUENCY_GAUGE_GHOST_CALDERON_OPERATOR_ON_THE_"
            "ACTUAL_CURRENT_C2_MAXIMAL_EXTERIOR_AND_ITS_TWO_SIDED_PARENT_"
            "SCHUR_COMPLEMENT_WITH_THE_DERIVED_INTERIOR_OPERATOR"
        ),
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "LOWEST_TRANSVERSE_LEVEL",
    "constraint_ghost_frequency_block",
    "current_c2_transverse_frequency_symbol",
    "gauge_ghost_hessian_claim_boundary",
    "lowest_transverse_residue_witness",
    "transverse_frequency_dtn",
    "transverse_frequency_solution",
]
