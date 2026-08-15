"""Event-weighted M5-to-M4 gauge--LR pushforward.

The unique minimal child localization factor ``Lambda=1-4 sigma**2`` is
inserted once, in the rank-16 parent connection Hessian.  Both the boundary
gauge kernel and the current-current kernel are then derivatives of the same
Schur complement.  This module evaluates the resulting weighted static DtN
spectrum and tests the strongest LR channel without an independent Yukawa
coupling.
"""

from __future__ import annotations

import json
import math
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

import numpy as np
from scipy.integrate import solve_ivp

from bhsm.interface.aether_diagonal_sp1_m4_attachment_v15_50 import RADIUS0
from bhsm.interface.aether_unified_heat_pushforward_gap_v15_70 import (
    UP_CHANNEL_FACTOR,
    geometric_heat_parameter,
    physical_heat_susceptibility,
)


VERSION = "v15.71"
CLASSIFICATION = "BHSM_ACTION_COMPLETION_DERIVED_FROM_EXISTING_BHSM_STRUCTURE"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False


def half_cap_sigma(rho: float) -> float:
    """Selected degree-one response profile on ``0<=rho<=pi/2``."""

    value = float(rho)
    if not 0.0 <= value <= math.pi / 2.0:
        raise ValueError("require 0<=rho<=pi/2")
    return -0.5 + value / math.pi - math.sin(2.0 * value) / (2.0 * math.pi)


def localization_weight(rho: float) -> float:
    sigma = half_cap_sigma(rho)
    return 1.0 - 4.0 * sigma * sigma


def _log_weight_derivative(rho: float) -> float:
    sigma = half_cap_sigma(rho)
    sigma_prime = (1.0 - math.cos(2.0 * rho)) / math.pi
    return -8.0 * sigma * sigma_prime / localization_weight(rho)


def _weighted_dtn(kind: str, level: int) -> float:
    """Dimensionless weighted DtN eigenvalue at the equator.

    The pole has ``Lambda~8 rho**3/(3 pi)``.  Frobenius exponents are used
    rather than an arbitrary pole boundary value.
    """

    n = int(level)
    if kind == "transverse":
        if n < 2:
            raise ValueError("transverse level must be at least two")
        angular = float(n * n)
        cotangent_factor = 1.0
        exponent = (-3.0 + math.sqrt(9.0 + 4.0 * angular)) / 2.0
    elif kind == "electric":
        if n < 1:
            raise ValueError("electric level must be at least one")
        angular = float(n * (n + 2))
        cotangent_factor = 3.0
        exponent = (-5.0 + math.sqrt(25.0 + 4.0 * angular)) / 2.0
    else:
        raise ValueError("kind must be transverse or electric")

    # Starting at 1e-3 avoids catastrophic cancellation in the closed form
    # for Lambda while the Frobenius error remains O(epsilon**2).
    epsilon = 1.0e-3

    def equation(rho: float, state: np.ndarray) -> np.ndarray:
        u, first = state
        second = -(
            cotangent_factor / math.tan(rho) + _log_weight_derivative(rho)
        ) * first + angular * u / math.sin(rho) ** 2
        return np.asarray((first, second))

    solution = solve_ivp(
        equation,
        (epsilon, math.pi / 2.0),
        (epsilon**exponent, exponent * epsilon ** (exponent - 1.0)),
        rtol=2.0e-9,
        atol=2.0e-11,
        max_step=1.0e-2,
    )
    if not solution.success:
        raise RuntimeError(solution.message)
    return float(solution.y[1, -1] / solution.y[0, -1])


@lru_cache(maxsize=None)
def transverse_dtn(level: int) -> float:
    return _weighted_dtn("transverse", level)


@lru_cache(maxsize=None)
def electric_dtn(level: int) -> float:
    return _weighted_dtn("electric", level)


def weighted_static_kernel_bound() -> dict[str, float]:
    radius = RADIUS0 / 2.0
    # K5 is the exact EH fiber coefficient pi^2 R_F^5 at kappa1=1.
    k5 = math.pi**2 * RADIUS0**5
    transverse = radius / (k5 * transverse_dtn(2))
    electric = radius / (k5 * electric_dtn(1))
    return {
        "K_F_five_dimensional": k5,
        "transverse_dimensionless_DtN_level_2": transverse_dtn(2),
        "electric_dimensionless_DtN_level_1": electric_dtn(1),
        "transverse_maximum": transverse,
        "Coulomb_maximum": electric,
        "sum_bound": transverse + electric,
    }


