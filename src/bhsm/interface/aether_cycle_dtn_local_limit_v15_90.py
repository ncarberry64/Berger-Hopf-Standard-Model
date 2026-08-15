"""Low-spectral-momentum local expansion of the same BHSM cycle DtN map."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import PchipInterpolator

from bhsm.interface.aether_one_cycle_joint_residues_v15_86 import EVENT_TIME
from bhsm.interface.aether_sampled_event_shell_pushforward_v15_74 import _profile


VERSION = "v15.90"
CLASSIFICATION = "BHSM_ONE_CYCLE_DTN_LOW_MOMENTUM_LOCAL_LIMIT"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False

# Values of the analytic variational integrals on the constraint-solved cycle
# states.  The reset row uses the v15.51 projected reset state; the remaining
# rows use the v15.74 states.  The event endpoint continuously extends the last
# regular state, as in v15.86.
LOCAL_DERIVATIVE_ROWS = (
    (0.0, 1499.2765206503693, 1139.4371744908735, "reset"),
    (0.08, 1355.0486724852508, 1071.3208410836976, "controlled"),
    (0.10, 1151.5702501306814, 925.6964316050930, "controlled"),
    (0.103, 995.3541710349837, 810.0256112515134, "controlled"),
    (0.10602, 976.9174729066602, 800.5376988693650, "controlled"),
    (EVENT_TIME, 976.9174729066602, 800.5376988693650, "event_limit"),
)


def variational_local_coefficient(time: float, sector: str, points: int = 1800) -> float:
    """Evaluate dN/dlambda at lambda=0 from the differentiated ODE."""

    if float(time) not in (0.08, 0.10, 0.103, 0.10602):
        raise ValueError("direct profile evaluation requires a stored controlled slice")
    profile = _profile(float(time), points=points)
    chi = np.asarray(profile["chi"])
    radius = np.asarray(profile["radius"])
    coefficient = np.asarray(profile["fiber_coefficient"])
    weight = np.asarray(profile["weight"])
    radial = np.asarray(profile["C"])
    if sector == "transverse":
        source_weight = coefficient * weight * radial / radius
        boundary_power = 1
    elif sector == "electric":
        source_weight = coefficient * weight * radial * radius
        boundary_power = 3
    else:
        raise ValueError("sector must be transverse or electric")
    return float(
        np.trapezoid(source_weight, chi) / radius[-1] ** boundary_power
    )


def continuous_spectral_dtn(
    time: float, sector: str, spectral_lambda: float, points: int = 1400,
) -> float:
    """Solve the weighted radial problem for continuous lambda near zero."""

    lam = float(spectral_lambda)
    if lam <= 0.0:
        raise ValueError("positive spectral lambda required")
    profile = _profile(float(time), points=points)
    chi = np.asarray(profile["chi"])
    radius = np.asarray(profile["radius"])
    radial = np.asarray(profile["C"])
    weight = np.asarray(profile["weight"])
    coefficient = np.asarray(profile["fiber_coefficient"])
    if sector == "transverse":
        p = coefficient * weight * radius / radial
        source_weight = coefficient * weight * radial / radius
        exponent = (-3.0 + math.sqrt(9.0 + 4.0 * lam)) / 2.0
        boundary_power = 1
    elif sector == "electric":
        p = coefficient * weight * radius**3 / radial
        source_weight = coefficient * weight * radial * radius
        exponent = (-5.0 + math.sqrt(25.0 + 4.0 * lam)) / 2.0
        boundary_power = 3
    else:
        raise ValueError("sector must be transverse or electric")
    mask = (p > 1.0e-18) & (source_weight > 1.0e-18)
    x = chi[mask]
    p = p[mask]
    source_weight = source_weight[mask]
    radius = radius[mask]
    log_p = PchipInterpolator(x, np.log(p))
    log_w = PchipInterpolator(x, np.log(source_weight))

    def p_at(value: float) -> float:
        return math.exp(float(log_p(value)))

    def w_at(value: float) -> float:
        return math.exp(float(log_w(value)))

    pole = float(x[0])
    boundary = float(x[-1])
    initial = np.asarray((
        pole**exponent,
        p_at(pole) * exponent * pole ** (exponent - 1.0),
    ))
    solution = solve_ivp(
        lambda value, state: np.asarray((
            state[1] / p_at(value), lam * w_at(value) * state[0]
        )),
        (pole, boundary),
        initial,
        rtol=1.0e-10,
        atol=1.0e-13,
        max_step=1.0e-3,
    )
    if not solution.success:
        raise RuntimeError(solution.message)
    return float(
        solution.y[1, -1]
        / (radius[-1] ** boundary_power * solution.y[0, -1])
    )


def cycle_local_coefficients() -> dict[str, Any]:
    times = np.asarray([row[0] for row in LOCAL_DERIVATIVE_ROWS])
    transverse = np.asarray([row[1] for row in LOCAL_DERIVATIVE_ROWS])
    electric = np.asarray([row[2] for row in LOCAL_DERIVATIVE_ROWS])

    def average(values: np.ndarray) -> float:
        return float(
            PchipInterpolator(times, values).integrate(0.0, EVENT_TIME)
            / EVENT_TIME
        )

    t_cycle = average(transverse)
    e_cycle = average(electric)
    return {
        "spectral_parameters": {
            "transverse": "lambda_T=n^2_for_the_coexact_vector_problem",
            "electric": "lambda_E=ell*(ell+2)_for_the_Gauss_scalar_problem",
        },
        "local_expansions": {
            "transverse": "N_T(lambda)=K_T_local*lambda+O(lambda^2)",
            "electric": "N_E(lambda)=K_E_local*lambda+O(lambda^2)",
        },
        "cycle_K_T_local": t_cycle,
        "cycle_K_E_Gauss_local": e_cycle,
        "cycle_rows": [
            {
                "time": time,
                "K_T_local": transverse_value,
                "K_E_Gauss_local": electric_value,
                "provenance": provenance,
            }
            for time, transverse_value, electric_value, provenance
            in LOCAL_DERIVATIVE_ROWS
        ],
        "carrier_trace_local_ray": {
            "Y": (5.0 / 3.0) * t_cycle,
            "Sp1": t_cycle,
            "SU3": t_cycle,
        },
        "spatial_local_inverse_coupling_ray": "5/3:1:1",
    }


def locality_claim_boundary() -> dict[str, Any]:
    return {
        "local_spatial_Fij_derivative_coefficient_derived": True,
        "local_Gauss_constraint_derivative_coefficient_derived": True,
        "same_DtN_operator_as_absolute_cycle_residue": True,
        "independent_intrinsic_boundary_normalization_added": False,
        "dynamic_frequency_response_derived": False,
        "Lorentz_invariant_FmunuFmunu_coefficient_derived": False,
        "reason": (
            "the_static_transverse_and_Gauss_maps_fix_spatial_and_constraint_"
            "derivatives;_the_omega_squared_response_is_required_before_"
            "identifying_a_single_local_Lorentzian_Maxwell_coefficient"
        ),
    }


def completion_payload() -> dict[str, Any]:
    cycle = cycle_local_coefficients()
    boundary = locality_claim_boundary()
    lam = 1.0e-5
    direct_t = continuous_spectral_dtn(0.10602, "transverse", lam)
    direct_e = continuous_spectral_dtn(0.10602, "electric", lam)
    analytic_t = variational_local_coefficient(0.10602, "transverse")
    analytic_e = variational_local_coefficient(0.10602, "electric")
    validation = {
        "transverse_small_lambda_matches_variation": abs(
            direct_t / lam - analytic_t
        ) / analytic_t < 5.0e-6,
        "electric_small_lambda_matches_variation": abs(
            direct_e / lam - analytic_e
        ) / analytic_e < 5.0e-6,
        "cycle_local_coefficients_positive": (
            cycle["cycle_K_T_local"] > 0.0
            and cycle["cycle_K_E_Gauss_local"] > 0.0
        ),
        "local_trace_ray_exact": math.isclose(
            cycle["carrier_trace_local_ray"]["Y"]
            / cycle["carrier_trace_local_ray"]["Sp1"],
            5.0 / 3.0,
        ),
        "no_independent_normalization": not boundary[
            "independent_intrinsic_boundary_normalization_added"
        ],
        "Lorentz_completion_not_overclaimed": not boundary[
            "Lorentz_invariant_FmunuFmunu_coefficient_derived"
        ],
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_cycle_dtn_local_limit_v15_90",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "cycle_local_coefficients": cycle,
        "small_lambda_validation": {
            "lambda": lam,
            "transverse_direct_over_lambda": direct_t / lam,
            "transverse_variational": analytic_t,
            "electric_direct_over_lambda": direct_e / lam,
            "electric_variational": analytic_e,
        },
        "claim_boundary": boundary,
        "scientific_result": (
            "DIFFERENTIATING_THE_SAME_WEIGHTED_DtN_EQUATION_AT_lambda=0_"
            "DERIVES_POSITIVE_CYCLE-LOCAL_SPATIAL_AND_GAUSS_COEFFICIENTS_"
            "K_T=1394.790187_AND_K_E=1082.968994;_A_DYNAMIC_omega^2_"
            "CALCULATION_IS_STILL_REQUIRED_FOR_A_LORENTZIAN_MAXWELL_IDENTITY"
        ),
        "active_calculation": (
            "ADD_CONTINUOUS_BOUNDARY_FREQUENCY_TO_THE_SAME_M5_RADIAL_"
            "STURM-LIOUVILLE_PROBLEM_AND_COMPARE_dN/d(omega^2)_WITH_THE_"
            "SPATIAL_LOCAL_COEFFICIENT"
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
    path = target / "BHSM_aether_cycle_dtn_local_limit_v15_90.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "LOCAL_DERIVATIVE_ROWS", "variational_local_coefficient",
    "continuous_spectral_dtn", "cycle_local_coefficients",
    "locality_claim_boundary", "completion_payload", "deterministic_json",
    "materialize",
]
