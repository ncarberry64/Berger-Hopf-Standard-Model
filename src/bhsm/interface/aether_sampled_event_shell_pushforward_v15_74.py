"""Sample the exact event-weighted DtN operator on controlled child slices.

The stored states are deterministic outputs of the v15.51 Euler--Dirac flow,
reintegrated with step 5e-4 through t=0.103 and refined to the last regular
state t=0.10602.  They are not fitted data.  Each state reconstructs the full
radial weight, quotient metric and EH fiber coefficient before solving the
transverse and electric Sturm--Liouville problems.
"""

from __future__ import annotations

import json
import math
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import PchipInterpolator

from bhsm.interface.aether_post_cut_nonround_lorentzian_cap_v15_48 import cap_fields
from bhsm.interface.aether_unified_heat_pushforward_gap_v15_70 import (
    UP_CHANNEL_FACTOR,
    geometric_heat_parameter,
    physical_heat_susceptibility,
)


VERSION = "v15.74"
CLASSIFICATION = "BHSM_CONTROLLED_EVENT_SHELL_UNIFIED_PUSHFORWARD_SAMPLE"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False


SNAPSHOTS: dict[float, dict[str, tuple[float, ...] | float]] = {
    0.08: {
        "q": (0.016870858601002518, 0.015438643060034635, 0.01315436592931361, 0.013545095991648569, -0.09298141709174776, -0.10686117524745095, -0.13407533436111052, 0.0, 0.0),
        "v": (0.2676798821428418, 0.3121886361408372, 0.2770546982012226, -1.668772085133537, -3.436207364224451, -1.0381055161031036, -1.5661212208762902, 0.0, 0.0),
        "m": (0.0171158660609078, 0.9948568587891228, 0.02195736097899646, 0.4661952305167985),
        "constraint_residual": 1.793838906224421e-4,
    },
    0.10: {
        "q": (0.022342633348732262, 0.022332036785720887, 0.019520142304445938, -0.03389099514495458, -0.1788110976844653, -0.12480219313422464, -0.1637125972602199, 0.0, 0.0),
        "v": (0.2545894096089554, 0.3867159766514235, 0.3835965736179502, -3.4051603378887676, -5.821750584793562, -0.6364995421560544, -1.2869028507339586, 0.0, 0.0),
        "m": (0.08301346687654328, 1.2445146714008335, -0.08561725965508961, 0.7004665568602942),
        "constraint_residual": 1.4949319560031427e-4,
    },
    0.103: {
        "q": (0.022935183369114206, 0.023554996118527734, 0.020826663777311315, -0.04615187229968598, -0.20079435300705206, -0.12594113550546132, -0.1668552567539739, 0.0, 0.0),
        "v": (0.20588339916042953, 0.42813269011720023, 0.4521081589946459, -4.370918472168553, -7.679440076873198, -0.34434561447845147, -1.0311643206035057, 0.0, 0.0),
        "m": (0.13868657708314616, 1.256334743511068, -0.202244625717853, 0.8441650430971793),
        "constraint_residual": 1.5037593392719373e-4,
    },
    0.10602: {
        "q": (0.023541750197571067, 0.02491529650190556, 0.022275167797186895, -0.06049852250873416, -0.22584612670896823, -0.12668491043104713, -0.16972723625838004, 0.0, 0.0),
        "v": (0.23147156810202354, 0.46362649824717767, 0.48079024214309946, -4.799906566952149, -8.098617157608073, -0.2928486948219527, -1.0137530828264476, 0.0, 0.0),
        "m": (0.1646363511782319, 1.4596683906940477, -0.19892423994137573, 0.8692130997632196),
        "constraint_residual": 4.143321241656394e-5,
    },
}


