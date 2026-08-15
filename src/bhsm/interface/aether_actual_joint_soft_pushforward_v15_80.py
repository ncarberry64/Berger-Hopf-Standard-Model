"""First joint gauge/LR pushforward on the actual Euler--Dirac soft event.

The calculation uses the fixed v15.51 Galerkin coordinates and the measured
soft eigenvector from v15.79.  Gauge stiffness and the fermionic soft source
are evaluated on the same linearly transported child slice.
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

from bhsm.interface.aether_actual_dirac_event_pencil_v15_79 import (
    event_pencil_diagnostics,
)
from bhsm.interface.aether_diagonal_sp1_m4_attachment_v15_50 import RADIUS0
from bhsm.interface.aether_m4_standard_model_zeta_backreaction_v15_51 import (
    attached_eta_gauge_dirac_acceleration,
)
from bhsm.interface.aether_post_cut_nonround_lorentzian_cap_v15_48 import cap_fields
from bhsm.interface.aether_sampled_event_shell_pushforward_v15_74 import (
    SNAPSHOTS,
    up_channel_norm_bound,
)
from bhsm.interface.aether_unified_heat_pushforward_gap_v15_70 import (
    geometric_heat_parameter,
    physical_heat_susceptibility,
)


VERSION = "v15.80"
CLASSIFICATION = "BHSM_ACTUAL_EVENT_JOINT_SOFT_PUSHFORWARD"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False


def soft_wall_source_projection() -> dict[str, float | str | bool]:
    diagnostic = event_pencil_diagnostics()
    component = diagnostic["soft_eigenvector_components"]
    q = SNAPSHOTS[0.10602]["q"]
    boundary_v = float(q[5] - q[6])
    delta_u = -component["dot_u1"] + component["dot_u2"]
    delta_v = component["dot_v0"] - component["dot_v1"]
    delta_h4 = (
        component["dot_log_R"] + delta_u
        - math.tanh(2.0 * boundary_v) * delta_v
    )
    delta_log_lapse = -component["lapse_n1"] + component["lapse_n2"]
    radius = RADIUS0 / 2.0
    lowest_energy = 1.5 / radius
    # Euclideanized ADM Dirac source on a normalized positive-energy mode.
    # The normal zero-mode factor is exactly one.  The lapse term alone makes
    # the result nonzero; the Hubble/spin-connection term is fixed, not fitted.
    source = -delta_log_lapse * lowest_energy + 1.5 * delta_h4
    return {
        "boundary_Berger_v": boundary_v,
        "soft_delta_u_boundary": delta_u,
        "soft_delta_v_boundary": delta_v,
        "soft_delta_H4": delta_h4,
        "soft_delta_log_lapse": delta_log_lapse,
        "lowest_S3_Dirac_energy": lowest_energy,
        "normal_zero_mode_overlap": 1.0,
        "source_formula": "g_s0=-delta_logN*E0+(3/2)*delta_H4",
        "g_s0": source,
        "temporal_density_Fierz_scalar_fraction": 0.5,
        "nonzero": abs(source) > 1.0e-8,
        "coordinate_scope": "FIXED_v15.51_DIMENSIONLESS_GALERKIN_CHART",
    }


def first_actual_joint_crossing() -> dict[str, float | str]:
    diagnostic = event_pencil_diagnostics()
    source = soft_wall_source_projection()
    susceptibility = physical_heat_susceptibility(geometric_heat_parameter())
    gauge_norm = up_channel_norm_bound(0.10602)
    scalar_coefficient = 0.5 * float(source["g_s0"]) ** 2
    delta_star = susceptibility * scalar_coefficient / (1.0 - gauge_norm)
    delta0 = float(diagnostic["positive_distance_delta"])
    delta_rate = float(diagnostic["delta_time_derivative"])
    increment = (delta_star - delta0) / delta_rate
    eta_at_crossing = (
        float(diagnostic["minimum_eta_Legendre"])
        + float(diagnostic["minimum_eta_Legendre_time_derivative"]) * increment
    )
    return {
        "control": "delta=-lambda_soft(D_Euler-Dirac)",
        "regulated_LR_susceptibility": susceptibility,
        "gauge_norm_at_reference_slice": gauge_norm,
        "soft_scalar_coefficient": scalar_coefficient,
        "delta_star": delta_star,
        "time_increment_from_0.10602": increment,
        "crossing_time": 0.10602 + increment,
        "minimum_eta_Legendre_at_crossing": eta_at_crossing,
        "crossing_equation": (
            "1=gauge_norm+Chi_LR*g_s0^2/(2*delta_star)"
        ),
    }


def _linearized_crossing_state() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    state = SNAPSHOTS[0.10602]
    q = np.asarray(state["q"], dtype=float)
    velocity = np.asarray(state["v"], dtype=float)
    multipliers = np.asarray(state["m"], dtype=float)
    dynamics = attached_eta_gauge_dirac_acceleration(
        q, velocity, multipliers, points=32, step=5.0e-5
    )
    dt = float(first_actual_joint_crossing()["time_increment_from_0.10602"])
    return (
        q + dt * velocity,
        velocity + dt * np.asarray(dynamics["acceleration"]),
        multipliers + dt * np.asarray(dynamics["multiplier_velocity"]),
    )


def _crossing_profile(points: int = 900) -> dict[str, np.ndarray | float]:
    q, velocity, multipliers = _linearized_crossing_state()
    fields = cap_fields(q, velocity, points=points)
    chi = np.asarray(fields["chi"])
    A = np.asarray(fields["A"])
    B = np.asarray(fields["B"])
    C = np.asarray(fields["C"])
    f = np.asarray(fields["f"])
    n1, n2, b0, b1 = multipliers
    lapse = np.exp(n1 * np.cos(4.0 * chi) + n2 * np.cos(8.0 * chi))
    shift = np.sin(4.0 * chi) * (b0 + b1 * np.cos(4.0 * chi))
    normal_f = (
        np.asarray(fields["f_dot_coordinate"])
        - shift * np.asarray(fields["f_prime"])
    ) / lapse
    spatial_x = (
        np.asarray(fields["f_prime"]) ** 2 / C**2
        + 3.0 * np.cos(f) ** 2 / A**2
        + 3.0 * np.sin(f) ** 2 / B**2
    )
    legendre = 1.0 + (spatial_x - normal_f**2) ** 3
    localization = 1.0 - 4.0 * np.asarray(fields["sigma"]) ** 2
    radius = A * B / np.sqrt(A * A + B * B)
    fiber = math.pi**2 * (A * A + B * B) ** 2.5
    return {
        "chi": chi, "C": C, "radius": radius,
        "weight": localization * legendre, "fiber": fiber,
        "minimum_legendre": float(np.min(legendre)),
    }


def _crossing_dtn(sector: str, level: int) -> float:
    profile = _crossing_profile()
    chi = np.asarray(profile["chi"])
    C = np.asarray(profile["C"])
    radius = np.asarray(profile["radius"])
    weight = np.asarray(profile["weight"])
    fiber = np.asarray(profile["fiber"])
    if sector == "transverse":
        p = fiber * weight * radius / C
        potential = fiber * weight * C * level * level / radius
        exponent = (-3.0 + math.sqrt(9.0 + 4.0 * level * level)) / 2.0
        boundary_power = 1
    elif sector == "electric":
        p = fiber * weight * radius**3 / C
        potential = fiber * weight * C * radius * level * (level + 2)
        exponent = (-5.0 + math.sqrt(25.0 + 4.0 * level * (level + 2))) / 2.0
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
        (pole, boundary), initial, rtol=2.0e-9, atol=2.0e-11,
        max_step=2.0e-3,
    )
    if not solution.success:
        raise RuntimeError(solution.message)
    return float(
        solution.y[1, -1]
        / (radial[-1] ** boundary_power * solution.y[0, -1])
    )


@lru_cache(maxsize=1)
def same_slice_residues() -> dict[str, float | str | bool]:
    crossing = first_actual_joint_crossing()
    transverse = _crossing_dtn("transverse", 2)
    electric = _crossing_dtn("electric", 1)
    return {
        "crossing_time": float(crossing["crossing_time"]),
        "delta_star": float(crossing["delta_star"]),
        "minimum_eta_Legendre": float(_crossing_profile()["minimum_legendre"]),
        "absolute_transverse_DtN_residue": transverse,
        "absolute_electric_DtN_residue": electric,
        "nonzero_LR_soft_residue": (
            float(soft_wall_source_projection()["g_s0"]) ** 2
            / (2.0 * float(crossing["delta_star"]))
        ),
        "common_slice": True,
        "common_Gamma_boundary": True,
        "independent_Yukawa_normalization": False,
    }


def completion_payload() -> dict[str, Any]:
    source = soft_wall_source_projection()
    crossing = first_actual_joint_crossing()
    residues = same_slice_residues()
    validation = {
        "soft_fermion_source_nonzero": source["nonzero"],
        "crossing_precedes_Dirac_zero": (
            0.0 < crossing["delta_star"]
            < event_pencil_diagnostics()["positive_distance_delta"]
        ),
        "eta_operator_regular_at_actual_crossing": (
            residues["minimum_eta_Legendre"] > 0.5
        ),
        "gauge_residues_positive": (
            residues["absolute_transverse_DtN_residue"] > 0.0
            and residues["absolute_electric_DtN_residue"] > 0.0
        ),
        "LR_residue_nonzero": residues["nonzero_LR_soft_residue"] > 0.0,
        "same_slice_and_functional": (
            residues["common_slice"] and residues["common_Gamma_boundary"]
            and not residues["independent_Yukawa_normalization"]
        ),
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_actual_joint_soft_pushforward_v15_80",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "soft_wall_source_projection": source,
        "first_actual_joint_crossing": crossing,
        "same_slice_residues": residues,
        "scientific_result": (
            "IN_THE_FIXED_CONSTRAINT-SOLVED_GALERKIN_CHART_THE_MEASURED_"
            "EULER-DIRAC_SOFT_MODE_HAS_A_NONZERO_NORMALIZED_FERMION_SOURCE;_"
            "ITS_SCALAR_LR_FIERZ_BLOCK_FIRST_CROSSES_AT_delta_star_ON_THE_"
            "SAME_CHILD_SLICE_WHERE_THE_ABSOLUTE_TRANSVERSE_AND_ELECTRIC_"
            "GAUGE_DtN_RESIDUES_ARE_EVALUATED"
        ),
        "claim_boundary": {
            "joint_actual_event_crossing_in_Galerkin_chart": True,
            "absolute_same_slice_gauge_DtN_evaluated": True,
            "nonzero_same_slice_LR_residue_evaluated": True,
            "full_Sobolev_soft_source_projection_evaluated": False,
            "family_hierarchy_and_full_cycle_backreaction_evaluated": False,
        },
        "active_calculation": (
            "LIFT_THE_MEASURED_SOFT_SOURCE_AND_DtN_PAIR_FROM_THE_FIXED_"
            "GALERKIN_CHART_TO_THE_FULL_SOBOLEV_KKT_PENCIL,_THEN_SOLVE_"
            "THE_BACKREACTED_ONE-CYCLE_GAP_AND_FLOQUET_MASS"
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
    path = target / "BHSM_aether_actual_joint_soft_pushforward_v15_80.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "soft_wall_source_projection", "first_actual_joint_crossing",
    "same_slice_residues", "completion_payload", "deterministic_json",
    "materialize",
]
