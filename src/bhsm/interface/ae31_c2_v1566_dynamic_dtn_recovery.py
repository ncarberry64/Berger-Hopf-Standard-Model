"""Continuous-frequency recovery of the v15.65--v15.66 round-cap DtN."""

from __future__ import annotations

import math
from typing import Any

import numpy as np
from scipy.integrate import quad, solve_ivp

from bhsm.interface.aether_full_gauge_dtn_lr_kernel_v15_66 import (
    full_gauge_dtn_completion,
)


ACTION_VERSION = "BHSM-AE-3.1.0"
CLASSIFICATION = "V1566_ROUND_CAP_CONTINUOUS_FREQUENCY_DTN_RECOVERY"


def round_cap_frequency_dtn(mode: int = 2, *, q_squared: float = 0.0) -> float:
    """Solve the regular Lorentzian round-cap transverse radial equation."""

    m = int(mode)
    q2 = float(q_squared)
    if m < 2 or not math.isfinite(q2):
        raise ValueError("coexact mode >=2 and finite q_squared required")
    epsilon = 1.0e-4

    def equation(rho: float, state: np.ndarray) -> np.ndarray:
        u, first = state
        second = -first / math.tan(rho) + (
            m * m / math.sin(rho) ** 2 - q2
        ) * u
        return np.asarray((first, second))

    solution = solve_ivp(
        equation,
        (epsilon, math.pi / 2.0),
        (epsilon**m, m * epsilon ** (m - 1)),
        rtol=2.0e-12,
        atol=1.0e-14,
        max_step=1.0e-3,
    )
    if not solution.success:
        raise RuntimeError(solution.message)
    return float(solution.y[1, -1] / solution.y[0, -1])


def exact_round_cap_residue(mode: int = 2) -> dict[str, Any]:
    """Extract the exact low-frequency temporal/spatial residue ratio."""

    m = int(mode)
    if m < 2:
        raise ValueError("coexact mode >=2 required")
    electric = quad(
        lambda rho: math.sin(rho) * math.tan(rho / 2.0) ** (2 * m),
        0.0,
        math.pi / 2.0,
        epsabs=1.0e-13,
        epsrel=1.0e-13,
    )[0]
    step = 1.0e-4
    derivative = (
        round_cap_frequency_dtn(m, q_squared=step)
        - round_cap_frequency_dtn(m, q_squared=-step)
    ) / (2.0 * step)
    ratio = m * electric
    result = {
        "mode": m,
        "static_dimensionless_DtN": float(m),
        "electric_weight_integral": electric,
        "minus_d_DtN_d_q_squared_exact": electric,
        "centered_difference_derivative": derivative,
        "temporal_to_spatial_residue_ratio": ratio,
        "one_Lorentzian_Maxwell_residue": ratio == 1.0,
        "continuous_frequency_not_cycle_surrogate": True,
    }
    if m == 2:
        exact_electric = 3.0 - 4.0 * math.log(2.0)
        exact_ratio = 6.0 - 8.0 * math.log(2.0)
        result.update(
            {
                "exact_electric_formula": "3-4*log(2)",
                "exact_ratio_formula": "6-8*log(2)",
                "exact_electric_formula_residual": abs(electric - exact_electric),
                "exact_ratio_formula_residual": abs(ratio - exact_ratio),
            }
        )
    return result


def v1566_current_c2_recovery_classification() -> dict[str, Any]:
    """Separate reusable provenance from an unauthorized additive repair."""

    parent = full_gauge_dtn_completion()
    residue = exact_round_cap_residue(2)
    return {
        "reusable_upstream_assets": [
            "ACTION_OWNED_K_F_FIVE_DIMENSIONAL",
            "FULL_GAUGE_COEFFICIENT_RAY_5_OVER_3_TO_1_TO_1",
            "STATIC_ORDER_ONE_DTN_OPERATOR",
            "LR_GROUP_FACTORS",
        ],
        "parent_provenance": parent["provenance"],
        "round_cap_dynamic_ratio": residue[
            "temporal_to_spatial_residue_ratio"
        ],
        "round_cap_dynamic_Maxwell_residue": residue[
            "one_Lorentzian_Maxwell_residue"
        ],
        "same_geometry_as_current_AE3_weighted_reciprocal_profile": False,
        "may_be_added_to_current_AE3_trace_without_double_counting": False,
        "why_not_additive": (
            "V1566_IS_THE_BULK_PUSHFORWARD_OF_THE_PREDECESSOR_ROUND_CAP_USING_"
            "THE_SAME_PARENT_CONNECTION_COEFFICIENT_NOT_AN_INDEPENDENT_"
            "CONTACT_FIELD"
        ),
        "v1566_supplies_missing_noncommon_current_C2_correction": False,
        "v1569_common_parent_subtraction_still_required": True,
        "scientific_result": (
            "THE_RECOVERED_STATIC_KERNEL_AND_GROUP_RAY_SURVIVE_BUT_ITS_"
            "CONTINUOUS_FREQUENCY_ROUND_CAP_COMPLETION_ALSO_FAILS_THE_"
            "SINGLE_MAXWELL_RESIDUE_TEST"
        ),
    }


def claim_boundary() -> dict[str, Any]:
    return {
        "V1566_ROUND_CAP_CONTINUOUS_FREQUENCY_DTN_DERIVED": True,
        "V1566_STATIC_FULL_GAUGE_KERNEL_PROVENANCE_REUSABLE": True,
        "V1566_ROUND_CAP_ONE_LORENTZIAN_MAXWELL_RESIDUE_DERIVED": False,
        "V1566_ADDITIVE_CURRENT_C2_BOUNDARY_CORRECTION_AUTHORIZED": False,
        "CURRENT_C2_LORENTZIAN_MAXWELL_RESIDUE_DERIVED": False,
        "CURRENT_C2_NORMALIZED_PHOTON_PROPAGATOR_DERIVED": False,
        "MUON_MAGNETIC_MOMENT_DERIVED": False,
        "FULL_BHSM_COMPLETE": False,
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "claim_boundary",
    "exact_round_cap_residue",
    "round_cap_frequency_dtn",
    "v1566_current_c2_recovery_classification",
]