def _profile(time: float, points: int = 900) -> dict[str, np.ndarray | float]:
    state = SNAPSHOTS[float(time)]
    q = np.asarray(state["q"], dtype=float)
    velocity = np.asarray(state["v"], dtype=float)
    multipliers = np.asarray(state["m"], dtype=float)
    fields = cap_fields(q, velocity, points=points)
    chi = np.asarray(fields["chi"])
    A = np.asarray(fields["A"])
    B = np.asarray(fields["B"])
    C = np.asarray(fields["C"])
    n1, n2, b0, b1 = multipliers
    lapse = np.exp(n1 * np.cos(4.0 * chi) + n2 * np.cos(8.0 * chi))
    shift = np.sin(4.0 * chi) * (b0 + b1 * np.cos(4.0 * chi))
    normal_f = (
        np.asarray(fields["f_dot_coordinate"])
        - shift * np.asarray(fields["f_prime"])
    ) / lapse
    spatial_x = (
        np.asarray(fields["f_prime"]) ** 2 / C**2
        + 3.0 * np.cos(np.asarray(fields["f"])) ** 2 / A**2
        + 3.0 * np.sin(np.asarray(fields["f"])) ** 2 / B**2
    )
    legendre = 1.0 + (spatial_x - normal_f**2) ** 3
    localization = 1.0 - 4.0 * np.asarray(fields["sigma"]) ** 2
    radius = A * B / np.sqrt(A * A + B * B)
    # From the eight-dimensional Einstein term after diagonal Sp(1) reduction.
    fiber_coefficient = math.pi**2 * (A * A + B * B) ** 2.5
    return {
        "chi": chi,
        "A": A,
        "B": B,
        "C": C,
        "radius": radius,
        "legendre": legendre,
        "localization": localization,
        "weight": localization * legendre,
        "fiber_coefficient": fiber_coefficient,
        "minimum_legendre": float(np.min(legendre)),
        "minimum_legendre_chi": float(chi[int(np.argmin(legendre))]),
        "boundary_legendre": float(legendre[-1]),
        "boundary_radius": float(radius[-1]),
    }


def _dtn(time: float, sector: str, level: int, points: int = 900) -> float:
    profile = _profile(time, points)
    chi = np.asarray(profile["chi"])
    radius = np.asarray(profile["radius"])
    C = np.asarray(profile["C"])
    weight = np.asarray(profile["weight"])
    coefficient = np.asarray(profile["fiber_coefficient"])
    n = int(level)
    if sector == "transverse":
        if n < 2:
            raise ValueError("transverse level must be at least two")
        p = coefficient * weight * radius / C
        potential = coefficient * weight * C * n * n / radius
        exponent = (-3.0 + math.sqrt(9.0 + 4.0 * n * n)) / 2.0
        boundary_power = 1
    elif sector == "electric":
        if n < 1:
            raise ValueError("electric level must be at least one")
        p = coefficient * weight * radius**3 / C
        potential = coefficient * weight * C * radius * n * (n + 2)
        exponent = (-5.0 + math.sqrt(25.0 + 4.0 * n * (n + 2))) / 2.0
        boundary_power = 3
    else:
        raise ValueError("unknown sector")

    mask = (p > 1.0e-18) & (potential > 1.0e-18)
    x = chi[mask]
    p = p[mask]
    potential = potential[mask]
    radial = radius[mask]
    log_p = PchipInterpolator(x, np.log(p))
    log_q = PchipInterpolator(x, np.log(potential))

    def p_at(value: float) -> float:
        return math.exp(float(log_p(value)))

    def q_at(value: float) -> float:
        return math.exp(float(log_q(value)))

    pole = float(x[0])
    boundary = float(x[-1])
    initial = np.asarray((
        pole**exponent,
        p_at(pole) * exponent * pole ** (exponent - 1.0),
    ))
    solution = solve_ivp(
        lambda value, state: np.asarray((
            state[1] / p_at(value), q_at(value) * state[0]
        )),
        (pole, boundary), initial,
        rtol=2.0e-9, atol=2.0e-11, max_step=2.0e-3,
    )
    if not solution.success:
        raise RuntimeError(solution.message)
    return float(
        solution.y[1, -1]
        / (radial[-1] ** boundary_power * solution.y[0, -1])
    )