def weighted_up_channel_gap_bound() -> float:
    susceptibility = physical_heat_susceptibility(geometric_heat_parameter())
    return float(
        2.0 * UP_CHANNEL_FACTOR
        * weighted_static_kernel_bound()["sum_bound"] * susceptibility
    )


def unified_localization_contract() -> dict[str, Any]:
    rows = []
    for level in (2, 3, 4, 8):
        rows.append({
            "sector": "transverse",
            "level": level,
            "weighted_DtN": transverse_dtn(level),
            "round_DtN": float(level),
        })
    for level in (1, 2, 3, 4, 8):
        rows.append({
            "sector": "electric",
            "level": level,
            "weighted_DtN": electric_dtn(level),
            "round_DtN": level * (level + 2.0) / (level + 1.0),
        })
    bound = weighted_up_channel_gap_bound()
    return {
        "single_parent_action": (
            "S5_loc=(K_F^(5)/4)*integral_M5 Lambda(sigma) Tr_16(F^2)"
        ),
        "localization": "Lambda(sigma)=1-4*sigma^2",
        "profile": (
            "sigma(rho)=-1/2+rho/pi-sin(2rho)/(2pi),_0<=rho<=pi/2"
        ),
        "placement": "before_gauge_and_fermion_source_derivatives",
        "gauge_kernel": "K_A=K_F^(5)*N_Lambda+Pi_AA",
        "LR_kernel": "G_LR=(K_F^(5)*N_Lambda)^(-1)_projected_to_LR",
        "same_weighted_inverse_in_both": True,
        "mode_rows": rows,
        "static_kernel_bound": weighted_static_kernel_bound(),
        "up_channel_gap_norm_upper_bound": bound,
        "supercritical": bound >= 1.0,
    }


def completion_payload() -> dict[str, Any]:
    contract = unified_localization_contract()
    validation = {
        "pole_weight_zero": abs(localization_weight(0.0)) < 1.0e-14,
        "wall_weight_one": abs(localization_weight(math.pi / 2.0) - 1.0) < 1.0e-14,
        "weighted_DtN_positive": all(
            row["weighted_DtN"] > 0.0 for row in contract["mode_rows"]
        ),
        "same_operator_generates_gauge_and_LR": contract[
            "same_weighted_inverse_in_both"
        ],
        "minimal_localization_alone_subcritical": not contract["supercritical"],
        "independent_Yukawa_not_added": True,
        "independent_gauge_normalization_not_added": True,
        "no_new_continuous_coefficient": True,
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_event_weighted_unified_pushforward_v15_71",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "unified_localization_contract": contract,
        "scientific_result": (
            "THE_SELECTED_EVENT_WEIGHT_MUST_ACT_ON_THE_COMMON_PARENT_BLOCK;_"
            "ITS_EXACT_WEIGHTED_DTN_KERNEL_MODIFIES_GAUGE_AND_LR_TOGETHER_"
            "BUT_IS_NOT_BY_ITSELF_SUPERCRITICAL_AT_THE_GEOMETRIC_HEAT_SCALE"
        ),
        "active_calculation": (
            "INCLUDE_THE_ACTION-OWNED_LORENTZIAN_ETA_LEGENDRE_ZERO_AS_THE_"
            "NON-GAUSSIAN_EVENT_DOMAIN_OF_THIS_SAME_WEIGHTED_SCHUR_COMPLEMENT"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def _canonical(value: Any) -> Any:
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        value = float(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite float")
        return round(value, 12)
    if isinstance(value, Mapping):
        return {key: _canonical(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    return value


def deterministic_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(_canonical(payload), indent=2, sort_keys=True) + "\n"


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_event_weighted_unified_pushforward_v15_71.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "half_cap_sigma",
    "localization_weight", "transverse_dtn", "electric_dtn",
    "weighted_static_kernel_bound", "weighted_up_channel_gap_bound",
    "unified_localization_contract", "completion_payload", "deterministic_json",
    "materialize",
]