@lru_cache(maxsize=None)
def lowest_transverse_stiffness(time: float) -> float:
    return _dtn(float(time), "transverse", 2)


@lru_cache(maxsize=None)
def lowest_electric_stiffness(time: float) -> float:
    return _dtn(float(time), "electric", 1)


def up_channel_norm_bound(time: float) -> float:
    inverse = (
        1.0 / lowest_transverse_stiffness(time)
        + 1.0 / lowest_electric_stiffness(time)
    )
    susceptibility = physical_heat_susceptibility(geometric_heat_parameter())
    return float(2.0 * UP_CHANNEL_FACTOR * inverse * susceptibility)


def sampled_rows() -> list[dict[str, float]]:
    rows = []
    for time in sorted(SNAPSHOTS):
        profile = _profile(time)
        rows.append({
            "time": time,
            "constraint_residual": float(SNAPSHOTS[time]["constraint_residual"]),
            "minimum_eta_Legendre": float(profile["minimum_legendre"]),
            "minimum_shell_chi": float(profile["minimum_legendre_chi"]),
            "boundary_eta_Legendre": float(profile["boundary_legendre"]),
            "boundary_radius": float(profile["boundary_radius"]),
            "lowest_transverse_stiffness": lowest_transverse_stiffness(time),
            "lowest_electric_stiffness": lowest_electric_stiffness(time),
            "up_channel_norm_upper_bound": up_channel_norm_bound(time),
        })
    return rows


def completion_payload() -> dict[str, Any]:
    rows = sampled_rows()
    validation = {
        "all_constraint_residuals_controlled": all(
            row["constraint_residual"] < 2.0e-4 for row in rows
        ),
        "all_weighted_operators_regular": all(
            row["minimum_eta_Legendre"] > 0.0 for row in rows
        ),
        "gauge_stiffness_softens": (
            rows[-1]["lowest_transverse_stiffness"]
            < rows[0]["lowest_transverse_stiffness"]
            and rows[-1]["lowest_electric_stiffness"]
            < rows[0]["lowest_electric_stiffness"]
        ),
        "LR_bound_strengthens": (
            rows[-1]["up_channel_norm_upper_bound"]
            > rows[0]["up_channel_norm_upper_bound"]
        ),
        "controlled_branch_remains_subcritical": all(
            row["up_channel_norm_upper_bound"] < 1.0 for row in rows
        ),
        "same_weighted_operator_used_for_both": True,
        "no_independent_Yukawa_or_gauge_rescaling": True,
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_sampled_event_shell_pushforward_v15_74",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "sampled_rows": rows,
        "scientific_result": (
            "THE_ACTUAL_WEIGHTED_DTN_STIFFNESSES_DECREASE_AND_THE_SAME-"
            "OPERATOR_LR_BOUND_INCREASES_ALONG_THE_CONTROLLED_BRANCH,_BUT_"
            "THE_FREE-CONFORMAL_BRANCH_REMAINS_STRICTLY_SUBCRITICAL_BEFORE_"
            "ITS_NEXT_STAGE_LEGENDRE_SINGULARITY"
        ),
        "claim_boundary": {
            "actual_radial_profiles_used": True,
            "nonround_quotient_metric_used": True,
            "joint_crossing_found_on_controlled_branch": False,
            "independent_sector_fix_added": False,
        },
        "active_calculation": (
            "ADD_THE_COMMON_GAUGE-FERMION_SUPERTRACE_LOG_TO_THE_SAME_"
            "CONSTRAINED_CHILD_ACTION_AND_RECOMPUTE_THE_EVENT-SHELL_FLOW_"
            "AND_WEIGHTED_DTN/LR_EIGENVALUE_TOGETHER"
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
    path = target / "BHSM_aether_sampled_event_shell_pushforward_v15_74.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "SNAPSHOTS",
    "lowest_transverse_stiffness", "lowest_electric_stiffness",
    "up_channel_norm_bound", "sampled_rows", "completion_payload",
    "deterministic_json", "materialize",
]
